#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Matrice dell'informativa: ciò che le informative dichiarano, voce per voce, contro ciò che il codice fa.

Uso:
    python3 notice_matrix.py <repo> --audit <cartella-audit>      # dopo draft_ropa.py e privacy_scan.py (pre-passaggio)

Scrive <cartella-audit>/informativa.csv, una riga per voce, con le stesse colonne di entita.csv
(voce, dettaglio, prepass, esito, gap_id, note). Perché: dopo la matrice per entità, le differenze fra due giri sullo
stesso gestionale stavano nei temi dell'informativa (destinatari, trasferimenti, dati particolari, versioni divergenti):
ogni giro confrontava le voci che gli capitavano. Qui le voci sono fisse e la prima risposta è meccanica:

  - una riga per ogni fornitore trovato nel codice e per ogni risorsa di terzi caricata dal browser: il nome compare
    in qualche informativa del repository?
  - voci fisse: titolare e contatti, DPO/RPD, basi giuridiche, trasferimenti extra-SEE, tempi di conservazione,
    diritti e reclamo; dati particolari e geolocalizzazione se il codice li tratta; più versioni dell'informativa.

«si: <file>» vuol dire che la parola chiave c'è, non che la voce sia corretta: l'agente controlla che dica il vero.
«non trovato» va chiuso con esito (ok, gap con gap_id, non applicabile, non verificabile con motivo).
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

SKIP = {"node_modules", ".git", ".next", "dist", "build", "vendor", "__pycache__", ".venv", "venv", "coverage"}
DOC_NAME = re.compile(r"(privacy|informativ|policy|cookie|gdpr|dati-personali|trattamento)", re.I)
DOC_EXT = {".md", ".mdx", ".html", ".htm", ".tsx", ".jsx", ".astro", ".vue", ".svelte", ".php", ".txt", ".sql", ".ts", ".js"}
# fornitori con sede o gruppo fuori dal SEE (indicativo: la sede del trattamento va verificata)
EXTRA_SEE = re.compile(r"(google|youtube|meta|facebook|instagram|whatsapp|telegram|mailgun|sendgrid|mailchimp|twilio|stripe|sentry|"
                       r"amazon|aws|microsoft|azure|cloudflare|vercel|openai|anthropic|hubspot|intercom|hotjar|clarity|posthog|mixpanel|algolia|cloudinary|vimeo)", re.I)
NOT_NOTICE = re.compile(r"(stato|piano|riepilogo|aggiornamento|setup|implementazion|deployment|(^|/)security/|checklist|report|todo|nis2|"
                        r"readme|changelog|guida|guide|runbook|analisi|audit|migration|test)", re.I)
GENERIC = {"server", "configurato", "configurati", "servizi", "servizio", "provider", "del", "di", "the", "api", "modalità", "senza", "cookie", "browser"}
NEGA_TRASF = re.compile(r"(non (trasferiamo|trasferisce|vengono trasferiti|sono trasferiti)|nessun trasferimento|non (escono|lasciano)|"
                        r"esclusivamente (in italia|nell'unione|nel see|nell'ue)|solo (in italia|nell'unione|nel see|nell'ue))", re.I)
NEGA_PART = re.compile(r"non (raccogli\w*|trattiamo|tratta|tratt\w*)[^.]{0,60}(salute|sanitar|particolar)", re.I)
FIXED = [
    ("titolare e contatti", r"titolare|controller"),
    ("DPO / RPD", r"\bdpo\b|\brpd\b|responsabile della protezione|data protection officer"),
    ("basi giuridiche", r"base giuridica|basi giuridiche|art\.?\s*6|legittimo interesse|esecuzione del contratto|obbligo di legge|legal basis"),
    ("trasferimenti extra-SEE", r"extra[- ]?(ue|see|ee)|fuori dall?['’ ]?(unione|ue|see|spazio)|trasferiment|stati uniti|\busa\b|data privacy framework|\bdpf\b|clausole contrattuali|scc"),
    ("tempi di conservazione", r"conservat|conservazione|retention|per \d+ (giorni|mesi|anni)|\d+ (giorni|mesi|anni)"),
    ("diritti e reclamo", r"diritt[oi]|reclamo|garante|art\.?\s*1[5-9]|art\.?\s*2[0-2]"),
]


