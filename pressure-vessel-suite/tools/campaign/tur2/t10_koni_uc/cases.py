"""Cone junction boundary cases; numeric code equations are deliberately absent."""
from copy import deepcopy

from tools.campaign.examples import example_junction_check


def _case(angle: float, has_knuckle: bool, end: str = "large", mismatch: bool = False) -> dict:
    project = example_junction_check()
    project["project_name"] = f"T10-{angle:g}-{end}-{'K' if has_knuckle else 'N'}"
    cone = project["cones"][0]
    cone["half_apex_angle"] = angle
    junction = project["junctions"][0]
    junction["cone_end"] = end
    junction["knuckle_radius_mm"] = 75 if has_knuckle else None
    if mismatch:
        junction["large_end_diameter"] = 990
    # The baseline junction adjoins SHELL-01 at its 1000 mm large end.
    expected = "BLOCKED" if angle > 30 and not has_knuckle or mismatch or end != "large" else "OUT_OF_SCOPE"
    return {"id": f"A{angle:g}-{end}-{'K' if has_knuckle else 'N'}{'-M' if mismatch else ''}",
            "angle_deg": angle, "knuckle_present": has_knuckle, "end": end,
            "mismatch": mismatch, "project": deepcopy(project), "expected": expected,
            "basis": "Topology/input-envelope expectation only; no App 1-5/1-8 numeric oracle."}


def all_cases() -> list[dict]:
    cases = []
    # Sweep 5..75 degrees in 5 degree increments, paired for knuckle presence.
    for angle in range(5, 76, 5):
        for has_knuckle in (False, True):
            cases.append(_case(float(angle), has_knuckle))
    # Verify the >30 boundary, explicit end identity, and inconsistent diameter input.
    cases.extend([_case(30, False), _case(30.1, False), _case(30.1, True),
                  _case(75, True, "small"), _case(15, True, "large", True)])
    return cases
