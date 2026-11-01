<?php require __DIR__ . '/../includes/header.php'; require __DIR__ . '/../../lib/db.php';
$s = db()->prepare("SELECT * FROM albo WHERE id = ?"); $s->execute([(int)($_GET['id'] ?? 0)]); $a = $s->fetch(); ?>
<h1><?= htmlspecialchars($a['oggetto']) ?></h1>
<div><?= $a['testo'] ?></div>
<?php if ($a['allegato']): ?><a href="/albo/allegati/<?= htmlspecialchars($a['allegato']) ?>">Allegato</a><?php endif; ?>
<?php require __DIR__ . '/../includes/footer.php'; ?>
