#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Ricerca statica degli indizi privacy nel codice, per categoria, con file e riga (mai i valori).

Uso:
    python3 privacy_scan.py <repo> [--json privacy-scan.json]

Categorie (ognuna collegata a un controllo della matrice A–N):
  tracker      (E/J) script e risorse di terzi: analytics, pixel, font e mappe da CDN, video incorporati, CDN di librerie
  cookie       (E)   scritture di cookie e di localStorage/sessionStorage, con il nome se è scritto nel codice
  consenso     (E)   librerie o componenti di gestione del consenso
  particolari  (C)   campi e modelli con dati di salute, religione, etnia, orientamento, sindacato, penali, biometrici
  minori       (C)   date di nascita ed età
  geolocalizzazione (N/G) posizione del dispositivo, coordinate GPS
  log          (H)   chiamate di log che citano dati personali (email, telefono, codice fiscale, IP, utente intero)
  diritti      (F)   cancellazione dell'account, esportazione dei dati, disattivazione al posto della cancellazione
  marketing    (M/B) newsletter, marketing, consensi pre-spuntati
  documenti    (D)   informativa, cookie policy, termini, pagine privacy presenti nel repository
Le categorie si cercano solo nei file di codice (nella documentazione sono parole, non comportamenti); i log di test,
seed e script di manutenzione sono esclusi. È euristico e deterministico (stesso repository, stesso risultato): ogni riga è un indizio da leggere, non un gap.
Sola lettura; salta dipendenze e build.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKIP = {"node_modules", ".git", ".next", "dist", "build", "vendor", "__pycache__", ".venv", "venv", "coverage", ".turbo", "out"}
EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".htm", ".py", ".php", ".rb", ".go", ".java",
       ".cs", ".prisma", ".sql", ".md", ".mdx", ".json", ".yml", ".yaml", ".env", ".txt"}
CODE = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".htm", ".py", ".php", ".rb", ".go", ".java", ".cs", ".prisma", ".sql"}
CAT = {
    "tracker": re.compile(r"(?i)(google-analytics\.com|googletagmanager\.com|gtag\(|\bga\(['\"]|fbq\(|connect\.facebook\.net|hotjar|clarity\.ms|"
                          r"fonts\.googleapis\.com|fonts\.gstatic\.com|youtube\.com/embed|youtube-nocookie|player\.vimeo\.com|maps\.googleapis\.com|"
                          r"google\.com/maps/embed|recaptcha|intercom|snap\.licdn|static\.ads-twitter|analytics\.tiktok|matomo|plausible\.io|"
                          r"cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|@vercel/analytics|posthog|mixpanel|segment\.(com|io)|"
                          r"@next/third-parties|next/script[^\n]*(googletag|analytics))"),
    "cookie": re.compile(r"(document\.cookie\s*=|cookies\(\)\)?\.set\(|\.cookies\.set\(|setCookie\(|res\.cookie\(|response\.set_cookie|"
                         r"localStorage\.setItem\(|sessionStorage\.setItem\()"),
    "consenso": re.compile(r"(?i)(cookieconsent|cookie-consent|cookiebot|onetrust|iubenda|klaro|tarteaucitron|consentmanager|"
                           r"\bconsent(Given|Status|State)?\b|banner[-_ ]?cookie|cookie[-_ ]?banner)"),
    "particolari": re.compile(r"(?i)\b\w*(salute|healthData|healthRecord|medical\w*|medic[oi]\b|diagnos\w*|malatti\w*|certificat\w*medic\w*|patolog\w*|disabilit(?!at)\w*|disabil[ei]\b|invalidit\w*|handicap|"
                              r"religio\w*|etni\w*|ethnic\w*|razz\w*|orientament\w*|sexual\w*|sessual\w*|sindacat\w*|trade.?union|"
                              r"penal\w*|criminal\w*|casellario|biometr\w*|genetic\w*|gravidanz\w*|pregnan\w*|allerg\w*|farmac\w*|terapi\w*)\w*\b"),
    "minori": re.compile(r"(?i)\b(data_?nascita|dataDiNascita|birth_?date|birthday|date_?of_?birth|\bdob\b|eta_?minima|minorenn\w*|minor\b|"
                         r"parental|genitor\w*|tutore)"),
    "geolocalizzazione": re.compile(r"(?i)(navigator\.geolocation|getCurrentPosition|watchPosition|\bgps_?lat\w*|\bgps_?l(ng|on)\w*|"
                                    r"\blatitude\b|\blongitude\b|\b(lat|lng|lon)\s*[,}]|geofenc\w*|geolocat\w*)"),
    "log": re.compile(r"(?i)(console\.(log|info|warn|error|debug)|logger\.(info|debug|warn|error|log)|\bprint\(|log\.(info|debug|warn|error))"
                      r"[^\n]{0,200}\b(email|e-mail|phone|telefono|cellulare|codice_?fiscale|codiceFiscale|\bcf\b|ip_?address|\bip\b|"
                      r"indirizzo|address|password|iban|user\b|utente\b|body\b|req\.body|payload)"),
    "diritti": re.compile(r"(?i)((delete|elimina|cancella)\w*[_-]?(account|utente|user|profil\w*|me\b)|"
                          r"(export|esporta)\w*[_-]?(data|dati|account|utente|user|personal)|portabil\w*|right.?to.?(erasure|access)|"
                          r"isActive\s*:\s*false|deletedAt\s*:\s*new Date|anonimi[sz]\w*|pseudonim\w*)"),
    "marketing": re.compile(r"(?i)(newsletter|marketing|mailchimp|brevo|sendinblue|mailerlite|"
                            r"(defaultChecked|checked|default)\s*[:=]\s*(true|\{true\})[^\n]{0,80}(newsletter|marketing|privacy|consens)|"
                            r"(newsletter|marketing|consens\w*)[^\n]{0,80}(defaultChecked|default\s*[:=]\s*true|@default\(true\)))"),
}
DOC_NAME = re.compile(r"(?i)(privacy|informativa|cookie[-_ ]?policy|gdpr|termini|terms|data[-_ ]?protection|trattamento[-_ ]?dati)")


