"""Independent arithmetic for UG-99(b) plus hydrostatic liquid head."""
G = 9.80665


def static_head_mpa(density_kg_m3: float, height_mm: float) -> float:
    return density_kg_m3 * G * height_mm / 1_000_000_000.0


def ug99_pressure(mawp_mpa: float, stress_ratio: float) -> float:
    return 1.3 * mawp_mpa * stress_ratio
