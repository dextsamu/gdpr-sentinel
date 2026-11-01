#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Copia i template della skill in una cartella di lavoro riservata.

Uso:
    python3 init_gdpr.py <cartella-di-destinazione>

Crea gdpr-matrix.csv, gaps.csv, processing-map.csv, documentary-matrix.csv, meta.json e domande.md. Non sovrascrive file esistenti.
Se hai già una cartella di audit di appsec-sentinel, passa quella (o una sua sottocartella `gdpr/`).
"""
import json
import shutil
from datetime import datetime
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FILES = {
    "gdpr-matrix.csv": "gdpr-matrix.csv",
    "processing-map.csv": "processing-map.csv",
    "questions-template.md": "domande.md",
    "documentary-matrix.csv": "documentary-matrix.csv",
    "meta-template.json": "meta.json",
    "gaps.csv": "gaps.csv",
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1].startswith("-"):   # «--help» non deve diventare una cartella
        print(__doc__)
        return 0 if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help") else 2
    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    for src, name in FILES.items():
        target = dest / name
        if target.exists():
            print(f"già presente, non sovrascritto: {target}")
            continue
        shutil.copy2(ASSETS / src, target)
        print(f"creato: {target}")
    tj = dest / "registro-tool" / "tempi.json"   # inizio del lavoro: check_delivery ne ricava la durata
    if not tj.exists():
        tj.parent.mkdir(exist_ok=True)
        tj.write_text(json.dumps({"inizio": datetime.now().astimezone().isoformat(timespec="seconds")}), encoding="utf-8")
    print("Sostituisci la riga d'esempio della mappa (T01) con i trattamenti reali, poi esegui check_matrix.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
