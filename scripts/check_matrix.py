#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Controlla la matrice GDPR (gdpr-matrix.csv) e, opzionalmente, la mappa dei trattamenti.

Uso:
    python3 check_matrix.py <gdpr-matrix.csv> [--map processing-map.csv]

Verifica:
  - sono presenti tutti i controlli A–N;
  - lo stato è uno tra: riscontrato, confermato da codice/config, ipotesi, non verificabile;
  - nessuna riga afferma «conforme/non conforme» (la skill non dà giudizi di conformità);
  - ogni riga `non verificabile` o `ipotesi` ha una domanda (domanda_id);
  - ogni riga `riscontrato` / `confermato da codice/config` ha almeno un'evidenza;
  - ogni riga con gap in stato «riscontrato» o «confermato da codice/config» ha la colonna `smentita` compilata
    nella forma «esito | verificatore | tentativi» (esito: resiste, declassato, respinto, non eseguita): un verificatore
    diverso dall'autore ha provato a confutarla; una smentita dello stesso autore non vale
    (references/refutation-pass.md). È un warning, non un errore; la colonna è facoltativa nei vecchi audit;
  - ogni controllo va compilato: una riga con solo il testo del modello o la sola evidenza automatica «[prepass]» è un errore;
  - (con --map) i campi della mappa vuoti sono segnalati: vanno scritti «non verificato»;
  - (con --gaps gaps.csv) un gap per riga: ID unico (es. GDPR-001), controllo A–N, stato ammesso, priorità alta/media/bassa,
    riferimenti file:riga per i gap riscontrati o confermati, smentita per quelli ad alta priorità; un controllo con gap
    nell'elenco deve citarli anche nella riga della matrice. Senza gap strutturati due giri non si possono confrontare.
Esce con 1 se trova errori.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

CONTROLLI = list("ABCDEFGHIJKLMN")
ESITI_SMENTITA = ("resiste", "declassato", "respinto", "non eseguita")
STATI = {"riscontrato", "confermato da codice/config", "ipotesi", "non verificabile"}
GIUDIZI = re.compile(r"\b(non\s+conforme|non\s+conformit[aà]|conforme|compliant|non-compliant)\b", re.I)


