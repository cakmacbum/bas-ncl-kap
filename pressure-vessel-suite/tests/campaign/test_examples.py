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
