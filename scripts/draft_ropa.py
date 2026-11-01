#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Bozza del registro dei trattamenti (art. 30) e dell'elenco fornitori ricavata dal codice.

Uso:
    python3 draft_ropa.py <repo> [--out cartella]

Produce (tutto in stato «ipotesi da validare», mai come registro definitivo):
  processing-map-bozza.csv   una riga per gruppo di dati personali trovati nello schema (Prisma, Django, SQL)
  fornitori-bozza.csv        servizi di terzi rilevati da dipendenze, variabili d'ambiente e URL nel codice
Il codice mostra cosa il software può trattare e a chi può inviare dati, non chi è titolare o responsabile,
né le basi giuridiche, né i paesi: quelle colonne restano «da verificare con il titolare». Sola lettura.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

SKIP = {"node_modules", ".git", ".next", "dist", "build", "vendor", "__pycache__", ".venv", "coverage"}
SUPPLIERS = {
    "twilio": ("Twilio", "messaggistica (SMS/WhatsApp)", "numero di telefono, testo dei messaggi"), "@sendgrid": ("SendGrid", "invio email", "email, contenuto"),
    "nodemailer": ("Server SMTP configurato", "invio email", "email, contenuto"), "resend": ("Resend", "invio email", "email, contenuto"),
    "stripe": ("Stripe", "pagamenti", "dati di pagamento, email"), "@sentry": ("Sentry", "monitoraggio errori", "indirizzi IP, identificativi, contesto d'errore"),
    "posthog": ("PostHog", "analytics", "eventi, identificativi"), "mixpanel": ("Mixpanel", "analytics", "eventi, identificativi"),
    "firebase": ("Google Firebase", "backend/notifiche", "identificativi, token dispositivo"), "aws-sdk": ("Amazon Web Services", "hosting/storage", "dati archiviati"),
    "@aws-sdk": ("Amazon Web Services", "hosting/storage", "dati archiviati"), "googleapis": ("Google (API)", "servizi Google (es. Drive, Calendar)", "file, calendari"),
    "@google-cloud": ("Google Cloud", "hosting/storage", "dati archiviati"), "web-push": ("Servizi push del browser (Google/Mozilla/Apple)", "notifiche push", "token di sottoscrizione"),
    "openai": ("OpenAI", "intelligenza artificiale", "testi inviati al modello"), "@anthropic-ai": ("Anthropic", "intelligenza artificiale", "testi inviati al modello"),
    "next-auth": ("Provider OAuth configurati", "autenticazione", "identificativi e profilo"), "@auth/": ("Provider OAuth configurati", "autenticazione", "identificativi e profilo"),
    "@vercel": ("Vercel", "hosting/analytics", "log, metriche"), "cloudinary": ("Cloudinary", "media", "immagini"), "algolia": ("Algolia", "ricerca", "query, contenuti indicizzati"),
    "mailchimp": ("Mailchimp", "email marketing", "email, profilo"), "@hubspot": ("HubSpot", "CRM/marketing", "contatti"), "intercom": ("Intercom", "chat", "messaggi, identificativi"),
}
HOST_CLASS = {"fonts.googleapis.com": ("Google Fonts", "font di terzi", "indirizzo IP del visitatore"), "fonts.gstatic.com": ("Google Fonts", "font di terzi", "indirizzo IP del visitatore"),
              "googletagmanager.com": ("Google Tag Manager", "tag manager", "IP, identificativi"), "google-analytics.com": ("Google Analytics", "analytics", "IP, identificativi, eventi"),
              "maps.googleapis.com": ("Google Maps", "mappe", "coordinate, IP"), "api.twilio.com": ("Twilio", "messaggistica", "telefono, messaggi"),
              "drive.google.com": ("Google Drive", "archiviazione", "file"), "www.googleapis.com": ("Google (API)", "servizi Google", "dati dei servizi"),
              "mailchimp.com": ("Mailchimp", "email marketing", "email, profilo"), "sentry.io": ("Sentry", "monitoraggio errori", "IP, identificativi, contesto d'errore"),
              "hotjar.com": ("Hotjar", "analytics/registrazione sessioni", "interazioni, IP"), "clarity.ms": ("Microsoft Clarity", "registrazione sessioni", "interazioni, IP"),
              "connect.facebook.net": ("Meta Pixel", "marketing", "IP, eventi"), "youtube.com": ("YouTube", "video incorporati", "IP, cookie"),
              "brevo.com": ("Brevo", "email marketing", "email, profilo"), "sendinblue.com": ("Brevo", "email marketing", "email, profilo"),
              "mailgun.net": ("Mailgun", "invio email", "email, contenuto dei messaggi"), "api.sendgrid.com": ("SendGrid", "invio email", "email, contenuto"),
              "youtube-nocookie.com": ("YouTube (modalità senza cookie)", "video incorporati", "IP"), "player.vimeo.com": ("Vimeo", "video incorporati", "IP, cookie"),
              "hcaptcha.com": ("hCaptcha", "anti-bot", "IP, dati del browser"), "challenges.cloudflare.com": ("Cloudflare Turnstile", "anti-bot", "IP, dati del browser")}
