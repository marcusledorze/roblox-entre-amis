"""Export de la roadmap en Markdown (page de lecture seule sur GitHub).

Le tableau est écrit dans README.md, entre deux marqueurs, pour qu'il soit
la première chose visible sur la page d'accueil du dépôt.
"""
from __future__ import annotations

import re
import time

START = "<!-- ROADMAP:START (généré par roadmap-app/roadmap.py export, ne pas modifier à la main) -->"
END = "<!-- ROADMAP:END -->"
ICONS = {"ideas": "💡", "rc": "🚦", "p1": "🛠️", "p2": "✨", "doing": "🔧", "done": "✅"}
# ordre de lecture sur GitHub : ce qui bloque la V1 d'abord, ce qui est fait en dernier
ORDER = ["rc", "doing", "p1", "p2", "ideas", "done"]


def _esc(text: str) -> str:
    """Neutralise le Markdown/HTML actif dans un texte libre (une seule ligne)."""
    text = " ".join((text or "").split())
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"([\\`*_\[\]|#])", r"\\\1", text)


def board_markdown(board: dict, now: str | None = None) -> str:
    now = now or time.strftime("%d/%m/%Y %H:%M")
    cols = {c["id"]: c for c in board["columns"]}
    cards = board["cards"]
    pending = sum(1 for c in cards if c.get("pending"))
    out = [
        "## Roadmap",
        "",
        f"_Mise à jour : {now} · {len(cards)} cartes · {pending} à traiter._ "
        "Version modifiable : l'app locale `py roadmap-app/server.py` → http://127.0.0.1:8787",
        "",
    ]
    for col_id in ORDER + [c for c in cols if c not in ORDER]:
        if col_id not in cols:
            continue
        items = sorted((c for c in cards if c["column"] == col_id), key=lambda c: c.get("position", 0))
        out.append(f"### {ICONS.get(col_id, '')} {_esc(cols[col_id]['title'])} ({len(items)})".replace("  ", " "))
        out.append("")
        if not items:
            out += ["_Vide._", ""]
            continue
        if col_id == "done":
            out.append("<details><summary>Voir tout ce qui a été fait</summary>")
            out.append("")
        for c in items:
            box = "x" if col_id == "done" else " "
            line = f"- [{box}] **{_esc(c['title'])}**"
            if c.get("description"):
                line += f" — {_esc(c['description'])}"
            tags = []
            if c.get("pending"):
                tags.append("⚠️ à traiter")
            if c.get("effort"):
                tags.append(f"effort {_esc(c['effort'])}")
            if c.get("risk"):
                tags.append(f"risque {_esc(c['risk'])}")
            if tags:
                line += " · _" + " · ".join(tags) + "_"
            out.append(line)
            if c.get("security"):
                out.append(f"  - 🔒 {_esc(c['security'])}")
            if c.get("notes"):
                out.append(f"  - 📝 {_esc(c['notes'][-1]['text'])}")
        if col_id == "done":
            out += ["", "</details>"]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def inject(readme: str, block: str) -> str:
    """Remplace (ou ajoute) le bloc roadmap dans le README."""
    section = f"{START}\n{block}{END}"
    if START in readme and END in readme:
        head, rest = readme.split(START, 1)
        _, tail = rest.split(END, 1)
        return head + section + tail
    return readme.rstrip() + ("\n\n" if readme.strip() else "") + section + "\n"
