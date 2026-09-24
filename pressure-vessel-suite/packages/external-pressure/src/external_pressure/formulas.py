"""Dış basınç formülleri — ASME UG-28 mantığı.

Silindirik gövde ve bombeler için dış basınç stabilite (buckling) hesapları.
K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: ASME BPVC Section VIII Division 1, UG-28, UG-33, UCS/UNF tabloları.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ExternalPressureResult:
    """Dış basınç hesap ara sonuçları."""
    L_over_D: float = 0.0
    D_over_t: float = 0.0
    A: float = 0.0          # Strain factor (geometrik)
    B: float = 0.0          # Allowable compressive stress (MPa)
    P_allow: float = 0.0    # İzin verilen dış basınç (MPa)
    factor_A_table: str = ""
    factor_B_table: str = ""


def shell_external_pressure_allowable(
    D: float,
    L: float,
    t: float,
    A: float,
    B: float,
    P_external: float,
) -> Tuple[float, ExternalPressureResult]:
    """UG-28 — Silindirik gövde dış basınç stabilite kontrolü.

    Mantık:
    1. L/D ve D/t oranlarını hesapla
    2. UG-28.1 Şekil G (geometrik) grafiği → A (strain factor)
    3. Malzeme sıcaklık grafiği → B (izin verilen gerilme, MPa)
    4. P_allow = 4B / (3 × D/t)
    5. P_external ≤ P_allow → preliminary numerical estimate only. This helper
       does not establish UG-28 compliance and must not be used to issue PASS.

    Args:
        D: Dış çap (mm).
        L: Destekler arası uzunluk (mm). Gövde uzunluğu veya flanş-flanş arası.
        t: Nominal et kalınlığı (mm).
        A: Strain factor (geometrik grafikten okunan). Üretici veya kullanıcı girer.
        B: Allowable compressive stress (MPa). Malzeme grafikten okunan.
        P_external: Uygulanan dış basınç (MPa).

    Returns:
        (P_allow, detay) — izin verilen dış basınç ve ara sonuçlar.

    Referans: UG-28(a), UG-28.1
    """
    detail = ExternalPressureResult()

    if D <= 0 or L <= 0 or t <= 0:
        raise ValueError("D, L, t pozitif olmalı")

    L_over_D = L / D
    D_over_t = D / t

    detail.L_over_D = L_over_D
    detail.D_over_t = D_over_t
    detail.A = A
    detail.B = B

    # UG-28(c)(1): P_allow = 4B / (3 × D/t)
    # B > 0 ve A > 0 olmalı (grafiklerden okunmuş)
    if A <= 0 or B <= 0:
        raise ValueError(
            "Strain factor A ve allowable stress B pozitif olmalı. "
            "UG-28 grafiklerinden okunmalıdır."
        )

    P_allow = 4.0 * B / (3.0 * D_over_t)
    detail.P_allow = P_allow

    return P_allow, detail


def shell_external_pressure_required_thickness(
    D: float,
    L: float,
    P_external: float,
    A: float,
    B: float,
    C: float = 0.0,
) -> Tuple[float, ExternalPressureResult]:
    """UG-28 — Dış basınç için gerekli et kalınlığı.

    P_external = 4B / (3 × D/t) → t = 4B×D / (3×D×P_external) = 4B / (3×P_external)
    (D/t cinsinden D iptal olmaz — D/(D/t) = t)

    Args:
        D: Dış çap (mm).
        L: Destekler arası uzunluk (mm).
        P_external: Dış basınç (MPa).
        A: Strain factor.
        B: Allowable stress (MPa).
        C: Korozyon payı (mm).

    Returns:
        (t_required, detay)

    Referans: UG-28
    """
    detail = ExternalPressureResult()

    if D <= 0 or L <= 0 or P_external <= 0:
        raise ValueError("D, L, P_external pozitif olmalı")

    L_over_D = L / D
    detail.L_over_D = L_over_D

    # P = 4B / (3 × D/t) → D/t = 4B / (3P) → t = D / (D/t)
    if B <= 0:
        raise ValueError("B (allowable stress) pozitif olmalı")

    D_over_t_required = 4.0 * B / (3.0 * P_external)
    t_required = D / D_over_t_required + C

    detail.D_over_t = D_over_t_required
    detail.A = A
    detail.B = B
    detail.P_allow = P_external  # eşitlik durumu

    return t_required, detail


def head_external_pressure_allowable(
    D: float,
    t: float,
    A: float,
    B: float,
) -> Tuple[float, ExternalPressureResult]:
    """UG-33 — Bombe dış basınç stabilite kontrolü.

    Bombeler için L/D oranı gövdeye göre farklıdır.
    2:1 elipsoidal ve torispherical için basitleştirilmiş kontrol:
        P_allow = B × t / (0.5 × D)

    This intentionally simplified calculation is not a complete UG-33 method.
    It does not select/validate geometry-specific code charts and its numeric
    result must remain subject to engineering review.

    Args:
        D: Reference outside diameter (mm), supplied by the caller.
        t: Et kalınlığı (mm).
        A: Strain factor.
        B: Allowable stress (MPa).

    Returns:
        (P_allow, detay)

    Referans: UG-33
    """
    detail = ExternalPressureResult()

    if D <= 0 or t <= 0:
        raise ValueError("D, t pozitif olmalı")
    if A <= 0 or B <= 0:
        raise ValueError("A, B pozitif olmalı")

    detail.D_over_t = D / t
    detail.A = A
    detail.B = B

    # UG-33/UG-28(d) bombe yaklaşımı: P_allow = B / (Ro/t) = 2Bt/D.
    # D, bu fonksiyona verilen referans çaptır; çağıran katman dış çapı sağlar.
    P_allow = 2.0 * B * t / D
    detail.P_allow = P_allow

    return P_allow, detail


# ── Minimum required thickness (UG-28 iteration) ──────────────────────────────

def external_pressure_min_thickness(
    D: float,
    L: float,
    P_external: float,
    B_func,
    C: float = 0.0,
    t_min: float = 2.0,
    t_max: float = 200.0,
    tol: float = 0.01,
    max_iter: int = 50,
) -> float:
    """Dış basınç için minimum et kalınlığı — iteratif çözüm.

    B_func: (D, L, t) → (A, B) fonksiyonu (kullanıcı/mühendis tanımlar).

    Args:
        D: Dış çap (mm).
        L: Destekler arası uzunluk (mm).
        P_external: Dış basınç (MPa).
        B_func: Strain→stress fonksiyonu.
        C: Korozyon payı (mm).
        t_min, t_max: Arama aralığı (mm).
        tol: Yakınsama toleransı (mm).
        max_iter: Maksimum iterasyon.

    Returns:
        Gerekli minimum et kalınlığı (mm).
    """
    if D <= 0 or L <= 0 or P_external <= 0:
        raise ValueError("D, L, P_external pozitif olmalı")

    for _ in range(max_iter):
        t_mid = (t_min + t_max) / 2.0
        t_corroded = t_mid - C
        if t_corroded <= 0:
            t_min = t_mid
            continue

        A, B = B_func(D, L, t_corroded)
        if A <= 0 or B <= 0:
            t_min = t_mid
            continue

        P_allow = 4.0 * B / (3.0 * D / t_corroded)

        if abs(P_allow - P_external) < tol:
            return t_mid
        elif P_allow < P_external:
            t_min = t_mid
        else:
            t_max = t_mid

    return t_max


__all__ = [
    "ExternalPressureResult",
    "shell_external_pressure_allowable",
    "shell_external_pressure_required_thickness",
    "head_external_pressure_allowable",
    "external_pressure_min_thickness",
]
