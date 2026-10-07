"""Catalog-backed flange stress examples and controlled load variations."""
from copy import deepcopy

from tools.campaign.examples import example_flange_stress


def variants():
    base = example_flange_stress()
    cases = []
    # The catalog's working flange_stress example is the trigger-complete base.
    # Vary its two explicit load inputs without changing required factors/geometry.
    for i in range(30):
        project = deepcopy(base)
        flange = project["flanges"][0]
        flange["bolt_load_W_N"] = 50_000 + i * 5_000
        flange["moment_M_Nmm"] = 500_000 + i * 100_000
        flange["flange_id"] = "F1"
        cases.append((f"F21-{i + 1:02d}", project))
    return cases
