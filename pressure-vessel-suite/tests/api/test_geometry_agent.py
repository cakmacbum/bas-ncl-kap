"""Safe structured-output contract for the basic geometry assistant."""

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api import geometry_agent
from apps.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("GEOMETRY_AGENT_API_KEY", "test-key")
    monkeypatch.setenv("GEOMETRY_AGENT_MODEL", "test/model")


def payload(instruction="Çapı 1200 mm, boyu 2.5 m olsun"):
    return {
        "instruction": instruction,
        "context": {
            "active_shell_id": "SHELL-02",
            "shell_ids": ["SHELL-01", "SHELL-02"],
            "heads": [
                {"head_id": "HEAD-L", "side": "left"},
                {"head_id": "HEAD-R", "side": "right"},
            ],
            "diameter_relation": "linked",
        },
    }


def provider_response(content):
    return {"choices": [{"message": {"content": json.dumps(content)}}]}


def test_unconfigured_agent_is_explicit_and_non_mutating(client, monkeypatch):
    monkeypatch.delenv("GEOMETRY_AGENT_API_KEY", raising=False)
    monkeypatch.delenv("GEOMETRY_AGENT_MODEL", raising=False)
    response = client.post("/api/agent/geometry/interpret", json=payload())
    assert response.status_code == 503
    assert "yapılandırılmadı" in response.json()["detail"]


def test_structured_basic_geometry_suggestion(client, configured, monkeypatch):
    captured = {}

    def fake_call(body):
        captured.update(body)
        return provider_response({
            "summary": "Aktif gövde ölçüleri güncellenecek.",
            "changes": [
                {"target_type": "shell", "target_id": "SHELL-02", "field": "inside_diameter", "value": 1200},
                {"target_type": "shell", "target_id": "SHELL-02", "field": "tangent_length", "value": 2500},
            ],
            "warnings": [],
        })

    monkeypatch.setattr(geometry_agent, "_call_chat_completion", fake_call)
    response = client.post("/api/agent/geometry/interpret", json=payload())
    assert response.status_code == 200
    assert [item["field"] for item in response.json()["changes"]] == ["inside_diameter", "tangent_length"]
    assert captured["model"] == "test/model"
    assert captured["temperature"] == 0
    assert captured["response_format"]["type"] == "json_schema"
    assert "Never calculate, estimate" in captured["messages"][0]["content"]


def test_non_active_shell_change_is_removed(client, configured, monkeypatch):
    monkeypatch.setattr(geometry_agent, "_call_chat_completion", lambda _body: provider_response({
        "summary": "Yanlış hedef",
        "changes": [
            {"target_type": "shell", "target_id": "SHELL-01", "field": "inside_diameter", "value": 900},
        ],
        "warnings": [],
    }))
    response = client.post("/api/agent/geometry/interpret", json=payload())
    assert response.status_code == 200
    assert response.json()["changes"] == []
    assert "aktif gövde" in response.json()["warnings"][0]


def test_ambiguous_head_change_is_removed(client, configured, monkeypatch):
    monkeypatch.setattr(geometry_agent, "_call_chat_completion", lambda _body: provider_response({
        "summary": "Bombe tipi",
        "changes": [
            {"target_type": "head", "target_id": "HEAD-L", "field": "type", "value": "elliptical"},
        ],
        "warnings": [],
    }))
    response = client.post(
        "/api/agent/geometry/interpret",
        json=payload("Bombesi eliptik olsun"),
    )
    assert response.status_code == 200
    assert response.json()["changes"] == []
    assert "sol, sağ veya her iki" in response.json()["warnings"][0]


def test_explicit_left_head_change_is_allowed(client, configured, monkeypatch):
    monkeypatch.setattr(geometry_agent, "_call_chat_completion", lambda _body: provider_response({
        "summary": "Sol bombe",
        "changes": [
            {"target_type": "head", "target_id": "HEAD-L", "field": "type", "value": "torispherical"},
            {"target_type": "head", "target_id": "HEAD-L", "field": "nominal_thickness", "value": 14},
        ],
        "warnings": [],
    }))
    response = client.post(
        "/api/agent/geometry/interpret",
        json=payload("Sol bombe torisferik ve 14 mm olsun"),
    )
    assert response.status_code == 200
    assert len(response.json()["changes"]) == 2


def test_invalid_provider_schema_returns_bad_gateway(client, configured, monkeypatch):
    monkeypatch.setattr(geometry_agent, "_call_chat_completion", lambda _body: provider_response({
        "summary": "Kapsam dışı",
        "changes": [
            {"target_type": "shell", "target_id": "SHELL-02", "field": "material_id", "value": "M2"},
        ],
        "warnings": [],
    }))
    response = client.post("/api/agent/geometry/interpret", json=payload())
    assert response.status_code == 502
    assert "şemasına uymuyor" in response.json()["detail"]


def test_invalid_active_shell_context_is_rejected(client):
    bad = payload()
    bad["context"]["active_shell_id"] = "UNKNOWN"
    response = client.post("/api/agent/geometry/interpret", json=bad)
    assert response.status_code == 422
