<?php
require __DIR__ . '/../lib/db.php';
$pdo = db();
$pdo->exec("DELETE FROM contatti WHERE creato_il < NOW() - INTERVAL 12 MONTH");
$pdo->exec("DELETE FROM tentativi_modulo WHERE creato_il < NOW() - INTERVAL 7 DAY");
echo "pulizia completata\n";
