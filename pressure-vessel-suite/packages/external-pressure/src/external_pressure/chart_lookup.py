"""UG-28/UG-33 chart lookup without extrapolation.

Chart ordinates are supplied by the licensed project data pack. The engine only
performs bounded interpolation and records the source/edition in the caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from materials.interpolation import linear_interpolate


@dataclass(frozen=True)
class ChartLookupResult:
    value: float
    chart: str
    edition: str
    lower: float
    upper: float


def lookup_chart(x: float, points: Iterable[tuple[float, float]], *, chart: str, edition: str) -> ChartLookupResult:
    ordered = sorted((float(a), float(b)) for a, b in points)
    if len(ordered) < 2:
        raise ValueError("A chart needs at least two data points")
    if x < ordered[0][0] or x > ordered[-1][0]:
        raise LookupError(f"{chart} value {x:g} is outside chart range {ordered[0][0]:g}..{ordered[-1][0]:g}")
    value = linear_interpolate(x, [a for a, _ in ordered], [b for _, b in ordered])
    lower = max(a for a, _ in ordered if a <= x)
    upper = min(a for a, _ in ordered if a >= x)
    return ChartLookupResult(value, chart, edition, lower, upper)


__all__ = ["ChartLookupResult", "lookup_chart"]
