"""EN13445DesignCode — EN 13445 hesap eklentisi.

calc-core DesignCode arayüzünü uygular.
ASME ile karıştırılmaz — ayrı plugin.

K1 kuralı: Formüller yalnızca hesap eklentilerinde.
K5 kuralı: Herhesap denetlenebilir olmalı (ara değerler + madde referansı).
K6 kuralı: Standart telifli metni gömülmez.
K7 kuralı: Domain modelinden bağımsız.

Referans: EN 13445-3:2021+A1:2023
"""

from __future__ import annotations

from typing import Any, Dict

from calc_core.code_interface import DesignCode
from calc_core.result import CalculationResult
from code_en_13445 import formulas


class EN13445DesignCode(DesignCode):
    """EN 13445 hesap eklentisi.

    Uygulanan maddeler:
    - EN 13445-3, 5.4.2: Silindirik gövde, iç basınç
    - EN 13445-3, 5.5.2-5.5.4: Bombeler (ellipsoidal, torispherical, hemispherical)
    - EN 13445-5, 10.2: PED test basıncı
    """

    def __init__(self, edition: str = "2021+A1:2023"):
        self._edition = edition

    @property
    def code_name(self) -> str:
        return "EN 13445"

    @property
    def code_edition(self) -> str:
        return self._edition

    def calculate_shell_thickness(self, input_data: dict) -> CalculationResult:
        """EN 13445-3, 5.4.2 — Silindirik gövde iç basınç et kalınlığı.

        Args:
            input_data: {
                "shell": ShellSection,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "welds": List[WeldJoint],
                "code_edition": str,
            }
        """
        shell = input_data["shell"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        welds = input_data.get("welds", [])

        result = CalculationResult(
            component_id=shell.section_id,
            component_type="shell",
            calculation_type="thickness",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="EN 13445-3, 5.4.2",
            formula_reference="5.4.2-1/5.4.2-2",
        )

        # Malzeme bul
        mat = None
        for m in materials:
            if m.material_id == shell.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Material '{shell.material_id}' not found")
            return result

        # Birimleştirme katsayısı (z) — EN 13445-3, Tablo 5.4.2-1
        z = 1.0
        if shell.weld_joint_id:
            for w in welds:
                if w.joint_id == shell.weld_joint_id:
                    z = w.joint_coefficient
                    break

        # Girdiler
        P = dc.design_pressure
        if shell.inside_diameter:
            R = shell.inside_diameter / 2.0
        else:
            R = shell.outside_diameter / 2.0 - shell.nominal_thickness
        f = mat.allowable_stress  # EN'de "f" = tasarım gerilmesi
        C = shell.internal_corrosion_allowance

        # Korozyonlu iç yarıçap — iç korozyon iç yüzeyden metal yer, iç yarıçap BÜYÜR.
        # ASME tarafındaki aynı düzeltme: docs/validation/asme-worked-examples.md V-16.
        R_corroded = R + C

        # Girdi anlık görüntüsü (K5)
        result.input_snapshot = {
            "P_MPa": P,
            "R_mm": R,
            "R_corroded_mm": R_corroded,
            "f_MPa": f,
            "z": z,
            "C_mm": C,
            "mill_tolerance_pct": shell.mill_tolerance,
            "forming_thinning_mm": shell.forming_thinning,
        }

        # K4: Malzeme manuel girilmiş
        result.add_assumption(
            f"K4: Design stress f={f} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        # Hesap
        try:
            e_circ, e_long, e_required = formulas.shell_thickness_internal_pressure(
                P=P, R=R_corroded, f=f, z=z, e=shell.nominal_thickness, C=C
            )
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Ara değerler (K5)
        result.add_intermediate("P", P, "MPa", "Design pressure")
        result.add_intermediate("R", R, "mm", "Inside radius (original)")
        result.add_intermediate("R_corroded", R_corroded, "mm", "Inside radius (corroded)")
        result.add_intermediate("f", f, "MPa", "Design stress at design temperature")
        result.add_intermediate("z", z, "-", "Joint coefficient")
        result.add_intermediate("C", C, "mm", "Corrosion allowance")
        result.add_intermediate("e_circ", e_circ, "mm", "Required thickness (circumferential stress)")
        result.add_intermediate("e_long", e_long, "mm", "Required thickness (longitudinal stress)")
        result.add_intermediate("e_required", e_required, "mm", "Required thickness (governing)")

        # Mill tolerans + şekillendirme incelmesi
        mt_factor = 1.0 - shell.mill_tolerance / 100.0 if shell.mill_tolerance > 0 else 0.90
        e_nominal = formulas.shell_required_nominal_thickness(
            e_required=e_required,
            C=C,
            mill_tolerance_factor=mt_factor,
            forming_thinning=shell.forming_thinning,
        )

        result.add_intermediate("mill_tolerance_factor", mt_factor, "-", "Mill tolerance factor")
        result.add_intermediate("forming_thinning", shell.forming_thinning, "mm", "Forming thinning")
        result.add_intermediate("e_nominal_required", e_nominal, "mm", "Required nominal thickness")

        # Sonuç
        result.final_result = e_nominal
        result.final_result_unit = "mm"
        result.allowable_limit = shell.nominal_thickness
        result.allowable_limit_unit = "mm"

        # Durum
        utilization = e_nominal / shell.nominal_thickness if shell.nominal_thickness > 0 else float('inf')
        result.utilization_ratio = utilization

        if e_nominal <= shell.nominal_thickness:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Required nominal thickness {e_nominal:.2f} mm exceeds "
                f"selected thickness {shell.nominal_thickness:.2f} mm"
            )

        result.rounding_rule = "shell_required_nominal_thickness"

        # Malzeme bilgisi
        result.material_properties_used = {
            "designation": mat.material_designation,
            "design_stress_f": f,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "standard_pack": mat.standard_pack,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_head_thickness(self, input_data: dict) -> CalculationResult:
        """EN 13445-3, 5.5.x — Bombe et kalınlığı.

        Desteklenen tipler: elliptical, torispherical, hemispherical.
        """
        head = input_data["head"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        welds = input_data.get("welds", [])

        from domain.enums import HeadType

        result = CalculationResult(
            component_id=head.head_id,
            component_type="head",
            calculation_type="thickness",
            code=self.code_name,
            edition=self.code_edition,
        )

        # Malzeme bul
        mat = None
        for m in materials:
            if m.material_id == head.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Material '{head.material_id}' not found")
            return result

        # Birimleştirme katsayısı (z)
        z = 1.0
        if head.weld_joint_id:
            for w in welds:
                if w.joint_id == head.weld_joint_id:
                    z = w.joint_coefficient
                    break

        P = dc.design_pressure
        f = mat.allowable_stress
        C = head.internal_corrosion_allowance
        # Korozyonlu iç ölçüler (bkz. V-16).
        D = head.inside_diameter + 2 * C
        R = D / 2.0

        result.input_snapshot = {
            "P_MPa": P,
            "D_mm": D,
            "f_MPa": f,
            "z": z,
            "C_mm": C,
            "head_type": head.type.value,
        }

        result.add_assumption(
            f"K4: Design stress f={f} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            if head.type == HeadType.ELLIPTICAL:
                result.clause_reference = "EN 13445-3, 5.5.2"
                result.formula_reference = "5.5.2-1"
                e, shape_factor = formulas.head_elliptical_thickness(P, D, f, z, C)
                result.add_intermediate("shape_factor", shape_factor, "-", "Elliptical shape factor")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.TORISPHERICAL:
                result.clause_reference = "EN 13445-3, 5.5.3"
                result.formula_reference = "5.5.3-1"
                L = head.crown_radius if head.crown_radius else D
                r = head.knuckle_radius if head.knuckle_radius else D / 10.0
                e, W = formulas.head_torispherical_thickness(P, D, L, r, f, z, C)
                result.add_intermediate("L", L, "mm", "Crown radius")
                result.add_intermediate("r", r, "mm", "Knuckle radius")
                result.add_intermediate("W_factor", W, "-", "Shape factor W")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.HEMISPHERICAL:
                result.clause_reference = "EN 13445-3, 5.5.4"
                result.formula_reference = "5.5.4-1"
                e = formulas.head_hemispherical_thickness(P, R, f, z, C)
                result.add_intermediate("R", R, "mm", "Inside radius")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.FLAT:
                result.set_not_calculated(
                    "Flat head calculation is not implemented. "
                    "This result must not be used for fabrication."
                )
                return result
            else:
                result.set_not_calculated(f"Unknown head type: {head.type}")
                return result

        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Nominal kalınlık
        mt_factor = 1.0 - head.mill_tolerance / 100.0 if head.mill_tolerance > 0 else 0.90
        e_nominal = formulas.shell_required_nominal_thickness(
            e_required=e,
            C=C,
            mill_tolerance_factor=mt_factor,
            forming_thinning=head.forming_thinning,
        )

        result.add_intermediate("P", P, "MPa", "Design pressure")
        result.add_intermediate("f", f, "MPa", "Design stress")
        result.add_intermediate("z", z, "-", "Joint coefficient")
        result.add_intermediate("C", C, "mm", "Corrosion allowance")
        result.add_intermediate("mill_tolerance_factor", mt_factor, "-", "Mill tolerance factor")
        result.add_intermediate("e_nominal_required", e_nominal, "mm", "Required nominal thickness")

        result.final_result = e_nominal
        result.final_result_unit = "mm"
        result.allowable_limit = head.nominal_thickness
        result.allowable_limit_unit = "mm"

        utilization = e_nominal / head.nominal_thickness if head.nominal_thickness > 0 else float('inf')
        result.utilization_ratio = utilization

        if e_nominal <= head.nominal_thickness:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Required nominal thickness {e_nominal:.2f} mm exceeds "
                f"selected thickness {head.nominal_thickness:.2f} mm"
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "design_stress_f": f,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "standard_pack": mat.standard_pack,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_mawp(self, input_data: dict) -> CalculationResult:
        """MAWP hesabı — her bileşen için ayrı.

        Args:
            input_data: {
                "component_type": "shell" | "head",
                "component": ShellSection | Head,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "welds": List[WeldJoint],
                "nominal_thickness": float,
                "code_edition": str,
            }
        """
        comp_type = input_data["component_type"]
        component = input_data["component"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        welds = input_data.get("welds", [])
        t_actual = input_data.get("nominal_thickness", component.nominal_thickness)

        result = CalculationResult(
            component_id=component.section_id if hasattr(component, 'section_id') else component.head_id,
            component_type=comp_type,
            calculation_type="mawp",
            code=self.code_name,
            edition=self.code_edition,
        )

        # Malzeme
        mat_id = component.material_id
        mat = None
        for m in materials:
            if m.material_id == mat_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Material '{mat_id}' not found")
            return result

        # Birimleştirme katsayısı
        z = 1.0
        weld_id = component.weld_joint_id if hasattr(component, 'weld_joint_id') else None
        if weld_id:
            for w in welds:
                if w.joint_id == weld_id:
                    z = w.joint_coefficient
                    break

        f = mat.allowable_stress
        C = component.internal_corrosion_allowance

        result.input_snapshot = {
            "component_type": comp_type,
            "e_actual_mm": t_actual,
            "f_MPa": f,
            "z": z,
            "C_mm": C,
        }

        result.add_assumption(
            f"K4: Design stress f={f} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            if comp_type == "shell":
                if component.inside_diameter:
                    R = component.inside_diameter / 2.0
                else:
                    R = component.outside_diameter / 2.0 - t_actual
                R = R + C  # korozyonlu iç yarıçap (V-16)
                result.clause_reference = "EN 13445-3, 5.4.2"
                mawp = formulas.mawp_from_shell(R, t_actual, f, z, C)
                result.add_intermediate("R", R, "mm", "Corroded inside radius")
                result.add_intermediate("e_actual", t_actual, "mm", "Actual thickness")
                result.add_intermediate("C", C, "mm", "Corrosion allowance")
                result.add_intermediate("e_corroded", t_actual - C, "mm", "Corroded thickness")

            elif comp_type == "head":
                from domain.enums import HeadType
                head = component
                D = head.inside_diameter + 2 * C  # korozyonlu iç çap (V-16)
                if head.type == HeadType.ELLIPTICAL:
                    result.clause_reference = "EN 13445-3, 5.5.2"
                    mawp = formulas.mawp_from_head("elliptical", D, t_actual, f, z, C=C)
                elif head.type == HeadType.TORISPHERICAL:
                    result.clause_reference = "EN 13445-3, 5.5.3"
                    L = head.crown_radius if head.crown_radius else D
                    r = head.knuckle_radius if head.knuckle_radius else D / 10.0
                    mawp = formulas.mawp_from_head("torispherical", D, t_actual, f, z, L, r, C)
                elif head.type == HeadType.HEMISPHERICAL:
                    result.clause_reference = "EN 13445-3, 5.5.4"
                    mawp = formulas.mawp_from_head("hemispherical", D, t_actual, f, z, C=C)
                else:
                    result.set_not_calculated(f"Unsupported head type: {head.type}")
                    return result
                result.add_intermediate("D", D, "mm", "Inside diameter")
            else:
                result.set_not_calculated(f"Unknown component type: {comp_type}")
                return result

        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        result.add_intermediate("f", f, "MPa", "Design stress")
        result.add_intermediate("z", z, "-", "Joint coefficient")
        result.add_intermediate("MAWP", mawp, "MPa", "Maximum Allowable Working Pressure")

        result.final_result = mawp
        result.final_result_unit = "MPa"
        result.set_pass()
        result.material_properties_used = {
            "designation": mat.material_designation,
            "design_stress_f": f,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_hydrotest_pressure(self, input_data: dict) -> CalculationResult:
        """EN 13445-5, 10.2 — PED test basıncı.

        PED test basıncı = max(1.25 × çalışma azami yükü, 1.43 × PS)

        Args:
            input_data: {
                "project": VesselProject,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "code_edition": str,
            }
        """
        dc = input_data["design_conditions"]
        project = input_data.get("project")

        result = CalculationResult(
            component_type="system",
            calculation_type="hydrotest",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="EN 13445-5, 10.2",
            formula_reference="10.2-1",
        )

        # PED test basıncı
        ps = dc.maximum_allowable_pressure_ps
        p_operating_max = dc.operating_pressure

        p_test, limiter = formulas.ped_test_pressure(
            ps_mpa=ps,
            operating_pressure_max=p_operating_max,
        )

        result.input_snapshot = {
            "PS_MPa": ps,
            "P_operating_max_MPa": p_operating_max,
            "limiter": limiter,
            "hydrotest_temperature_C": dc.hydrotest_temperature,
        }

        result.add_intermediate("PS", ps, "MPa", "Maximum allowable pressure (PS)")
        result.add_intermediate("P_operating_max", p_operating_max, "MPa", "Maximum operating pressure")
        result.add_intermediate("P_from_op", 1.25 * p_operating_max, "MPa", "1.25 × P_operating_max")
        result.add_intermediate("P_from_ps", 1.43 * ps, "MPa", "1.43 × PS")
        result.add_intermediate("P_test", p_test, "MPa", "PED test pressure")
        result.add_intermediate("limiter", limiter, "-", "Limiter")

        result.add_assumption(
            f"PED test pressure = max(1.25 × {p_operating_max}, 1.43 × {ps}) = {p_test:.3f} MPa. "
            f"Limiter: {limiter}."
        )

        result.final_result = p_test
        result.final_result_unit = "MPa"
        result.set_pass()

        return result

    def calculate_nozzle(self, input_data: dict) -> CalculationResult:
        """Nozul takviye hesabı — NOT_CALCULATED (bu aşamada)."""
        result = CalculationResult(
            component_type="nozzle",
            calculation_type="nozzle_reinforcement",
            code=self.code_name,
            edition=self.code_edition,
        )
        nozzle = input_data.get("nozzle")
        if nozzle:
            result.component_id = nozzle.tag
        result.set_not_calculated(
            "Nozzle reinforcement calculation for EN 13445 will be implemented in a future phase. "
            "This result must not be used for fabrication."
        )
        return result


__all__ = ["EN13445DesignCode"]
