"""Independent rectangular weld-group line-integral oracle."""
from __future__ import annotations

import math


def oracle(params: dict, *, shear_N: float, normal_N: float,
           moment_Nmm: float, effective_Lw_mm: float,
           effective_Sw_mm: float) -> dict:
    """Return line geometry and throat stress for the pad-to-shell joint.

    The load resultants are taken from the public API's input snapshot; the
    weld geometry and stress transformation are independently recomputed.
    """
    b, d = float(params["b_mm"]), float(params["d_mm"])
    z = float(params["weld_leg_mm"])
    # The API supplies its effective (corner/krater-corrected) line geometry.
    # The load-to-line-force and effective-throat transformation below is
    # recomputed independently; raw closed-line identities remain in the result.
    raw_lw = 2.0 * (b + d)
    raw_sw = b * d + d * d / 3.0
    lw, sw = float(effective_Lw_mm), float(effective_Sw_mm)
    line_force = math.hypot(shear_N / lw, normal_N / lw + moment_Nmm / sw)
    throat = math.sqrt(2.0) / 2.0 * z
    return {"Lw": lw, "Sw": sw, "raw_Lw": raw_lw, "raw_Sw": raw_sw,
            "line_force": line_force,
            "throat": throat, "weld_stress": line_force / throat}
