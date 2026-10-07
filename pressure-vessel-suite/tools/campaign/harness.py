"""Run vessel projects through the public FastAPI calculation route."""
from __future__ import annotations

from fastapi.testclient import TestClient


def run_case(project: dict) -> dict:
    from apps.api import _bootstrap  # noqa: F401
    from apps.api.main import app
    try:
        with TestClient(app) as client:
            created = client.post("/api/projects", json=project)
            if created.status_code != 201:
                return {"ok": False, "http_status": created.status_code, "payload": None,
                        "error": created.text}
            project_id = created.json()["id"]
            response = client.post(f"/api/projects/{project_id}/calculate")
            if response.status_code != 200:
                return {"ok": False, "http_status": response.status_code, "payload": None,
                        "error": response.text}
            payload = response.json()
            return {"ok": not bool(payload.get("errors")), "http_status": response.status_code,
                    "payload": payload, "error": None if not payload.get("errors") else str(payload["errors"])}
    except Exception as exc:
        return {"ok": False, "http_status": 500, "payload": None,
                "error": f"{type(exc).__name__}: {exc}"}


def find_results(payload: dict, *, component_id: str | None = None,
                 calculation_type: str | None = None, clause_prefix: str | None = None) -> list[dict]:
    rows = payload.get("results", [])
    return [r for r in rows if
            (component_id is None or r.get("component_id") == component_id) and
            (calculation_type is None or r.get("calculation_type") == calculation_type) and
            (clause_prefix is None or str(r.get("clause_reference", "")).startswith(clause_prefix))]


def value_of(result: dict, name: str) -> float | None:
    for item in result.get("intermediate_values", []):
        if item.get("name") == name and item.get("value") is not None:
            return float(item["value"])
    final = result.get("final_result")
    if isinstance(final, dict):
        value = final.get(name)
        return float(value) if isinstance(value, (int, float)) else None
    if name in {"final_result", "value"} and isinstance(final, (int, float)):
        return float(final)
    return None
