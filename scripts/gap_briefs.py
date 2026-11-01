#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Scrive un brief per il verificatore per ogni gap da smentire (smentite/smentita-<ID>.md).

Uso:
    python3 gap_briefs.py <cartella-audit> --repo <repository> [--priorita alta,media]

Perché: finora il verificatore riceveva le righe di gaps.csv e basta. Un brief per gap gli dà l'affermazione, i punti
del codice da aprire (con le righe citate) e le ipotesi di smentita tipiche della privacy, che non sono quelle della
sicurezza: obbligo di legge, dato non personale, trattamento di un altro titolare, informativa che già lo copre, job
di cancellazione altrove. Il brief NON contiene la motivazione dell'autore, la matrice A–N né le domande per il DPO:
il verificatore deve partire dall'affermazione e dal codice, non dalle conclusioni.

Selezione: gap in stato «riscontrato» o «confermato da codice/config», con priorità tra quelle indicate (predefinita:
alta) e senza un esito di smentita già scritto. Gli esiti vanno in smentite/esiti.json e si applicano con
apply_refutations.py.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

AREE = {"A": "mappa dei trattamenti e ruoli", "B": "principi e basi giuridiche", "C": "dati particolari, penali, minori",
        "D": "trasparenza (artt. 13/14)", "E": "cookie e tracking", "F": "diritti degli interessati",
        "G": "retention e cancellazione", "H": "privacy by design/default e sicurezza", "I": "fornitori e accordi",
        "J": "trasferimenti internazionali", "K": "governance", "L": "incidenti e data breach",
        "M": "profilazione, AI, marketing", "N": "casi italiani e settoriali"}

COMUNI = [
    "Il codice citato fa davvero ciò che il gap afferma? Leggilo per intero (anche le righe vicine e i file che lo chiamano): un gap può descrivere il contrario di ciò che c'è.",
    "Il trattamento avviene davvero in produzione, o è codice di prova, esempio, funzione disattivata, ramo non raggiungibile?",
    "Il dato è davvero personale? Può essere anonimo, aggregato, riferito a un ente e non a una persona, o non collegabile a nessuno?",
    "Il trattamento è di un altro titolare (o il fornitore agisce come titolare autonomo) e quindi l'obbligo indicato non è di chi è sotto esame?",
    "Un obbligo di legge, un contratto o un'altra base giuridica (art. 6) giustificano il trattamento come avviene nel codice?",
    "L'informativa o un altro documento del repository (privacy, termini, banner, pagine) dicono già ciò che il gap dice che manca? Cercalo, non supporlo.",
    "Lo stato dichiarato è quello raggiunto? Una lettura del codice non è una prova sul sito in funzione; la priorità è giusta per il rischio reale per gli interessati?",
]
PER_AREA = {
    "C": ["Il dato è davvero sanitario o particolare (art. 9), o è un'informazione amministrativa (es. sola presenza di un certificato, senza diagnosi)?"],
    "E": ["Lo strumento è tecnico o necessario (sessione, sicurezza, preferenze) e quindi esente dal consenso?",
          "Il caricamento avviene davvero prima del consenso? Cerca condizioni, banner e attese nel codice che lo precede."],
    "F": ["La richiesta è soddisfatta da un altro percorso (job, cancellazione differita, procedura manuale documentata, endpoint diverso)?"],
    "G": ["Un job, un TTL del database, una rotazione dei log o del backup cancella già i dati nel tempo promesso? Cerca nel codice e negli script."],
    "H": ["I dati scritti nei log o esposti sono mascherati, filtrati o non personali? La configurazione di produzione è diversa da quella letta?"],
    "I": ["Il fornitore riceve davvero dati personali, o solo dati tecnici non identificativi? È indicato da qualche parte (informativa, elenco responsabili)?"],
    "J": ["I dati escono davvero dal SEE (regione del servizio, server europei) o il trasferimento ha già un meccanismo indicato?"],
    "M": ["Il consenso o la scelta sono richiesti altrove (lato server il valore predefinito è diverso dal modulo)? È davvero marketing o profilazione?"],
    "N": ["La raccolta è limitata nel tempo, nella precisione o a un momento preciso (es. solo al check-in) e dichiarata altrove?"],
}
OK_STATI = ("riscontrato", "confermato da codice/config")


