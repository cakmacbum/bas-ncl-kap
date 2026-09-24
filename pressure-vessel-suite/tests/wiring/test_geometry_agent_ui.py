"""Geometry-agent UI stays review-only and globally reachable."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "apps" / "web-ui" / "src"


def read(name: str) -> str:
    return (SRC / name).read_text(encoding="utf-8")


def test_agent_drawer_is_global_and_requires_confirmation():
    app = read("App.tsx")
    drawer = read("GeometryAgentDrawer.tsx")
    assert "<GeometryAgentDrawer" in app
    assert "Değişiklikleri Uygula" in drawer
    assert "setProject((current) => applyGeometryAgentChanges" in drawer
    assert "api.interpretGeometry" in drawer


def test_agent_patch_preserves_unmentioned_project_fields():
    patcher = read("geometryAgent.ts")
    assert "let next = project" in patcher
    assert 'target_type === "shell"' in patcher
    assert 'target_type === "vessel"' in patcher
    assert "materials" not in patcher
    assert "nozzles" not in patcher
