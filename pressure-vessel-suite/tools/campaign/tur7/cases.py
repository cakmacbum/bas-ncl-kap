"""Tohum 7777, 300 vaka. Yalnız girdi üretir; hesap sonucu içermez."""
import random
from tools.campaign.bases import vertical_leg_tank

SEED = 7777


def _project(case_id, D_i, P, S, E, CA, crown_depth=None, nozzle=None, nominal=20.0):
    pr = vertical_leg_tank(design_conditions={
        "design_pressure": P, "operating_pressure": P, "maximum_allowable_pressure_ps": P})
    sh = pr["shell_sections"][0]
    sh.update(inside_diameter=D_i, outside_diameter=D_i + 2 * nominal, nominal_thickness=nominal,
              internal_corrosion_allowance=CA)
    for h in pr["heads"]:
        h.update(type="elliptical", inside_diameter=D_i, outside_diameter=D_i + 2 * nominal,
                 straight_flange_length=25, nominal_thickness=nominal,
                 internal_corrosion_allowance=CA)
        if crown_depth is not None:
            h["crown_depth"] = crown_depth
        else:
            h.pop("crown_depth", None)
    for m in pr["materials"]:
        if m["material_id"] == "M1":
            m["allowable_stress"] = S
            m["allowable_stress_test_temp"] = S
    for w in pr["welds"]:
        if w["joint_id"] == "WJ-01":
            w["joint_efficiency"] = E
    pr["diameter_relation"] = "independent"
    pr["nozzles"] = []
    if nozzle:
        d, tn = nozzle
        pr["nozzles"] = [{"tag": "N1", "host_component_id": "SHELL-01", "axial_position": 500,
                          "outside_diameter": d + 2 * tn, "inside_diameter": d, "neck_thickness": tn,
                          "material_id": "M1", "reinforcement_pad": False}]
    pr["project_number"] = case_id
    pr["project_name"] = f"T7-A2 {case_id}"
    return pr


def cases():
    rng = random.Random(SEED)
    out = []
    for i in range(300):
        if i < 100:
            typ, sub = "shell", "shell"
        elif i < 150:
            typ, sub = "head", "head_std"
        elif i < 200:
            typ, sub = "head", "head_h"
        else:
            typ, sub = "nozzle", "nozzle"
        D = round(rng.uniform(300, 2500), 3)
        P = round(rng.uniform(0.2, 6.0), 5)
        S = round(rng.uniform(100, 200), 4)
        E = round(rng.choice([rng.uniform(0.7, 1.0), 1.0, 0.85, 0.7]), 5)
        CA = round(rng.uniform(0, 3), 4)
        crown = round(D / 4, 4) if sub == "head_h" else None
        noz = None
        d_noz = tn = None
        nominal = 20.0
        if typ == "nozzle":
            d_noz = round(D * rng.uniform(0.05, 0.4), 3)
            tn = round(rng.uniform(4, 24), 3)
            noz = (d_noz, tn)
            nominal = round(rng.uniform(15, 40), 3)
        cid = f"T7A2-{i + 1:03d}"
        out.append({"id": cid, "type": typ, "subgroup": sub, "D_i": D, "P": P, "S": S, "E": E,
                    "CA": CA, "crown_depth": crown, "nozzle_d": d_noz, "neck_t": tn,
                    "project": _project(cid, D, P, S, E, CA, crown, nozzle=noz, nominal=nominal)})
    return out
