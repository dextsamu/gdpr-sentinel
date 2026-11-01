# Command card · gdpr-sentinel (English)

Type the command after `/gdpr-sentinel` (or as the first word of your request). Every command works in English or Italian: the Italian word is in brackets. The skill never says "compliant" and is not legal advice: it prepares evidence, drafts and questions for the controller, DPO and counsel.
Reports and chat follow your language. Machine-readable files (`gdpr-matrix.csv`, `processing-map.csv`) keep canonical Italian field names and state values because the scripts check them.

## The flow in six lines
1. `static <repo>` (`statica`): real processing from the code and the A–N matrix.
2. `draft-register <repo>` (`bozza-registro`): draft Art. 30 register and suppliers (all "hypothesis to validate").
3. `notice`, `cookie`, `retention`, `suppliers`: comparison with what is declared; for cookies, a scan before consent.
4. `questions` (`domande`): ready questions for the controller, DPO, counsel and suppliers.
5. `close` then `pdf`: delivery check (secrets, refutations, forbidden words), then the report.
6. `compare <old> <new>` after the fixes.

## Analysis
| Command | What it does | Limit |
|---|---|---|
| `static <repo>` | Processing map and A–N matrix from the code | Only what the code shows |
| `draft-register <repo>` | Draft processing map and suppliers | Roles, legal bases and countries are confirmed by the controller |
| `draft-dpia <processing-map.csv>` (`bozza-dpia`) | Draft DPIA sheets with need indicators | Not a DPIA; the controller decides with the DPO |
| `data-subject-request` (`richiesta-interessato`) | Sheet, checks and reply texts for a rights request (Italian template, translate and have it reviewed by counsel) | Not legal advice |
| `notice <repo>` (`informativa`) | Privacy notice versus code | Flags gaps, does not judge |
| `cookie <repo> [url…]` | Cookies, storage and third-party requests before consent, clean browser | Local URLs or with the controller's written confirmation; indicative classification |
| `retention <repo>` | Control G, backups included; deletion and anonymization evidence against declared times | Absence of evidence is not a violation |
| `suppliers <repo>` (`fornitori`) | Third-party services and possible transfers | The DPA and the country must be asked of the controller |
| `documentary <repo>` (`documentale`) | Compares privacy documents with code | States: consistent, inconsistent, obsolete, duplicate, missing |
| `security <repo>` (`sicurezza`) | Hands over to `appsec-sentinel` for findings that affect data (Art. 32) | Needs the sister skill |

## Verify and deliver
| Command | What it does |
|---|---|
| `questions [folder]` | List of questions with recipient and material needed |
| `report [folder]` | Checks the matrix (`check_matrix.py`) and produces the report |
| `close [folder]` (`chiudi`) | Delivery check in one step; zero "FAIL" before delivering |
| `refute [folder]` (`smentita`) | A verifier other than the author tries to refute every found or confirmed gap |
| `redact [folder]` (`redazione`) | Looks for secrets and personal data in files and the PDF; never prints values |
| `pdf [folder]` | Corporate PDF report. Options: `--sintetico`, `--lang en`, `--previous`, `--nis2` |
| `canonicalize [folder]` (`normalizza`) | Converts English states and outcomes to the canonical Italian values the scripts check; free text untouched. `close` tells you when it is needed |
| `compare <old> <new>` (`confronta`) | Differences between two audits. "Resolved" is not "verified" |

## Remember
- Four states: *found* (`riscontrato`) · *confirmed from code/config* (`confermato da codice/config`) · *hypothesis* (`ipotesi`) · *not verifiable* (`non verificabile`). Never "compliant".
- The code shows what the software can process, not who the controller is nor the legal basis.
- Working files and reports are confidential: keep them out of Git and public repositories.
