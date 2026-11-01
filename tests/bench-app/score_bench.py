#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Banco di prova privacy per gdpr-sentinel: un portale soci finto con 15 difetti noti e 5 esche, e il punteggio.

Uso:
    python3 tests/bench-app/score_bench.py prepare <cartella>             # crea <cartella>/bench-app (repository Git)
    python3 tests/bench-app/score_bench.py score <audit> [<audit> …]      # richiamo, difetti alti, falsi allarmi

`prepare` copia l'app (codice e informativa in public/privacy.md) senza la verità e senza commenti che indichino i difetti,
in un repository Git. L'agente va lanciato dentro <cartella>/bench-app, con la cartella di lavoro FUORI da quella cartella.
I difetti sono quasi tutti contraddizioni fra l'informativa e il codice, il caso più frequente nelle verifiche reali.

`score` legge gaps.csv (o findings/findings.json) di ogni cartella:
  - un difetto è trovato se un finding cita uno dei suoi file e il testo contiene una delle sue parole chiave;
  - un'esca è un falso allarme se un finding la cita con severità media o superiore;
  - con più audit: tabella difetto × giro e accordo.
Limiti: il riconoscimento è meccanico (un finding che cita il file giusto con parole sbagliate non conta, e viceversa);
i difetti sono quelli che conosciamo, quindi il richiamo misura la skill su queste classi, non su tutto.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRUTH = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
SEV = {"critica": 0, "alta": 1, "media": 2, "bassa": 3, "informativa": 4}   # priorità dei gap: alta, media, bassa


def prepare(dest):
    app = Path(dest) / "bench-app"
    if app.exists():
        sys.exit(f"esiste già: {app}")
    shutil.copytree(HERE / "template", app)
    for b in app.rglob("*.bench"):   # manifest salvati come *.bench nel repository (dipendenze vulnerabili apposta)
        b.rename(b.with_suffix(""))
    g = lambda *a: subprocess.run(["git", "-C", str(app), "-c", "user.email=dev@example.test", "-c", "user.name=dev", *a],
                                  capture_output=True, text=True, check=True)
    g("init", "-q"); g("add", "-A"); g("commit", "-qm", "versione 1.4.0")
    print(f"pronto: {app}\nLancia l'agente dentro questa cartella; crea la cartella di lavoro fuori (es. {Path(dest) / 'gdpr-A'}).")


def load(audit):
    import csv
    g = Path(audit) / "gaps.csv"
    if g.exists():
        out = []
        for r in csv.DictReader(g.open(encoding="utf-8")):
            if not (r.get("id") or "").strip() or r["id"].startswith("ESEMPIO"):
                continue
            out.append({"id": r["id"], "titolo": r.get("titolo", ""), "osservato": r.get("rischio_interessati", ""), "categoria": r.get("controllo", ""),
                        "severita": (r.get("priorita") or "media").strip().lower(), "asset": "",
                        "prova": {"riferimenti_file": re.split(r"[;\n]", r.get("riferimenti") or ""), "descrizione": ""}})
        return out
    for p in (Path(audit) / "findings" / "findings.json", Path(audit) / "findings.json"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    sys.exit(f"nessun gaps.csv né findings.json in {audit}")


def text(f):
    return " ".join(str(x) for x in (f.get("titolo"), f.get("osservato"), f.get("categoria"), (f.get("prova") or {}).get("descrizione"))).lower()


def cites(f, files):
    refs = [re.sub(r"^\./", "", str(r).split(":")[0]) for r in (f.get("prova") or {}).get("riferimenti_file") or []]
    refs.append(str(f.get("asset") or ""))
    return any(r.endswith(x) or x in r for r in refs for x in files)


def score_one(fs):
    found, fa, used = {}, {}, set()
    for t in TRUTH["difetti"]:
        hit = [f["id"] for f in fs if cites(f, t["file"]) and re.search(t["parole"], text(f))]
        if hit:
            found[t["id"]] = hit; used.update(hit)
    for d in TRUTH["esche"]:
        claim = lambda f: " ".join(str(x) for x in (f.get("titolo"), f.get("osservato"))).lower()   # solo ciò che il finding afferma
        hit = [f["id"] for f in fs if cites(f, d["file"]) and re.search(d["parole"], claim(f)) and SEV.get(f.get("severita"), 9) <= 2]
        if hit:
            fa[d["id"]] = hit
    extra = [f for f in fs if f["id"] not in used and not any(f["id"] in v for v in fa.values())]
    return found, fa, extra


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("prepare", "score"):
        print(__doc__); return 2
    if sys.argv[1] == "prepare":
        prepare(sys.argv[2]); return 0
    audits = sys.argv[2:]
    alti = {t["id"] for t in TRUTH["difetti"] if t["alto"]}
    n = len(TRUTH["difetti"])
    res = {}
    for a in audits:
        fs = load(a)
        found, fa, extra = score_one(fs)
        res[a] = found
        print(f"== {a}")
        print(f"  difetti trovati: {len(found)}/{n} · alti: {len(alti & set(found))}/{len(alti)} · falsi allarmi sulle esche: {len(fa)}/{len(TRUTH['esche'])} · finding fuori elenco: {len(extra)}")
        miss = [t for t in TRUTH["difetti"] if t["id"] not in found]
        for t in miss:
            print(f"  - mancato {t['id']} ({t.get('area', t.get('controllo', ''))}{', alto' if t['alto'] else ''}): {t['titolo']}")
        for d, ids in fa.items():
            print(f"  ! falso allarme {d}: {next(x['titolo'] for x in TRUTH['esche'] if x['id'] == d)} ({', '.join(ids)})")
        for f in extra[:8]:
            print(f"  ? fuori elenco {f['id']} [{f.get('severita')}]: {f.get('titolo', '')[:90]} (da valutare a mano: difetto non piantato o rumore)")
    if len(audits) > 1:
        print("\n== difetto × giro")
        for t in TRUTH["difetti"]:
            print(f"  {t['id']} {'A' if t['alto'] else ' '} " + " ".join("x" if t["id"] in res[a] else "." for a in audits) + f"  {t['titolo'][:70]}")
        sets = [set(res[a]) for a in audits]
        union, inter = set().union(*sets), set.intersection(*sets)
        print(f"accordo sui difetti noti: {len(inter)}/{len(union)} trovati da tutti i giri · trovati da almeno un giro: {len(union)}/{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
