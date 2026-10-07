"""Independent UG-28 arithmetic using user-supplied A and B values."""
from __future__ import annotations


def shell_allowable_pressure(b_mpa: float, outside_diameter_mm: float,
                             thickness_mm: float) -> float:
    # UG-28(c)(1): Pa = 4B / (3 Do/t); MPa is retained throughout.
    return 4.0 * b_mpa / (3.0 * outside_diameter_mm / thickness_mm)


def shell_a_parameter(length_mm: float, outside_diameter_mm: float,
                      thickness_mm: float) -> float | None:
    ld = length_mm / outside_diameter_mm
    dt = outside_diameter_mm / thickness_mm
    # UG-28(c)(2) chart procedure applies in the usual chart geometry range.
    if ld < 0.5 or ld > 50 or dt < 10 or dt > 1000:
        return None
    # A is a chart input. Never infer it from a copyrighted chart.
    return None


def head_allowable_pressure(b_mpa: float, outside_diameter_mm: float,
                            thickness_mm: float) -> float:
    # UG-33 spherical-head equation shares the 4B/(3Do/t) pressure relation.
    return shell_allowable_pressure(b_mpa, outside_diameter_mm, thickness_mm)
