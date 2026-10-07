"""Deterministic, deliberately compact coverage matrix for F20."""
from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank, horizontal_saddle_tank, skirt_column, with_code


def variants():
    bases = (vertical_leg_tank, horizontal_saddle_tank, skirt_column)
    for bi, base_fn in enumerate(bases):
        for i, head_type in enumerate(("elliptical", "torispherical", "hemispherical", "flat")):
            p = base_fn()
            for h in p["heads"]:
                h["type"] = head_type
                if head_type == "torispherical":
                    h.update(crown_radius=1000, knuckle_radius=60, torispherical_geometry="custom")
                if head_type == "flat":
                    h["flat_attachment_factor"] = 0.33
            p["project_number"] = f"F20-{bi}-{i}"
            yield f"head-{bi}-{head_type}", p
        for j, pressure in enumerate((0.5, 1.0, 1.5)):
            p = base_fn(design_conditions={"design_pressure": pressure})
            p["project_number"] = f"F20-{bi}-P{j}"
            yield f"pressure-{bi}-{pressure}", p
        p = base_fn()
        template = vertical_leg_tank()["nozzles"][0]
        p["nozzles"] = [dict(template, tag=f"N{k}", axial_position=300 + 350*k) for k in range(1, 4)]
        p["project_number"] = f"F20-{bi}-nozzles"
        yield f"three-nozzles-{bi}", p
    # Alternate code, external pressure, MDMT, load, plus an invalid input.
    for case_id, p in (("en-code", with_code(vertical_leg_tank(), "EN 13445")),
                       ("external-pressure", vertical_leg_tank(design_conditions={"external_pressure": 0.1})),
                       ("mdmt", vertical_leg_tank(design_conditions={"minimum_design_temperature": -40})),
                       ("wind-load", vertical_leg_tank()),
                       ("vacuum", vertical_leg_tank(design_conditions={"vacuum_condition": True})),
                       ("invalid-pressure", vertical_leg_tank(design_conditions={"design_pressure": -1}))):
        if case_id == "wind-load":
            p["load_cases"] = [{"load_case_id":"W1", "name":"Wind", "load_type":"wind", "wind_speed_m_s":30}]
        p["project_number"] = f"F20-{case_id}"
        yield case_id, p
