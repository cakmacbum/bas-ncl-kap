"""Independent line integral identities; WRC cases test dimensions only."""
from __future__ import annotations

import math


def oracle(params: dict) -> dict:
    b, d = params.get("b_mm"), params.get("d_mm")
    if params.get("invalid") or not isinstance(b, (int, float)) or not isinstance(d, (int, float)) or b <= 0 or d <= 0:
        return {"Lw": None, "Sw": None, "Jw": None, "weld_stress": None}
    if params["shape"] == "circle":
        length = math.pi * b
        sw = math.pi * b * b / 4
    else:
        length = 2 * (b + d)
        sw = b * d + d * d / 3
    # Isotropic polar line integral for the closed circle/rectangle. It is a
    # geometric descriptor, not the directional section modulus Sw.
    jw = (math.pi * b**3 / 4 if params["shape"] == "circle"
          else (b**3 + d**3) / 3 + b * d * (b + d) / 2)
    return {"Lw": length, "Sw": sw, "Jw": jw, "weld_stress": None}
