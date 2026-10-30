"""Etek taban halkası (base ring), ankraj cıvatası ve beton yataklık kontrolü.

Kaynak yaklaşımı: Moss PVDM Procedure 3-9 / Jawad-Farr (Structural Analysis and
Design of Process Equipment) — lineer şekil değiştirme düzlemli, çekme almayan
beton ve yalnız çekme alan cıvata halkası kesiti (elastik, modüler oran n).
Moss'un grafik/tablo katsayıları KULLANILMAZ; denge denklemleri doğrudan sayısal
çözülür (kesit şeritlere bölünür), böylece çizelge verisi gerekmez (K6).

verified:false — halka kalınlığı konsol formülü (t = l*sqrt(3*fc/Fb)) ve cıvata
altı eğilme (t = sqrt(6*T*x/(b*Fb))) basitleştirilmiş formlardır; Fb varsayımı
0,66*Fy'dir. Sonuç PASS olsa bile REVIEW_REQUIRED kalır.
Kapsam dışı: etek-halka kaynağı, bolt chair/üst halka, çekme-kesme etkileşimi,
sürtünme (kesme sürtünmesiz alınır, güvenli taraf), beton kopma (breakout).
"""

from __future__ import annotations

import math
from typing import Optional

from calc_core.result import CalculationResult

_ES_MPA = 200000.0
_N_STRIPS = 800


def _concrete_strips(r_o: float, r_i: float):
    dx = 2.0 * r_o / _N_STRIPS
    out = []
    for i in range(_N_STRIPS):
        x = -r_o + (i + 0.5) * dx
        w = 2.0 * (math.sqrt(max(r_o**2 - x**2, 0.0)) - math.sqrt(max(r_i**2 - x**2, 0.0)))
        out.append((x, w * dx))
    return out


def _bolt_positions(R_b: float, N: int, phase_rad: float):
    return [R_b * math.cos(phase_rad + 2.0 * math.pi * k / N) for k in range(N)]


def solve_ring_section(W: float, M: float, r_o: float, r_i: float, R_b: float,
                       N: int, A_b: float, n: float, phase_rad: float = 0.0) -> Optional[dict]:
    """W (N, basma +) ve M (N·mm) altında beton max basıncı ve cıvata çekmesi.

    Dönüş: {"fc_max","sigma_bolt_max","x_na","tension"} veya None (denge sağlanamaz).
    """
    area = math.pi * (r_o**2 - r_i**2)
    inertia = math.pi / 4.0 * (r_o**4 - r_i**4)
    if W <= 0:
        return None
    s_min = W / area - M * r_o / inertia
    if s_min >= 0.0:
        return {"fc_max": W / area + M * r_o / inertia, "sigma_bolt_max": 0.0,
                "x_na": None, "tension": False}
    strips = _concrete_strips(r_o, r_i)
    xb = _bolt_positions(R_b, N, phase_rad)
    e = M / W

    def a_m(xna: float):
        a = m = 0.0
        for x, dA in strips:
            d = x - xna
            if d > 0.0:
                a += d * dA
                m += d * x * dA
        for x in xb:
            d = xna - x
            if d > 0.0:
                a -= n * A_b * d
                m -= n * A_b * d * x  # çekme (−σ) x<0 tarafında: katkı +|x|
        return a, m

    def h(xna: float):
        a, m = a_m(xna)
        return m - e * a, a

    steps = 2000
    prev_x, prev_h, prev_a = None, None, None
    root = None
    for i in range(steps + 1):
        xna = r_o * (1.0 - 1e-6) - i * (2.0 * r_o * (1.0 - 1e-6)) / steps
        hv, a = h(xna)
        if a > 0 and prev_a is not None and prev_a > 0 and prev_h * hv <= 0.0:
            lo, hi = xna, prev_x
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                hm, _a = h(mid)
                if hm * h(lo)[0] <= 0.0:
                    hi = mid
                else:
                    lo = mid
            root = 0.5 * (lo + hi)
            break
        prev_x, prev_h, prev_a = xna, hv, a
    if root is None:
        return None
    a, _m = a_m(root)
    c = W / a
    return {"fc_max": c * (r_o - root),
            "sigma_bolt_max": max((n * c * (root - x) for x in xb), default=0.0),
            "x_na": root, "tension": True, "c": c}


