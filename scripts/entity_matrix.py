#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Matrice per entità: per ogni tabella o modello con dati personali, le stesse quattro domande, pre-compilate dal codice.

Uso:
    python3 entity_matrix.py <repo> --out <cartella-audit>/entita.csv

Perché: su un repository grande due giri indipendenti vedevano in comune circa il 60% delle cause, e le differenze
stavano soprattutto in conservazione, export, cancellazione e isolamento fra enti, domande che si pongono tabella per
tabella. Lasciando all'agente la scelta di dove guardare e di come raggruppare, ogni giro sceglieva diversamente. Qui le
domande e il taglio (una riga per entità e domanda) sono fissi, e la prima risposta la dà uno script, con file e riga.

Domande (colonna `domanda`):
  cancellazione   esiste nel codice una cancellazione o anonimizzazione dell'entità (job, script, route)?
  export          l'entità compare nell'esportazione dei dati dell'interessato (art. 15/20)?
  diritto_oblio   l'entità viene cancellata o anonimizzata quando l'utente chiede la cancellazione (art. 17)?
  isolamento      (solo se il codice ha un campo di ente) le letture dell'entità filtrano per ente?

Colonna `prepass`: «si» con riferimenti, «non trovato» (nessuna evidenza: va guardato) o «n/a». L'agente compila
`esito` sulle righe «non trovato» e su quelle che contraddicono l'informativa: ok, gap (con `gap_id`), non applicabile,
non verificabile (con il motivo in `note`). Le righe «si» restano ok salvo prova contraria. È un'indicazione meccanica:
un «si» significa che una cancellazione esiste, non che rispetti i tempi dichiarati.

Riconosce Prisma (schema.prisma e chiamate prisma.<modello>), Django (models.py e <Modello>.objects) e SQL
(CREATE TABLE, DELETE FROM / UPDATE). Su altri ORM la pre-compilazione resta parziale.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import draft_ropa as dr   # noqa: E402  (modelli e gruppi di dati personali)

SKIP = {"node_modules", ".git", ".next", "dist", "build", "vendor", "__pycache__", ".venv", "venv", "coverage", "tests", "test", "__tests__", "e2e"}
CODE = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".php", ".rb", ".go", ".sql"}
TENANT = re.compile(r"^(organization|organisation|org|tenant|ente|company|azienda|account|workspace|team)_?id$", re.I)
# esportazione e cancellazione DELL'INTERESSATO, non i report aziendali (turni-export, report/export)
EXPORT_PATH = re.compile(r"(gdpr|privacy|personal|account|profil\w*|/me/|my-?data|miei-?dati|portabil|data-?export|download-?data)[^/]*/?(.*export|.*esport|.*download)|"
                         r"(data-?export|esporta-?dati|portabil|my-?data|miei-?dati)", re.I)
ERASE_PATH = re.compile(r"(delete-?account|account-?deletion|erasure|oblio|cancella\w*-?account|right-to-be-forgotten|elimina-?account|me/delete|account/delete)", re.I)
USER_LINK = re.compile(r"^(user|utente|member|socio|dipendente|volontario|person|persona|customer|cliente|iscritto|alunno|patient|paziente)_?id$|^email$", re.I)
API_PATH = re.compile(r"(^|/)(api|routes?|views?|controllers?|handlers?|pages/api|app/api)(/|\.)", re.I)


def accessor(name, kind):
    if kind == "prisma":
        return name[0].lower() + name[1:]
    return name


