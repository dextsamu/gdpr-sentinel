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

## Prossimo

1. **Accordo oltre il 70%** sui repository grandi: raggruppamento suggerito delle cause vicine prima dell'unione e controllo che ogni controllo A–N abbia risposto alle sue `domande_minime`.
2. **Secondo banco privacy** diverso dal primo (sito di un ente pubblico o di una scuola: modulistica, albo, minori, trasparenza). Misura la generalizzazione, che un banco solo non può misurare.
3. **Giro misurato su Codex e Antigravity**: uno `statica` sul banco privacy con ciascun agente, con punteggio, per poter scrivere nel README che le skill funzionano su quegli agenti e non solo che sono state provate.
4. **Rilascio successivo** insieme ad appsec-sentinel.

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
