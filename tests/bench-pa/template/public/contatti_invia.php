<?php
require __DIR__ . '/../lib/db.php';
require __DIR__ . '/../lib/mail.php';
$ip = $_SERVER['REMOTE_ADDR'];
$pdo = db();
$n = $pdo->prepare("SELECT COUNT(*) FROM tentativi_modulo WHERE ip = ? AND creato_il > NOW() - INTERVAL 1 HOUR");
$n->execute([$ip]);
if ($n->fetchColumn() > 5) { http_response_code(429); exit('Troppi invii, riprova più tardi.'); }
$pdo->prepare("INSERT INTO tentativi_modulo (ip) VALUES (?)")->execute([$ip]);

$nome = trim($_POST['nome'] ?? ''); $email = trim($_POST['email'] ?? ''); $msg = trim($_POST['messaggio'] ?? '');
$pdo->prepare("INSERT INTO contatti (nome, email, messaggio) VALUES (?, ?, ?)")->execute([$nome, $email, $msg]);
file_put_contents(__DIR__ . '/registro/contatti.log', date('c') . " $ip $nome <$email> " . str_replace("\n", ' ', $msg) . "\n", FILE_APPEND);
invia_mail('segreteria@ic-esempio.edu.it', 'Messaggio dal sito', $msg, $email);
header('Location: /contatti.php?inviato=1');
