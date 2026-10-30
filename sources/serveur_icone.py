"""Serveur local : sert le dossier de travail et enregistre les PNG envoyés en POST /save/<nom>.png."""
import functools, http.server, os, re, sys

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.join(ROOT, "icones")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8766


class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        name = self.path.split("?")[0].rsplit("/", 1)[-1]
        if not re.fullmatch(r"[a-z0-9_\-]+\.(png|webp)", name):
            self.send_response(400); self.end_headers(); return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")


http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(H, directory=ROOT)).serve_forever()
