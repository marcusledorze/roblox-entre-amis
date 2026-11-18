"""Tests de la roadmap locale : py -m unittest discover -s roadmap-app/tests -v"""
from __future__ import annotations

import http.client
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["ROADMAP_QUIET"] = "1"

import export_html  # noqa: E402
import export_md  # noqa: E402
import roadmap  # noqa: E402
import seed  # noqa: E402
from server import make_server  # noqa: E402
from store import Store, ValidationError  # noqa: E402


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "roadmap.json")
        self.store = Store(self.path)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_user_card_is_pending_claude_card_is_not(self):
        u = self.store.create({"title": "Idée", "actor": "user"})
        c = self.store.create({"title": "Fait", "actor": "claude", "column": "done"})
        self.assertTrue(u["pending"])
        self.assertEqual(u["column"], "ideas")
        self.assertFalse(c["pending"])
        self.assertEqual([x["id"] for x in self.store.queue()], [u["id"]])

    def test_user_update_marks_pending_and_resolve_clears(self):
        c = self.store.create({"title": "A", "actor": "claude", "column": "p1"})
        self.store.update(c["id"], {"column": "done", "actor": "user"})
        card = self.store.get(c["id"])
        self.assertTrue(card["pending"])
        self.assertIn("p1 → done", card["pendingReason"])
        self.store.resolve(c["id"], "Vérifié dans Studio")
        card = self.store.get(c["id"])
        self.assertFalse(card["pending"])
        self.assertEqual(card["notes"][-1]["text"], "Vérifié dans Studio")

    def test_reorder_only_is_not_pending(self):
        a = self.store.create({"title": "A", "actor": "claude", "column": "p2"})
        b = self.store.create({"title": "B", "actor": "claude", "column": "p2"})
        self.store.update(b["id"], {"column": "p2", "position": 0, "actor": "user"})
        self.assertEqual(self.store.get(b["id"])["position"], 0)
        self.assertEqual(self.store.get(a["id"])["position"], 1)
        self.assertFalse(self.store.get(b["id"])["pending"])

    def test_same_values_do_not_mark_pending(self):
        c = self.store.create({"title": "A", "actor": "claude", "description": "x"})
        self.store.update(c["id"], {"title": "A", "description": "x", "actor": "user"})
        self.assertFalse(self.store.get(c["id"])["pending"])

    def test_validation(self):
        bad = [
            {"title": ""},
            {"title": "x" * 141},
            {"title": "ok", "column": "nope"},
            {"title": "ok", "effort": "XL"},
            {"title": "ok", "risk": "énorme"},
            {"title": 5},
            {"title": "ok", "admin": True},
            {"title": "ok", "actor": "root"},
            {"title": "ok", "position": -1},
            {"title": "ok", "position": True},
        ]
        for payload in bad:
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                self.store.create(payload)
        self.assertEqual(self.store.snapshot()["cards"], [])

    def test_control_chars_stripped(self):
        c = self.store.create({"title": "A\x00B\x1b", "actor": "claude"})
        self.assertEqual(c["title"], "AB")

    def test_persistence_and_external_reload(self):
        c = self.store.create({"title": "Persiste", "actor": "claude"})
        other = Store(self.path)
        self.assertEqual(other.get(c["id"])["title"], "Persiste")
        other.resolve(c["id"], "note externe")
        # le premier Store voit la modification faite par un autre processus
        self.assertEqual(self.store.snapshot()["cards"][0]["notes"][-1]["text"], "note externe")

    def test_delete_and_missing(self):
        c = self.store.create({"title": "X", "actor": "claude"})
        self.store.delete(c["id"])
        with self.assertRaises(KeyError):
            self.store.update(c["id"], {"title": "Y"})


