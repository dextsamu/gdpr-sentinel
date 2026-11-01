<?php $titolo = 'Personale'; require __DIR__ . '/../includes/header.php'; require __DIR__ . '/../../lib/db.php';
$p = db()->query("SELECT nome, cognome, ruolo, email_istituzionale, codice_fiscale, indirizzo_residenza, telefono_personale, cv_file FROM personale ORDER BY cognome")->fetchAll(); ?>
<h1>Amministrazione trasparente — Personale</h1>
<table><tr><th>Nome</th><th>Ruolo</th><th>Email</th><th>Codice fiscale</th><th>Residenza</th><th>Telefono</th><th>CV</th></tr>
<?php foreach ($p as $r): ?>
<tr><td><?= htmlspecialchars($r['nome'] . ' ' . $r['cognome']) ?></td><td><?= htmlspecialchars($r['ruolo']) ?></td><td><?= htmlspecialchars($r['email_istituzionale']) ?></td>
<td><?= htmlspecialchars($r['codice_fiscale']) ?></td><td><?= htmlspecialchars($r['indirizzo_residenza']) ?></td><td><?= htmlspecialchars($r['telefono_personale']) ?></td>
<td><a href="/cv/<?= htmlspecialchars($r['cv_file']) ?>">CV</a></td></tr>
<?php endforeach; ?></table>
<?php require __DIR__ . '/../includes/footer.php'; ?>
