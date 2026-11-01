<?php
function invia_mail(string $a, string $oggetto, string $testo, string $risposta_a = ''): bool {
    $ch = curl_init('https://api.mailgun.net/v3/mg.ic-esempio.edu.it/messages');
    curl_setopt_array($ch, [
        CURLOPT_USERPWD => 'api:' . getenv('MAILGUN_KEY'),
        CURLOPT_POSTFIELDS => ['from' => 'sito@ic-esempio.edu.it', 'to' => $a, 'subject' => $oggetto, 'text' => $testo, 'h:Reply-To' => $risposta_a],
        CURLOPT_RETURNTRANSFER => true,
    ]);
    $ok = curl_exec($ch) !== false;
    curl_close($ch);
    return $ok;
}
