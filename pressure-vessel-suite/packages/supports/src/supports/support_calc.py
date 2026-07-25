"""SupportCalculator — saddle (Zick) ve skirt destek hesaplayıcı.

Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult
from supports import formulas


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
        """Saddle (Zick analizi) kontrolü.

        Args:
            input_data: {
                "support": {
                    "tag": str,
                    "type": "saddle",
                    "location_mm": float,
                    "width_mm": float,
                    "height_mm": float,
                },
                "shell": ShellSection,
                "vessel_length": float,      # mm
                "saddle_distance": float,     # saddle'lar arası mesafe (mm)
                "saddle_from_end": float,     # saddle'dan kap ucuna mesafe (mm)
                "total_weight_N": float,      # toplam ağırlık (N)
                "materials": List[MaterialProperty],
                "design_conditions": DesignConditions,
            }

        Returns:
            CalculationResult — PASS/FAIL/NOT_CALCULATED.
        """
        support = input_data["support"]
        shell = input_data["shell"]
        L = input_data.get("saddle_distance", input_data.get("vessel_length", shell.tangent_length))
        A = input_data.get("saddle_from_end", L * 0.2)
        W_total = input_data.get("total_weight_N", 0.0)
        materials = input_data.get("materials", [])
        dc = input_data.get("design_conditions")

        tag = support.get("tag", "SADDLE-01")
        b = support.get("width_mm", 200.0)
        h = support.get("height_mm", 0.0)

        result = CalculationResult(
            component_id=tag,
            component_type="support",
            calculation_type="saddle_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Zick Analysis",
            formula_reference="Zick (1951)",
        )

        # Malzeme
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

        # Gövde parametreleri
        if shell.inside_diameter:
            D_i = shell.inside_diameter
        else:
            D_i = shell.outside_diameter - 2 * shell.nominal_thickness

        R_m = D_i / 2.0 + shell.nominal_thickness / 2.0
        t = shell.nominal_thickness

        # Saddle reaksiyonu
        Q = formulas.saddle_reaction(W_total, n_saddles=2)

        result.input_snapshot = {
            "tag": tag,
            "D_i_mm": D_i,
            "R_m_mm": R_m,
            "t_mm": t,
            "L_mm": L,
            "A_mm": A,
            "b_mm": b,
            "h_mm": h,
            "W_total_N": W_total,
            "Q_N": Q,
        }

        # Zick gerilmeleri
        try:
            S1 = formulas.zick_longitudinal_bending(Q, L, R_m, t, A, h)
            S2 = formulas.zick_circumferential_saddle(Q, R_m, t, b)
            S3 = formulas.zick_circumferential_crown(Q, R_m, t, b, L)
            S4 = formulas.zick_shear_stress(Q, R_m, t, A, L)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        S_allow = mat.allowable_stress
        S1_lim, S2_lim, S3_lim, S4_lim = formulas.saddle_stress_limits(S_allow)

        # Ara değerler
        result.add_intermediate("Q", Q, "N", "Saddle reaction force")
        result.add_intermediate("R_m", R_m, "mm", "Mean radius")
        result.add_intermediate("t", t, "mm", "Shell thickness")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")
        result.add_intermediate("S1", S1, "MPa", "Longitudinal bending at saddle")
        result.add_intermediate("S1_limit", S1_lim, "MPa", "S1 limit (0.67×S_allow)")
        result.add_intermediate("S2", S2, "MPa", "Circumferential at saddle")
        result.add_intermediate("S2_limit", S2_lim, "MPa", "S2 limit")
        result.add_intermediate("S3", S3, "MPa", "Circumferential at crown")
        result.add_intermediate("S3_limit", S3_lim, "MPa", "S3 limit")
        result.add_intermediate("S4", S4, "MPa", "Shear stress")
        result.add_intermediate("S4_limit", S4_lim, "MPa", "S4 limit")

        # En kritik gerilme
        stresses = [
            ("S1", S1, S1_lim),
            ("S2", S2, S2_lim),
            ("S3", S3, S3_lim),
            ("S4", S4, S4_lim),
        ]

        max_ratio = 0.0
        critical_name = ""
        for name, s, lim in stresses:
            ratio = s / lim if lim > 0 else float('inf')
            if ratio > max_ratio:
                max_ratio = ratio
                critical_name = name

        result.final_result = max(S1, S2, S3, S4)
        result.final_result_unit = "MPa"
        result.allowable_limit = S1_lim  # hepsi aynı limit
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = max_ratio

        failures = []
        for name, s, lim in stresses:
            if s > lim:
                failures.append(f"{name}={s:.2f} > limit={lim:.2f}")

        if failures:
            result.set_fail(max_ratio)
            result.add_warning(f"Saddle stress check failed: {'; '.join(failures)}")
        else:
            result.set_pass(max_ratio)

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "source_reference": mat.source_reference,
        }

        return result

    def check_skirt(self, input_data: dict) -> CalculationResult:
        """Skirt (etek destek) kontrolü.

        Args:
            input_data: {
                "support": {
                    "tag": str,
                    "type": "skirt",
                    "diameter_mm": float,
                    "thickness_mm": float,
                    "height_mm": float,
                },
                "total_weight_N": float,
                "overturning_moment_Nmm": float,
                "materials": List[MaterialProperty],
                "design_conditions": DesignConditions,
                "skirt_material_id": str,
            }
        """
        support = input_data["support"]
        W_total = input_data.get("total_weight_N", 0.0)
        M_overturn = input_data.get("overturning_moment_Nmm", 0.0)
        materials = input_data.get("materials", [])
        skirt_mat_id = input_data.get("skirt_material_id", "")

        tag = support.get("tag", "SKIRT-01")
        D_skirt = support.get("diameter_mm", 0.0)
        t_skirt = support.get("thickness_mm", 0.0)

        result = CalculationResult(
            component_id=tag,
            component_type="support",
            calculation_type="skirt_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Appendix G",
            formula_reference="Skirt Foundation",
        )

        # Malzeme
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

        result.input_snapshot = {
            "tag": tag,
            "D_skirt_mm": D_skirt,
            "t_skirt_mm": t_skirt,
            "W_total_N": W_total,
            "M_overturning_Nmm": M_overturn,
        }

        try:
            S_bend = formulas.skirt_bending_stress(M_overturn, D_skirt, t_skirt)
            S_comp = formulas.skirt_compression_stress(W_total, D_skirt, t_skirt)
            S_comb = formulas.skirt_combined_stress(S_bend, S_comp)
            P_base = formulas.skirt_base_pressure(W_total, M_overturn, D_skirt, t_skirt)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        S_allow = mat.allowable_stress

        result.add_intermediate("D_skirt", D_skirt, "mm", "Skirt diameter")
        result.add_intermediate("t_skirt", t_skirt, "mm", "Skirt thickness")
        result.add_intermediate("W_total", W_total, "N", "Total weight")
        result.add_intermediate("M_overturning", M_overturn, "N·mm", "Overturning moment")
        result.add_intermediate("S_bending", S_bend, "MPa", "Bending stress")
        result.add_intermediate("S_compression", S_comp, "MPa", "Compression stress")
        result.add_intermediate("S_combined", S_comb, "MPa", "Combined stress")
        result.add_intermediate("P_base", P_base, "MPa", "Base pressure")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")

        utilization = S_comb / S_allow if S_allow > 0 else float('inf')

        result.final_result = S_comb
        result.final_result_unit = "MPa"
        result.allowable_limit = S_allow
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = utilization

        if S_comb <= S_allow:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Skirt combined stress {S_comb:.2f} MPa exceeds "
                f"allowable {S_allow:.2f} MPa."
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "source_reference": mat.source_reference,
        }

        return result

    def check_leg_support(self, input_data: dict) -> CalculationResult:
        """Ayak (leg) destek kontrolü.

        §7.3: Simetrik ayak dağılımı formülü:
        N_i = W/n + Mx·y_i/Σy² + My·x_i/Σx²

        Args:
            input_data: {
                "support": {
                    "tag": str,
                    "type": "leg",
                    "n_legs": int,
                    "leg_diameter_mm": float,
                    "leg_thickness_mm": float,
                    "base_plate_area_mm2": float,
                },
                "total_weight_N": float,
                "overturning_moment_Nmm": float,
                "moment_direction": str,  # "x" veya "y"
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
        n_legs = support.get("n_legs", 4)
        D_leg = support.get("leg_diameter_mm", 100.0)
        t_leg = support.get("leg_thickness_mm", 10.0)
        A_base = support.get("base_plate_area_mm2", 0.0)

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
            result.set_not_calculated("At least 2 legs required.")
            return result

        result.input_snapshot = {
            "tag": tag,
            "n_legs": n_legs,
            "D_leg_mm": D_leg,
            "t_leg_mm": t_leg,
            "W_total_N": W_total,
            "M_overturning_Nmm": M_overturn,
        }

        # §7.3: Simetrik ayak dağılımı
        # N_i = W/n + Mx·y_i/Σy² (moment x ekseni etrafında ise)
        # Basitleştirilmiş: maksimum reaksiyon
        # Maksimum reaksiyon = W/n + M/(n·r) burada r = D/2 (dağılım yarıçapı)
        r_dist = D_leg * n_legs / (2 * 3.14159)  # Yaklaşık dağılım yarıçapı
        if r_dist > 0 and M_overturn > 0:
            N_max = W_total / n_legs + M_overturn / (n_legs * r_dist)
        else:
            N_max = W_total / n_legs

        N_min = W_total / n_legs - (M_overturn / (n_legs * r_dist) if r_dist > 0 else 0)

        # Basınç kontrolü
        if A_base > 0:
            P_base = N_max / A_base
        else:
            # Dairesel ayak tabanı
            A_leg = 3.14159 * (D_leg / 2) ** 2
            P_base = N_max / A_leg

        S_allow = mat.allowable_stress

        result.add_intermediate("n_legs", n_legs, "-", "Number of legs")
        result.add_intermediate("D_leg", D_leg, "mm", "Leg diameter")
        result.add_intermediate("t_leg", t_leg, "mm", "Leg thickness")
        result.add_intermediate("W_total", W_total, "N", "Total weight")
        result.add_intermediate("M_overturning", M_overturn, "N·mm", "Overturning moment")
        result.add_intermediate("r_dist", r_dist, "mm", "Distribution radius")
        result.add_intermediate("N_max", N_max, "N", "Maximum leg reaction")
        result.add_intermediate("N_min", N_min, "N", "Minimum leg reaction")
        result.add_intermediate("P_base", P_base, "MPa", "Base pressure")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")

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

        if P_base <= S_allow:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Leg base pressure {P_base:.2f} MPa exceeds "
                f"allowable {S_allow:.2f} MPa."
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "source_reference": mat.source_reference,
        }

        return result


__all__ = ["SupportCalculator"]