# servizi riconoscibili solo dal percorso (stesso host www.google.com)
PATH_CLASS = [(r"(www\.)?google\.com/recaptcha|gstatic\.com/recaptcha", ("Google reCAPTCHA", "anti-bot", "IP, dati del browser e di navigazione")),
              (r"(www\.)?google\.com/maps", ("Google Maps", "mappe", "IP, posizione cercata"))]
CODE_SUFFIX = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".css", ".html", ".htm", ".py", ".php", ".rb", ".go", ".java",
               ".cs", ".twig", ".erb", ".jsp", ".cshtml", ".aspx", ".env", ".example", ".md", ".yml", ".yaml", ".json"}
GROUPS = {
    "Identificativi e contatti": r"email|telefon|phone|cellulare|cognome|surname|lastname|firstname|username|indirizzo|address|zip|(^|_)nome$|(^|_)name$|nominativ",
    "Dati anagrafici e documenti": r"nasc|birth|codicefiscale|cf\b|fiscalcode|documento|passport|carta|patente|tessera",
    "Geolocalizzazione": r"\blat\b|\blng\b|gps|latitud|longitud|geoloc|position",
    "Dati di accesso e tecnici": r"password|hash|token|session|ipaddress|\bip\b|useragent|mfa|totp|webauthn|credential",
    "Dati finanziari": r"iban|card|carta|pagament|payment|fattur|invoice|stipend|salary|importo",
    "Dati di salute o categorie particolari": r"salute|health|malattia|certificat|sanit|medic|invalid|disabil|religio|sindacat|etnic|orientament",
    "Lavoro e presenze": r"turno|timbratur|presenz|ferie|assenza|straordinari|banca\s?ore|qualific|mansion|disponibil",
}


def files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP):
            yield p


