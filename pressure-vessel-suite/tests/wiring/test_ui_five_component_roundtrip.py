"""Five component fixture coverage for the web UI list/load contract."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_five_component_fixture_survives_ui_list_and_load_wiring():
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "vessel_project_five_component.json").read_text(encoding="utf-8")
    )
    ui = ROOT / "apps" / "web-ui" / "src"
    api = (ui / "api.ts").read_text(encoding="utf-8")
    pages = (ui / "pages.tsx").read_text(encoding="utf-8")
    store = (ui / "store.ts").read_text(encoding="utf-8")

    ids = [(entry["component_type"], entry["component_id"]) for entry in fixture["component_sequence"]]
    assert ids == [
        ("head", "HEAD-L"), ("shell", "SHELL-01"), ("cone", "CONE-01"),
        ("shell", "SHELL-02"), ("head", "HEAD-R"),
    ]
    assert len(fixture["materials"]) >= 2
    assert len(fixture["welds"]) >= 2

    # The UI presents server summaries, fetches the selected VesselProject, and
    # hydrates the store through normalizeProject without collapsing its arrays.
    assert "async listProjects()" in api and 'fetchJson(`${BASE}/projects`)' in api
    assert "async getProject(id: string)" in api
    assert "api.listProjects()" in pages and "api.getProject(id)" in pages
    assert "loadProject(id, await api.getProject(id))" in pages
    assert "project: normalizeProject(project)" in store
    for collection in ("shell_sections", "heads", "cones", "materials", "welds", "component_sequence"):
        assert collection in store
