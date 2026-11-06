"""EN 13445-3 Madde 8 — Dış basınç ve vakum stabilite formülleri (saf matematik).

Bu modül EN 13445-3:2021+A1:2023 Madde 8.5 (silindirik kabuklar) ve
Madde 8.7 (küresel kabuklar ve bombeler) dış basınç ve vakum formüllerini
uygular.

K1 kuralı: Formüller yalnızca hesap eklentisinde.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
K7 kuralı: Domain modelinden bağımsız (saf float/int girer/çıkar).

Not: Formüller lisanslı standart metninden doğrulanmamıştır (bellekten, verified=False).
"""

from __future__ import annotations

import math
from typing import Dict, Tuple, Union


def cylinder_analysis_thickness(
    nominal_thickness: float,
    corrosion_allowance: float,
    mill_tolerance_pct: float = 0.0,
) -> float:
    """EN 13445-3, 8.5 — Silindirik kabuk analiz et kalınlığı e_a.

    e_a = e - c - delta_e
    Burada:
        e: nominal et kalınlığı (mm)
        c: toplam korozyon payı (mm)
        delta_e: negatif sac toleransı (mm), girilmediyse tipik %10 varsayılır.

    Args:
        nominal_thickness: Nominal et kalınlığı e (mm).
        corrosion_allowance: Toplam korozyon payı c (mm).
        mill_tolerance_pct: Negatif sac toleransı (%) [ör. 10.0]. 0 veya negatifse %10.

    Returns:
        e_a: Analiz et kalınlığı (mm).
    """
    if nominal_thickness <= 0:
        raise ValueError(f"Nominal kalınlık e = {nominal_thickness} > 0 olmalıdır.")
    tol_pct = mill_tolerance_pct if mill_tolerance_pct > 0 else 10.0
    delta_e = nominal_thickness * (tol_pct / 100.0)
    ea = nominal_thickness - corrosion_allowance - delta_e
    return ea


def cylinder_effective_length(
    tangent_length: float,
    head_1_depth: float = 0.0,
    head_2_depth: float = 0.0,
) -> float:
    """EN 13445-3, 8.5 — Takviye halkasız silindir için tasarım boyu L.

    L = tangent_length + (1/3) * head_1_depth + (1/3) * head_2_depth

    Args:
        tangent_length: Gövde teğet boyu (mm).
        head_1_depth: 1. bombe iç derinliği (mm).
        head_2_depth: 2. bombe iç derinliği (mm).

    Returns:
        L: Etkin silindir boyu (mm).
    """
    if tangent_length <= 0:
        raise ValueError(f"Gövde boyu {tangent_length} > 0 olmalıdır.")
    return tangent_length + (head_1_depth / 3.0) + (head_2_depth / 3.0)


def cylinder_elastic_instability_pressure(
    E: float,
    ea: float,
    R: float,
    L: float,
    nu: float = 0.3,
    n_min: int = 2,
    n_max: int = 20,
) -> Tuple[float, int]:
    """EN 13445-3, 8.5.2 — Silindirik kabuk elastik göçme basıncı p_m (von Mises).

    Z = pi * R / L
    epsilon(n) = (1 / (n^2 - 1 + 0.5 * Z^2)) * [
        Z^4 / (n^2 + Z^2)^2 + (ea^2 / (12 * (1 - nu^2) * R^2)) * (n^2 - 1 + Z^2)^2
    ]
    p_m(n) = (E * ea * epsilon(n)) / R

    n dalga sayısı (n >= 2) üzerinden minimize edilir.

    Docstring notu: Formül bellekten yazılmıştır (verified=False).

    Args:
        E: Tasarım sıcaklığındaki elastisite modülü (MPa).
        ea: Analiz et kalınlığı (mm).
        R: Ortalama silindir yarıçapı (mm).
        L: Tasarım boyu (mm).
        nu: Poisson oranı (varsayılan: 0.3).
        n_min: Minimum dalga sayısı (varsayılan: 2).
        n_max: Maksimum dalga sayısı (varsayılan: 20).

    Returns:
        (p_m_min, governing_n): Minimum elastik göçme basıncı (MPa) ve belirleyici dalga sayısı.
    """
    if ea <= 0:
        raise ValueError(f"Analiz et kalınlığı ea = {ea} > 0 olmalıdır.")
    if R <= 0:
        raise ValueError(f"Yarıçap R = {R} > 0 olmalıdır.")
    if L <= 0:
        raise ValueError(f"Boy L = {L} > 0 olmalıdır.")
    if E <= 0:
        raise ValueError(f"Elastisite modülü E = {E} > 0 olmalıdır.")

    Z = (math.pi * R) / L
    Z2 = Z * Z
    Z4 = Z2 * Z2
    bending_coeff = (ea * ea) / (12.0 * (1.0 - nu * nu) * R * R)
    prefactor = (E * ea) / R

    best_pm = float("inf")
    best_n = n_min

    for n in range(n_min, n_max + 1):
        n2 = float(n * n)
        denom_eps = n2 - 1.0 + 0.5 * Z2
        if denom_eps <= 0:
            continue
        term_membrane = Z4 / ((n2 + Z2) ** 2)
        term_bending = bending_coeff * ((n2 - 1.0 + Z2) ** 2)
        eps = (term_membrane + term_bending) / denom_eps
        pm_n = prefactor * eps
        if pm_n < best_pm:
            best_pm = pm_n
            best_n = n

    return best_pm, best_n


