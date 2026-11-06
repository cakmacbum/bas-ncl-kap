"""EN 13445-3 Madde 9 — Açıklıkların takviyesi (Basınç-alan yöntemi).

Bu modül EN 13445-3:2021+A1:2023 Madde 9'da tanımlanan tekil dairesel
açıklıkların takviye hesabını saf matematiksel fonksiyonlarla (float girer/çıkar)
uygular.

K1 kuralı: Formüller yalnızca hesap eklentisinde yer alır.
K6 kuralı: Lisanslı standart metni gömülmez; bağıntılar ve madde referansları verilir.
verified=False (Bellekten formüller; lisanslı metinle doğrulanmadı).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

# EN 13445-3 Madde 9.4 Uygulanabilirlik sınırları
MAX_DI_OVER_DIS = 1.0  # d_ib / D_is <= 1.0
MAX_EC_OVER_DIS = 0.1  # e_c / D_is <= 0.1


def effective_shell_length(R_is: float, e_c: float) -> float:
    """Gövde etkin boyu (EN 13445-3, 9.5):
    l_so = sqrt((2 * R_is + e_c) * e_c)

    Args:
        R_is: Gövde korozyonlu iç yarıçapı (mm).
        e_c: Gövde analiz kalınlığı (mm).
    """
    if R_is <= 0.0 or e_c <= 0.0:
        return 0.0
    return math.sqrt((2.0 * R_is + e_c) * e_c)


def effective_nozzle_length(d_eb: float, e_b: float) -> float:
    """Nozul dış etkin boyu (EN 13445-3, 9.5):
    l_bo = sqrt((d_eb - e_b) * e_b)

    Args:
        d_eb: Nozul dış çapı (mm).
        e_b: Nozul analiz et kalınlığı (mm).
    """
    if d_eb <= 0.0 or e_b <= 0.0 or d_eb <= e_b:
        return 0.0
    return math.sqrt((d_eb - e_b) * e_b)


def effective_inside_projection(inside_proj: float, l_bo: float) -> float:
    """Nozul iç çıkıntı etkin boyu (EN 13445-3, 9.5):
    l'_bi = min(inside_proj, 0.5 * l_bo)

    Args:
        inside_proj: Gerçek iç çıkıntı boyu (mm).
        l_bo: Nozul etkin boyu (mm).
    """
    if inside_proj <= 0.0 or l_bo <= 0.0:
        return 0.0
    return min(inside_proj, 0.5 * l_bo)


def shell_reinforcement_area(l_so: float, e_c: float) -> float:
    """Gövde etkin metal kesit alanı (Af_s):
    Af_s = l'_s * e_c
    (İzole tekil açıklık için l'_s = l_so).
    """
    return max(0.0, l_so) * max(0.0, e_c)


def nozzle_reinforcement_area(
    e_b: float,
    l_bo_eff: float,
    l_bi_eff: float,
    e_c: float,
) -> float:
    """Nozul etkin metal kesit alanı (Af_b):
    Af_b = e_b * (l'_bo + l'_bi + e_s)
    burada e_s = e_c (gövde analiz kalınlığı).
    """
    return max(0.0, e_b) * (max(0.0, l_bo_eff) + max(0.0, l_bi_eff) + max(0.0, e_c))


def pad_reinforcement_area(w_p: float, l_so: float, e_p: float) -> float:
    """Takviye pedi metal kesit alanı (Af_p):
    l'_p = min(w_p, l_so)
    Af_p = l'_p * e_p
    """
    if w_p <= 0.0 or e_p <= 0.0 or l_so <= 0.0:
        return 0.0
    l_p_eff = min(w_p, l_so)
    return l_p_eff * e_p


def shell_pressure_area_cylinder(R_is: float, l_so: float, a: float) -> float:
    """Silindirik gövde basınç alanı (Ap_s):
    Ap_s = R_is * (l_so + a)
    burada a = d_ib / 2 (açıklık yarıçapı).
    """
    return max(0.0, R_is) * (max(0.0, l_so) + max(0.0, a))


def shell_pressure_area_sphere(R_is: float, l_so: float, a: float) -> float:
    """Küre / bombe sadeleştirilmiş basınç alanı (Ap_s):
    Ap_s = 0.5 * R_is * (l_so + a)
    EN 13445-3 9.5 küresel kabuk için R^2 / (R + 0.5*e_c) ≈ R sadeleştirmesi.
    """
    return 0.5 * max(0.0, R_is) * (max(0.0, l_so) + max(0.0, a))


def nozzle_pressure_area(d_ib: float, l_bo_eff: float, e_c: float) -> float:
    """Nozul basınç alanı (Ap_b):
    Ap_b = 0.5 * d_ib * (l'_bo + e_c)
    """
    return 0.5 * max(0.0, d_ib) * (max(0.0, l_bo_eff) + max(0.0, e_c))


def check_pressure_area_reinforcement(
    *,
    P: float,
    f_s: float,
    f_b: float,
    f_p: float = 0.0,
    Af_s: float,
    Af_b: float,
    Af_p: float = 0.0,
    Af_w: float = 0.0,
    Ap_s: float,
    Ap_b: float,
    Ap_phi: float = 0.0,
) -> Dict[str, Any]:
    """EN 13445-3 Madde 9.5.2 kabul kriteri hesabı:
    Kapasite (Sol taraf):
    Phi = (Af_s + Af_w) * (f_s - 0.5 * P) + Af_p * (f_op - 0.5 * P) + Af_b * (f_ob - 0.5 * P)
    burada f_ob = min(f_b, f_s), f_op = min(f_p, f_s)

    Yük (Sağ taraf):
    Psi = P * (Ap_s + Ap_b + 0.5 * Ap_phi)

    Kullanım oranı:
    u = Psi / Phi (<= 1.0 ise takviye yeterli)
    """
    f_ob = min(f_b, f_s)
    f_op = min(f_p, f_s) if Af_p > 0.0 else 0.0

    term_s = (Af_s + Af_w) * (f_s - 0.5 * P)
    term_p = Af_p * (f_op - 0.5 * P) if Af_p > 0.0 else 0.0
    term_b = Af_b * (f_ob - 0.5 * P)

    capacity_phi = term_s + term_p + term_b
    load_psi = P * (Ap_s + Ap_b + 0.5 * Ap_phi)

    if capacity_phi <= 0.0:
        utilization = float("inf")
    else:
        utilization = load_psi / capacity_phi

    is_reinforced = utilization <= 1.0

    return {
        "P": P,
        "f_s": f_s,
        "f_b": f_b,
        "f_p": f_p,
        "f_ob": f_ob,
        "f_op": f_op,
        "Af_s": Af_s,
        "Af_b": Af_b,
        "Af_p": Af_p,
        "Af_w": Af_w,
        "Ap_s": Ap_s,
        "Ap_b": Ap_b,
        "Ap_phi": Ap_phi,
        "term_s": term_s,
        "term_p": term_p,
        "term_b": term_b,
        "capacity_phi": capacity_phi,
        "load_psi": load_psi,
        "utilization": utilization,
        "is_reinforced": is_reinforced,
    }


def check_applicability_limits(
    d_ib: float,
    D_is: float,
    e_c: float,
) -> List[Tuple[str, bool, float, float]]:
    """EN 13445-3 Madde 9.4 uygulanabilirlik sınırları kontrolleri:
    1. d_ib / D_is <= 1.0
    2. e_c / D_is <= 0.1
    Döner: list of (check_name, is_ok, limit, actual_value)
    """
    checks = []
    if D_is > 0.0:
        ratio_d = d_ib / D_is
        checks.append(("9.4 d_ib/D_is <= 1.0", ratio_d <= (MAX_DI_OVER_DIS + 1e-9), MAX_DI_OVER_DIS, ratio_d))
        ratio_e = e_c / D_is
        checks.append(("9.4 e_c/D_is <= 0.1", ratio_e <= (MAX_EC_OVER_DIS + 1e-9), MAX_EC_OVER_DIS, ratio_e))
    return checks
