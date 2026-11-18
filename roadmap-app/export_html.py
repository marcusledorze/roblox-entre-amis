"""Génère la page web de la roadmap (page/index.html) à partir de page/template.html.

Les données sont insérées dans un <script type="application/json">, avec les
caractères < > & échappés en \\u003c etc. : un titre de carte ne peut ni fermer
la balise script ni injecter de HTML. La page n'affiche le texte qu'avec textContent.
"""
from __future__ import annotations

import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "page", "template.html")
OUTPUT = os.path.join(HERE, "page", "index.html")
PLACEHOLDER = "__ROADMAP_DATA__"
FIELDS = ("id", "title", "description", "theme", "effort", "risk", "security", "column", "position", "pending", "notes")


def safe_json(obj) -> str:
    return (json.dumps(obj, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def render(board: dict, template: str, generated: str | None = None) -> str:
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("le modèle doit contenir exactement un " + PLACEHOLDER)
    cards = [{k: c.get(k) for k in FIELDS} for c in board["cards"]]
    for c in cards:  # seule la dernière note est affichée, sans l'historique
        c["notes"] = [{"text": n.get("text", "")} for n in (c["notes"] or [])][-1:]
    payload = {
        "generated": generated or time.strftime("%d/%m/%Y à %H:%M"),
        "board": {"columns": board["columns"], "cards": cards},
    }
    return template.replace(PLACEHOLDER, safe_json(payload))


def write(board: dict, out: str = OUTPUT, template_path: str = TEMPLATE) -> str:
    with open(template_path, encoding="utf-8") as f:
        html = render(board, f.read())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return out
