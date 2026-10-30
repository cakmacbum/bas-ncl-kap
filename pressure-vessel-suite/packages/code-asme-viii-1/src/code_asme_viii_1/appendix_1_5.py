"""ASME VIII-1 Appendix 1-5 — koni/silindir birleşimi takviye halkası (iç basınç).

Yöntem (verified:false — lisanslı metinle satır satır doğrulanmadı):
  * Birleşimde koni meridyen kuvvetinin radyal bileşeni, statikten:
        Q = P*R/2           (çevre birim uzunluğu başına eksenel kuvvet)
        radyal çizgi yükü = Q*tan(alpha)
    Gerekli takviye alanı (App. 1-5 form yapısı):
        A_r = k * Q * R * tan(alpha) / (S*E) * (1 - Delta/alpha)
  * Etkin genişlik (App. 1-5/1-8): silindirde 0,78*sqrt(R*t_s), konide
    0,78*sqrt(R*t_c/cos(alpha)).
  * Mevcut alan: A_e = w_s*(t_s - t_sr) + w_c*(t_c - t_cr) + ek halka alanı.

Kaynak notu: Delta (Table 1-5.2) lisanslı çizelgedir; K6 gereği koda gömülmez,
kullanıcı girer (boşsa Delta=0 -> güvenli taraf). Q için sade statik denge
kullanıldı; ASME'nin Q_L/Q_S ifadeleri ile karşılaştırılmalıdır, bu yüzden
sonuç PASS olsa bile REVIEW_REQUIRED kalır. alpha > 30 deg ve dış basınç
kapsam dışıdır.
"""

from __future__ import annotations

import math
from typing import Optional

from code_asme_viii_1 import formulas

K_EFFECTIVE_WIDTH = 0.78  # App. 1-5/1-8 etkin genişlik katsayısı


def effective_width(R: float, t: float, alpha_deg: float = 0.0) -> float:
    """w = 0,78*sqrt(R*t/cos(alpha)) (silindir için alpha=0)."""
    if R <= 0 or t <= 0:
        return 0.0
    return K_EFFECTIVE_WIDTH * math.sqrt(R * t / math.cos(math.radians(alpha_deg)))


def required_ring_area(P: float, R: float, alpha_deg: float, SE: float,
                       delta_deg: float = 0.0, k: float = 1.0) -> tuple[float, float]:
    """(Q [N/mm], A_r [mm2]). alpha=0 veya Delta>=alpha -> A_r = 0."""
    if alpha_deg <= 0 or SE <= 0:
        raise ValueError("alpha > 0 ve S*E > 0 olmalı")
    Q = P * R / 2.0
    reduction = max(0.0, 1.0 - delta_deg / alpha_deg)
    A_r = k * Q * R * math.tan(math.radians(alpha_deg)) / SE * reduction
    return Q, A_r


def _mat_weld(project, material_id: str, weld_joint_id: Optional[str]):
    mat = project.get_material(material_id)
    weld = project.get_weld(weld_joint_id) if weld_joint_id else None
    return mat, (weld.joint_efficiency if weld else None)