def _worst(W, M, r_o, r_i, R_b, N, A_b, n):
    sols = [solve_ring_section(W, M, r_o, r_i, R_b, N, A_b, n, ph)
            for ph in (0.0, math.pi / N)]
    if any(s is None for s in sols):
        return None
    return max(sols, key=lambda s: (s["fc_max"], s["sigma_bolt_max"])) | {
        "fc_max_all": max(s["fc_max"] for s in sols),
        "sigma_bolt_all": max(s["sigma_bolt_max"] for s in sols),
    }


def check_skirt_base_ring(input_data: dict, ring, code: str = "ASME VIII-1",
                          edition: str = "") -> CalculationResult:
    """input_data: tag, skirt_mean_diameter_mm, skirt_thickness_mm, total_weight_N (basma),
    min_weight_N (uplift), overturning_moment_Nmm, horizontal_load_N. ring: SkirtBaseRingInput."""
    tag = input_data.get("tag", "SKIRT-01")
    result = CalculationResult(
        component_id=tag, component_type="support", calculation_type="skirt_base_ring",
        code=code, edition=edition,
        clause_reference="Moss PVDM Proc. 3-9 / Jawad-Farr base ring",
        formula_reference="Elastik halka kesiti: n=Es/Ec, beton basma + cıvata çekme dengesi",
    )
    D_m = input_data.get("skirt_mean_diameter_mm") or 0.0
    t_sk = input_data.get("skirt_thickness_mm") or 0.0
    W_c = input_data.get("total_weight_N") or 0.0
    W_u = input_data.get("min_weight_N") or 0.0
    M = max(0.0, input_data.get("overturning_moment_Nmm") or 0.0)
    V = max(0.0, input_data.get("horizontal_load_N") or 0.0)

    if D_m <= 0 or t_sk <= 0 or W_c <= 0 or W_u <= 0:
        result.set_not_calculated("Etek çapı/kalınlığı ve basma/uplift ağırlıkları pozitif olmalı.")
        return result
    missing = []
    if ring.bolt_allowable_tension_MPa is None:
        missing.append("bolt_allowable_tension_MPa")
    if V > 0 and ring.bolt_allowable_shear_MPa is None:
        missing.append("bolt_allowable_shear_MPa (yatay yük > 0)")
    if missing:
        result.set_blocked_missing_input(
            "Taban halkası girdisi eksik (çizelge değerleri K6 gereği kullanıcıdan): " + ", ".join(missing)
        )
        return result

    r_o, r_i = ring.ring_outer_diameter_mm / 2.0, ring.ring_inner_diameter_mm / 2.0
    R_b = ring.bolt_circle_diameter_mm / 2.0
    N = ring.bolt_count
    d_eff = ring.bolt_diameter_mm - ring.bolt_corrosion_allowance_mm
    if d_eff <= 0:
        result.set_not_calculated("Korozyon sonrası cıvata çapı <= 0.")
        return result
    A_b = ring.bolt_stress_area_mm2 or 0.75 * math.pi / 4.0 * d_eff**2
    if ring.bolt_stress_area_mm2 is None:
        result.add_assumption("K4: Cıvata çekme alanı girilmedi; 0,75·(π/4·d²) varsayıldı.")
    if not (r_i < R_b < r_o + 0.25 * (r_o - r_i) + 1e-9) or R_b <= 0:
        result.add_warning("Cıvata dairesi halka genişliğinin dışında/kenarında; geometri doğrulanmalı.")
    fc = ring.concrete_fc_MPa
    n = ring.modular_ratio_n or _ES_MPA / (4700.0 * math.sqrt(fc))
    if ring.modular_ratio_n is None:
        result.add_assumption(f"K4: n = Es/Ec = {n:.2f} (Ec = 4700·√f'c ACI 318, Es = 200000 MPa).")
    fc_allow = ring.concrete_allowable_bearing_MPa or 0.85 * fc / 2.31
    if ring.concrete_allowable_bearing_MPa is None:
        result.add_assumption("K4: Beton izin yataklık basıncı 0,85·f'c/2,31 (AISC 360 J8 ASD) varsayıldı.")
    Fb = ring.ring_allowable_bending_MPa or 0.66 * ring.ring_yield_MPa
    if ring.ring_allowable_bending_MPa is None:
        result.add_assumption("K4: Halka izin eğilme gerilmesi 0,66·Fy varsayıldı.")

    comp = _worst(W_c, M, r_o, r_i, R_b, N, A_b, n)
    upl = _worst(W_u, M, r_o, r_i, R_b, N, A_b, n)
    result.input_snapshot = {
        "W_comp_N": W_c, "W_min_N": W_u, "M_Nmm": M, "V_N": V, "n": n, "A_bolt_mm2": A_b,
        "fc_allow_MPa": fc_allow, "Fb_MPa": Fb,
    }
    if comp is None or upl is None:
        result.set_fail(float("inf"))
        result.add_warning(
            "Devirme momenti halka/ankraj kesitinin taşıyabileceği eksantrikliği aşıyor "
            "(denge sağlanamıyor): halka çapını/cıvata dairesini büyütün veya ağırlığı artırın."
        )
        return result

    fc_max = comp["fc_max_all"]
    sig_b = upl["sigma_bolt_all"]
    sk_out_r = (D_m + t_sk) / 2.0
    sk_in_r = (D_m - t_sk) / 2.0
    ell = max(r_o - sk_out_r, sk_in_r - r_i, 0.0)
    t_bear = ell * math.sqrt(3.0 * fc_max / Fb)
    x_b = abs(R_b - sk_out_r)
    b_eff = math.pi * 2.0 * R_b / N
    T_bolt = sig_b * A_b
    t_bolt = math.sqrt(6.0 * T_bolt * x_b / (b_eff * Fb)) if T_bolt > 0 else 0.0
    t_req = max(t_bear, t_bolt)
    tau = V / (N * A_b) if V > 0 else 0.0

    utils = {
        "beton_yataklik": fc_max / fc_allow,
        "civata_cekme": sig_b / ring.bolt_allowable_tension_MPa,
        "halka_kalinlik": t_req / ring.ring_thickness_mm,
        "civata_kesme": tau / ring.bolt_allowable_shear_MPa if V > 0 else 0.0,
    }
    governing = max(utils, key=utils.get)
    util = utils[governing]
    add = result.add_intermediate
    add("fc_max", fc_max, "MPa", "Beton max basınç (basma ağırlığı + M)")
    add("fc_allow", fc_allow, "MPa", "Beton izin yataklık")
    add("sigma_bolt", sig_b, "MPa", "Cıvata max çekme gerilmesi (uplift ağırlığı + M)")
    add("T_bolt", T_bolt, "N", "En çok yüklü cıvata çekme kuvveti")
    add("sigma_bolt_allow", ring.bolt_allowable_tension_MPa, "MPa", "Cıvata izin çekme")
    add("tau_bolt", tau, "MPa", "Cıvata kesme V/(N·A_b), sürtünme yok")
    add("cantilever_l", ell, "mm", "Halka konsol boyu")
    add("t_required_bearing", t_bear, "mm", "t = l·√(3·fc/Fb)")
    add("t_required_bolt", t_bolt, "mm", "t = √(6·T·x/(b·Fb))")
    add("t_ring", ring.ring_thickness_mm, "mm", "Girilen halka kalınlığı")
    for k, v in utils.items():
        add(f"util_{k}", v, "-", "Kullanım oranı")
    result.final_result = t_req
    result.final_result_unit = "mm"
    result.allowable_limit = ring.ring_thickness_mm
    result.allowable_limit_unit = "mm"
    result.utilization_ratio = util
    result.add_assumption(
        "Cıvata fazı (0 ve π/N) için en elverişsiz değer alındı; kesme sürtünmesiz; "
        "çekme-kesme etkileşimi, etek-halka kaynağı ve beton kopma kontrolü kapsam dışı."
    )
    if util > 1.0:
        result.set_fail(util)
        result.add_warning(f"Yöneten kontrol: {governing} (kullanım {util:.2f} > 1).")
    else:
        result.set_review_required(
            "Taban halkası/ankraj/beton kontrolleri sağlandı; basitleştirilmiş formüller "
            "(verified:false) nedeniyle nihai PASS değildir, mühendis incelemesi gerekir."
        )
        result.utilization_ratio = util
    return result
