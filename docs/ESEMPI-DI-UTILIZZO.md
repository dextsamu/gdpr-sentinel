# Esempi di utilizzo di gdpr-sentinel

Frasi pronte da incollare; sostituisci i segnaposto tra `<...>`. La skill è un'analisi tecnica e documentale: porta fatti e domande a titolare, DPO e legale, **non** dà pareri legali né giudizi di conformità.

## 1. Verifica tecnica di un'applicazione (solo statica)
> Usa gdpr-sentinel sul repository `<nome>`. Solo analisi statica e documentale. Fai la mappa dei trattamenti reali, confronta l'informativa col codice (fornitori, trasferimenti, cookie) e dammi la matrice A–N con le domande per il DPO.

Esempio di risultato: `examples/collaudo-statico/`.

## 2. Informativa contro codice
> Confronta la pagina privacy di `<repository>` con ciò che il codice contatta davvero: font esterni, CDN, SDK, provider di email/SMS/messaggistica, backup. Elenca le incongruenze.

## 3. Cookie e tracking (con test del browser)
> Ho un'istanza di prova su `<URL autorizzato>`. Con un browser pulito, elenca cookie, storage e richieste a terzi prima e dopo il consenso, e confrontali con il banner e l'informativa. Nessun dato reale.

Senza istanza autorizzata la skill prepara il test e lo segna «preparato, non eseguito».

## 4. Conservazione e cancellazione
> Verifica per ogni categoria di dati quanto vengono conservati, come vengono cancellati o anonimizzati, e cosa succede nei backup.

## 5. Fornitori e trasferimenti
> Elenca i fornitori che ricevono dati personali e, per ciascuno, le domande da fare per DPA, ruolo e trasferimenti extra-SEE. Verifica alla fonte, ora, l'adesione al DPF.

## 6. Abbinata ad appsec-sentinel
> Dopo l'assessment di sicurezza, usa gdpr-sentinel sulla stessa cartella di audit e collega i finding all'articolo 32.

## Dove lanciarla e dove salvare
- In Claude (web/desktop) o in Claude Code, con il repository collegato o i file allegati.
- Crea la cartella di lavoro con `python3 scripts/init_gdpr.py <cartella>` e tienila fuori dal repository.

## Cosa non chiedere
- «Siamo conformi al GDPR?»: la skill non dichiara mai conformità.
- Richieste di diritti o test su dati o servizi reali senza autorizzazione.
