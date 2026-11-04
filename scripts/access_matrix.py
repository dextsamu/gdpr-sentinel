#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Samuele Cucurnia e Pietro Previtali
"""Matrice dei ruoli e degli accessi: per ogni entità con dati personali e ogni ruolo, chi può leggerla e quanto.

Uso:
    python3 access_matrix.py <repo> --audit <cartella-audit>      # dopo entity_matrix.py (pre-passaggio)

Scrive <cartella-audit>/accessi.csv, una riga per coppia entità × ruolo:
    entita, dati, ruolo, prepass, ambito, esito, gap_id, note

Perché: con la matrice per entità e quella dell'informativa, due giri sullo stesso gestionale davano lo stesso giudizio
su quasi tutte le celle, ma l'accordo sull'insieme dei gap restava intorno al 60%: le cause viste da un giro solo erano
quasi tutte di ruoli e accessi interni (dati sanitari visibili a chi non ne ha bisogno, GPS ai responsabili, elenchi
completi a ogni dipendente). Ogni giro guardava le coppie che gli capitavano. Qui le coppie sono fisse.

Ruoli: l'enum dei ruoli usato dal modello utente (Prisma), le scelte di un campo ruolo (Django), un ENUM SQL di una
colonna ruolo, oppure i valori confrontati con un campo ruolo nel codice (`user.role === 'X'`, `$_SESSION['ruolo']
!== 'x'`). In più `pubblico (senza login)` se qualche lettura sta in un file senza controllo di accesso visibile.
I flag sull'utente (`canAccessX`, `isY`, `is_staff`) non diventano righe: compaiono nel `prepass` quando un file li cita.

Righe per ruolo solo per le entità con dati a rischio più alto (salute e categorie particolari, geolocalizzazione, dati
finanziari, documenti); per tutte la riga «pubblico» quando c'è una lettura senza controllo di accesso.

`prepass`, per le entità lette dalle API: le letture (file:riga) divise in «citano il ruolo», «controllo di permesso
generico», «nessun controllo di ruolo visibile» e «citano solo altri ruoli». È un indizio meccanico: citare un ruolo non
vuol dire limitarlo. I ruoli amministrativi sono pre-compilati «n/a probabile». L'agente chiude le altre righe con
`ambito` (propri, gruppo, tutti, nessuno) ed `esito` (ok, gap con gap_id e file:riga in note, non applicabile, non
verificabile con il motivo in note).
"""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import draft_ropa as dr          # noqa: E402
import entity_matrix as em       # noqa: E402  (stessi file, stesse esclusioni, stesse cartelle API)

USER_MODEL = re.compile(r"^(user|users|utente|utenti|member|members|socio|soci|account|accounts|persona|personale|staff)$", re.I)
ROLE_FIELD = r"(?:role|ruolo|ruoli|roles|userRole|user_role|tipo_utente|profilo)"
ADMIN = re.compile(r"(admin|superuser|super_user|amministrator|root|sysadmin|owner)", re.I)
FLAG = re.compile(r"^(is|can|has|puo|may)_?[A-Za-z]\w*$")
FLAG_SKIP = re.compile(r"(active|deleted|verified|enabled|locked|email|totp|mfa|cancel|confirm|pending|shared|complet|read|archiv|default|public|privat|"
                       r"onboard|first|blocked|banned|online|test|demo|anonym)", re.I)
PERM = re.compile(r"\b(hasPermission|has_perm|can\(|authorize|requireRole|checkRole|requirePermission|permission_required|PermissionRequired|"
                  r"@PreAuthorize|Gate::|->can\(|policy|isAllowed|ensureRole|requireAdmin|requireResponsabile|withRole)\b", re.I)
AUTH = re.compile(r"(requireAuth|getServerSession|getSession|auth\(\)|currentUser|getCurrentUser|login_required|LoginRequired|IsAuthenticated|"
                  r"\$_SESSION|session\[|request\.user|req\.user|ctx\.user|withAuth|authenticate|verifyToken|jwt|@UseGuards|middleware\(['\"]auth)", re.I)
READS_PRISMA = "findMany|findFirst|findUnique|findFirstOrThrow|findUniqueOrThrow|count|aggregate|groupBy"
READS_DJANGO = "filter|all|get|values|values_list|exclude"
# Righe per ruolo solo per i dati a rischio più alto: su un gestionale di 63 entità una riga per ruolo e per entità erano
# 144 righe da chiudere, troppe per un giro (e il nome di un collega in un elenco turni non è la domanda). Per le altre
# entità resta la riga «pubblico»; l'isolamento fra enti sta in entita.csv, i controlli di autorizzazione in appsec-sentinel.
SENSIBILI = re.compile(r"(salute|particolari|geoloc|finanziari|documenti)", re.I)


