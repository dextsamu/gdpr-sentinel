<?php $titolo = 'Galleria'; require __DIR__ . '/includes/header.php'; require __DIR__ . '/../lib/db.php';
$foto = db()->query("SELECT file, alunno_nome, classe, evento FROM galleria ORDER BY id DESC")->fetchAll(); ?>
<h1>Galleria</h1>
<?php foreach ($foto as $f): ?>
  <figure><img src="/foto/<?= htmlspecialchars($f['file']) ?>" alt="<?= htmlspecialchars($f['alunno_nome']) ?>">
  <figcaption><?= htmlspecialchars($f['alunno_nome'] . ', classe ' . $f['classe'] . ' — ' . $f['evento']) ?></figcaption></figure>
<?php endforeach; require __DIR__ . '/includes/footer.php'; ?>
