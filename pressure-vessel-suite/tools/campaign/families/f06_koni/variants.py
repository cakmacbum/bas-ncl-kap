from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank, with_code


def variants():
    # 30 geçerli kombinasyon: açı köşeleri, çap oranları, basınç ve CA örnekleri.
    specs = [(a, ratio, p, ca) for a in (5, 15, 30, 45, 60)
             for ratio, p, ca in ((0.5, 0.5, 0), (0.7, 1.0, 1), (0.85, 2.0, 2))]
    # K2-05 yayınlanmış geometri/basınç koşulu, ayrıca yeniden üretilebilir.
    specs.append((25.3, 10.39/12.75, 200.953*0.006894757293168, 0.0))
    for i, (angle, ratio, pressure, ca) in enumerate(specs, 1):
        p = with_code(vertical_leg_tank(), "ASME VIII-1")
        large = 1000.0
        small = large * ratio
        p["design_conditions"].update(operating_pressure=pressure, design_pressure=pressure,
            maximum_allowable_pressure_ps=pressure, operating_temperature=100,
            design_temperature=100, minimum_design_temperature=-20)
        p["cones"] = [{"cone_id":"CONE-01", "large_diameter":large,
            "small_diameter":small, "half_apex_angle":angle,
            "length":(large-small)/(2*__import__('math').tan(__import__('math').radians(angle))),
            "nominal_thickness":12.7, "material_id":"M1",
            "internal_corrosion_allowance":ca}]
        p["junctions"] = [{"junction_id":"J-L", "left_component_id":"CONE-01",
            "right_component_id":"SHELL-01", "junction_type":"cone_to_shell",
            "cone_end":"large", "large_end_diameter":large,
            "small_end_diameter":small, "analysis_status":"REVIEW_REQUIRED"}]
        p["component_sequence"] = []
        yield f"GRID-{i:02d}", p
