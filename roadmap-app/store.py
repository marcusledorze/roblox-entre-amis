"""Stockage de la roadmap : un fichier JSON, écrit de façon atomique.

Toute modification faite par l'utilisateur (acteur "user") marque la carte
« à traiter » (pending). Claude lit la file d'attente et marque les cartes
traitées (acteur "claude"), ce qui ne les remet pas en attente.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
import uuid

COLUMNS = [
    {"id": "ideas", "title": "Idées"},
    {"id": "rc", "title": "Release candidate (avant V1)"},
    {"id": "p1", "title": "P1 · Stabilité"},
    {"id": "p2", "title": "P2 · Features"},
    {"id": "doing", "title": "En cours"},
    {"id": "done", "title": "Fait"},
]
COLUMN_IDS = {c["id"] for c in COLUMNS}
EFFORTS = {"", "S", "M", "L", "S-M", "M-L"}
RISKS = {"", "faible", "moyen", "élevé"}
ACTORS = {"user", "claude"}

LIMITS = {"title": 140, "description": 4000, "security": 1000, "theme": 40, "note": 2000}
EDITABLE = ("title", "description", "security", "theme", "effort", "risk", "column")


class ValidationError(ValueError):
    pass


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _clean_text(value, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError(f"{field} doit être du texte")
    value = value.replace("\r\n", "\n").strip()
    # retire les caractères de contrôle (sauf saut de ligne / tabulation)
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    if len(value) > LIMITS[field]:
        raise ValidationError(f"{field} trop long (max {LIMITS[field]})")
    return value


def validate_fields(payload: dict, partial: bool) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("objet JSON attendu")
    unknown = set(payload) - set(EDITABLE) - {"actor", "position"}
    if unknown:
        raise ValidationError("champ inconnu : " + ", ".join(sorted(unknown)))
    out: dict = {}
    for field in ("title", "description", "security", "theme"):
        if field in payload:
            out[field] = _clean_text(payload[field], field)
    if "effort" in payload:
        if payload["effort"] not in EFFORTS:
            raise ValidationError("effort invalide")
        out["effort"] = payload["effort"]
    if "risk" in payload:
        if payload["risk"] not in RISKS:
            raise ValidationError("risque invalide")
        out["risk"] = payload["risk"]
    if "column" in payload:
        if payload["column"] not in COLUMN_IDS:
            raise ValidationError("colonne invalide")
        out["column"] = payload["column"]
    if "position" in payload:
        pos = payload["position"]
        if not isinstance(pos, int) or isinstance(pos, bool) or pos < 0 or pos > 10000:
            raise ValidationError("position invalide")
        out["position"] = pos
    if not partial:
        if not out.get("title"):
            raise ValidationError("titre obligatoire")
        out.setdefault("column", "ideas")
    elif "title" in out and not out["title"]:
        raise ValidationError("titre obligatoire")
    return out


def _actor(payload: dict) -> str:
    actor = payload.get("actor", "user") if isinstance(payload, dict) else "user"
    if actor not in ACTORS:
        raise ValidationError("acteur invalide")
    return actor


class Store:
    def __init__(self, path: str):
        self.path = path
        self.lock = threading.RLock()
        self._mtime = None
        self.data = self._load()

    # ---------- persistance ----------
    def _stat(self):
        try:
            st = os.stat(self.path)
            return (st.st_mtime_ns, st.st_size)
        except FileNotFoundError:
            return None

    def _load(self) -> dict:
        self._mtime = self._stat()
        if self._mtime is None:
            return {"rev": 0, "cards": []}
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("rev", 0)
        data.setdefault("cards", [])
        return data

    def _refresh(self) -> None:
        """Recharge si le fichier a été modifié par un autre processus (CLI, git pull)."""
        if self._stat() != self._mtime:
            self.data = self._load()

    def _save(self) -> None:
        self.data["rev"] += 1
        folder = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".roadmap-", suffix=".json", dir=folder)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            os.replace(tmp, self.path)
            self._mtime = self._stat()
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

    # ---------- lecture ----------
    def snapshot(self) -> dict:
        with self.lock:
            self._refresh()
            return json.loads(json.dumps({"rev": self.data["rev"], "columns": COLUMNS, "cards": self.data["cards"]}))

    def get(self, card_id: str) -> dict | None:
        with self.lock:
            for c in self.data["cards"]:
                if c["id"] == card_id:
                    return c
        return None

    def queue(self) -> list:
        with self.lock:
            self._refresh()
            return [json.loads(json.dumps(c)) for c in self.data["cards"] if c.get("pending")]

    # ---------- écriture ----------
    def _column_cards(self, column: str) -> list:
        return sorted((c for c in self.data["cards"] if c["column"] == column), key=lambda c: c.get("position", 0))

    def _place(self, card: dict, column: str, position: int | None) -> None:
        others = [c for c in self._column_cards(column) if c["id"] != card["id"]]
        if position is None or position > len(others):
            position = len(others)
        others.insert(position, card)
        for i, c in enumerate(others):
            c["position"] = i
        card["column"] = column

    def _history(self, card: dict, actor: str, action: str, detail: str = "") -> None:
        card.setdefault("history", []).append({"at": _now(), "by": actor, "action": action, "detail": detail[:300]})
        card["history"] = card["history"][-30:]

    def create(self, payload: dict) -> dict:
        actor = _actor(payload)
        fields = validate_fields(payload, partial=False)
        with self.lock:
            self._refresh()
            card = {
                "id": uuid.uuid4().hex[:10],
                "title": fields["title"],
                "description": fields.get("description", ""),
                "theme": fields.get("theme", ""),
                "effort": fields.get("effort", ""),
                "risk": fields.get("risk", ""),
                "security": fields.get("security", ""),
                "column": fields["column"],
                "position": 0,
                "createdBy": actor,
                "createdAt": _now(),
                "updatedAt": _now(),
                "pending": actor == "user",
                "pendingReason": "nouvelle carte" if actor == "user" else "",
                "notes": [],
                "history": [],
            }
            self.data["cards"].append(card)
            self._place(card, card["column"], fields.get("position"))
            self._history(card, actor, "create", card["title"])
            self._save()
            return json.loads(json.dumps(card))

    def update(self, card_id: str, payload: dict) -> dict:
        actor = _actor(payload)
        fields = validate_fields(payload, partial=True)
        with self.lock:
            self._refresh()
            card = self.get(card_id)
            if card is None:
                raise KeyError(card_id)
            changes = []
            for key in ("title", "description", "security", "theme", "effort", "risk"):
                if key in fields and fields[key] != card.get(key):
                    card[key] = fields[key]
                    changes.append(key)
            new_col = fields.get("column", card["column"])
            if new_col != card["column"] or "position" in fields:
                old_col = card["column"]
                self._place(card, new_col, fields.get("position"))
                if old_col != new_col:
                    self._place_cleanup(old_col)
                    changes.append(f"colonne {old_col} → {new_col}")
            if not changes and "position" not in fields:
                return json.loads(json.dumps(card))
            card["updatedAt"] = _now()
            if changes and actor == "user":
                card["pending"] = True
                reason = ", ".join(changes)
                prev = card.get("pendingReason") or ""
                card["pendingReason"] = reason if not prev else (prev + " ; " + reason)[-300:]
            if changes:
                self._history(card, actor, "update", ", ".join(changes))
            self._save()
            return json.loads(json.dumps(card))

    def _place_cleanup(self, column: str) -> None:
        for i, c in enumerate(self._column_cards(column)):
            c["position"] = i

    def delete(self, card_id: str, actor: str = "user") -> None:
        if actor not in ACTORS:
            raise ValidationError("acteur invalide")
        with self.lock:
            self._refresh()
            card = self.get(card_id)
            if card is None:
                raise KeyError(card_id)
            self.data["cards"].remove(card)
            self._place_cleanup(card["column"])
            self._save()

    def resolve(self, card_id: str, note: str, column: str | None = None) -> dict:
        """Claude a traité la carte : retire « à traiter » et ajoute une note."""
        note = _clean_text(note, "note")
        if column is not None and column not in COLUMN_IDS:
            raise ValidationError("colonne invalide")
        with self.lock:
            self._refresh()
            card = self.get(card_id)
            if card is None:
                raise KeyError(card_id)
            if column and column != card["column"]:
                old = card["column"]
                self._place(card, column, None)
                self._place_cleanup(old)
            card["pending"] = False
            card["pendingReason"] = ""
            if note:
                card.setdefault("notes", []).append({"at": _now(), "by": "claude", "text": note})
            card["updatedAt"] = _now()
            self._history(card, "claude", "resolve", note)
            self._save()
            return json.loads(json.dumps(card))
