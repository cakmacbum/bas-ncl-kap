"""Supabase JWT auth ve 500 işleyicisi testleri."""

import time

import jwt
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api.main import app

SECRET = "test-secret-at-least-32-bytes-long-xxxx"
SUPA = "https://example.supabase.co"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    monkeypatch.setenv("SUPABASE_URL", SUPA)
    return TestClient(app, raise_server_exceptions=False)


def token(exp_delta=3600, secret=SECRET, aud="authenticated", iss=f"{SUPA}/auth/v1"):
    claims = {"sub": "u1", "aud": aud, "iss": iss, "exp": int(time.time()) + exp_delta}
    return jwt.encode(claims, secret, algorithm="HS256")


def auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_health_is_public(client):
    assert client.get("/api/health").status_code == 200


def test_protected_without_token_401(client):
    r = client.get("/api/projects")
    assert r.status_code == 401
    assert "detail" in r.json()


def test_valid_token_passes(client):
    assert client.get("/api/projects", headers=auth(token())).status_code == 200


@pytest.mark.parametrize("bad", [
    lambda: token(exp_delta=-60),
    lambda: token(secret="x" * 40),
    lambda: token(aud="other"),
    lambda: token(iss="https://evil.example/auth/v1"),
    lambda: "garbage",
])
def test_bad_tokens_401(client, bad):
    assert client.get("/api/projects", headers=auth(bad())).status_code == 401


def test_500_hides_details(client, monkeypatch):
    from apps.api import main

    def boom():
        raise RuntimeError("secret-internal-detail")

    monkeypatch.setattr(main.store, "summaries", boom)
    r = client.get("/api/projects", headers=auth(token()))
    assert r.status_code == 500
    assert "secret-internal-detail" not in r.text
