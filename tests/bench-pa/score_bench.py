#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Secondo banco privacy: il sito di un istituto comprensivo (PHP) con 15 difetti noti e 5 esche.

Uso:
    python3 tests/bench-pa/score_bench.py prepare <cartella>
    python3 tests/bench-pa/score_bench.py score <audit> [<audit> …]

Perché: un banco solo (tests/bench-app, portale soci in Next.js) misura la skill sulle classi di difetti su cui è stata
scritta. Questo cambia linguaggio, tipo di titolare (una scuola pubblica) e temi: minori, albo online, amministrazione
trasparente, modulistica, servizi incorporati di terze parti. Stesso punteggio del primo banco (stesso script).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bench-app"))
import score_bench as sb   # noqa: E402

sb.HERE = HERE
sb.TRUTH = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    sys.exit(sb.main())
