"""Extreme torispherical head probes with an independent Appendix 1-4 M oracle."""
from __future__ import annotations
import math
from tools.campaign.bases import vertical_leg_tank, with_code


def cases():
    # r/D deliberately spans the requested 3–20%; L is independently varied.
    specs = [
        ("r003", .03, .9, 20), ("r030", .03, .9, 20),
        ("r050", .05, .5, 20), ("r120", .12, 1.2, 20),
        ("r200", .20, .9, 20), ("L050", .08, .5, 20),
        ("L120", .08, 1.2, 20), ("thin", .08, .9, .05),
        ("thick", .08, .9, 500), ("p-low", .08, .9, 20),
        ("p-high", .08, .9, 20), ("r003-L050", .03, .5, 20),
        ("r003-L120", .03, 1.2, 20), ("r200-L050", .20, .5, 20),
        ("r200-L120", .20, 1.2, 20), ("thin-r003", .03, .9, .05),
        ("thick-r200", .20, .9, 500), ("missing-r", .08, .9, 20),
        ("small-D", .08, .9, 20), ("large-D", .08, .9, 20),
    ]
    for name, ratio, lr, thickness in specs:
        d = 500.0 if name == "small-D" else 2000.0 if name == "large-D" else 1000.0
        pressure = .2 if name == "p-low" else 8.0 if name == "p-high" else 1.2
        p = with_code(vertical_leg_tank(), "ASME VIII-1")
        p["project_number"] = "T09-" + name
        p["project_name"] = "T09 torispherical boundary probe " + name
        p["design_conditions"].update(operating_pressure=pressure, design_pressure=pressure,
                                         maximum_allowable_pressure_ps=pressure)
        head = p["heads"][0]
        head.update(head_id="HEAD-L", type="torispherical", inside_diameter=d,
                    outside_diameter=d+2*thickness, crown_radius=lr*d,
                    knuckle_radius=None if name == "missing-r" else ratio*d,
                    torispherical_geometry="custom", nominal_thickness=thickness,
                    internal_corrosion_allowance=0, mill_tolerance=0)
        p["heads"] = [head, {**head, "head_id":"HEAD-R"}]
        # Test hatası düzeltmesi (A3): sıra iki terminal bombe + gövde ister; welds korunur (shell/head WJ-01'e bağlı).
        p["shell_sections"][0]["inside_diameter"] = d
        p["component_sequence"] = [{"component_type":"head", "component_id":"HEAD-L"},
                                   {"component_type":"shell", "component_id":"SHELL-01"},
                                   {"component_type":"head", "component_id":"HEAD-R"}]
        p["nozzles"] = []; p["supports"] = []
        yield name, p, {"pressure_mpa":pressure,"D_mm":d,"L_mm":lr*d,"r_mm":None if name == "missing-r" else ratio*d,
                        "r_over_D":ratio,"L_over_D":lr,"nominal_thickness_mm":thickness}


def oracle(pressure, stress, efficiency, L, r, thickness):
    """UG-32(e)/App 1-4(d), M=1/4(3+sqrt(L/r)); dimensions in MPa/mm."""
    if not all(v and v > 0 for v in (pressure, stress, efficiency, L, r, thickness)):
        return None
    m = .25 * (3 + math.sqrt(L/r))
    required = pressure*L*m/(2*stress*efficiency-.2*pressure)
    mawp = 2*stress*efficiency*thickness/(L*m+.2*thickness)
    return {"M":m,"required_thickness":required,"mawp":mawp}
