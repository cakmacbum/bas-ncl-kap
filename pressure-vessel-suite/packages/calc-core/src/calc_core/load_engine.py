"""Global yük toplama ve yük zarfı yardımcıları.

Bu modül kod standardı katsayılarını uygulamaz; proje girdilerindeki kuvvet ve
momentleri ortak bir referans kota taşır. Böylece rüzgâr/deprem veya destek
hesapları bağlanmadan önce dahi yük kaybı ve yanlış kombinasyon sessizce PASS
üretemez. Birimler N, N-mm ve mm'dir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Iterable, Mapping, Sequence

from domain.load_cases import (
    ExternalLoad,
    LoadCase,
    LoadCombination,
    LoadType,
    validate_load_combination,
)


@dataclass(frozen=True)
class GlobalLoadState:
    """Bir yük durumu veya kombinasyonunun referans kota indirgenmiş zarfı."""

    load_case_ids: tuple[str, ...]
    axial_force_n: float = 0.0
    shear_x_n: float = 0.0
    shear_y_n: float = 0.0
    overturning_moment_x_nmm: float = 0.0
    overturning_moment_y_nmm: float = 0.0
    torsional_moment_z_nmm: float = 0.0
    elevation_min_mm: float | None = None
    elevation_max_mm: float | None = None
    assumptions: tuple[str, ...] = ()

    @property
    def resultant_shear_n(self) -> float:
        return (self.shear_x_n**2 + self.shear_y_n**2) ** 0.5

    @property
    def resultant_overturning_moment_nmm(self) -> float:
        return (
            self.overturning_moment_x_nmm**2
            + self.overturning_moment_y_nmm**2
        ) ** 0.5


def _check_finite(value: float, name: str) -> float:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _shift_external_load(load: ExternalLoad, base_elevation_mm: float) -> tuple[float, ...]:
    """Momenti, kuvvetin uygulama kotundan taban referansına taşır."""
    dz = _check_finite(load.elevation_mm - base_elevation_mm, "elevation")
    fx, fy, fz = load.fx_n, load.fy_n, load.fz_n
    # r=(0,0,dz), M_base=M_at_point+r×F.
    return (
        fx,
        fy,
        fz,
        load.mx_nmm - dz * fy,
        load.my_nmm + dz * fx,
        load.mz_nmm,
    )


def aggregate_load_case(
    load_case: LoadCase,
    *,
    base_elevation_mm: float = 0.0,
    extra_loads: Iterable[ExternalLoad] = (),
) -> GlobalLoadState:
    """Bir LoadCase içindeki tüm 6-bileşenli yükleri tek zarf hâline getirir.

    `extra_loads`, ekipman/platform/izolasyon/boru gibi proje ağırlıklarının
    bileşen kotlarıyla açıkça eklenmesi içindir. Ağırlık kuvveti `fz_n` ile
    negatif yönde verilmelidir; modül işaret değiştirmez.
    """
    loads = [*load_case.external_loads, *extra_loads]
    sums = [0.0] * 6
    elevations: list[float] = []
    for load in loads:
        values = _shift_external_load(load, base_elevation_mm)
        for i, value in enumerate(values):
            sums[i] += _check_finite(value, f"load component {i}")
        elevations.append(load.elevation_mm)

    assumptions = []
    if load_case.load_type in (LoadType.WIND, LoadType.SEISMIC):
        assumptions.append(
            f"{load_case.load_type.value} code coefficients are not applied by the generic engine; "
            "component forces must come from a verified code module."
        )
    if not loads:
        assumptions.append("No component loads supplied; global envelope is zero and requires review.")

    return GlobalLoadState(
        load_case_ids=(load_case.load_case_id,),
        axial_force_n=sums[2],
        shear_x_n=sums[0],
        shear_y_n=sums[1],
        overturning_moment_x_nmm=sums[3],
        overturning_moment_y_nmm=sums[4],
        torsional_moment_z_nmm=sums[5],
        elevation_min_mm=min(elevations) if elevations else None,
        elevation_max_mm=max(elevations) if elevations else None,
        assumptions=tuple(assumptions),
    )


def combine_load_cases(
    cases: Mapping[str, LoadCase],
    combination: LoadCombination,
    *,
    base_elevation_mm: float = 0.0,
) -> GlobalLoadState:
    """Kombinasyon faktörleriyle global kuvvet/moment zarfını üretir.

    Eksik case veya eksik faktör sessizce 1.0 kabul edilmez; bu, Faz C'nin
    temel veri-kaybı güvenlik kuralı olarak açık hata üretir.
    """
    missing = [case_id for case_id in combination.load_case_ids if case_id not in cases]
    if missing:
        raise ValueError(f"Load combination references missing cases: {', '.join(missing)}")
    unknown_factors = set(combination.load_factors) - set(combination.load_case_ids)
    if unknown_factors:
        raise ValueError(f"Load combination has factors for unknown cases: {sorted(unknown_factors)}")
    validation_errors = validate_load_combination(list(cases.values()), combination)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))

    states = []
    for case_id in combination.load_case_ids:
        factor = combination.load_factors.get(case_id, 1.0)
        _check_finite(float(factor), f"factor {case_id}")
        state = aggregate_load_case(cases[case_id], base_elevation_mm=base_elevation_mm)
        states.append((float(factor), state))

    assumptions = [f"Combination {combination.combination_id}: {combination.name}"]
    for factor, state in states:
        assumptions.extend(state.assumptions)
        assumptions.append(f"Load case factor applied: {state.load_case_ids[0]} × {factor:g}")
    return GlobalLoadState(
        load_case_ids=tuple(combination.load_case_ids),
        axial_force_n=sum(f * s.axial_force_n for f, s in states),
        shear_x_n=sum(f * s.shear_x_n for f, s in states),
        shear_y_n=sum(f * s.shear_y_n for f, s in states),
        overturning_moment_x_nmm=sum(f * s.overturning_moment_x_nmm for f, s in states),
        overturning_moment_y_nmm=sum(f * s.overturning_moment_y_nmm for f, s in states),
        torsional_moment_z_nmm=sum(f * s.torsional_moment_z_nmm for f, s in states),
        assumptions=tuple(assumptions),
    )


def governing_state(states: Sequence[GlobalLoadState]) -> GlobalLoadState | None:
    """En büyük bileşke kesme + devrilme momenti zarfını seçer."""
    return max(
        states,
        key=lambda state: (state.resultant_shear_n, state.resultant_overturning_moment_nmm),
        default=None,
    )


__all__ = ["GlobalLoadState", "aggregate_load_case", "combine_load_cases", "governing_state"]
