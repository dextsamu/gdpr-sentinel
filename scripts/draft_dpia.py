#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Bozza di scheda DPIA (art. 35 GDPR) dalla mappa dei trattamenti, con indicatori di necessità.

Uso:
    python3 draft_dpia.py <processing-map.csv> [--out dpia-bozza.md]

Per ogni trattamento della mappa scrive una scheda con i quattro contenuti dell'art. 35(7): descrizione,
necessità e proporzionalità, rischi per gli interessati, misure. Precompila SOLO ciò che la mappa dice già;
il resto resta «da compilare con il titolare». Cerca nel testo della mappa indicatori che di solito rendono
probabile una DPIA (categorie particolari, minori, geolocalizzazione, monitoraggio sistematico, larga scala,
lavoratori, uso innovativo, decisioni automatizzate). Sono segnali da discutere, NON la decisione: se la DPIA
serve lo stabilisce il titolare con il DPO, anche alla luce dell'elenco del Garante (art. 35(4)).
La bozza non è una DPIA, non valuta il rischio residuo e non dichiara conformità. Sola lettura sulla mappa.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

INDICATORI = [
    ("categorie particolari o dati molto personali", r"salute|sanitar|biometric|genetic|religios|sindacal|orientamento|etnic|politic|giudiziar|certificat\w* (?:medic|inps)|malattia|infortun"),
    ("minori o persone vulnerabili", r"minor|bambin|student|anzian|pazient|vulnerabil"),
    ("geolocalizzazione o tracciamento degli spostamenti", r"gps|geolocal|posizione|coordinate|geofenc"),
    ("monitoraggio sistematico", r"timbratur|presenz|videosorveglian|monitor|tracci|log di accesso|profilazion"),
    ("lavoratori o volontari (rapporto di squilibrio)", r"dipendent|lavorator|volontar|turn[io]|straordinar|banca ore"),
    ("larga scala", r"larga scala|migliaia|tutti i (?:cittadin|utenti|soci)|intera popolazione"),
    ("uso innovativo di tecnologie", r"intelligenza artificiale|\bia\b|\bai\b|machine learning|riconoscimento facciale|llm|biometria"),
    ("decisioni automatizzate con effetti sulla persona", r"decisione automatizzata|punteggio|scoring|esclusione automatica"),
]
NV = re.compile(r"(?i)^\s*(non verificato|da verificare.*|n/?d|-)?\s*$")


def val(row, k):
    v = (row.get(k) or "").strip()
    return "da compilare con il titolare" if NV.match(v) else v


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("--out", type=Path, default=Path("dpia-bozza.md"))
    a = ap.parse_args()
    if not a.map.exists():
        print(f"ERRORE: {a.map} non esiste", file=sys.stderr)
        return 1
    with a.map.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if not (r.get("trattamento") or "").strip().lower().startswith("esempio")]
    if not rows:
        print("ERRORE: nessun trattamento reale nella mappa (le righe «esempio» sono ignorate)", file=sys.stderr)
        return 1
    out = ["# Bozza di scheda DPIA (art. 35 GDPR)", "",
           "> Bozza ricavata dalla mappa dei trattamenti. **Non è una DPIA completata**: non valuta il rischio residuo, non esprime giudizi di conformità e "
           "va compilata e decisa dal titolare con il DPO. Le caselle «da compilare con il titolare» non erano nella mappa.", ""]
    riepilogo = []
    for r in rows:
        testo = " ".join((r.get(k) or "") for k in ("trattamento", "dati_e_interessati", "finalita", "sistemi_e_destinatari")).lower()
        hit = [n for n, rx in INDICATORI if re.search(rx, testo)]
        riepilogo.append((r.get("id", "?"), r.get("trattamento", ""), hit))
        out += [f"## {r.get('id', '?')} · {r.get('trattamento', '')}", "",
                f"**Indicatori che suggeriscono una DPIA** (segnali da discutere, non una decisione): "
                + (("; ".join(hit) + f" ({len(hit)} su {len(INDICATORI)})") if hit else "nessuno rilevato dal testo della mappa (non significa che la DPIA non serva)"), "",
                "### 1. Descrizione del trattamento",
                f"- Dati e interessati: {val(r, 'dati_e_interessati')}", f"- Finalità: {val(r, 'finalita')}",
                f"- Ruoli (titolare, responsabili): {val(r, 'ruoli')}", f"- Sistemi e destinatari: {val(r, 'sistemi_e_destinatari')}",
                f"- Paesi e trasferimenti: {val(r, 'paesi_e_trasferimenti')}", f"- Conservazione: {val(r, 'retention')}", "",
                "### 2. Necessità e proporzionalità",
                f"- Base giuridica e condizione: {val(r, 'base_giuridica_e_condizione')}",
                "- Minimizzazione (i dati raccolti sono solo quelli necessari alla finalità?): da compilare con il titolare",
                "- Alternative meno invasive valutate: da compilare con il titolare",
                f"- Diritti degli interessati e controlli: {val(r, 'diritti_e_controlli')}", "",
                "### 3. Rischi per diritti e libertà degli interessati",
                "- Accesso illecito, modifica o perdita dei dati; uso per finalità diverse; discriminazione o danno da errori: probabilità e gravità da stimare con il titolare",
                f"- Lacune già note dalla verifica: {val(r, 'gap')}", "",
                "### 4. Misure previste",
                f"- Evidenze trovate (codice, configurazione, documenti): {val(r, 'evidenze')}",
                "- Misure tecniche e organizzative da confermare e rischio residuo: da compilare con il titolare", "",
                "### 5. Consultazione e decisione",
                "- Parere del DPO, eventuale consultazione degli interessati o dei rappresentanti, eventuale consultazione preventiva del Garante (art. 36): da compilare",
                ""]
    out += ["---", "## Riepilogo degli indicatori", "", "| ID | Trattamento | Indicatori | Numero |", "|---|---|---|---|"]
    for i, n, h in riepilogo:
        out.append(f"| {i} | {n} | {'; '.join(h) or '—'} | {len(h)} |")
    out.append("\nCon due o più indicatori la DPIA è di norma da considerare; con uno solo o nessuno la scelta resta motivata dal titolare e va documentata.")
    a.out.write_text("\n".join(out) + "\n", encoding="utf-8")
    con2 = sum(1 for _, _, h in riepilogo if len(h) >= 2)
    print(f"schede scritte: {len(rows)} in {a.out}; trattamenti con due o più indicatori: {con2}")
    print("Bozza, non DPIA: decide il titolare con il DPO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