def roles_and_flags(repo, texts):
    """(ruoli, flag, fonte) dal codice. Ruoli in ordine di scoperta, senza duplicati."""
    roles, flags, src = [], [], ""
    for sp in repo.rglob("*.prisma"):
        if set(sp.relative_to(repo).parts) & em.SKIP:
            continue
        t = sp.read_text(encoding="utf-8", errors="replace")
        enums = {m.group(1): re.findall(r"^\s*([A-Za-z_]\w*)\s*$", m.group(2), re.M) for m in re.finditer(r"^enum\s+(\w+)\s*\{(.*?)^\}", t, re.S | re.M)}
        for m in re.finditer(r"^model\s+(\w+)\s*\{(.*?)^\}", t, re.S | re.M):
            if not USER_MODEL.match(m.group(1)):
                continue
            for fm in re.finditer(r"^\s+(\w+)\s+(\w+)(\[\])?", m.group(2), re.M):
                fname, ftype = fm.group(1), fm.group(2)
                if ftype in enums and re.search(r"role|ruol", fname + ftype, re.I) and not roles:
                    roles, src = list(enums[ftype]), f"{sp.relative_to(repo).as_posix()} enum {ftype}"
                elif ftype == "Boolean" and FLAG.match(fname) and not FLAG_SKIP.search(fname):
                    flags.append(fname)
    if not roles:   # Django: choices del campo ruolo o TextChoices
        for f, lines in texts.items():
            if not f.endswith("models.py"):
                continue
            t = "\n".join(lines)
            m = re.search(r"class\s+\w*(?:Role|Ruolo)\w*\((?:models\.)?(?:TextChoices|IntegerChoices)\):(.*?)(?=^\S)", t + "\nX", re.S | re.M)
            if m:
                roles = re.findall(r"^\s+([A-Z_][A-Z0-9_]*)\s*=", m.group(1), re.M)
            else:
                m = re.search(r"(?i)(?:ROLE|RUOL)\w*_?CHOICES\s*=\s*[\[(](.*?)[\])]\s*$", t, re.S | re.M)
                if m:
                    roles = re.findall(r"\(\s*['\"](\w+)['\"]", m.group(1))
            flags += [x for x in re.findall(r"^\s+(\w+)\s*=\s*models\.BooleanField", t, re.M) if FLAG.match(x) and not FLAG_SKIP.search(x)]
            if roles:
                src = f"{f} (scelte del ruolo)"
                break
    if not roles:   # SQL: colonna ruolo ENUM('a','b')
        for f, lines in texts.items():
            if f.endswith(".sql"):
                m = re.search(rf"(?i){ROLE_FIELD}\w*[`\"\]]?\s+ENUM\s*\(([^)]*)\)", "\n".join(lines))
                if m:
                    roles, src = re.findall(r"'(\w+)'", m.group(1)), f"{f} (ENUM della colonna ruolo)"
                    break
    if not roles:   # valori confrontati con un campo ruolo nel codice
        seen = {}
        rx = re.compile(rf"(?i){ROLE_FIELD}['\"]?\]?[^\n=!;]{{0,15}}?(?:[!=]==?|\bin\s*\[?)\s*['\"]([A-Za-z_]\w*)['\"]|['\"]([A-Za-z_]\w*)['\"]\s*[!=]==?\s*[\w$.\[\]'\"]*{ROLE_FIELD}\b")
        for f, lines in texts.items():
            for n, line in enumerate(lines, 1):
                for m in rx.finditer(line):
                    v = m.group(1) or m.group(2)
                    seen.setdefault(v, f"{f}:{n}")
        roles = list(seen)
        src = ("valori confrontati con il campo ruolo: " + "; ".join(f"{k} ({v})" for k, v in list(seen.items())[:4])) if seen else ""
    return roles, sorted(set(flags)), src


