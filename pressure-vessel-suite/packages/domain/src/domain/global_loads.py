"""Preliminary global wind and seismic load models.

These functions implement transparent equivalent-static loads, not a complete
ASCE 7, EN 1991/1998 or TBDY compliance check. Returned values are suitable
for load-case construction and support screening; code/site review remains
mandatory.
"""

from __future__ import annotations

from pydantic import BaseModel


class WindLoadResult(BaseModel):
    """Equivalent-static wind action on a projected vessel area."""

    velocity_m_s: float
    projected_area_m2: float
    dynamic_pressure_pa: float
    net_pressure_pa: float
    force_n: float
    moment_n_m: float
    centroid_elevation_m: float
    assumptions: tuple[str, ...] = (
        "Uniform projected area",
        "Equivalent-static resultant at area centroid",
        "Code/site gust and exposure verification required",
    )


class SeismicLoadResult(BaseModel):
    """Equivalent-static horizontal seismic action."""

    weight_n: float
    seismic_coefficient: float
    base_shear_n: float
    moment_n_m: float
    center_of_mass_elevation_m: float
    assumptions: tuple[str, ...] = (
        "Single-degree equivalent-static resultant",
        "No modal, torsional or vertical seismic effects included",
        "Site spectrum and code load combinations require review",
    )


def calculate_wind_load(
    *,
    wind_speed_m_s: float,
    projected_width_m: float,
    exposed_height_m: float,
    base_elevation_m: float = 0.0,
    air_density_kg_m3: float = 1.225,
    drag_coefficient: float = 1.2,
    gust_factor: float = 1.0,
    directionality_factor: float = 0.85,
) -> WindLoadResult:
    """Calculate a transparent preliminary wind resultant.

    ``q = 0.5*rho*V²`` and ``p = q*Cd*G*Kd``. Dimensions are SI and the
    moment is taken about the vessel base.
    """

    values = {
        "wind_speed_m_s": wind_speed_m_s,
        "projected_width_m": projected_width_m,
        "exposed_height_m": exposed_height_m,
        "air_density_kg_m3": air_density_kg_m3,
        "drag_coefficient": drag_coefficient,
        "gust_factor": gust_factor,
        "directionality_factor": directionality_factor,
    }
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    if base_elevation_m < 0:
        raise ValueError("base_elevation_m cannot be negative")

    area = projected_width_m * exposed_height_m
    q = 0.5 * air_density_kg_m3 * wind_speed_m_s**2
    pressure = q * drag_coefficient * gust_factor * directionality_factor
    force = pressure * area
    centroid = base_elevation_m + exposed_height_m / 2.0
    return WindLoadResult(
        velocity_m_s=wind_speed_m_s,
        projected_area_m2=area,
        dynamic_pressure_pa=q,
        net_pressure_pa=pressure,
        force_n=force,
        moment_n_m=force * centroid,
        centroid_elevation_m=centroid,
    )


def calculate_seismic_load(
    *,
    weight_n: float,
    seismic_acceleration_g: float,
    center_of_mass_elevation_m: float,
    importance_factor: float = 1.0,
    response_reduction_factor: float = 1.0,
) -> SeismicLoadResult:
    """Calculate preliminary equivalent-static seismic base shear.

    ``Cs = ag/g * I/R`` and ``V = Cs*W``. ``seismic_acceleration_g`` is
    entered as a fraction of gravity (for example 0.30).
    """

    for name, value in {
        "weight_n": weight_n,
        "seismic_acceleration_g": seismic_acceleration_g,
        "importance_factor": importance_factor,
        "response_reduction_factor": response_reduction_factor,
    }.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    if center_of_mass_elevation_m < 0:
        raise ValueError("center_of_mass_elevation_m cannot be negative")

    coefficient = seismic_acceleration_g * importance_factor / response_reduction_factor
    shear = coefficient * weight_n
    return SeismicLoadResult(
        weight_n=weight_n,
        seismic_coefficient=coefficient,
        base_shear_n=shear,
        moment_n_m=shear * center_of_mass_elevation_m,
        center_of_mass_elevation_m=center_of_mass_elevation_m,
    )


__all__ = ["WindLoadResult", "SeismicLoadResult", "calculate_wind_load", "calculate_seismic_load"]