def excerpt(repo: Path, ref: str, ctx: int = 3) -> str:
    m = re.match(r"^(.+?):(\d+)(?:-(\d+))?$", ref.strip())
    path, a, b = (m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))) if m else (ref.strip(), None, None)
    p = (repo / path)
    try:
        if not p.resolve().is_relative_to(repo.resolve()) or not p.is_file():
            return ""
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, ValueError):
        return ""
    if a is None:
        return ""
    lo, hi = max(1, a - ctx), min(len(lines), b + ctx)
    body = "\n".join(f"{n:>5}  {lines[n - 1][:200]}" for n in range(lo, hi + 1))
    return f"\n```\n{body}\n```\n"


def brief(r: dict, repo: Path) -> str:
    c = (r.get("controllo") or "").strip().upper()[:1]
    refs = [x for x in re.split(r"[;\n]+|,\s+(?=[\w./-]+:\d)", r.get("riferimenti") or "") if x.strip()]
    dove = "\n".join(f"- `{x.strip()}`" + excerpt(repo, x) for x in refs) or "- (nessun riferimento a file: cerca tu dove il trattamento avviene)"
    ip = COMUNI + PER_AREA.get(c, [])
    return (f"# Smentita di {r['id']}\n\n"
            "Il tuo compito è **dimostrare che questo gap è sbagliato, esagerato o non pertinente**. Non sei l'autore: "
            "non cercare conferme. Se non riesci a smentirlo, dillo e scrivi cosa hai cercato e dove. Non dichiarare "
            "conformità e non dare pareri legali: valuti solo se l'affermazione regge sul codice e sui documenti del repository.\n\n"
            f"## Affermazione\n{r.get('titolo', '').strip()}\n\n"
            f"- Area: {c} — {AREE.get(c, 'non indicata')}\n- Stato dichiarato: {r.get('stato', '').strip()} · priorità: {r.get('priorita', '').strip()}\n"
            f"- Rischio per gli interessati dichiarato: {r.get('rischio_interessati', '').strip() or '(non indicato)'}\n"
            f"- Norma citata: {r.get('norma', '').strip() or '(non indicata)'}\n\n"
            f"## Dove guardare\n{dove}\n\n"
            "## Ipotesi di smentita da provare (almeno quelle pertinenti)\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(ip, 1)) +
            "\n\n## Cosa restituire\nUna voce in `smentite/esiti.json`:\n"
            f'`{{"id": "{r["id"]}", "esito": "resiste|declassato|respinto", "verificatore": "chi sei", "tentativi": ["ipotesi → dove hai guardato → cosa hai trovato", ...], '
            '"priorita": "solo se declassato", "stato": "solo se declassato", "motivo": "obbligatorio se declassato o respinto"}`\n')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("audit", type=Path)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--priorita", default="alta", help="priorità da smentire, separate da virgola (predefinita: alta)")
    a = ap.parse_args()
    gp = a.audit / "gaps.csv"
    if not gp.exists():
        print(f"manca {gp}"); return 2
    pr = {x.strip().lower() for x in a.priorita.split(",")}
    rows = [r for r in csv.DictReader(gp.open(encoding="utf-8")) if not (r.get("id") or "").startswith("ESEMPIO")]
    sel = [r for r in rows if (r.get("stato") or "").strip() in OK_STATI and (r.get("priorita") or "").strip().lower() in pr
           and (r.get("smentita") or "").strip().lower() in ("", "non eseguita")]
    out = a.audit / "smentite"
    out.mkdir(exist_ok=True)
    for r in sel:
        (out / f"smentita-{r['id']}.md").write_text(brief(r, a.repo), encoding="utf-8")
    print(f"{len(sel)} brief in {out} (gap con priorità {', '.join(sorted(pr))} in stato riscontrato o confermato, senza esito).")
    print("Dai al verificatore SOLO references/refutation-pass.md, questi brief e il repository; poi apply_refutations.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
