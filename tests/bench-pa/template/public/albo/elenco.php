<?php $titolo = 'Albo online'; require __DIR__ . '/../includes/header.php'; require __DIR__ . '/../../lib/db.php';
$atti = db()->query("SELECT id, numero, oggetto, pubblicato_dal FROM albo ORDER BY pubblicato_dal DESC")->fetchAll(); ?>
<h1>Albo online</h1>
<table><?php foreach ($atti as $a): ?>
  <tr><td><?= htmlspecialchars($a['numero']) ?></td><td><a href="/albo/atto.php?id=<?= (int)$a['id'] ?>"><?= htmlspecialchars($a['oggetto']) ?></a></td><td><?= $a['pubblicato_dal'] ?></td></tr>
<?php endforeach; ?></table>
<?php require __DIR__ . '/../includes/footer.php'; ?>
