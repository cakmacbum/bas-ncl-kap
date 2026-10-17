"""Scale and unit-system cases for the public project API."""
from __future__ import annotations

from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank


LENGTH_KEYS = {
    "inside_diameter", "outside_diameter", "tangent_length", "nominal_thickness",
    "internal_corrosion_allowance", "external_corrosion_allowance", "forming_thinning",
    "crown_radius", "knuckle_radius", "crown_depth", "straight_flange_length",
    "axial_position", "head_position_diameter", "neck_thickness", "inside_projection",
    "outside_projection", "corrosion_allowance", "reinforcement_pad_thickness",
    "reinforcement_pad_od", "large_diameter", "small_diameter", "length", "width",
    "height", "diameter", "thickness", "location_mm", "leg_diameter_mm",
    "leg_thickness_mm", "leg_pad_length_mm", "leg_pad_width_mm", "leg_pad_thickness_mm",
    "leg_base_plate_length_mm", "leg_base_plate_width_mm", "leg_base_plate_thickness_mm",
    "leg_anchor_bolt_diameter_mm", "leg_anchor_circle_diameter_mm", "leg_weld_size_mm",
}


def _scale_lengths(value, factor: float):
    if isinstance(value, dict):
        return {key: (_scale_lengths(item, factor) if isinstance(item, (dict, list)) else
                      item * factor if key.endswith("_mm") and isinstance(item, (int, float)) or
                      key in LENGTH_KEYS and isinstance(item, (int, float)) else item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [_scale_lengths(item, factor) for item in value]
    return value


def variants():
    base = vertical_leg_tank()
    yield "BASE", deepcopy(base), {"scale": 1.0, "unit_system": "SI"}
    for index, factor in enumerate((0.25, 0.5, 0.75, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0), 1):
        project = _scale_lengths(deepcopy(base), factor)
        project["project_number"] += f"-S{index:02d}"
        project["project_name"] += f" scale {factor}"
        yield f"SCALE-{index:02d}", project, {"scale": factor, "unit_system": "SI"}
    for index, factor in enumerate((0.25, 0.5, 0.75, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0), 1):
        project = _scale_lengths(deepcopy(base), factor)
        project["project_number"] += f"-I{index:02d}"
        project["project_name"] += f" imperial-converted-{index}"
        project["unit_system"] = "Imperial"
        project = _convert_si_to_imperial(project)
        yield f"IMPERIAL-{index:02d}", project, {"scale": 1.0, "unit_system": "Imperial",
                                                   "conversion": "mm→in, MPa→psi"}


def _convert_si_to_imperial(value, key=""):
    if isinstance(value, dict):
        converted = {}
        for child_key, child in value.items():
            if child_key in {"design_pressure", "operating_pressure", "maximum_allowable_pressure_ps",
                             "external_pressure", "hydrotest_pressure"} and isinstance(child, (int, float)):
                converted[child_key] = child * 145.0377377
            elif isinstance(child, (dict, list)):
                converted[child_key] = _convert_si_to_imperial(child, child_key)
            elif (child_key.endswith("_mm") or child_key in LENGTH_KEYS) and isinstance(child, (int, float)):
                converted[child_key] = child / 25.4
            else:
                converted[child_key] = child
        return converted
    if isinstance(value, list):
        return [_convert_si_to_imperial(item) for item in value]
    return value
