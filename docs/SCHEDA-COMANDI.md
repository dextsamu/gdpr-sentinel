# Scheda comandi · gdpr-sentinel

Scrivi il comando dopo `/gdpr-sentinel` (o come prima parola della richiesta). La skill non dichiara mai «conforme» e non è un parere legale: prepara prove, bozze e domande per titolare, DPO e legale.

## Il flusso in sei righe
1. `statica <repo>`: trattamenti reali dal codice e matrice A–N.
2. `bozza-registro <repo>`: bozza dell'art. 30 e dei fornitori (tutta «ipotesi da validare»).
3. `informativa`, `cookie`, `retention`, `fornitori`: confronto con quanto dichiarato; per i cookie, scansione prima del consenso.
4. `domande`: domande pronte per titolare, DPO, legale e fornitori.
5. `chiudi` poi `pdf`: controllo di consegna (segreti, smentite, parole vietate), quindi il report.
6. `confronta <vecchio> <nuovo>` dopo le correzioni.

## Analisi
| Comando | Che cosa fa | Limite |
|---|---|---|
| `statica <repo>` | Mappa dei trattamenti e matrice A–N dal codice | Solo ciò che il codice mostra |
| `bozza-registro <repo>` | Bozza di processing map e fornitori | Ruoli, basi giuridiche, paesi li conferma il titolare |
| `informativa <repo>` | Informativa contro codice | Segnala scostamenti, non giudica |
| `cookie <repo> [url…]` | Cookie, storage e richieste a terzi prima del consenso, browser pulito | URL locali o con conferma scritta del titolare; classificazione indicativa |
| `retention <repo>` | Controllo G, backup compresi; evidenze di cancellazione e anonimizzazione, confronto con i tempi dichiarati | L'assenza di evidenza non è una violazione |
| `fornitori <repo>` | Servizi di terzi e possibili trasferimenti | Il DPA e il paese vanno chiesti al titolare |
| `documentale <repo>` | Confronta i documenti privacy con il codice | Stati: coerente, incoerente, obsoleto, duplicato, mancante |
| `sicurezza <repo>` | Passa ad `appsec-sentinel` per i finding che incidono sui dati (art. 32) | Serve la skill gemella |

## Verifica e consegna
| Comando | Che cosa fa |
|---|---|
| `domande [cartella]` | Elenco di domande con destinatario e materiale necessario |
| `report [cartella]` | Controlla la matrice (`check_matrix.py`) e produce il rapporto |
| `chiudi [cartella]` | Controllo di consegna in un solo passo; zero «falliti» prima di consegnare |
| `smentita [cartella]` | Un verificatore diverso dall'autore prova a confutare ogni gap riscontrato o confermato |
| `redazione [cartella]` | Cerca segreti e dati personali nei file e nel PDF; non stampa mai i valori |
| `pdf [cartella]` | Report PDF aziendale. Opzioni: `--sintetico`, `--lang en`, `--previous`, `--nis2` |
| `confronta <vecchio> <nuovo>` | Differenze tra due audit. «Risolto» non è «verificato» |

## Da ricordare
- Quattro stati: riscontrato · confermato da codice o configurazione · ipotesi · non verificabile. Mai «conforme».
- Il codice mostra cosa il software può trattare, non chi è titolare né la base giuridica.
- I file di lavoro e i report sono riservati: fuori da Git e dai repository pubblici.

Dettagli: [README](../README.md) · [automazioni](../references/automation.md)
