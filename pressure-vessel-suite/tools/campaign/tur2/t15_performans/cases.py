"""Deterministic 100-project load set for T15."""
from __future__ import annotations

from tools.campaign.bases import vertical_leg_tank


def cases(count: int = 100) -> list[tuple[str, dict]]:
    rows = []
    for index in range(count):
        pressure = 0.8 + index * 0.01
        project = vertical_leg_tank()
        project["project_number"] = f"T15-P{index:03d}"
        project["project_name"] = f"T15 performance project {index:03d}"
        project["design_conditions"]["design_pressure"] = pressure
        rows.append((f"T15-{index:03d}", project))
    return rows
