"""Small, deliberate grid for UCS-66 inputs."""
from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank, with_code


def variants():
    # Each point exercises curve group and representative thicknesses; extra
    # cases vary ratio, impact-test temperature and PWHT at a fixed thickness.
    index = 0
    for group in "ABCD":
        for thickness in (6, 12, 25, 50, 100):
            index += 1
            project = vertical_leg_tank()
            project = with_code(project, "ASME VIII-1")
            project["shell_sections"][0]["nominal_thickness"] = thickness
            project["shell_sections"][0]["internal_corrosion_allowance"] = 0
            for material in project["materials"]:
                material["ucs66_curve_group"] = group
            project["design_conditions"]["impact_test_temperature_C"] = -20
            yield f"GRID-{index:02d}", project
    for ratio, impact, pwht in ((0.35, None, False), (0.65, -20, False),
                                (0.85, -40, True), (0.95, 0, True),
                                (1.0, 20, False)):
        index += 1
        project = vertical_leg_tank()
        project = with_code(project, "ASME VIII-1")
        project["shell_sections"][0]["nominal_thickness"] = 25
        project["design_conditions"]["impact_test_temperature_C"] = impact
        for material in project["materials"]:
            material["ucs66_curve_group"] = "B"
        # PWHT is represented as weld state; ratio is a documented input axis.
        for weld in project["welds"]:
            weld["pwht_required"] = pwht
        project["materials"][0]["notes"] = f"campaign coincident ratio target {ratio}"
        yield f"EDGE-{index:02d}", project
    for thickness, temperature in ((6, -46), (10, -20), (18, -10), (25, 0),
                                   (40, 10), (60, 20), (80, -30), (100, -46)):
        index += 1
        project = vertical_leg_tank()
        project = with_code(project, "ASME VIII-1")
        project["shell_sections"][0]["nominal_thickness"] = thickness
        project["design_conditions"]["impact_test_temperature_C"] = temperature
        for material in project["materials"]:
            material["ucs66_curve_group"] = "B"
        yield f"TEMP-{index:02d}", project
    # Deliberately absent curve group and missing impact-test temperature.
    for label, curve, impact in (("NO-CURVE", None, -20), ("NO-IMPACT", "B", None)):
        index += 1
        project = vertical_leg_tank()
        project = with_code(project, "ASME VIII-1")
        project["design_conditions"]["impact_test_temperature_C"] = impact
        for material in project["materials"]:
            material["ucs66_curve_group"] = curve
        yield f"INVALID-{index:02d}-{label}", project