def read(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("matrix", type=Path)
    ap.add_argument("--map", type=Path, dest="pmap")
    ap.add_argument("--gaps", type=Path)
    args = ap.parse_args()

    errs, warns = [], []
    rows = read(args.matrix)
    present = {(r.get("controllo") or "").strip().upper() for r in rows}
    for c in CONTROLLI:
        if c not in present:
            errs.append(f"controllo {c} assente dalla matrice")

    for r in rows:
        c = (r.get("controllo") or "?").strip().upper()
        stato = (r.get("stato") or "").strip().lower()
        if stato not in STATI:
            errs.append(f"{c}: stato non ammesso {stato!r} (ammessi: {', '.join(sorted(STATI))})")
        blob = " ".join((v or "") for v in r.values())
        if GIUDIZI.search(blob):
            errs.append(f"{c}: contiene un giudizio di conformità: la skill non lo può esprimere")
        has_evidence = any((r.get(k) or "").strip() for k in ("evidenza_tecnica", "evidenza_documentale"))
        own = [k for k in ("evidenza_tecnica", "evidenza_documentale", "decisione_mancante", "gap", "domanda_id")
               if (r.get(k) or "").strip() and not (r.get(k) or "").strip().startswith("[prepass]")]
        if not own:
            errs.append(f"{c}: controllo non compilato (solo il modello o l'evidenza automatica [prepass]): scrivere evidenza, gap o la domanda per il titolare")
        if stato in {"riscontrato", "confermato da codice/config"} and not has_evidence:
            errs.append(f"{c}: stato '{stato}' senza alcuna evidenza")
        if stato in {"non verificabile", "ipotesi"} and not (r.get("domanda_id") or "").strip():
            warns.append(f"{c}: stato '{stato}' senza domanda_id (serve una domanda già formulata)")

        if stato in {"riscontrato", "confermato da codice/config"} and (r.get("gap") or "").strip() and "smentita" in r:
            sm = (r.get("smentita") or "").strip().lower()
            parts = [x.strip() for x in sm.split("|")]
            if not sm:
                warns.append(f"{c}: gap {stato} senza smentita: farlo confutare da un verificatore diverso dall'autore")
            elif not sm.startswith(ESITI_SMENTITA):
                warns.append(f"{c}: smentita senza esito riconoscibile (iniziare con: {', '.join(ESITI_SMENTITA)})")
            elif sm.startswith("non eseguita"):
                warns.append(f"{c}: smentita non eseguita: dichiararlo come limite nel report")
            elif len(parts) < 3 or not all(parts[:3]):
                warns.append(f"{c}: smentita nella forma «esito | verificatore | tentativi»: indicare chi ha provato a confutare e cosa ha provato")
            elif re.search(r"\bstess[oa]\b|\bio\b|\bme\b", parts[1]):
                warns.append(f"{c}: smentita fatta dall'autore stesso: non è indipendente, usare «non eseguita» oppure un verificatore diverso")

    if args.pmap:
        for r in read(args.pmap):
            empty = [k for k, v in r.items() if k not in ("id", "gap") and not (v or "").strip()]
            if empty:
                warns.append(f"mappa {r.get('id', '?')}: campi vuoti ({', '.join(empty)}): scrivere «non verificato»")

    if args.gaps:
        seen = set()
        mrow = {(r.get("controllo") or "").strip().upper(): r for r in rows}
        for g in read(args.gaps):
            gid = (g.get("id") or "").strip()
            if gid.startswith("ESEMPIO"):
                continue
            c = (g.get("controllo") or "").strip().upper()
            st = (g.get("stato") or "").strip().lower()
            pr = (g.get("priorita") or "").strip().lower()
            if not re.fullmatch(r"[A-Z]{2,6}-[0-9]{3,4}", gid):
                errs.append(f"gap {gid or '?'}: ID non valido (es. GDPR-001)")
            if gid in seen:
                errs.append(f"gap {gid}: ID duplicato")
            seen.add(gid)
            if c not in CONTROLLI:
                errs.append(f"gap {gid}: controllo {c!r} non tra A–N")
            if st not in STATI:
                errs.append(f"gap {gid}: stato non ammesso {st!r}")
            if pr not in ("alta", "media", "bassa"):
                errs.append(f"gap {gid}: priorità {pr!r} non ammessa (alta, media, bassa)")
            if GIUDIZI.search(" ".join((v or "") for v in g.values())):
                errs.append(f"gap {gid}: contiene un giudizio di conformità")
            if st in {"riscontrato", "confermato da codice/config"} and not (g.get("riferimenti") or "").strip():
                errs.append(f"gap {gid}: stato '{st}' senza riferimenti")
            if st in {"non verificabile", "ipotesi"} and not (g.get("domanda_id") or "").strip():
                warns.append(f"gap {gid}: stato '{st}' senza domanda_id")
            sm = (g.get("smentita") or "").strip().lower()
            if pr == "alta" and st in {"riscontrato", "confermato da codice/config"}:
                if not sm:
                    errs.append(f"gap {gid}: priorità alta senza smentita (anche «non eseguita», dichiarata)")
                elif not sm.startswith(ESITI_SMENTITA):
                    errs.append(f"gap {gid}: smentita senza esito riconoscibile")
            if c in mrow and gid not in (mrow[c].get("gap") or "") and not (mrow[c].get("gap") or "").strip():
                warns.append(f"gap {gid}: la riga {c} della matrice non cita i suoi gap")

    for w in warns:
        print(f"WARNING {w}")
    for e in errs:
        print(f"ERRORE  {e}")
    tot = len(rows)
    nv = sum((r.get("stato") or "").strip().lower() == "non verificabile" for r in rows)
    print(f"\n{tot} controlli · {nv} non verificabili · {len(errs)} errori · {len(warns)} warning")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