def cylinder_yield_pressure(sigma_e: float, ea: float, R: float) -> float:
    """EN 13445-3, 8.5.2 — Silindirik kabuk akma basıncı p_y.

    p_y = sigma_e * ea / R
    Burada:
        sigma_e: Tasarım sıcaklığındaki akma dayanımı (Rp0,2/T, MPa).
        ea: Analiz et kalınlığı (mm).
        R: Ortalama silindir yarıçapı (mm).

    Args:
        sigma_e: Akma dayanımı (MPa).
        ea: Analiz et kalınlığı (mm).
        R: Ortalama silindir yarıçapı (mm).

    Returns:
        p_y: Akma basıncı (MPa).
    """
    if ea <= 0:
        raise ValueError(f"ea = {ea} > 0 olmalıdır.")
    if R <= 0:
        raise ValueError(f"R = {R} > 0 olmalıdır.")
    if sigma_e <= 0:
        raise ValueError(f"sigma_e = {sigma_e} > 0 olmalıdır.")
    return (sigma_e * ea) / R


def curve_figure_8_5_5(pm_over_py: float) -> float:
    """EN 13445-3 Şekil 8.5-5 Eğri 1 (silindir) — pr / py oranı.

    Bellekten yazılmıştır (lisanslı standart metninden doğrulanmadı, verified=False).
    x = pm / py:
      - x <= 0: 0.0
      - x <= 1.0: 0.5 * x (elastik göçme ve %0.5 dairesellik sapması)
      - x > 1.0: 1.0 - 0.5 / x (elastoplastik geçiş, x -> sonsuz için 1.0'a yaklaşır)

    Args:
        pm_over_py: p_m / p_y oranı.

    Returns:
        pr_over_py: p_r / p_y oranı.
    """
    if pm_over_py <= 0.0:
        return 0.0
    if pm_over_py <= 1.0:
        return 0.5 * pm_over_py
    return 1.0 - 0.5 / pm_over_py


def sphere_elastic_instability_pressure(E: float, ea: float, R: float) -> float:
    """EN 13445-3, 8.7 — Küresel kabuk elastik göçme basıncı p_m.

    p_m = 1.21 * E * (ea^2 / R^2)

    Docstring notu: Formül bellekten yazılmıştır (verified=False).

    Args:
        E: Elastisite modülü (MPa).
        ea: Analiz et kalınlığı (mm).
        R: Taç / küre yarıçapı (mm).

    Returns:
        p_m: Elastik göçme basıncı (MPa).
    """
    if ea <= 0:
        raise ValueError(f"ea = {ea} > 0 olmalıdır.")
    if R <= 0:
        raise ValueError(f"R = {R} > 0 olmalıdır.")
    if E <= 0:
        raise ValueError(f"E = {E} > 0 olmalıdır.")
    return 1.21 * E * ((ea * ea) / (R * R))


def sphere_yield_pressure(sigma_e: float, ea: float, R: float) -> float:
    """EN 13445-3, 8.7 — Küresel kabuk akma basıncı p_y.

    p_y = 2 * sigma_e * ea / R

    Docstring notu: Formül bellekten yazılmıştır (verified=False).

    Args:
        sigma_e: Akma dayanımı (Rp0,2/T, MPa).
        ea: Analiz et kalınlığı (mm).
        R: Taç / küre yarıçapı (mm).

    Returns:
        p_y: Küre akma basıncı (MPa).
    """
    if ea <= 0:
        raise ValueError(f"ea = {ea} > 0 olmalıdır.")
    if R <= 0:
        raise ValueError(f"R = {R} > 0 olmalıdır.")
    if sigma_e <= 0:
        raise ValueError(f"sigma_e = {sigma_e} > 0 olmalıdır.")
    return (2.0 * sigma_e * ea) / R


