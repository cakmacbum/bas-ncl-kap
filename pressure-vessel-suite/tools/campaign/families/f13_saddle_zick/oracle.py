"""Independent elementary beam and thin-shell checks, with API inputs explicit."""
from math import pi


def calculate(*, M1_Nmm, M2_Nmm, R_m_mm, t_corroded_mm, K1):
    """Return the two longitudinal bending stresses (N/mm2 = MPa).

    The saddle bending coefficient K1 is passed explicitly; this oracle does
    not contain a coefficient table or infer one from geometry.
    """
    if min(R_m_mm, t_corroded_mm, K1) <= 0:
        raise ValueError("positive radius, thickness, and K1 required")
    area_moment_scale = R_m_mm * R_m_mm * t_corroded_mm
    return {
        "S1_saddle": abs(M1_Nmm) / (K1 * area_moment_scale),
        "S1_midspan": abs(M2_Nmm) / (pi * area_moment_scale),
    }
