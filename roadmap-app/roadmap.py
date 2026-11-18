"""Outil en ligne de commande pour Claude (et les humains) : lit et traite la roadmap.

  py roadmap-app/roadmap.py queue                       # cartes « à traiter »
  py roadmap-app/roadmap.py show <id>
  py roadmap-app/roadmap.py resolve <id> "note" [--column done]
  py roadmap-app/roadmap.py add "titre" --column p1 [--description ...] [--effort S] [--risk faible]
  py roadmap-app/roadmap.py move <id> <colonne>
  py roadmap-app/roadmap.py export                      # met à jour la roadmap du README.md (page GitHub)

Passe par le serveur local s'il tourne (pour que la page se mette à jour),
sinon écrit directement dans le fichier de données. Les actions faites ici
sont signées « claude » et ne remettent pas la carte en attente.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import COLUMN_IDS, Store  # noqa: E402
from server import DEFAULT_DATA  # noqa: E402
from export_md import board_markdown, inject  # noqa: E402

README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")


class Client:
    def __init__(self, port: int, data: str):
        self.base = f"http://127.0.0.1:{port}"
        self.data = data
        self.online = self._ping()
        self.store = None if self.online else Store(data)

    def _ping(self) -> bool:
        try:
            with urllib.request.urlopen(self.base + "/api/board", timeout=1.5) as r:
                return r.status == 200
        except (urllib.error.URLError, OSError):
            return False

    def _call(self, method: str, path: str, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = json.loads(e.read().decode("utf-8")).get("error", str(e))
            raise SystemExit(f"Erreur : {msg}")

    def board(self):
        return self._call("GET", "/api/board") if self.online else self.store.snapshot()

    def queue(self):
        return self._call("GET", "/api/queue")["cards"] if self.online else self.store.queue()

    def create(self, payload):
        payload = dict(payload, actor="claude")
        return self._call("POST", "/api/cards", payload) if self.online else self.store.create(payload)

    def update(self, cid, payload):
        payload = dict(payload, actor="claude")
        return self._call("PATCH", f"/api/cards/{cid}", payload) if self.online else self.store.update(cid, payload)

    def resolve(self, cid, note, column=None):
        if self.online:
            return self._call("POST", f"/api/cards/{cid}/resolve", {"note": note, "column": column})
        return self.store.resolve(cid, note, column)


def fmt(card: dict) -> str:
    lines = [f"[{card['id']}] ({card['column']}) {card['title']}"]
    if card.get("pending"):
        lines.append(f"  À TRAITER : {card.get('pendingReason', '')}")
    for key, label in (("description", "Description"), ("effort", "Effort"), ("risk", "Risque"), ("security", "Sécurité")):
        if card.get(key):
            lines.append(f"  {label} : {card[key]}")
    for n in card.get("notes", [])[-3:]:
        lines.append(f"  Note {n['at']} : {n['text']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--data", default=DEFAULT_DATA)
    p.add_argument("--json", action="store_true", help="sortie JSON")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("queue")
    s = sub.add_parser("show"); s.add_argument("id")
    s = sub.add_parser("resolve"); s.add_argument("id"); s.add_argument("note"); s.add_argument("--column", choices=sorted(COLUMN_IDS))
    s = sub.add_parser("add"); s.add_argument("title"); s.add_argument("--column", default="ideas", choices=sorted(COLUMN_IDS))
    s.add_argument("--description", default=""); s.add_argument("--effort", default=""); s.add_argument("--risk", default="")
    s.add_argument("--security", default=""); s.add_argument("--theme", default="")
    s = sub.add_parser("move"); s.add_argument("id"); s.add_argument("column", choices=sorted(COLUMN_IDS))
    s = sub.add_parser("export"); s.add_argument("--readme", default=README)
    a = p.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    c = Client(a.port, a.data)
    if a.cmd == "queue":
        out = c.queue()
        if a.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print(f"{len(out)} carte(s) à traiter" + ("" if c.online else " (serveur arrêté : lecture du fichier)"))
            for card in out:
                print(fmt(card))
        return 0
    if a.cmd == "show":
        card = next((x for x in c.board()["cards"] if x["id"] == a.id), None)
        if not card:
            raise SystemExit("carte introuvable")
        print(json.dumps(card, ensure_ascii=False, indent=2) if a.json else fmt(card))
        return 0
    if a.cmd == "resolve":
        print(fmt(c.resolve(a.id, a.note, a.column)))
        return 0
    if a.cmd == "add":
        print(fmt(c.create({"title": a.title, "column": a.column, "description": a.description, "effort": a.effort,
                            "risk": a.risk, "security": a.security, "theme": a.theme})))
        return 0
    if a.cmd == "move":
        print(fmt(c.update(a.id, {"column": a.column})))
        return 0
    if a.cmd == "export":
        old = ""
        if os.path.exists(a.readme):
            with open(a.readme, encoding="utf-8") as f:
                old = f.read()
        new = inject(old, board_markdown(c.board()))
        with open(a.readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print(f"Roadmap exportée dans {a.readme}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
