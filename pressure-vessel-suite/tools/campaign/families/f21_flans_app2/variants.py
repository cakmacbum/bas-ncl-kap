"""Deterministic flange input variations, including missing/invalid user data."""
from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank, with_code


def variants():
    cases = []
    # Balanced parameter sampling across hub type, pressure, gasket, bolts and geometry.
    for i in range(30):
        loose = i % 3 == 0
        hub = i % 3 == 2
        flange = {
            "flange_id": "F1", "type": "loose" if loose else "integral",
            "inside_diameter": 460.375 if i % 2 else 1066.8,
            "outside_diameter": 596.9 if i % 2 else 1276.35,
            "thickness": 44.45 if i % 2 else 107.95,
            "hub_small_thickness": 3.175 if i % 2 else 4.7625,
            "hub_large_thickness": 12.7 if hub else (None if i == 29 else 4.7625),
            "hub_length": 28.575 if hub else 0.1,
            "material_id": "M1", "gasket_m": (2.5, 2.75, 3.0)[i % 3],
            "gasket_y": (19994.6, 25511.0, 30000.0)[i % 3],
            "bolt_count": (8, 16, 24)[i % 3],
            "bolt_area": (500.0, 1000.0, 1500.0)[i % 3],
            "bolt_allowable_stress": 172.4,
            "flange_factor_Y": None if i == 28 else 7.822,
            "flange_factor_f": 2.93, "flange_factor_F": 0.9089,
            "flange_factor_V": 0.5501, "flange_factor_T": 1.8418,
            "flange_factor_U": 12.2005,
            "bolt_load_W_N": 299800 if i % 2 else 2828000,
            "moment_M_Nmm": 1.08e7 if i % 2 else 1.08e8,
        }
        if i == 27:  # Deliberately invalid zero input
            flange["bolt_count"] = 0
        pressure = (1.034, 1.379, 0.0)[i % 3] if i == 27 else (1.034, 1.379, 1.724)[i % 3]
        project = with_code(vertical_leg_tank(
            design_conditions={"operating_pressure": pressure, "design_pressure": pressure,
                "maximum_allowable_pressure_ps": pressure, "operating_temperature": 343.3,
                "design_temperature": 343.3, "minimum_design_temperature": -20.0},
            flanges=[flange],
        ), "ASME VIII-1")
        cases.append((f"F21-{i+1:02d}", project))
    return cases
