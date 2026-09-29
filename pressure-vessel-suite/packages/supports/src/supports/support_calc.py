"""SupportCalculator — saddle (Zick) ve skirt destek hesaplayıcı.

Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult
from supports import formulas, leg_detail


class SupportCalculator:
    """Destek hesaplayıcı.

    Yatay kaplar için saddle (Zick analizi), dikey kaplar için skirt temeli.

    Kullanım:
        calc = SupportCalculator()
        result = calc.check_saddle(input_data)
    """

    def __init__(self, code: str = "ASME VIII-1", edition: str = "2025"):
        self._code = code
        self._edition = edition

    def check_saddle(self, input_data: dict) -> CalculationResult:
        """Eyer (Zick 1951) kontrolü — iki eyerli yatay kap.

        Formül yapısı (M1, M2, membran, boynuz eğilmesi, kesme, sınırlar) kodda;
        K1/K2/K3/K6/K7 katsayı tabloları K6 gereği kodda YOKTUR — kullanıcı
        Zick 1951 / Moss PVDM Prosedür 3-10 tablosundan θ, halka durumu ve A/R'ye
        göre okuyup `support` içinde verir. Eksikse sonuç BLOCKED_CODE_DATA.

        Args:
            input_data: {
                "support": {
                    "tag": str, "location_mm": float,   # bu eyerin küresel konumu
                    "width_mm": float,                  # b
                    "contact_angle_deg": float,         # θ (K okumak için)
                    "saddle_stiffened": bool,           # eyer düzleminde halka
                    "zick_K1", "zick_K2", "zick_K3", "zick_K6", "zick_K7": float | None,
                },
                "shell": ShellSection,
                "vessel_length": float,        # L: teğet-teğet kap boyu (mm)
                "tangent_start_mm": float,     # ilk teğet çizgisinin küresel konumu
                "saddle_positions_mm": [x1, x2],  # TÜM eyerlerin konumları
                "head_depth_mm": float,        # H: başlık derinliği (D/4 = 2:1 eliptik)
                "head_thickness_mm": float,    # t_h (korozyonlu; yalnız A ≤ R/2)
                "joint_efficiency": float,     # E (yoksa 1,0 varsayımı yazılır)
                "total_weight_N": float,       # W (hangi durum: "weight_case")
                "materials": [...], "design_conditions": DesignConditions,
            }

        Bu eyerin A'sı en yakın teğet çizgisine mesafesidir (sol eyer A_sol, sağ
        eyer A_sağ); her eyer kendi Q ve A'sıyla ayrı sonuç üretir, iki uç
        arasında büyük A ayrıca ara değer olarak raporlanır. Q, ağırlık
        merkezinin teğet-teğet orta noktada olduğu varsayımıyla moment
        dengesinden hesaplanır (simetri yoksa W/2 değildir).

        Returns:
            CalculationResult — FAIL, REVIEW_REQUIRED (nihai PASS yoktur),
            BLOCKED_CODE_DATA, BLOCKED_MISSING_INPUT, OUT_OF_SCOPE ya da NOT_CALCULATED.
        """
        support = input_data["support"]
        shell = input_data["shell"]
        W_total = input_data.get("total_weight_N", 0.0)
        materials = input_data.get("materials", [])
        dc = input_data.get("design_conditions")

        tag = support.get("tag", "SADDLE-01")
        b = support.get("width_mm") or 0.0
        theta = support.get("contact_angle_deg")
        x_self = support.get("location_mm")

        result = CalculationResult(
            component_id=tag,
            component_type="support",
            calculation_type="saddle_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Zick Analysis",
            formula_reference="Zick (1951); Moss PVDM Procedure 3-10",
        )

        mat = None
        for m in materials:
            if m.material_id == shell.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(
                f"Shell material '{shell.material_id}' not found. "
                "Saddle calculation requires material properties."
            )
            return result

        if W_total <= 0:
            result.set_not_calculated(
                "Total weight not specified. Saddle calculation requires vessel weight."
            )
            return result

        positions = input_data.get("saddle_positions_mm")
        if positions is not None:
            positions = sorted(float(x) for x in positions)
            if len(positions) >= 3:
                result.set_out_of_scope(
                    f"{len(positions)} eyer var: Zick yalnız iki eyerli kap için geçerlidir "
                    "(üç ve fazlası statik belirsizdir); ayrıntılı analiz/FEA gerekir."
                )
                return result
            if len(positions) < 2:
                result.set_not_calculated(
                    "Zick analizi iki eyer gerektirir; tek eyer tanımlı."
                )
                return result

        # ── Eksik girdiler (sessiz varsayım YOK) ─────────────────────────────
        L = input_data.get("vessel_length")
        x0 = input_data.get("tangent_start_mm")
        H = input_data.get("head_depth_mm")
        ring = support.get("saddle_stiffened")
        missing = []
        if positions is None:
            missing.append("saddle_positions_mm (iki eyerin konumu)")
        if not L or L <= 0:
            missing.append("vessel_length (teğet-teğet L)")
        if x0 is None:
            missing.append("tangent_start_mm")
        if H is None or H < 0:
            missing.append("head_depth_mm (başlık derinliği H; başlık tanımı gerekli)")
        if b <= 0:
            missing.append("eyer genişliği b (width_mm)")
        if x_self is None:
            missing.append("eyer konumu (location_mm)")
        if ring is None:
            missing.append("saddle_stiffened (eyer düzleminde halka var mı)")
        if dc is None:
            missing.append("design_conditions (basınç)")
        if missing:
            result.set_blocked_missing_input(
                "Zick eyer hesabı için eksik girdi: " + "; ".join(missing) + "."
            )
            return result

        # ── Gövde (korozyonlu) ───────────────────────────────────────────────
        t_nom = shell.nominal_thickness
        t = t_nom - shell.internal_corrosion_allowance - shell.external_corrosion_allowance
        if t <= 0:
            result.set_not_calculated("Korozyonlu gövde kalınlığı sıfır veya negatif.")
            return result
        if shell.inside_diameter:
            D_i = shell.inside_diameter
        else:
            D_i = shell.outside_diameter - 2 * t_nom
        R_m = D_i / 2.0 + shell.internal_corrosion_allowance + t / 2.0

        # ── Eyer geometrisi ve reaksiyonlar ──────────────────────────────────
        x_end = x0 + L
        x_left, x_right = positions
        if abs(x_self - x_left) <= 1e-6:
            is_left = True
        elif abs(x_self - x_right) <= 1e-6:
            is_left = False
        else:
            result.set_not_calculated("Eyer konumu saddle_positions_mm içinde bulunamadı.")
            return result
        A_left = x_left - x0
        A_right = x_end - x_right
        if A_left <= 0 or A_right <= 0:
            result.set_not_calculated(
                f"Eyer teğet-teğet aralığın dışında: A_sol={A_left:g}, A_sağ={A_right:g} mm."
            )
            return result
        A = A_left if is_left else A_right
        x_cg = x0 + L / 2.0
        try:
            Q_left, Q_right = formulas.saddle_reactions_two(W_total, x_left, x_right, x_cg)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result
        if Q_left <= 0 or Q_right <= 0:
            result.set_out_of_scope(
                f"Ağırlık merkezi eyerlerin dışında: Q_sol={Q_left:.0f} N, Q_sağ={Q_right:.0f} N "
                "(kap devrilir / kaldırma) — Zick geçersiz."
            )
            return result
        Q = Q_left if is_left else Q_right

        head_stiff = (not ring) and A <= R_m / 2.0
        P = dc.design_pressure
        S_allow = mat.allowable_stress
        E = input_data.get("joint_efficiency")
        E_assumed = E is None
        if E_assumed:
            E = 1.0
        limits = formulas.saddle_stress_limits(S_allow, mat.yield_strength, E)
        t_head = input_data.get("head_thickness_mm")
        if head_stiff and (not t_head or t_head <= 0):
            result.set_blocked_missing_input(
                "A ≤ R/2 (eyer başlığa yakın): başlık kesmesi için korozyonlu başlık "
                "kalınlığı (head_thickness_mm) gerekli."
            )
            return result

        result.input_snapshot = {
            "tag": tag,
            "D_i_mm": D_i,
            "R_m_mm": R_m,
            "t_corroded_mm": t,
            "L_mm": L,
            "H_mm": H,
            "A_mm": A,
            "A_left_mm": A_left,
            "A_right_mm": A_right,
            "A_governing_mm": max(A_left, A_right),
            "b_mm": b,
            "theta_deg": theta,
            "saddle_stiffened": bool(ring),
            "head_stiffened_A_le_R_over_2": head_stiff,
            "W_total_N": W_total,
            "weight_case": input_data.get("weight_case", "belirtilmedi"),
            "Q_left_N": Q_left,
            "Q_right_N": Q_right,
            "Q_N": Q,
            "P_MPa": P,
            "E": E,
        }

        # ── Katsayısız yapısal ara değerler ──────────────────────────────────
        try:
            M1 = formulas.zick_moment_saddle(Q, L, R_m, A, H)
            M2 = formulas.zick_moment_midspan(Q, L, R_m, A, H)
            S1_mid = formulas.zick_longitudinal_stress_midspan(M2, R_m, t)
            S_p = formulas.zick_pressure_longitudinal(P, R_m, t)
            S4_membrane = formulas.zick_circumferential_membrane(Q, R_m, t, b)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        result.add_intermediate("Q", Q, "N", "Eyer reaksiyonu (moment dengesi)")
        result.add_intermediate("R_m", R_m, "mm", "Ortalama yarıçap (korozyonlu)")
        result.add_intermediate("t", t, "mm", "Korozyonlu gövde kalınlığı")
        result.add_intermediate("L", L, "mm", "Teğet-teğet kap boyu")
        result.add_intermediate("H", H, "mm", "Başlık derinliği")
        result.add_intermediate("A", A, "mm", "Bu eyerin teğet çizgisine uzaklığı")
        result.add_intermediate("A_left", A_left, "mm", "Sol eyer A")
        result.add_intermediate("A_right", A_right, "mm", "Sağ eyer A")
        result.add_intermediate("M1", M1, "N·mm", "Eyer kesiti boyuna moment (+ = hogging)")
        result.add_intermediate("M2", M2, "N·mm", "Orta açıklık boyuna moment (+ = sagging)")
        result.add_intermediate("S1_midspan", S1_mid, "MPa", "|M2|/(π R² t)")
        result.add_intermediate("S_pressure_long", S_p, "MPa", "P·R/(2t)")
        result.add_intermediate("S4_membrane", S4_membrane, "MPa", "Boynuz membran terimi Q/(4t(b+1,56√(Rt)))")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")
        result.add_intermediate("Sy", mat.yield_strength, "MPa", "Akma dayanımı")

        # ── Kullanıcı katsayıları (K6: tablo kodda yok) ──────────────────────
        K1 = math.pi if (ring or head_stiff) else support.get("zick_K1")
        K2 = 1.0 / math.pi if ring else support.get("zick_K2")
        K3 = support.get("zick_K3") if head_stiff else None
        K6 = support.get("zick_K6") if not ring else None
        K7 = support.get("zick_K7")
        need = []
        if not K1:
            need.append("zick_K1")
        if not K2:
            need.append("zick_K2")
        if head_stiff and not K3:
            need.append("zick_K3 (başlık kesmesi)")
        if (not ring) and not K6:
            need.append("zick_K6")
        if not K7:
            need.append("zick_K7")
        if need:
            result.set_blocked_code_data(
                "Zick katsayıları girilmedi: " + ", ".join(need) + ". Program K tablosunu "
                "İÇERMEZ (lisans/K6): K değerlerini Zick 1951 / Moss PVDM Prosedür 3-10 "
                f"tablosundan θ={theta if theta is not None else '?'}° ve halka durumuna "
                "(halkasız/halkalı/A ≤ R/2, A/R) göre okuyup girin."
            )
            return result

        # ── Gerilmeler ───────────────────────────────────────────────────────
        try:
            S1_sad = formulas.zick_longitudinal_stress_saddle(M1, K1, R_m, t)
            S2 = formulas.zick_shear_shell(Q, R_m, t, L, A, H, K2, head_stiffened=head_stiff)
            S5 = formulas.zick_circumferential_bottom(Q, R_m, t, b, K7)
            S3 = formulas.zick_shear_head(Q, R_m, t_head, K3) if head_stiff else None
            S4 = (
                formulas.zick_circumferential_horn(Q, R_m, t, b, L, K6) if not ring else None
            )
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        S1_max = max(S1_sad, S1_mid)
        checks = [
            ("S1_tension", S1_max + S_p, limits["S1_tension"], "Boyuna eğilme + P·R/2t (çekme)"),
            ("S1_compression", S1_max, limits["S1_compression"], "Boyuna eğilme (basma)"),
            ("S2", S2, limits["S2"], "Kabuk teğetsel kesme"),
            ("S5", S5, limits["S5"], "Eyer altı çevresel basma"),
        ]
        if S3 is not None:
            checks.append(("S3", S3, limits["S3"], "Başlık kesmesi"))
        if S4 is not None:
            checks.append(("S4", S4, limits["S4"], "Eyer boynuzu çevresel (membran+eğilme)"))

        result.add_intermediate("K1", K1, "-", "K1 (kullanıcı / π)")
        result.add_intermediate("K2", K2, "-", "K2 (kullanıcı / 1/π)")
        if K3:
            result.add_intermediate("K3", K3, "-", "K3 (kullanıcı)")
        if K6:
            result.add_intermediate("K6", K6, "-", "K6 (kullanıcı)")
        result.add_intermediate("K7", K7, "-", "K7 (kullanıcı)")
        result.add_intermediate("S1_saddle", S1_sad, "MPa", "|M1|/(K1 R² t)")

        max_ratio = 0.0
        critical = None
        failures = []
        for name, s, lim, desc in checks:
            ratio = s / lim if lim > 0 else float("inf")
            result.add_intermediate(name, s, "MPa", desc)
            result.add_intermediate(f"{name}_limit", lim, "MPa", f"{name} sınırı")
            result.add_intermediate(f"{name}_ratio", ratio, "-", f"{name} kullanım oranı")
            if ratio > max_ratio or critical is None:
                max_ratio, critical = ratio, (name, s, lim)
            if s > lim:
                failures.append(f"{name}={s:.2f} > sınır={lim:.2f} MPa")

        result.final_result = critical[1]
        result.final_result_unit = "MPa"
        result.allowable_limit = critical[2]
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = max_ratio
        result.add_intermediate("governing_check", critical[0], "-", "En yüksek kullanım oranlı kontrol")

        # ── Uyarılar / varsayımlar ───────────────────────────────────────────
        result.add_assumption(
            "Zick: ağırlık merkezi teğet-teğet orta noktada; iki başlık aynı H ve "
            "uniform gövde et kalınlığı varsayıldı. Simetri yoksa Q moment dengesinden "
            "hesaplandı ve her eyer kendi Q/A'sıyla değerlendirildi (yaklaşık)."
        )
        result.add_assumption(
            f"Yük durumu: W = {W_total:.0f} N ({input_data.get('weight_case', 'ağırlık durumu belirtilmedi')})."
        )
        result.add_assumption(
            "S1 basma ve çekme tarafında aynı K1 kullanıldı (|M| ile); basma tarafı K1' "
            "ayrımı yapılmadı, basınç gerilmesi yalnız çekmeye eklendi."
        )
        if E_assumed:
            result.add_assumption("Eklem verimi E girilmedi → 1,0 varsayıldı (S1 çekme sınırı S·E).")
        if abs(A_left - A_right) > 1e-6 * L:
            result.add_warning(
                f"Asimetrik eyer yerleşimi (A_sol={A_left:g}, A_sağ={A_right:g} mm): Zick simetrik "
                "türetilmiştir; sonuç yaklaşıktır."
            )
        if A > L / 4.0:
            result.add_warning("A > L/4: Zick kesme ifadesi bu aralıkta geçerlilik sınırının dışında.")
        if theta is None:
            result.add_notice("θ (contact_angle_deg) girilmedi; K katsayıları θ'ya göre okunmalıdır.")
        elif theta < 120.0:
            result.add_warning("θ < 120°: kod asgari eyer sarma açısı 120° (Zick 1951).")
        if t / R_m < 0.005:
            result.add_warning(
                "t/R < 0,005: basma tarafında burkulma sınırı (UG-23(b), B) hesaplanmadı; "
                "yalnız 0,5·Sy sınırı uygulandı."
            )
        if ring:
            result.add_warning(
                "Halkalı eyer: halka tasarımı ve eyer boynuzu çevresel eğilme (S4) hesaplanmadı."
            )
        result.add_warning(
            "Aşınma plakası (S5 için b ve t artışı), eyer yapısı ve temel bu kontrolde YOK."
        )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "yield_strength": mat.yield_strength,
            "source_reference": mat.source_reference,
        }

        if failures:
            result.set_fail(max_ratio)
            result.add_warning(f"Saddle stress check failed: {'; '.join(failures)}")
        else:
            result.set_review_required(
                "Zick yapısı uygulandı ancak yük durumları, halka/aşınma plakası, burkulma "
                "ve eyer/temel kontrolleri tam değil. Bağımsız mühendislik incelemesi gerekir; "
                "bu sonuç nihai PASS değildir."
            )
            result.utilization_ratio = max_ratio
        return result

    def check_skirt(self, input_data: dict) -> CalculationResult:
        """Skirt (etek destek) kontrolü — basma (burkulma dahil) ve çekme.

        Etek ORTALAMA çap (`diameter_mm`) ve et kalınlığı ile modellenir.
        Basma: S_c = W/A + M/Z <= min(S, B); B = UG-23(b) çizelge faktörü
        (kullanıcı girdisi, K6). Çekme: S_t = M/Z - W_min/A <= S*E (E: etek
        kaynak verimi, girilmezse 0,6 VARSAYIMI). Ankraj/taban plakası/kaldırma
        kontrolü kapsam dışıdır.

        Args:
            input_data: {
                "support": {
                    "tag": str, "type": "skirt",
                    "diameter_mm": float,   # ORTALAMA çap
                    "thickness_mm": float, "height_mm": float,
                    "skirt_allowable_compressive_MPa": float | None,  # B
                    "skirt_weld_efficiency": float | None,
                },
                "total_weight_N": float,     # basma için ağırlık
                "min_weight_N": float | None,  # çekme için (boş kap); yoksa total
                "overturning_moment_Nmm": float,
                "materials": List[MaterialProperty],
                "design_conditions": DesignConditions,
                "skirt_material_id": str,
            }
        """
        support = input_data["support"]
        W_total = input_data.get("total_weight_N", 0.0)
        W_min_in = input_data.get("min_weight_N")
        M_overturn = input_data.get("overturning_moment_Nmm", 0.0)
        materials = input_data.get("materials", [])
        skirt_mat_id = input_data.get("skirt_material_id", "")

        tag = support.get("tag", "SKIRT-01")
        D_skirt = support.get("diameter_mm") or 0.0
        t_skirt = support.get("thickness_mm") or 0.0
        B_user = support.get("skirt_allowable_compressive_MPa") or 0.0
        E_user = support.get("skirt_weld_efficiency")

        result = CalculationResult(
            component_id=tag,
            component_type="support",
            calculation_type="skirt_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Moss PVDM Proc. 4-1 / UG-23(b)",
            formula_reference="Skirt compression (B factor) and tension check",
        )

        mat = None
        for m in materials:
            if m.material_id == skirt_mat_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(
                f"Skirt material '{skirt_mat_id}' not found."
            )
            return result

        if W_total <= 0:
            result.set_not_calculated("Total weight not specified.")
            return result

        if D_skirt <= 0 or t_skirt <= 0:
            result.set_not_calculated("Skirt diameter and thickness must be positive.")
            return result

        if E_user is not None and not (0.0 < E_user <= 1.0):
            result.set_not_calculated("skirt_weld_efficiency must satisfy 0 < E <= 1.")
            return result
        E_weld = E_user if E_user else 0.6
        W_min = W_total if W_min_in is None else W_min_in

        result.input_snapshot = {
            "tag": tag,
            "D_skirt_mean_mm": D_skirt,
            "t_skirt_mm": t_skirt,
            "W_total_N": W_total,
            "W_min_N": W_min,
            "M_overturning_Nmm": M_overturn,
            "skirt_allowable_compressive_B_MPa": B_user or None,
            "skirt_weld_efficiency": E_weld,
        }

        try:
            S_bend = formulas.skirt_bending_stress(M_overturn, D_skirt, t_skirt)
            S_comp = formulas.skirt_compression_stress(W_total, D_skirt, t_skirt)
            S_comb = formulas.skirt_combined_stress(S_bend, S_comp)
            S_ten = formulas.skirt_tensile_stress(M_overturn, W_min, D_skirt, t_skirt)
            A_geom = formulas.skirt_geometric_factor_A(D_skirt, t_skirt)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        S_allow = mat.allowable_stress
        S_allow_t = S_allow * E_weld

        result.add_intermediate("D_skirt_mean", D_skirt, "mm", "Skirt MEAN diameter")
        result.add_intermediate("t_skirt", t_skirt, "mm", "Skirt thickness")
        result.add_intermediate("W_total", W_total, "N", "Weight used for compression")
        result.add_intermediate("W_min", W_min, "N", "Minimum weight used for tension")
        result.add_intermediate("M_overturning", M_overturn, "N·mm", "Overturning moment")
        result.add_intermediate("S_bending", S_bend, "MPa", "Bending stress M/Z")
        result.add_intermediate("S_compression", S_comp, "MPa", "Axial compression W/A")
        result.add_intermediate("S_combined", S_comb, "MPa", "Combined compressive stress W/A + M/Z")
        result.add_intermediate("S_tension", S_ten, "MPa", "Tension side M/Z - W_min/A (<=0: none)")
        result.add_intermediate("S_allow", S_allow, "MPa", "Tensile allowable stress S")
        result.add_intermediate("S_allow_tension", S_allow_t, "MPa", "S*E_weld")
        result.add_intermediate("A_geometric", A_geom, "-", "A = 0.125/(R/t), for B chart lookup (info)")
        result.add_intermediate("E_weld", E_weld, "-", "Skirt weld efficiency used")
        if E_user is None:
            result.add_assumption(
                "K4: Etek kaynak verimi girilmedi; E = 0,6 VARSAYILDI (çekme tarafı S·E). "
                "Gerçek birleşim verimini `skirt_weld_efficiency` ile girin."
            )
        result.add_assumption(
            "Etek çapı ORTALAMA çap olarak alınır; dış çap girilirse gerilme %1-2 "
            "emniyetsiz çıkar."
        )
        if W_min_in is None:
            result.add_assumption(
                "K4: Çekme kontrolü için ayrı minimum (boş) ağırlık verilmedi; "
                "W_min = W_total alındı."
            )

        ten_util = S_ten / S_allow_t if S_ten > 0 and S_allow_t > 0 else 0.0
        S_allow_c = min(S_allow, B_user) if B_user > 0 else None

        if S_allow_c is not None:
            comp_util = S_comb / S_allow_c
            result.add_intermediate("B_factor", B_user, "MPa", "UG-23(b) B (user input)")
            result.add_intermediate("S_allow_compressive", S_allow_c, "MPa", "min(S, B)")
            result.allowable_limit = S_allow_c
        else:
            # B eksik: B, S'yi geçemez; S üst sınırdır.
            comp_util = S_comb / S_allow if S_allow > 0 else float("inf")
            result.allowable_limit = S_allow if comp_util > 1.0 else None
        util = max(comp_util, ten_util)

        result.final_result = S_comb
        result.final_result_unit = "MPa"
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = util

        if S_ten > 0:
            result.add_warning(
                f"Etekte çekme (kaldırma) tarafı {S_ten:.2f} MPa: ankraj/taban plakası/"
                "kaldırma kontrolü bu modülde YOK; ayrıca doğrulanmalı."
            )

        if ten_util > 1.0:
            result.set_fail(util)
            result.add_warning(
                f"Skirt tension {S_ten:.2f} MPa exceeds S·E = {S_allow_t:.2f} MPa."
            )
        elif S_allow_c is None and comp_util > 1.0:
            result.set_fail(util)
            result.add_warning(
                f"Skirt combined compressive stress {S_comb:.2f} MPa exceeds tensile "
                f"allowable S = {S_allow:.2f} MPa (upper bound of UG-23(b)); FAIL "
                "independent of B."
            )
        elif S_allow_c is None:
            result.utilization_ratio = None
            result.set_blocked_code_data(
                "UG-23(b) B faktörü girilmedi: etek basma/burkulma kontrolü yapılamaz. "
                "Destek formunda `skirt_allowable_compressive_MPa` alanına tasarım "
                "sıcaklığında Fig. çizelgesinden okunan B değerini girin "
                f"(A = 0.125/(R/t) = {A_geom:.5f}; K6: çizelge repoda tutulmaz)."
            )
        elif comp_util > 1.0:
            result.set_fail(util)
            result.add_warning(
                f"Skirt combined compressive stress {S_comb:.2f} MPa exceeds "
                f"allowable min(S,B) = {S_allow_c:.2f} MPa."
            )
        else:
            result.set_review_required(
                "Etek gerilme/burkulma kontrolü geçti; taban plakası, ankraj, temel, "
                "açıklık/bağlantı ve yerel kabuk etkileri kapsam dışıdır. Bağımsız "
                "mühendislik incelemesi gerekir; bu sonuç nihai PASS değildir."
            )
            result.utilization_ratio = util

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "source_reference": mat.source_reference,
        }

        return result

    def check_leg_detail(self, input_data: dict) -> List[CalculationResult]:
        """Ayak alt kontrolleri: leg_section_check, leg_weld_check, base_plate_check, wrc_local_stress.

        Yalnız `support.leg_section_type` doluysa anlamlıdır (boşsa boş liste döner: eski
        boru-ayak davranışı, yalnız `leg_stress`). Formüller `sections.py`, `wrc.py`,
        `formulas.py`, `welds.strength` içindedir; `leg_detail.py` orkestre eder.
        """
        if not input_data["support"].get("leg_section_type"):
            return []
        return leg_detail.check_leg_detail(input_data, self._code, self._edition)

    def summarize_leg(self, leg_result: CalculationResult, details: List[CalculationResult]) -> None:
        """`leg_stress` özetini alt kontrol durumlarıyla zenginleştirir; nihai PASS vermez."""
        if details:
            leg_detail.summarize_leg(leg_result, details)

    def check_leg_support(self, input_data: dict) -> CalculationResult:
        """Ayak (leg) destek kontrolü.

        Simetrik ayak takımı; takım tek birim olarak modellenir
        (bkz. `formulas.leg_reaction_extremes`). Ayak boru kesitlidir — dış
        çap `leg_diameter_mm` ve et kalınlığı `leg_thickness_mm` halka
        kesit alanını belirler (bkz. `formulas.leg_pipe_section_area`);
        `base_plate_area_mm2` verilmişse o alan tercih edilir.

        Args:
            input_data: {
                "support": {
                    "tag": str,
                    "type": "leg",
                    "n_legs": int,
                    "leg_diameter_mm": float,   # ayak dış çapı
                    "leg_thickness_mm": float,  # ayak et kalınlığı
                    "support_radius_mm": float, # moment kolu
                    "base_plate_area_mm2": float,
                },
                "total_weight_N": float,
                "overturning_moment_Nmm": float,
                "materials": List[MaterialProperty],
                "skirt_material_id": str,
            }
        """
        support = input_data["support"]
        W_total = input_data.get("total_weight_N", 0.0)
        M_overturn = input_data.get("overturning_moment_Nmm", 0.0)
        materials = input_data.get("materials", [])
        skirt_mat_id = input_data.get("skirt_material_id", "")

        tag = support.get("tag", "LEG-01")
        n_legs = support.get("n_legs") or 0
        D_leg = support.get("leg_diameter_mm") or 0.0
        t_leg = support.get("leg_thickness_mm") or 0.0
        support_radius = support.get("support_radius_mm") or 0.0
        A_base = support.get("base_plate_area_mm2") or 0.0
        n_anchor = support.get("anchor_bolt_count") or 0
        anchor_tension_allowable = support.get("anchor_tension_allowable_N") or 0.0
        anchor_shear_allowable = support.get("anchor_shear_allowable_N") or 0.0
        lateral_load = support.get("lateral_load_N") or 0.0

        result = CalculationResult(
            component_id=tag,
            component_type="support",
            calculation_type="leg_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Appendix G",
            formula_reference="Leg Support",
        )

        mat = None
        for m in materials:
            if m.material_id == skirt_mat_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Skirt material '{skirt_mat_id}' not found.")
            return result

        if W_total <= 0:
            result.set_not_calculated("Total weight not specified.")
            return result

        if n_legs < 2:
            result.set_not_calculated(
                "At least 2 legs required (tek ayak devrilme analizi ayrı iş; bu sürümde kapsam dışı)."
            )
            return result

        # Kesit: leg_section_type None/pipe → mevcut boru davranışı (D, t); channel/box/angle →
        # serbest profil ölçülerinden gerçek kesit alanı (sections.py).
        section_type = support.get("leg_section_type")
        A_leg_profile = None
        if section_type in ("channel", "box", "angle"):
            geom, gmiss, gerr = leg_detail.build_leg_geometry(support)
            if gerr:
                result.set_not_calculated(gerr)
                return result
            if gmiss:
                result.set_not_calculated(
                    f"Leg profile dimensions missing ({section_type}): " + ", ".join(gmiss) + "."
                )
                return result
            A_leg_profile = geom.section.A
        elif D_leg <= 0 or t_leg <= 0:
            result.set_not_calculated(
                "Leg diameter and thickness must be provided and positive."
            )
            return result

        if M_overturn > 0 and support_radius <= 0:
            result.set_not_calculated(
                "Support radius must be provided for leg overturning-moment checks."
            )
            return result

        result.input_snapshot = {
            "tag": tag,
            "n_legs": n_legs,
            "D_leg_mm": D_leg,
            "t_leg_mm": t_leg,
            "W_total_N": W_total,
            "M_overturning_Nmm": M_overturn,
            "anchor_bolt_count": n_anchor,
            "lateral_load_N": lateral_load,
            "leg_section_type": section_type or "pipe (varsayılan, eski davranış)",
        }

        # §7.3: Simetrik ayak dağılımı — formüller supports/formulas.py'dedir (K1).
        r_dist = support_radius
        try:
            N_max, N_min = formulas.leg_reaction_extremes(
                W_total, n_legs, M_overturn, r_dist
            )
            # Yükselme (uplift) EN DÜŞÜK ağırlıkla değerlendirilir: N_max basma
            # (hidrotest) ağırlığıyla, N_min boş kap ağırlığıyla. Boş ağırlık
            # verilmemişse basma ağırlığı kullanılır ve bu, kaldırmayı olduğundan
            # az gösterir (emniyetsiz) — varsayım sonuca yazılır.
            W_min_in = input_data.get("min_weight_N")
            if W_min_in is not None and 0 < W_min_in < W_total:
                _, N_min = formulas.leg_reaction_extremes(
                    W_min_in, n_legs, M_overturn, r_dist
                )
                result.add_assumption(
                    f"Yükselme kontrolü boş kap ağırlığıyla ({W_min_in:.0f} N), basma "
                    f"kontrolü {W_total:.0f} N ile yapıldı."
                )
            else:
                result.add_assumption(
                    "K4: Boş (minimum) ağırlık verilmedi; yükselme basma ağırlığıyla "
                    "değerlendirildi — kaldırma olduğundan az görünebilir."
                )
            # Ayak ÇELİK gerilmesi daima ayak kesitinden hesaplanır. Ayak boru
            # kesitlidir (dış çap D_leg, et kalınlığı t_leg) — dolu daire DEĞİL,
            # halka kesit. Taban plakası alanı ayak çeliğini taşımaz: eskiden
            # `base_plate_area_mm2` verilince N_max/A_taban çelik izin gerilmesiyle
            # kıyaslanıyordu; büyük plaka girdikçe ayak "daha güvenli" görünüyordu
            # (emniyetsiz, B-33). Plaka alanı yalnız temel yataklık basıncına aittir.
            A_leg = (
                A_leg_profile if A_leg_profile is not None
                else formulas.leg_pipe_section_area(D_leg, t_leg)
            )
            P_base = formulas.leg_base_pressure(N_max, A_leg)
            P_bearing = formulas.leg_base_pressure(N_max, A_base) if A_base > 0 else None
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        S_allow = mat.allowable_stress

        result.add_intermediate("n_legs", n_legs, "-", "Number of legs")
        if A_leg_profile is None:
            result.add_intermediate("D_leg", D_leg, "mm", "Leg diameter")
            result.add_intermediate("t_leg", t_leg, "mm", "Leg thickness")
        else:
            result.add_intermediate("leg_section_type", section_type, "-", "Leg profile type (free dimensions)")
        result.add_intermediate("W_total", W_total, "N", "Total weight")
        result.add_intermediate("M_overturning", M_overturn, "N·mm", "Overturning moment")
        result.add_intermediate("r_dist", r_dist, "mm", "Distribution radius")
        result.add_intermediate("N_max", N_max, "N", "Maximum leg reaction")
        result.add_intermediate("N_min", N_min, "N", "Minimum leg reaction")
        result.add_intermediate("A_leg", A_leg, "mm²", "Leg cross-section (annulus)")
        result.add_intermediate("P_base", P_base, "MPa", "Leg axial stress N_max/A_leg")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")
        if P_bearing is not None:
            # Temel yataklık basıncı: izin verilen değer (beton/grout) girdisi yok →
            # kontrol EDİLMEZ; çelik S ile kıyaslanmaz (farklı büyüklük).
            result.add_intermediate("P_bearing", P_bearing, "MPa", "Foundation bearing N_max/A_base")
            result.add_warning(
                f"Taban plakası yataklık basıncı {P_bearing:.2f} MPa hesaplandı ancak temel "
                "(beton/grout) izin verilen basıncı girdisi olmadığından KONTROL EDİLMEDİ."
            )

        if support.get("anchor_bolt_diameter_mm"):
            result.add_warning(
                f"anchor_bolt_diameter_mm ({support['anchor_bolt_diameter_mm']:g} mm) girildi ancak hesapta "
                "KULLANILMADI: gerilme alanı diş adımına bağlıdır (girdi yok); ankraj kapasitesi kullanıcı "
                "girdisi izin verilen çekme/kesme kuvvetleriyle (N) değerlendirilir."
            )

        # Ankraj ve taban kesmesi: negatif reaksiyon, ankraj verilmeden PASS
        # sayılamaz. Bu kontrol basınç plakası gerilmesinden ayrı tutulur.
        uplift_per_leg = max(0.0, -N_min)
        anchor_tension_ratio = 0.0
        anchor_shear_ratio = 0.0
        anchor_review = False
        if uplift_per_leg > 0.0:
            if n_anchor <= 0 or anchor_tension_allowable <= 0.0:
                anchor_review = True
                result.add_warning(
                    "Negatif ayak reaksiyonu için ankraj cıvatası adedi ve izin verilen çekme kuvveti girilmedi."
                )
            else:
                tension_per_bolt = uplift_per_leg * n_legs / n_anchor
                anchor_tension_ratio = tension_per_bolt / anchor_tension_allowable
                result.add_intermediate("uplift_per_leg", uplift_per_leg, "N", "Uplift demand per leg")
                result.add_intermediate("anchor_tension_per_bolt", tension_per_bolt, "N", "Anchor tension demand")
                result.add_intermediate("anchor_tension_ratio", anchor_tension_ratio, "-", "Anchor tension utilization")

        if lateral_load > 0.0:
            if n_anchor <= 0 or anchor_shear_allowable <= 0.0:
                anchor_review = True
                result.add_warning(
                    "Yatay taban yükü için ankraj cıvatası adedi ve izin verilen kesme kuvveti girilmedi."
                )
            else:
                shear_per_bolt = lateral_load / n_anchor
                anchor_shear_ratio = shear_per_bolt / anchor_shear_allowable
                result.add_intermediate("anchor_shear_per_bolt", shear_per_bolt, "N", "Anchor shear demand")
                result.add_intermediate("anchor_shear_ratio", anchor_shear_ratio, "-", "Anchor shear utilization")

        anchor_ratio = max(anchor_tension_ratio, anchor_shear_ratio)

        # Basit gerilme kontrolü (basınç)
        utilization = P_base / S_allow if S_allow > 0 else float('inf')

        result.final_result = P_base
        result.final_result_unit = "MPa"
        result.allowable_limit = S_allow
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = utilization

        if N_min < 0:
            result.add_warning(
                "Bacak reaksiyonu negatif (kaldırma). "
                "Ankraj bağlantısı gerekli."
            )

        if P_base > S_allow or anchor_ratio > 1.0:
            result.set_fail(max(utilization, anchor_ratio))
            if anchor_ratio > 1.0:
                result.add_warning("Ankraj talebi izin verilen çekme/kesme kapasitesini aşıyor.")
            else:
                result.add_warning(
                    f"Leg base pressure {P_base:.2f} MPa exceeds allowable {S_allow:.2f} MPa."
                )
        elif anchor_review:
            result.set_review_required(
                "Destek ankrajı tamamlanmadan ayak sonucu nihai PASS olarak kullanılamaz."
            )
            result.utilization_ratio = max(utilization, anchor_ratio)
        else:
            result.set_review_required(
                "Simplified leg checks do not establish support layout, shell-local "
                "load transfer, or foundation capacity. Independent engineering "
                "review is required; this result is not a final PASS."
            )
            result.utilization_ratio = max(utilization, anchor_ratio)

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "source_reference": mat.source_reference,
        }

        return result


__all__ = ["SupportCalculator"]
