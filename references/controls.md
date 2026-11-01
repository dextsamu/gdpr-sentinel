# Controlli GDPR / ePrivacy A–N — checklist dettagliata

Per ogni controllo: cosa guardare e quale errore di ragionamento evitare. Gli articoli citati vanno sempre riverificati sul testo ufficiale (`sources.md`).

## Indice
A Mappa trattamenti · B Principi e basi giuridiche · C Dati particolari/penali/minori · D Trasparenza · E Cookie e tracking · F Diritti · G Retention · H Privacy by design e sicurezza · I Fornitori · J Trasferimenti · K Governance · L Incidenti · M Profilazione/AI/marketing · N Casi italiani

**A. Mappa dei trattamenti e ruoli.** Identifica titolari, responsabili, contitolari, autorizzati e destinatari per ogni finalità. Un fornitore può avere ruoli diversi su flussi diversi. Censisci raccolta, derivazioni, visualizzazione, accesso interno, esportazione, comunicazione, conservazione, cancellazione, incluse code, log, copie, backup, supporto, provider AI.

**B. Principi e basi giuridiche (artt. 5, 6).** Finalità specifiche, necessità, minimizzazione, correttezza, trasparenza, esattezza, limitazione della conservazione, accountability. *Il consenso non è obbligatorio per ogni trattamento.* Se è usato: libertà, specificità, granularità, informazione, prova, revocabilità (EDPB 05/2020). Se si usa l'interesse legittimo: verifica presupposti e valutazione richiesta. Non inventare basi giuridiche al posto del titolare.

**C. Dati particolari, penali, minori.** Distingui base art. 6 e condizione art. 9; dati art. 10 e norme nazionali. Non chiamare «biometrico art. 9» qualsiasi foto o dato corporeo: valuta finalità di identificazione univoca e contenuto sanitario. Minori: tipo di servizio, base giuridica, età, autorizzazioni; niente soglia unica per ogni trattamento.

**D. Trasparenza (artt. 13/14).** **Confronto sistematico informativa ↔ codice**: elenca i destinatari e i paesi dichiarati nell'informativa e confrontali con ciò che il codice contatta davvero (font e icone esterni, CDN, SDK, API di terzi, provider di email/SMS/messaggistica, storage e backup, strumenti di monitoraggio, calendari). Una dichiarazione assoluta («nessun trasferimento extra-SEE», «solo server UE») è verificabile e va confrontata con ogni fornitore trovato. Confronta informative, interfacce, contratti e codice: identità/contatti, finalità, basi, destinatari, trasferimenti, retention, diritti, reclamo, obbligatorietà, decisioni automatizzate. Cerca funzionalità, SDK, integrazioni e finalità assenti dall'informativa o descritte in modo inesatto.

**E. Cookie e tracking (ePrivacy, linee guida Garante).** Inventaria cookie, storage, pixel, SDK, fingerprinting, tag server-side, analytics, video/mappe/font/embed esterni che ricevono dati. In **browser pulito** verifica traffico e stato: prima della scelta, dopo rifiuto, dopo consenso granulare, dopo revoca. Controlla blocco preventivo quando richiesto, scelta effettiva, assenza di dark pattern, prova del consenso. Non presumere che un analytics sia «tecnico» dal nome né che ogni chiamata esterna richieda consenso: valuta finalità e configurazione effettive.

**F. Diritti degli interessati.** Accesso, rettifica, cancellazione, limitazione, portabilità (ove applicabile), opposizione, revoca. Identificazione proporzionata, nessuna esposizione di terzi negli export, tutte le categorie di dati coperte, download sicuri, tracciamento delle richieste. Tempi e proroghe secondo gli articoli pertinenti: un mese non è un «termine universale di 30 giorni».

**G. Retention e cancellazione effettiva.** Includi i **backup** (dove sono, per quanto, se cifrati, come si applica una cancellazione) e i fornitori che li ospitano. Per categoria: durata o criterio motivato, obblighi di conservazione, meccanismo verificabile. Esamina soft delete, copie, repliche, indici, cache, log, file, dati derivati, dataset AI. Backup: scadenza, segregazione, uso limitato, riapplicazione delle cancellazioni dopo restore. Non chiedere cancellazioni incompatibili con obblighi legali; pseudonimizzazione ≠ anonimizzazione.

**H. Privacy by design/default e sicurezza (artt. 25, 32).** Impostazioni protettive, accessi minimi, esposizione pubblica, prevenzione degli accessi interni impropri, cifratura/chiavi, pseudonimizzazione, disponibilità, ripristino, test periodici proporzionati al rischio. Collega ai finding di `appsec-sentinel` se esiste un audit di sicurezza. Una misura mancante non dimostra da sola una violazione senza contesto e alternative.

**I. Fornitori e accordi.** Ruoli, DPA art. 28, accordi art. 26 se pertinenti, istruzioni, sub-responsabili, misure effettive, audit, notifiche, assistenza sui diritti, restituzione/cancellazione. Confronta promesse contrattuali e comportamento reale dell'app; il certificato del fornitore non dimostra la sicurezza della *tua* configurazione.

**J. Trasferimenti internazionali.** Mappa entità destinatarie, paesi, accessi remoti, supporto, log, backup, subfornitori — non solo la regione del database. Meccanismo applicabile: decisione di adeguatezza, DPF per entità e ambito corretti, SCC/TIA e misure supplementari (EDPB 01/2020). Controlla stato attuale e prove: hosting UE o marchio del provider non sono garanzia automatica.

**K. Governance.** Responsabilità art. 24, rappresentante art. 27, registro art. 30 e relative eccezioni, necessità di DPIA artt. 35/36, DPO artt. 37-39 (obbligo e indipendenza), autorizzazioni, formazione, gestione accessi. Non rendere universali obblighi che dipendono da presupposti, scala, categorie di dati e rischio.

**L. Incidenti e data breach.** Rilevazione, classificazione, registro delle violazioni, reperibilità, raccolta informazioni. Distingui: avviso del responsabile al titolare *senza ingiustificato ritardo*; notifica del titolare all'autorità (art. 33; 72 ore dalla conoscenza, con eccezione se il rischio è improbabile); comunicazione agli interessati in caso di rischio elevato (art. 34, con eccezioni). Le 72 ore vanno valutate nel contesto, non come obbligo universale di ogni soggetto per qualsiasi incidente. Non decidere tu la notifica.

**M. Profilazione, AI e marketing.** Finalità ulteriori, arricchimenti, segmentazione, comunicazioni commerciali, opposizione, decisioni automatizzate art. 22 (significatività dell'intervento umano). Per l'AI: dati verso i provider, training, output e inferenze sugli interessati; distingui GDPR dagli obblighi AI Act eventualmente applicabili.

**N. Casi italiani e settoriali (se pertinenti).** Monitoraggio dei lavoratori, geolocalizzazione, amministratori di sistema e relativi log, dati sanitari, minori, comunicazioni elettroniche, indicazioni attuali di Garante/ACN. Se emergono presupposti concreti valuta separatamente NIS2. Non inventare tempi di conservazione standard identici per ogni log o organizzazione.
