"""Flanş formülleri — ASME VIII-1 Appendix 2 mantığı.

Integral ve loose-type flanşlar için moment ve gerilme hesapları.
K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: ASME BPVC Section VIII Division 1, Appendix 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class FlangeForces:
    """Flanş üzerindeki kuvvetler ve momentler."""
    W: float = 0.0          # Total bolt load (N)
    H: float = 0.0          # Hydrostatic end force (N)
    H_D: float = 0.0        # Pressure force on inside diameter (N)
    H_G: float = 0.0        # Gasket reaction (N)
    H_T: float = 0.0        # Total hydrostatic end force minus H_D (N)
    h_D: float = 0.0        # Moment arm for H_D (mm)
    h_G: float = 0.0        # Moment arm for H_G (mm)
    h_T: float = 0.0        # Moment arm for H_T (mm)
    M: float = 0.0          # Total moment (N·mm)


@dataclass
class FlangeStress:
    """Flanş gerilme sonuçları."""
    S_H: float = 0.0        # Longitudinal hub stress (MPa)
    S_R: float = 0.0        # Radial flange stress (MPa)
    S_T: float = 0.0        # Tangential flange stress (MPa)
    S_avg: float = 0.0      # Average stress (MPa)
    allowable: float = 0.0  # Allowable stress (MPa)


def hydrostatic_end_force(
    P: float,
    G: float,
) -> float:
    """Appendix 2 — Hidrostatik uç kuvveti.

    H = π/4 × G² × P

    Args:
        P: Tasarım basıncı (MPa).
        G: Gasket reaction diameter (mm).

    Returns:
        Hidrostatik uç kuvveti (N).

    Referans: Appendix 2-5
    """
    return math.pi / 4.0 * G * G * P


def bolt_load_operating(
    H: float,
    H_p: float,
) -> float:
    """Appendix 2 — İşletme durumunda cıvata yükü.

    W = H + H_p
    H_p: Gasket sıkma kuvveti (N).

    Args:
        H: Hidrostatik uç kuvveti (N).
        H_p: Gasket sıkma kuvveti (N).

    Returns:
        Cıvata yükü (N).

    Referans: Appendix 2-5(a)
    """
    return H + H_p


def bolt_load_gasket_only(
    W_m1: float,
    W_m2: float,
) -> float:
    """Appendix 2 — Cıvata alanı kontrolü.

    W = max(W_m1, W_m2)
    W_m1: İşletme durumu cıvata yükü (N).
    W_m2: Gasket sıkma durumu cıvata yükü (N).

    Returns:
        Kritik cıvata yükü (N).

    Referans: Appendix 2-5(b)
    """
    return max(W_m1, W_m2)


def flange_moment(
    H_D: float,
    h_D: float,
    H_G: float,
    h_G: float,
    H_T: float,
    h_T: float,
) -> float:
    """Appendix 2 — Flanş momenti.

    M = H_D × h_D + H_G × h_G + H_T × h_T

    Args:
        H_D: İç çap üzerindeki basınç kuvveti (N).
        h_D: H_D moment kolu (mm).
        H_G: Gasket reaksiyonu (N).
        h_G: H_G moment kolu (mm).
        H_T: Hidrostatik uç kuvveti farkı (N).
        h_T: H_T moment kolu (mm).

    Returns:
        Toplam moment (N·mm).

    Referans: Appendix 2-6
    """
    return H_D * h_D + H_G * h_G + H_T * h_T


def hub_longitudinal_stress(
    M: float,
    f: float,
    g1: float,
    h0: float,
) -> float:
    """Appendix 2 — Hub boyuna gerilme.

    S_H = (M × f) / (λ × g1² × h0)   (integral flange)

    Args:
        M: Moment (N·mm).
        f: Hub correction factor.
        g1: Hub thickness at small end (mm).
        h0: Hub length (mm).

    Returns:
        Hub boyuna gerilme (MPa).

    Referans: Appendix 2-7
    """
    if g1 <= 0 or h0 <= 0:
        raise ValueError("g1 ve h0 pozitif olmalı")
    # λ faktörü integral flange için yaklaşık 1.0
    return M * f / (g1 * g1 * h0)


def radial_flange_stress(
    M: float,
    B: float,
    t: float,
    h0: float,
) -> float:
    """Appendix 2 — Radyal flanş gerilmesi.

    S_R = (4×M × β) / (λ × t² × B)   (integral flange, β=1)

    Args:
        M: Moment (N·mm).
        B: Flanş iç çapı (mm).
        t: Flanş kalınlığı (mm).
        h0: Hub uzunluğu (mm).

    Returns:
        Radyal gerilme (MPa).

    Referans: Appendix 2-7
    """
    if B <= 0 or t <= 0:
        raise ValueError("B ve t pozitif olmalı")
    # β = 1, λ ≈ 1 (integral)
    return 4.0 * M / (t * t * B)


def tangential_flange_stress(
    M: float,
    Y: float,
    t: float,
    B: float,
) -> float:
    """Appendix 2 — Teğetsel flanş gerilmesi.

    S_T = (M × Y) / (t² × B) - Z × S_R

    Args:
        M: Moment (N·mm).
        Y: Flanş faktörü (tablo).
        t: Flanş kalınlığı (mm).
        B: Flanş iç çapı (mm).

    Returns:
        Teğetsel gerilme (MPa).

    Referans: Appendix 2-7
    """
    if B <= 0 or t <= 0:
        raise ValueError("B ve t pozitif olmalı")
    return M * Y / (t * t * B)


def average_flange_stress(
    S_R: float,
    S_T: float,
) -> float:
    """Appendix 2 — Ortalama flanş gerilmesi.

    S_avg = (S_R + S_T) / 2

    Returns:
        Ortalama gerilme (MPa).

    Referans: Appendix 2-7
    """
    return (S_R + S_T) / 2.0


def flange_stress_check(
    S_H: float,
    S_R: float,
    S_T: float,
    S_avg: float,
    S_allow: float,
) -> Tuple[bool, str]:
    """Appendix 2 — Flanş gerilme kontrolü.

    Kontroller:
    1. S_H ≤ 1.5 × S_allow
    2. S_R ≤ S_allow
    3. S_avg ≤ S_allow

    Args:
        S_H: Hub boyuna gerilme (MPa).
        S_R: Radyal gerilme (MPa).
        S_T: Teğetsel gerilme (MPa).
        S_avg: Ortalama gerilme (MPa).
        S_allow: İzin verilen gerilme (MPa).

    Returns:
        (pass, açıklama)

    Referans: Appendix 2-7
    """
    checks = []

    if S_H > 1.5 * S_allow:
        checks.append(f"S_H={S_H:.2f} > 1.5×S_allow={1.5*S_allow:.2f}")
    if S_R > S_allow:
        checks.append(f"S_R={S_R:.2f} > S_allow={S_allow:.2f}")
    if S_avg > S_allow:
        checks.append(f"S_avg={S_avg:.2f} > S_allow={S_allow:.2f}")

    if checks:
        return False, "; ".join(checks)
    return True, "All stress checks passed"


__all__ = [
    "FlangeForces",
    "FlangeStress",
    "hydrostatic_end_force",
    "bolt_load_operating",
    "bolt_load_gasket_only",
    "flange_moment",
    "hub_longitudinal_stress",
    "radial_flange_stress",
    "tangential_flange_stress",
    "average_flange_stress",
    "flange_stress_check",
]
