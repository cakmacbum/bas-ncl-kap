"""ExternalPressureCalculator — dış basınç ve vakum stabilite kontrolü.

ASME VIII-1 UG-28 mantığı. Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K5 kuralı: Her hesap denetlenebilir (CalculationResult).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult
from external_pressure import formulas


class ExternalPressureCalculator:
    """Dış basınç stabilite hesaplayıcı.

    ASME VIII-1 UG-28 mantığıyla silindirik gövde ve bombeler için
    dış basınç/buckling kontrolü yapar.

    Not: A ve B faktörleri UG-28 grafiklerinden okunmalıdır.
    Bu modül grafik okuma yapmaz; A ve B değerlerini girdi olarak alır.

    Kullanım:
        calc = ExternalPressureCalculator()
        result = calc.check_shell_external_pressure(input_data)
    """

    def __init__(self, code: str = "ASME VIII-1", edition: str = "2025"):
        self._code = code
        self._edition = edition

    def check_shell_external_pressure(self, input_data: dict) -> CalculationResult:
        """Silindirik gövde dış basınç stabilite kontrolü.

        Args:
            input_data: {
                "shell": ShellSection,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "strain_factor_A": float,  # UG-28 grafikten okunan
                "allowable_stress_B": float,  # Malzeme grafikten okunan
                "unstiffened_length": float, mm (destekler arası)
            }

        Returns:
            CalculationResult — PASS/FAIL/NOT_CALCULATED.
        """
        shell = input_data["shell"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        A = input_data.get("strain_factor_A", 0.0)
        B = input_data.get("allowable_stress_B", 0.0)
        L = input_data.get("unstiffened_length", shell.tangent_length)

        result = CalculationResult(
            component_id=shell.section_id,
            component_type="shell",
            calculation_type="external_pressure",
            code=self._code,
            edition=self._edition,
            clause_reference="UG-28",
            formula_reference="UG-28(a)",
        )

        # Malzeme kontrolü
        mat = None
        for m in materials:
            if m.material_id == shell.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(
                f"Material '{shell.material_id}' not found. "
                "External pressure calculation requires material properties."
            )
            return result

        P_ext = dc.external_pressure
        if P_ext <= 0:
            result.set_not_calculated(
                "No external pressure specified. External pressure check skipped."
            )
            return result

        # A/B faktör kontrolü
        if A <= 0 or B <= 0:
            result.set_not_calculated(
                "Strain factor A and allowable stress B must be provided from "
                "UG-28 charts. Manual entry required."
            )
            result.add_assumption(
                "K4: A (strain factor) and B (allowable compressive stress) "
                "must be entered manually from ASME UG-28 charts."
            )
            return result

        # Dış çap
        if shell.outside_diameter:
            D = shell.outside_diameter
        else:
            D = shell.inside_diameter + 2 * shell.nominal_thickness

        t = shell.nominal_thickness

        # Girdi anlık görüntüsü
        result.input_snapshot = {
            "D_mm": D,
            "L_mm": L,
            "t_mm": t,
            "P_external_MPa": P_ext,
            "A_strain_factor": A,
            "B_allowable_stress_MPa": B,
            "material": mat.material_designation,
        }

        result.add_assumption(
            f"K4: A={A}, B={B} MPa entered manually from UG-28 charts for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            P_allow, detail = formulas.shell_external_pressure_allowable(
                D=D, L=L, t=t, A=A, B=B, P_external=P_ext,
            )
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Ara değerler
        result.add_intermediate("D", D, "mm", "Outside diameter")
        result.add_intermediate("L", L, "mm", "Unstiffened length")
        result.add_intermediate("t", t, "mm", "Nominal thickness")
        result.add_intermediate("L/D", detail.L_over_D, "-", "Length-to-diameter ratio")
        result.add_intermediate("D/t", detail.D_over_t, "-", "Diameter-to-thickness ratio")
        result.add_intermediate("A", A, "-", "Strain factor (from UG-28 chart)")
        result.add_intermediate("B", B, "MPa", "Allowable compressive stress")
        result.add_intermediate("P_allow", P_allow, "MPa", "Allowable external pressure")
        result.add_intermediate("P_external", P_ext, "MPa", "Applied external pressure")

        # Sonuç
        result.final_result = P_allow
        result.final_result_unit = "MPa"
        result.allowable_limit = P_ext
        result.allowable_limit_unit = "MPa"

        utilization = P_ext / P_allow if P_allow > 0 else float('inf')
        result.utilization_ratio = utilization

        if P_ext <= P_allow:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"External pressure {P_ext:.4f} MPa exceeds allowable "
                f"{P_allow:.4f} MPa. Increase thickness or reduce span."
            )

        # Malzeme bilgisi
        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress_design": mat.allowable_stress,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "source_reference": mat.source_reference,
        }

        return result

    def check_head_external_pressure(self, input_data: dict) -> CalculationResult:
        """Bombe dış basınç stabilite kontrolü.

        Args:
            input_data: {
                "head": Head,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "strain_factor_A": float,
                "allowable_stress_B": float,
            }
        """
        head = input_data["head"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        A = input_data.get("strain_factor_A", 0.0)
        B = input_data.get("allowable_stress_B", 0.0)

        result = CalculationResult(
            component_id=head.head_id,
            component_type="head",
            calculation_type="external_pressure",
            code=self._code,
            edition=self._edition,
            clause_reference="UG-33",
            formula_reference="UG-33",
        )

        mat = None
        for m in materials:
            if m.material_id == head.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Material '{head.material_id}' not found")
            return result

        P_ext = dc.external_pressure
        if P_ext <= 0:
            result.set_not_calculated("No external pressure specified.")
            return result

        if A <= 0 or B <= 0:
            result.set_not_calculated(
                "Strain factor A and allowable stress B must be provided from "
                "UG-33 charts. Manual entry required."
            )
            return result

        D = head.inside_diameter
        t = head.nominal_thickness

        result.input_snapshot = {
            "D_mm": D,
            "t_mm": t,
            "P_external_MPa": P_ext,
            "A": A,
            "B_MPa": B,
            "head_type": head.type.value,
        }

        result.add_assumption(
            f"K4: A={A}, B={B} MPa entered manually from UG-33 charts for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            P_allow, detail = formulas.head_external_pressure_allowable(
                D=D, t=t, A=A, B=B,
            )
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        result.add_intermediate("D", D, "mm", "Inside diameter")
        result.add_intermediate("t", t, "mm", "Nominal thickness")
        result.add_intermediate("D/t", detail.D_over_t, "-", "Diameter-to-thickness ratio")
        result.add_intermediate("A", A, "-", "Strain factor")
        result.add_intermediate("B", B, "MPa", "Allowable compressive stress")
        result.add_intermediate("P_allow", P_allow, "MPa", "Allowable external pressure")

        result.final_result = P_allow
        result.final_result_unit = "MPa"
        result.allowable_limit = P_ext
        result.allowable_limit_unit = "MPa"

        utilization = P_ext / P_allow if P_allow > 0 else float('inf')
        result.utilization_ratio = utilization

        if P_ext <= P_allow:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"External pressure {P_ext:.4f} MPa exceeds allowable "
                f"{P_allow:.4f} MPa for head."
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress_design": mat.allowable_stress,
            "source_reference": mat.source_reference,
        }

        return result

    def check_vacuum_stability(self, input_data: dict) -> CalculationResult:
        """Vakum stabilite kontrolü (tam vakum = ~0.101 MPa dış basınç).

        Args:
            input_data: {
                "shell": ShellSection,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "strain_factor_A": float,
                "allowable_stress_B": float,
                "unstiffened_length": float,
            }
        """
        dc = input_data["design_conditions"]

        if not dc.vacuum_condition:
            result = CalculationResult(
                component_type="system",
                calculation_type="vacuum_stability",
                code=self._code,
                edition=self._edition,
            )
            result.set_not_calculated("No vacuum condition specified.")
            return result

        # Vakum = 0.101 MPa dış basınç (deniz seviyesi)
        vacuum_pressure = 0.101325  # MPa

        # Orijinal dc'yi bozmadan kopyala
        modified_input = dict(input_data)
        from domain.conditions import DesignConditions
        modified_dc = DesignConditions(
            operating_pressure=dc.operating_pressure,
            design_pressure=dc.design_pressure,
            maximum_allowable_pressure_ps=dc.maximum_allowable_pressure_ps,
            operating_temperature=dc.operating_temperature,
            design_temperature=dc.design_temperature,
            minimum_design_temperature=dc.minimum_design_temperature,
            external_pressure=vacuum_pressure,
            vacuum_condition=True,
            hydrotest_temperature=dc.hydrotest_temperature,
            corrosion_allowance_internal=dc.corrosion_allowance_internal,
            corrosion_allowance_external=dc.corrosion_allowance_external,
        )
        modified_input["design_conditions"] = modified_dc

        return self.check_shell_external_pressure(modified_input)


__all__ = ["ExternalPressureCalculator"]
