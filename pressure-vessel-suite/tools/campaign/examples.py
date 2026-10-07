"""Small, reproducible public-API projects for campaign result types."""
from __future__ import annotations

from .bases import horizontal_saddle_tank, skirt_column, vertical_leg_tank


def example_thickness() -> dict:
    return vertical_leg_tank()


def example_mawp() -> dict:
    p = vertical_leg_tank()
    p["design_conditions"]["fluid_density_kg_m3"] = 1000
    p["load_cases"] = [{"load_case_id": "FILL", "name": "Liquid fill", "load_type": "fluid_weight",
        "fluid_density_kg_m3": 1000, "fluid_level_mm": 1800}]
    return p


def example_nozzle_reinforcement() -> dict:
    return vertical_leg_tank()


def example_clash_check() -> dict:
    return vertical_leg_tank()


def example_weld_validation() -> dict:
    return vertical_leg_tank()


def example_hydrotest() -> dict:
    return vertical_leg_tank()


def example_pneumatic_test() -> dict:
    return vertical_leg_tank()


def example_mdmt_check() -> dict:
    return vertical_leg_tank()


def example_leg_stress() -> dict:
    return vertical_leg_tank()


def example_skirt_stress() -> dict:
    return skirt_column()


def example_saddle_stress() -> dict:
    p = horizontal_saddle_tank()
    p["supports"] = [dict(s, contact_angle_deg=120, saddle_stiffened=True,
                           zick_K1=1.0, zick_K2=1.0, zick_K6=1.0, zick_K7=1.0)
                      for s in p["supports"]]
    return p


def example_leg_section_check() -> dict:
    p = vertical_leg_tank()
    p["supports"][0].update(leg_section_type="pipe", leg_eccentricity_mm=80,
        leg_unbraced_length_mm=600, base_plate_yield_MPa=250,
        base_plate_length_mm=250, base_plate_width_mm=200, base_plate_thickness_mm=16,
        foundation_bearing_allowable_MPa=10, pad_to_shell_weld_leg_mm=6,
        leg_to_pad_weld_leg_mm=6, leg_to_base_plate_weld_leg_mm=6,
        weld_electrode_strength_MPa=490, weld_min_leg_mm=3,
        leg_attachment="shell", wrc_coefficients={
            pt: {load: {"Nx": 0, "Ny": 0, "Mx": 0, "My": 0}
                 for load in ("P", "ML", "MC", "VL", "VC")}
            for pt in ("A", "B", "C", "D")})
    return p


def example_leg_weld_check() -> dict:
    return example_leg_section_check()


def example_base_plate_check() -> dict:
    return example_leg_section_check()


def example_wrc_local_stress() -> dict:
    return example_leg_section_check()


def example_flange_stress() -> dict:
    p = vertical_leg_tank()
    p["flanges"] = [{"flange_id": "F1", "type": "integral", "inside_diameter": 500,
        "outside_diameter": 800, "thickness": 50, "hub_small_thickness": 35,
        "hub_large_thickness": 50, "hub_length": 100, "material_id": "M1",
        "bolt_load_W_N": 100000, "moment_M_Nmm": 1000000,
        "flange_factor_Y": 1.0, "flange_factor_f": 1.0,
        "flange_factor_F": 1.0, "flange_factor_V": 1.0,
        "flange_factor_T": 1.0, "flange_factor_U": 1.0}]
    return p


def example_junction_check() -> dict:
    p = vertical_leg_tank()
    p["cones"] = [{"cone_id": "C1", "large_diameter": 1000, "small_diameter": 800,
        "half_apex_angle": 15, "length": 500, "nominal_thickness": 12, "material_id": "M1"}]
    p["component_sequence"] = [{"component_type": "head", "component_id": p["heads"][0]["head_id"]},
        {"component_type": "shell", "component_id": "SHELL-01"},
        {"component_type": "cone", "component_id": "C1"},
        {"component_type": "head", "component_id": p["heads"][1]["head_id"]}]
    p["junctions"] = [{"junction_id": "J1", "left_component_id": "SHELL-01",
        "right_component_id": "C1", "junction_type": "cone_to_shell", "cone_end": "large",
        "weld_joint_id": "WJ-01", "weld_efficiency": 1.0,
        "large_end_diameter": 1000, "small_end_diameter": 800}]
    return p


def example_global_load_case() -> dict:
    p = vertical_leg_tank()
    p["load_cases"] = [{"load_case_id": "WIND-1", "name": "Wind", "load_type": "wind",
        "wind_speed_m_s": 35, "external_loads": [{"load_id": "W1", "component_id": "LEGS",
        "fx_n": 1000, "my_nmm": 200000}]}]
    return p


def example_global_load_combination() -> dict:
    p = vertical_leg_tank()
    p["load_cases"] = [{"load_case_id": "WIND-OP", "name": "Wind operating", "load_type": "wind",
        "wind_speed_m_s": 35}, {"load_case_id": "WIND-EMPTY", "name": "Wind empty", "load_type": "wind",
        "wind_speed_m_s": 35}]
    p["load_combinations"] = [{"combination_id": "COMB-1", "name": "Wind operating + empty",
        "load_case_ids": ["WIND-OP", "WIND-EMPTY"],
        "load_factors": {"WIND-OP": 1.0, "WIND-EMPTY": 1.0}}]
    return p


def example_external_pressure() -> dict:
    p = vertical_leg_tank()
    p["design_conditions"]["external_pressure"] = 0.1
    p["shell_sections"][0].update(ug28_strain_factor_a=0.001, ug28_allowable_stress_b=50)
    for head in p["heads"]:
        head.update(ug28_strain_factor_a=0.001, ug28_allowable_stress_b=50)
    return p


def example_pressure_consistency() -> dict:
    p = vertical_leg_tank()
    p["design_conditions"]["operating_pressure"] = 2.0
    p["design_conditions"]["design_pressure"] = 1.5
    return p
