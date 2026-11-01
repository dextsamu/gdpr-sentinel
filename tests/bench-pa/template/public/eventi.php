<?php $titolo = 'Eventi'; require __DIR__ . '/includes/header.php'; ?>
<h1>Eventi</h1>
<div class="video" data-src="https://www.youtube-nocookie.com/embed/kJiHgFeDcBa">
  <p>Il video è ospitato da YouTube. Cliccando su «Mostra il video» accetti il caricamento dei contenuti di YouTube.</p>
  <button onclick="var d=this.parentNode; d.innerHTML='<iframe width=560 height=315 src=&quot;'+d.dataset.src+'&quot; allowfullscreen></iframe>'">Mostra il video</button>
</div>
<?php require __DIR__ . '/includes/footer.php'; ?>
