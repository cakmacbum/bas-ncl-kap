"""ASMEVIII1DesignCode — ASME VIII Division 1 hesap eklentisi.

K5 kuralı: Herhesap denetlenebilir olmalı (ara değerler + madde referansı).
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from calc_core.code_interface import DesignCode
from calc_core.result import CalculationResult
from code_asme_viii_1 import formulas
from domain.enums import CalculationStatus


class ASMEVIII1DesignCode(DesignCode):
    """ASME VIII Division 1 hesap eklentisi.

    Uygulanan maddeler:
    - UG-27: Silindirik gövde, iç basınç
    - UG-32: Bombeler (ellipsoidal, torispherical, hemispherical)
    - UG-99: Hidrostatik test basıncı
    """

    def __init__(self, edition: str = "2025"):
        self._edition = edition

    @property
    def code_name(self) -> str:
        return "ASME VIII-1"

    @property
    def code_edition(self) -> str:
        return self._edition

    def calculate_shell_thickness(self, input_data: dict) -> CalculationResult:
        """UG-27 — Silindirik gövde iç basınç et kalınlığı.

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
            clause_reference="UG-27(c)(1)",
            formula_reference="UG-27(c)(1) Eq. (1)",
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

        # Kaynak verimi bul
        E = 1.0
        if shell.weld_joint_id:
            for w in welds:
                if w.joint_id == shell.weld_joint_id:
                    E = w.joint_efficiency
                    break

        # Girdiler
        P = dc.design_pressure
        if shell.inside_diameter:
            R = shell.inside_diameter / 2.0
        else:
            R = shell.outside_diameter / 2.0 - shell.nominal_thickness
        S = mat.allowable_stress
        C = shell.internal_corrosion_allowance

        # Korozyon payı düşülmüş yarıçap
        R_corroded = R - C

        # Girdi anlık görüntüsü (K5)
        result.input_snapshot = {
            "P_MPa": P,
            "R_mm": R,
            "R_corroded_mm": R_corroded,
            "S_MPa": S,
            "E": E,
            "C_mm": C,
            "mill_tolerance_pct": shell.mill_tolerance,
            "forming_thinning_mm": shell.forming_thinning,
        }

        # K4: Malzeme manuel girilmiş
        result.add_assumption(
            f"K4: Allowable stress S={S} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        # Hesap
        try:
            t_circ, t_long, t_required = formulas.shell_thickness_internal_pressure(
                P=P, R=R_corroded, S=S, E=E, C=C
            )
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Ara değerler (K5)
        result.add_intermediate("P", P, "MPa", "Design pressure")
        result.add_intermediate("R", R, "mm", "Inside radius (original)")
        result.add_intermediate("R_corroded", R_corroded, "mm", "Inside radius (corroded)")
        result.add_intermediate("S", S, "MPa", "Allowable stress at design temperature")
        result.add_intermediate("E", E, "-", "Joint efficiency")
        result.add_intermediate("C", C, "mm", "Corrosion allowance")
        result.add_intermediate("t_circ", t_circ, "mm", "Required thickness (circumferential stress)")
        result.add_intermediate("t_long", t_long, "mm", "Required thickness (longitudinal stress)")
        result.add_intermediate("t_required", t_required, "mm", "Required thickness (governing)")

        # Mill tolerans + şekillendirme incelmesi
        mt_factor = 1.0 - shell.mill_tolerance / 100.0 if shell.mill_tolerance > 0 else 0.875
        t_nominal = formulas.shell_required_nominal_thickness(
            t_required=t_required,
            C=C,
            mill_tolerance_factor=mt_factor,
            forming_thinning=shell.forming_thinning,
        )

        result.add_intermediate("mill_tolerance_factor", mt_factor, "-", "Mill tolerance factor")
        result.add_intermediate("forming_thinning", shell.forming_thinning, "mm", "Forming thinning")
        result.add_intermediate("t_nominal_required", t_nominal, "mm", "Required nominal thickness")

        # Sonuç
        result.final_result = t_nominal
        result.final_result_unit = "mm"
        result.allowable_limit = shell.nominal_thickness
        result.allowable_limit_unit = "mm"

        # Durum
        if not shell.nominal_thickness or shell.nominal_thickness <= 0:
            result.set_not_calculated(
                "Seçilen nominal kalınlık girilmemiş veya 0. İmalat için kullanılamaz."
            )
            return result
        utilization = t_nominal / shell.nominal_thickness
        result.utilization_ratio = utilization

        if t_nominal <= shell.nominal_thickness:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Required nominal thickness {t_nominal:.2f} mm exceeds "
                f"selected thickness {shell.nominal_thickness:.2f} mm"
            )

        result.rounding_rule = "shell_required_nominal_thickness"

        # Malzeme bilgisi
        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "standard_pack": mat.standard_pack,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_head_thickness(self, input_data: dict) -> CalculationResult:
        """UG-32 — Bombe et kalınlığı.

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

        # Kaynak verimi
        E = 1.0
        if head.weld_joint_id:
            for w in welds:
                if w.joint_id == head.weld_joint_id:
                    E = w.joint_efficiency
                    break

        P = dc.design_pressure
        D = head.inside_diameter
        R = D / 2.0
        S = mat.allowable_stress
        C = head.internal_corrosion_allowance

        result.input_snapshot = {
            "P_MPa": P,
            "D_mm": D,
            "S_MPa": S,
            "E": E,
            "C_mm": C,
            "head_type": head.type.value,
        }

        result.add_assumption(
            f"K4: Allowable stress S={S} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            if head.type == HeadType.ELLIPTICAL:
                result.clause_reference = "UG-32(d)"
                result.formula_reference = "UG-32(d)"
                t, K = formulas.head_elliptical_thickness(P, D, S, E, C)
                result.add_intermediate("K_factor", K, "-", "2:1 elliptical head factor")
                result.add_intermediate("t_required", t, "mm", "Required thickness")

            elif head.type == HeadType.TORISPHERICAL:
                result.clause_reference = "UG-32(e)"
                result.formula_reference = "UG-32(e)"
                L = head.crown_radius if head.crown_radius else D
                r = head.knuckle_radius if head.knuckle_radius else D / 10.0
                t, M = formulas.head_torispherical_thickness_full(P, L, r, S, E)
                result.add_intermediate("L", L, "mm", "Crown radius")
                result.add_intermediate("r", r, "mm", "Knuckle radius")
                result.add_intermediate("M_factor", M, "-", "M factor")
                result.add_intermediate("t_required", t, "mm", "Required thickness")

            elif head.type == HeadType.HEMISPHERICAL:
                result.clause_reference = "UG-32(f)"
                result.formula_reference = "UG-32(f)"
                t = formulas.head_hemispherical_thickness(P, R, S, E, C)
                result.add_intermediate("R", R, "mm", "Inside radius")
                result.add_intermediate("t_required", t, "mm", "Required thickness")

            elif head.type == HeadType.FLAT:
                result.clause_reference = "UG-34(c)(2)"
                result.formula_reference = "UG-34(c)(2)"
                C_attach = head.flat_attachment_factor
                if C_attach is None:
                    result.set_blocked_missing_input(
                        "UG-34 bağlantı katsayısı C girilmemiş. "
                        "Şekil UG-34'e göre bağlantı tipine uygun C değeri girilmeli."
                    )
                    return result
                d = head.inside_diameter - 2 * C  # korozyona uğramış çap
                t = formulas.flat_head_thickness(P, d, S, E, C_attach, CA=C)
                result.add_intermediate("C_attach", C_attach, "-", "UG-34 attachment factor")
                result.add_intermediate("d_corroded", d, "mm", "Corroded diameter")
                result.add_intermediate("t_required", t, "mm", "Required thickness")
            else:
                result.set_not_calculated(f"Unknown head type: {head.type}")
                return result

        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Nominal kalınlık
        mt_factor = 1.0 - head.mill_tolerance / 100.0 if head.mill_tolerance > 0 else 0.875
        t_nominal = formulas.shell_required_nominal_thickness(
            t_required=t,
            C=C,
            mill_tolerance_factor=mt_factor,
            forming_thinning=head.forming_thinning,
        )

        result.add_intermediate("P", P, "MPa", "Design pressure")
        result.add_intermediate("S", S, "MPa", "Allowable stress")
        result.add_intermediate("E", E, "-", "Joint efficiency")
        result.add_intermediate("C", C, "mm", "Corrosion allowance")
        result.add_intermediate("mill_tolerance_factor", mt_factor, "-", "Mill tolerance factor")
        result.add_intermediate("t_nominal_required", t_nominal, "mm", "Required nominal thickness")

        result.final_result = t_nominal
        result.final_result_unit = "mm"
        result.allowable_limit = head.nominal_thickness
        result.allowable_limit_unit = "mm"

        if not head.nominal_thickness or head.nominal_thickness <= 0:
            result.set_not_calculated(
                "Seçilen nominal kalınlık girilmemiş veya 0. İmalat için kullanılamaz."
            )
            return result
        utilization = t_nominal / head.nominal_thickness
        result.utilization_ratio = utilization

        if t_nominal <= head.nominal_thickness:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Required nominal thickness {t_nominal:.2f} mm exceeds "
                f"selected thickness {head.nominal_thickness:.2f} mm"
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
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

        # Kaynak verimi
        E = 1.0
        weld_id = component.weld_joint_id if hasattr(component, 'weld_joint_id') else None
        if weld_id:
            for w in welds:
                if w.joint_id == weld_id:
                    E = w.joint_efficiency
                    break

        S = mat.allowable_stress
        C = component.internal_corrosion_allowance

        result.input_snapshot = {
            "component_type": comp_type,
            "t_actual_mm": t_actual,
            "S_MPa": S,
            "E": E,
            "C_mm": C,
        }

        result.add_assumption(
            f"K4: Allowable stress S={S} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        try:
            if comp_type == "shell":
                if component.inside_diameter:
                    R = component.inside_diameter / 2.0
                else:
                    R = component.outside_diameter / 2.0 - t_actual
                result.clause_reference = "UG-27(c)(1)"
                mawp = formulas.mawp_from_shell(R, t_actual, S, E, C)
                result.add_intermediate("R", R, "mm", "Inside radius")
                result.add_intermediate("t_actual", t_actual, "mm", "Actual thickness")
                result.add_intermediate("C", C, "mm", "Corrosion allowance")
                result.add_intermediate("t_corroded", t_actual - C, "mm", "Corroded thickness")

            elif comp_type == "head":
                from domain.enums import HeadType
                head = component
                D = head.inside_diameter
                if head.type == HeadType.ELLIPTICAL:
                    result.clause_reference = "UG-32(d)"
                    mawp = formulas.mawp_from_ellipsoidal_head(D, t_actual, S, E, C)
                elif head.type == HeadType.TORISPHERICAL:
                    result.clause_reference = "UG-32(e)"
                    L = head.crown_radius if head.crown_radius else D
                    r = head.knuckle_radius if head.knuckle_radius else D / 10.0
                    mawp = formulas.mawp_from_torispherical_head(L, r, t_actual, S, E, C)
                elif head.type == HeadType.HEMISPHERICAL:
                    result.clause_reference = "UG-32(f)"
                    R = D / 2.0
                    mawp = formulas.mawp_from_hemispherical_head(R, t_actual, S, E, C)
                elif head.type == HeadType.FLAT:
                    result.clause_reference = "UG-34(c)(2)"
                    C_attach = head.flat_attachment_factor
                    if C_attach is None:
                        result.set_blocked_missing_input(
                            "UG-34 bağlantı katsayısı C girilmemiş. MAWP hesaplanamaz."
                        )
                        return result
                    d = D - 2 * C  # korozyona uğramış çap
                    mawp = formulas.flat_head_mawp(d, t_actual, S, E, C_attach, CA=C)
                    result.add_intermediate("C_attach", C_attach, "-", "UG-34 attachment factor")
                    result.add_intermediate("d_corroded", d, "mm", "Corroded diameter")
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

        result.add_intermediate("S", S, "MPa", "Allowable stress")
        result.add_intermediate("E", E, "-", "Joint efficiency")
        result.add_intermediate("MAWP", mawp, "MPa", "Maximum Allowable Working Pressure")

        result.final_result = mawp
        result.final_result_unit = "MPa"
        result.set_pass()
        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_hydrotest_pressure(self, input_data: dict) -> CalculationResult:
        """UG-99 — Hidrostatik test basıncı.

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
            clause_reference="UG-99(b)",
            formula_reference="UG-99(b)",
        )

        # Test sıcaklığındaki ve tasarım sıcaklığındaki izin verilen gerilme
        # V1'de test sıcaklığı = 20°C, malzeme özellikleri manuel girilmiş
        # S_test / S_design oranı kullanıcıdan alınır veya 1.0 varsayılır
        materials = input_data.get("materials", [])

        if not materials:
            result.set_not_calculated("No materials defined for hydrotest calculation")
            return result

        # İlk malzemeyi kullan (V1'de basitleştirme)
        mat = materials[0]
        S_design = mat.allowable_stress

        # V1'de test sıcaklığındaki gerilme = tasarım sıcaklığındaki gerilme varsayımı
        # (daha düşük sıcaklık → genellikle daha yüksek gerilme → ratio ≥ 1.0)
        S_test = S_design  # Konservatif varsayım

        result.add_assumption(
            f"K4: Test temperature allowable stress = design temperature allowable stress "
            f"({S_design} MPa). Ratio = 1.0 (conservative)."
        )

        P_design = dc.design_pressure
        p_test = formulas.hydrotest_pressure_asme(P_design, S_test, S_design)

        result.input_snapshot = {
            "P_design_MPa": P_design,
            "S_test_MPa": S_test,
            "S_design_MPa": S_design,
            "hydrotest_temperature_C": dc.hydrotest_temperature,
        }

        result.add_intermediate("P_design", P_design, "MPa", "Design pressure")
        result.add_intermediate("S_test", S_test, "MPa", "Allowable stress at test temperature")
        result.add_intermediate("S_design", S_design, "MPa", "Allowable stress at design temperature")
        result.add_intermediate("ratio", S_test / S_design, "-", "Stress ratio (S_test/S_design)")
        result.add_intermediate("P_test", p_test, "MPa", "Hydrostatic test pressure")

        result.final_result = p_test
        result.final_result_unit = "MPa"
        result.set_pass()

        return result

    def calculate_pneumatic_test_pressure(self, input_data: dict) -> CalculationResult:
        """UG-100 — Pnömatik test basıncı.

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
            calculation_type="pneumatic_test",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="UG-100",
            formula_reference="UG-100",
        )

        materials = input_data.get("materials", [])

        if not materials:
            result.set_not_calculated("No materials defined for pneumatic test calculation")
            return result

        mat = materials[0]
        S_design = mat.allowable_stress
        S_test = S_design  # Konservatif varsayım (hidrotest ile aynı)

        result.add_assumption(
            f"K4: Test temperature allowable stress = design temperature allowable stress "
            f"({S_design} MPa). Ratio = 1.0 (conservative)."
        )

        P_design = dc.design_pressure
        p_test = formulas.pneumatic_test_pressure(P_design, S_test, S_design)

        result.input_snapshot = {
            "P_design_MPa": P_design,
            "S_test_MPa": S_test,
            "S_design_MPa": S_design,
            "test_temperature_C": dc.hydrotest_temperature,
        }

        result.add_intermediate("P_design", P_design, "MPa", "Design pressure")
        result.add_intermediate("S_test", S_test, "MPa", "Allowable stress at test temperature")
        result.add_intermediate("S_design", S_design, "MPa", "Allowable stress at design temperature")
        result.add_intermediate("ratio", S_test / S_design, "-", "Stress ratio (S_test/S_design)")
        result.add_intermediate("P_test", p_test, "MPa", "Pneumatic test pressure")

        result.final_result = p_test
        result.final_result_unit = "MPa"
        result.set_pass()

        # Pnömatik test güvenlik uyarıları
        result.add_warning(
            "Pnömatik test hidrostatik testten daha tehlikelidir. "
            "Yüksek enerji depolayan bir testtir; uygun güvenlik önlemleri alınmalı."
        )
        result.add_warning(
            f"Test sıcaklığı {dc.hydrotest_temperature}°C. "
            "MDMT kontrolü yapılmalı — test sıcaklığı MDMT'nin altında olmamalı."
        )

        return result

    def _host_required_thickness(self, host, host_type: str, dc, materials) -> float:
        """Host bileşenin (gövde/bombe) korozyonlu gerekli et kalınlığını (t_required) getir.

        Nozul takviye hesabı için mevcut kalınlık hesabını yeniden kullanır (K5 izlenebilirlik).
        """
        if host_type == "shell":
            res = self.calculate_shell_thickness({
                "shell": host,
                "design_conditions": dc,
                "materials": materials,
                "welds": [],
            })
        else:
            res = self.calculate_head_thickness({
                "head": host,
                "design_conditions": dc,
                "materials": materials,
                "welds": [],
            })
        for iv in res.intermediate_values:
            if iv.get("name") == "t_required":
                return float(iv.get("value") or 0.0)
        return 0.0

    def calculate_nozzle(self, input_data: dict) -> CalculationResult:
        """Nozul takviye hesabı — ASME UG-37/UG-40 (nozzles paketine delege eder)."""
        nozzle = input_data.get("nozzle")
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        shells = input_data.get("shell_sections", [])
        heads = input_data.get("heads", [])

        def _nc(msg: str) -> CalculationResult:
            r = CalculationResult(
                component_id=nozzle.tag if nozzle else None,
                component_type="nozzle",
                calculation_type="nozzle_reinforcement",
                code=self.code_name,
                edition=self.code_edition,
            )
            r.set_not_calculated(msg + " This result must not be used for fabrication.")
            return r

        if nozzle is None:
            return _nc("Nozzle definition missing.")

        try:
            from nozzles import (
                NozzleReinforcementInput,
                build_reinforcement_calculation_result,
            )
        except ImportError:
            return _nc("Nozzle reinforcement module (nozzles) is not available.")

        # Host bileşeni bul (gövde veya bombe)
        host = None
        host_type = None
        for s in shells:
            if s.section_id == nozzle.host_component_id:
                host, host_type = s, "shell"
                break
        if host is None:
            for h in heads:
                if h.head_id == nozzle.host_component_id:
                    host, host_type = h, "head"
                    break
        if host is None:
            return _nc(f"Host component '{nozzle.host_component_id}' not found for nozzle {nozzle.tag}.")

        def _find_mat(mat_id):
            for m in materials:
                if m.material_id == mat_id:
                    return m
            return None

        noz_mat = _find_mat(nozzle.material_id)
        host_mat = _find_mat(host.material_id)

        t_req_host = self._host_required_thickness(host, host_type, dc, materials)

        inp = NozzleReinforcementInput(
            nozzle_tag=nozzle.tag,
            nozzle_inside_diameter=nozzle.inside_diameter,
            nozzle_outside_diameter=nozzle.outside_diameter,
            nozzle_neck_thickness=nozzle.neck_thickness,
            nozzle_corrosion_allowance=nozzle.corrosion_allowance,
            nozzle_projection_outside=nozzle.outside_projection,
            nozzle_projection_inside=nozzle.inside_projection,
            nozzle_allowable_stress=noz_mat.allowable_stress if noz_mat else 0.0,
            component_type=host_type,
            component_inside_diameter=host.inside_diameter or 0.0,
            component_nominal_thickness=host.nominal_thickness,
            component_corrosion_allowance=host.internal_corrosion_allowance,
            component_required_thickness=t_req_host,
            component_allowable_stress=host_mat.allowable_stress if host_mat else 0.0,
            has_reinforcement_pad=nozzle.reinforcement_pad,
            reinforcement_pad_od=nozzle.reinforcement_pad_od or 0.0,
            reinforcement_pad_thickness=nozzle.reinforcement_pad_thickness or 0.0,
            reinforcement_pad_allowable_stress=host_mat.allowable_stress if host_mat else 0.0,
            design_pressure=dc.design_pressure,
            design_temperature=dc.design_temperature,
        )
        return build_reinforcement_calculation_result(inp)

    def validate_welds(self, project) -> list:
        """Projedeki tüm kaynakları doğrula (welds paketine delege eder)."""
        try:
            from welds import WeldValidationInput, build_weld_validation_result
        except ImportError:
            return []

        dc = project.design_conditions
        results = []
        for weld in project.welds:
            # Bağlı bileşen kalınlığı: ilk gövde kesitini referans al (basitleştirilmiş)
            comp_thickness = 0.0
            if project.shell_sections:
                comp_thickness = project.shell_sections[0].nominal_thickness
            is_nozzle_weld = (weld.weld_category or "").upper() in ("C", "D")
            inp = WeldValidationInput(
                weld=weld,
                connected_component_thickness=comp_thickness,
                is_nozzle_weld=is_nozzle_weld,
                design_pressure=dc.design_pressure,
                design_temperature=dc.design_temperature,
            )
            results.append(build_weld_validation_result(inp))
        return results

    def check_nozzle_clashes(self, project) -> list:
        """Nozul çakışma/geometri kontrolleri (nozzles paketine delege eder)."""
        try:
            from nozzles import build_clash_check_result
        except ImportError:
            return []

        return [build_clash_check_result(nozzle, project) for nozzle in project.nozzles]

    def check_external_pressure(self, project) -> list:
        """Dış basınç/vakum stabilite kontrolü (external-pressure paketine delege eder).

        K6 kuralı: A/B chart verisi yoksa BLOCKED_CODE_DATA döner.
        """
        dc = project.design_conditions
        external_pressure = dc.external_pressure or 0

        if external_pressure <= 0 and not dc.vacuum_condition:
            return []

        try:
            from external_pressure import ExternalPressureCalculator
        except ImportError:
            r = CalculationResult(
                component_type="system",
                calculation_type="external_pressure_check",
                code=self.code_name,
                edition=self.code_edition,
            )
            r.set_not_calculated(
                "External pressure module (external-pressure) is not available."
            )
            return [r]

        calc = ExternalPressureCalculator(code=self.code_name, edition=self.code_edition)
        results = []

        # Chart verisi yoksa BLOCKED_CODE_DATA (K6)
        # A/B değerleri kullanıcıdan alınır — eğer girilmemişse blokaj
        for shell in project.shell_sections:
            r = calc.check_shell_external_pressure({
                "shell": shell,
                "design_conditions": dc,
                "materials": project.materials,
                "strain_factor_A": 0.0,  # Kullanıcı girecek
                "allowable_stress_B": 0.0,  # Kullanıcı girecek
            })
            # A/B girilmemişse NOT_CALCULATED döner → BLOCKED_CODE_DATA'ya çevir
            if r.status == CalculationStatus.NOT_CALCULATED and "chart" in (r.warnings[0].lower() if r.warnings else ""):
                r.set_blocked_code_data(
                    "UG-28 chart verisi (A/B faktörleri) girilmemiş. "
                    "Kullanıcıdan lisanslı chart verisi gerekli (K6)."
                )
            results.append(r)

        for head in project.heads:
            r = calc.check_head_external_pressure({
                "head": head,
                "design_conditions": dc,
                "materials": project.materials,
                "strain_factor_A": 0.0,
                "allowable_stress_B": 0.0,
            })
            if r.status == CalculationStatus.NOT_CALCULATED and "chart" in (r.warnings[0].lower() if r.warnings else ""):
                r.set_blocked_code_data(
                    "UG-33 chart verisi (A/B faktörleri) girilmemiş. "
                    "Kullanıcıdan lisanslı chart verisi gerekli (K6)."
                )
            results.append(r)

        # Vakum kontrolü
        if dc.vacuum_condition:
            if project.shell_sections:
                r = calc.check_vacuum_stability({
                    "shell": project.shell_sections[0],
                    "design_conditions": dc,
                    "materials": project.materials,
                    "strain_factor_A": 0.0,
                    "allowable_stress_B": 0.0,
                })
                if r.status == CalculationStatus.NOT_CALCULATED and "chart" in (r.warnings[0].lower() if r.warnings else ""):
                    r.set_blocked_code_data(
                        "Vakum stabilite kontrolü için UG-28 chart verisi gerekli (K6)."
                    )
                results.append(r)

        return results

    def calculate_cone_thickness(self, input_data: dict) -> CalculationResult:
        """UG-32(g) — Konik bölüm et kalınlığı.

        Args:
            input_data: {
                "cone": Cone,
                "design_conditions": DesignConditions,
                "materials": List[MaterialProperty],
                "welds": List[WeldJoint],
                "code_edition": str,
            }
        """
        cone = input_data["cone"]
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        welds = input_data.get("welds", [])

        result = CalculationResult(
            component_id=cone.cone_id,
            component_type="cone",
            calculation_type="thickness",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="UG-32(g)",
            formula_reference="UG-32(g)",
        )

        # Malzeme bul
        mat = None
        for m in materials:
            if m.material_id == cone.material_id:
                mat = m
                break
        if mat is None:
            result.set_not_calculated(f"Material '{cone.material_id}' not found")
            return result

        # Kaynak verimi
        E = 1.0
        if cone.weld_joint_id:
            for w in welds:
                if w.joint_id == cone.weld_joint_id:
                    E = w.joint_efficiency
                    break

        P = dc.design_pressure
        D = cone.large_diameter
        S = mat.allowable_stress
        C = cone.internal_corrosion_allowance
        alpha = cone.half_apex_angle

        result.input_snapshot = {
            "P_MPa": P,
            "D_mm": D,
            "S_MPa": S,
            "E": E,
            "C_mm": C,
            "alpha_deg": alpha,
        }

        result.add_assumption(
            f"K4: Allowable stress S={S} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )

        # Yarı tepe açısı uyarısı
        if alpha > 30:
            result.add_warning(
                f"Yarı tepe açısı {alpha}° > 30°. "
                "UG-32(g) yerine Appendix 1-4/1-5 kontrolü gerekebilir."
            )

        try:
            t = formulas.cone_thickness(P, D, S, E, alpha, C)
        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        result.add_intermediate("P", P, "MPa", "Design pressure")
        result.add_intermediate("D", D, "mm", "Large diameter")
        result.add_intermediate("S", S, "MPa", "Allowable stress")
        result.add_intermediate("E", E, "-", "Joint efficiency")
        result.add_intermediate("alpha", alpha, "deg", "Half apex angle")
        result.add_intermediate("cos_alpha", math.cos(math.radians(alpha)), "-", "cos(α)")
        result.add_intermediate("C", C, "mm", "Corrosion allowance")
        result.add_intermediate("t_required", t, "mm", "Required thickness")

        # Nominal kalınlık
        mt_factor = 1.0 - cone.mill_tolerance / 100.0 if cone.mill_tolerance > 0 else 0.875
        t_nominal = formulas.shell_required_nominal_thickness(
            t_required=t,
            C=C,
            mill_tolerance_factor=mt_factor,
        )

        result.add_intermediate("mill_tolerance_factor", mt_factor, "-", "Mill tolerance factor")
        result.add_intermediate("t_nominal_required", t_nominal, "mm", "Required nominal thickness")

        result.final_result = t_nominal
        result.final_result_unit = "mm"
        result.allowable_limit = cone.nominal_thickness
        result.allowable_limit_unit = "mm"

        if not cone.nominal_thickness or cone.nominal_thickness <= 0:
            result.set_not_calculated(
                "Seçilen nominal kalınlık girilmemiş veya 0. İmalat için kullanılamaz."
            )
            return result
        utilization = t_nominal / cone.nominal_thickness
        result.utilization_ratio = utilization

        if t_nominal <= cone.nominal_thickness:
            result.set_pass(utilization)
        else:
            result.set_fail(utilization)
            result.add_warning(
                f"Required nominal thickness {t_nominal:.2f} mm exceeds "
                f"selected thickness {cone.nominal_thickness:.2f} mm"
            )

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "source_reference": mat.source_reference,
        }

        return result


__all__ = ["ASMEVIII1DesignCode"]
