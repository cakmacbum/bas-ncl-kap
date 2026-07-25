"""FlangeCalculator — flanş hesaplayıcı (ASME VIII-1 Appendix 2 mantığı).

Moment, gerilme kontrolleri ve flanş boyutlandırma.
Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult
from flanges import formulas


class FlangeCalculator:
    """Flanş hesaplayıcı.

    ASME VIII-1 Appendix 2 mantığıyla flanş moment ve gerilme hesapları yapar.

    Kullanım:
        calc = FlangeCalculator()
        result = calc.check_flange_stress(input_data)
    """

    def __init__(self, code: str = "ASME VIII-1", edition: str = "2025"):
        self._code = code
        self._edition = edition

    def check_flange_stress(self, input_data: dict) -> CalculationResult:
        """Flanş gerilme kontrolü.

        Args:
            input_data: {
                "flange": {
                    "tag": str,
                    "type": "integral" | "loose",
                    "B": float,          # İç çap (mm)
                    "A": float,          # Dış çap (mm)
                    "t": float,          # Flanş kalınlığı (mm)
                    "g0": float,         # Hub kalınlığı (large end, mm)
                    "g1": float,         # Hub kalınlığı (small end, mm)
                    "h0": float,         # Hub uzunluğu (mm)
                    "material_id": str,
                },
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "bolt_load_W": float,   # Cıvata yükü (N)
                "moment_M": float,      # Moment (N·mm)
                "flange_factor_Y": float,  # Y faktörü (tablo)
                "flange_factor_f": float,  # Hub correction factor
            }

        Returns:
            CalculationResult — PASS/FAIL/NOT_CALCULATED.
        """
        flange = input_data["flange"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        W = input_data.get("bolt_load_W", 0.0)
        M = input_data.get("moment_M", 0.0)
        Y = input_data.get("flange_factor_Y", 5.0)  # Varsayılan değer
        f = input_data.get("flange_factor_f", 1.0)

        tag = flange.get("tag", "FLANGE-01")

        result = CalculationResult(
            component_id=tag,
            component_type="flange",
            calculation_type="flange_stress",
            code=self._code,
            edition=self._edition,
            clause_reference="Appendix 2",
            formula_reference="Appendix 2-7",
        )

        # Malzeme
        mat_id = flange.get("material_id", "")
        mat = None
        for m in materials:
            if m.material_id == mat_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(
                f"Flange material '{mat_id}' not found. "
                "Flange stress calculation requires material properties."
            )
            return result

        B = flange["B"]
        t = flange["t"]
        g1 = flange.get("g1", flange.get("g0", t))
        h0 = flange.get("h0", g1 * 2.0)
        flange_type = flange.get("type", "integral")

        # Girdi anlık görüntüsü
        result.input_snapshot = {
            "flange_tag": tag,
            "flange_type": flange_type,
            "B_mm": B,
            "t_mm": t,
            "g1_mm": g1,
            "h0_mm": h0,
            "bolt_load_W_N": W,
            "moment_M_Nmm": M,
            "Y_factor": Y,
            "f_factor": f,
            "P_design_MPa": dc.design_pressure,
            "material": mat.material_designation,
        }

        S_allow = mat.allowable_stress

        result.add_assumption(
            f"K4: Allowable stress S={S_allow} MPa from "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        # Gerilme hesapları
        try:
            S_H = formulas.hub_longitudinal_stress(M, f, g1, h0)
            S_R = formulas.radial_flange_stress(M, B, t, h0)
            S_T = formulas.tangential_flange_stress(M, Y, t, B)
            S_avg = formulas.average_flange_stress(S_R, S_T)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Ara değerler
        result.add_intermediate("B", B, "mm", "Flange bore (inside diameter)")
        result.add_intermediate("t", t, "mm", "Flange thickness")
        result.add_intermediate("g1", g1, "mm", "Hub thickness at small end")
        result.add_intermediate("h0", h0, "mm", "Hub length")
        result.add_intermediate("W", W, "N", "Bolt load")
        result.add_intermediate("M", M, "N·mm", "Flange moment")
        result.add_intermediate("S_allow", S_allow, "MPa", "Allowable stress")
        result.add_intermediate("S_H", S_H, "MPa", "Longitudinal hub stress")
        result.add_intermediate("S_R", S_R, "MPa", "Radial flange stress")
        result.add_intermediate("S_T", S_T, "MPa", "Tangential flange stress")
        result.add_intermediate("S_avg", S_avg, "MPa", "Average flange stress")
        result.add_intermediate("1.5×S_allow", 1.5 * S_allow, "MPa", "Hub stress limit")

        # Gerilme kontrolü
        passed, check_msg = formulas.flange_stress_check(S_H, S_R, S_T, S_avg, S_allow)

        # En kritik gerilme oranını bul
        ratios = [
            S_H / (1.5 * S_allow) if S_allow > 0 else float('inf'),
            S_R / S_allow if S_allow > 0 else float('inf'),
            S_avg / S_allow if S_allow > 0 else float('inf'),
        ]
        max_ratio = max(ratios)

        result.final_result = S_H
        result.final_result_unit = "MPa"
        result.allowable_limit = 1.5 * S_allow
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = max_ratio

        if passed:
            result.set_pass(max_ratio)
        else:
            result.set_fail(max_ratio)
            result.add_warning(f"Flange stress check failed: {check_msg}")

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_allow,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_moment_from_pressure(
        self,
        input_data: dict,
    ) -> Dict[str, float]:
        """Basınçtan moment hesapla (Appendix 2-5/2-6).

        Args:
            input_data: {
                "P": float,          # Tasarım basıncı (MPa)
                "G": float,          # Gasket reaction diameter (mm)
                "B": float,          # Flanş iç çapı (mm)
                "h_D": float,        # H_D moment kolu (mm)
                "h_G": float,        # H_G moment kolu (mm)
                "h_T": float,        # H_T moment kolu (mm)
                "H_p": float,        # Gasket sıkma kuvveti (N)
            }

        Returns:
            {"H": float, "H_D": float, "H_G": float, "H_T": float, "W": float, "M": float}
        """
        P = input_data["P"]
        G = input_data["G"]
        B = input_data["B"]
        h_D = input_data.get("h_D", 0.0)
        h_G = input_data.get("h_G", 0.0)
        h_T = input_data.get("h_T", 0.0)
        H_p = input_data.get("H_p", 0.0)

        H = formulas.hydrostatic_end_force(P, G)
        H_D = math.pi / 4.0 * B * B * P
        H_G = H_p
        H_T = H - H_D

        W = formulas.bolt_load_operating(H, H_p)
        M = formulas.flange_moment(H_D, h_D, H_G, h_G, H_T, h_T)

        return {
            "H": H,
            "H_D": H_D,
            "H_G": H_G,
            "H_T": H_T,
            "W": W,
            "M": M,
        }


import math  # noqa: E402 (math.pi kullanımı)

__all__ = ["FlangeCalculator"]
