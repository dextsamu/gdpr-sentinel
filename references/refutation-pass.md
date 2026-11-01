# Smentita dei gap

Un gap scritto da chi l'ha trovato sembra solido a chi l'ha scritto. Prima del report, ogni gap in stato «riscontrato» o «confermato da codice/config» passa da un verificatore **diverso dall'autore** che prova a dimostrare che è sbagliato o esagerato. Non si cerca conferma.

## Chi può farlo
Un secondo agente con lo stesso perimetro e gli stessi divieti, una sessione nuova (altra conversazione o altro agente) che riparte dal solo gap, o una persona; un secondo passaggio nella stessa conversazione non conta. Nessuno amplia il mandato. Se manca un verificatore indipendente, scrivi `non eseguita` e dichiaralo nel report.

## Cosa riceve il verificatore
Un brief per gap, scritto da `scripts/gap_briefs.py <cartella> --repo <repository>` in `smentite/smentita-<ID>.md`: l'affermazione, le righe di codice citate e le ipotesi di smentita pertinenti all'area. Non riceve la motivazione dell'autore, la matrice né le domande per il DPO. Sul banco privacy, con 4 gap falsi aggiunti apposta tra 9, il verificatore ne ha respinti 3 e declassato il quarto, senza respingere nessun gap vero.

## Cosa provare a smentire
1. Il trattamento esiste davvero in produzione, o è codice di prova, esempio, funzione disattivata?
2. Un'altra base giuridica, un accordo o un'informativa già lo coprono e il codice letto non lo mostra?
3. Il fornitore è davvero destinatario di dati personali, o riceve solo dati non identificativi?
4. Il tempo di conservazione dichiarato è comunque rispettato da un job o da una regola a monte?
5. Il rischio per gli interessati dipende da condizioni non verificate (dati presenti, categorie coinvolte, volumi)?
6. Lo stato dichiarato è quello raggiunto? Una lettura del codice non è un test.

## Chi non può farlo
Lo stesso agente che ha scritto il gap, nella stessa conversazione, non è un verificatore indipendente: riformulare l'evidenza non è un tentativo di confutarla. In quel caso scrivi `non eseguita` e dichiaralo. Le righe «non verificabile» o senza gap non richiedono smentita: non riempirle per far tacere il controllo.

## Esito
Scrivilo nella colonna `smentita` di `gdpr-matrix.csv` **solo per i gap** (righe con `gap` compilato in stato riscontrato o confermato), nella forma `esito | verificatore | tentativi`, per esempio `resiste | secondo agente in una sessione nuova, solo con il gap | cercato un DPA nei contratti e nel codice: nessuno`. L'esito è una di queste parole:
- `resiste`: nessuna smentita valida;
- `declassato`: cambia lo stato (per esempio in «ipotesi») e aggiorna il gap;
- `respinto`: il gap esce dal report;
- `non eseguita`: nessun verificatore indipendente.

Rilancia `check_matrix.py`. La smentita riduce i falsi positivi: non dimostra che il gap sia vero né sostituisce il parere di DPO o legale.

## Senza sottoagenti: pacchetto per una seconda sessione
Se nella tua sessione non puoi avviare un verificatore nuovo, non fermarti a «non eseguita»: proponi all'utente una seconda sessione (un'altra conversazione, un altro agente come Codex o Antigravity, un collega) e prepara il pacchetto con `scripts/refutation_pack.py prepara <cartella-audit> --repo <repository>`. Scrive in `smentite/pacchetto/` le istruzioni da incollare come primo messaggio (`ISTRUZIONI.md`), questo metodo e un brief per ogni gap ad alta priorità, senza le conclusioni dell'autore. Quando la seconda sessione ha scritto `esiti.json`, `scripts/refutation_pack.py importa <cartella-audit> <esiti.json>` li controlla e li applica. «non eseguita» resta solo se l'utente non può o non vuole aprire una seconda sessione.
