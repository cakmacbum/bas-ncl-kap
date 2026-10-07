"""Independent thin-wall skirt stress calculations in SI units."""
from __future__ import annotations

import math


def axial_stress(weight_n: float, moment_nmm: float, diameter_mm: float, thickness_mm: float) -> float:
    """Maximum absolute axial extreme-fiber stress, MPa: W/A +/- M/Z."""
    area = math.pi * diameter_mm * thickness_mm
    section_modulus = math.pi * diameter_mm**2 * thickness_mm / 4.0
    return abs(weight_n / area) + abs(moment_nmm / section_modulus)


def weld_stress(weight_n: float, moment_nmm: float, diameter_mm: float,
                thickness_mm: float, efficiency: float) -> float:
    """Tensile-side membrane plus bending stress divided by weld efficiency."""
    section_modulus = math.pi * diameter_mm**2 * thickness_mm / 4.0
    tensile = max(0.0, -weight_n / (math.pi * diameter_mm * thickness_mm)
                  + moment_nmm / section_modulus)
    return tensile / efficiency
