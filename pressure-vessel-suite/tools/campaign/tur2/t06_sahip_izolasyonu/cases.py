"""T06 owner-isolation case catalogue and endpoint inventory."""
from __future__ import annotations

# All HTTP routes declared in apps/api/main.py, including public and non-project routes.
ENDPOINTS = [
    {"method": "GET", "path": "/api/health", "owner_required": False},
    {"method": "POST", "path": "/api/agent/geometry/interpret", "owner_required": True},
    {"method": "GET", "path": "/api/projects", "owner_required": True},
    {"method": "POST", "path": "/api/projects", "owner_required": True},
    {"method": "GET", "path": "/api/projects/{project_id}", "owner_required": True},
    {"method": "PUT", "path": "/api/projects/{project_id}", "owner_required": True},
    {"method": "POST", "path": "/api/projects/{project_id}/calculate", "owner_required": True},
    {"method": "GET", "path": "/api/projects/{project_id}/report.html", "owner_required": True},
    {"method": "GET", "path": "/api/projects/{project_id}/model.step", "owner_required": True},
    {"method": "GET", "path": "/api/projects/{project_id}/model.stl", "owner_required": True},
    {"method": "POST", "path": "/api/import/step", "owner_required": True},
]

CASES = [
    {"id": "owner-create", "kind": "create", "expected": 201},
    {"id": "owner-list", "kind": "list", "expected": 200},
    {"id": "other-list", "kind": "other-list", "expected": 200, "invariant": "created id absent"},
    {"id": "other-read", "kind": "read", "expected": 404},
    {"id": "other-update", "kind": "update", "expected": 404, "invariant": "original unchanged"},
    {"id": "other-calculate", "kind": "calculate", "expected": 404},
    {"id": "other-report", "kind": "report", "expected": 404},
    {"id": "other-step", "kind": "step", "expected": 404},
    {"id": "other-stl", "kind": "stl", "expected": 404},
    {"id": "owner-read", "kind": "owner-read", "expected": 200},
    {"id": "owner-update", "kind": "owner-update", "expected": 200},
    {"id": "owner-calculate", "kind": "owner-calculate", "expected": 200},
    {"id": "invalid-uuid", "kind": "bad-header", "header": "not-a-uuid", "expected": 400},
    {"id": "uppercase-uuid", "kind": "bad-header", "header": "OWNER_UPPER", "expected": 400},
    {"id": "empty-header", "kind": "bad-header", "header": "", "expected": 400},
    {"id": "uppercase-list", "kind": "bad-route-header", "method": "GET", "path": "/api/projects", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-create", "kind": "bad-route-header", "method": "POST", "path": "/api/projects", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-read", "kind": "bad-route-header", "method": "GET", "path": "/api/projects/{id}", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-update", "kind": "bad-route-header", "method": "PUT", "path": "/api/projects/{id}", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-calculate", "kind": "bad-route-header", "method": "POST", "path": "/api/projects/{id}/calculate", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-report", "kind": "bad-route-header", "method": "GET", "path": "/api/projects/{id}/report.html", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-step", "kind": "bad-route-header", "method": "GET", "path": "/api/projects/{id}/model.step", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-stl", "kind": "bad-route-header", "method": "GET", "path": "/api/projects/{id}/model.stl", "header": "OWNER_UPPER", "expected": 400},
    {"id": "uppercase-import", "kind": "bad-route-header", "method": "POST", "path": "/api/import/step", "header": "OWNER_UPPER", "expected": 400},
    {"id": "health-no-header", "kind": "health", "expected": 200},
    {"id": "agent-missing-header", "kind": "agent-no-header", "expected": 400},
    {"id": "import-missing-header", "kind": "import-no-header", "expected": 400},
]
