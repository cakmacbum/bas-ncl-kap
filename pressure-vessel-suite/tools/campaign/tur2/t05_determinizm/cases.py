"""Determinism campaign inputs built from the shared valid tank fixture."""
from __future__ import annotations

from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank


def cases():
    """Yield twenty distinct, stable project payloads."""
    for index in range(1, 21):
        project = vertical_leg_tank()
        project["project_number"] = f"T05-{index:02d}"
        project["project_name"] = f"Determinism case {index:02d}"
        yield {"case_id": f"T05-{index:02d}", "project": project}


def permuted(project: dict) -> dict:
    """Reverse list ordering for the requested input collections."""
    result = deepcopy(project)
    for field in ("nozzles", "welds", "materials"):
        if isinstance(result.get(field), list):
            result[field].reverse()
    return result
