"""Compact boundary and corner cases for global MAWP/static head."""
from tools.campaign.bases import vertical_leg_tank, horizontal_saddle_tank


def variants():
    # Independent pressure boundary, liquid density and vessel orientation.
    for i, pressure in enumerate((0.8, 1.0, 1.2, 1.5, 2.0), 1):
        yield f"V-P{i}", vertical_leg_tank(design_conditions={"design_pressure": pressure})
    for i, density in enumerate((0.0, 500.0, 800.0, 1000.0, 1200.0, 1800.0), 1):
        yield f"V-RHO{i}", vertical_leg_tank(design_conditions={"fluid_density_kg_m3": density})
    for i, thickness in enumerate((8.0, 10.0, 12.0, 14.0, 18.0), 1):
        p = vertical_leg_tank()
        p["shell_sections"][0]["nominal_thickness"] = thickness
        yield f"V-T{i}", p
    for i, thickness in enumerate((7.0, 9.0, 12.0, 15.0), 1):
        p = vertical_leg_tank()
        for head in p["heads"]:
            head["nominal_thickness"] = thickness
        yield f"V-H{i}", p
    for i, density in enumerate((500.0, 800.0, 1000.0, 1200.0), 1):
        yield f"H-RHO{i}", horizontal_saddle_tank(design_conditions={"fluid_density_kg_m3": density})
    for i, thickness in enumerate((6.0, 8.0, 11.0, 16.0), 1):
        p = horizontal_saddle_tank()
        p["shell_sections"][0]["nominal_thickness"] = thickness
        yield f"H-T{i}", p
    # Missing material is a deliberately invalid input and must be out of scope.
    p = vertical_leg_tank()
    p["materials"] = []
    yield "INVALID-NO-MATERIAL", p
    # Published Codeware cylinder reference: inputs and value transcribed from source K1-01.
    p = vertical_leg_tank()
    p["shell_sections"] = [{"section_id": "SHELL-01", "inside_diameter": 609.6,
        "tangent_length": 3000, "nominal_thickness": 4.7625, "material_id": "M1",
        "internal_corrosion_allowance": 0, "external_corrosion_allowance": 0,
        "mill_tolerance": 0, "forming_thinning": 0}]
    p["heads"] = []
    p["materials"] = [dict(p["materials"][0], allowable_stress=137.895, allowable_stress_test_temp=137.895)]
    p["design_conditions"]["design_pressure"] = 0.696
    p["design_conditions"]["fluid_density_kg_m3"] = 997
    yield "PUB-CW-K1-01", p
