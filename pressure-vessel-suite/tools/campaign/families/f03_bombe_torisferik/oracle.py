"""Independent UG-32(e)/Appendix 1-4(d) equations (MPa and mm)."""
from __future__ import annotations
import math


def reference(pressure_mpa: float, stress_mpa: float, efficiency: float,
              crown_radius_mm: float, knuckle_radius_mm: float) -> dict:
    if min(pressure_mpa, stress_mpa, efficiency, crown_radius_mm, knuckle_radius_mm) <= 0:
        raise ValueError("pressure, stress, efficiency, and radii must be positive")
    m = 0.25 * (3 + math.sqrt(crown_radius_mm / knuckle_radius_mm))
    required = pressure_mpa * crown_radius_mm * m / (2 * stress_mpa * efficiency - 0.2 * pressure_mpa)
    mawp = 2 * stress_mpa * efficiency * 20.0 / (crown_radius_mm * m + 0.2 * 20.0)
    return {"M":m, "required_thickness":required, "mawp":mawp}


def thickness_mawp(pressure_mpa: float, stress_mpa: float, efficiency: float,
                   crown_radius_mm: float, knuckle_radius_mm: float,
                   corroded_thickness_mm: float) -> dict:
    m = 0.25 * (3 + math.sqrt(crown_radius_mm / knuckle_radius_mm))
    required = pressure_mpa * crown_radius_mm * m / (2 * stress_mpa * efficiency - 0.2 * pressure_mpa)
    mawp = 2 * stress_mpa * efficiency * corroded_thickness_mm / (crown_radius_mm*m + 0.2*corroded_thickness_mm)
    return {"M":m, "required_thickness":required, "mawp":mawp}

