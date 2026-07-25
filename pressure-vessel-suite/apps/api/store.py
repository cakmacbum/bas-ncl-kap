"""Basit bellek-içi proje deposu (V1).

Projeler bellekte + isteğe bağlı JSON dosyasında tutulur. SQLite V1'de şart değil.
"""

from __future__ import annotations

import uuid
from typing import Dict, List

from domain import VesselProject  # type: ignore


class ProjectStore:
    """Bellek-içi VesselProject deposu."""

    def __init__(self) -> None:
        self._items: Dict[str, VesselProject] = {}

    def create(self, project: VesselProject) -> str:
        project_id = uuid.uuid4().hex[:12]
        self._items[project_id] = project
        return project_id

    def get(self, project_id: str) -> VesselProject | None:
        return self._items.get(project_id)

    def update(self, project_id: str, project: VesselProject) -> bool:
        if project_id not in self._items:
            return False
        self._items[project_id] = project
        return True

    def list_ids(self) -> List[str]:
        return list(self._items.keys())

    def summaries(self) -> List[dict]:
        return [
            {
                "id": pid,
                "project_number": p.project_number,
                "project_name": p.project_name,
                "customer": p.customer,
                "revision": p.revision,
                "calculation_code": p.calculation_code.value,
            }
            for pid, p in self._items.items()
        ]


store = ProjectStore()
