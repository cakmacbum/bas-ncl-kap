"""Clean-room UG-27 arithmetic; no suite calculation implementation imported."""
from __future__ import annotations


def calculate(project: dict) -> dict[str, float]:
    shell = project["shell_sections"][0]
    mat = next((m for m in project["materials"] if m["material_id"] == shell["material_id"]), None)
    if mat is None:
        return {}
    t_nom = float(shell["nominal_thickness"])
    mill = float(shell.get("mill_tolerance", 0)) / 100.0
    ca_i = float(shell.get("internal_corrosion_allowance", 0))
    ca_o = float(shell.get("external_corrosion_allowance", 0))
    if shell.get("inside_diameter") is not None:
        ri = float(shell["inside_diameter"]) / 2 + ca_i
    else:
        ri = float(shell["outside_diameter"]) / 2 - t_nom * (1 - mill) + ca_o
    pressure = float(project["design_conditions"]["design_pressure"])
    stress = float(mat["allowable_stress"])
    weld = next((w for w in project.get("welds", []) if w["joint_id"] == shell.get("weld_joint_id")), None)
    efficiency = float(weld["joint_efficiency"]) if weld else 1.0
    denominator = stress * efficiency - .6 * pressure
    if pressure <= 0 or ri <= 0 or denominator <= 0:
        return {}
    required = pressure * ri / denominator
    net_delivery = t_nom * (1 - mill) - ca_i - ca_o
    mawp = (stress * efficiency * net_delivery) / (ri + .6 * net_delivery) if net_delivery > 0 else 0.0
    return {"required_thickness": required, "mawp": mawp, "used_radius": ri}
