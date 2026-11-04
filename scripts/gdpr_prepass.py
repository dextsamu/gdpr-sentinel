#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Pre-passaggio deterministico per gdpr-sentinel: tutti gli strumenti automatici in ordine fisso, prima del lavoro manuale.

Uso:
    python3 gdpr_prepass.py <repo> --audit <cartella-di-lavoro>

Perché: in appsec-sentinel due giri sullo stesso repository concordavano solo sul 20% finché la parte automatica
dipendeva da cosa l'agente decideva di lanciare; con un pre-passaggio fisso e un elenco di aree l'accordo è salito
al 60–64%. Qui l'elenco di aree è la matrice A–N.

Ordine (sempre lo stesso):
  1. draft_ropa.py      -> registro-tool/processing-map-bozza.csv, fornitori-bozza.csv
  2. retention_check.py -> registro-tool/retention-evidenze.csv
  3. privacy_scan.py    -> registro-tool/privacy-scan.json (tracker, cookie, consenso, dati particolari, minori,
                           geolocalizzazione, log, diritti, marketing, documenti)
  4. gdpr-matrix.csv    -> colonna evidenza_tecnica pre-compilata con «[prepass] …» SOLO dove è vuota; lo stato non
                           viene toccato: le evidenze automatiche sono indizi, la decisione resta manuale
Registro dei passi in registro-tool/gdpr-prepass.json. Non modifica il repository e non ne esegue il codice.
Un controllo che ha solo l'evidenza «[prepass]» e nient'altro è considerato non compilato da check_matrix.py.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script, *args):
    t0 = time.time()
    p = subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, timeout=900)
    return {"comando": " ".join([script, *map(str, args)]), "uscita": p.returncode, "secondi": round(time.time() - t0, 1),
            "ultime_righe": (p.stdout.strip().splitlines() or [""])[-2:]}


