"""Statik kafa hesabı — hidrostatik basınç düzeltmesi (kaynak §19).

K1 kuralı: Formül burada yazılır; orchestrator yalnızca çağırır.
"""

from __future__ import annotations


def static_head_pressure(
    fluid_density_kg_m3: float,
    height_mm: float,
    gravity_m_s2: float = 9.80665,
) -> float:
    """Statik sıvı basıncı hesabı.

    ΔP = ρ × g × h

    Args:
        fluid_density_kg_m3: Sıvı yoğunluğu (kg/m³).
        height_mm: Sıvı yüksekliği (mm).
        gravity_m_s2: Yerçekimi ivmesi (m/s²). Varsayılan: 9.80665.

    Returns:
        Statik basınç (MPa).

    Referans: Hidrostatik temel formül
    """
    if fluid_density_kg_m3 < 0:
        raise ValueError("Sıvı yoğunluğu negatif olamaz")
    if height_mm < 0:
        raise ValueError("Yükseklik negatif olamaz")

    # mm → m dönüşümü
    height_m = height_mm / 1000.0

    # Pa → MPa dönüşümü
    pressure_pa = fluid_density_kg_m3 * gravity_m_s2 * height_m
    pressure_mpa = pressure_pa / 1e6

    return pressure_mpa


__all__ = ["static_head_pressure"]
