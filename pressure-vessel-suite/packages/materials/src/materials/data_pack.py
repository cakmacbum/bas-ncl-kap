"""Sürümlü malzeme veri paketi yardımcıları.

ASME tablo içeriği uygulamaya gömülmez; lisanslı veri dışarıdan alınır,
checksum'lanır ve proje snapshot'ında saklanır.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable

from materials.interpolation import linear_interpolate


@dataclass(frozen=True)
class MaterialDataPack:
    standard: str
    edition: str
    source: str
    records: tuple[dict[str, Any], ...]
    checksum: str

    @classmethod
    def from_records(cls, standard: str, edition: str, records: Iterable[dict[str, Any]], source: str = ""):
        frozen = tuple(dict(r) for r in records)
        payload = json.dumps(frozen, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        return cls(standard, edition, source, frozen, hashlib.sha256(payload).hexdigest())

    def snapshot(self) -> dict[str, Any]:
        return {"standard": self.standard, "edition": self.edition, "source": self.source,
                "checksum": self.checksum, "records": [dict(r) for r in self.records]}


def interpolate_pack_property(points: Iterable[tuple[float, float]], temperature_c: float) -> float:
    """Verilen tablo aralığında interpolasyon yapar; ekstrapolasyon yapmaz."""
    data = sorted((float(t), float(v)) for t, v in points)
    if not data or temperature_c < data[0][0] or temperature_c > data[-1][0]:
        raise LookupError("Temperature is outside the material data-pack range")
    return linear_interpolate(temperature_c, [x for x, _ in data], [y for _, y in data])


__all__ = ["MaterialDataPack", "interpolate_pack_property"]
