"""EN 13445-3 formülleri — saf matematik.

Bu modül EN 13445-3:2021+A1:2023'teki temel formülleri uygular.
K1 kuralı: Formüller yalnızca hesap eklentilerinde.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: EN 13445-3:2021+A1:2023
"""

from __future__ import annotations

import math
from typing import Tuple


# ── EN 13445-3, 5.4.2: Silindirik gövde, iç basınç ──────────────────────────

def shell_thickness_internal_pressure(
    P: float,
    R: float,
    f: float,
    z: float,
) -> Tuple[float, float, float]:
    """EN 13445-3, 5.4.2 — Silindirik gövde iç basınç et kalınlığı.

    Çevresel gerilme (uzunlamasına dikişler — daha kritik):
        e_circ = P × R / (f × z - P/2)

    Boyuna gerilme (çevresel dikişler):
        e_long = P × R / (2 × f × z + P)

    Burada:
    f = tasarım gerilmesi (izin verilen gerilme, MPa)
    z = birimleştirme katsayısı (joint coefficient, 0.7–1.0)

    Args:
        P: Tasarım basıncı (MPa).
        R: İç yarıçap (mm).
        f: Tasarım gerilmesi / izin verilen gerilme (MPa).
        z: Birimleştirme katsayısı (joint coefficient).
        e: Mevcut et kalınlığı (mm) — kontrol için.
        C: Korozyon payı (mm).

    Returns:
        (e_circ, e_long, e_required) — çevresel, boyuna ve kritik kalınlık (mm).

    Referans: EN 13445-3, 5.4.2, Eq. (5.4.2-1) ve (5.4.2-2)
    """
    # Çevresel gerilme (uzunlamasına dikiş) — Eq. (5.4.2-1)
    denominator_circ = f * z - P / 2.0
    if denominator_circ <= 0:
        raise ValueError(
            f"EN 13445-3, 5.4.2: f×z - P/2 = {denominator_circ:.4f} ≤ 0. "
            "Basınç çok yüksek veya tasarım gerilmesi çok düşük."
        )
    e_circ = P * R / denominator_circ

    # Boyuna gerilme (çevresel dikiş) — Eq. (5.4.2-2)
    denominator_long = 2 * f * z + P
    e_long = P * R / denominator_long

    # Kritik kalınlık (büyük olan)
    e_required = max(e_circ, e_long)

    return e_circ, e_long, e_required


def shell_required_nominal_thickness(
    e_required: float,
    C: float,
    mill_tolerance_factor: float = 0.90,
    forming_thinning: float = 0.0,
) -> float:
    """Gerekli nominal et kalınlığı (EN 13445).

    e_nominal = e_required / mill_tolerance_factor + C + forming_thinning

    EN 13445'de tipik mill toleransı %10 → factor = 0.90.

    Args:
        e_required: Korozyonsuz gerekli kalınlık (mm).
        C: Korozyon payı (mm).
        mill_tolerance_factor: Sac tolerans faktörü (0.90 = %10 negatif).
        forming_thinning: Şekillendirme incelmesi (mm).

    Returns:
        Gerekli nominal kalınlık (mm).
    """
    if mill_tolerance_factor <= 0 or mill_tolerance_factor > 1.0:
        raise ValueError(f"mill_tolerance_factor 0-1 aralığında olmalı: {mill_tolerance_factor}")
    return e_required / mill_tolerance_factor + C + forming_thinning


# ── EN 13445-3, 5.5.2: Elipsoidal bombe ──────────────────────────────────────

def head_elliptical_thickness(
    P: float,
    D: float,
    f: float,
    z: float,
) -> Tuple[float, float]:
    """EN 13445-3, 5.5.2 — Elipsoidal bombe et kalınlığı.

    Standart 2:1 elipsoidal:
        e = P × D / (4 × f × z - P)

    Args:
        P: Tasarım basıncı (MPa).
        D: İç çap (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        C: Korozyon payı (mm).

    Returns:
        (e_required, shape_factor)

    Referans: EN 13445-3, 5.5.2, Eq. (5.5.2-1)
    """
    denominator = 4 * f * z - P
    if denominator <= 0:
        raise ValueError(
            f"EN 13445-3, 5.5.2: 4×f×z - P = {denominator:.4f} ≤ 0. "
            "Basınç çok yüksek."
        )
    e = P * D / denominator
    return e, 1.0  # shape_factor = 1.0 for 2:1 elliptical


# ── EN 13445-3, 5.5.3: Torisferik bombe ──────────────────────────────────────

def head_torispherical_thickness(
    P: float,
    L: float,
    r: float,
    f: float,
    z: float,
) -> Tuple[float, float]:
    """EN 13445-3, 5.5.3 — Torisferik bombe et kalınlığı (Korbbogen tipi).

    Q = (L/r) × (D/L - 0.5) × (D/L - 0.5) ... (karmaşık formül)

    Basitleştirilmiş yaklaşım (EN 13445-3, Tablo 5.5.3):
        e = P × L × W / (2 × f × z + 0.5 × P)

    Burada:
    W = şekil faktörü (L/r oranına bağlı)

    Args:
        P: Tasarım basıncı (MPa).
        D: İç çap (mm).
        L: Taç yarıçapı (mm).
        r: Büküm yarıçapı (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.

    Returns:
        (e_required, W_factor)

    Referans: EN 13445-3, 5.5.3
    """
    if r <= 0:
        raise ValueError("Büküm yarıçapı (r) sıfırdan büyük olmalı")
    if L <= 0:
        raise ValueError("Taç yarıçapı (L) sıfırdan büyük olmalı")

    # W faktörü — EN 13445-3, Tablo 5.5.3
    L_r_ratio = L / r
    if L_r_ratio <= 10:
        W = (3 + math.sqrt(L_r_ratio)) / 4.0
    else:
        W = 0.5 * (1 + math.sqrt(L / (2 * r)))

    denominator = 2 * f * z + 0.5 * P
    if denominator <= 0:
        raise ValueError(f"EN 13445-3, 5.5.3: 2×f×z + 0.5×P = {denominator:.4f} ≤ 0")

    e = P * L * W / denominator

    return e, W


