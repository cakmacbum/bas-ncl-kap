"""Deterministic, plausible variants of the three campaign bases."""
import random
from copy import deepcopy
from tools.campaign.bases import horizontal_saddle_tank, skirt_column, vertical_leg_tank

SEED = 20261017
COUNT = 300
BASES = (("vertical_leg", vertical_leg_tank), ("horizontal_saddle", horizontal_saddle_tank), ("skirt_column", skirt_column))

def cases(count=COUNT, seed=SEED):
    rng = random.Random(seed)
    for i in range(count):
        base_name, factory = BASES[i % 3]
        p = deepcopy(factory())
        p["project_number"] = f"T04-{i+1:03d}"
        p["project_name"] = f"T04 fuzz {i+1:03d}"
        shell = p["shell_sections"][0]
        d = rng.randint(700, 1600)
        t = rng.choice((8, 10, 12, 14, 16, 20))
        shell.update(inside_diameter=d, outside_diameter=d+2*t, nominal_thickness=t,
                     tangent_length=rng.randint(1800, 4800))
        pressure = round(rng.uniform(.15, 1.8), 3)
        p["design_conditions"].update(design_pressure=pressure,
            operating_pressure=round(pressure*rng.uniform(.65, .95), 3),
            design_temperature=rng.choice((20, 50, 100, 150, 200)))
        p.update(calculation_code="ASME VIII-1", code_edition="2025")
        for h in p.get("heads", []):
            h.update(inside_diameter=d, nominal_thickness=t)
        for m in p.get("materials", []):
            m["design_temperature"] = p["design_conditions"]["design_temperature"]
        if base_name == "vertical_leg":
            p["supports"][0].update(leg_count=rng.randint(3, 8),
                leg_diameter_mm=rng.choice((88.9, 101.6, 114.3, 139.7)),
                leg_thickness_mm=rng.choice((6, 8, 10, 12)))
        elif base_name == "horizontal_saddle":
            length = shell["tangent_length"]
            for s, ratio in zip(p["supports"], (.25, .75)):
                s.update(location_mm=round(length*ratio), width_mm=rng.choice((180, 220, 250, 300)))
        else:
            p["supports"][0].update(diameter_mm=d, thickness_mm=rng.choice((8, 10, 12, 16)),
                                     height_mm=rng.randint(700, 1800))
        ns = p.setdefault("nozzles", [])
        for n in ns:
            n["axial_position"] = min(max(250, shell["tangent_length"]//2), shell["tangent_length"]-250)
        while len(ns) > (target := rng.randint(0, 3)):
            ns.pop()
        while len(ns) < target:
            n = len(ns)+1
            ns.append({"tag": f"N{n}", "host_component_id": shell["section_id"],
                "axial_position": rng.randint(250, shell["tangent_length"]-250),
                "outside_diameter": 48.3, "inside_diameter": 40.9, "neck_thickness": 3.7,
                "material_id": "M1", "reinforcement_pad": False})
        yield {"case_id": f"T04-{i+1:03d}", "base": base_name, "project": p}
