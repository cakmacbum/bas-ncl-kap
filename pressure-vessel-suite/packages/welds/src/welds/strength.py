"""Köşe kaynağı dayanım formülleri.

`validator.py` kaynağın belge/NDT uygunluğunu denetler; bu modül ise kaynağın
yük taşıma kapasitesini hesaplar. Destek (ayak/ped/taban plakası) ve ileride
nozul bağlantı kaynakları için ortak kullanılır.

Yöntem: kaynak "çizgi" olarak modellenir (birim boğaz kalınlığı); kaynak
grubunun uzunluğu ve kesit modülü geometriden çıkar, birim boy kuvvetleri
bileşke olarak toplanır, sonra gerçek boğaz kalınlığına bölünür.

K6 kuralı: AWS D1.1 asgari köşe kaynağı bacağı tablosu gömülmez — gerekirse
`min_leg_mm` kullanıcıdan gelir; verilmezse kontrol yapılmaz ve bu durum
sonuçta açıkça belirtilir.

Referanslar:
- AWS D1.1, Structural Welding Code — Steel (köşe kaynağı izin verilen kayma
  gerilmesi 0,30·Fexx, etkin boğaz)
- Blodgett, O.W., *Design of Welded Structures* (1966), §7.4 — kaynağı çizgi
  kabul eden grup özellikleri
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

# Eşit bacaklı 45° köşe kaynağında boğaz/bacak oranı (√2/2 ≈ 0,707).
FILLET_THROAT_RATIO = math.sqrt(0.5)
# AWS D1.1: köşe kaynağı etkin boğazında izin verilen kayma = 0,30 × Fexx.
FILLET_ALLOWABLE_SHEAR_FACTOR = 0.30


def fillet_throat(leg: float) -> float:
    """Etkin boğaz a = 0,707 × z."""
    if leg <= 0:
        raise ValueError(f"Kaynak bacağı pozitif olmalı: {leg}")
    return FILLET_THROAT_RATIO * leg


def fillet_effective_length(length: float, leg: float) -> float:
    """Krater düzeltmeli etkin boy L_eff = L − 2z (her iki uçta bir bacak boyu)."""
    if length <= 0 or leg <= 0:
        raise ValueError(f"length ve leg pozitif olmalı: {length}, {leg}")
    L_eff = length - 2.0 * leg
    if L_eff <= 0:
        raise ValueError(f"Kaynak boyu ({length}) krater düzeltmesinden (2z={2 * leg}) kısa")
    return L_eff


def fillet_allowable_shear(Fexx: float) -> float:
    """Boğazda izin verilen kayma gerilmesi = 0,30 × Fexx (MPa)."""
    if Fexx <= 0:
        raise ValueError(f"Fexx pozitif olmalı: {Fexx}")
    return FILLET_ALLOWABLE_SHEAR_FACTOR * Fexx


# ── Kaynak grubu özellikleri (çizgi kaynak) ───────────────────────────────────

@dataclass(frozen=True)
class WeldGroup:
    """Çizgi kaynak grubu: toplam boy L_w (mm) ve eğilme kesit modülü S_w (mm²)."""

    L_w: float
    S_w: float


def weld_group_rectangle(b: float, d: float) -> WeldGroup:
    """Dört kenardan çevre kaynağı (ör. ped → gövde).

    d: eğilme doğrultusundaki boy (moment d boyunca kol oluşturur), b: diğer kenar.
        L_w = 2(b + d),   S_w = b·d + d²/3
    """
    if b <= 0 or d <= 0:
        raise ValueError(f"b ve d pozitif olmalı: {b}, {d}")
    return WeldGroup(L_w=2.0 * (b + d), S_w=b * d + d * d / 3.0)


def weld_group_two_lines(d: float, b: float) -> WeldGroup:
    """Aralarında b mesafe bulunan, eğilme doğrultusunda d boyunda iki paralel
    kaynak (ör. U profil flanş uçları → ped).

        L_w = 2d,   S_w = d²/3

    (b yalnız geometrik doğrulama için; düzlem-içi eğilmede S_w'ye girmez.)
    """
    if b <= 0 or d <= 0:
        raise ValueError(f"b ve d pozitif olmalı: {b}, {d}")
    return WeldGroup(L_w=2.0 * d, S_w=d * d / 3.0)


def weld_group_circle(d: float) -> WeldGroup:
    """Daire kontur çevre kaynağı (boru ayak). d: kaynak dairesinin çapı.

        L_w = π·d,   S_w = π·d²/4      (I_w = π·d³/8 çizgi atalet momenti)
    """
    if d <= 0:
        raise ValueError(f"d pozitif olmalı: {d}")
    return WeldGroup(L_w=math.pi * d, S_w=math.pi * d * d / 4.0)


def weld_group_channel(b: float, d: float) -> WeldGroup:
    """C (U profil) konturu: iki yatay kenar b + bir düşey kenar d.

    d: eğilme doğrultusundaki boy (üst/alt kenarlar arası). Kaynak grubu
    d/2 merkezinde simetriktir:  I_w = 2·b·(d/2)² + d³/12
        L_w = 2b + d,   S_w = I_w/(d/2) = b·d + d²/6
    """
    if b <= 0 or d <= 0:
        raise ValueError(f"b ve d pozitif olmalı: {b}, {d}")
    return WeldGroup(L_w=2.0 * b + d, S_w=b * d + d * d / 6.0)


def scale_weld_group(group: WeldGroup, ratio: float) -> WeldGroup:
    """Grubu eşit oranda kısaltır (kısmi temas/kaynak): L_w ve S_w oranla çarpılır.

    YAKLAŞIKTIR: gerçek kısmi kaynak grubunun S_w'si geometriye bağlıdır; doğrusal
    ölçekleme bir idealizasyondur (çağıran sonuca yazmalıdır).
    """
    if not (0.0 < ratio <= 1.0):
        raise ValueError(f"ratio (0,1] aralığında olmalı: {ratio}")
    return WeldGroup(L_w=group.L_w * ratio, S_w=group.S_w * ratio)


def weld_line_forces(
    L_w: float,
    S_w: float,
    shear: float = 0.0,
    normal: float = 0.0,
    moment: float = 0.0,
) -> float:
    """Kaynak çizgisinde birim boy bileşke kuvveti f_r (N/mm).

        f_v = V / L_w                      (kaynağa paralel kesme)
        f_n = N / L_w + M / S_w            (kaynağa dik çekme/eğilme)
        f_r = √(f_v² + f_n²)
    """
    if L_w <= 0 or S_w <= 0:
        raise ValueError(f"L_w ve S_w pozitif olmalı: {L_w}, {S_w}")
    f_v = abs(shear) / L_w
    f_n = abs(normal) / L_w + abs(moment) / S_w
    return math.hypot(f_v, f_n)


@dataclass(frozen=True)
class FilletWeldCheck:
    """Tek bir köşe kaynağı birleşiminin dayanım sonucu."""

    leg_mm: float
    throat_mm: float
    line_force_N_per_mm: float
    stress_MPa: float
    allowable_MPa: float
    utilization: float
    required_leg_mm: float
    min_leg_mm: Optional[float]
    min_leg_ok: Optional[bool]  # None → asgari bacak kontrolü yapılmadı (girdi yok)


def check_fillet_weld_group(
    leg: float,
    group: WeldGroup,
    Fexx: float,
    shear: float = 0.0,
    normal: float = 0.0,
    moment: float = 0.0,
    min_leg_mm: Optional[float] = None,
) -> FilletWeldCheck:
    """Köşe kaynağı grubunu kesme + normal kuvvet + moment altında kontrol eder.

        τ = f_r / a,   a = 0,707·z,   τ ≤ 0,30·Fexx
        z_gerekli = f_r / (0,30·Fexx · 0,707)
    """
    throat = fillet_throat(leg)
    allowable = fillet_allowable_shear(Fexx)
    f_r = weld_line_forces(group.L_w, group.S_w, shear, normal, moment)
    stress = f_r / throat
    required_leg = f_r / (allowable * FILLET_THROAT_RATIO)
    if min_leg_mm is not None and min_leg_mm <= 0:
        raise ValueError(f"min_leg_mm pozitif olmalı: {min_leg_mm}")
    return FilletWeldCheck(
        leg_mm=leg,
        throat_mm=throat,
        line_force_N_per_mm=f_r,
        stress_MPa=stress,
        allowable_MPa=allowable,
        utilization=stress / allowable,
        required_leg_mm=required_leg,
        min_leg_mm=min_leg_mm,
        min_leg_ok=None if min_leg_mm is None else leg >= min_leg_mm,
    )


__all__ = [
    "FILLET_THROAT_RATIO",
    "FILLET_ALLOWABLE_SHEAR_FACTOR",
    "fillet_throat",
    "fillet_effective_length",
    "fillet_allowable_shear",
    "WeldGroup",
    "weld_group_rectangle",
    "weld_group_two_lines",
    "weld_group_circle",
    "weld_group_channel",
    "scale_weld_group",
    "weld_line_forces",
    "FilletWeldCheck",
    "check_fillet_weld_group",
]
