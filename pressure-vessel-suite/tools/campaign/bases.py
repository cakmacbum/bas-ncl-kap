"""Reusable valid vessel project templates."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json

_FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "vessel_project_five_component.json"

def _merge(dst, src):
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _merge(dst[key], value)
        else:
            dst[key] = deepcopy(value)
    return dst

def _base(name, orientation, supports, **overrides):
    p = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    p.update(project_number=f"CAMPAIGN-{name.upper()}", project_name=name, orientation=orientation)
    # Templates are intentionally single-vessel defaults; remove the fixture's
    # optional multi-component ordering so list overrides remain valid.
    p["component_sequence"] = []
    p["cones"] = []
    p["supports"] = supports
    return _merge(p, overrides)

def vertical_leg_tank(**overrides):
    legs = [{"support_id": f"LEG-{i}", "host_component_id": "SHELL-01", "type": "leg",
             "location_mm": 500 + (i-1)*300, "width_mm": 100, "height_mm": 600,
             "material_id": "M1", "leg_count": 4, "leg_diameter_mm": 100,
             "leg_thickness_mm": 8, "leg_pad_length_mm": 250, "leg_pad_width_mm": 180,
             "leg_pad_thickness_mm": 12, "leg_base_plate_length_mm": 250,
             "leg_base_plate_width_mm": 200, "leg_base_plate_thickness_mm": 16,
             "leg_anchor_bolt_count": 4, "leg_anchor_bolt_diameter_mm": 20,
             "leg_anchor_circle_diameter_mm": 150, "leg_weld_size_mm": 6,
             "ucs66_curve_group": "A"} for i in range(1, 5)]
    project = _base("vertical-leg", "vertical", legs, **overrides)
    project.setdefault("nozzles", []).append({"tag": "N1", "host_component_id": "SHELL-01",
        "axial_position": 1000, "outside_diameter": 60.3, "inside_diameter": 52.5,
        "neck_thickness": 3.9, "material_id": "M1", "reinforcement_pad": False})
    return project

def horizontal_saddle_tank(**overrides):
    supports = [{"support_id": f"SAD-{i}", "host_component_id": "SHELL-01", "type": "saddle",
                 "location_mm": x, "width_mm": 250, "height_mm": 400, "material_id": "M1"}
                for i, x in enumerate((400, 1600), 1)]
    return _base("horizontal-saddle", "horizontal", supports, **overrides)

def skirt_column(**overrides):
    support = [{"support_id": "SKIRT-01", "host_component_id": "SHELL-01", "type": "skirt",
                "location_mm": 0, "width_mm": 8, "height_mm": 1200, "diameter_mm": 1000,
                "thickness_mm": 8, "material_id": "M1", "skirt_allowable_compressive_MPa": 100}]
    return _base("skirt-column", "vertical", support, **overrides)

def with_code(project: dict, code: str) -> dict:
    result = deepcopy(project)
    if code not in ("ASME VIII-1", "EN 13445"):
        raise ValueError(f"Unsupported code: {code}")
    result["calculation_code"] = code
    result["code_edition"] = "2025" if code == "ASME VIII-1" else "2021+A1:2023"
    return result
