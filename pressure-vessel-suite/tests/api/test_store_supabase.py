"""Supabase deposu + revizyon uçları: PostgREST taklit (gerçek ağ yok)."""

import json
from urllib.parse import parse_qs, unquote, urlsplit

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api import main as main_mod
from apps.api.storage_supabase import StoreUnavailable, SupabaseProjectStore, select_store
from apps.api.store import MAX_PROJECTS_PER_OWNER, store as memory_store
from tests.api.test_api_smoke import SAMPLE

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"


class FakePostgrest:
    """projects / project_revisions için minimal PostgREST taklidi."""

    def __init__(self):
        self.tables = {"projects": [], "project_revisions": []}
        self.calls = []
        self.fail = False

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, headers))
        assert headers["Authorization"].startswith("Bearer ")
        if self.fail:
            return 500, b"{}"
        parts = urlsplit(url)
        table = parts.path.rsplit("/", 1)[-1]
        q = {k: unquote(v[0]) for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
        rows = self.tables[table]
        if method == "POST":
            rows.append(json.loads(body))
            return 201, b""
        sel = [r for r in rows if self._match(r, q)]
        if method == "PATCH":
            for r in sel:
                r.update(json.loads(body))
            return 200, json.dumps(sel).encode()
        if "order" in q:
            col, _, direction = q["order"].partition(".")
            sel.sort(key=lambda r: r.get(col, ""), reverse=direction == "desc")
        if "limit" in q:
            sel = sel[: int(q["limit"])]
        return 200, json.dumps([self._project(r, q["select"]) for r in sel]).encode()

    @staticmethod
    def _match(row, q):
        for k, v in q.items():
            if k in ("select", "order", "limit"):
                continue
            assert v.startswith("eq.")
            if str(row[k]) != v[3:]:
                return False
        return True

    @staticmethod
    def _project(row, select):
        out = {}
        for col in select.split(","):
            if ":data->>" in col:
                alias, _, key = col.partition(":data->>")
                out[alias] = row["data"].get(key)
            else:
                out[col] = row.get(col)
        return out


@pytest.fixture
def fake(monkeypatch):
    f = FakePostgrest()
    st = SupabaseProjectStore("https://x.supabase.co", "service-key", f)
    monkeypatch.setattr(main_mod, "store", st)
    return f


def client(cid):
    c = TestClient(main_mod.app, raise_server_exceptions=False)
    c.headers["X-Client-Id"] = cid
    return c


def test_select_store_env():
    assert select_store(memory_store, env={}) is memory_store
    assert select_store(memory_store, env={"SUPABASE_URL": "https://x"}) is memory_store
    s = select_store(memory_store, env={"SUPABASE_URL": "https://x", "SUPABASE_SERVICE_ROLE_KEY": "k"})
    assert isinstance(s, SupabaseProjectStore)


def test_crud_and_revisions(fake):
    a = client(A)
    pid = a.post("/api/projects", json=SAMPLE).json()["id"]
    assert a.get(f"/api/projects/{pid}").status_code == 200
    changed = {**SAMPLE, "project_name": "Yeni ad"}
    assert a.put(f"/api/projects/{pid}", json=changed).status_code == 200
    assert a.get(f"/api/projects/{pid}").json()["project_name"] == "Yeni ad"
    assert [r["revision"] for r in a.get(f"/api/projects/{pid}/revisions").json()] == [2, 1]
    assert a.get(f"/api/projects/{pid}/revisions/1").json()["project_name"] == SAMPLE["project_name"]
    assert a.get(f"/api/projects/{pid}/revisions/2").json()["project_name"] == "Yeni ad"
    assert a.get(f"/api/projects/{pid}/revisions/9").status_code == 404
    summ = a.get("/api/projects").json()
    assert len(summ) == 1 and summ[0]["id"] == pid and summ[0]["project_name"] == "Yeni ad"


def test_owner_isolation(fake):
    a, b = client(A), client(B)
    pid = a.post("/api/projects", json=SAMPLE).json()["id"]
    assert b.get("/api/projects").json() == []
    assert b.get(f"/api/projects/{pid}").status_code == 404
    assert b.put(f"/api/projects/{pid}", json=SAMPLE).status_code == 404
    assert b.get(f"/api/projects/{pid}/revisions").status_code == 404
    assert b.get(f"/api/projects/{pid}/revisions/1").status_code == 404


def test_bad_id_never_reaches_backend(fake):
    a = client(A)
    n = len(fake.calls)
    assert a.get("/api/projects/x%26owner=neq.z/revisions").status_code == 404
    assert a.get("/api/projects/abc*/revisions/1").status_code == 404
    assert len(fake.calls) == n


def test_owner_limit(fake):
    a = client(A)
    for _ in range(MAX_PROJECTS_PER_OWNER):
        assert a.post("/api/projects", json=SAMPLE).status_code == 201
    assert a.post("/api/projects", json=SAMPLE).status_code == 429


def test_backend_down_is_503(fake):
    fake.fail = True
    r = client(A).get("/api/projects")
    assert r.status_code == 503


def test_service_key_only_in_server_headers(fake):
    a = client(A)
    r = a.post("/api/projects", json=SAMPLE)
    assert "service-key" not in r.text
    assert all(h["apikey"] == "service-key" for _, _, h in fake.calls)


def test_store_unavailable_class():
    def boom(*_a):
        raise StoreUnavailable("net")

    st = SupabaseProjectStore("https://x", "k", boom)
    with pytest.raises(StoreUnavailable):
        st.get(A, "0123456789ab")
