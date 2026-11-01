# Strumenti automatici

Gli script preparano le prove e le bozze; **non stabiliscono la conformità**. Tutto ciò che ricavano dal codice è «ipotesi da validare» finché titolare, DPO o legale non confermano ruoli, basi giuridiche, paesi e tempi.


**Windows.** Gli esempi usano `python3`. Su Windows usa `python` o `py`; se l'alias del Microsoft Store non parte, installa Python 3 oppure usa l'interprete già disponibile nel tuo ambiente. Gli script usano solo la libreria standard (il PDF richiede `reportlab`).

## Flusso consigliato
1. `init_gdpr.py` crea la cartella di lavoro (riservata, fuori da Git).
2. `draft_ropa.py <repo> --out cartella`: `processing-map-bozza.csv` (modelli con dati personali, raggruppati per tipo, con possibile art. 9 segnalato) e `fornitori-bozza.csv` (servizi di terzi da dipendenze, variabili e URL). Ruoli, basi giuridiche, paesi e DPA restano «da verificare con il titolare». Il codice mostra cosa il software **può** trattare, non chi è titolare.
3. `retention_check.py <repo> [--declared retention.csv]`: job pianificati, cancellazioni con soglia, modelli con campi di data senza cancellazione evidente. L'assenza di evidenza non è una violazione: può esserci una procedura fuori dal codice.
4. `cookie_scan.py <url…>`: apre ogni URL in un browser pulito, senza cliccare nulla, e registra cookie (mai i valori), storage e domini di terzi **prima del consenso**. URL locali liberi; altri solo con `--autorizzato` e conferma scritta del titolare. Richiede `pip install playwright && playwright install chromium`. La classificazione dei domini è indicativa, non un parere sulla necessità del consenso.
5. `check_matrix.py` per la matrice A–N (segnala i gap senza `smentita`, vedi `refutation-pass.md`); `redact_check.py <cartella>` sui file e sul PDF prima di consegnare.
5b. Prima di consegnare: `check_delivery.py <cartella-audit> --app <repo>`: un solo passo che unisce i controlli meccanici. Zero «falliti»; i «da verificare» si risolvono o si dichiarano.
6. `build_report_pdf.py`: completo, `--sintetico`, `--lang en`, `--previous`, `--nis2` (se ci sono finding di sicurezza nella stessa cartella).
7. `compare_audits.py` per confrontare due audit.

## Collaudo degli script
`python3 tests/run_checks.py` prova gli script contro `tests/fixtures/vuln-app`. Aggiorna il test se modifichi uno script.
