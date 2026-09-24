"""UI wiring regression for the two-material/two-junction fixture."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "apps" / "web-ui" / "src"


def test_two_material_two_weld_fixture_is_represented_by_ui_controls():
    fixture = json.loads((ROOT / "tests" / "fixtures" / "ui_two_materials_two_welds.json").read_text(encoding="utf-8"))
    pages = (UI / "pages.tsx").read_text(encoding="utf-8")
    store = (UI / "store.ts").read_text(encoding="utf-8")

    assert {m["material_id"] for m in fixture["materials"]} == {"M1", "M2"}
    assert {w["joint_id"] for w in fixture["welds"]} == {"WJ-01", "WJ-02"}
    assert "const materialOpts = project.materials.map" in pages
    assert "const weldOpts = project.welds.map" in pages
    assert "options={materialOpts}" in pages
    assert "options={[{ value: \"\", label: \"— yok —\" }, ...weldOpts]}" in pages
    assert "const hostOpts = (project.component_sequence ?? []).map" in pages
    assert "addMaterial" in store and "addWeld" in store
    assert "removeMaterial" in store and "removeWeld" in store
