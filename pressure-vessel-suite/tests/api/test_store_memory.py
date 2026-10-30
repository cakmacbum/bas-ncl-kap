"""Bellek içi depo: revizyon geçmişi ve sahip kontrolü."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.store import store
from tests.api.test_api_smoke import SAMPLE

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"


@pytest.fixture(autouse=True)
def _clean():
    store._items.clear()
    store._revs.clear()
    yield
    store._items.clear()
    store._revs.clear()


def make(cid):
    c = TestClient(app, raise_server_exceptions=False)
    c.headers["X-Client-Id"] = cid
    return c


def test_revisions_memory():
    a, b = make(A), make(B)
    pid = a.post("/api/projects", json=SAMPLE).json()["id"]
    a.put(f"/api/projects/{pid}", json={**SAMPLE, "project_name": "V2"})
    assert [r["revision"] for r in a.get(f"/api/projects/{pid}/revisions").json()] == [2, 1]
    assert a.get(f"/api/projects/{pid}/revisions/1").json()["project_name"] == SAMPLE["project_name"]
    assert a.get(f"/api/projects/{pid}/revisions/2").json()["project_name"] == "V2"
    assert a.get(f"/api/projects/{pid}/revisions/3").status_code == 404
    assert b.get(f"/api/projects/{pid}/revisions").status_code == 404
    assert b.get(f"/api/projects/{pid}/revisions/1").status_code == 404
