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

1. **Accordo fra due giri su un repository grande.** Con la 1.4.1 i due giri danno lo stesso giudizio sul 91% delle righe aperte di `entita.csv` (cancellazione 28/28, isolamento 37/40, export 11/12, oblio 14/19), con un costo per giro simile a prima. Restano variabili il diritto all'oblio sulle tabelle collegate solo indirettamente all'utente e i temi fuori matrice (documenti, consensi, fornitori: accordo sui gap 62%). Prossimo passo possibile: una seconda griglia per i temi documentali (informativa contro codice, voce per voce).
2. **Rilascio successivo** insieme ad appsec-sentinel.

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
