"""Faz E2: transaction'lı, değiştirilemez hesap koşusu deposu.

SQLite yalnızca standart kütüphane ile kullanılır. Bir koşu kaydı INSERT edildikten
sonra payload güncellenmez; düzeltmeler yeni revision/run olarak eklenir.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


class CalculationRunStore:
    """Calculation run, audit, approval ve attachment metadata deposu."""

    ROLE_PERMISSIONS = {
        "engineer": frozenset({"create_run", "attach"}),
        "checker": frozenset({"approve", "attach"}),
        "approver": frozenset({"approve"}),
        "admin": frozenset({"create_run", "approve", "attach"}),
    }

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._db = sqlite3.connect(self.path)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS calculation_runs (
              run_id TEXT PRIMARY KEY, project_number TEXT NOT NULL,
              revision TEXT NOT NULL, created_at TEXT NOT NULL,
              actor TEXT NOT NULL, payload TEXT NOT NULL, payload_hash TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL DEFAULT 'CALCULATED'
            );
            CREATE TABLE IF NOT EXISTS audit_events (
              event_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
              event_type TEXT NOT NULL, actor TEXT NOT NULL, created_at TEXT NOT NULL,
              details TEXT NOT NULL, FOREIGN KEY(run_id) REFERENCES calculation_runs(run_id)
            );
            CREATE TABLE IF NOT EXISTS approvals (
              run_id TEXT NOT NULL, role TEXT NOT NULL, actor TEXT NOT NULL,
              signed_at TEXT NOT NULL, note TEXT NOT NULL DEFAULT '',
              PRIMARY KEY(run_id, role), FOREIGN KEY(run_id) REFERENCES calculation_runs(run_id)
            );
            CREATE TABLE IF NOT EXISTS attachments (
              attachment_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, filename TEXT NOT NULL,
              media_type TEXT NOT NULL, content_hash TEXT NOT NULL, created_at TEXT NOT NULL,
              FOREIGN KEY(run_id) REFERENCES calculation_runs(run_id)
            );
            CREATE TRIGGER IF NOT EXISTS calculation_runs_immutable_update
            BEFORE UPDATE ON calculation_runs
            BEGIN SELECT RAISE(ABORT, 'calculation runs are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS calculation_runs_immutable_delete
            BEFORE DELETE ON calculation_runs
            BEGIN SELECT RAISE(ABORT, 'calculation runs are immutable'); END;
            """
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def create_run(self, project_number: str, revision: str, payload: Mapping[str, Any], actor: str) -> str:
        """Atomik olarak immutable run ve audit olayı oluştur."""
        if not actor:
            raise ValueError("actor zorunludur")
        run_id = uuid4().hex
        created = datetime.now(timezone.utc).isoformat()
        encoded = _json(dict(payload))
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        with self._db:
            self._db.execute(
                "INSERT INTO calculation_runs(run_id,project_number,revision,created_at,actor,payload,payload_hash) VALUES(?,?,?,?,?,?,?)",
                (run_id, project_number, revision, created, actor, encoded, digest),
            )
            self._audit(run_id, "CALCULATION_CREATED", actor, {"payload_hash": digest})
        return run_id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self._db.execute("SELECT * FROM calculation_runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item["payload"])
        item["approvals"] = [dict(r) for r in self._db.execute(
            "SELECT role,actor,signed_at,note FROM approvals WHERE run_id = ?", (run_id,)
        )]
        return item

    def approve(self, run_id: str, role: str, actor: str, note: str = "") -> None:
        if not self.can(role, "approve"):
            raise PermissionError(f"Rol '{role}' approval/sign-off yetkisine sahip değil.")
        if self.get_run(run_id) is None:
            raise KeyError(run_id)
        now = datetime.now(timezone.utc).isoformat()
        with self._db:
            self._db.execute(
                "INSERT INTO approvals(run_id,role,actor,signed_at,note) VALUES(?,?,?,?,?) "
                "ON CONFLICT(run_id,role) DO UPDATE SET actor=excluded.actor,signed_at=excluded.signed_at,note=excluded.note",
                (run_id, role, actor, now, note),
            )
            self._audit(run_id, "APPROVAL_SIGNED", actor, {"role": role, "note": note})

    @classmethod
    def can(cls, role: str, permission: str) -> bool:
        """RBAC kontrolü; API katmanı bu kararı tekrar üretmek zorunda kalmaz."""
        return permission in cls.ROLE_PERMISSIONS.get(role, frozenset())

    def add_attachment(self, run_id: str, filename: str, media_type: str, content: bytes) -> str:
        if self.get_run(run_id) is None:
            raise KeyError(run_id)
        attachment_id = uuid4().hex
        digest = hashlib.sha256(content).hexdigest()
        with self._db:
            self._db.execute(
                "INSERT INTO attachments VALUES(?,?,?,?,?,?)",
                (attachment_id, run_id, filename, media_type, digest, datetime.now(timezone.utc).isoformat()),
            )
            self._audit(run_id, "ATTACHMENT_REGISTERED", "system", {"attachment_id": attachment_id, "sha256": digest})
        return attachment_id

    def audit_log(self, run_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self._db.execute(
            "SELECT event_id,event_type,actor,created_at,details FROM audit_events WHERE run_id=? ORDER BY event_id",
            (run_id,),
        )]

    def backup(self, destination: str | Path) -> None:
        """SQLite online backup API ile tutarlı yedek al."""
        target = sqlite3.connect(str(destination))
        try:
            self._db.backup(target)
        finally:
            target.close()

    def _audit(self, run_id: str, event_type: str, actor: str, details: Mapping[str, Any]) -> None:
        self._db.execute(
            "INSERT INTO audit_events(run_id,event_type,actor,created_at,details) VALUES(?,?,?,?,?)",
            (run_id, event_type, actor, datetime.now(timezone.utc).isoformat(), _json(details)),
        )


__all__ = ["CalculationRunStore"]
