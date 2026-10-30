"""Durumsuz uçlar: POST /api/calculate ve /api/report.html (proje gövdede)."""

import copy

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.store import store
from test_api_smoke import SAMPLE


@pytest.fixture
def client():
    store._items.clear()
    return TestClient(app)


def test_calculate_matches_id_endpoint(client):
    pid = client.post("/api/projects", json=SAMPLE).json()["id"]
    by_id = client.post(f"/api/projects/{pid}/calculate").json()
    r = client.post("/api/calculate", json=SAMPLE)
    assert r.status_code == 200
    assert r.json()["global_mawp_mpa"] == by_id["global_mawp_mpa"]
    assert r.json()["global_mawp_mpa"] is not None


def test_report_matches_id_endpoint(client):
    pid = client.post("/api/projects", json=SAMPLE).json()["id"]
    by_id = client.get(f"/api/projects/{pid}/report.html")
    r = client.post("/api/report.html", json=SAMPLE)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "<html" in r.text.lower()
    assert len(r.text) > 0 and by_id.status_code == 200


@pytest.mark.parametrize("path", ["/api/calculate", "/api/report.html"])
def test_invalid_body_422(client, path):
    bad = copy.deepcopy(SAMPLE)
    del bad["shell_sections"][0]["inside_diameter"]
    assert client.post(path, json=bad).status_code == 422
    assert client.post(path, content=b"not json").status_code == 422


@pytest.mark.parametrize("path", ["/api/calculate", "/api/report.html"])
def test_oversize_body_413(client, path):
    big = b'{"project_name": "' + b"x" * (2 * 1024 * 1024 + 10) + b'"}'
    assert client.post(path, content=big).status_code == 413