def models(root: Path):
    out = []
    for p in files(root):
        if p.suffix == ".sql":   # schema SQL (anche PHP, Laravel, Django senza models.py): CREATE TABLE nome (campi …)
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"(?is)create\s+table\s+(?:if\s+not\s+exists\s+)?[`\"\[]?(\w+)[`\"\]]?\s*\((.*?)\)\s*;", txt):
                cols = [c for c in re.findall(r"(?m)^\s*[`\"\[]?(\w+)[`\"\]]?\s+[A-Za-z]", m.group(2))
                        if c.upper() not in {"PRIMARY", "KEY", "UNIQUE", "CONSTRAINT", "FOREIGN", "INDEX", "CHECK"}]
                for extra in re.findall(r",\s*[`\"\[]?(\w+)[`\"\]]?\s+(?:VARCHAR|CHAR|TEXT|INT|DATE|DATETIME|TINYINT|DECIMAL|ENUM|BOOLEAN|MEDIUMTEXT)", m.group(2), re.I):
                    if extra not in cols:
                        cols.append(extra)
                out.append((m.group(1), cols, str(p.relative_to(root))))
        elif p.suffix == ".prisma":
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"^model\s+(\w+)\s*\{(.*?)^\}", txt, re.S | re.M):
                out.append((m.group(1), re.findall(r"^\s+(\w+)\s+\w+", m.group(2), re.M), str(p.relative_to(root))))
        elif p.suffix == ".py" and p.name == "models.py":
            txt = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"^class\s+(\w+)\(.*?Model\):(.*?)(?=^class\s|\Z)", txt, re.S | re.M):
                out.append((m.group(1), re.findall(r"^\s+(\w+)\s*=\s*models\.", m.group(2), re.M), str(p.relative_to(root))))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("--out", type=Path, default=Path("."))
    a = ap.parse_args()
    if not a.repo.is_dir():
        sys.exit(f"cartella non trovata: {a.repo}")
    a.out.mkdir(parents=True, exist_ok=True)
    # trattamenti
    rows, n = [], 0
    for name, fields, src in models(a.repo):
        hit = {g: [f for f in fields if re.search(rx, f, re.I)] for g, rx in GROUPS.items()}
        hit = {g: v for g, v in hit.items() if v}
        if not hit:
            continue
        n += 1
        cats = "; ".join(f"{g}: {', '.join(v[:5])}" for g, v in hit.items())
        special = "Dati di salute o categorie particolari" in hit
        rows.append({"id": f"T{n:02d}", "trattamento": f"da definire: dati gestiti dal modello «{name}»", "dati_e_interessati": cats + " · interessati da identificare",
                     "finalita": "da verificare con il titolare", "ruoli": "da verificare", "base_giuridica_e_condizione": "da verificare" + (" (possibile art. 9: verificare condizione)" if special else ""),
                     "sistemi_e_destinatari": f"{src}", "paesi_e_trasferimenti": "da verificare (vedi fornitori-bozza.csv)", "retention": "da verificare (vedi retention_check.py)",
                     "diritti_e_controlli": "da verificare", "evidenze": f"{src} · modello {name}", "gap": "ipotesi da validare: bozza ricavata solo dai nomi dei campi"})
    # fornitori
    sup = {}
    pk = a.repo / "package.json"
    if pk.exists():
        try:
            d = json.loads(pk.read_text(encoding="utf-8"))
            deps = {**d.get("dependencies", {}), **d.get("devDependencies", {})}
            for dep in deps:
                for k, v in SUPPLIERS.items():
                    if dep == k or dep.startswith(k):
                        sup.setdefault(v[0], {"tipo": v[1], "dati": v[2], "ev": set()})["ev"].add(f"package.json: {dep}")
        except json.JSONDecodeError:
            pass
    rx = re.compile(r"https?://([a-z0-9.-]+\.[a-z]{2,})(/[^\s'\"<>)]*)?")
    for p in files(a.repo):
        if p.suffix.lower() not in CODE_SUFFIX and "env" not in p.name:
            continue
        if p.stat().st_size > 400000:
            continue
        rel = str(p.relative_to(a.repo))
        if "package-lock" in rel or "node_modules" in rel:
            continue
        for ln, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for h, path in rx.findall(line):
                key = next((k for k in HOST_CLASS if h == k or h.endswith("." + k)), None)   # anche i sottodomini (www., us21.api.)
                v = HOST_CLASS[key] if key else next((c for r_, c in PATH_CLASS if re.match(r_, h + path)), None)
                if v:
                    sup.setdefault(v[0], {"tipo": v[1], "dati": v[2], "ev": set()})["ev"].add(f"{rel}:{ln}")
    with (a.out / "processing-map-bozza.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "trattamento", "dati_e_interessati", "finalita", "ruoli", "base_giuridica_e_condizione", "sistemi_e_destinatari", "paesi_e_trasferimenti", "retention", "diritti_e_controlli", "evidenze", "gap"])
        w.writeheader(); w.writerows(rows)
    with (a.out / "fornitori-bozza.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fornitore", "tipo_servizio", "dati_probabilmente_trattati", "evidenza_nel_codice", "ruolo_privacy", "paese_e_trasferimento", "dpa_o_accordo", "stato"])
        for k, v in sorted(sup.items()):
            w.writerow([k, v["tipo"], v["dati"], "; ".join(sorted(v["ev"])[:5]), "da verificare (responsabile o autonomo titolare?)", "da verificare", "da verificare", "ipotesi da validare"])
    print(f"trattamenti in bozza: {len(rows)}  fornitori rilevati: {len(sup)}  -> {a.out}")
    print("Sono ipotesi dai nomi dei campi e dalle dipendenze: ruoli, basi giuridiche e paesi vanno confermati col titolare.")


if __name__ == "__main__":
    main()
