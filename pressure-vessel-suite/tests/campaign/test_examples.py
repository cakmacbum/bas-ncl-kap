from __future__ import annotations

import inspect

from tools.campaign import examples
from tools.campaign.harness import run_case


def test_each_example_reaches_its_calculation_type():
    for name, factory in inspect.getmembers(examples, inspect.isfunction):
        if not name.startswith("example_"):
            continue
        target = name.removeprefix("example_")
        outcome = run_case(factory())
        assert outcome["ok"], f"{name}: {outcome['error']}"
        matches = [r for r in outcome["payload"]["results"]
                   if r.get("calculation_type") == target]
        assert matches, f"{name}: no {target} row emitted"
        assert all(r.get("status") not in {"BLOCKED MISSING INPUT", "BLOCKED CODE DATA",
                                           "NOT CALCULATED"} for r in matches), name


def test_catalogued_unreachable_types_have_no_false_example():
    names = {name.removeprefix("example_") for name, _ in
             inspect.getmembers(examples, inspect.isfunction) if name.startswith("example_")}
    # These are documented with source locations in RESULT_CATALOG.md: the current
    # route cannot emit a usable row of the requested type for these cases.
    assert not names.intersection({"material_check", "fatigue", "flange",
        "external_pressure_check", "vacuum_stability", "load_combination"})


def test_static_head_and_ratio_input_contracts():
    mawp = examples.example_mawp()
    assert mawp["design_conditions"]["fluid_density_kg_m3"] > 0
    assert mawp["load_cases"][0]["fluid_level_mm"] > 0
    assert mawp["load_cases"][0]["fluid_density_kg_m3"] > 0
    # No coincident-load-ratio field is currently modeled; its absence is
    # recorded as a source-backed limitation in the catalog.
