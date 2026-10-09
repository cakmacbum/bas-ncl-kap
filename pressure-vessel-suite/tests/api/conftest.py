"""API testleri için varsayılanlar: auth kapalı, geometri ajanı açık (test_auth.py bunları ezer)."""

import pytest


@pytest.fixture(autouse=True)
def _api_test_env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.delenv("AUTH_MODE", raising=False)
    monkeypatch.setenv("GEOMETRY_AGENT_ENABLED", "true")


DEFAULT_CLIENT_ID = "00000000-0000-4000-8000-000000000001"


@pytest.fixture(autouse=True)
def _default_client_id(monkeypatch):
    """Mevcut testler başlıksız TestClient kullanır; varsayılan X-Client-Id ekle.
    (test_isolation başlığı client.headers.pop ile kaldırabilir.)"""
    from fastapi.testclient import TestClient

    orig = TestClient.__init__

    def init(self, *a, **k):
        orig(self, *a, **k)
        self.headers.setdefault("X-Client-Id", DEFAULT_CLIENT_ID)

    monkeypatch.setattr(TestClient, "__init__", init)
