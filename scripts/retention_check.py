#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Cerca nel codice l'evidenza di cancellazione o anonimizzazione e la confronta con i tempi dichiarati.

Uso:
    python3 retention_check.py <repo> [--declared retention.csv] [--out retention-evidenze.csv]

retention.csv (facoltativo): dato,giorni_dichiarati,fonte   (es. «dati GPS,90,informativa»)
Rileva: job pianificati (node-cron, cron, celery, APScheduler), cancellazioni con soglia temporale
(deleteMany/delete con data, «giorni», subDays, timedelta), costanti con nomi tipo RETENTION/DAYS,
e i modelli con campi di data (createdAt, deletedAt, cancellato) senza alcuna cancellazione che li citi.
È euristico: segnala evidenza e assenza di evidenza, non conferma che la cancellazione funzioni.
Un modello senza evidenza non è per forza una violazione: può avere una procedura fuori dal codice.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

SKIP = {"node_modules", ".git", ".next", "dist", "build", "vendor", "__pycache__", ".venv", "coverage"}
PATTERNS = {
    "job pianificato": re.compile(r"(cron\.schedule\(|schedule\s*:\s*['\"][\d*/,\- ]+['\"]|@(?:periodic_task|shared_task)|crontab\(|add_job\()"),
    "cancellazione con soglia": re.compile(r"(deleteMany|\.delete\(|DELETE\s+FROM|\.destroy\(|updateMany)[^\n]{0,200}(lt|lte|before|<|older|cutoff|threshold)", re.I),
    "calcolo di soglia in giorni": re.compile(r"(\b(\d{2,4})\s*\*\s*24\s*\*\s*60|subDays\(\s*\w*\s*,?\s*(\d+)|timedelta\(days\s*=\s*(\d+)|\b(\w*(?:retention|giorni|days|scadenza)\w*)\s*[:=]\s*(\d{2,4}))", re.I),
    "anonimizzazione": re.compile(r"(anonimizz|anonymi[sz]|null\s*,?\s*//\s*gdpr|pseudonim)", re.I),
}
DATE_FIELDS = re.compile(r"^\s+(createdAt|deletedAt|cancellatoIl|expiresAt|scadenza|created_at|deleted_at)\s", re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("--declared", type=Path)
    ap.add_argument("--out", type=Path, default=Path("retention-evidenze.csv"))
    a = ap.parse_args()
    if not a.repo.is_dir():
        sys.exit(f"cartella non trovata: {a.repo}")
    ev, texts, models = [], {}, []
    for p in a.repo.rglob("*"):
        if not p.is_file() or set(p.relative_to(a.repo).parts) & SKIP or p.stat().st_size > 400000:
            continue
        if p.suffix.lower() in {".ts", ".tsx", ".js", ".mjs", ".py", ".sql", ".sh"}:
            t = p.read_text(encoding="utf-8", errors="replace")
            texts[str(p.relative_to(a.repo))] = t
            for ln, line in enumerate(t.splitlines(), 1):
                for k, rx in PATTERNS.items():
                    m = rx.search(line)
                    if m:
                        ev.append((k, f"{p.relative_to(a.repo)}:{ln}", line.strip()[:140]))
        elif p.suffix == ".prisma":
            t = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"^model\s+(\w+)\s*\{(.*?)^\}", t, re.S | re.M):
                if DATE_FIELDS.search(m.group(2)):
                    models.append(m.group(1))
    corpus = "\n".join(texts.values())
    no_ev = []
    for m in models:
        cited = re.search(rf"prisma\.{m[0].lower() + m[1:]}\.(deleteMany|delete|updateMany)", corpus)
        (ev.append(("modello con cancellazione nel codice", m, "cita delete/updateMany")) if cited else no_ev.append(m))
    declared = []
    if a.declared and a.declared.exists():
        declared = list(csv.DictReader(a.declared.open(encoding="utf-8")))
    with a.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tipo", "dove", "estratto"])
        w.writerows(ev)
        for m in no_ev:
            w.writerow(["modello senza evidenza di cancellazione", m, "nessun delete/updateMany trovato: verificare procedura fuori dal codice"])
    jobs = [e for e in ev if e[0] == "job pianificato"]
    print(f"evidenze trovate: {len(ev)}  (job pianificati {len(jobs)})  modelli con date senza cancellazione evidente: {len(no_ev)} su {len(models)}  -> {a.out}")
    for m in no_ev[:25]:
        print(f"  senza evidenza: {m}")
    if declared:
        days = {int(x) for e in ev if e[0] == "calcolo di soglia in giorni" for x in re.findall(r"\b(\d{2,4})\b", e[2])}
        print("\nConfronto con i tempi dichiarati (indicativo):")
        for d in declared:
            gg = int(d["giorni_dichiarati"])
            print(f"  {d['dato']}: dichiarati {gg} giorni, {'trovata una soglia uguale nel codice' if gg in days else 'nessuna soglia uguale trovata: verificare'}")


if __name__ == "__main__":
    main()
