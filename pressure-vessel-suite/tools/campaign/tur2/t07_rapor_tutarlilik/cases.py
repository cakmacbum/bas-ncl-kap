"""Deterministic report consistency cases based on campaign examples."""
from __future__ import annotations

from tools.campaign.bases import vertical_leg_tank
from tools.campaign.examples import (
    example_flange_stress, example_global_load_case, example_hydrotest,
    example_junction_check, example_leg_section_check, example_mawp,
    example_mdmt_check, example_nozzle_reinforcement, example_skirt_stress,
    example_thickness,
)


CASES = [
    {"id": "R01", "name": "thickness", "project": example_thickness},
    {"id": "R02", "name": "mawp", "project": example_mawp},
    {"id": "R03", "name": "nozzle reinforcement", "project": example_nozzle_reinforcement},
    {"id": "R04", "name": "hydrotest", "project": example_hydrotest},
    {"id": "R05", "name": "MDMT", "project": example_mdmt_check},
    {"id": "R06", "name": "leg section", "project": example_leg_section_check},
    {"id": "R07", "name": "skirt", "project": example_skirt_stress},
    {"id": "R08", "name": "flange", "project": example_flange_stress},
    {"id": "R09", "name": "junction", "project": example_junction_check},
    {"id": "R10", "name": "global load", "project": example_global_load_case},
    {"id": "R11", "name": "thickness repeated", "project": example_thickness},
    {"id": "R12", "name": "mawp repeated", "project": example_mawp},
    {"id": "R13", "name": "nozzle repeated", "project": example_nozzle_reinforcement},
    {"id": "R14", "name": "hydrotest repeated", "project": example_hydrotest},
    {"id": "R15", "name": "MDMT repeated", "project": example_mdmt_check},
    {"id": "R16", "name": "leg section repeated", "project": example_leg_section_check},
    {"id": "R17", "name": "skirt repeated", "project": example_skirt_stress},
    {"id": "R18", "name": "flange repeated", "project": example_flange_stress},
    {"id": "R19", "name": "junction repeated", "project": example_junction_check},
    {"id": "R20", "name": "global load repeated", "project": example_global_load_case},
]
