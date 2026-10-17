"""Deterministic horizontal saddle campaign cases."""
from copy import deepcopy
from tools.campaign.examples import example_saddle_stress


def cases():
    rows = []
    index = 0
    # 2-support full-factorial sample; 3 supports are separately probed as scope.
    for count in (2, 3):
        for ratio in (0.05, 0.10, 0.20, 0.30):
            for angle in (120, 135, 150):
                for plate in (False, True):
                    for state in ("empty", "operating", "hydrotest"):
                        index += 1
                        p = example_saddle_stress()
                        shell = p["shell_sections"][0]
                        # A is the end distance from support center to tangent end.
                        shell["tangent_length"] = 4000
                        A = ratio * shell["tangent_length"]
                        spacing = shell["tangent_length"] - 2 * A
                        supports = []
                        positions = ([A, A + spacing] if count == 2 else
                                     [A, A + spacing / 2, A + spacing])
                        for n, x in enumerate(positions, 1):
                            s = deepcopy(p["supports"][0])
                            s.update(support_id=f"SAD-{n}", location_mm=x,
                                     contact_angle_deg=angle, saddle_stiffened=plate,
                                     wear_plate=plate, wear_plate_thickness_mm=10 if plate else 0,
                                     zick_K1=1.0, zick_K2=1.0, zick_K6=1.0, zick_K7=1.0)
                            supports.append(s)
                        p["supports"] = supports
                        p["project_number"] = f"T11-{index:03d}"
                        # An explicit load descriptor drives empty, liquid operating,
                        # or hydrotest service. Static head is represented by fluid level.
                        if state != "empty":
                            p["load_cases"] = [{"load_case_id": "T11-FILL",
                                "name": state, "load_type": "fluid_weight",
                                "fluid_density_kg_m3": 1000,
                                "fluid_level_mm": 2000 if state == "hydrotest" else 1600}]
                        else:
                            p["load_cases"] = []
                        rows.append((f"T11-{index:03d}", p, {
                            "saddles": count, "A_over_L": ratio, "contact_angle_deg": angle,
                            "wear_plate": plate, "state": state,
                            "A_mm": A, "L_mm": shell["tangent_length"]}))
    return rows
