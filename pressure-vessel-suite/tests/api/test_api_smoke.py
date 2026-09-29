"""FastAPI backend smoke testleri — proje oluştur → hesapla → rapor."""

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.store import store


@pytest.fixture
def client():
    store._items.clear()
    return TestClient(app)


SAMPLE = {
    "project_number": "API-001",
    "project_name": "API Test",
    "customer": "Demo",
    "calculation_code": "ASME VIII-1",
    "code_edition": "2025",
    "design_conditions": {
        "operating_pressure": 1.0, "design_pressure": 1.2,
        "maximum_allowable_pressure_ps": 1.5, "operating_temperature": 150,
        "design_temperature": 200, "minimum_design_temperature": -10,
        "corrosion_allowance_internal": 2.0,
    },
    "shell_sections": [{
        "section_id": "SHELL-01", "inside_diameter": 1000, "tangent_length": 2000,
        "nominal_thickness": 12, "material_id": "M1", "weld_joint_id": "WJ-01",
        "internal_corrosion_allowance": 2.0, "mill_tolerance": 12.5,
    }],
    "heads": [
        {"head_id": "HL", "type": "elliptical", "inside_diameter": 1000,
         "nominal_thickness": 12, "material_id": "M1", "internal_corrosion_allowance": 2.0},
        {"head_id": "HR", "type": "elliptical", "inside_diameter": 1000,
         "nominal_thickness": 12, "material_id": "M1", "internal_corrosion_allowance": 2.0},
    ],
    "nozzles": [{
        "tag": "N1", "host_component_id": "SHELL-01", "axial_position": 800,
        "circumferential_angle": 90, "outside_diameter": 168.3, "inside_diameter": 154.1,
        "neck_thickness": 7.1, "material_id": "M1",
    }],
    "materials": [{
        "material_id": "M1", "standard_pack": "ASME II-D 2025",
        "material_designation": "SA-516 Gr.70", "product_form": "plate",
        "temperature": 200, "allowable_stress": 138, "yield_strength": 260,
        "tensile_strength": 485, "source_reference": "ASME II-D", "density": 7850,
    }],
    "welds": [{
        "joint_id": "WJ-01", "joint_type": "longitudinal", "weld_category": "A",
        "joint_efficiency": 1.0, "nde_method": "RT-1", "nde_extent": "100%",
    }],
}


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_calculate_report_flow(client):
    # Oluştur
    r = client.post("/api/projects", json=SAMPLE)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert len(r.json()["input_file_hash"]) == 64

    # Oku
    assert client.get(f"/api/projects/{pid}").status_code == 200

    # Hesapla
    calc = client.post(f"/api/projects/{pid}/calculate")
    assert calc.status_code == 200
    data = calc.json()
    assert data["global_mawp_mpa"] is not None
    types = {x["calculation_type"] for x in data["results"]}
    assert {"thickness", "mawp", "hydrotest", "nozzle_reinforcement",
            "weld_validation", "clash_check"}.issubset(types)
    assert data["volume_mass"]["inner_volume_liters"] > 0

    # Rapor
    rep = client.get(f"/api/projects/{pid}/report.html")
    assert rep.status_code == 200
    assert "BASINÇLI KAP HESAP RAPORU" in rep.text


def test_five_component_chain_survives_api_save_open_roundtrip(client):
    """The complete VesselProject fixture survives API list/load unchanged."""
    fixture_path = Path(__file__).parents[1] / "fixtures" / "vessel_project_five_component.json"
    project = json.loads(fixture_path.read_text(encoding="utf-8"))
    project["project_number"] = "API-CHAIN-001"

    created = client.post("/api/projects", json=project)
    assert created.status_code == 201
    pid = created.json()["id"]
    listed = client.get("/api/projects")
    assert listed.status_code == 200
    summary = next(item for item in listed.json() if item["id"] == pid)
    assert summary["project_number"] == "API-CHAIN-001"
    opened = client.get(f"/api/projects/{pid}")
    assert opened.status_code == 200
    saved = opened.json()
    assert [(x["component_type"], x["component_id"]) for x in saved["component_sequence"]] == [
        ("head", "HEAD-L"), ("shell", "SHELL-01"), ("cone", "CONE-01"),
        ("shell", "SHELL-02"), ("head", "HEAD-R"),
    ]
    assert {x["material_id"] for x in saved["materials"]} == {"M1", "M2"}
    assert {x["joint_id"] for x in saved["welds"]} == {"WJ-01", "WJ-02"}
    assert [x["material_id"] for x in saved["shell_sections"]] == ["M1", "M2"]
    assert [x["weld_joint_id"] for x in saved["shell_sections"]] == ["WJ-01", "WJ-02"]
    assert client.post(f"/api/projects/{pid}/calculate").status_code == 200
    report = client.get(f"/api/projects/{pid}/report.html")
    assert report.status_code == 200
    for component_id in ("HEAD-L", "SHELL-01", "CONE-01", "SHELL-02", "HEAD-R"):
        assert component_id in report.text
    assert "24." in report.text and "25." in report.text
    assert "Applicability" in report.text


def test_en_calculation_code_selects_en_engine(client):
    """EN isteği API'de ASME'ye sessizce düşmemelidir."""
    import copy

    sample_en = copy.deepcopy(SAMPLE)
    sample_en["project_number"] = "API-EN-001"
    sample_en["calculation_code"] = "EN 13445"
    sample_en["code_edition"] = "2021+A1:2023"

    created = client.post("/api/projects", json=sample_en)
    assert created.status_code == 201
    pid = created.json()["id"]

    calculated = client.post(f"/api/projects/{pid}/calculate")

    assert calculated.status_code == 200
    assert calculated.json()["code"] == "EN 13445"


def test_404_unknown_project(client):
    assert client.post("/api/projects/nope/calculate").status_code == 404


def test_stl_endpoint(client):
    """3D görüntüleyici için STL mesh üretilir (CadQuery kurulu ortamda)."""
    from apps.api import services

    pid = client.post("/api/projects", json=SAMPLE).json()["id"]
    r = client.get(f"/api/projects/{pid}/model.stl")
    if not services.CADQUERY_AVAILABLE:
        assert r.status_code == 503
        return
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 1000


def test_calculate_payload_contains_verification(client):
    """Yayın kapısı yanıtta görünür (bilgilendirici); hesap sonucu değişmez."""
    pid = client.post("/api/projects", json=SAMPLE).json()["id"]
    body = client.post(f"/api/projects/{pid}/calculate").json()
    ver = body["verification"]
    assert set(ver) >= {"case_name", "passed", "checks", "errors"}
    assert len(ver["checks"]) == len(body["results"])
    # passed, hata listesiyle tutarlı olmalı
    assert ver["passed"] is (not ver["errors"])
    assert all("notices" in r for r in body["results"])
