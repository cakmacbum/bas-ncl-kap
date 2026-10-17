from math import sqrt


def oracle(params):
    """Independent plate bearing and cantilever strip checks (mm, MPa, N)."""
    length, width, fy, reaction, footprint = (
        params[key] for key in ("L", "W", "Fy", "N", "footprint")
    )
    q = reaction / (length * width)
    m = max((length - 0.8 * footprint) / 2, 0.0)
    n = max((width - 0.8 * footprint) / 2, 0.0)
    cantilever = max(m, n)
    required = cantilever * sqrt(3 * q / (0.75 * fy)) if fy else None
    return {"t_required": required, "bearing_pressure_q": q}
