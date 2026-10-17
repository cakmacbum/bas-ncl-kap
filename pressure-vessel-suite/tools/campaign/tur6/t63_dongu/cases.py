"""Seeded inputs for T63: 120 nozzle and 120 elliptical-head cases."""
from __future__ import annotations

import random
from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank


SEED = 630


def cases():
    rng = random.Random(SEED)
    for component, kind in (("A", "nozzle"), ("B", "head")):
        for i in range(120):
            d_i = round(rng.uniform(300, 2500), 3)
            pressure = round(rng.uniform(0.2, 8.0), 5)
            allowable = round(rng.uniform(100, 200), 4)
            efficiency = round(rng.uniform(0.85, 1.0), 5)
            ca = round(rng.uniform(0, 3), 4)
            project = vertical_leg_tank(
                design_conditions={"design_pressure": pressure, "operating_pressure": pressure,
                                   "maximum_allowable_pressure_ps": pressure}
            )
            shell = project["shell_sections"][0]
            shell.update(inside_diameter=d_i, outside_diameter=d_i + 40,
                         nominal_thickness=20, internal_corrosion_allowance=ca)
            for head in project["heads"]:
                head.update(type="elliptical", inside_diameter=d_i, outside_diameter=d_i + 40,
                            crown_depth=d_i / 4, straight_flange_length=25, nominal_thickness=20,
                            internal_corrosion_allowance=ca)
            for material in project["materials"]:
                if material["material_id"] == "M1":
                    material["allowable_stress"] = allowable
                    material["allowable_stress_test_temp"] = allowable
            for weld in project["welds"]:
                if weld["joint_id"] == "WJ-01":
                    weld["joint_efficiency"] = efficiency
            project["diameter_relation"] = "independent"
            if kind == "nozzle":
                ratio = rng.uniform(0.05, 0.4)
                nozzle_d = round(d_i * ratio, 3)
                neck_t = round(rng.uniform(4, 24), 3)
                project["nozzles"] = [{"tag": "N1", "host_component_id": "SHELL-01",
                    "axial_position": 500, "outside_diameter": nozzle_d + 2 * neck_t,
                    "inside_diameter": nozzle_d, "neck_thickness": neck_t,
                    "material_id": "M1", "reinforcement_pad": False}]
                project["shell_sections"][0]["nominal_thickness"] = round(rng.uniform(8, 35), 3)
                project["shell_sections"][0]["internal_corrosion_allowance"] = ca
                case_id = f"T63-A-{i + 1:03d}"
                inputs = {"D_i_mm": d_i, "d_over_D": ratio, "P_MPa": pressure,
                          "S_MPa": allowable, "E": efficiency, "CA_i_mm": ca,
                          "nozzle_d_mm": nozzle_d, "neck_t_mm": neck_t}
            else:
                case_id = f"T63-B-{i + 1:03d}"
                inputs = {"D_i_mm": d_i, "P_MPa": pressure, "S_MPa": allowable,
                          "E": efficiency, "CA_i_mm": ca}
            project["project_number"] = case_id
            project["project_name"] = f"T63 campaign {case_id}"
            yield {"id": case_id, "component": component, "kind": kind,
                   "inputs": inputs, "project": project}