def evaluate_cone_junction(result, project, junction, cone, other, other_type: str) -> None:
    """Birleşim sonucunu (CalculationResult) App. 1-5 ile doldurur; girdi tamsa çağrılır."""
    result.clause_reference = "Appendix 1-5"
    result.formula_reference = "A_r = k*Q*R*tan(a)/(S*E)*(1-D/a); A_e = w_s*dt_s + w_c*dt_c"
    if cone is None or other is None or other_type != "shell":
        result.set_out_of_scope("Appendix 1-5 takviye kontrolü yalnız koni-silindir birleşimi için uygulandı.")
        return
    alpha = cone.half_apex_angle
    if alpha <= 0 or alpha > 30:
        result.set_out_of_scope("App. 1-5 yöntemi 0° < alpha <= 30° için uygulanır; bu açı kapsam dışı.")
        return
    P = project.design_conditions.design_pressure
    mat_s, E_s = _mat_weld(project, other.material_id, other.weld_joint_id)
    mat_c, E_c = _mat_weld(project, cone.material_id, cone.weld_joint_id)
    if mat_s is None or mat_c is None:
        result.set_blocked_missing_input("Gövde veya koni malzemesi projede bulunamadı.")
        return
    E_j = junction.weld_efficiency
    E_s = E_s if E_s is not None else E_j
    E_c = E_c if E_c is not None else E_j
    design = None
    for d in (getattr(getattr(project, "cone_base", None), "junctions", None) or []):
        if d.junction_id == junction.junction_id:
            design = d
    delta = design.delta_deg if design and design.delta_deg is not None else 0.0
    extra = design.extra_ring_area_mm2 if design else 0.0
    if design is None or design.delta_deg is None:
        result.add_assumption(
            "K4/K6: Table 1-5.2 Delta girilmedi; Delta = 0 (güvenli taraf) alındı. "
            "Lisanslı çizelgeden okunan değer `cone_base.junctions[].delta_deg` ile girilebilir."
        )

    end = junction.cone_end
    C_s_i, C_s_e = other.internal_corrosion_allowance, other.external_corrosion_allowance
    C_c_i, C_c_e = cone.internal_corrosion_allowance, cone.external_corrosion_allowance
    d_in_s = other.inside_diameter if other.inside_diameter else other.outside_diameter - 2 * other.nominal_thickness
    R_s = d_in_s / 2.0 + C_s_i
    R_c = (cone.large_diameter if end == "large" else cone.small_diameter) / 2.0 + C_c_i
    t_s = other.nominal_thickness - C_s_i - C_s_e
    t_c = cone.nominal_thickness - C_c_i - C_c_e
    if t_s <= 0 or t_c <= 0:
        result.set_blocked_missing_input("Korozyon payı sonrası net cidar <= 0.")
        return
    S_s, S_c = mat_s.allowable_stress, mat_c.allowable_stress
    try:
        _, _, t_sr = formulas.shell_thickness_internal_pressure(P, R_s, S_s, E_s)
        t_cr = formulas.cone_thickness(P, 2 * R_c, S_c, E_c, alpha)
        # Takviye paydasında güvenli taraf: iki tarafın küçüğü
        SE = min(S_s * E_s, S_c * E_c)
        Q, A_r = required_ring_area(P, R_c, alpha, SE, delta)
    except ValueError as exc:
        result.set_not_calculated(str(exc))
        return
    w_s = effective_width(R_s, t_s)
    w_c = effective_width(R_c, t_c, alpha)
    A_e = w_s * max(0.0, t_s - t_sr) + w_c * max(0.0, t_c - t_cr) + extra

    add = result.add_intermediate
    add("P", P, "MPa", "Tasarım basıncı (statik yük hariç)")
    add("R_junction", R_c, "mm", "Birleşim iç yarıçapı (korozyonlu)")
    add("alpha", alpha, "deg", "Yarı tepe açısı")
    add("delta", delta, "deg", "Table 1-5.2 Delta")
    add("Q", Q, "N/mm", "Q = P*R/2 (statik denge)")
    add("SE_governing", SE, "MPa", "min(S*E) silindir/koni")
    add("t_s_net", t_s, "mm", "Silindir net cidar")
    add("t_sr", t_sr, "mm", "Silindir gerekli (UG-27)")
    add("t_c_net", t_c, "mm", "Koni net cidar")
    add("t_cr", t_cr, "mm", "Koni gerekli (UG-32(g))")
    add("w_shell", w_s, "mm", "Silindir etkin genişlik 0,78*sqrt(R*t)")
    add("w_cone", w_c, "mm", "Koni etkin genişlik 0,78*sqrt(R*t/cos a)")
    add("A_r", A_r, "mm2", "Gerekli takviye alanı")
    add("A_e", A_e, "mm2", "Mevcut alan")
    result.final_result = A_r
    result.final_result_unit = "mm2"
    result.allowable_limit = A_e
    result.allowable_limit_unit = "mm2"
    result.input_snapshot.update({"P_MPa": P, "end": end, "A_r_mm2": A_r, "A_e_mm2": A_e})
    result.add_assumption("Yalnız iç basınç; dış basınç, eksenel/eğilme yükleri ve Q_L/Q_S'nin kod ifadesi kapsam dışı.")
    if A_r <= 0:
        result.utilization_ratio = 0.0
        result.set_review_required("Delta >= alpha: takviye gerekmiyor; formül doğrulanmamış (verified:false), mühendis incelemesi gerekir.")
        return
    util = A_r / A_e if A_e > 0 else float("inf")
    result.utilization_ratio = util
    if util > 1.0:
        result.set_fail(util)
        result.add_warning(f"Gerekli takviye alanı {A_r:.0f} mm2 > mevcut {A_e:.0f} mm2; halka ekleyin/kalınlaştırın.")
    else:
        result.set_review_required(
            "App. 1-5 takviye kontrolü sağlandı ancak formül yapısı lisanslı metinle doğrulanmadı "
            "(verified:false); nihai PASS değildir."
        )
        result.utilization_ratio = util
