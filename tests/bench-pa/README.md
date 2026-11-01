# Secondo banco privacy: sito di un istituto comprensivo

Il sito istituzionale finto di una scuola pubblica («Istituto Comprensivo Esempio»), in **PHP + MariaDB**: notizie, albo online, amministrazione trasparente, modulistica per le iscrizioni, galleria, contatti, con informativa in `public/privacy.html`. **15 difetti** e **5 esche**. Cambia rispetto al primo banco (`tests/bench-app`, portale soci in Next.js) il linguaggio, il tipo di titolare e i temi: dati sanitari di minori nella modulistica e all'albo, pubblicazione oltre il periodo di legge, dati eccedenti in amministrazione trasparente, consenso unico pre-spuntato per le foto, documenti d'identità in una cartella pubblica, servizi di terze parti incorporati (YouTube, Maps, reCAPTCHA, Google Fonts), Mailgun negli USA, informativa senza RPD. Le esche: Matomo senza cookie sul server della scuola, video degli eventi caricato solo al clic, compensi pubblicati per obbligo di legge, IP del limitatore cancellati dopo 7 giorni, cookie di sessione PHP.

```bash
python3 tests/bench-pa/score_bench.py prepare ~/prova
cd ~/prova/bench-app && <agente>: /gdpr-sentinel statica .     # cartella di lavoro FUORI dall'app
python3 tests/bench-pa/score_bench.py score ~/prova/gdpr-A [~/prova/gdpr-B]
```

Stesso punteggio del primo banco (lo script è quello di `tests/bench-app`). Limiti: verità scritta da noi, app piccola (22 file) e con difetti evidenti; misura se la skill generalizza a un altro linguaggio e a un ente pubblico, non la sua resa su un sito reale grande.
