#!/usr/bin/env python3
"""LABORATORIO: pagina finta con tracciamento prima del consenso, per collaudare cookie_scan.py.
Solo 127.0.0.1. Imposta un cookie con valore riconoscibile, scrive in localStorage e chiede risorse a domini di terzi."""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = b"""<!doctype html><title>lab</title><h1>Pagina di prova</h1>
<script>localStorage.setItem('_ga_lab','1');</script>
<script src="https://www.google-analytics.com/analytics.js"></script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Set-Cookie", "_ga_lab=VALORE-SEGRETO-DI-PROVA-123; Max-Age=31536000; Path=/")
        self.end_headers(); self.wfile.write(PAGE)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
