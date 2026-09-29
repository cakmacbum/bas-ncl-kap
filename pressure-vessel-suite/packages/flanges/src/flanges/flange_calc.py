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
                    "g0": float,         # Hub kalınlığı (küçük uç, mm)
                    "g1": float,         # Hub kalınlığı (büyük uç / flanş sırtı, mm)
                    "h": float,          # Hub uzunluğu (mm; yalnız bilgi)
                    "material_id": str,
                },
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "bolt_load_W": float,   # Cıvata yükü (N)
                "moment_M": float,      # Moment (N·mm)
                "flange_factor_Y": float,  # Y faktörü (tablo)
                "flange_factor_f": float,  # Hub correction factor
                "flange_factor_F/V/T/U": float,  # Şekil 2-7.1 faktörleri (kullanıcı)
            }

        Returns:
            CalculationResult — PASS/FAIL/NOT_CALCULATED.
        """
        flange = input_data["flange"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        W = input_data.get("bolt_load_W")
        M = input_data.get("moment_M")
        # Y, Appendix 2 Şekil 2-7.1'den K = A/B oranına göre okunur ve geniş bir
        # aralıkta değişir. Eskiden sessizce 5.0 varsayılıyordu; bu modül hesap
        # hattına bağlandığı gün sessizce yanlış sonuç üretirdi. K4: varsayılan yok.
        Y = input_data.get("flange_factor_Y")
        f = input_data.get("flange_factor_f")
        # F, V, T, U: Şekil 2-7.1 faktörleri — kullanıcı girdisi (K6), varsayılan yok (K4).
        F = input_data.get("flange_factor_F")
        V = input_data.get("flange_factor_V")
        T_ = input_data.get("flange_factor_T")
        U = input_data.get("flange_factor_U")

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

        flange_type = flange.get("type", "integral")
        if flange_type != "integral":
            result.set_out_of_scope(
                f"Flanş tipi '{flange_type}': bu modül yalnız integral-hub flanş "
                "gerilme formüllerini (Appendix 2-7: S_H, S_R, S_T; L, Z, e, d) uygular. "
                "Gevşek (loose) flanşlar için Appendix 2-7 farklı formüller kullanır "
                "(ör. S_H hesaplanmaz, L/Z/K ve halka faktörleri farklıdır); integral "
                "formüllerle hesaplamak sessizce yanlış sonuç üretirdi — hesap yapılmadı."
            )
            return result

        # K6/K4: Şekil 2-7.1 faktörleri ve g1 kullanıcı girdisidir; eksik olanlar adıyla listelenir.
        A = flange.get("A")
        g0 = flange.get("g0")
        g1 = flange.get("g1")
        factors = {"Y": Y, "f": f, "F": F, "V": V, "T": T_, "U": U}
        missing = [k for k, v in factors.items() if v is None or v <= 0]
        if g1 is None or g1 <= 0:
            missing.append("g1 (hub büyük uç kalınlığı, hub_large_thickness)")
        if A is None or A <= 0:
            missing.append("A (flanş dış çapı)")
        if missing:
            result.set_blocked_missing_input(
                "Appendix 2-7 gerilme hesabı için eksik girdi: " + ", ".join(missing) + ". "
                "Y, f, F, V, T, U Şekil 2-7.1 eğrilerinden (K = A/B ve g1/g0, h/h0 "
                "oranlarına göre) kullanıcı tarafından okunur; lisanslı eğri verisi koda "
                "gömülmez, interpolasyon yapılmaz ve varsayılan atanmaz (K4/K6)."
            )
            return result

        if M is None or W is None or M <= 0 or W <= 0:
            result.set_blocked_missing_input(
                "Flanş momenti M ve cıvata yükü W hesaplanmamış/girilmemiş "
                "(Appendix 2-5/2-6: conta çapı G, moment kolları h_D/h_G/h_T ve conta "
                "sıkma yükü gerekir). M = 0 ile gerilme sıfır çıkar ve sahte PASS "
                "üretir — bu yüzden hesap yapılmaz (K4)."
            )
            return result

        B = flange["B"]
        t = flange["t"]
        h = flange.get("h")

        # Girdi anlık görüntüsü
        result.input_snapshot = {
            "flange_tag": tag,
            "flange_type": flange_type,
            "A_mm": A,
            "B_mm": B,
            "t_mm": t,
            "g0_mm": g0,
            "g1_mm": g1,
            "h_mm": h,
            "bolt_load_W_N": W,
            "moment_M_Nmm": M,
            "Y_factor": Y,
            "f_factor": f,
            "F_factor": F,
            "V_factor": V,
            "T_factor": T_,
            "U_factor": U,
            "P_design_MPa": dc.design_pressure,
            "material": mat.material_designation,
        }

        S_f = mat.allowable_stress

        result.add_assumption(
            f"K4: Allowable stress S_f={S_f} MPa from "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )
        result.add_assumption(
            "Şekil 2-7.1 faktörleri (Y, f, F, V, T, U) kullanıcı girdisidir (K6); "
            "g0 = hub küçük uç kalınlığı, g1 = hub büyük uç kalınlığı."
        )

        # Şekil parametreleri ve gerilmeler
        try:
            sp = formulas.flange_shape_parameters(A, B, t, g0, F, V, T_, U)
            S_H = formulas.hub_longitudinal_stress(M, f, sp["L"], g1, B)
            S_R = formulas.radial_flange_stress(M, sp["L"], t, sp["e"], B)
            S_T = formulas.tangential_flange_stress(M, Y, t, B, sp["Z"], S_R)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        checks = formulas.flange_stress_checks(S_H, S_R, S_T, S_f)

        # Ara değerler (K5)
        result.add_intermediate("A", A, "mm", "Flange outside diameter")
        result.add_intermediate("B", B, "mm", "Flange bore (inside diameter)")
        result.add_intermediate("t", t, "mm", "Flange thickness")
        result.add_intermediate("g0", g0, "mm", "Hub thickness at small end")
        result.add_intermediate("g1", g1, "mm", "Hub thickness at large end")
        result.add_intermediate("K", sp["K"], "", "K = A/B")
        result.add_intermediate("Z", sp["Z"], "", "Z = (K²+1)/(K²−1)")
        result.add_intermediate("h0", sp["h0"], "mm", "h0 = √(B·g0)")
        result.add_intermediate("e", sp["e"], "1/mm", "e = F/h0")
        result.add_intermediate("d", sp["d"], "mm³", "d = (U/V)·h0·g0²")
        result.add_intermediate("L", sp["L"], "", "L = (t·e+1)/T + t³/d")
        result.add_intermediate("W", W, "N", "Bolt load (user input)")
        result.add_intermediate("M", M, "N·mm", "Flange moment (user input)")
        result.add_intermediate("S_f", S_f, "MPa", "Allowable stress at design temperature")
        result.add_intermediate("S_H", S_H, "MPa", "Longitudinal hub stress f·M/(L·g1²·B)")
        result.add_intermediate("S_R", S_R, "MPa", "Radial flange stress (1.33·t·e+1)·M/(L·t²·B)")
        result.add_intermediate("S_T", S_T, "MPa", "Tangential flange stress Y·M/(t²·B) − Z·S_R")
        result.add_intermediate("(S_H+S_R)/2", (S_H + S_R) / 2.0, "MPa", "Combined stress S_H/S_R")
        result.add_intermediate("(S_H+S_T)/2", (S_H + S_T) / 2.0, "MPa", "Combined stress S_H/S_T")
        result.add_intermediate("1.5×S_f", 1.5 * S_f, "MPa", "S_H limit (2.5·S_n not applied)")

        violations = [f"{n}={v:.2f} > {lim:.2f}" for n, v, lim in checks if v > lim]
        ratios = [(v / lim if lim > 0 else float("inf")) for _, v, lim in checks]
        max_ratio = max(ratios)

        result.final_result = S_H
        result.final_result_unit = "MPa"
        result.allowable_limit = 1.5 * S_f
        result.allowable_limit_unit = "MPa"
        result.utilization_ratio = max_ratio

        if not violations:
            # W ve M kullanıcı girdisidir; rijitlik/conta/cıvata kontrolleri yapılmaz →
            # nihai PASS verilmez.
            result.set_review_required()
            result.add_warning(
                "W ve M kullanıcı girdisidir (Appendix 2 çalışma sayfası); program "
                "bu değerleri doğrulamaz. Yapılan: integral flanş için S_H ≤ 1.5·S_f, "
                "S_R ≤ S_f, S_T ≤ S_f, (S_H+S_R)/2 ≤ S_f ve (S_H+S_T)/2 ≤ S_f kontrolleri "
                "(Y, f, F, V, T, U kullanıcı girdisi). Yapılmadı: S_H için 2.5·S_n sınırı "
                "(nozul/kabuk gerilmesi S_n girdisi yok; yalnız 1.5·S_f uygulandı), "
                "flanş rijitlik (Appendix 2-14), conta yerleşme/işletme (Wm1/Wm2) ve cıvata "
                "alanı kontrolleri; sızdırmazlık/oturma (S_fo) durumu için ayrı gerilme "
                "kontrolü. Nihai onay için tam Appendix 2 çalışma sayfası gerekir."
            )
        else:
            result.set_fail(max_ratio)
            result.add_warning("Flange stress check failed: " + "; ".join(violations))

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S_f,
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
