<?php session_start(); ?>
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title><?= htmlspecialchars($titolo ?? 'Istituto Comprensivo Esempio') ?></title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;700&display=swap">
  <link rel="stylesheet" href="/assets/stile.css">
  <script src="https://www.google.com/recaptcha/api.js?render=6LdEsempioChiavePubblica000000000000000"></script>
</head>
<body>
<header><a href="/">Istituto Comprensivo Esempio</a>
  <nav><a href="/albo/elenco.php">Albo online</a> <a href="/trasparenza/personale.php">Amministrazione trasparente</a>
  <a href="/modulistica/iscrizione.php">Iscrizioni</a> <a href="/eventi.php">Eventi</a> <a href="/galleria.php">Galleria</a>
  <a href="/contatti.php">Contatti</a> <a href="/privacy.html">Privacy</a></nav>
</header>
<main>
