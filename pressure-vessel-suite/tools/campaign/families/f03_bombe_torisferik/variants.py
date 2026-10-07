"""Deterministic torispherical head inputs for F03."""
from __future__ import annotations

from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank, with_code


def _project(case_id: str, pressure: float = 1.2, diameter: float = 1000.0,
             ratio: float = 0.06, geometry: str = "standard_asme_fd",
             custom_l_ratio: float = 0.9, thickness: float = 20.0) -> dict:
    p = vertical_leg_tank()
    p = with_code(p, "ASME VIII-1")
    p["project_number"] = f"F03-{case_id}"
    p["project_name"] = f"F03 {case_id}"
    p["design_conditions"].update(operating_pressure=pressure, design_pressure=pressure,
                                   maximum_allowable_pressure_ps=pressure)
    p["shell_sections"] = [{"section_id":"SHELL-01", "inside_diameter":diameter,
        "tangent_length":2000, "nominal_thickness":thickness, "material_id":"M1",
        "internal_corrosion_allowance":0, "mill_tolerance":0}]
    p["heads"] = [{"head_id":"HEAD-L", "type":"torispherical", "inside_diameter":diameter,
        "outside_diameter":diameter+2*thickness, "crown_radius":diameter+2*thickness if geometry == "standard_asme_fd" else custom_l_ratio*diameter,
        "knuckle_radius":ratio*(diameter+2*thickness) if geometry == "standard_asme_fd" else ratio*diameter,
        "torispherical_geometry":geometry, "straight_flange_length":25,
        "nominal_thickness":thickness, "material_id":"M1", "internal_corrosion_allowance":0,
        "mill_tolerance":0}]
    p["heads"].append({"head_id":"HEAD-R", **{k:v for k,v in p["heads"][0].items() if k != "head_id"}})
    p["component_sequence"] = [{"component_type":"head", "component_id":"HEAD-L"},
                                {"component_type":"shell", "component_id":"SHELL-01"},
                                {"component_type":"head", "component_id":"HEAD-R"}]
    p["nozzles"] = []
    p["supports"] = []
    p["welds"] = []
    return p


def variants():
    # Boundaries, center points, and pressure/size interactions across both geometry routes.
    specs = [("STD-r006",0.06,"standard_asme_fd",1.2,1000),
             ("STD-r010",0.10,"standard_asme_fd",1.2,1000),
             ("STD-r015",0.15,"standard_asme_fd",1.2,1000),
             ("STD-r0059",0.059,"standard_asme_fd",1.2,1000),
             ("STD-L080",0.06,"standard_asme_fd",0.8,1000),
             ("STD-L090",0.06,"standard_asme_fd",0.9,1000),
             ("STD-L100",0.06,"standard_asme_fd",1.0,1000),
             ("STD-D500",0.06,"standard_asme_fd",1.2,500),
             ("STD-D2000",0.06,"standard_asme_fd",1.2,2000),
             ("STD-P060",0.06,"standard_asme_fd",0.6,1000),
             ("STD-P180",0.06,"standard_asme_fd",1.8,1000),
             ("STD-P300",0.06,"standard_asme_fd",3.0,1000)]
    for cid, ratio, geom, pressure, diameter in specs:
        # Standard geometry has crown L=Do; ratio is the requested r/D fraction.
        p = _project(cid, pressure, diameter, ratio, geom)
        p["heads"][0]["knuckle_radius"] = ratio * diameter
        yield cid, p
    for i, (ratio, lratio, pressure, diameter) in enumerate([
        (0.06,.8,1.2,1000),(.06,.9,1.2,1000),(.06,1.,1.2,1000),
        (.10,.8,1.2,1000),(.10,.9,1.2,1000),(.10,1.,1.2,1000),
        (.15,.8,1.2,1000),(.15,.9,1.2,1000),(.15,1.,1.2,1000),
        (.059,.9,1.2,1000),(.06,.9,.6,1000),(.06,.9,1.8,1000),
        (.10,.9,1.2,500),(.10,.9,1.2,2000),(.06,.9,3.,1000),
        (.15,1.,.6,500),(.10,.9,1.8,2000),(.08,.95,1.2,1000)]):
        cid=f"CUS-{i+1:02d}"
        yield cid, _project(cid, pressure, diameter, ratio, "custom", lratio)
    published = _project("PUB-K1-10", 420*0.006894757293168, 47*25.4,
                         2.9273/48, "custom", 1.0, .8901*25.4)
    published["heads"][0]["crown_radius"] = 48*25.4
    published["heads"][0]["knuckle_radius"] = 2.9273*25.4
    yield "PUB-K1-10", published
    # Missing radius deliberately exercises the required-input/blocking path.
    p = _project("BAD-MISSING-R", 1.2)
    p["heads"][0]["knuckle_radius"] = None
    yield "BAD-MISSING-R", p
