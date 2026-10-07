"""Compact, deliberate variants for test-pressure behavior."""
from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    # Pressure basis is independently anchored at the component MAWP scale below;
    # vary the independent test-stress ratio, hydrostatic head, and material limiter.
    cases = []
    for i, ratio in enumerate((1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6), 1):
        for rho in (0, 1000):
            p = vertical_leg_tank(design_conditions={
                "operating_pressure": 0.5, "design_pressure": 1.0,
                "maximum_allowable_pressure_ps": 1.0,
                "operating_temperature": 200, "design_temperature": 200,
                "minimum_design_temperature": -10,
                "hydrotest_temperature": 20, "fluid_density_kg_m3": rho,
            })
            for material in p["materials"]:
                material["allowable_stress_test_temp"] = material["allowable_stress"] * ratio
            cases.append((f"R{int(ratio*10):02d}-D{rho}", p))
    # Missing test allowable and invalid zero design pressure should be blocked by validation.
    p = vertical_leg_tank()
    for material in p["materials"]:
        material.pop("allowable_stress_test_temp", None)
    cases.append(("MISSING-TEST-STRESS", p))
    invalid = vertical_leg_tank()
    invalid["design_conditions"]["maximum_allowable_pressure_ps"] = 0
    cases.append(("INVALID-ZERO-PS", invalid))
    return cases
