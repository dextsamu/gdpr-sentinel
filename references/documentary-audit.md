<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Samuele Cucurnia e Pietro Previtali -->
# Audit documentale privacy

Obiettivo: verificare che i **documenti privacy** (informativa, registro, DPIA, DPA, procedure) esistano, siano datati e riesaminati, e che **dicano ciò che il sistema fa davvero**. È il corrispettivo documentale dei controlli D, G, I, J, K, L.

## Metodo
1. **Inventaria** i documenti: informativa e termini (pagine pubbliche e testi nel codice), registro dei trattamenti, DPIA, DPA e contratti con i fornitori, procedura di violazione dei dati, politiche di retention, accordi (per esempio sul controllo dei lavoratori), moduli di consenso, guide ai backup. Per ognuno: percorso, data o versione, autore, argomento. Dichiara quanti ne hai letti per intero, in parte, non letti.
2. **Confronta con il trattamento reale**: destinatari e paesi dichiarati contro fornitori e chiamate nel codice (font, CDN, SDK, API di terzi, email, messaggistica, backup); tempi di conservazione dichiarati contro i job di cancellazione; categorie di dati dichiarate contro il modello dati; dichiarazioni assolute («nessun trasferimento extra-SEE», «solo server UE») contro ogni fornitore trovato.
3. **Cerca i documenti attesi** e segna quelli mancanti: informativa, registro (art. 30, se dovuto), DPIA (se pertinente), nomina dei responsabili (art. 28), procedura di violazione (artt. 33-34), prova di esercizio dei diritti. L'assenza di un documento è un rilievo, non una violazione certa: dipende da presupposti e scala (`controls.md`).
4. **Registra** in `documentary-matrix.csv` (id, documento, tipo, data_o_versione, cosa_afferma, evidenza_nel_codice, stato, rilievo, azione_proposta). Stati: coerente · incoerente · obsoleto · duplicato · mancante · non verificabile.
5. **Domande**: ogni «non verificabile» e ogni «incoerente» ha la sua domanda per titolare, DPO, legale o fornitore (`questions-template.md`).

## Limiti
Nessun giudizio di conformità: un documento coerente col codice non prova la conformità, un documento mancante non prova una violazione. Le norme e le decisioni (adeguatezza, DPF) vanno riverificate alla fonte, ora.

## PDF
`python3 scripts/build_report_pdf.py <cartella>` assembla un PDF A4 aziendale con copertina, sintesi, matrice A–N, mappa dei trattamenti, audit documentale, domande e limiti. Usa `meta.json` (modello in `assets/meta-template.json`). Rileggi il PDF prima di consegnarlo: niente dati personali veri, niente segreti, niente «conforme» o «non conforme».