def scan(root):
    res = {k: [] for k in list(CAT) + ["documenti"]}
    for p in sorted(root.rglob("*")):
        if not p.is_file() or SKIP & set(p.relative_to(root).parts):
            continue
        rel = p.relative_to(root).as_posix()
        if DOC_NAME.search(p.name) and p.suffix.lower() in {".md", ".mdx", ".tsx", ".jsx", ".html", ".htm", ".txt", ".pdf", ".vue", ".svelte"}:
            res["documenti"].append({"file": rel, "riga": 0, "indizio": "documento o pagina privacy"})
        if p.suffix.lower() not in EXT and not p.name.startswith(".env"):
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            if len(line) > 1500:
                continue
            for k, rx in CAT.items():
                if p.suffix.lower() not in CODE:
                    continue   # indizi solo nel codice: nella documentazione sono parole, non comportamenti
                if k == "log" and re.search(r"(?i)(^|/)(tests?|__tests__|e2e|spec|seeds?|scripts|scratch)/|seed[^/]*\.\w+$", rel):
                    continue   # log di test, seed e script di manutenzione: non girano per gli utenti
                m = rx.search(line)
                if not m:
                    continue
                ind = m.group(0)[:60]
                if k == "cookie":
                    nm = re.search(r"(?:set\w*\(|cookie\s*=\s*)\s*['\"`]([\w.-]{1,40})", line[m.start():])
                    ind = f"{m.group(0).strip()} {nm.group(1) if nm else ''}".strip()
                res[k].append({"file": rel, "riga": n, "indizio": ind})
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    if not a.repo.is_dir():
        sys.exit(f"cartella non trovata: {a.repo}")
    res = scan(a.repo)
    for k, v in res.items():
        files = sorted({x["file"] for x in v})
        print(f"{k:18} {len(v):4} indizi in {len(files):3} file" + (f"  (es. {', '.join(files[:3])})" if files else ""))
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"scritto: {a.json}")
    print("Indizi, non gap: ognuno va letto e valutato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
