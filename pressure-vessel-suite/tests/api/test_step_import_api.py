"""POST /api/import/step testleri — tanıyıcı sahte fonksiyonla değiştirilir.

Tanıma ayrı (spawn) süreçte koştuğu için sahteler modül seviyesinde olmalı (çocuk süreç bu
modülü adıyla import eder). Spawn başına ~5 sn import maliyeti var; süreç açan testler az tutuldu.
"""

import multiprocessing
import os
import tempfile
import threading
import time

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api import main, services
from apps.api.main import app
from apps.api.store import store

STEP = b"ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"
HDR = {"Content-Type": "application/octet-stream"}


class _FakeRec:
    def __init__(self, d):
        self._d = d

    def to_dict(self):
        return self._d


def fake_ok(path, filename=None):
    return _FakeRec({
        "status": "RECOGNIZED", "source": {"filename": filename}, "heads": [], "nozzles": [],
        "_path": str(path), "_existed": os.path.exists(path),
    })


def fake_rejected(path, filename=None):
    return _FakeRec({"status": "REJECTED", "source": {"filename": filename}})


def fake_blocked(path, filename=None):
    return _FakeRec({"status": "BLOCKED", "source": {"filename": filename}})


def fake_slow(path, filename=None):
    time.sleep(120)
    return fake_ok(path, filename)


def fake_crash(path, filename=None):
    os._exit(3)


def fake_raises(path, filename=None):
    raise RuntimeError(f"gizli ayrıntı: {path}")


@pytest.fixture
def client():
    store._items.clear()
    return TestClient(app)


@pytest.fixture
def tmpbase(monkeypatch, tmp_path):
    """Uç noktanın geçici dizinlerini izlenebilir bir köke yönlendir."""
    base = tmp_path / "tmpbase"
    base.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(base))
    return base


@pytest.fixture
def no_recognition(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("tanıma çağrılmamalıydı")

    monkeypatch.setattr(services, "recognize_step_isolated", _boom)


def _assert_no_path(detail: str, base) -> None:
    assert str(base) not in detail
    assert "upload.step" not in detail and "step-import-" not in detail


# ── Süreç açan testler ───────────────────────────────────────────────────────


def test_200_temp_silinir_dosya_adi_ve_depo(client, monkeypatch, tmpbase):
    monkeypatch.setattr(services, "recognize_step", fake_ok)
    r = client.post("/api/import/step", content=STEP, headers={**HDR, "X-Filename": "../../etc/passwd"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "RECOGNIZED"
    assert body["source"]["filename"] == "passwd"
    assert body["_existed"] is True
    assert body["_path"].startswith(str(tmpbase))
    assert not os.path.exists(body["_path"])
    assert list(tmpbase.iterdir()) == []
    assert list(store._items.keys()) == []


@pytest.mark.parametrize("fake, code", [(fake_rejected, 200), (fake_blocked, 503)])
def test_rejected_200_blocked_503(client, monkeypatch, fake, code):
    monkeypatch.setattr(services, "recognize_step", fake)
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == code
    if code == 200:
        assert r.json()["status"] == "REJECTED"


def test_504_zaman_asimi_sunucu_ayakta(client, monkeypatch, tmpbase):
    monkeypatch.setattr(services, "recognize_step", fake_slow)
    monkeypatch.setattr(services, "STEP_RECOGNITION_TIMEOUT_S", 1.5)
    t0 = time.monotonic()
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 504
    assert time.monotonic() - t0 < 30
    _assert_no_path(r.json()["detail"], tmpbase)
    assert multiprocessing.active_children() == []  # süreç öldürüldü
    assert list(tmpbase.iterdir()) == []
    assert main._step_slots.acquire(blocking=False)  # slot geri verildi
    main._step_slots.release()

    monkeypatch.setattr(services, "recognize_step", fake_ok)
    monkeypatch.setattr(services, "STEP_RECOGNITION_TIMEOUT_S", 60.0)
    r2 = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r2.status_code == 200 and r2.json()["status"] == "RECOGNIZED"


@pytest.mark.parametrize("fake", [fake_crash, fake_raises])
def test_surec_coker_temiz_500(client, monkeypatch, tmpbase, fake):
    monkeypatch.setattr(services, "recognize_step", fake)
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 500
    detail = r.json()["detail"]
    _assert_no_path(detail, tmpbase)
    assert "gizli" not in detail and "RuntimeError" not in detail
    assert list(tmpbase.iterdir()) == []
    assert multiprocessing.active_children() == []


# ── Süreç açmayan testler ────────────────────────────────────────────────────


def test_413(client, tmpbase, no_recognition):
    big = STEP + b"0" * (20 * 1024 * 1024)
    r = client.post("/api/import/step", content=big, headers=HDR)
    assert r.status_code == 413
    assert list(tmpbase.iterdir()) == []


def test_415(client, tmpbase, no_recognition):
    r = client.post("/api/import/step", content=b"bu bir step degil", headers=HDR)
    assert r.status_code == 415
    # Başlık ilk 4 KB'ta yoksa büyük gövde de 415 (akışta erken kesilir)
    r = client.post("/api/import/step", content=b"x" * 5000 + STEP, headers=HDR)
    assert r.status_code == 415
    assert list(tmpbase.iterdir()) == []


def test_503_tanıyıcı_yok(client, monkeypatch):
    monkeypatch.setattr(services, "recognize_step", None)
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 503


def test_429_eszamanli_sinir(client, tmpbase, no_recognition):
    held = 0
    try:
        while main._step_slots.acquire(blocking=False):
            held += 1
        assert held == main.STEP_MAX_CONCURRENT == 2
        r = client.post("/api/import/step", content=STEP, headers=HDR)
        assert r.status_code == 429
        assert r.headers.get("retry-after")
        assert list(tmpbase.iterdir()) == []
    finally:
        for _ in range(held):
            main._step_slots.release()


def test_slot_tanima_suresince_tutulur_ve_hata_sonrasi_birakilir(client, monkeypatch, tmpbase):
    seen = {}

    def _isolated(path, filename=None):
        seen["thread"] = threading.current_thread() is not threading.main_thread()
        got = [main._step_slots.acquire(blocking=False) for _ in range(2)]
        for ok in got:
            if ok:
                main._step_slots.release()
        seen["free_during"] = got
        raise services.StepRecognitionTimeout()

    monkeypatch.setattr(services, "recognize_step_isolated", _isolated)
    r = client.post("/api/import/step", content=STEP, headers=HDR)
    assert r.status_code == 504
    assert seen["thread"] is True  # olay döngüsü dışında (threadpool)
    # 2 slottan biri bu istekte tutuluyor; yalnız biri boş
    assert seen["free_during"] == [True, False]
    both = [main._step_slots.acquire(blocking=False) for _ in range(2)]
    try:
        assert both == [True, True]
    finally:
        for ok in both:
            if ok:
                main._step_slots.release()
    assert list(tmpbase.iterdir()) == []


def test_safe_filename_kodlanmis_yol():
    assert main._safe_filename("..%2F..%2Fetc%2Fpasswd") == "passwd"
    assert main._safe_filename("..\\..\\x.step") == "x.step"
    assert main._safe_filename("") is None
