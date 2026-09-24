"""CAD scope must reject multi-component chains before building partial solids."""

import json
from pathlib import Path
from types import SimpleNamespace

from cad_engine.vessel_builder import build_vessel


ROOT = Path(__file__).resolve().parents[2]


def test_five_component_chain_is_explicitly_out_of_scope_for_exact_cad():
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "ui_five_component_geometry.json").read_text(
            encoding="utf-8"
        )
    )
    project = SimpleNamespace(
        shell_sections=[SimpleNamespace(**item) for item in fixture["shells"]],
        heads=[SimpleNamespace(**item) for item in fixture["heads"]],
        cones=[SimpleNamespace(**item) for item in fixture["cones"]],
        component_sequence=[SimpleNamespace(**item) for item in fixture["component_sequence"]],
    )

    result = build_vessel(project)

    assert result.scope_status == "OUT_OF_SCOPE"
    assert result.shape is None
    assert result.error and "OUT_OF_SCOPE" in result.error
    assert "yaklaşık STEP/STL üretilmedi" in result.error
