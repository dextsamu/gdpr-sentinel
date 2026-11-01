<?php
require __DIR__ . '/../../lib/db.php';
if (($_SESSION['ruolo'] ?? '') !== 'segreteria') { http_response_code(403); exit; }
$tipo = $_POST['tipo'];
$testo = $_POST['testo'];
if ($tipo === 'contributo_disabilita') {
    $testo = "Si dispone l'erogazione del contributo per l'assistenza all'alunno " . $_POST['alunno'] . " (classe " . $_POST['classe']
           . "), con certificazione ai sensi della L. 104/1992, diagnosi: " . $_POST['diagnosi'] . ". Importo: euro " . $_POST['importo'] . ".";
}
db()->prepare("INSERT INTO albo (numero, oggetto, testo, allegato, pubblicato_dal, pubblicato_al) VALUES (?, ?, ?, ?, CURDATE(), CURDATE() + INTERVAL 15 DAY)")
    ->execute([$_POST['numero'], $_POST['oggetto'], $testo, $_POST['allegato'] ?? null]);
header('Location: /albo/elenco.php');