# ── EN 13445-3, 5.5.4: Yarım küresel bombe ──────────────────────────────────

def head_hemispherical_thickness(
    P: float,
    R: float,
    f: float,
    z: float,
) -> float:
    """EN 13445-3, 5.5.4 — Yarım küresel bombe et kalınlığı.

    e = P × R / (2 × f × z - 0.5 × P)

    Args:
        P: Tasarım basıncı (MPa).
        R: İç yarıçap (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.

    Returns:
        Gerekli kalınlık (mm).

    Referans: EN 13445-3, 5.5.4, Eq. (5.5.4-1)
    """
    denominator = 2 * f * z - 0.5 * P
    if denominator <= 0:
        raise ValueError(f"EN 13445-3, 5.5.4: 2×f×z - 0.5×P = {denominator:.4f} ≤ 0")

    return P * R / denominator


# ── PED test basıncı ──────────────────────────────────────────────────────────

def ped_test_pressure(
    ps_mpa: float,
    operating_pressure_max: float,
    coefficient_ps: float = 1.43,
    coefficient_op: float = 1.25,
) -> Tuple[float, str]:
    """PED test basıncı hesabı.

    PED 2014/68/EU Ek I, Madde 8.1'e uygun:
        P_test = max(coefficient_op × P_operating_max, coefficient_ps × PS)

    Varsayılan katsayılar:
        coefficient_op = 1.25 (çalışma azami yükü için)
        coefficient_ps = 1.43 (PS için)

    Args:
        ps_mpa: Azami izin verilen basınç / PS (MPa).
        operating_pressure_max: Azami çalışma basıncı (MPa).
        coefficient_ps: PS katsayısı (varsayılan 1.43).
        coefficient_op: Çalışma basıncı katsayısı (varsayılan 1.25).

    Returns:
        (P_test, limiter) — test basıncı ve hangi değerin limitleyici olduğu.

    Referans: PED 2014/68/EU, Annex I, 8.1
    """
    p_from_op = coefficient_op * operating_pressure_max
    p_from_ps = coefficient_ps * ps_mpa

    if p_from_op >= p_from_ps:
        return p_from_op, "operating_pressure"
    else:
        return p_from_ps, "PS"


# ── MAWP hesaplama ────────────────────────────────────────────────────────────

def mawp_from_shell(
    R: float,
    e_actual: float,
    f: float,
    z: float,
    C: float = 0.0,
) -> float:
    """EN 13445-3, 5.4.2'den MAWP hesabı (silindirik gövde).

    P = f × z × e / (R + e/2)

    Args:
        R: İç yarıçap (mm).
        e_actual: Nominal et kalınlığı (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        C: Korozyon payı (mm).

    Returns:
        MAWP (MPa).
    """
    e = e_actual - C
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")

    mawp = f * z * e / (R + e / 2.0)
    return mawp


def mawp_from_head(
    head_type: str,
    D: float,
    e_actual: float,
    f: float,
    z: float,
    L: float = 0.0,
    r: float = 0.0,
    C: float = 0.0,
) -> float:
    """EN 13445-3'den MAWP hesabı (bombe).

    Args:
        head_type: Bombe tipi ("elliptical", "torispherical", "hemispherical").
        D: İç çap (mm).
        e_actual: Nominal et kalınlığı (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        L: Taç yarıçapı (mm) — torisferik için.
        r: Büküm yarıçapı (mm) — torisferik için.
        C: Korozyon payı (mm).

    Returns:
        MAWP (MPa).
    """
    e = e_actual - C
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")

    if head_type == "elliptical":
        # P = 4 × f × z × e / (D + e)
        return 4 * f * z * e / (D + e)

    elif head_type == "torispherical":
        if L <= 0 or r <= 0:
            raise ValueError("Torisferik bombe için L ve r parametreleri gerekli")
        L_r_ratio = L / r
        if L_r_ratio <= 10:
            W = (3 + math.sqrt(L_r_ratio)) / 4.0
        else:
            W = 0.5 * (1 + math.sqrt(L / (2 * r)))
        # P = 2 × f × z × e / (L × W - 0.5 × e)
        denominator = L * W - 0.5 * e
        if denominator <= 0:
            raise ValueError("Torisferik MAWP hesabında payda ≤ 0")
        return 2 * f * z * e / denominator

    elif head_type == "hemispherical":
        R = D / 2.0
        # P = 2 × f × z × e / (R + 0.5 × e)
        return 2 * f * z * e / (R + 0.5 * e)

    else:
        raise ValueError(f"Desteklenmeyen bombe tipi: {head_type}")


__all__ = [
    "shell_thickness_internal_pressure",
    "shell_required_nominal_thickness",
    "head_elliptical_thickness",
    "head_torispherical_thickness",
    "head_hemispherical_thickness",
    "ped_test_pressure",
    "mawp_from_shell",
    "mawp_from_head",
]
