"""API testleri için varsayılanlar: auth kapalı, geometri ajanı açık (test_auth.py bunları ezer)."""

import pytest


@pytest.fixture(autouse=True)
def _api_test_env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("GEOMETRY_AGENT_ENABLED", "true")