class SeedTests(unittest.TestCase):
    def test_seed_builds_all_columns_without_pending(self):
        d = tempfile.mkdtemp()
        try:
            s = seed.build(os.path.join(d, "r.json"))
            cols = {c["column"] for c in s.data["cards"]}
            self.assertEqual(cols, {"done", "rc", "p1", "p2"})
            self.assertEqual(len(s.queue()), 0)
            self.assertEqual(len(s.data["cards"]), len(seed.DONE) + len(seed.RC) + len(seed.P1) + len(seed.P2))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_committed_data_file_is_valid(self):
        path = os.path.join(ROOT, "data", "roadmap.json")
        if not os.path.exists(path):
            self.skipTest("pas de fichier de données")
        snap = Store(path).snapshot()
        ids = [c["id"] for c in snap["cards"]]
        self.assertEqual(len(ids), len(set(ids)))
        for c in snap["cards"]:
            self.assertIn(c["column"], {col["id"] for col in snap["columns"]})


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.data = os.path.join(cls.dir, "roadmap.json")
        cls.httpd = make_server(0, cls.data)
        cls.port = cls.httpd.server_address[1]
        # le port réel n'est connu qu'après bind : on reconstruit le handler avec ce port
        from server import make_handler
        cls.httpd.RequestHandlerClass = make_handler(Store(cls.data), cls.port)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def req(self, method, path, body=None, headers=None, raw=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        h = {"Host": f"127.0.0.1:{self.port}"}
        if body is not None:
            raw = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        conn.request(method, path, body=raw, headers=h)
        r = conn.getresponse()
        data = r.read()
        conn.close()
        ctype = r.getheader("Content-Type", "")
        return r.status, (json.loads(data) if "json" in ctype else data), r

    def test_static_and_security_headers(self):
        status, body, r = self.req("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"STEAL A CRYSTAL!", body)
        self.assertIn("default-src 'self'", r.getheader("Content-Security-Policy"))
        self.assertEqual(r.getheader("X-Frame-Options"), "DENY")
        for path in ("/app.js", "/style.css"):
            self.assertEqual(self.req("GET", path)[0], 200)

    def test_path_traversal_and_unknown_files(self):
        for path in ("/../store.py", "/static/../server.py", "/data/roadmap.json", "/%2e%2e/server.py", "/server.py"):
            with self.subTest(path=path):
                self.assertEqual(self.req("GET", path)[0], 404)

    def test_crud_flow(self):
        status, card, _ = self.req("POST", "/api/cards", {"title": "Daily rewards", "column": "p2", "actor": "user"})
        self.assertEqual(status, 201)
        self.assertTrue(card["pending"])
        status, q, _ = self.req("GET", "/api/queue")
        self.assertIn(card["id"], [c["id"] for c in q["cards"]])
        status, upd, _ = self.req("PATCH", f"/api/cards/{card['id']}", {"effort": "S", "actor": "user"})
        self.assertEqual((status, upd["effort"]), (200, "S"))
        status, res, _ = self.req("POST", f"/api/cards/{card['id']}/resolve", {"note": "Planifié", "column": "doing"})
        self.assertEqual((status, res["pending"], res["column"]), (200, False, "doing"))
        status, board, _ = self.req("GET", "/api/board")
        self.assertEqual(len(board["columns"]), 6)
        self.assertEqual(self.req("DELETE", f"/api/cards/{card['id']}")[0], 200)
        self.assertEqual(self.req("PATCH", f"/api/cards/{card['id']}", {"title": "x"})[0], 404)

    def test_bad_requests(self):
        self.assertEqual(self.req("POST", "/api/cards", {"title": ""})[0], 400)
        self.assertEqual(self.req("POST", "/api/cards", raw=b"{nope", headers={"Content-Type": "application/json"})[0], 400)
        self.assertEqual(self.req("POST", "/api/cards", raw=b'{"title":"x"}', headers={"Content-Type": "text/plain"})[0], 400)
        big = {"title": "x", "description": "y" * (70 * 1024)}
        self.assertEqual(self.req("POST", "/api/cards", big)[0], 400)
        self.assertEqual(self.req("PATCH", "/api/cards/<script>", {"title": "x"})[0], 404)

    def test_dns_rebinding_host_refused(self):
        status, _, _ = self.req("GET", "/api/board", headers={"Host": "evil.example:80"})
        self.assertEqual(status, 421)

    def test_cross_origin_writes_refused(self):
        status, _, _ = self.req("POST", "/api/cards", {"title": "csrf"}, headers={"Origin": "https://evil.example"})
        self.assertEqual(status, 403)
        status, _, _ = self.req("POST", "/api/cards", {"title": "csrf"}, headers={"Sec-Fetch-Site": "cross-site"})
        self.assertEqual(status, 403)
        status, _, _ = self.req("POST", "/api/cards", {"title": "same", "actor": "claude"},
                                headers={"Origin": f"http://127.0.0.1:{self.port}", "Sec-Fetch-Site": "same-origin"})
        self.assertEqual(status, 201)

    def test_cli_uses_running_server(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            roadmap.main(["--port", str(self.port), "add", "Depuis la CLI", "--column", "p1", "--effort", "S"])
        self.assertIn("Depuis la CLI", buf.getvalue())
        status, board, _ = self.req("GET", "/api/board")
        card = next(c for c in board["cards"] if c["title"] == "Depuis la CLI")
        self.assertFalse(card["pending"])  # action signée claude
        self.assertEqual(card["createdBy"], "claude")


class CliOfflineTests(unittest.TestCase):
    def test_cli_falls_back_to_file(self):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "r.json")
            s = Store(path)
            c = s.create({"title": "Idée hors ligne", "actor": "user"})
            buf = io.StringIO()
            with redirect_stdout(buf):
                roadmap.main(["--port", "1", "--data", path, "queue"])
                roadmap.main(["--port", "1", "--data", path, "resolve", c["id"], "Fait", "--column", "done"])
            self.assertIn("1 carte(s) à traiter", buf.getvalue())
            card = Store(path).get(c["id"])
            self.assertEqual((card["pending"], card["column"]), (False, "done"))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "r.json")
        self.readme = os.path.join(self.dir, "README.md")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def export(self):
        with redirect_stdout(io.StringIO()):
            roadmap.main(["--port", "1", "--data", self.path, "export", "--readme", self.readme,
                          "--page", os.path.join(self.dir, "page.html")])
        with open(self.readme, encoding="utf-8") as f:
            return f.read()

    def page(self):
        with open(os.path.join(self.dir, "page.html"), encoding="utf-8") as f:
            return f.read()

    def test_html_page_embeds_data_safely(self):
        s = Store(self.path)
        evil = "</script><script>alert(1)</script> & <img src=x onerror=alert(2)>"
        c = s.create({"title": evil, "column": "rc", "actor": "user", "security": "a b"})
        s.resolve(c["id"], "note 1")
        s.resolve(c["id"], "note 2")
        self.export()
        html = self.page()
        self.assertNotIn("__ROADMAP_DATA__", html)
        self.assertNotIn("<script>alert", html)
        self.assertNotIn("<img src=x", html)
        self.assertEqual(html.count("</script>"), 2)  # seulement les 2 balises du modèle
        start = html.index('id="roadmap-data">') + len('id="roadmap-data">')
        payload = json.loads(html[start:html.index("</script>", start)])
        card = payload["board"]["cards"][0]
        self.assertEqual(card["title"], evil)  # le texte reste intact une fois décodé
        self.assertEqual(card["notes"], [{"text": "note 2"}])  # seule la dernière note
        self.assertNotIn("history", card)

    def test_template_placeholder_required(self):
        with self.assertRaises(ValueError):
            export_html.render({"columns": [], "cards": []}, "<p>pas de marqueur</p>")

    def test_export_injects_block_and_keeps_rest(self):
        s = Store(self.path)
        s.create({"title": "Daily rewards", "column": "p2", "effort": "S", "security": "heure serveur", "actor": "user"})
        done = s.create({"title": "Tutoriel", "column": "done", "actor": "claude"})
        s.resolve(done["id"], "Vérifié en jeu")
        with open(self.readme, "w", encoding="utf-8") as f:
            f.write("# Titre\n\nIntro\n\n" + export_md.START + "\nancien\n" + export_md.END + "\n\nFin\n")
        text = self.export()
        self.assertTrue(text.startswith("# Titre\n\nIntro\n"))
        self.assertTrue(text.rstrip().endswith("Fin"))
        self.assertNotIn("ancien", text)
        self.assertIn("- [ ] **Daily rewards**", text)
        self.assertIn("⚠️ à traiter", text)
        self.assertIn("🔒 heure serveur", text)
        self.assertIn("- [x] **Tutoriel**", text)
        self.assertIn("📝 Vérifié en jeu", text)
        # idempotent : un 2e export ne duplique pas le bloc
        self.assertEqual(self.export().count(export_md.START), 1)

    def test_export_escapes_markdown_and_html(self):
        s = Store(self.path)
        s.create({"title": "<script>alert(1)</script> [lien](http://x) | ## titre", "actor": "claude",
                  "description": "ligne1\nligne2 ![img](x)"})
        text = self.export()
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertNotIn("[lien](", text)
        self.assertNotIn("![img](", text)
        self.assertIn("ligne1 ligne2", text)

    def test_export_without_readme_creates_it(self):
        Store(self.path).create({"title": "X", "actor": "claude"})
        text = self.export()
        self.assertTrue(text.startswith(export_md.START))
        self.assertIn(export_md.END, text)


if __name__ == "__main__":
    unittest.main()