def top_files(items, n=4):
    c = Counter(x["file"] for x in items)
    return ", ".join(f"{f} ({k})" for f, k in c.most_common(n))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("--audit", type=Path, required=True)
    a = ap.parse_args()
    repo, audit = a.repo.resolve(), a.audit.resolve()
    if not repo.is_dir():
        sys.exit(f"cartella non trovata: {repo}")
    gm = audit / "gdpr-matrix.csv"
    if not gm.exists():
        sys.exit(f"{audit} non sembra una cartella di lavoro (manca gdpr-matrix.csv): creala con init_gdpr.py")
    reg = audit / "registro-tool"
    reg.mkdir(exist_ok=True)
    log = [run("draft_ropa.py", repo, "--out", reg),
           run("retention_check.py", repo, "--out", reg / "retention-evidenze.csv"),
           run("privacy_scan.py", repo, "--json", reg / "privacy-scan.json"),
           run("entity_matrix.py", repo, "--out", audit / "entita.csv")]
    log.append(run("notice_matrix.py", repo, "--audit", audit))   # dopo draft_ropa e privacy_scan, di cui legge i risultati
    log.append(run("access_matrix.py", repo, "--audit", audit))   # dopo entity_matrix: stesse entità

    def rows(p):
        return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []
    pm, forn, ret = rows(reg / "processing-map-bozza.csv"), rows(reg / "fornitori-bozza.csv"), rows(reg / "retention-evidenze.csv")
    ps = json.loads((reg / "privacy-scan.json").read_text(encoding="utf-8")) if (reg / "privacy-scan.json").exists() else {}
    g = lambda k: ps.get(k, [])
    senza = [r for r in ret if any("senza" in str(v).lower() for v in r.values())]
    ev = {
        "A": f"{len(pm)} gruppi di dati personali nello schema e {len(forn)} fornitori nel codice (registro-tool/processing-map-bozza.csv, fornitori-bozza.csv)",
        "C": (f"dati particolari: {len(g('particolari'))} indizi in {len({x['file'] for x in g('particolari')})} file ({top_files(g('particolari'))}); "
              f"minori/date di nascita: {len(g('minori'))} indizi (registro-tool/privacy-scan.json)"),
        "D": f"documenti privacy nel repository: {', '.join(x['file'] for x in g('documenti')[:6]) or 'nessuno trovato'}; confrontarli con A, E, G, I",
        "E": (f"tracker e risorse di terzi: {len(g('tracker'))} ({top_files(g('tracker'))}); scritture di cookie/storage: {len(g('cookie'))}; "
              f"gestione del consenso: {len(g('consenso'))} indizi (registro-tool/privacy-scan.json)"),
        "F": f"cancellazione, esportazione, disattivazione: {len(g('diritti'))} indizi ({top_files(g('diritti'))})",
        "G": f"retention: {len(ret)} voci, {len(senza)} senza evidenza di cancellazione (registro-tool/retention-evidenze.csv)",
        "H": f"log con dati personali: {len(g('log'))} indizi ({top_files(g('log'))}); per la sicurezza vedi appsec-sentinel",
        "I": f"fornitori nel codice: {', '.join(r.get('fornitore', '') for r in forn[:8]) or 'nessuno'} (registro-tool/fornitori-bozza.csv)",
        "J": f"{len(forn)} fornitori da verificare per sede e trasferimenti; risorse di terzi caricate dal browser: {len(g('tracker'))}",
        "M": f"marketing e consensi: {len(g('marketing'))} indizi ({top_files(g('marketing'))})",
        "N": f"geolocalizzazione: {len(g('geolocalizzazione'))} indizi ({top_files(g('geolocalizzazione'))})",
    }
    # Una riga da chiudere per categoria di indizi (come punti-pericolosi.csv di appsec-sentinel): due giri sullo stesso
    # gestionale vedevano in metà dei casi cause diverse perché uno dei due non apriva un'intera categoria (log, GPS,
    # video incorporati, dati sanitari). Chiudere ogni categoria con un gap o un «non difetto» motivato le fa aprire a tutti.
    import punti
    CATS = [("tracker e risorse di terzi", "tracker"), ("cookie e archiviazione nel browser", "cookie"), ("dati particolari", "particolari"),
            ("minori e date di nascita", "minori"), ("geolocalizzazione", "geolocalizzazione"), ("log con dati personali", "log"),
            ("diritti: cancellazione ed esportazione", "diritti"), ("marketing e consensi", "marketing")]
    out_lines, cats = [], []
    for nome, k in CATS:
        per, righe = {}, []
        for x in g(k):
            per[x["file"]] = per.get(x["file"], 0) + 1
            if per[x["file"]] <= 2:
                righe.append(f"{x['file']}:{x.get('riga', '')}".rstrip(":"))
        if righe:
            out_lines += [f"## {nome}: {len(righe)}" + (" (primi 40)" if len(righe) > 40 else "")] + righe[:40]
            cats.append((nome, len(righe)))
    fr = [x.strip() for r in forn for x in re.split(r"[;,]\s*", r.get("evidenza_nel_codice", "")) if ":" in x and not x.startswith("package.json")]
    if forn:
        out_lines += [f"## fornitori: {len(forn)}"] + (fr[:40] or ["package.json"])
        cats.append(("fornitori", len(forn)))
    # Temi documentali, sempre presenti anche senza indizi nel codice: nei giri reali sullo stesso gestionale le cause
    # viste da un giro solo erano soprattutto qui (informativa, registro e DPIA, data breach, segreti versionati).
    docs = [x["file"] for x in g("documenti")]
    def pick(rx):
        return [f for f in docs if re.search(rx, f, re.I)]
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True).stdout.splitlines() if (repo / ".git").exists() else \
        [str(q.relative_to(repo)).replace("\\", "/") for q in repo.rglob(".env*") if q.is_file()]   # con Git: solo i file versionati
    envs = sorted(f for f in tracked if re.search(r"(^|/)\.env(\.[\w.-]+)?$", f) and not re.search(r"(example|sample|template|dist)$", f, re.I)
                  and "node_modules/" not in f)
    for nome, fl in (("informativa e trasparenza (D): titolare, DPO, basi, destinatari, trasferimenti, tempi, diritti", pick(r"privacy|informativ|policy|cookie")),
                     ("governance (K): registro dei trattamenti, DPIA, nomine, accordi art. 28", pick(r"dpia|registro|ropa|nomin|dpa|accordo|art\.?_?28|governance")),
                     ("data breach (L): procedura, registro delle violazioni, log per ricostruire", pick(r"breach|violazion|incident")),
                     ("segreti e configurazioni versionate (art. 32)", envs)):
        out_lines += [f"## {nome}: {len(fl)}"] + fl[:40]
        cats.append((nome, len(fl)))
    (reg / "punti-pericolosi.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    punti.write(audit, cats)

    # (1.3.3 scriveva anche letture.csv, un elenco fisso di file da leggere: +30% di tempo senza effetto misurabile
    # sull'accordo; sostituito da entita.csv, che fissa le domande invece dei file.)

    mrows = list(csv.DictReader(gm.open(encoding="utf-8")))
    fields = list(mrows[0].keys()) if mrows else []
    filled = []
    for r in mrows:
        c = (r.get("controllo") or "").strip().upper()
        if c in ev and not (r.get("evidenza_tecnica") or "").strip():
            r["evidenza_tecnica"] = "[prepass] " + ev[c]
            filled.append(c)
    with gm.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(mrows)
    (reg / "gdpr-prepass.json").write_text(json.dumps({"repo": str(repo), "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "passi": log},
                                                      indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"pre-passaggio GDPR completato: {len(pm)} gruppi di dati, {len(forn)} fornitori, {len(ret)} voci di retention, "
          f"{sum(len(v) for v in ps.values())} indizi privacy")
    print(f"matrice pre-compilata (solo evidenza tecnica): {', '.join(filled) or 'nessun controllo (già compilati)'}; B, K, L e lo stato di tutti restano manuali")
    print("Gli indizi non sono gap: ognuno va letto, e ogni gap va scritto in gaps.csv con file e riga.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
