<?php $titolo = 'Incarichi'; require __DIR__ . '/../includes/header.php'; require __DIR__ . '/../../lib/db.php';
$i = db()->query("SELECT nominativo, incarico, atto, compenso_lordo, anno FROM incarichi WHERE anno >= YEAR(CURDATE()) - 3 ORDER BY anno DESC")->fetchAll(); ?>
<h1>Amministrazione trasparente — Incarichi conferiti e compensi (art. 14 e 15 D.Lgs. 33/2013)</h1>
<table><?php foreach ($i as $r): ?>
<tr><td><?= htmlspecialchars($r['nominativo']) ?></td><td><?= htmlspecialchars($r['incarico']) ?></td><td><?= htmlspecialchars($r['atto']) ?></td><td><?= number_format((float)$r['compenso_lordo'], 2, ',', '.') ?></td><td><?= (int)$r['anno'] ?></td></tr>
<?php endforeach; ?></table>
<?php require __DIR__ . '/../includes/footer.php'; ?>
