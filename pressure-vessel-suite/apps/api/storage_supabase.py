"""Supabase (PostgREST) tabanlı kalıcı proje deposu — ProjectStore ile aynı arayüz.

Yalnız SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY ikisi de tanımlıysa seçilir (select_store).
Servis anahtarı yalnız sunucuda kullanılır; sahip filtresi her sorguda uygulanır.
Ağ katmanı enjekte edilebilir (transport) — testler gerçek ağ kullanmaz.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Callable, List, Tuple
from urllib.parse import quote

from domain import VesselProject  # type: ignore

from apps.api.store import MAX_PROJECTS_PER_OWNER, ProjectLimitReached

_ID_RE = re.compile(r"^[0-9a-f]{12}$")
_TIMEOUT = 10

# (method, url, headers, body) -> (status, response_bytes)
Transport = Callable[[str, str, dict, "bytes | None"], Tuple[int, bytes]]


class StoreUnavailable(Exception):
    """Depo erişilemez / beklenmeyen yanıt (API 503 döner)."""


def _urllib_transport(method: str, url: str, headers: dict, body: "bytes | None") -> Tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:  # noqa: S310 (https URL env'den)
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise StoreUnavailable(str(e)) from None


class SupabaseProjectStore:
    def __init__(self, url: str, service_key: str, transport: Transport | None = None) -> None:
        self._base = url.rstrip("/") + "/rest/v1"
        self._headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        }
        self._transport = transport or _urllib_transport

    # -- yardımcılar ---------------------------------------------------
    def _call(self, method: str, path: str, body: object = None, prefer: str | None = None):
        headers = dict(self._headers)
        if prefer:
            headers["Prefer"] = prefer
        data = json.dumps(body).encode("utf-8") if body is not None else None
        status, raw = self._transport(method, f"{self._base}/{path}", headers, data)
        if status >= 300:
            raise StoreUnavailable(f"supabase {status}")
        return json.loads(raw) if raw else None

    @staticmethod
    def _eq(value: object) -> str:
        return "eq." + quote(str(value), safe="")

    def _own(self, owner: str, project_id: str):
        """Sahip satırını (id, revision) döndürür; yok/başkasınınsa None."""
        if not _ID_RE.match(project_id):
            return None
        rows = self._call(
            "GET", f"projects?select=id,revision&id={self._eq(project_id)}&owner={self._eq(owner)}"
        )
        return rows[0] if rows else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # -- ProjectStore arayüzü ------------------------------------------
    def create(self, owner: str, project: VesselProject) -> str:
        rows = self._call("GET", f"projects?select=id&owner={self._eq(owner)}&limit={MAX_PROJECTS_PER_OWNER}")
        if len(rows) >= MAX_PROJECTS_PER_OWNER:
            raise ProjectLimitReached
        project_id = uuid.uuid4().hex[:12]
        data = project.model_dump(mode="json")
        self._call(
            "POST",
            "projects",
            {"id": project_id, "owner": owner, "data": data, "revision": 1, "updated_at": self._now()},
            prefer="return=minimal",
        )
        self._call(
            "POST", "project_revisions", {"project_id": project_id, "revision": 1, "data": data}, prefer="return=minimal"
        )
        return project_id

    def get(self, owner: str, project_id: str) -> VesselProject | None:
        if not _ID_RE.match(project_id):
            return None
        rows = self._call("GET", f"projects?select=data&id={self._eq(project_id)}&owner={self._eq(owner)}")
        return VesselProject.model_validate(rows[0]["data"]) if rows else None

    def update(self, owner: str, project_id: str, project: VesselProject) -> bool:
        data = project.model_dump(mode="json")
        for _ in range(3):  # iyimser eşzamanlılık: revision koşullu PATCH
            row = self._own(owner, project_id)
            if row is None:
                return False
            nxt = int(row["revision"]) + 1
            updated = self._call(
                "PATCH",
                f"projects?id={self._eq(project_id)}&owner={self._eq(owner)}&revision={self._eq(row['revision'])}",
                {"data": data, "revision": nxt, "updated_at": self._now()},
                prefer="return=representation",
            )
            if updated:
                self._call(
                    "POST",
                    "project_revisions",
                    {"project_id": project_id, "revision": nxt, "data": data},
                    prefer="return=minimal",
                )
                return True
        raise StoreUnavailable("revizyon çakışması")

    def summaries(self, owner: str) -> List[dict]:
        sel = ",".join(
            f"{k}:data->>{k}"
            for k in ("project_number", "project_name", "customer", "revision", "calculation_code")
        )
        return self._call(
            "GET", f"projects?select=id,{sel}&owner={self._eq(owner)}&order=updated_at.desc"
        ) or []

    def revisions(self, owner: str, project_id: str) -> List[dict] | None:
        if self._own(owner, project_id) is None:
            return None
        return self._call(
            "GET",
            f"project_revisions?select=revision,created_at&project_id={self._eq(project_id)}&order=revision.desc",
        ) or []

    def get_revision(self, owner: str, project_id: str, n: int) -> VesselProject | None:
        if self._own(owner, project_id) is None:
            return None
        rows = self._call(
            "GET", f"project_revisions?select=data&project_id={self._eq(project_id)}&revision={self._eq(int(n))}"
        )
        return VesselProject.model_validate(rows[0]["data"]) if rows else None


def select_store(memory_store, env=None, transport: Transport | None = None):
    env = os.environ if env is None else env
    url, key = env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return SupabaseProjectStore(url, key, transport)
    return memory_store