def strip(t):
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--audit", type=Path, required=True)
    a = ap.parse_args()
    repo, audit = a.repo.resolve(), a.audit.resolve()
    reg = audit / "registro-tool"
    docs = {}
    for p in repo.rglob("*"):
        rel = p.relative_to(repo)
        if not p.is_file() or set(rel.parts) & SKIP or p.suffix.lower() not in DOC_EXT or not DOC_NAME.search(str(rel)):
            continue
        rp = rel.as_posix()
        if NOT_NOTICE.search(rp):
            continue   # documenti interni di progetto (stato, piani, guide, sicurezza): non sono informative per gli interessati
        if re.search(r"(^|/)(api|lib|scripts|migrations|tests?)/", rp) and p.suffix.lower() not in {".md", ".mdx", ".html", ".htm", ".sql"} \
                and not re.search(r"(privacy-?policy|informativ)", p.name, re.I):
            continue   # codice che parla di privacy (route, utilità) non è un'informativa; un seed con il testo dell'informativa sì
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(txt) < 400:
            continue
        docs[rel.as_posix()] = strip(txt).lower()
    def where(rx):
        return [f for f, t in docs.items() if re.search(rx, t, re.I)]
    rows = []
    def row(voce, dett, hits, extra=""):
        rows.append([voce, dett, (f"si: {'; '.join(hits[:3])}" if hits else ("non trovato" + extra)), "", "", ""])
    note_docs = "" if docs else " (nessuna informativa trovata nel repository)"
    rows.append(["versioni dell'informativa", f"{len(docs)} documenti", ("n/a (una sola)" if len(docs) <= 1 else
                 f"non trovato: {len(docs)} documenti ({'; '.join(list(docs)[:6])}): verificare che non si contraddicano"), "", "", ""])
    fp0 = reg / "fornitori-bozza.csv"
    extra_see = sorted({r.get("fornitore", "") for r in csv.DictReader(fp0.open(encoding="utf-8")) if EXTRA_SEE.search(r.get("fornitore", ""))}) if fp0.exists() else []
    for voce, rx in FIXED:
        if voce == "trasferimenti extra-SEE" and extra_see:
            neg = [f for f, t in docs.items() if NEGA_TRASF.search(t)]
            if neg:
                rows.append([voce, f"fornitori probabilmente extra-SEE nel codice: {', '.join(extra_see[:5])}",
                             f"non trovato: {'; '.join(neg[:3])} esclude i trasferimenti, ma il codice usa fornitori probabilmente extra-SEE", "", "", ""])
                continue
        row(voce, "", where(rx), note_docs)
    try:
        ps = json.loads((reg / "privacy-scan.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        ps = {}
    code_files = lambda k: sorted({x["file"] for x in ps.get(k, []) if not DOC_NAME.search(x["file"])})
    if code_files("particolari"):
        neg = [f for f, t in docs.items() if NEGA_PART.search(t)]
        if neg:
            rows.append(["dati particolari (art. 9)", f"nel codice: {', '.join(code_files('particolari')[:3])}",
                         f"non trovato: {'; '.join(neg[:3])} esclude i dati particolari, ma il codice li tratta", "", "", ""])
        else:
            row("dati particolari (art. 9)", f"nel codice: {', '.join(code_files('particolari')[:3])}", where(r"salute|sanitar|particolari|art\.?\s*9|malatti|biometric|sindacal|religio"), note_docs)
    if code_files("geolocalizzazione"):
        row("geolocalizzazione", f"nel codice: {', '.join(code_files('geolocalizzazione')[:3])}", where(r"geoloc|\bgps\b|posizione|coordinate|location"), note_docs)
    forn = []
    fp = reg / "fornitori-bozza.csv"
    if fp.exists():
        forn = [r for r in csv.DictReader(fp.open(encoding="utf-8"))]
    seen = set()
    for r in forn:
        nome = r.get("fornitore", "").strip()
        if not nome or nome.lower() in seen:
            continue
        seen.add(nome.lower())
        parole = [w for w in re.findall(r"[a-zà-ù0-9]{3,}", nome.lower()) if w not in GENERIC]
        if re.fullmatch(r"[\w.-]+\.[a-z]{2,}", nome.lower()):   # fornitore indicato col dominio (ip-api.com): si cerca il dominio
            hits = [f for f, t in docs.items() if nome.lower() in t]
        else:
            hits = [f for f, t in docs.items() if parole and all(w in t for w in parole)]
        extra = " · fornitore probabilmente extra-SEE" if EXTRA_SEE.search(nome) else ""
        row(f"destinatario: {nome}", (r.get("tipo_servizio", "") + extra).strip(" ·"), hits, note_docs)
    for host in sorted({re.sub(r"^www\.", "", x["indizio"].split("/")[0]) for x in ps.get("tracker", []) if "." in x.get("indizio", "")}):
        if host.lower() in seen:
            continue
        seen.add(host.lower())
        base = host.split(".")[-2] if host.count(".") >= 1 else host
        if base in ("google", "googleapis", "gstatic"):   # «Google» compare ovunque: cerca il servizio
            base = {"fonts.googleapis.com": "font", "fonts.gstatic.com": "font"}.get(host, host.split(".")[0])
        row(f"risorsa di terzi nel browser: {host}", "caricata dalle pagine", where(re.escape(base)), note_docs)
    out = audit / "informativa.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["voce", "dettaglio", "prepass", "esito", "gap_id", "note"])
        w.writerows(rows)
    aperte = sum(1 for r in rows if not r[2].startswith(("si", "n/a")))
    print(f"matrice dell'informativa: {len(docs)} documenti, {len(rows)} voci, {aperte} da guardare")
    return 0


if __name__ == "__main__":
    sys.exit(main())
