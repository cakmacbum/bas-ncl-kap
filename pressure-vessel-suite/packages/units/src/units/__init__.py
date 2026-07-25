"""Birim sistemi ve dönüşümler.

Kanonik iç birimler (SI-bazlı, basınçlı kap hesapları için pratik):
  - Uzunluk: mm
  - Basınç: MPa
  - Sıcaklık: °C
  - Alan: mm²
  - Hacim: mm³ (L olarak da gösterilir)
  - Kuvvet: N
  - Gerilme: MPa

Dış dünya ile dönüşüm fonksiyonları bu modül üzerinden yapılır.
K1 kuralı: Formüller yalnızca hesap eklentilerinde; burası yalnızca dönüşüm yapar.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Final

# ── Sabitler ──────────────────────────────────────────────────────────────────

_INCH_TO_MM: Final[float] = 25.4
_MM_TO_INCH: Final[float] = 1.0 / _INCH_TO_MM

_BAR_TO_MPA: Final[float] = 0.1
_MPA_TO_BAR: Final[float] = 10.0
_PSI_TO_MPA: Final[float] = 0.006894757293168
_MPA_TO_PSI: Final[float] = 1.0 / _PSI_TO_MPA
_ATM_TO_MPA: Final[float] = 0.101325

_KPA_TO_MPA: Final[float] = 0.001
_MPA_TO_KPA: Final[float] = 1000.0

_L_TO_MM3: Final[float] = 1_000_000.0  # 1 L = 1e6 mm³
_MM3_TO_L: Final[float] = 1.0 / _L_TO_MM3
_M3_TO_MM3: Final[float] = 1e9
_MM3_TO_M3: Final[float] = 1e-9
_IN3_TO_MM3: Final[float] = _INCH_TO_MM ** 3  # 16387.064
_MM3_TO_IN3: Final[float] = 1.0 / _IN3_TO_MM3

_M2_TO_MM2: Final[float] = 1e6
_MM2_TO_M2: Final[float] = 1e-6
_IN2_TO_MM2: Final[float] = _INCH_TO_MM ** 2  # 645.16
_MM2_TO_IN2: Final[float] = 1.0 / _IN2_TO_MM2

_M_TO_MM: Final[float] = 1000.0
_MM_TO_M: Final[float] = 0.001


# ── Enum'lar ──────────────────────────────────────────────────────────────────

class PressureUnit(str, Enum):
    MPA = "MPa"
    BAR = "bar"
    PSI = "psi"
    KPA = "kPa"
    ATM = "atm"
    PA = "Pa"


class TemperatureUnit(str, Enum):
    C = "°C"
    K = "K"
    F = "°F"


class LengthUnit(str, Enum):
    MM = "mm"
    M = "m"
    IN = "in"
    FT = "ft"


class AreaUnit(str, Enum):
    MM2 = "mm²"
    M2 = "m²"
    IN2 = "in²"


class VolumeUnit(str, Enum):
    MM3 = "mm³"
    M3 = "m³"
    L = "L"
    IN3 = "in³"


class ForceUnit(str, Enum):
    N = "N"
    KN = "kN"
    LBF = "lbf"


# ── Dönüşüm fonksiyonları ─────────────────────────────────────────────────────

def convert_pressure(value: float, from_unit: PressureUnit, to_unit: PressureUnit) -> float:
    """Basınç birimi dönüşümü."""
    mpa = _to_mpa(value, from_unit)
    return _from_mpa(mpa, to_unit)


def _to_mpa(value: float, unit: PressureUnit) -> float:
    if unit == PressureUnit.MPA:
        return value
    if unit == PressureUnit.BAR:
        return value * _BAR_TO_MPA
    if unit == PressureUnit.PSI:
        return value * _PSI_TO_MPA
    if unit == PressureUnit.KPA:
        return value * _KPA_TO_MPA
    if unit == PressureUnit.ATM:
        return value * _ATM_TO_MPA
    if unit == PressureUnit.PA:
        return value * 1e-6
    raise ValueError(f"Bilinmeyen basınç birimi: {unit}")


def _from_mpa(mpa: float, unit: PressureUnit) -> float:
    if unit == PressureUnit.MPA:
        return mpa
    if unit == PressureUnit.BAR:
        return mpa * _MPA_TO_BAR
    if unit == PressureUnit.PSI:
        return mpa * _MPA_TO_PSI
    if unit == PressureUnit.KPA:
        return mpa * _MPA_TO_KPA
    if unit == PressureUnit.ATM:
        return mpa / _ATM_TO_MPA
    if unit == PressureUnit.PA:
        return mpa * 1e6
    raise ValueError(f"Bilinmeyen basınç birimi: {unit}")


def convert_temperature(value: float, from_unit: TemperatureUnit, to_unit: TemperatureUnit) -> float:
    """Sıcaklık birimi dönüşümü."""
    celsius = _to_celsius(value, from_unit)
    return _from_celsius(celsius, to_unit)


def _to_celsius(value: float, unit: TemperatureUnit) -> float:
    if unit == TemperatureUnit.C:
        return value
    if unit == TemperatureUnit.K:
        return value - 273.15
    if unit == TemperatureUnit.F:
        return (value - 32.0) * 5.0 / 9.0
    raise ValueError(f"Bilinmeyen sıcaklık birimi: {unit}")


def _from_celsius(celsius: float, unit: TemperatureUnit) -> float:
    if unit == TemperatureUnit.C:
        return celsius
    if unit == TemperatureUnit.K:
        return celsius + 273.15
    if unit == TemperatureUnit.F:
        return celsius * 9.0 / 5.0 + 32.0
    raise ValueError(f"Bilinmeyen sıcaklık birimi: {unit}")


def convert_length(value: float, from_unit: LengthUnit, to_unit: LengthUnit) -> float:
    """Uzunluk birimi dönüşümü."""
    mm = _to_mm_length(value, from_unit)
    return _from_mm_length(mm, to_unit)


def _to_mm_length(value: float, unit: LengthUnit) -> float:
    if unit == LengthUnit.MM:
        return value
    if unit == LengthUnit.M:
        return value * _M_TO_MM
    if unit == LengthUnit.IN:
        return value * _INCH_TO_MM
    if unit == LengthUnit.FT:
        return value * _INCH_TO_MM * 12.0
    raise ValueError(f"Bilinmeyen uzunluk birimi: {unit}")


def _from_mm_length(mm: float, unit: LengthUnit) -> float:
    if unit == LengthUnit.MM:
        return mm
    if unit == LengthUnit.M:
        return mm * _MM_TO_M
    if unit == LengthUnit.IN:
        return mm * _MM_TO_INCH
    if unit == LengthUnit.FT:
        return mm * _MM_TO_INCH / 12.0
    raise ValueError(f"Bilinmeyen uzunluk birimi: {unit}")


def convert_area(value: float, from_unit: AreaUnit, to_unit: AreaUnit) -> float:
    """Alan birimi dönüşümü."""
    mm2 = _to_mm2(value, from_unit)
    return _from_mm2(mm2, to_unit)


def _to_mm2(value: float, unit: AreaUnit) -> float:
    if unit == AreaUnit.MM2:
        return value
    if unit == AreaUnit.M2:
        return value * _M2_TO_MM2
    if unit == AreaUnit.IN2:
        return value * _IN2_TO_MM2
    raise ValueError(f"Bilinmeyen alan birimi: {unit}")


def _from_mm2(mm2: float, unit: AreaUnit) -> float:
    if unit == AreaUnit.MM2:
        return mm2
    if unit == AreaUnit.M2:
        return mm2 * _MM2_TO_M2
    if unit == AreaUnit.IN2:
        return mm2 * _MM2_TO_IN2
    raise ValueError(f"Bilinmeyen alan birimi: {unit}")


def convert_volume(value: float, from_unit: VolumeUnit, to_unit: VolumeUnit) -> float:
    """Hacim birimi dönüşümü."""
    mm3 = _to_mm3(value, from_unit)
    return _from_mm3(mm3, to_unit)


def _to_mm3(value: float, unit: VolumeUnit) -> float:
    if unit == VolumeUnit.MM3:
        return value
    if unit == VolumeUnit.M3:
        return value * _M3_TO_MM3
    if unit == VolumeUnit.L:
        return value * _L_TO_MM3
    if unit == VolumeUnit.IN3:
        return value * _IN3_TO_MM3
    raise ValueError(f"Bilinmeyen hacim birimi: {unit}")


def _from_mm3(mm3: float, unit: VolumeUnit) -> float:
    if unit == VolumeUnit.MM3:
        return mm3
    if unit == VolumeUnit.M3:
        return mm3 * _MM3_TO_M3
    if unit == VolumeUnit.L:
        return mm3 * _MM3_TO_L
    if unit == VolumeUnit.IN3:
        return mm3 * _MM3_TO_IN3
    raise ValueError(f"Bilinmeyen hacim birimi: {unit}")


# ── Yuvarlama yardımcıları ────────────────────────────────────────────────────

def round_to(value: float, decimals: int = 2) -> float:
    """Belirli ondalık basamağa yuvarla (standart round)."""
    return round(value, decimals)


def round_up_to_nearest(value: float, step: float) -> float:
    """Değeri step'in katına yukarı yuvarla.

    Sac kalınlığı gibi değerlerde kullanılır: 7.42 → step=0.5 → 7.5
    """
    if step <= 0:
        raise ValueError("step sıfırdan büyük olmalı")
    return math.ceil(value / step) * step


def round_down_to_nearest(value: float, step: float) -> float:
    """Değeri step'in katına aşağı yuvarla."""
    if step <= 0:
        raise ValueError("step sıfırdan büyük olmalı")
    return math.floor(value / step) * step


# ── Tolerans kontrolü ────────────────────────────────────────────────────────

def within_tolerance(actual: float, expected: float, tolerance: float) -> bool:
    """İki değer tolerans dahilinde mi? (mutlak tolerans ±)"""
    return abs(actual - expected) <= tolerance


def relative_tolerance(actual: float, expected: float, rel_tol: float = 0.001) -> bool:
    """Göreceli tolerans kontrolü (varsayılan %0.1)."""
    if expected == 0.0:
        return abs(actual) <= rel_tol
    return abs(actual - expected) / abs(expected) <= rel_tol


__all__ = [
    "PressureUnit",
    "TemperatureUnit",
    "LengthUnit",
    "AreaUnit",
    "VolumeUnit",
    "ForceUnit",
    "convert_pressure",
    "convert_temperature",
    "convert_length",
    "convert_area",
    "convert_volume",
    "round_to",
    "round_up_to_nearest",
    "round_down_to_nearest",
    "within_tolerance",
    "relative_tolerance",
]
