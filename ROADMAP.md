# Roadmap di gdpr-sentinel

Cosa è fatto, cosa viene dopo e perché. Le priorità vengono dalle misure (banco privacy e giri reali), non da una lista di desideri: ogni voce dice quale numero dovrebbe cambiare. Nessuna data promessa; l'ordine è l'ordine di lavoro. La skill non dichiara mai conformità e non sostituisce DPO o legale: nessuna voce va in quella direzione.

## Fatto

**1.0 – 1.1 (29–30/10/2026).** Mappa dei trattamenti reali, matrice A–N, stati onesti, domande per titolare e DPO, bozze di registro e DPIA, controllo dei cookie su istanze autorizzate, report PDF condiviso con appsec-sentinel.

**1.2.0 (01/11/2026), prima versione pubblica**:
- gap strutturati in `gaps.csv`, pre-passaggio deterministico (fornitori, retention, indizi privacy nel codice);
- banco privacy con difetti noti: 15/15 in due giri, 0 falsi allarmi sulle esche;
- `doppio` con unione per causa e smentita dei gap ad alta priorità (`apply_refutations.py`);
- `domande_minime` per ogni controllo e regola «un gap = una causa»: accordo fra due giri su un gestionale reale dal 44–46% al 63%.

**1.2.1 (01/11/2026)**: script condivisi allineati ad appsec-sentinel (controllo di consegna); nessun cambiamento nel metodo privacy.

**1.2.2 (01/11/2026)**: brief per la smentita dei gap (`gap_briefs.py`). Sul banco privacy con 4 gap falsi su 9: 3 respinti e 1 declassato, nessun vero respinto.

**Dopo la 1.2.2**: secondo banco privacy `tests/bench-pa` (scuola, PHP): 15/15 in due giri, 0 falsi allarmi; il pre-passaggio ora riconosce fornitori, tabelle e log anche in PHP e SQL.

**1.3.0 (01/11/2026)**: smentita senza sottoagenti (`refutation_pack.py`, provata sul secondo banco: 13 gap verificati da una sessione nuova), esiti riportati anche nella matrice, `punti-pericolosi.csv` per categorie di indizi (accordo su UnityKore 59%: nessun effetto misurabile), PDF con threat model e test dinamici.

**Giro misurato su Antigravity e Codex (01/11/2026)**: `statica` sul secondo banco con lo stesso prompt: 14/15 e 14/15, 0 falsi allarmi, smentita indipendente in entrambi (sessione nuova con il pacchetto su Antigravity, sottoagente su Codex). Dettagli in `docs/ALTRI-AGENTI.md`.

**1.4.0 – 1.4.2 (02/11/2026)**: matrice per entità (`entita.csv`) e matrice dell'informativa (`informativa.csv`): su UnityKore stesso giudizio su 98% e 81% delle righe aperte fra due giri.

**1.5.0 (04/11/2026)**: terza matrice, ruoli e accessi (`accessi.csv`): chi vede cosa, una riga per ruolo sulle entità con dati a rischio più alto e una riga «pubblico» per le letture senza login. Due paia di giri su UnityKore: 86% e 92% di giudizi uguali (ambito 71% e 96%); l'accordo sull'insieme dei gap resta 60–69%.

## Prossimo

1. **Accordo fra due giri su un repository grande.** Con la 1.4.2 le due matrici rendono stabile la parte strutturata (entità 98%, informativa 81%) e le cause gravi (82%); l'accordo sull'insieme dei gap resta intorno al 60% perché le cause fuori matrice (ruoli e accessi interni, procedure, dettagli dei documenti) cambiano da un giro all'altro. Per un cliente resta `doppio`; con la 1.5.0 anche chi vede cosa è stabile (86–92%), ma l'accordo complessivo resta 60–69%: le differenze stanno ora in documenti, procedure e segreti versionati, che non si prestano a una matrice per riga. Prossimo passo da misurare: un elenco fisso di cause documentali (informativa per versione, DPIA, registro, accordi) chiuso come le matrici.

## Dopo

- **`cookie_scan.py` su un sito reale autorizzato per iscritto.** Provato il 02/11/2026 sul sito della scuola servito in locale (risultato atteso su tutte le pagine, esche comprese); manca un sito pubblico vero con il consenso del titolare.
- **Diritti degli interessati su istanza autorizzata**: esportazione e cancellazione provate con account sintetici, con gli stessi limiti dei test dinamici di appsec-sentinel. Serve un banco con database in esecuzione (il portale soci del primo banco, con PostgreSQL).
- **Gap che raggruppano più cause**: un controllo automatico basato su titolo e numero di file citati è stato provato (02/11/2026) e scartato, perché segnalava allo stesso modo i giri ben separati e quelli raggruppati. Serve un criterio migliore.
- **Registro art. 30 sulle app grandi**: raggruppare automaticamente le righe della bozza per finalità, che oggi vanno raggruppate a mano.
- **Trasferimenti e adesioni al DPF**: verifica guidata quando il mandato consente la rete, con data della verifica nel report.

## Non in programma

- Giudizi di conformità, punteggi «GDPR», pareri legali.
- Invio di dati personali o documenti del titolare a servizi esterni.

## Come proporre una voce

Apri una issue con il caso concreto (trattamento, cosa è stato mancato o sbagliato, come si misura).
