"""Sahip bazlı proje izolasyonu: anonim X-Client-Id ve Supabase kullanıcısı."""

import time

import jwt
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api import store as store_mod
from apps.api.main import app
from apps.api.store import store
from tests.api.test_api_smoke import SAMPLE

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"


@pytest.fixture(autouse=True)
def _clean():
    store._items.clear()
    yield
    store._items.clear()


def make(cid=None):
    c = TestClient(app, raise_server_exceptions=False)
    c.headers.pop("X-Client-Id", None)
    if cid:
        c.headers["X-Client-Id"] = cid
    return c


def test_a_creates_b_does_not_see():
    a, b = make(A), make(B)
    assert a.post("/api/projects", json=SAMPLE).status_code == 201
    assert len(a.get("/api/projects").json()) == 1
    assert b.get("/api/projects").json() == []


def test_other_owner_gets_404_everywhere():
    a, b = make(A), make(B)
    pid = a.post("/api/projects", json=SAMPLE).json()["id"]
    base = f"/api/projects/{pid}"
    assert a.get(base).status_code == 200
    assert b.get(base).status_code == 404
    assert b.put(base, json=SAMPLE).status_code == 404
    assert b.post(f"{base}/calculate").status_code == 404
    assert b.get(f"{base}/report.html").status_code == 404
    assert b.get(f"{base}/model.step").status_code == 404
    assert b.get(f"{base}/model.stl").status_code == 404
    assert b.get("/api/projects/doesnotexist").status_code == 404


def test_missing_header_400():
    r = make().get("/api/projects")
    assert r.status_code == 400
    assert r.json() == {"detail": "Missing or invalid X-Client-Id"}


@pytest.mark.parametrize("bad", ["abc", "{" + A + "}", A.replace("-", ""), "urn:uuid:" + A, A + "x"])
def test_malformed_header_400(bad):
    r = make().get("/api/projects", headers={"X-Client-Id": bad})
    assert r.status_code == 400


def test_uppercase_uuid_same_owner():
    make(A).post("/api/projects", json=SAMPLE)
    assert len(make(A.upper()).get("/api/projects").json()) == 1


def test_health_public_without_header():
    assert make().get("/api/health").status_code == 200


def test_per_owner_limit_429(monkeypatch):
    monkeypatch.setattr(store_mod, "MAX_PROJECTS_PER_OWNER", 2)
    a, b = make(A), make(B)
    assert a.post("/api/projects", json=SAMPLE).status_code == 201
    assert a.post("/api/projects", json=SAMPLE).status_code == 201
    r = a.post("/api/projects", json=SAMPLE)
    assert r.status_code == 429 and r.json() == {"detail": "Project limit reached"}
    assert b.post("/api/projects", json=SAMPLE).status_code == 201


def test_global_lru_eviction(monkeypatch):
    monkeypatch.setattr(store_mod, "MAX_PROJECTS_GLOBAL", 3)
    a, b = make(A), make(B)
    ids = [a.post("/api/projects", json=SAMPLE).json()["id"] for _ in range(3)]
    assert a.get(f"/api/projects/{ids[0]}").status_code == 200  # ids[0] yeniden erişildi
    new = b.post("/api/projects", json=SAMPLE).json()["id"]
    assert a.get(f"/api/projects/{ids[1]}").status_code == 404  # en az yakın erişilen atıldı
    assert a.get(f"/api/projects/{ids[0]}").status_code == 200
    assert a.get(f"/api/projects/{ids[2]}").status_code == 200
    assert b.get(f"/api/projects/{new}").status_code == 200


SECRET = "test-secret-at-least-32-bytes-long-xxxx"
SUPA = "https://example.supabase.co"


def _tok(sub):
    claims = {"sub": sub, "aud": "authenticated", "iss": f"{SUPA}/auth/v1", "exp": int(time.time()) + 3600}
    return {"Authorization": "Bearer " + jwt.encode(claims, SECRET, algorithm="HS256")}


def test_supabase_mode_two_users_isolated(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    monkeypatch.setenv("SUPABASE_URL", SUPA)
    c = make()  # X-Client-Id yok; supabase modunda gerekmez
    pid = c.post("/api/projects", json=SAMPLE, headers=_tok("u1")).json()["id"]
    assert len(c.get("/api/projects", headers=_tok("u1")).json()) == 1
    assert c.get("/api/projects", headers=_tok("u2")).json() == []
    assert c.get(f"/api/projects/{pid}", headers=_tok("u2")).status_code == 404
    assert c.get(f"/api/projects/{pid}").status_code == 401
    assert c.get("/api/projects", headers={"X-Client-Id": A}).status_code == 401
