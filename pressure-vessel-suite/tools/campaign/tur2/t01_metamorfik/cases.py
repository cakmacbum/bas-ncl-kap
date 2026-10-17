"""Metamorphic input generators for supported pressure component families."""
from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank

COMPONENTS = ("gövde", "eliptik", "torisferik", "yarım küre", "düz kapak", "koni", "nozul", "dış basınç")
RELATIONS = ("P↑ → t_required↑", "S↑ → t_required↓", "CA↑ → nominal gereksinim↑",
             "E↓ → t_required↑", "nominal kalınlık↑ → MAWP↑", "sıcaklık↑ → S↓")

def project_for(component):
    p = vertical_leg_tank()
    p["heads"] = [h for h in p["heads"] if h["head_id"] == "HEAD-L"]
    p["nozzles"] = []
    # Taban kurgusunda tek bombe var; sıralama iki terminal bombe ister (koni vakası için).
    if component == "torisferik": p["heads"][0]["type"] = "torispherical"
    if component == "yarım küre": p["heads"][0]["type"] = "hemispherical"
    if component == "düz kapak":
        p["heads"][0]["type"] = "flat"
        p["heads"][0]["flat_attachment_factor"] = 0.33  # UG-34 C (test girdisi eksikti)
    if component == "koni":
        p["cones"] = [{"cone_id":"C1", "large_diameter":1000, "small_diameter":800,
                       "half_apex_angle":15, "length":500, "nominal_thickness":12,
                       "material_id":"M1", "weld_joint_id":"WJ-01", "internal_corrosion_allowance":2}]
        p["junctions"] = [{"junction_id":"J1", "left_component_id":"SHELL-01", "right_component_id":"C1",
                            "junction_type":"cone_to_shell", "cone_end":"large", "weld_joint_id":"WJ-01",
                            "weld_efficiency":1.0, "large_end_diameter":1000, "small_end_diameter":800}]
        p["component_sequence"] = [{"component_type":"head","component_id":"HEAD-L"},
                                    {"component_type":"shell","component_id":"SHELL-01"},
                                    {"component_type":"cone","component_id":"C1"},
                                    {"component_type":"head","component_id":"HEAD-R"}]
        p["heads"].append({**p["heads"][0], "head_id":"HEAD-R"})
    if component == "nozul":
        p["nozzles"] = [{"tag":"N1", "host_component_id":"SHELL-01", "axial_position":800,
                         "outside_diameter":60.3, "inside_diameter":52.5, "neck_thickness":8,
                         "material_id":"M1", "reinforcement_pad":False}]
    if component == "dış basınç":
        p["design_conditions"]["external_pressure"] = .1
        p["shell_sections"][0].update(ug28_strain_factor_a=.001, ug28_allowable_stress_b=50)
        p["heads"][0].update(ug28_strain_factor_a=.001, ug28_allowable_stress_b=50)
    return p

def vary(p, relation, step):
    p = deepcopy(p)
    x = step / 4
    shell, head = p["shell_sections"][0], p["heads"][0]
    if relation == RELATIONS[0]: p["design_conditions"]["design_pressure"] = .5 + x
    elif relation == RELATIONS[1]:
        for m in p["materials"]: m["allowable_stress"] = 80 + 100*x
    elif relation == RELATIONS[2]:
        p["design_conditions"]["corrosion_allowance_internal"] = 1 + 4*x
        shell["internal_corrosion_allowance"] = 1 + 4*x; head["internal_corrosion_allowance"] = 1 + 4*x
    elif relation == RELATIONS[3]:
        for w in p["welds"]: w["joint_efficiency"] = 1 - .4*x
    elif relation == RELATIONS[4]:
        shell["nominal_thickness"] = 8 + 8*x; head["nominal_thickness"] = 8 + 8*x
    else:
        p["design_conditions"]["design_temperature"] = 100 + 100*x
        for m in p["materials"]: m["temperature"] = 100 + 100*x; m["allowable_stress"] = 160 - 40*x
    for cone in p.get("cones", []):  # koni de aynı ilişkiye göre değişsin
        if relation == RELATIONS[2]: cone["internal_corrosion_allowance"] = 1 + 4*x
        elif relation == RELATIONS[4]: cone["nominal_thickness"] = 8 + 8*x
    return p

