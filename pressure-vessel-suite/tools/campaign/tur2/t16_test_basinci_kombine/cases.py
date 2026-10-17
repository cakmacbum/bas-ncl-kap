"""T16: combined test pressure, liquid head and governing component cases."""
from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank, horizontal_saddle_tank


def cases():
    out = []
    # Orthogonal matrix: orientation, fluid density, test/design stress ratio,
    # and pressure-basis field. Fixture components deliberately include a weaker head.
    index = 0
    for orientation, base, full_head_mm in (
        ("vertical", vertical_leg_tank, 2500.0),
        ("horizontal", horizontal_saddle_tank, 1000.0),
    ):
        for density in (0.0, 500.0, 1000.0, 1200.0):
            for ratio in (0.8, 1.0, 1.25):
                for basis_mode in ("mawp", "design"):
                    index += 1
                    project = base()
                    conditions = project["design_conditions"]
                    conditions.update({
                        "design_pressure": 1.0,
                        "operating_pressure": 0.7,
                        "operating_temperature": 200,
                        "design_temperature": 200,
                        "hydrotest_temperature": 20,
                        "fluid_density_kg_m3": density,
                    })
                    if basis_mode == "mawp":
                        conditions["maximum_allowable_pressure_ps"] = 1.4
                    else:
                        conditions["maximum_allowable_pressure_ps"] = 1.4
                    for material in project["materials"]:
                        material["allowable_stress_test_temp"] = material["allowable_stress"] * ratio
                    # Explicit fill level makes the bottom-head increment independently calculable.
                    conditions["test_fluid_level_mm"] = full_head_mm
                    out.append((f"T16-{index:02d}-{orientation}-{int(density)}-{ratio}-{basis_mode}", project))
    return out
