#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Scansione dinamica di cookie, storage e richieste a terzi di una pagina, PRIMA di qualsiasi interazione.

Uso:
    python3 cookie_scan.py <URL> [<URL> ...] [--out cartella] [--autorizzato] [--wait 4]

Cosa fa: apre ogni URL in un browser pulito (Chromium headless, senza cookie né consenso), non clicca nulla,
aspetta il caricamento e registra: cookie impostati (nome, dominio, durata, flag, MAI il valore), chiavi di
localStorage/sessionStorage, richieste verso domini di terzi con tipo di risorsa, e una classificazione
indicativa dei domini noti (analytics, pubblicità, font/CDN di terzi, social, video).
Questa è la prova più forte per confrontare informativa e banner con ciò che parte davvero prima del consenso.

Regole: URL locali (localhost, 127.0.0.1, *.localhost, *.test) liberi; ogni altro URL richiede --autorizzato,
cioè la conferma che il titolare ha autorizzato la scansione. Nessun login, nessun invio di form, nessuna
interazione con il banner. Richiede: pip install playwright && playwright install chromium.
Esito indicativo: la classificazione dei domini non è un parere legale sulla necessità del consenso.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

KNOWN = {
    "google-analytics.com": "analytics", "googletagmanager.com": "tag manager", "analytics.google.com": "analytics",
    "doubleclick.net": "pubblicità", "googlesyndication.com": "pubblicità", "facebook.net": "social/pubblicità", "facebook.com": "social/pubblicità",
    "connect.facebook.net": "social/pubblicità", "hotjar.com": "analytics/sessioni", "clarity.ms": "analytics/sessioni", "linkedin.com": "social/pubblicità",
    "licdn.com": "social", "twitter.com": "social", "t.co": "social", "tiktok.com": "social/pubblicità", "youtube.com": "video (cookie di terzi)",
    "youtube-nocookie.com": "video", "ytimg.com": "video", "vimeo.com": "video", "fonts.googleapis.com": "font di terzi (IP verso Google)",
    "fonts.gstatic.com": "font di terzi (IP verso Google)", "cdnjs.cloudflare.com": "CDN di terzi", "cdn.jsdelivr.net": "CDN di terzi",
    "unpkg.com": "CDN di terzi", "maps.googleapis.com": "mappe (dati verso Google)", "gstatic.com": "risorse Google", "recaptcha.net": "anti-bot",
    "hcaptcha.com": "anti-bot", "stripe.com": "pagamenti", "paypal.com": "pagamenti", "sentry.io": "monitoraggio errori", "intercom.io": "chat",
    "hs-scripts.com": "marketing", "hubspot.com": "marketing", "mailchimp.com": "email marketing",
}


def is_local(host):
    h = (host or "").lower()
    return h in ("localhost", "127.0.0.1", "::1") or h.endswith((".localhost", ".test"))


def classify(host):
    h = host.lower()
    for k, v in KNOWN.items():
        if h == k or h.endswith("." + k):
            return v
    return "da classificare"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--out", type=Path, default=Path("."))
    ap.add_argument("--autorizzato", action="store_true")
    ap.add_argument("--wait", type=float, default=4.0)
    a = ap.parse_args()
    for u in a.urls:
        host = urlparse(u).hostname
        if not is_local(host) and not a.autorizzato:
            sys.exit(f"RIFIUTATO: «{host}» non è locale. Serve --autorizzato (conferma scritta del titolare). Nessuna richiesta inviata.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Serve playwright: pip install playwright && playwright install chromium")
    a.out.mkdir(parents=True, exist_ok=True)
    report = []
    with sync_playwright() as pw:
        for u in a.urls:
            site = urlparse(u).hostname
            br = pw.chromium.launch()
            ctx = br.new_context()
            page = ctx.new_page()
            reqs = []
            page.on("request", lambda r: reqs.append((urlparse(r.url).hostname or "", r.resource_type)))
            status = ""
            try:
                resp = page.goto(u, wait_until="load", timeout=25000)
                status = resp.status if resp else ""
                page.wait_for_timeout(int(a.wait * 1000))
            except Exception as e:
                status = f"errore: {type(e).__name__}"
            cookies = [{"nome": c["name"], "dominio": c["domain"], "scadenza": "sessione" if c["expires"] in (-1, 0) else c["expires"],
                        "secure": c["secure"], "httpOnly": c["httpOnly"], "sameSite": c.get("sameSite", "")} for c in ctx.cookies()]
            try:
                ls = page.evaluate("Object.keys(localStorage)")
                ss = page.evaluate("Object.keys(sessionStorage)")
            except Exception:
                ls, ss = [], []
            third = {}
            for h, t in reqs:
                if h and h != site and not h.endswith("." + (site or "")):
                    third.setdefault(h, set()).add(t)
            tp = [{"dominio": h, "tipi": sorted(t), "classe": classify(h)} for h, t in sorted(third.items())]
            report.append({"url": u, "status": status, "cookie": cookies, "localStorage": ls, "sessionStorage": ss, "terze_parti": tp})
            br.close()
    (a.out / "cookie-scan.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    with (a.out / "cookie-scan.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["url", "tipo", "nome_o_dominio", "dettaglio", "classe"])
        for r in report:
            for c in r["cookie"]:
                w.writerow([r["url"], "cookie", c["nome"], f"{c['dominio']} · scadenza {c['scadenza']} · secure={c['secure']} httpOnly={c['httpOnly']}", "da classificare (tecnico o no?)"])
            for k in r["localStorage"] + r["sessionStorage"]:
                w.writerow([r["url"], "storage", k, "chiave di storage del browser", "da classificare"])
            for t in r["terze_parti"]:
                w.writerow([r["url"], "terza parte", t["dominio"], ", ".join(t["tipi"]), t["classe"]])
    for r in report:
        print(f"{r['url']}  stato {r['status']}  cookie {len(r['cookie'])}  storage {len(r['localStorage']) + len(r['sessionStorage'])}  domini di terzi {len(r['terze_parti'])}")
        for t in r["terze_parti"]:
            print(f"  terza parte: {t['dominio']:32} {t['classe']}")
    print(f"scritto: {a.out}/cookie-scan.json e .csv. Valori dei cookie non salvati. Confrontali con informativa e banner.")


if __name__ == "__main__":
    main()
