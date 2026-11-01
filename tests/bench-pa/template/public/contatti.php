<?php $titolo = 'Contatti'; require __DIR__ . '/includes/header.php'; ?>
<h1>Contatti</h1>
<p>Segreteria: segreteria@ic-esempio.edu.it · 06 0000000</p>
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2970!2d12.49!3d41.89" width="600" height="300" loading="lazy"></iframe>
<form method="post" action="/contatti_invia.php">
  <input name="nome" required> <input name="email" type="email" required>
  <textarea name="messaggio" required></textarea>
  <input type="hidden" name="g-recaptcha-response" id="g">
  <button>Invia</button>
</form>
<?php require __DIR__ . '/includes/footer.php'; ?>