def files(repo):
    for p in repo.rglob("*"):
        if p.is_file() and p.suffix.lower() in CODE and not (set(p.relative_to(repo).parts) & SKIP) and p.stat().st_size < 400000:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    repo = a.repo.resolve()
    models, seen = [], set()
    allm = dr.models(repo)
    has_orm = any(not src.endswith(".sql") for _, _, src in allm)
    for name, fields, src in sorted(allm, key=lambda m: m[2].endswith(".sql")):
        if name.lower() in seen or (has_orm and src.endswith(".sql")):   # le migrazioni SQL ripetono i modelli dell'ORM
            continue
        seen.add(name.lower())
        groups = [g for g, rx in dr.GROUPS.items() if any(re.search(rx, f, re.I) for f in fields)]
        if groups:
            kind = "prisma" if src.endswith(".prisma") else "django" if src.endswith(".py") else "sql"
            models.append((name, fields, src, kind, groups))
    multi = any(TENANT.match(f) for _, fs, *_ in models for f in fs)
    texts = {}
    for p in files(repo):
        try:
            texts[str(p.relative_to(repo)).replace("\\", "/")] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            pass
    export_files = [f for f in texts if EXPORT_PATH.search(f)]
    erase_files = [f for f in texts if ERASE_PATH.search(f)]

    def refs_for(name, kind, rx_ops, only=None, api_only=False):
        acc = re.escape(accessor(name, kind))
        if kind == "prisma":
            rx = re.compile(rf"\b(?:prisma|tx|db|client)\s*\.\s*{acc}\s*\.\s*(?:{rx_ops})\b")
        elif kind == "django":
            rx = re.compile(rf"\b{acc}\.objects\b[^\n]*\.(?:{rx_ops})\b")
        else:
            rx = re.compile(rf"(?i)\b(?:delete\s+from|update)\s+[`\"\[]?{acc}[`\"\]]?\b")
        out = []
        for f, lines in texts.items():
            if (only is not None and f not in only) or (api_only and not API_PATH.search(f)):
                continue
            for n, line in enumerate(lines, 1):
                if rx.search(line):
                    out.append(f"{f}:{n}")
        return out

    def mentions(name, kind, flist):
        acc = accessor(name, kind)
        rx = re.compile(rf"\b{re.escape(acc)}\b|\b{re.escape(name)}\b")
        return [f"{f}:{n}" for f in flist for n, line in enumerate(texts.get(f, []), 1) if rx.search(line)][:3]

    rows = []
    for name, fields, src, kind, groups in models:
        dati = ", ".join(groups)
        dele = refs_for(name, kind, "delete|deleteMany" if kind != "sql" else "")
        anon = [r for r in refs_for(name, kind, "update|updateMany") if any(k in " ".join(texts[r.rsplit(":", 1)[0]]).lower()
                                                                             for k in ("anonimi", "anonymi", "redact", "gdpr", "retention"))]
        canc = dele + [r for r in anon if r not in dele]
        rows.append([name, dati, src, "cancellazione", ("si: " + "; ".join(canc[:3])) if canc else "non trovato"])
        personale = name.lower() in ("user", "users", "utente", "utenti", "member", "socio", "soci", "dipendente", "persona", "customer", "cliente") \
            or any(USER_LINK.match(f) for f in fields)
        if not personale:   # export e oblio riguardano i dati legati a una persona che può chiederli
            rows.append([name, dati, src, "export", "n/a (nessun legame con un interessato nel modello)"])
            rows.append([name, dati, src, "diritto_oblio", "n/a (nessun legame con un interessato nel modello)"])
        exp = mentions(name, kind, export_files) if personale else None
        if personale:
            rows.append([name, dati, src, "export", ("si: " + "; ".join(exp)) if exp else ("non trovato" if export_files else "non trovato (nessuna esportazione nel codice)")])
            era = mentions(name, kind, erase_files)
            rows.append([name, dati, src, "diritto_oblio", ("si: " + "; ".join(era)) if era else ("non trovato" if erase_files else "non trovato (nessuna cancellazione su richiesta nel codice)")])
        if multi:
            tf = next((f for f in fields if TENANT.match(f)), None)
            if not tf and not personale:
                rows.append([name, dati, src, "isolamento", "n/a (né campo di ente né legame con un interessato)"])
            elif not tf:
                rows.append([name, dati, src, "isolamento", "non trovato (nessun campo di ente: l'isolamento passa da una relazione, da verificare nelle letture)"])
            else:
                reads = refs_for(name, kind, "findMany|findFirst|count|aggregate|groupBy" if kind == "prisma" else "filter|all", api_only=True)
                senza = []
                for r in reads:
                    f, n = r.rsplit(":", 1)
                    win = " ".join(texts[f][int(n) - 1:int(n) + 12])
                    if not re.search(rf"\b{re.escape(tf)}\b|tenant|organization|organisation", win, re.I):
                        senza.append(r)
                stato = f"campo {tf}; letture senza filtro visibile: {len(senza)} su {len(reads)}" + (f" ({'; '.join(senza[:3])})" if senza else "")
                rows.append([name, dati, src, "isolamento", ("si: " if not senza else "non trovato: ") + stato])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["entita", "dati", "fonte", "domanda", "prepass", "esito", "gap_id", "note"])
        for r in rows:
            w.writerow(r + ["", "", ""])
    aperte = sum(1 for r in rows if not r[4].startswith(("si", "n/a")))
    print(f"matrice per entità: {len(models)} entità con dati personali, {len(rows)} righe, {aperte} da guardare (prepass «non trovato»)"
          + (" · codice multi-ente: domanda «isolamento» inclusa" if multi else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
