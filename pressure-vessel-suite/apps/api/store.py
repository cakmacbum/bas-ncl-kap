"""Bellek-içi, sahip (owner) bazlı proje deposu (V1).

- Başkasının projesi yok gibi davranır (get/update -> None/False; çağıran 404 döner).
- Sahip başına en fazla MAX_PROJECTS_PER_OWNER proje; küresel tavan MAX_PROJECTS_GLOBAL,
  aşılınca en az yakın zamanda erişilen proje atılır (LRU).
- threading.Lock ile korunur.
"""

from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from typing import List, Tuple

from domain import VesselProject  # type: ignore

MAX_PROJECTS_PER_OWNER = 50
MAX_PROJECTS_GLOBAL = 5000


class ProjectLimitReached(Exception):
    """Sahip başına proje sınırı doldu."""


class ProjectStore:
    def __init__(self) -> None:
        # project_id -> (owner, project); sıra = LRU (sonda en yeni erişilen)
        self._items: "OrderedDict[str, Tuple[str, VesselProject]]" = OrderedDict()
        self._lock = threading.Lock()

    def create(self, owner: str, project: VesselProject) -> str:
        with self._lock:
            if sum(1 for o, _ in self._items.values() if o == owner) >= MAX_PROJECTS_PER_OWNER:
                raise ProjectLimitReached
            project_id = uuid.uuid4().hex[:12]
            self._items[project_id] = (owner, project)
            while len(self._items) > MAX_PROJECTS_GLOBAL:
                self._items.popitem(last=False)
            return project_id

    def get(self, owner: str, project_id: str) -> VesselProject | None:
        with self._lock:
            entry = self._items.get(project_id)
            if entry is None or entry[0] != owner:
                return None
            self._items.move_to_end(project_id)
            return entry[1]

    def update(self, owner: str, project_id: str, project: VesselProject) -> bool:
        with self._lock:
            entry = self._items.get(project_id)
            if entry is None or entry[0] != owner:
                return False
            self._items[project_id] = (owner, project)
            self._items.move_to_end(project_id)
            return True

    def summaries(self, owner: str) -> List[dict]:
        with self._lock:
            return [
                {
                    "id": pid,
                    "project_number": p.project_number,
                    "project_name": p.project_name,
                    "customer": p.customer,
                    "revision": p.revision,
                    "calculation_code": p.calculation_code.value,
                }
                for pid, (o, p) in self._items.items()
                if o == owner
            ]


store = ProjectStore()
