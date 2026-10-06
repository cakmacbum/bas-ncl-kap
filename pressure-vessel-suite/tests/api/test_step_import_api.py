"""POST /api/import/step testleri — tanıyıcı sahte nesneyle değiştirilir."""

import os

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api import services
from apps.api.main import app
from apps.api.store import store

STEP = b"ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"
HDR = {"Content-Type": "application/octet-stream"}


class _FakeRec:
    def __init__(self, filename, status="RECOGNIZED"):
        self._d = {"status": status, "source": {"filename": filename}, "heads": [], "nozzles": []}

    def to_dict(self):
        return self._d


@pytest.fixture
def client():
    store._items.clear()
    return TestClient(app)


@pytest.fixture
def fake(monkeypatch):
    seen = {}

    def _rec(path, filename=None):
        seen["path"] = str(path)
        seen["existed"] = os.path.exists(path)
        seen["filename"] = filename
        return _FakeRec(filename)

    monkeypatch.setattr(services, "recognize_step", _rec)
    return seen


def test_200_ve_temp_silinir(client, fake):
    r = client.post("/api/import/step", content=STEP, headers={**HDR, "X-Filename": "kap.step"})
    assert r.status_code == 200
    assert r.json()["status"] == "RECOGNIZED"
    assert r.json()["source"]["filename"] == "kap.step"
    assert fake["existed"] is True
    assert not os.path.exists(fake["path"])


def test_rejected_da_200(client, monkeypatch):
    monkeypatch.setattr(services, "recognize_step", lambda p, filename=None: _FakeRec(filename, "REJECTED"))
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 200 and r.json()["status"] == "REJECTED"


def test_413(client, fake):
    big = STEP + b"0" * (20 * 1024 * 1024)
    r = client.post("/api/import/step", content=big, headers=HDR)
    assert r.status_code == 413
    assert "path" not in fake


def test_415(client, fake):
    r = client.post("/api/import/step", content=b"bu bir step degil", headers=HDR)
    assert r.status_code == 415
    assert "path" not in fake


def test_503_tanıyıcı_yok(client, monkeypatch):
    monkeypatch.setattr(services, "recognize_step", None)
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 503


def test_503_blocked(client, monkeypatch):
    monkeypatch.setattr(services, "recognize_step", lambda p, filename=None: _FakeRec(filename, "BLOCKED"))
    assert client.post("/api/import/step", content=STEP, headers=HDR).status_code == 503


def test_dosya_adi_yol_bilesenleri_atilir(client, fake):
    r = client.post("/api/import/step", content=STEP, headers={**HDR, "X-Filename": "../../etc/passwd"})
    assert r.status_code == 200
    assert fake["filename"] == "passwd"
    r = client.post("/api/import/step", content=STEP, headers={**HDR, "X-Filename": "..%2F..%2Fetc%2Fpasswd"})
    assert fake["filename"] == "passwd"


def test_proje_deposu_degismez(client, fake):
    before = list(store._items.keys())
    client.post("/api/import/step", content=STEP, headers=HDR)
    assert list(store._items.keys()) == before == []
