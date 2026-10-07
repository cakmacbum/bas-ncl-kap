from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank, with_code


def _case(case_id, diameter, pressure, stress=138.0, efficiency=1.0, ca=0.0, thick=16.0):
    p = vertical_leg_tank()
    p = with_code(p, "ASME VIII-1")
    p["project_number"] = "F04-" + case_id
    p["project_name"] = "F04 " + case_id
    p["design_conditions"].update(operating_pressure=pressure * 0.8,
                                  design_pressure=pressure,
                                  maximum_allowable_pressure_ps=pressure * 1.25,
                                  corrosion_allowance_internal=ca)
    for material in p["materials"]:
        material["allowable_stress"] = stress
    for head in p["heads"]:
        head.update(type="hemispherical", inside_diameter=diameter,
                    nominal_thickness=thick, internal_corrosion_allowance=ca,
                    mill_tolerance=0.0, forming_thinning=0.0)
        if efficiency != 1.0:
            # Joint efficiency is specified by its associated weld record.
            for weld in p["welds"]:
                if weld.get("weld_joint_id") == head.get("weld_joint_id") or weld.get("joint_id") == head.get("weld_joint_id"):
                    weld["joint_efficiency"] = efficiency
    return p


def variants():
    specs = []
    for d, p in ((300, .1), (300, 20), (4000, .1), (4000, 20),
                 (1000, 1), (2000, 5), (3000, 10), (1500, 3), (2500, 8)):
        specs.append((f"grid-D{d}-P{p:g}", d, p, 138, 1, 0, 24))
    for d in (300, 500, 1000, 2000, 3000, 4000):
        specs.append((f"diameter-{d}", d, 2, 138, 1, 0, 24))
    for p in (.1, .5, 1, 5, 10, 20):
        specs.append((f"pressure-{p:g}", 1500, p, 138, 1, 0, 24))
    for name, vals in (("ca-2", (1500, 5, 138, 1, 2, 24)),
                       ("ca-5", (1500, 5, 138, 1, 5, 24)),
                       ("eff-0.85", (1500, 5, 138, .85, 0, 24)),
                       ("stress-low", (1500, 5, 100, 1, 0, 24)),
                       ("thick-wall", (300, 20, 138, 1, 0, 180)),
                       ("thin-wall", (4000, .1, 138, 1, 0, 6))):
        specs.append((name, *vals))
    for d, p in ((300, .1), (4000, 20), (1000, 10), (2000, 15), (3000, 1)):
        specs.append((f"interaction-{d}-{p:g}", d, p, 120, .9, 1, 36))
    # Published sphere-segment checks from K1-12/13; same UG-32(f) pressure law,
    # but not geometrically a complete hemispherical head.
    specs.extend((
        ("K1-12-spherical-segment", 18288, 1.0834, 147.548, 1, .762, 37.592),
        ("K1-13-spherical-segment", 18288, 1.1690, 147.548, 1, .762, 37.084),
    ))
    for spec in specs:
        case_id, d, pressure, stress, efficiency, ca, thick = spec
        yield case_id, _case(case_id, d, pressure, stress, efficiency, ca, thick)
    bad = _case("invalid-zero-pressure", 1000, 1)
    bad["design_conditions"]["design_pressure"] = 0
    yield "invalid-zero-pressure", bad
