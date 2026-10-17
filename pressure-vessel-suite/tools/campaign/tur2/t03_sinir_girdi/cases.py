"""Deterministic invalid-project cases for the public API boundary."""
from __future__ import annotations

from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank


def _set_path(project: dict, path: str, value) -> None:
    parts = path.split(".")
    target = project
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last = parts[-1]
    if last.isdigit():
        target[int(last)] = value
    else:
        target[last] = value


def _delete_path(project: dict, path: str) -> None:
    parts = path.split(".")
    target = project
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    del target[parts[-1]]


def build_cases() -> list[dict]:
    """Return unique cases with a single intentional input defect each."""
    cases: list[dict] = []

    def add(case_id: str, path: str, value, defect: str = "invalid") -> None:
        project = deepcopy(vertical_leg_tank())
        if defect == "missing":
            _delete_path(project, path)
        elif defect == "empty":
            _set_path(project, path, [])
        else:
            _set_path(project, path, value)
        project["project_number"] = f"T03-{case_id}"
        cases.append({"id": case_id, "input": {"path": path, "value": "<missing>" if defect == "missing" else value},
                      "project": project, "defect": defect})

    # Pressure limits and non-finite / non-numeric JSON values.
    for i, val in enumerate([-1, 0, 1e9, "1.2", "bad", None, float("nan"), float("inf")]):
        add(f"pressure-design-{i+1}", "design_conditions.design_pressure", val)
    for i, val in enumerate([-1, 0, 1e9, "1.0", "bad", None, float("nan")]):
        add(f"pressure-operating-{i+1}", "design_conditions.operating_pressure", val)
    for i, val in enumerate([-1, 0, 1e9, "200", "bad", None, float("nan")]):
        add(f"temperature-{i+1}", "design_conditions.design_temperature", val)
    # Geometric thickness / diameter extremes and type coercion.
    for i, val in enumerate([-12, 0, 1e9, "12", "bad", None, float("nan")]):
        add(f"shell-thickness-{i+1}", "shell_sections.0.nominal_thickness", val)
    for i, val in enumerate([-1000, 0, 1e9, "1000", "bad", None]):
        add(f"shell-diameter-{i+1}", "shell_sections.0.inside_diameter", val)
    # Required fields, enums, structural shape, and component references.
    for i, (path, value, defect) in enumerate([
        ("project_number", None, "missing"), ("calculation_code", None, "missing"),
        ("code_edition", None, "missing"), ("design_conditions", None, "missing"),
        ("design_conditions.design_pressure", None, "missing"),
        ("design_conditions.operating_pressure", None, "missing"),
        ("shell_sections", [], "empty"), ("heads", [], "empty"),
        ("materials", [], "empty"), ("supports", [], "empty"),
        ("calculation_code", "NOT-A-CODE", "invalid"),
        ("orientation", "diagonal", "invalid"),
        ("diameter_relation", "coupled-ish", "invalid"),
        ("design_conditions", "not-an-object", "invalid"),
        ("shell_sections", "not-a-list", "invalid"),
        ("shell_sections.0.material_id", "UNKNOWN", "invalid"),
        ("shell_sections.0.section_id", "", "invalid"),
        ("shell_sections.0.nominal_thickness", {"value": 12}, "invalid"),
        ("design_conditions.vacuum_condition", "false", "invalid"),
        ("design_conditions.external_pressure", -1, "invalid"),
        ("design_conditions.corrosion_allowance_internal", -1, "invalid"),
        ("design_conditions.fluid_density_kg_m3", -1, "invalid"),
    ], 1):
        add(f"shape-enum-{i:02d}", path, value, defect)
    return cases
