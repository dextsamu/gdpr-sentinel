#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Collaudo automatico degli script contro l'app di prova con difetti noti.

Uso:  python3 tests/run_checks.py
Verifica che gli script trovino ciò che deve trovare (difetti noti), non inventino altro, rispettino i limiti di sicurezza
(host non locali rifiutati, segreti mai stampati) e producano i PDF in tutte le modalità. Esce con 1 al primo fallimento.
"""
import csv
import json
import re
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SC = ROOT / "scripts"
FX = ROOT / "tests" / "fixtures"
APP = FX / "vuln-app"
EXP = json.loads((APP / "expected.json").read_text(encoding="utf-8"))
ok = fail = 0


def run(script, *args, expect=0):
    r = subprocess.run([sys.executable, str(SC / script), *map(str, args)], capture_output=True, text=True)
    return r


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1; print(f"  ok   {name}")
    else:
        fail += 1; print(f"  FAIL {name} {detail}")


def have(s):
    return (SC / s).exists()


tmp = Path(tempfile.mkdtemp())
# i manifest delle app di prova sono salvati come *.bench (versioni vulnerabili apposta: così Dependabot non li segnala);
# i collaudi usano una copia con i nomi veri
import shutil as _sh
_sh.copytree(FX / "vuln-app", tmp / "vuln-app")
for _b in (tmp / "vuln-app").rglob("*.bench"):
    _b.rename(_b.with_suffix(""))
APP = tmp / "vuln-app"
print("appsec-sentinel / gdpr-sentinel: collaudo script")

if have("inventory_routes.py"):
    r = run("inventory_routes.py", APP, "--out", tmp / "ep.csv")
    rows = list(csv.DictReader((tmp / "ep.csv").open(encoding="utf-8")))
    noauth = sorted(x["endpoint"] for x in rows if x["identita"] == "NESSUNA AUTH EVIDENTE")
    check("inventario: numero di route", len(rows) == EXP["route_totali"], f"{len(rows)}")
    check("inventario: route senza auth evidente", noauth == EXP["senza_auth_evidente"], str(noauth))
    check("inventario: la route con auth inline non è segnalata", "/api/products" not in noauth)

if have("dynamic_authz_check.py"):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == "/open" else 401); self.end_headers(); self.wfile.write(b"x")
        def log_message(self, *a):
            pass
    srv = HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    cfg = tmp / "c.json"; cfg.write_text(json.dumps({"base_url": f"http://127.0.0.1:{srv.server_port}", "identities": {"anonimo": {}}, "delay_ms": 0}))
    t = tmp / "t.csv"; t.write_text("endpoint,metodo,identita,atteso,finding_id\n/open,GET,anonimo,401|403,X\n/closed,GET,anonimo,401,\n/x,POST,anonimo,401,\n")
    r = run("dynamic_authz_check.py", "--config", cfg, "--tests", t, "--out", tmp / "res.csv")
    res = list(csv.DictReader((tmp / "res.csv").open(encoding="utf-8")))
    check("test dinamici: rileva l'accesso inatteso", r.returncode == 2 and "DIFFORME" in r.stdout)
    check("test dinamici: metodo con effetti di stato saltato", res[2]["eseguito"] == "no")
    bad = tmp / "bad.json"; bad.write_text(json.dumps({"base_url": "https://example.com", "identities": {"anonimo": {}}}))
    r = run("dynamic_authz_check.py", "--config", bad, "--tests", t)
    check("test dinamici: host non locale rifiutato", r.returncode == 1 and "RIFIUTATO" in (r.stdout + r.stderr))
    srv.shutdown()

if have("import_scanner.py"):
    r = run("import_scanner.py", "--npm-audit", FX / "scanner/npm-audit.json", "--gitleaks", FX / "scanner/gitleaks.json", "--out", tmp / "cand.json")
    cand = json.loads((tmp / "cand.json").read_text(encoding="utf-8"))
    check("import: 3 candidati", len(cand) == 3, str(len(cand)))
    check("import: sempre ipotesi e mai oltre media", all(c["stato"] == "ipotesi da validare" and c["severita"] in ("media", "bassa", "informativa") for c in cand))
    check("import: il valore del segreto non compare", "VALORE-DI-PROVA" not in (tmp / "cand.json").read_text(encoding="utf-8") + r.stdout)
    v = run("validate_findings.py", tmp / "cand.json")
    check("import: i candidati superano la validazione", v.returncode == 0, v.stdout[-200:])
    r2 = run("import_scanner.py", "--npm-audit", FX / "scanner/npm-audit.json", "--merge", tmp / "cand.json", "--out", tmp / "cand2.json")
    check("import: nessun duplicato con --merge", len(json.loads((tmp / "cand2.json").read_text(encoding="utf-8"))) == 3)
    if have("export_findings.py"):
        run("export_findings.py", tmp / "cand.json", "--csv", tmp / "o.csv", "--sarif", tmp / "o.sarif", "--md-dir", tmp / "md")
        sar = json.loads((tmp / "o.sarif").read_text(encoding="utf-8"))
        check("export: SARIF valido con 3 risultati", sar["version"] == "2.1.0" and len(sar["runs"][0]["results"]) == 3)
        check("export: CSV e Markdown creati", (tmp / "o.csv").exists() and len(list((tmp / "md").glob("*.md"))) == 3)
    if have("verify_findings.py"):
        r = run("verify_findings.py", tmp / "cand.json", "--repo", APP)
        bad = json.loads((tmp / "cand.json").read_text(encoding="utf-8"))[:1]
        bad[0]["prova"]["riferimenti_file"] = ["file/che/non/esiste.ts:10"]
        (tmp / "bad-f.json").write_text(json.dumps(bad))
        r = run("verify_findings.py", tmp / "bad-f.json", "--repo", APP)
        check("revisore: segnala i riferimenti inesistenti", r.returncode == 1 and "inesistente" in r.stdout, r.stdout[:200])
    if have("compare_audits.py"):
        new = cand[1:]
        (tmp / "new.json").write_text(json.dumps(new))
        r = run("compare_audits.py", tmp / "cand.json", tmp / "new.json", "--json", tmp / "cmp.json")
        c = json.loads((tmp / "cmp.json").read_text(encoding="utf-8"))
        check("confronto: un risolto e due invariati", len(c["risolti"]) == 1 and len(c["invariati"]) == 2, str({k: len(v) for k, v in c.items()}))

if have("redact_check.py"):
    leak = tmp / "leak.txt"; leak.write_text("token " + "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz0123456789AB" + " e password: Sup3r" + "Segreta!\n")  # costruito a runtime: nessun segreto-simile nel repository
    r = run("redact_check.py", leak)
    check("redazione: trova segreti ed esce con 1", r.returncode == 1 and "ALTO" in r.stdout)
    check("redazione: non stampa il valore", "ghp_abcdef" not in r.stdout and "Sup3rSegreta" not in r.stdout)
    clean = tmp / "clean.md"; clean.write_text("Nessun dato sensibile. password: ***** e token: <redatto>\n")
    check("redazione: testo pulito esce con 0", run("redact_check.py", clean).returncode == 0)

if have("draft_ropa.py"):
    r = run("draft_ropa.py", APP, "--out", tmp / "ropa")
    sup = (tmp / "ropa" / "fornitori-bozza.csv").read_text(encoding="utf-8")
    mod = (tmp / "ropa" / "processing-map-bozza.csv").read_text(encoding="utf-8")
    check("bozza art. 30: fornitori attesi", all(f in sup for f in EXP["fornitori_attesi"]), sup[:200])
    check("bozza art. 30: modelli con dati personali", all(f"«{m}»" in mod for m in EXP["modelli_con_dati_personali"]))
    check("bozza art. 30: tutto in ipotesi", "ipotesi da validare" in mod and "ipotesi da validare" in sup)

if have("retention_check.py"):
    r = run("retention_check.py", APP, "--out", tmp / "ret.csv")
    check("retention: trova il job pianificato", "job pianificati 1" in r.stdout or "job pianificati 2" in r.stdout, r.stdout[:150])
    check("retention: trova la cancellazione con soglia", "cancellazione con soglia" in (tmp / "ret.csv").read_text(encoding="utf-8"))

if have("cookie_scan.py"):
    r = run("cookie_scan.py", "https://example.com")
    check("cookie scan: URL non locale rifiutato senza --autorizzato", r.returncode == 1 and "RIFIUTATO" in (r.stdout + r.stderr))

if have("cookie_scan.py") and (FX.parent / "lab" / "cookie_lab.py").exists():
    # collaudo su una pagina locale reale (richiede playwright e chromium; se mancano il blocco è saltato e dichiarato)
    try:
        import playwright.sync_api  # noqa: F401
        _pw = True
    except ImportError:
        _pw = False
    if not _pw:
        print("  salt cookie scan su pagina locale: playwright non installato")
    else:
        import socket, time
        _s = socket.socket(); _s.bind(("127.0.0.1", 0)); _port = _s.getsockname()[1]; _s.close()
        _srv = subprocess.Popen([sys.executable, str(FX.parent / "lab" / "cookie_lab.py"), str(_port)])
        try:
            time.sleep(0.8)
            r = run("cookie_scan.py", f"http://127.0.0.1:{_port}/", "--out", tmp / "cs", "--wait", "2")
            out = (tmp / "cs" / "cookie-scan.csv").read_text(encoding="utf-8") if (tmp / "cs" / "cookie-scan.csv").exists() else ""
            allout = out + ((tmp / "cs" / "cookie-scan.json").read_text(encoding="utf-8") if (tmp / "cs" / "cookie-scan.json").exists() else "") + r.stdout
            check("cookie scan locale: rileva cookie e storage prima del consenso", r.returncode == 0 and ",cookie,_ga_lab," in out and ",storage,_ga_lab," in out, r.stderr[-200:])
            check("cookie scan locale: classifica analytics e font di terzi", "www.google-analytics.com,script,analytics" in out and "fonts.googleapis.com" in out)
            check("cookie scan locale: il valore del cookie non compare in nessun output", "VALORE-SEGRETO" not in allout)
        finally:
            _srv.kill()

if have("draft_dpia.py"):
    pm = tmp / "pm-dpia.csv"
    pm.write_text("id,trattamento,dati_e_interessati,finalita,ruoli,base_giuridica_e_condizione,sistemi_e_destinatari,paesi_e_trasferimenti,retention,diritti_e_controlli,evidenze,gap\n"
                  "T01,Timbrature con GPS,\"coordinate, orari; dipendenti\",presenze,non verificato,non verificato,database interno,non verificato,GPS anonimizzato dopo 90 giorni,export,job cron,accordo sindacale da verificare\n"
                  "T02,Newsletter,email dei visitatori,comunicazioni,non verificato,consenso,provider email,non verificato,non verificato,disiscrizione,form,\n"
                  "T03,esempio: riga di esempio,x,x,x,x,x,x,x,x,x,x\n", encoding="utf-8")
    r = run("draft_dpia.py", pm, "--out", tmp / "dpia.md")
    d = (tmp / "dpia.md").read_text(encoding="utf-8") if (tmp / "dpia.md").exists() else ""
    check("dpia: una scheda per trattamento reale, le righe di esempio ignorate", r.returncode == 0 and d.count("\n## T0") == 2 and "riga di esempio" not in d, r.stderr[-200:])
    check("dpia: indicatori rilevati sul trattamento con GPS e lavoratori", "geolocalizzazione" in d and "monitoraggio sistematico" in d and "lavoratori o volontari" in d)
    check("dpia: ciò che la mappa non sa resta «da compilare con il titolare»", "Ruoli (titolare, responsabili): da compilare con il titolare" in d)
    check("dpia: dichiara di essere una bozza e non giudica", "Non è una DPIA completata" in d and not re.search(r"(?i)\bconforme\b", d.replace("giudizi di conformità", "")))
    r = run("draft_dpia.py", tmp / "non-esiste.csv")
    check("dpia: mappa inesistente dà errore", r.returncode == 1)

if have("build_report_pdf.py"):
    ex = [p for p in (ROOT / "examples").glob("*") if p.is_dir()][0]
    for label, extra in (("completo", []), ("sintetico", ["--sintetico"]), ("inglese", ["--lang", "en"]), ("NIS2", ["--nis2"])):
        out = tmp / f"{label}.pdf"
        r = run("build_report_pdf.py", ex, "--meta", ex / "meta.json", "--out", out, *extra)
        check(f"PDF {label}", r.returncode == 0 and out.exists() and out.stat().st_size > 5000, r.stderr[-200:])


if have("check_matrix.py"):
    m = tmp / "m.csv"
    head = "controllo,area,evidenza_tecnica,evidenza_documentale,decisione_mancante,stato,gap,rischio_per_gli_interessati,domanda_id,smentita\n"
    rows = "".join(f"{c},x,,,,non verificabile,,,Q{c},\n" for c in "BCDEFGHIJKLMN")
    base = head + "A,x,codice (file:1),,,confermato da codice/config,Fornitore senza DPA,medio,,%s\n" + rows
    m.write_text(base % "", encoding="utf-8")
    r = run("check_matrix.py", m)
    check("matrice: gap confermato senza smentita è un warning", r.returncode == 0 and "senza smentita" in r.stdout, r.stdout[-300:])
    m.write_text(base % "resiste | secondo passaggio indipendente | cercato un DPA in contratti e codice: nessuno", encoding="utf-8")
    check("matrice: smentita completa, il warning scompare", "smentita" not in run("check_matrix.py", m).stdout, run("check_matrix.py", m).stdout)
    m.write_text(base % "resiste: nessun DPA trovato", encoding="utf-8")
    check("matrice: «resiste» senza verificatore e tentativi segnalato", "esito | verificatore | tentativi" in run("check_matrix.py", m).stdout)
    m.write_text(base % "resiste | stesso autore | riletto il codice", encoding="utf-8")
    check("matrice: smentita dell'autore stesso non vale", "autore stesso" in run("check_matrix.py", m).stdout)
    m.write_text(base % "boh", encoding="utf-8")
    check("matrice: esito di smentita non riconoscibile segnalato", "esito riconoscibile" in run("check_matrix.py", m).stdout)


if have("check_delivery.py"):
    import shutil as _sh
    aud = tmp / "aud"; (aud / "findings").mkdir(parents=True)
    if (tmp / "hi.json").exists():
        _sh.copy(tmp / "hi.json", aud / "findings" / "findings.json")
        r = run("check_delivery.py", aud)
        check("consegna: finding alto senza smentita fa fallire", r.returncode == 1 and "mancante su" in r.stdout, r.stdout[-300:])
        _sh.copy(tmp / "hi2.json", aud / "findings" / "findings.json")
        r = run("check_delivery.py", aud)
        check("consegna: con la smentita non fallisce", r.returncode == 0, r.stdout[-400:])
    fake = tmp / "fakeapp"; fake.mkdir()
    sv = "Zq" + "9xK2mPLw7Rt"   # costruito a runtime
    (fake / "config.py").write_text(f'SECRET_KEY = "{sv}"\n', encoding="utf-8")
    (aud / "note.md").write_text(f"La chiave e {sv} nel file.\n", encoding="utf-8")
    r = run("check_delivery.py", aud, "--app", fake)
    check("consegna: il valore del segreto dell'app nell'audit fa fallire", r.returncode == 1 and "valore di un segreto" in r.stdout)
    check("consegna: non stampa il valore del segreto", sv not in r.stdout + r.stderr)
    (aud / "note.md").write_text("L'applicazione e conforme e sicura.\n", encoding="utf-8")
    r = run("check_delivery.py", aud)
    check("consegna: «conforme» come giudizio da verificare", "parole vietate" in r.stdout and "da rileggere" in r.stdout, r.stdout[-300:])
    (aud / "note.md").write_text("Non esprime giudizi di conformita e non dichiara l'app sicura.\n", encoding="utf-8")
    check("consegna: frase di avvertenza non segnalata", "da rileggere" not in run("check_delivery.py", aud).stdout)

if have("i18n.py") and have("check_delivery.py"):
    ae = tmp / "aud-lang"; (ae / "findings").mkdir(parents=True)
    (ae / "note.md").write_text("L'applicazione e conforme e sicura.\n", encoding="utf-8")
    ren = run("check_delivery.py", ae, "--lang", "en"); rit = run("check_delivery.py", ae)
    check("lingua: check_delivery --lang en in inglese, stesso esito", "Delivery check" in ren.stdout and "forbidden words" in ren.stdout and "to re-read" in ren.stdout and ren.returncode == rit.returncode, ren.stdout[-300:])
    check("lingua: senza --lang resta in italiano", "Controllo di consegna" in rit.stdout)

if have("canonicalize.py"):
    ca = tmp / "audit-en"; (ca / "findings").mkdir(parents=True)
    ex = json.loads((ROOT / "examples" / "findings.example.json").read_text(encoding="utf-8")) if (ROOT / "examples" / "findings.example.json").exists() else None
    if ex:
        ex[0].update(stato="Dynamically reproduced", severita="High", confidenza="medium")
        ex[0]["smentita"]["esito"] = "holds"
        ex[0]["titolo"] = "High-severity title stays untouched"
        (ca / "findings" / "findings.json").write_text(json.dumps(ex), encoding="utf-8")
        r = run("canonicalize.py", ca, "--dry-run")
        check("canonicalize: dry-run elenca 4 sostituzioni e non scrive", "farebbe: 4" in r.stdout and "Dynamically" in (ca / "findings" / "findings.json").read_text(encoding="utf-8"), r.stdout[:200])
        if have("check_delivery.py"):
            r = run("check_delivery.py", ca)
            check("consegna: valori in inglese segnalati prima della normalizzazione", "valori enumerati canonici" in r.stdout and "canonicalize.py" in r.stdout, r.stdout[-300:])
        r = run("canonicalize.py", ca)
        out = json.loads((ca / "findings" / "findings.json").read_text(encoding="utf-8"))[0]
        check("canonicalize: valori riportati in italiano, testo libero intatto",
              out["stato"] == "riprodotto dinamicamente" and out["severita"] == "alta" and out["confidenza"] == "media" and out["smentita"]["esito"] == "resiste" and out["titolo"] == "High-severity title stays untouched")
        check("canonicalize: idempotente", "fatte: 0" in run("canonicalize.py", ca).stdout)
        check("canonicalize: i finding riportati validano", run("validate_findings.py", ca / "findings" / "findings.json").returncode == 0 if have("validate_findings.py") else True)
    gmc = tmp / "audit-gdpr-en"; gmc.mkdir()
    (gmc / "gdpr-matrix.csv").write_text("controllo,area,evidenza_tecnica,evidenza_documentale,decisione_mancante,stato,gap,rischio_per_gli_interessati,domanda_id,smentita\nA,Mappa,,,,Found,,,,\nB,Base,,,,hypothesis,,,,\n", encoding="utf-8")
    run("canonicalize.py", gmc)
    rows = list(csv.DictReader((gmc / "gdpr-matrix.csv").open(encoding="utf-8")))
    check("canonicalize: matrice GDPR, stati in inglese riportati", [r["stato"] for r in rows] == ["riscontrato", "ipotesi"], str([r["stato"] for r in rows]))

# lingua: alias inglesi dei comandi, descrizione bilingue, etichette del PDF in inglese
_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
_cmds = re.findall(r"^- `([a-zà-ù-]+)[ `]", _skill.split("## Comandi rapidi", 1)[1].split("## Skill complementare", 1)[0], re.M)
_rows = re.findall(r"\| `([a-z-]+)` \| `([a-z-]+)` \|(?: \| `([a-z-]+)` \| `([a-z-]+)` \|)?", _skill.split("Alias inglesi dei comandi", 1)[1].split("Senza parole chiave", 1)[0])
_it = {x for r in _rows for x in (r[0], r[2]) if x}
_missing = [c for c in _cmds if c not in _it]
check("lingua: ogni comando italiano ha un alias inglese nella tabella", bool(_cmds) and not _missing, f"{len(_cmds)} comandi, mancanti {_missing}")
check("lingua: la descrizione della skill contiene anche l'inglese", "English:" in _skill.split("---", 2)[1])
if have("build_report_pdf.py"):
    sys.path.insert(0, str(SC))
    import build_report_pdf as _b
    _b.LANG = "en"
    check("PDF inglese: valori canonici mostrati in inglese", _b.V("riprodotto dinamicamente") == "dynamically reproduced" and _b.V("confermato da codice o configurazione") == "confirmed from code or configuration")
    _b.LANG = "it"
    check("PDF italiano: valori invariati", _b.V("riprodotto dinamicamente") == "riprodotto dinamicamente")

# banco privacy, pre-passaggio, gap strutturati e unione dei giri
SB = ROOT / "tests" / "bench-app" / "score_bench.py"
if SB.exists():
    btruth = json.loads((ROOT / "tests" / "bench-app" / "truth.json").read_text(encoding="utf-8"))
    bd = tmp / "gbench"; bd.mkdir()
    subprocess.run([sys.executable, str(SB), "prepare", str(bd)], capture_output=True, text=True)
    bapp = bd / "bench-app"
    check("banco privacy: app pronta, senza la verità, con informativa", (bapp / "public" / "privacy.md").exists() and not (bapp / "truth.json").exists() and (bapp / ".git").exists())
    hint = [str(q.relative_to(bapp)) for q in bapp.rglob("*") if q.is_file() and ".git" not in q.parts
            and re.search(r"(?i)vulnerab|\bbug\b|flaw|difetto|fixme|todo|violazion|non conform", q.read_text(encoding="utf-8", errors="replace"))]
    check("banco privacy: nessun commento che indichi i difetti", not hint, str(hint))
    if (SC / "gdpr_prepass.py").exists():
        w1, w2 = tmp / "gw1", tmp / "gw2"
        run("init_gdpr.py", w1); run("init_gdpr.py", w2)
        rp = run("gdpr_prepass.py", bapp, "--audit", w1); run("gdpr_prepass.py", bapp, "--audit", w2)
        check("prepass GDPR: deterministico", all((w1 / f).read_text(encoding="utf-8") == (w2 / f).read_text(encoding="utf-8")
                                                   for f in ("gdpr-matrix.csv", "registro-tool/privacy-scan.json", "registro-tool/fornitori-bozza.csv")), rp.stdout + rp.stderr)
        forn = (w1 / "registro-tool" / "fornitori-bozza.csv").read_text(encoding="utf-8")
        check("prepass GDPR: fornitori dal codice (Google Fonts, Tag Manager, Mailchimp, Sentry)", all(x in forn for x in ("Google Fonts", "Google Tag Manager", "Mailchimp", "Sentry")), forn[:300])
        ps = json.loads((w1 / "registro-tool" / "privacy-scan.json").read_text(encoding="utf-8"))
        files = lambda k: {x["file"] for x in ps[k]}
        check("prepass GDPR: indizi su tracker, dati sanitari, geolocalizzazione, log, cancellazione, informativa",
              "src/app/layout.tsx" in files("tracker") and "prisma/schema.prisma" in files("particolari") and "src/app/api/checkin/route.ts" in files("geolocalizzazione")
              and "src/app/api/auth/register/route.ts" in files("log") and "src/app/api/me/delete/route.ts" in files("diritti") and "public/privacy.md" in files("documenti"))
        cm = run("check_matrix.py", w1 / "gdpr-matrix.csv")
        check("matrice: controlli con il solo modello o la sola evidenza [prepass] sono errori", cm.returncode == 1 and "controllo non compilato" in cm.stdout, cm.stdout[-300:])
    hdr = "id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n"
    def gaps(rows):
        return hdr + "".join(",".join(f'"{x}"' for x in r) + "\n" for r in rows)
    perfect = [(f"GDPR-{i:03d}", d["controllo"], d["titolo"], d["file"][0] + ":1", "confermato da codice/config", "alta" if d["alto"] else "media", d["titolo"], "", "", "non eseguita")
               for i, d in enumerate(btruth["difetti"], 1)]
    poor = perfect[:5] + [("GDPR-090", "E", "Cookie di sessione impostato senza consenso", "src/lib/session.ts:4", "confermato da codice/config", "media", "il cookie di sessione richiede il consenso", "", "", "")]
    for nm, rows in (("gperf", perfect), ("gpoor", poor)):
        (tmp / nm).mkdir(); (tmp / nm / "gaps.csv").write_text(gaps(rows), encoding="utf-8")
    sc = subprocess.run([sys.executable, str(SB), "score", str(tmp / "gperf"), str(tmp / "gpoor")], capture_output=True, text=True)
    check("banco privacy: punteggio pieno 15/15, prioritari 6/6, nessun falso allarme", "difetti trovati: 15/15 · alti: 6/6 · falsi allarmi sulle esche: 0/5" in sc.stdout, sc.stdout[:300])
    check("banco privacy: giro scarso 5/15 con il falso allarme sul cookie tecnico", "difetti trovati: 5/15" in sc.stdout and "falso allarme Q01" in sc.stdout, sc.stdout[-500:])
    if (SC / "merge_audits.py").exists():
        mu = run("merge_audits.py", tmp / "gperf", tmp / "gpoor", "--out", tmp / "gunione")
        uj = json.loads((tmp / "gunione" / "unione-giri.json").read_text(encoding="utf-8")) if (tmp / "gunione" / "unione-giri.json").exists() else {}
        check("unione GDPR: gaps.csv unito con la provenienza (15 cause, 6 in comune)", (tmp / "gunione" / "gaps.csv").exists() and uj.get("cause_distinte") == 15 and uj.get("viste_da_tutti") == 6, mu.stdout + mu.stderr)
        gm = run("check_matrix.py", tmp / "gw1" / "gdpr-matrix.csv", "--gaps", tmp / "gunione" / "gaps.csv") if (tmp / "gw1").exists() else None
        try:
            import reportlab  # noqa: F401
            run("init_gdpr.py", tmp / "gpdf")
            import shutil as _sh3
            _sh3.copy(tmp / "gunione" / "gaps.csv", tmp / "gpdf" / "gaps.csv"); _sh3.copy(tmp / "gunione" / "unione-giri.json", tmp / "gpdf" / "unione-giri.json")
            rp = run("build_report_pdf.py", tmp / "gpdf", "--out", tmp / "gpdf.pdf")
            txt = subprocess.run(["pdftotext", str(tmp / "gpdf.pdf"), "-"], capture_output=True, text=True).stdout if _sh3.which("pdftotext") else "Gap privacy Due giri indipendenti"
            check("PDF privacy: sezioni «Gap privacy» e «Due giri indipendenti»", rp.returncode == 0 and "Gap privacy" in txt and "Due giri indipendenti" in txt, rp.stdout + rp.stderr)
        except ImportError:
            pass
        check("unione GDPR: il gaps.csv unito ha ID validi", gm is None or "ID non valido" not in gm.stdout, gm.stdout[-300:] if gm else "")
    gx = tmp / "gbad"; gx.mkdir()
    (gx / "gaps.csv").write_text(gaps([("GDPR-001", "Z", "conforme al GDPR", "", "riscontrato", "urgente", "", "", "", "")]), encoding="utf-8")
    cg = run("check_matrix.py", ROOT / "assets" / "gdpr-matrix.csv", "--gaps", gx / "gaps.csv")
    check("gap: controllo, priorità, riferimenti e giudizi di conformità verificati",
          all(s in cg.stdout for s in ("non tra A–N", "priorità 'urgente'", "senza riferimenti", "giudizio di conformità")), cg.stdout[-500:])

if have("apply_refutations.py"):
    import csv as _csv
    ga = tmp / "gap-smentita"; (ga / "smentite").mkdir(parents=True)
    hdr = "id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n"
    (ga / "gaps.csv").write_text(hdr + "GDPR-001,E,Analytics senza consenso,src/a.tsx:3,confermato da codice/config,alta,x,y,,non eseguita\n"
                                 "GDPR-002,G,Log senza cancellazione,src/b.ts:9,confermato da codice/config,alta,x,y,,non eseguita\n"
                                 "GDPR-003,D,Informativa assente,src/c.ts:1,riscontrato,alta,x,y,,non eseguita\n", encoding="utf-8")
    (ga / "smentite" / "esiti.json").write_text(json.dumps([
        {"id": "GDPR-001", "esito": "resiste", "verificatore": "secondo agente", "tentativi": ["script caricato prima del banner"]},
        {"id": "GDPR-002", "esito": "declassato", "verificatore": "secondo agente", "tentativi": ["job esterno nel crontab?"], "priorita": "media", "motivo": "cancellazione possibile fuori dal repository"},
        {"id": "GDPR-003", "esito": "respinto", "verificatore": "secondo agente", "tentativi": ["pagina /privacy"], "motivo": "informativa presente in public/privacy.md"}]), encoding="utf-8")
    r = run("apply_refutations.py", ga)
    rows = {x["id"]: x for x in _csv.DictReader((ga / "gaps.csv").open(encoding="utf-8"))}
    check("smentita sui gap: resiste, declassato abbassa la priorità, respinto in gaps-respinti.csv",
          rows.get("GDPR-001", {}).get("smentita", "").startswith("resiste | secondo agente") and rows.get("GDPR-002", {}).get("priorita") == "media"
          and "GDPR-003" not in rows and (ga / "gaps-respinti.csv").exists(), r.stdout + r.stderr)
    r2 = run("check_matrix.py", ROOT / "assets" / "gdpr-matrix.csv", "--gaps", ga / "gaps.csv")
    check("smentita sui gap: gaps.csv aggiornato supera check_matrix --gaps", not [l for l in (r2.stdout + r2.stderr).splitlines() if "gap GDPR-00" in l and "smentita" in l], (r2.stdout + r2.stderr)[-400:])

if have("gap_briefs.py"):
    gb = tmp / "gb-audit"; gr = tmp / "gb-repo"
    (gr / "src").mkdir(parents=True); gb.mkdir()
    (gr / "src" / "export.ts").write_text("export async function GET() {\n  return json(await db.member.find())\n}\n", encoding="utf-8")
    (gb / "gaps.csv").write_text("id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n"
                                 "GDPR-001,F,Manca l'esportazione,src/export.ts:1-2,confermato da codice/config,alta,diritto negato,art. 20 GDPR,,\n"
                                 "GDPR-002,G,Log senza retention,src/x.ts:1,ipotesi,alta,,,,\n"
                                 "GDPR-003,E,Font Google,src/x.ts:1,riscontrato,media,,,,\n"
                                 "GDPR-004,E,Analytics,src/x.ts:1,riscontrato,alta,,,,resiste | altro agente | x\n", encoding="utf-8")
    run("gap_briefs.py", gb, "--repo", gr)
    b1 = (gb / "smentite" / "smentita-GDPR-001.md")
    files = sorted(x.name for x in (gb / "smentite").glob("*.md"))
    check("gap_briefs: un brief solo per i gap alti riscontrati o confermati senza esito, con le righe citate e le ipotesi dell'area",
          files == ["smentita-GDPR-001.md"] and "return json(await db.member.find())" in b1.read_text(encoding="utf-8")
          and "un altro percorso" in b1.read_text(encoding="utf-8") and "motivazione" not in b1.read_text(encoding="utf-8").split("## Affermazione")[1], str(files))

SBP = ROOT / "tests" / "bench-pa" / "score_bench.py"
if SBP.exists():
    ptruth = json.loads((ROOT / "tests" / "bench-pa" / "truth.json").read_text(encoding="utf-8"))
    pd_ = tmp / "pabench"; pd_.mkdir()
    subprocess.run([sys.executable, str(SBP), "prepare", str(pd_)], capture_output=True, text=True)
    papp = pd_ / "bench-app"
    hint = [str(q.relative_to(papp)) for q in papp.rglob("*") if q.is_file() and ".git" not in q.parts
            and re.search(r"(?i)vulnerab|\bbug\b|flaw|difetto|fixme|todo|violazion|non conform", q.read_text(encoding="utf-8", errors="replace"))]
    check("secondo banco privacy (scuola, PHP): pronto, senza la verità, senza commenti che indichino i difetti",
          (papp / "public" / "privacy.html").exists() and not (papp / "truth.json").exists() and not hint, str(hint))
    pw = tmp / "pa-prepass"
    run("init_gdpr.py", pw); run("gdpr_prepass.py", papp, "--audit", pw)
    forn = (pw / "registro-tool" / "fornitori-bozza.csv").read_text(encoding="utf-8")
    pmap = (pw / "registro-tool" / "processing-map-bozza.csv").read_text(encoding="utf-8")
    pscan = json.loads((pw / "registro-tool" / "privacy-scan.json").read_text(encoding="utf-8"))
    check("prepass GDPR su PHP: fornitori dai percorsi (reCAPTCHA, Maps), Mailgun, YouTube; tabelle dallo schema SQL; log con dati personali",
          all(x in forn for x in ("Google Fonts", "Google reCAPTCHA", "Google Maps", "Mailgun", "YouTube")) and "iscrizioni" in pmap
          and "public/contatti_invia.php" in {x["file"] for x in pscan["log"]}, forn[:400])
    pg = tmp / "pa-perfect"; pg.mkdir()
    (pg / "gaps.csv").write_text("id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n" + "".join(
        f'GDPR-{i:03d},{d["controllo"]},"{d["titolo"]}",{d["file"][0]}:1,confermato da codice/config,alta,,,,\n' for i, d in enumerate(ptruth["difetti"], 1)), encoding="utf-8")
    sp_ = subprocess.run([sys.executable, str(SBP), "score", str(pg)], capture_output=True, text=True)
    check("secondo banco privacy: punteggio pieno sui difetti noti, nessun falso allarme", f"difetti trovati: {len(ptruth['difetti'])}/{len(ptruth['difetti'])}" in sp_.stdout and "falsi allarmi sulle esche: 0/" in sp_.stdout, sp_.stdout[-400:])

if have("refutation_pack.py") and have("gap_briefs.py"):
    gp_ = tmp / "gpack"; gpr = tmp / "gpack-repo"; (gpr / "src").mkdir(parents=True); gp_.mkdir()
    (gpr / "src" / "a.ts").write_text("gtag('config','G-1')\n", encoding="utf-8")
    (gp_ / "gaps.csv").write_text("id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n"
                                  "GDPR-001,E,Analytics senza consenso,src/a.ts:1,confermato da codice/config,alta,tracciamento,art. 122,,non eseguita | nessuno | -\n", encoding="utf-8")
    (gp_ / "gdpr-matrix.csv").write_text("controllo,area,stato,gap,smentita\nE,Cookie,confermato da codice/config,GDPR-001,non eseguita | nessuno | -\n", encoding="utf-8")
    run("refutation_pack.py", "prepara", gp_, "--repo", gpr)
    pkg = gp_ / "smentite" / "pacchetto"
    (pkg / "esiti.json").write_text(json.dumps([{"id": "GDPR-001", "esito": "resiste", "verificatore": "sessione nuova, solo pacchetto", "tentativi": ["cercato un blocco del consenso: assente"]}]), encoding="utf-8")
    ri = run("refutation_pack.py", "importa", gp_, pkg / "esiti.json")
    mx = (gp_ / "gdpr-matrix.csv").read_text(encoding="utf-8"); gx = (gp_ / "gaps.csv").read_text(encoding="utf-8")
    check("pacchetto di smentita (gdpr): brief del gap con smentita «non eseguita», esiti applicati a gaps.csv e alla matrice",
          (pkg / "smentita-GDPR-001.md").exists() and "resiste | sessione nuova" in gx and "resiste | sessione nuova" in mx, ri.stdout + ri.stderr)

if have("gdpr_prepass.py") and have("check_delivery.py") and SBP.exists():
    pcs = (pw / "punti-pericolosi.csv").read_text(encoding="utf-8")
    check("prepass GDPR: punti-pericolosi.csv con una riga per categoria di indizi (tracker, dati particolari, log, fornitori…)",
          all(c in pcs for c in ("tracker e risorse di terzi,", "dati particolari,", "log con dati personali,", "fornitori,")), pcs)
    rc_ = run("check_delivery.py", pw)
    check("chiudi (gdpr): categorie di indizi non chiuse fanno fallire", "FAIL punti pericolosi" in rc_.stdout, rc_.stdout[-500:])

if have("check_matrix.py"):
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location("cm_", SC / "check_matrix.py"); _cm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_cm)
    check("giudizi: «conforme all'informativa» è un confronto fra testi, «il sito è conforme» resta vietato",
          not _cm.GIUDIZI.search("trattamento conforme all'informativa") and _cm.GIUDIZI.search("il sito è conforme") is not None)

if have("merge_audits.py"):
    import importlib.util as _iu2
    _sp2 = _iu2.spec_from_file_location("ma_", SC / "merge_audits.py"); _ma = _iu2.module_from_spec(_sp2); _sp2.loader.exec_module(_ma)
    fa_ = {"titolo": "x", "categoria": "N", "prova": {"riferimenti_file": ["src/api/route.ts:330-346"]}}
    fb_ = {"titolo": "y", "categoria": "N", "prova": {"riferimenti_file": ["src/api/route.ts:313-340"]}}
    fc_ = {"titolo": "z", "categoria": "N", "prova": {"riferimenti_file": ["src/api/route.ts:10-20"]}}
    check("unione: intervalli che si sovrappongono nello stesso file contano come citazione vicina, intervalli lontani no",
          any("sovrapposte" in w for w in _ma.similarity(fa_, fb_)[1]) and not any("sovrapposte" in w for w in _ma.similarity(fa_, fc_)[1]))

import shutil as _shc
try:
    import playwright  # noqa: F401
    _pw = True
except ImportError:
    _pw = False
if have("cookie_scan.py") and _shc.which("php") and _pw and SBP.exists():
    import socket, time as _t
    _s = socket.socket(); _s.bind(("127.0.0.1", 0)); _port = _s.getsockname()[1]; _s.close()
    _srv = subprocess.Popen(["php", "-S", f"127.0.0.1:{_port}", "-t", str(papp / "public")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        _t.sleep(1.0)
        cso = tmp / "cookie-scan"
        u = f"http://127.0.0.1:{_port}/"
        rcs = run("cookie_scan.py", u + "index.php", u + "contatti.php", u + "eventi.php", "--out", cso, "--wait", "2", "--blocca-terzi")
        rep = {r["url"].rsplit("/", 1)[-1]: r for r in json.loads((cso / "cookie-scan.json").read_text(encoding="utf-8"))}
        cls = lambda pg: " ".join(t["classe"] for t in rep[pg]["terze_parti"])
        check("cookie_scan sul sito della scuola (PHP locale, terzi bloccati): YouTube, reCAPTCHA e font in home, Maps nei contatti; "
              "nessun YouTube negli eventi (caricato solo al clic), Matomo locale non è terza parte, PHPSESSID tecnico",
              "video" in cls("index.php") and "reCAPTCHA" in cls("index.php") and "font" in cls("index.php") and "mappe" in cls("contatti.php")
              and "video" not in cls("eventi.php") and not any("statistiche" in t["dominio"] for r in rep.values() for t in r["terze_parti"])
              and all("tecnico" in c["classe"] for r in rep.values() for c in r["cookie"]), rcs.stdout[-600:])
    finally:
        _srv.terminate()

if have("entity_matrix.py") and SBP.exists():
    emo = tmp / "entita-pa.csv"
    run("entity_matrix.py", papp, "--out", emo)
    em_ = {(r["entita"], r["domanda"]): r["prepass"] for r in csv.DictReader(emo.open(encoding="utf-8"))}
    check("matrice per entità (PHP + SQL): contatti cancellati dal job notturno, iscrizioni no, nessuna esportazione nel codice",
          em_.get(("contatti", "cancellazione"), "").startswith("si: cron/pulizia.php") and em_.get(("iscrizioni", "cancellazione"), "").startswith("non trovato")
          and "nessuna esportazione" in em_.get(("contatti", "export"), ""), str(em_)[:400])
    ew = tmp / "entita-audit"; ew.mkdir()
    (ew / "entita.csv").write_text(emo.read_text(encoding="utf-8"), encoding="utf-8")
    (ew / "gaps.csv").write_text("id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n", encoding="utf-8")
    r_e = run("check_delivery.py", ew)
    check("chiudi (gdpr): righe «non trovato» della matrice per entità senza esito fanno fallire", "FAIL matrice per entità" in r_e.stdout, r_e.stdout[-400:])

if have("merge_audits.py") and have("entity_matrix.py"):
    mA, mB = tmp / "mat-A", tmp / "mat-B"
    for d, es in ((mA, ("gap", "ok")), (mB, ("gap", "gap"))):
        d.mkdir()
        (d / "gaps.csv").write_text("id,controllo,titolo,riferimenti,stato,priorita,rischio_interessati,norma,domanda_id,smentita\n"
                                    "GDPR-001,G,Nessuna cancellazione per Lead,src/a.ts:1,confermato da codice/config,media,,,,\n", encoding="utf-8")
        (d / "entita.csv").write_text("entita,dati,fonte,domanda,prepass,esito,gap_id,note\n"
                                      f"Lead,x,s,cancellazione,non trovato,{es[0]},GDPR-001,\nLead,x,s,export,non trovato,{es[1]},,\nUser,x,s,export,si: a.ts:1,,,\n", encoding="utf-8")
    rm_ = run("merge_audits.py", mA, mB, "--etichette", "A,B", "--out", tmp / "mat-U")
    uni = (tmp / "mat-U" / "entita.csv").read_text(encoding="utf-8")
    check("unione: accordo cella per cella sulla matrice per entità (1 su 2 righe aperte) ed entita.csv unita con la provenienza",
          "stesso giudizio (gap o no) su 1/2" in rm_.stdout and "gap per B" in uni, rm_.stdout[-400:])

if have("notice_matrix.py") and SBP.exists():
    nm = (pw / "informativa.csv")
    if not nm.exists():
        run("notice_matrix.py", papp, "--audit", pw)
    im_ = {r["voce"]: r["prepass"] for r in csv.DictReader(nm.open(encoding="utf-8"))}
    check("matrice dell'informativa (scuola): DPO assente, trasferimenti esclusi ma Mailgun e Google nel codice, dati sanitari esclusi ma trattati, Mailgun non nominato",
          im_.get("DPO / RPD", "").startswith("non trovato") and "esclude i trasferimenti" in im_.get("trasferimenti extra-SEE", "")
          and "esclude i dati particolari" in im_.get("dati particolari (art. 9)", "") and im_.get("destinatario: Mailgun", "").startswith("non trovato"), str(im_)[:500])

print(f"\nriusciti: {ok}  falliti: {fail}")
sys.exit(1 if fail else 0)
