"""Clean-room arithmetic for the two test-pressure multipliers."""


def test_pressures(mawp_mpa: float, lsr: float) -> tuple[float, float]:
    """ASME VIII-1 UG-99(b), UG-100. Pressure units are preserved."""
    return 1.3 * mawp_mpa * lsr, 1.1 * mawp_mpa * lsr


def published_k1_14() -> dict:
    """K1-14: published nameplate MAWP 157 psig, LSR 1.0; gauge value unrounded."""
    return {"mawp_psig": 157.0, "lsr": 1.0, "hydro_psig": 1.3 * 157.0}
