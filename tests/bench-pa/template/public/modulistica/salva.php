<?php
require __DIR__ . '/../../lib/db.php';
require __DIR__ . '/../../lib/mail.php';
$nome_file = time() . '_' . basename($_FILES['documento']['name']);
move_uploaded_file($_FILES['documento']['tmp_name'], __DIR__ . '/../documenti/' . $nome_file);
$campi = ['alunno_nome', 'alunno_cognome', 'alunno_cf', 'alunno_nascita', 'classe_richiesta', 'allergie_intolleranze',
          'certificazione_disabilita', 'diagnosi_funzionale', 'genitore_nome', 'genitore_email', 'genitore_telefono', 'consenso_unico'];
$valori = array_map(fn($c) => $_POST[$c] ?? null, $campi);
$sql = "INSERT INTO iscrizioni (" . implode(',', $campi) . ", documento_identita) VALUES (" . str_repeat('?,', count($campi)) . "?)";
db()->prepare($sql)->execute([...$valori, '/documenti/' . $nome_file]);
invia_mail($_POST['genitore_email'], 'Domanda ricevuta', 'Abbiamo ricevuto la domanda di iscrizione di ' . $_POST['alunno_nome'] . '.');
header('Location: /modulistica/iscrizione.php?inviata=1');