def curve_figure_8_7_1(pm_over_py: float) -> float:
    """EN 13445-3 Şekil 8.7-1 (küresel kabuk / bombe) — pr / py oranı.

    Bellekten yazılmıştır (lisanslı standart metninden doğrulanmadı, verified=False).
    Şekil 8.5-5 ile aynı parçalı elastoplastik geçiş eğrisini kullanır:
      - x <= 0: 0.0
      - x <= 1.0: 0.5 * x
      - x > 1.0: 1.0 - 0.5 / x

    Args:
        pm_over_py: p_m / p_y oranı.

    Returns:
        pr_over_py: p_r / p_y oranı.
    """
    return curve_figure_8_5_5(pm_over_py)


def cylinder_external_pressure_allowable(
    E: float,
    sigma_e: float,
    ea: float,
    R: float,
    L: float,
    S: float = 1.5,
    nu: float = 0.3,
) -> Dict[str, Union[float, int]]:
    """EN 13445-3, 8.5 — Silindirik kabuk azami izin verilen dış basınç p_allow.

    Adımlar:
    1. p_m, n = cylinder_elastic_instability_pressure(E, ea, R, L, nu)
    2. p_y = cylinder_yield_pressure(sigma_e, ea, R)
    3. pm_over_py = p_m / p_y
    4. pr_over_py = curve_figure_8_5_5(pm_over_py)
    5. p_r = pr_over_py * p_y
    6. p_allow = p_r / S

    Args:
        E: Elastisite modülü (MPa).
        sigma_e: Akma dayanımı (MPa).
        ea: Analiz et kalınlığı (mm).
        R: Ortalama yarıçap (mm).
        L: Tasarım boyu (mm).
        S: Emniyet katsayısı (tasarım için 1.5, test için 1.1).
        nu: Poisson oranı (0.3).

    Returns:
        Dict içeren ara değerler ve p_allow.
    """
    pm, n = cylinder_elastic_instability_pressure(E, ea, R, L, nu)
    py = cylinder_yield_pressure(sigma_e, ea, R)
    pm_over_py = pm / py if py > 0 else 0.0
    pr_over_py = curve_figure_8_5_5(pm_over_py)
    pr = pr_over_py * py
    p_allow = pr / S if S > 0 else 0.0

    return {
        "p_m": pm,
        "n": n,
        "p_y": py,
        "pm_over_py": pm_over_py,
        "pr_over_py": pr_over_py,
        "p_r": pr,
        "S": S,
        "p_allow": p_allow,
    }


def sphere_external_pressure_allowable(
    E: float,
    sigma_e: float,
    ea: float,
    R: float,
    S: float = 1.5,
) -> Dict[str, float]:
    """EN 13445-3, 8.7 — Küresel kabuk / bombe azami izin verilen dış basınç p_allow.

    Adımlar:
    1. p_m = sphere_elastic_instability_pressure(E, ea, R)
    2. p_y = sphere_yield_pressure(sigma_e, ea, R)
    3. pm_over_py = p_m / p_y
    4. pr_over_py = curve_figure_8_7_1(pm_over_py)
    5. p_r = pr_over_py * p_y
    6. p_allow = p_r / S

    Args:
        E: Elastisite modülü (MPa).
        sigma_e: Akma dayanımı (MPa).
        ea: Analiz et kalınlığı (mm).
        R: Taç / küre yarıçapı (mm).
        S: Emniyet katsayısı (tasarım için 1.5, test için 1.1).

    Returns:
        Dict içeren ara değerler ve p_allow.
    """
    pm = sphere_elastic_instability_pressure(E, ea, R)
    py = sphere_yield_pressure(sigma_e, ea, R)
    pm_over_py = pm / py if py > 0 else 0.0
    pr_over_py = curve_figure_8_7_1(pm_over_py)
    pr = pr_over_py * py
    p_allow = pr / S if S > 0 else 0.0

    return {
        "p_m": pm,
        "p_y": py,
        "pm_over_py": pm_over_py,
        "pr_over_py": pr_over_py,
        "p_r": pr,
        "S": S,
        "p_allow": p_allow,
    }
