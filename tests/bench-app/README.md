# Banco di prova privacy

Un portale soci finto («Associazione Esempio ODV») con informativa (`public/privacy.md`) e codice che in **15 punti** la contraddice o tratta dati senza le tutele attese, più **5 esche** (cookie tecnico, font locale, retention dei tentativi di login implementata, coordinate della sede, esportazione dei dati funzionante). I difetti sono del tipo più frequente nelle verifiche reali: informativa ↔ codice (analytics, font di Google, Sentry, Mailchimp, dati sanitari, geolocalizzazione, cancellazione, retention di log e backup, consenso pre-spuntato, banner senza rifiuto, dati personali nei log).

```bash
python3 tests/bench-app/score_bench.py prepare ~/prova
cd ~/prova/bench-app && <agente>: /gdpr-sentinel statica .     # cartella di lavoro FUORI dall'app
python3 tests/bench-app/score_bench.py score ~/prova/gdpr-A [~/prova/gdpr-B]
```
Il punteggio legge `gaps.csv`: difetti trovati su 15, prioritari su 6, falsi allarmi sulle esche, gap fuori elenco da valutare a mano, e con più giri la tabella difetto × giro.

Limiti: verità scritta da noi, riconoscimento meccanico (file citato + parole chiave); la valutazione giuridica (basi, bilanciamenti, applicabilità) non è misurata: conta che il gap sia trovato e ancorato al codice.
