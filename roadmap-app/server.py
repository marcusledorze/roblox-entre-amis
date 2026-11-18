"""Serveur local de la roadmap STEAL A CRYSTAL! (Python standard, aucune dépendance).

Lancer :  py roadmap-app/server.py            (http://127.0.0.1:8787)
Options :  --port 8787  --data roadmap-app/data/roadmap.json

Sécurité : écoute seulement sur 127.0.0.1, refuse les en-têtes Host étrangers
(DNS rebinding), refuse les requêtes d'écriture venant d'une autre origine (CSRF),
exige du JSON, limite la taille des requêtes, ne sert que des fichiers statiques
connus.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from store import Store, ValidationError

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")
DEFAULT_DATA = os.path.join(HERE, "data", "roadmap.json")
MAX_BODY = 64 * 1024
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}
CARD_PATH = re.compile(r"^/api/cards/([0-9a-z_-]{1,64})$")
RESOLVE_PATH = re.compile(r"^/api/cards/([0-9a-z_-]{1,64})/resolve$")


def make_handler(store: Store, port: int):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    allowed_origins = {f"http://{h}" for h in allowed_hosts}

    class Handler(BaseHTTPRequestHandler):
        server_version = "RoadmapApp/1.0"
        sys_version = ""

        def log_message(self, fmt, *args):  # journal discret
            if os.environ.get("ROADMAP_QUIET"):
                return
            super().log_message(fmt, *args)

        # ---------- réponses ----------
        def _send(self, status: int, body: bytes, ctype: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
                "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
                "frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _json(self, status: int, payload) -> None:
            self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def _error(self, status: int, message: str) -> None:
            self._json(status, {"error": message})

        # ---------- garde-fous ----------
        def _host_ok(self) -> bool:
            return self.headers.get("Host", "") in allowed_hosts

        def _origin_ok(self) -> bool:
            origin = self.headers.get("Origin")
            if origin is not None and origin not in allowed_origins:
                return False
            site = self.headers.get("Sec-Fetch-Site")
            if site is not None and site not in ("same-origin", "none"):
                return False
            return True

        def _read_json(self):
            if not self.headers.get("Content-Type", "").lower().startswith("application/json"):
                raise ValidationError("Content-Type application/json obligatoire")
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise ValidationError("Content-Length invalide")
            if length < 0 or length > MAX_BODY:
                raise ValidationError("requête trop grosse")
            raw = self.rfile.read(length) if length else b"{}"
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValidationError("JSON invalide")

        # ---------- routage ----------
        def _dispatch(self, method: str) -> None:
            if not self._host_ok():
                return self._error(HTTPStatus.MISDIRECTED_REQUEST, "hôte refusé")
            path = urlparse(self.path).path
            if method in ("POST", "PATCH", "DELETE") and not self._origin_ok():
                return self._error(HTTPStatus.FORBIDDEN, "origine refusée")
            try:
                if method in ("GET", "HEAD"):
                    if path in STATIC_FILES:
                        name, ctype = STATIC_FILES[path]
                        with open(os.path.join(STATIC_DIR, name), "rb") as f:
                            return self._send(HTTPStatus.OK, f.read(), ctype)
                    if path == "/api/board":
                        return self._json(HTTPStatus.OK, store.snapshot())
                    if path == "/api/queue":
                        return self._json(HTTPStatus.OK, {"cards": store.queue()})
                    return self._error(HTTPStatus.NOT_FOUND, "introuvable")
                if method == "POST" and path == "/api/cards":
                    return self._json(HTTPStatus.CREATED, store.create(self._read_json()))
                m = RESOLVE_PATH.match(path)
                if method == "POST" and m:
                    body = self._read_json()
                    if not isinstance(body, dict):
                        raise ValidationError("objet JSON attendu")
                    return self._json(HTTPStatus.OK, store.resolve(m.group(1), body.get("note", ""), body.get("column")))
                m = CARD_PATH.match(path)
                if m and method == "PATCH":
                    return self._json(HTTPStatus.OK, store.update(m.group(1), self._read_json()))
                if m and method == "DELETE":
                    store.delete(m.group(1))
                    return self._json(HTTPStatus.OK, {"ok": True})
                return self._error(HTTPStatus.NOT_FOUND, "introuvable")
            except ValidationError as e:
                return self._error(HTTPStatus.BAD_REQUEST, str(e))
            except KeyError:
                return self._error(HTTPStatus.NOT_FOUND, "carte introuvable")

        def do_GET(self):
            self._dispatch("GET")

        def do_HEAD(self):
            self._dispatch("HEAD")

        def do_POST(self):
            self._dispatch("POST")

        def do_PATCH(self):
            self._dispatch("PATCH")

        def do_DELETE(self):
            self._dispatch("DELETE")

    return Handler


def make_server(port: int, data_path: str) -> ThreadingHTTPServer:
    store = Store(data_path)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(store, port))
    httpd.daemon_threads = True
    return httpd


def main() -> None:
    parser = argparse.ArgumentParser(description="Roadmap STEAL A CRYSTAL! (local)")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--data", default=DEFAULT_DATA)
    args = parser.parse_args()
    httpd = make_server(args.port, args.data)
    print(f"Roadmap : http://127.0.0.1:{args.port}  (données : {args.data})", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
