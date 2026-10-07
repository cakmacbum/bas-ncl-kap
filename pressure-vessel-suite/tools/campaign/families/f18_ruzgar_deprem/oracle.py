"""Clean-room elementary wind/seismic checks; independent of code plugins."""

def wind(speed_m_s: float, cf: float, area_m2: float, height_m: float) -> tuple[float, float]:
    """Return shear (N) and base moment (N m), uniform pressure over projected area."""
    q = 0.613 * speed_m_s ** 2
    force = q * cf * area_m2
    return force, force * height_m / 2.0


def seismic(cs: float, weight_n: float) -> float:
    return cs * weight_n


def combination(*terms: tuple[float, float]) -> float:
    return sum(value * factor for value, factor in terms)


def overturning_moment(shear_n: float, height_m: float) -> float:
    return shear_n * height_m / 2.0
