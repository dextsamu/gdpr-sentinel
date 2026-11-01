<?php $titolo = 'Iscrizioni'; require __DIR__ . '/../includes/header.php'; ?>
<h1>Domanda di iscrizione</h1>
<form method="post" action="/modulistica/salva.php" enctype="multipart/form-data">
  <fieldset><legend>Alunno</legend>
    <input name="alunno_nome" required> <input name="alunno_cognome" required>
    <input name="alunno_cf" required maxlength="16"> <input name="alunno_nascita" type="date" required>
    <select name="classe_richiesta"><option>1A</option><option>1B</option></select>
    <label>Allergie o intolleranze alimentari <textarea name="allergie_intolleranze"></textarea></label>
    <label><input type="checkbox" name="certificazione_disabilita" value="1"> L'alunno ha una certificazione ai sensi della L. 104/1992</label>
    <label>Diagnosi funzionale (sintesi) <textarea name="diagnosi_funzionale"></textarea></label>
  </fieldset>
  <fieldset><legend>Genitore</legend>
    <input name="genitore_nome" required> <input name="genitore_email" type="email" required> <input name="genitore_telefono" required>
    <label>Documento d'identità (PDF o JPG) <input type="file" name="documento" required></label>
  </fieldset>
  <label><input type="checkbox" name="consenso_unico" value="1" checked required>
    Dichiaro di aver letto l'informativa e acconsento al trattamento dei dati, alla pubblicazione di foto e video dell'alunno sul sito e sui social della scuola e all'invio di comunicazioni.</label>
  <button>Invia la domanda</button>
</form>
<?php require __DIR__ . '/../includes/footer.php'; ?>
