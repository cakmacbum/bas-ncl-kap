"""Execute T06 against the in-process public FastAPI application."""
from __future__ import annotations
import json
import uuid
from pathlib import Path
from fastapi.testclient import TestClient
from tools.campaign.tur2.t06_sahip_izolasyonu.cases import CASES, ENDPOINTS
from tools.campaign.bases import vertical_leg_tank

A = str(uuid.uuid5(uuid.NAMESPACE_URL, "t06-owner-a"))
B = str(uuid.uuid5(uuid.NAMESPACE_URL, "t06-owner-b"))
OUT = Path(__file__).with_name("results.json")


def main() -> None:
    from apps.api import _bootstrap  # noqa: F401
    from apps.api.main import app
    from apps.api.store import store
    store._items.clear()
    results = []
    with TestClient(app, raise_server_exceptions=False) as client:
        project = vertical_leg_tank()
        created = client.post("/api/projects", json=project, headers={"X-Client-Id": A})
        if created.status_code != 201:
            raise RuntimeError(f"Fixture project creation failed: {created.status_code} {created.text}")
        pid = created.json()["id"]
        changed = vertical_leg_tank()
        changed["project_name"] = "T06 unauthorized replacement"
        routes = {
            "read": ("GET", f"/api/projects/{pid}", None),
            "update": ("PUT", f"/api/projects/{pid}", changed),
            "calculate": ("POST", f"/api/projects/{pid}/calculate", None),
            "report": ("GET", f"/api/projects/{pid}/report.html", None),
            "step": ("GET", f"/api/projects/{pid}/model.step", None),
            "stl": ("GET", f"/api/projects/{pid}/model.stl", None),
        }
        for case in CASES:
            kind = case["kind"]
            headers = {"X-Client-Id": B}
            body = None
            if kind in routes:
                method, path, body = routes[kind]
                response = client.request(method, path, headers=headers, json=body)
            elif kind == "create":
                response = created
            elif kind == "list":
                response = client.get("/api/projects", headers={"X-Client-Id": A})
            elif kind == "other-list":
                response = client.get("/api/projects", headers=headers)
            elif kind == "owner-read":
                response = client.get(f"/api/projects/{pid}", headers={"X-Client-Id": A})
            elif kind == "owner-update":
                response = client.put(f"/api/projects/{pid}", json=project, headers={"X-Client-Id": A})
            elif kind == "owner-calculate":
                response = client.post(f"/api/projects/{pid}/calculate", headers={"X-Client-Id": A})
            elif kind == "bad-header":
                h = {} if not case["header"] else {"X-Client-Id": A.upper() if case["header"] == "OWNER_UPPER" else case["header"]}
                response = client.get("/api/projects", headers=h)
            elif kind == "bad-route-header":
                path = case["path"].replace("{id}", pid)
                body = project if case["method"] in {"POST", "PUT"} and path.endswith(("/projects", pid)) else None
                header = A.upper() if case["header"] == "OWNER_UPPER" else case["header"]
                response = client.request(case["method"], path, headers={"X-Client-Id": header}, json=body)
            elif kind == "health":
                response = client.get("/api/health")
            elif kind == "agent-no-header":
                response = client.post("/api/agent/geometry/interpret", json={})
            else:
                response = client.post("/api/import/step", content=b"", headers={})
            observed = response.status_code
            ok = observed == case["expected"]
            if kind == "other-list" and observed == 200:
                ok = ok and all(row.get("id") != pid for row in response.json())
            if kind == "update" and observed == 404:
                after = client.get(f"/api/projects/{pid}", headers={"X-Client-Id": A})
                ok = ok and after.status_code == 200 and after.json().get("project_name") == project["project_name"]
            if kind == "owner-read" and observed == 200:
                ok = ok and response.json().get("project_name") == project["project_name"]
            actual_header = case.get("header", "X-Client-Id present")
            if actual_header == "OWNER_UPPER":
                actual_header = A.upper()
            results.append({"vaka": case["id"], "girdi": {"yontem": kind, "proje_id": pid, "istemci": "B" if kind.startswith("other-") or kind in routes else "A", "başlık": actual_header}, "beklenen": {"http_status": case["expected"], "değişmez": case.get("invariant")}, "gözlenen": {"http_status": observed, "body": response.text[:500]}, "sonuç": "GEÇTİ" if ok else "BULGU", "önem": ("KRİTİK" if kind in routes else "ORTA") if not ok else None, "yön": "emniyetli (aynı UUID sahibine normalleşiyor)" if not ok and kind.startswith("uppercase") else ("B->A" if kind in routes else None), "dosya_satır": "apps/api/auth.py:118" if not ok and kind.startswith("uppercase") else None})
    OUT.write_text(json.dumps({"endpoints": ENDPOINTS, "vaka_sonuclari": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"T06: {len(results)} vaka; GEÇTİ={sum(x['sonuç']=='GEÇTİ' for x in results)}; BULGU={sum(x['sonuç']=='BULGU' for x in results)}; {OUT}")
if __name__ == "__main__":
    main()
