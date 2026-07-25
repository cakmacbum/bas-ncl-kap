"""MDMTCalculator — MDMT (Minimum Design Metal Temperature) hesaplayıcı.

ASME VIII-1 UCS-66 mantığı:
- Malzeme eğri grubu (A, B, C, D)
- Muafiyet kontrolü (UCS-66.1)
- Sıcaklık indirimi hesapları

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult


class UCS66CurveGroup(str, Enum):
    """UCS-66 malzeme eğri grupları."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# UCS-66 Tablo UCS-66.1 — Eğri grubuna göre MDMT limitleri (°C)
# Basitleştirilmiş: gerçekte kalınlığa göre değişir
UCS66_MDMT_LIMITS = {
    UCS66CurveGroup.A: -29.0,
    UCS66CurveGroup.B: -29.0,
    UCS66CurveGroup.C: -46.0,
    UCS66CurveGroup.D: -46.0,
}


class MDMTCalculator:
    """MDMT hesaplayıcı.

    ASME VIII-1 UCS-66 mantığıyla malzeme eğri grubu ve MDMT kontrolü yapar.

    Kullanım:
        calc = MDMTCalculator()
        result = calc.check_mdmt(input_data)
    """

    def __init__(self, code: str = "ASME VIII-1", edition: str = "2025"):
        self._code = code
        self._edition = edition

    def check_mdmt(self, input_data: dict) -> CalculationResult:
        """MDMT kontrolü — UCS-66.

        Args:
            input_data: {
                "component": ShellSection | Head,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "curve_group": UCS66CurveGroup,  # A, B, C, D
                "nominal_thickness_mm": float,
                "impact_test_temperature_C": float,  # opsiyonel
            }

        Returns:
            CalculationResult — PASS/FAIL/NOT_CALCULATED.
        """
        component = input_data.get("component")
        dc = input_data.get("design_conditions")
        materials = input_data.get("materials", [])
        curve_group = input_data.get("curve_group")
        t_nominal = input_data.get("nominal_thickness_mm", 0.0)
        impact_test_temp = input_data.get("impact_test_temperature_C")

        comp_id = ""
        if component:
            comp_id = getattr(component, "section_id", None) or getattr(component, "head_id", "")

        result = CalculationResult(
            component_id=comp_id,
            component_type="system",
            calculation_type="mdmt_check",
            code=self._code,
            edition=self._edition,
            clause_reference="UCS-66",
            formula_reference="UCS-66(a)",
        )

        if dc is None:
            result.set_not_calculated("Design conditions not provided.")
            return result

        if curve_group is None:
            result.set_blocked_missing_input(
                "UCS-66 eğri grubu belirtilmemiş. "
                "Malzeme standardına göre eğri grubu (A/B/C/D) girilmeli."
            )
            return result

        if t_nominal <= 0:
            result.set_not_calculated("Nominal thickness not specified or zero.")
            return result

        # Malzeme
        mat = None
        if component and materials:
            mat_id = getattr(component, "material_id", "")
            for m in materials:
                if m.material_id == mat_id:
                    mat = m
                    break

        result.input_snapshot = {
            "curve_group": curve_group.value,
            "nominal_thickness_mm": t_nominal,
            "minimum_design_temperature_C": dc.minimum_design_temperature,
            "impact_test_temperature_C": impact_test_temp,
        }

        # UCS-66 Tablo UCS-66.1 — Eğri grubuna göre MDMT limiti
        mdmt_limit = UCS66_MDMT_LIMITS.get(curve_group, -29.0)

        # Kalınlık düzeltmesi (basitleştirilmiş)
        # Gerçek hesapta Tablo UCS-66.1'den kalınlığa göre okunur
        if t_nominal > 38.0:
            # Kalın malzeme → daha yüksek MDMT
            thickness_penalty = (t_nominal - 38.0) * 0.5
            mdmt_limit = mdmt_limit + thickness_penalty

        result.add_intermediate("curve_group", curve_group.value, "-", "UCS-66 curve group")
        result.add_intermediate("t_nominal", t_nominal, "mm", "Nominal thickness")
        result.add_intermediate("mdmt_limit", mdmt_limit, "°C", "MDMT limit from UCS-66 Table")
        result.add_intermediate(
            "minimum_design_temperature", dc.minimum_design_temperature, "°C",
            "Minimum design temperature"
        )

        # MDMT kontrolü
        if dc.minimum_design_temperature >= mdmt_limit:
            # MDMT limiti aşılmadı → muafiyet yok, test gerekli
            result.add_warning(
                f"Minimum design temperature ({dc.minimum_design_temperature}°C) "
                f">= MDMT limit ({mdmt_limit}°C). Charpy V-notch impact testi gerekli."
            )

            # Impact test sıcaklığı kontrolü
            if impact_test_temp is not None:
                result.add_intermediate(
                    "impact_test_temperature", impact_test_temp, "°C",
                    "Impact test temperature"
                )
                if impact_test_temp <= dc.minimum_design_temperature:
                    result.set_pass()
                    result.add_assumption(
                        f"K4: Impact test at {impact_test_temp}°C covers "
                        f"minimum design temperature {dc.minimum_design_temperature}°C."
                    )
                else:
                    result.set_fail()
                    result.add_warning(
                        f"Impact test temperature ({impact_test_temp}°C) > "
                        f"minimum design temperature ({dc.minimum_design_temperature}°C). "
                        "Test does not cover design conditions."
                    )
            else:
                result.set_review_required(
                    "Impact test temperature not specified. "
                    "Charpy V-notch test required per UCS-66."
                )
        else:
            # MDMT limiti altında → muafiyet
            result.set_pass()
            result.add_assumption(
                f"K4: Minimum design temperature ({dc.minimum_design_temperature}°C) "
                f"< MDMT limit ({mdmt_limit}°C). Impact test exemption per UCS-66(a)."
            )

        result.final_result = mdmt_limit
        result.final_result_unit = "°C"

        if mat:
            result.material_properties_used = {
                "designation": mat.material_designation,
                "allowable_stress": mat.allowable_stress,
                "source_reference": mat.source_reference,
            }

        return result


__all__ = ["MDMTCalculator", "UCS66CurveGroup", "UCS66_MDMT_LIMITS"]
