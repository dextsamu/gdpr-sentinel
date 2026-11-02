# Changelog

Formato basato su [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/); versioni secondo [SemVer](https://semver.org/lang/it/).

## [Non rilasciato]
### Aggiunto (prova dinamica)
- **`cookie_scan.py` provato su un sito in funzione**: il sito della scuola (`tests/bench-pa`) servito in locale con PHP. Prima di ogni interazione rileva in home YouTube, reCAPTCHA e Google Fonts, nei contatti anche Google Maps; nella pagina eventi nessun YouTube (il video si carica solo al clic, l'esca); Matomo sul server della scuola non è una terza parte; `PHPSESSID` è riconosciuto come cookie di sessione. Senza blocco, YouTube imposta quattro cookie sul suo dominio, classificati «di terze parti».
- `cookie_scan.py`: classificazione dal percorso quando lo stesso host serve servizi diversi (`www.google.com/recaptcha` e `/maps`); classe dei cookie (di terze parti, sessione o sicurezza, da classificare); opzione `--blocca-terzi`, che registra le richieste verso terzi senza inviarle (nessun dato esce, risultato indipendente dalla rete). Test automatico in `tests/run_checks.py` quando PHP e Playwright sono disponibili.

### Misurato (Juice Shop con altri agenti)
- `appsec-sentinel rapido` su Juice Shop, stesso prompt: Codex 18/32 (vicino 22), Antigravity 6/32 (vicino 9), Claude 19–23/32. Tabella in `docs/ALTRI-AGENTI.md`.

### Aggiunto
- `punti-pericolosi.csv` comprende sempre quattro temi documentali, anche senza indizi nel codice: informativa e trasparenza (D), governance (K: registro, DPIA, nomine, accordi art. 28), data breach (L), segreti e configurazioni versionate (solo i file tracciati da Git).
- `merge_audits.py` (condiviso): righe o intervalli dello stesso file che si sovrappongono (± 3 righe) contano come citazione vicina (+0,4): due giri citano spesso la stessa istruzione con un numero di riga diverso (`route.ts:312` e `:313`) o con intervalli diversi (`330-346` e `313-346`). Rimisurando tutte le coppie di giri su UnityKore: 59→65%, 63→67%, 44→60%, 46→50%, 56→60%, 50→63%; appsec invariato (Juice 75%, Django 88%, Laravel 94%). Le unioni nuove sono state lette a mano: sono la stessa causa.
- **`letture.csv`**: il pre-passaggio sceglie i file da leggere a fondo, uguali per ogni giro (i 30 file con indizi in più categorie e fino a 10 documenti privacy); ogni riga chiude con `si` o con `no` e il motivo, altrimenti `chiudi` fallisce. Su UnityKore i due giri con l'elenco hanno letto per intero 16 e 32 file su 38 e impiegato circa 13 minuti invece di 9–10.

### Misurato
- **Accordo su UnityKore, con l'unione corretta: 60% (giri con i temi documentali) e 63% (giri anche con `letture.csv`)**; in tutto sei coppie di giri fra 50% e 67%. Prima stima: 56% (31 e 33 gap, `chiudi` senza falliti, 13 categorie chiuse in entrambi). Nessun miglioramento oltre la variabilità fra coppie di giri (56–67%): l'obiettivo «oltre il 70%» non è raggiungibile così su un repository di oltre mille file, e la skill continua a indicare `doppio` per le app grandi. Dettagli in ROADMAP.

## [1.3.2] - 2026-11-02
### Misurato
- **Codex**: `appsec-sentinel rapido` sul banco Django, 11/11 difetti (6/6 alti), 0 falsi allarmi, smentita con un sottoagente indipendente (3 resistono, 1 declassato), `chiudi` senza falliti. Con Antigravity (10/11) le due skill sono ora misurate su Claude, Codex e Antigravity.

## [1.3.1] - 2026-11-01
### Misurato
- **Antigravity e Codex**: `gdpr-sentinel statica` sul secondo banco privacy, stesso prompt: 14/15 difetti e 0 falsi allarmi per entrambi, smentita indipendente fatta in entrambi i casi (Antigravity con il pacchetto in una sessione nuova, Codex con un sottoagente). Tabella in `docs/ALTRI-AGENTI.md`. Corretta l'esca T02 del banco (si attivava su «preventiva»).

### Corretto
- Parole vietate e giudizi di conformità: «conforme all'informativa», «conforme a quanto dichiarato» confrontano due testi e non sono più segnalati; «il sito è conforme» resta vietato. Emerso dal giro di Antigravity sul secondo banco privacy (01/11/2026): il verificatore aveva scritto l'ipotesi che stava smentendo e `chiudi` falliva.

## [1.3.0] - 2026-11-01
### Aggiunto
- **Report PDF per `standard` e `completo`**: due sezioni nuove, «Threat model» (da `report/threat-model.md`: titoli, elenchi e tabelle resi come testo) e «Test dinamici eseguiti» (le righe della matrice endpoint con `test_eseguito=si`: identità, controllo atteso, esito osservato, finding). Prima il PDF mostrava solo il conteggio degli endpoint provati.
- **`punti-pericolosi.csv` anche in gdpr-sentinel**: il pre-passaggio scrive una riga da chiudere per ogni categoria di indizi trovata (tracker e risorse di terzi, cookie, dati particolari, minori, geolocalizzazione, log con dati personali, diritti, marketing, fornitori), con i punti in `registro-tool/punti-pericolosi.txt`; ogni riga chiude con `gap` (ID nella colonna `finding`, almeno uno che cita un file della categoria) o `non difetto` con un `file:riga` letto; «non esaminato» fa fallire `chiudi`. Motivo: nei due giri reali sullo stesso gestionale (accordo 63%) metà delle cause viste da un giro solo stava in categorie che l'altro non aveva aperto (log, GPS, video incorporati, dati sanitari). **Misurato su UnityKore, due giri `statica` nuovi**: 27 e 24 gap, `chiudi` senza falliti, tutte le 9 categorie chiuse in entrambi; **accordo 59%** (corrispondente 76%), contro il 63% dei due giri precedenti: nessun miglioramento, entro la variabilità. Le cause viste da un giro solo ora stanno quasi tutte fuori dalle categorie (documenti di governance, procedura data breach, file `.env` versionati, ruolo del DPO, età dei volontari) e una coppia è la stessa causa scritta in due modi (consenso GPS non applicato) che l'unione non abbina. L'obiettivo «oltre il 70%» resta aperto: le categorie rendono uniforme la copertura dove ci sono indizi nel codice, non sui temi documentali.
- **Smentita senza sottoagenti** (`scripts/refutation_pack.py`, condiviso con appsec-sentinel): pacchetto per una seconda sessione con istruzioni, metodo e un brief per gap ad alta priorità, e reimportazione degli esiti. **Provato** sul secondo banco: una sessione nuova con il solo pacchetto ha verificato 13 gap (12 resistono, 1 declassato: il modello dell'albo non è raggiungibile così com'è scritto) e gli esiti sono stati applicati con `importa`.
- `apply_refutations.py` riporta gli esiti anche nella colonna `smentita` di `gdpr-matrix.csv`, per le righe i cui gap sono tutti smentiti (prima la matrice restava «non eseguita» e `chiudi` segnalava 7 warning dopo una smentita fatta).

### Corretto
- `build_report_pdf.py`: una riga CSV con più colonne dell'intestazione (virgola fuori dalle virgolette) faceva fallire il PDF; ora le colonne in più vengono unite all'ultima. Emerso dal giro `standard` del 01/11/2026 sul PC dell'autore.
- `gap_briefs.py` sceglieva solo i gap con `smentita` vuota o esattamente «non eseguita»: ora anche «non eseguita | motivo | …», la forma che la skill fa scrivere.

## [1.2.3] - 2026-11-01
### Aggiunto
- **Secondo banco privacy** `tests/bench-pa`: sito di un istituto comprensivo in PHP + MariaDB (minori, albo online, amministrazione trasparente, modulistica, servizi incorporati), 15 difetti e 5 esche. **Misurato**: due giri `statica` indipendenti, 15/15 difetti ciascuno (6/6 alti), 0 falsi allarmi sulle esche, accordo 15/15 sui difetti noti. Due regole delle esche sono state ristrette dopo il primo giro, perché contavano come falso allarme un gap corretto che citava la pagina degli eventi come confronto e un gap vero sul file di log.

### Corretto (emerso dal secondo banco)
- Il pre-passaggio non riconosceva nulla su un sito PHP: 0 fornitori e 0 tabelle. Ora `draft_ropa.py` legge anche i file `.php` (e `.htm`, `.vue`, `.svelte`, `.twig`, `.erb`, `.jsp`, `.cshtml`…), riconosce i servizi dal percorso (Google reCAPTCHA e Google Maps su `www.google.com`), Mailgun, SendGrid, YouTube senza cookie, Vimeo, hCaptcha, Turnstile, e ricava i trattamenti dagli schemi SQL (`CREATE TABLE`); `privacy_scan.py` riconosce i log PHP e Python (`file_put_contents(… .log)`, `error_log`, `syslog`, `logging`) e i cookie PHP (`setcookie`, `session_start`). Sul sito della scuola: 6 fornitori, 7 tabelle, il log dei contatti.

## [1.2.2] - 2026-11-01
### Aggiunto
- **Brief per la smentita dei gap** (`scripts/gap_briefs.py <cartella> --repo <repository>`): un file per gap in `smentite/` con l'affermazione, le righe di codice citate e le ipotesi di smentita della privacy (il codice fa davvero ciò che il gap dice? dato non personale, altro titolare, obbligo di legge, informativa che già lo copre, job di cancellazione altrove, più quelle dell'area A–N); senza la motivazione dell'autore. Usato nel `doppio` e nella `smentita`. **Misurato** sul banco privacy con 9 gap ad alta priorità, 4 dei quali falsi aggiunti apposta (cookie di sessione senza consenso, tentativi di login mai cancellati, esportazione assente, coordinate della sede come dato personale): un sottoagente nuovo ha respinto 3 falsi e declassato il quarto (il codice fa il contrario del gap, ma il job non risulta avviato), nessun gap vero respinto, uno vero declassato a «ipotesi» con un motivo verificabile (Sentry non risulta caricato), e ha segnalato due difetti veri non presenti nell'elenco.

## [1.2.1] - 2026-11-01
### Cambiato
- `check_delivery.py` e `checklist.py` allineati ad appsec-sentinel (controllo dei problemi annotati nella checklist e dei punti pericolosi per categoria; non si applicano alla matrice A–N).

## [1.2.0] - 2026-11-01
### Aggiunto (dopo due giri reali sul gestionale B: 39 cause, 18 in comune, accordo 46%)
- **Smentita indipendente**: un «secondo passaggio» nella stessa conversazione non vale più come verificatore; serve una sessione nuova, un altro agente o una persona.
- **Smentita nel `doppio`**: `scripts/apply_refutations.py` (condiviso con appsec-sentinel) applica ai gap gli esiti di un verificatore indipendente: colonna `smentita` nella forma «esito | verificatore | tentativi», priorità o stato abbassati per i declassati, respinti in `gaps-respinti.csv`.
- Colonna `domande_minime` nella matrice A–N: le domande che ogni giro deve porsi per controllo, ricavate dai 21 gap visti da un solo giro (informativa raggiungibile senza login, export con dati di altre persone, URL con token nelle metriche, punteggi automatici sui lavoratori, contatti di emergenza come dati di terzi, cifratura dichiarata e reale, basi giuridiche diverse fra documenti). Misurato con una seconda coppia di giri: accordo 44% (prima 46%), finding con un corrispondente 66% (prima 67%); le differenze vengono soprattutto da come i giri dividono le cause. Per questo: regola «un gap = una causa» nella procedura `statica`; misurata con una terza coppia di giri: **accordo 63%** (prima 44–46%), finding con un corrispondente 83% (prima 66–67%), e `merge_audits` stampa anche la quota di finding con un corrispondente. Unione dei quattro giri: 52 cause distinte; un giro solo ne vede circa la metà.
- `check_delivery` non cerca le parole vietate nelle uscite degli script.
- `init_gdpr.py --help` stampa l'aiuto invece di creare una cartella «--help» (successo due volte in giri reali).
### Aggiunto (condiviso con appsec-sentinel)
- Report PDF con la sezione «Gap privacy» da `gaps.csv` e, dopo `doppio`, «Due giri indipendenti» da `unione-giri.json`.
- Tempi: `init_gdpr` registra l'inizio, `check_delivery` stampa la durata fino alla chiusura (pre-passaggio separato), `merge_audits` quella di ogni giro.

## [1.1.0] - 2026-10-30
### Aggiunto (primo giro reale sul banco privacy: 15/15 difetti noti in entrambi i giri)
- Due giri `doppio` indipendenti: entrambi 15/15 difetti noti, 6/6 prioritari, 0 falsi allarmi sulle esche; consegna senza errori; unione 23 cause, 16 in comune (70%; le differenze sono soprattutto di raggruppamento: B ha unito in un gap solo ciò che A ha diviso).
- Banco corretto dopo il giro: tre «falsi allarmi» erano difetti veri piantati senza volerlo (sessione ricavata dal solo id nel cookie, nessuna cancellazione dei soci cessati, esportazione incompleta), ora P13–P15; le esche contano solo se il gap afferma la cosa sbagliata.

### Aggiunto (ripetibilità e banco privacy, 31/10/2026)
- **Gap strutturati**: `gaps.csv` (un gap per riga: ID, controllo A–N, titolo, riferimenti `file:riga`, stato, priorità, rischio, norma, domanda, smentita), copiato da `init_gdpr.py` e verificato da `check_matrix.py --gaps`. Senza gap separati due giri non si potevano contare, unire né misurare.
- **Pre-passaggio deterministico** (`scripts/gdpr_prepass.py`, comando `prepass`): `draft_ropa`, `retention_check` e il nuovo `scripts/privacy_scan.py` (indizi nel codice per tracker, cookie, consenso, dati particolari, minori, geolocalizzazione, log con dati personali, diritti, marketing, documenti privacy) in ordine fisso; pre-compila solo l'evidenza tecnica della matrice. Due esecuzioni danno file identici.
- `check_matrix.py`: un controllo con il solo testo del modello o la sola evidenza automatica `[prepass]` è un errore (come le aree vuote di appsec-sentinel).
- **Unione di più giri** (`scripts/merge_audits.py`, condiviso con appsec-sentinel, ora legge e scrive `gaps.csv`) e comandi `doppio`/`double`, `unisci`/`merge`.
- **Banco di prova privacy** (`tests/bench-app/`): portale soci finto con informativa e 12 difetti noti (analytics e font di Google senza consenso, Sentry con dati personali e replay, Mailchimp, dati sanitari, GPS dei soci, cancellazione che disattiva soltanto, log e backup oltre i tempi dichiarati, consenso pre-spuntato, banner senza rifiuto, dati personali nei log) e 5 esche; `score_bench.py` legge `gaps.csv`.
- `draft_ropa.py` riconosce i fornitori anche dai sottodomini (`www.googletagmanager.com`, `us21.api.mailchimp.com`) e più servizi (Sentry, Hotjar, Clarity, Meta Pixel, YouTube, Brevo).

### Corretto
- `redact_check.py`: «pacchetto@versione» (es. `prisma@7.10.1`, negli output di npm audit) non è più segnalato come email; esclusi anche i sottodomini di `example.*`.
- `check_delivery` segna «da verificare» quando la validazione dei finding è stata eseguita senza il modulo `jsonschema` (controllo minimo).

### Aggiunto
- `scripts/canonicalize.py` (comando `normalizza`/`canonicalize`): riporta ai valori canonici italiani stati, severità, confidenza ed esiti scritti in inglese, senza toccare il testo libero; `chiudi` lo segnala. Alias inglesi anche per gli argomenti di `area` (`secrets`, `dependencies`). Limite dichiarato: i messaggi stampati dagli script e i nomi dei campi dei file macchina restano in italiano.
- Skill utilizzabile in inglese: alias inglesi di tutti i comandi (`quick`, `refute`, `close`…), sezione «Lingua / Language» (risposte, finding e report nella lingua dell'utente; valori canonici dei file macchina invariati), descrizione bilingue per l'attivazione da richieste in inglese, `docs/COMMAND-CARD.md`. Il PDF con `--lang en` mostra ora anche stati e confidenza in inglese. Limite dichiarato: istruzioni, reference e template restano scritti in italiano e l'agente li traduce al volo; i messaggi degli script restano in italiano.
- `scripts/i18n.py` e `--lang en` su `check_delivery` e `redact_check`; modelli in inglese `assets/questions-template.en.md` e `assets/richiesta-interessato-template.en.md` (rimando al «Garante» reso come autorità di controllo competente). Limite: gli altri script e `check_matrix` restano in italiano.
- `README.en.md`: guida breve in inglese (la skill resta in italiano, dichiarato).
- Struttura del repository verificata con `npx skills add <percorso> --list`.
- `scripts/draft_dpia.py`: bozza di scheda DPIA (art. 35) dalla mappa dei trattamenti, con indicatori di necessità; comando `bozza-dpia`. Precompila solo ciò che la mappa dice, non valuta il rischio residuo e non decide se la DPIA serve.
- `assets/richiesta-interessato-template.md`: scheda, controlli e testi di risposta per le richieste degli interessati (scadenze art. 12, proroga, rifiuto motivato); comando `richiesta-interessato`.
- Collaudo di `cookie_scan.py` con Chromium su una pagina locale (`tests/lab/cookie_lab.py`): rileva cookie, storage e terze parti e non scrive il valore del cookie. Il blocco è saltato e dichiarato se Playwright non c'è.
- `scripts/check_delivery.py` e comando `chiudi`: controllo di consegna in un solo passo (schema e revisore, smentite dei finding alti, matrice GDPR, redazione compresi i valori dei segreti dell'app con `--app`, parole vietate, copertura). Provato sugli audit prodotti da Codex e Antigravity.
- `docs/ALTRI-AGENTI.md`: dove installare la skill su altri agenti (Antigravity, Codex), esiti della prova su Windows (un giro, modalità rapido, app finta) e controlli da fare.
- Smentita dei gap: colonna facoltativa `smentita` in `gdpr-matrix.csv`, controllata da `check_matrix.py` (warning se un gap riscontrato o confermato non è stato confutato da un verificatore diverso dall'autore), `references/refutation-pass.md` e comando `smentita`.
- `docs/SCHEDA-COMANDI.md`: scheda dei comandi in una pagina, con il flusso in sei righe, richiamata dall'inizio del README e dalla sezione Comandi.
- Strumenti automatici: `cookie_scan.py` (browser pulito, prima del consenso), `draft_ropa.py` (bozza art. 30 e fornitori), `retention_check.py`, `redact_check.py`, `compare_audits.py`.
- PDF: opzioni `--sintetico`, `--lang en`, `--previous`, `--nis2`.
- `references/automation.md`, app di prova in `tests/` e `tests/run_checks.py` eseguito in CI.
- Report PDF: sezione «Matrici di copertura» con le tabelle complete (inventario, endpoint, controlli ASVS/NIST/ACN), non solo i conteggi.
- Report PDF con grafica rinnovata, coerente con quella dei repository: copertina a gradiente con scudo, indice con pagine, intestazione e «Pagina X di Y», riquadri di copertura, etichette colorate. Tema ambra per la privacy, teal per la sicurezza.
- Rimandi espliciti alla skill gemella `appsec-sentinel`: riquadro in testa al README, schema, comando `sicurezza`, regole di consegna in `SKILL.md`.
- Comandi `documentale` (audit documentale privacy) e `pdf`; reference `documentary-audit.md`, template `documentary-matrix.csv` e `meta-template.json`, script `build_report_pdf.py` (richiede `reportlab`), esempio anonimizzato con PDF. Il PDF supporta anche tabella delle domande per destinatario e piano da `meta.json` (report solo privacy).
- Comandi rapidi (`statica`, `informativa`, `cookie`, `retention`, `fornitori`, `domande`, `report`) definiti in `SKILL.md` e descritti nel README.
- Esempio anonimizzato di collaudo (`examples/collaudo-statico/`) e guida `docs/ESEMPI-DI-UTILIZZO.md`.
- Script `init_gdpr.py` per creare la cartella di lavoro dai template.
### Modificato
- Dopo le prove su Codex e Antigravity: nessun valore di segreto in nessun output (chat compresa); `verify_findings.py` nella chiusura; la smentita vale solo se fatta da un verificatore diverso (altrimenti `non eseguita`); smentita GDPR nella forma `esito | verificatore | tentativi`; CVSS da sola lettura statica solo dichiarando il limite; nota per Windows sul comando `python`; euristica sull'impatto «reale» meno severa.
- Dopo il primo collaudo su un caso reale: controlli D e G con confronto sistematico informativa ↔ codice (font, CDN, SDK, API di terzi, backup).

## [1.0.0] - 2026-10-29
### Aggiunto
- Valutazione tecnica GDPR/ePrivacy sul trattamento reale: controlli A–N, mappa dei trattamenti, matrice, domande per DPO/legale e script `check_matrix.py`.
- Controlli automatici su GitHub Actions e rilascio automatico del pacchetto `.skill` alla creazione di un tag `v*`.
- Modelli per issue e pull request, codice di condotta, `CITATION.cff`, immagine di anteprima.
- Licenza Apache-2.0, `NOTICE`, `THIRD_PARTY.md`, `SECURITY.md`, intestazioni SPDX negli script.