def mentions_role(text, role):
    if role.isupper() or "_" in role:
        return re.search(rf"\b{re.escape(role)}\b", text) is not None
    return re.search(rf"['\"]{re.escape(role)}['\"]", text, re.I) is not None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--audit", type=Path, required=True)
    a = ap.parse_args()
    repo, audit = a.repo.resolve(), a.audit.resolve()
    texts = {}
    for p in em.files(repo):
        try:
            texts[str(p.relative_to(repo)).replace("\\", "/")] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            pass
    roles, flags, src = roles_and_flags(repo, texts)
    # entità: quelle della matrice per entità (stesso elenco fra le due matrici), altrimenti ricalcolate
    ents = {}
    ep = audit / "entita.csv"
    if ep.exists():
        for r in csv.DictReader(ep.open(encoding="utf-8")):
            ents.setdefault(r["entita"], (r["dati"], r["fonte"]))
    else:
        for name, fields, s in dr.models(repo):
            g = [k for k, rx in dr.GROUPS.items() if any(re.search(rx, f, re.I) for f in fields)]
            if g:
                ents.setdefault(name, (", ".join(g), s))
    fields_of = {n.lower(): f for n, f, _ in dr.models(repo)}
    reads_of = {}
    for name, (_, fonte) in ents.items():
        kind = "prisma" if fonte.endswith(".prisma") else "django" if fonte.endswith(".py") else "sql"
        acc = re.escape(em.accessor(name, kind))
        if kind == "prisma":
            rx = re.compile(rf"\b(?:prisma|tx|db|client)\s*\.\s*{acc}\s*\.\s*(?:{READS_PRISMA})\b")
        elif kind == "django":
            rx = re.compile(rf"\b{acc}\.objects\b[^\n]*\.(?:{READS_DJANGO})\b")
        else:
            rx = re.compile(rf"(?i)\bselect\b[^;]*?\bfrom\s+[`\"\[]?{acc}[`\"\]]?\b")
        out = []
        for f, lines in texts.items():
            if not (em.API_PATH.search(f) or f.endswith(".php")) or f.endswith(".sql"):
                continue
            for n, line in enumerate(lines, 1):
                if rx.search(line):
                    out.append((f, n))
        reads_of[name] = out
    pubblico = any(not AUTH.search("\n".join(texts[f])) for rs in reads_of.values() for f, _ in rs)
    cols = roles + (["pubblico (senza login)"] if pubblico else [])
    rows = []
    for name, (dati, _) in ents.items():
        rs = reads_of[name]
        if not rs:
            rows.append([name, dati, "*", "n/a (nessuna lettura dell'entità nelle API o nelle pagine)", "", "", "", ""])
            continue
        if not cols:
            rows.append([name, dati, "*", f"non trovato: nessun ruolo riconosciuto nel codice; letture: {len(rs)} ("
                         + "; ".join(f"{f}:{n}" for f, n in rs[:4]) + ")", "", "", "", ""])
            continue
        if not USER_MODEL.match(name) and not any(em.USER_LINK.match(f) for f in fields_of.get(name.lower(), [])):
            # catalogo, configurazione o luogo: i dati non riguardano una persona (su UnityKore i due giri chiudevano queste
            # righe metà «non applicabile» e metà «ok», e la classificazione veniva da un campo come «nome» del corso)
            for r in cols:
                if r == "pubblico (senza login)" or SENSIBILI.search(dati):
                    rows.append([name, dati, r, "n/a probabile: nessun legame con una persona nel modello (catalogo, configurazione o luogo); "
                                 "cambiala solo se i campi contengono dati di persone", "", "", "", ""])
            continue
        if em.TECH.search(name):
            for r in cols:
                rows.append([name, dati, r, "n/a probabile: credenziale o token tecnico, letto dal sistema e non mostrato (verificare)", "", "", "", ""])
            continue
        for r in cols:
            if r != "pubblico (senza login)" and not SENSIBILI.search(dati):
                continue
            ref = lambda xs: "; ".join(f"{f}:{n}" for f, n in xs[:4]) + ("…" if len(xs) > 4 else "")
            if r == "pubblico (senza login)":
                aperte = [(f, n) for f, n in rs if not AUTH.search("\n".join(texts[f]))]
                rows.append([name, dati, r, (f"non trovato: letture in file senza controllo di accesso visibile: {len(aperte)} ({ref(aperte)})"
                                             if aperte else "n/a (ogni lettura ha un controllo di accesso visibile)"), "", "", "", ""])
                continue
            if ADMIN.search(r):
                rows.append([name, dati, r, "n/a probabile: ruolo amministrativo, accesso ampio atteso; gap solo se informativa, DPIA o "
                             "regolamenti lo limitano", "", "", "", ""])
                continue
            cita, perm, nessuno, altri, fl = [], [], [], [], set()
            for f, n in rs:
                t = "\n".join(texts[f])
                fl |= {x for x in flags if re.search(rf"\b{re.escape(x)}\b", t)}
                if mentions_role(t, r):
                    cita.append((f, n))
                elif any(mentions_role(t, o) for o in roles if o != r):
                    altri.append((f, n))
                elif PERM.search(t):
                    perm.append((f, n))
                else:
                    nessuno.append((f, n))
            parti = [f"letture: {len(rs)}"]
            for lab, xs in (("citano il ruolo", cita), ("controllo di permesso generico", perm), ("nessun controllo di ruolo visibile", nessuno),
                            ("citano solo altri ruoli", altri)):
                if xs:
                    parti.append(f"{lab}: {len(xs)} ({ref(xs)})")
            if fl:
                parti.append("flag citati: " + ", ".join(sorted(fl)))
            rows.append([name, dati, r, "non trovato: " + " · ".join(parti), "", "", "", ""])
    out = audit / "accessi.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["entita", "dati", "ruolo", "prepass", "ambito", "esito", "gap_id", "note"])
        w.writerows(rows)
    aperte = sum(1 for r in rows if not r[3].startswith(("si", "n/a")))
    print(f"matrice dei ruoli e degli accessi: {len(roles)} ruoli ({src or 'nessuna fonte'})"
          + (" + pubblico" if pubblico else "") + (f", flag: {', '.join(flags)}" if flags else "")
          + f" · {len(ents)} entità, {len(rows)} righe, {aperte} da guardare")
    return 0


if __name__ == "__main__":
    sys.exit(main())
