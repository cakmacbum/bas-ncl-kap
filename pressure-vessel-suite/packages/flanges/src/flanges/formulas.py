"""Flanş formülleri — ASME VIII-1 Appendix 2 mantığı.

Integral ve loose-type flanşlar için moment ve gerilme hesapları.
K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: ASME BPVC Section VIII Division 1, Appendix 2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


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
    S_HR_avg: float = 0.0   # (S_H+S_R)/2 (MPa)
    S_HT_avg: float = 0.0   # (S_H+S_T)/2 (MPa)
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


def flange_shape_parameters(
    A: float,
    B: float,
    t: float,
    g0: float,
    F: float,
    V: float,
    T: float,
    U: float,
) -> dict:
    """Appendix 2-7 — Şekil sabitlerinden türetilen boyutsuz parametreler.

    F, V, T, U lisanslı Şekil 2-7.1 eğrilerinden KULLANICI tarafından okunur (K6);
    burada yalnızca formülle hesaplanabilen büyüklükler üretilir.

    K  = A/B
    Z  = (K² + 1) / (K² − 1)
    h0 = √(B·g0)
    e  = F / h0
    d  = (U/V) · h0 · g0²
    L  = (t·e + 1)/T + t³/d

    Args:
        A, B: Flanş dış / iç çapı (mm). A > B olmalı (K > 1; aksi halde Z tanımsız).
        t: Flanş kalınlığı (mm).
        g0: Hub kalınlığı, küçük uç (mm).
        F, V, T, U: Şekil 2-7.1 faktörleri (boyutsuz, > 0).

    Returns:
        {"K", "Z", "h0", "e", "d", "L"}

    Referans: Appendix 2-7 (Taylor Forge yöntemi)
    """
    for name, val in (("A", A), ("B", B), ("t", t), ("g0", g0),
                      ("F", F), ("V", V), ("T", T), ("U", U)):
        if val is None or val <= 0:
            raise ValueError(f"{name} pozitif olmalı")
    if A <= B:
        raise ValueError("A > B olmalı (K = A/B > 1)")
    K = A / B
    Z = (K * K + 1.0) / (K * K - 1.0)
    h0 = math.sqrt(B * g0)
    e = F / h0
    d = (U / V) * h0 * g0 * g0
    L = (t * e + 1.0) / T + t ** 3 / d
    return {"K": K, "Z": Z, "h0": h0, "e": e, "d": d, "L": L}


def hub_longitudinal_stress(
    M: float,
    f: float,
    L: float,
    g1: float,
    B: float,
) -> float:
    """Appendix 2-7 — Hub boyuna gerilme (integral flanş).

    S_H = f·M / (L·g1²·B)

    Args:
        M: Moment (N·mm).
        f: Hub gerilme düzeltme faktörü (Şekil 2-7.6; kullanıcı girdisi).
        L: Flanş parametresi (flange_shape_parameters).
        g1: Hub kalınlığı, büyük uç (mm).
        B: Flanş iç çapı (mm).

    Returns:
        S_H (MPa).

    Referans: Appendix 2-7
    """
    if g1 <= 0 or B <= 0 or L <= 0:
        raise ValueError("g1, B ve L pozitif olmalı")
    return f * M / (L * g1 * g1 * B)


def radial_flange_stress(
    M: float,
    L: float,
    t: float,
    e: float,
    B: float,
) -> float:
    """Appendix 2-7 — Radyal flanş gerilmesi.

    S_R = (1.33·t·e + 1)·M / (L·t²·B)

    Returns:
        S_R (MPa).

    Referans: Appendix 2-7
    """
    if B <= 0 or t <= 0 or L <= 0:
        raise ValueError("B, t ve L pozitif olmalı")
    return (1.33 * t * e + 1.0) * M / (L * t * t * B)


def tangential_flange_stress(
    M: float,
    Y: float,
    t: float,
    B: float,
    Z: float,
    S_R: float,
) -> float:
    """Appendix 2-7 — Teğetsel flanş gerilmesi.

    S_T = Y·M/(t²·B) − Z·S_R

    Args:
        Y: Şekil 2-7.1 faktörü (kullanıcı girdisi).
        Z: (K²+1)/(K²−1).
        S_R: Radyal gerilme (MPa).

    Returns:
        S_T (MPa). Negatif olabilir (işaret korunur).

    Referans: Appendix 2-7
    """
    if B <= 0 or t <= 0:
        raise ValueError("B ve t pozitif olmalı")
    return Y * M / (t * t * B) - Z * S_R


def flange_stress_checks(
    S_H: float,
    S_R: float,
    S_T: float,
    S_f: float,
) -> List[Tuple[str, float, float]]:
    """Appendix 2-7 — Gerilme kontrolleri (integral flanş).

    Kontroller (S_n bilinmediğinden S_H için yalnız 1.5·S_f):
      S_H ≤ 1.5·S_f ; S_R ≤ S_f ; S_T ≤ S_f ;
      (S_H+S_R)/2 ≤ S_f ; (S_H+S_T)/2 ≤ S_f

    Gerilmeler işaretli karşılaştırılır (Appendix 2 işaretli değerleri kullanır);
    negatif gerilme sınırı aşmaz.

    Returns:
        [(ad, değer, sınır), ...]

    Referans: Appendix 2-7
    """
    return [
        ("S_H", S_H, 1.5 * S_f),
        ("S_R", S_R, S_f),
        ("S_T", S_T, S_f),
        ("(S_H+S_R)/2", (S_H + S_R) / 2.0, S_f),
        ("(S_H+S_T)/2", (S_H + S_T) / 2.0, S_f),
    ]


__all__ = [
    "FlangeForces",
    "FlangeStress",
    "hydrostatic_end_force",
    "bolt_load_operating",
    "bolt_load_gasket_only",
    "flange_moment",
    "flange_shape_parameters",
    "hub_longitudinal_stress",
    "radial_flange_stress",
    "tangential_flange_stress",
    "flange_stress_checks",
]
