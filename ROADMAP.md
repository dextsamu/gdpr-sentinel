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

## Prossimo

1. **Accordo oltre il 70%** sui repository grandi. Provato il 01/11/2026 con `punti-pericolosi.csv`: 59% (prima 63%), cioè nessun effetto misurabile; le differenze stanno nei temi documentali (governance, data breach, ruolo del DPO, segreti versionati). Prossimo tentativo: domande minime documentali numerate per i controlli D, K, L, chiuse una per una come le categorie, e abbinamento nell'unione dei gap con le stesse righe di codice citate anche se descritti in modo diverso.
2. **Rilascio successivo** insieme ad appsec-sentinel.

## Dopo

- **`cookie_scan.py` su un sito reale autorizzato per iscritto** (oggi provato solo su una pagina locale).
- **Diritti degli interessati su istanza autorizzata**: esportazione e cancellazione provate con account sintetici, con gli stessi limiti dei test dinamici di appsec-sentinel.
- **Registro art. 30 sulle app grandi**: raggruppare automaticamente le righe della bozza per finalità, che oggi vanno raggruppate a mano.
- **Trasferimenti e adesioni al DPF**: verifica guidata quando il mandato consente la rete, con data della verifica nel report.

## Non in programma

- Giudizi di conformità, punteggi «GDPR», pareri legali.
- Invio di dati personali o documenti del titolare a servizi esterni.

## Come proporre una voce

Apri una issue con il caso concreto (trattamento, cosa è stato mancato o sbagliato, come si misura).
