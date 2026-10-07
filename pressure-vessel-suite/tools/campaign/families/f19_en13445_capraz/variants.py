from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank, with_code

PRESSURES = (0.5, 1.2, 2.0, 4.0, 8.25)
EFFICIENCIES = (0.7, 0.85, 1.0)


def variants():
    # Paired code comparisons over boundary, midpoint, and published-pressure values.
    n = 0
    for pressure, z in ((0.5, .7), (1.2, .85), (2.0, 1.0), (4.0, .7), (8.25, .85), (1.2, 1.0), (4.0, 1.0), (8.25, 1.0), (0.5, 1.0), (2.0, .7), (8.25, .7)):
        for code in ("EN 13445", "ASME VIII-1"):
            n += 1
            p = vertical_leg_tank(design_conditions={"operating_pressure": pressure*.8,
                "design_pressure": pressure, "maximum_allowable_pressure_ps": pressure*1.25,
                "hydrotest_temperature": 20.0})
            # Set weld efficiency and material properties to the requested paired inputs.
            p["welds"][0]["joint_efficiency"] = z
            p = with_code(p, code)
            yield f"PAIR-{n:02d}", p
    # Head geometry changes (the base is 2:1 elliptical).
    for kind in ("elliptical", "torispherical"):
        for code in ("EN 13445", "ASME VIII-1"):
            n += 1
            p = vertical_leg_tank(design_conditions={"operating_pressure": .96, "design_pressure": 1.2,
                "maximum_allowable_pressure_ps": 1.5})
            p["heads"] = [dict(h, **({"type": kind, "crown_radius": 1000, "knuckle_radius": 60} if kind == "torispherical" else {"type": kind})) for h in p["heads"]]
            yield f"HEAD-{kind[:3].upper()}-{code[:1]}-{n:02d}", with_code(p, code)
    # Explicit invalid pressure and missing-strength cases must be blocked/out of scope.
    for label, override in (("ZERO-P", {"design_pressure": 0}), ("LOW-STRENGTH", {"design_pressure": 1.2})):
        for code in ("EN 13445", "ASME VIII-1"):
            n += 1
            p = vertical_leg_tank(design_conditions={"operating_pressure": .96, "design_pressure": 1.2,
                "maximum_allowable_pressure_ps": 1.5})
            if label == "ZERO-P":
                p["design_conditions"]["design_pressure"] = 0
            else:
                p["materials"][0]["yield_strength"] = None
            yield f"INVALID-{label}-{code[:1]}-{n:02d}", with_code(p, code)

