"""Independent UG-34(c)(2) calculation; no code implementation dependencies."""
from __future__ import annotations


def required_thickness(d_mm: float, pressure_mpa: float, allowable_mpa: float,
                       efficiency: float, c_factor: float, corrosion_mm: float = 0.0,
                       *, bolt_load_n: float = 0.0, gasket_reaction_diameter_mm: float = 0.0) -> float:
    # t = d*sqrt(CP/SE + 1.9 W hG/(S E d^3)) + CA
    term = c_factor * pressure_mpa / (allowable_mpa * efficiency)
    term += 1.9 * bolt_load_n * gasket_reaction_diameter_mm / (
        allowable_mpa * efficiency * d_mm**3)
    return d_mm * term**0.5 + corrosion_mm


def reference_cases() -> dict:
    # K1-05, COMPRESS Demo Vessel, published value 0.7589 in; CA=0.
    return {"PUBLISHED-K1-05": {
        "d_mm": 609.6, "pressure_mpa": 100 * 0.006894757293168361,
        "allowable_mpa": 20000 * 0.006894757293168361, "efficiency": 1.0,
        "c_factor": .2, "corrosion_mm": 0.0, "published_mm": .7589 * 25.4,
        "source": "K1-05 Codeware COMPRESS Demo Vessel, 2022, pp. 16-17",
    }}
