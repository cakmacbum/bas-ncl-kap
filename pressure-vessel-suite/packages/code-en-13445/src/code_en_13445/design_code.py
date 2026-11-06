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

from typing import Any, Dict, List

from calc_core.code_interface import DesignCode
from calc_core.result import CalculationResult
from code_en_13445 import formulas
from domain.enums import CalculationStatus

# EN 13445'te yaygın torisferik bombe (Korbbogen / DIN 28011) için büküm yarıçapı
# oranı. ASME F&D'nin %6'sından farklıdır — bu yüzden ASME'deki sabit BURAYA
# kopyalanmaz. Değerin kendisi bağımsız olarak doğrulanmadı; yalnızca varsayım
# olarak kaydedilir. Bkz. docs/limitations.md B-09.
EN_KNUCKLE_RATIO = 0.10


def _torispherical_radii_en(head, D: float, result: CalculationResult) -> tuple[float, float]:
    """EN torisferik bombe için taç (L) ve büküm (r) yarıçapları.

    Kullanıcı vermezse varsayılan kullanılır — ama **sessizce değil**. ASME
    tarafında aynı sessiz varsayılan %13'lük emniyetsiz bir sapmaya yol açmıştı
    (V-12); aynı desen burada tekrarlanmasın diye varsayım kayda geçer (K4).
    """
    if getattr(head, "torispherical_geometry", "standard_asme_fd") == "custom":
        if not head.crown_radius or not head.knuckle_radius:
            raise ValueError("Özel torisferik geometri için crown_radius ve knuckle_radius zorunludur")
        return head.crown_radius, head.knuckle_radius
    L = head.crown_radius if head.crown_radius else D
    if not head.crown_radius:
        result.add_assumption(
            f"K4: Taç yarıçapı girilmedi; L = D = {L:.1f} mm varsayıldı."
        )

    r = head.knuckle_radius if head.knuckle_radius else EN_KNUCKLE_RATIO * D
    if not head.knuckle_radius:
        result.add_assumption(
            f"K4: Büküm yarıçapı girilmedi; Korbbogen (DIN 28011) tipi varsayılarak "
            f"r = 0.10 D = {r:.1f} mm alındı. Bombenin gerçek bükümü farklıysa "
            f"gerekli kalınlık değişir."
        )
        result.add_warning(
            "Büküm yarıçapı imalat çiziminden girilmelidir — varsayılan %10 "
            "(Korbbogen) kullanıldı. Bu değer gerekli kalınlığı doğrudan etkiler "
            "ve bağımsız olarak doğrulanmamıştır (limitations.md B-09)."
        )

    return L, r


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

    @staticmethod
    def _apply_material_data_check(result: CalculationResult, mat, dc, nominal_thickness: float) -> None:
        """Flag material S metadata that does not match the entered design point.

        This check only verifies the user's declared temperature and thickness
        range; it does not prove that the manually entered EN design stress is
        the correct tabulated value.
        """
        issues = []
        if abs(mat.temperature - dc.design_temperature) > 1e-6:
            issues.append(
                f"Material '{mat.material_id}' design stress is declared at {mat.temperature:g} C; "
                f"design temperature is {dc.design_temperature:g} C. Verify the EN material value."
            )
        if nominal_thickness and not (mat.thickness_min <= nominal_thickness <= mat.thickness_max):
            issues.append(
                f"Nominal thickness {nominal_thickness:g} mm is outside material '{mat.material_id}' "
                f"declared range [{mat.thickness_min:g}, {mat.thickness_max:g}] mm."
            )
        for issue in issues:
            result.add_warning(issue)
        if issues and result.status == CalculationStatus.PASS:
            result.set_review_required(issues[0])

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
                P=P, R=R_corroded, f=f, z=z
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
        # K4: Negatif sac toleransı girilmediyse sektör tipiği varsayılır.
        # Değer makul ama sonucu ~%10 etkiler — sessiz kalmaz.
        if shell.mill_tolerance > 0:
            mt_factor = 1.0 - shell.mill_tolerance / 100.0
        else:
            mt_factor = 0.90
            result.add_assumption(
                "K4: Negatif sac toleransı girilmedi; "
                f"varsayılan {(1 - 0.90) * 100:.1f}% kullanıldı."
            )
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
        self._apply_material_data_check(result, mat, dc, shell.nominal_thickness)

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

        flat_review = False
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
                e, shape_factor = formulas.head_elliptical_thickness(P, D, f, z)
                result.add_intermediate("shape_factor", shape_factor, "-", "Elliptical shape factor")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.TORISPHERICAL:
                result.clause_reference = "EN 13445-3, 5.5.3"
                result.formula_reference = "5.5.3-1"
                L, r = _torispherical_radii_en(head, D, result)
                e, W = formulas.head_torispherical_thickness(P, L, r, f, z)
                result.add_intermediate("L", L, "mm", "Crown radius")
                result.add_intermediate("r", r, "mm", "Knuckle radius")
                result.add_intermediate("W_factor", W, "-", "Shape factor W")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.HEMISPHERICAL:
                result.clause_reference = "EN 13445-3, 5.5.4"
                result.formula_reference = "5.5.4-1"
                e = formulas.head_hemispherical_thickness(P, R, f, z)
                result.add_intermediate("R", R, "mm", "Inside radius")
                result.add_intermediate("e_required", e, "mm", "Required thickness")

            elif head.type == HeadType.FLAT:
                result.clause_reference = "EN 13445-3, 10.4"
                result.formula_reference = "e = C·D·√(P/f)"
                C_flat = getattr(head, "en_flat_end_factor_c", None)
                if not C_flat:
                    result.set_blocked_code_data(
                        "EN 13445-3, 10: düz kapak C katsayısı lisanslı grafikten okunur ve "
                        "programda yoktur (K6). Head.en_flat_end_factor_c girilmeden hesap yapılmaz; "
                        "ASME UG-34 C'si yerine kullanılmaz."
                    )
                    return result
                e = formulas.flat_end_thickness(P, D, f, C_flat)
                flat_review = True
                result.add_intermediate("C_flat", C_flat, "-", "EN 13445-3 Cl.10 factor C (user-read)")
                result.add_intermediate("D", D, "mm", "Corroded inside diameter")
                result.add_intermediate("e_required", e, "mm", "Required thickness")
                result.add_assumption(
                    "EN 13445-3, 10.4 kaynaklı desteksiz dairesel düz kapak biçimi e = C·D·√(P/f) "
                    "kullanıldı; z uygulanmadı, D = korozyonlu iç çap. Cıvatalı kapak (10.5) contadan "
                    "gelen moment terimini içerir ve bu formül onun için yetersizdir. Formül lisanslı "
                    "metinle doğrulanmadı (verified=False)."
                )
            else:
                result.set_not_calculated(f"Unknown head type: {head.type}")
                return result

        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Nominal kalınlık
        # K4: Negatif sac toleransı girilmediyse sektör tipiği varsayılır.
        # Değer makul ama sonucu ~%10 etkiler — sessiz kalmaz.
        if head.mill_tolerance > 0:
            mt_factor = 1.0 - head.mill_tolerance / 100.0
        else:
            mt_factor = 0.90
            result.add_assumption(
                "K4: Negatif sac toleransı girilmedi; "
                f"varsayılan {(1 - 0.90) * 100:.1f}% kullanıldı."
            )
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
        if flat_review:
            self._cap_unverified(result, "EN 13445-3, 10")
        self._apply_material_data_check(result, mat, dc, head.nominal_thickness)

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
        if comp_type == "cone":
            return self._cone_mawp(input_data)
        dc = input_data["design_conditions"]
        materials = input_data.get("materials", [])
        welds = input_data.get("welds", [])
        t_actual = input_data.get("nominal_thickness", component.nominal_thickness)
        flat_review = False

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
                    L, r = _torispherical_radii_en(head, D, result)
                    mawp = formulas.mawp_from_head("torispherical", D, t_actual, f, z, L, r, C)
                elif head.type == HeadType.HEMISPHERICAL:
                    result.clause_reference = "EN 13445-3, 5.5.4"
                    mawp = formulas.mawp_from_head("hemispherical", D, t_actual, f, z, C=C)
                elif head.type == HeadType.FLAT:
                    result.clause_reference = "EN 13445-3, 10.4"
                    result.formula_reference = "P = f·(e/(C·D))²"
                    C_flat = getattr(head, "en_flat_end_factor_c", None)
                    if not C_flat:
                        result.set_blocked_code_data(
                            "EN 13445-3, 10: düz kapak C katsayısı girilmedi (Head.en_flat_end_factor_c); "
                            "MAWP hesaplanmadı (K6)."
                        )
                        return result
                    mawp = formulas.flat_end_mawp(D, t_actual - C, f, C_flat)
                    flat_review = True
                    result.add_intermediate("C_flat", C_flat, "-", "EN 13445-3 Cl.10 factor C (user-read)")
                    result.add_intermediate("e_corroded", t_actual - C, "mm", "Corroded thickness")
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
        if flat_review:
            self._cap_unverified(result, "EN 13445-3, 10")
        self._apply_material_data_check(result, mat, dc, t_actual)
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

        # EN 13445-5 10.2.3.3.1: Pt = max(1.25·Ps·fa/ft ; 1.43·Ps). fa/ft (test/tasarım
        # sıcaklığı gerilme oranı) uygulanmıyor. 1.43·Ps, oran ≤ 1.43/1.25 iken —
        # oranın en büyük/en küçük seçilmesinden bağımsız olarak — belirleyicidir;
        # oran bu eşiği aşarsa test basıncı düşük kalır (emniyetsiz). Oranın hangi
        # malzemeden seçileceği lisanslı metinle doğrulanmadığı için o durumda karar
        # mühendise bırakılır (K3/K4).
        review_reason = self._test_ratio_review_reason(input_data, dc)
        if review_reason:
            result.add_warning(review_reason)
            result.set_review_required(review_reason)
        else:
            result.set_pass()

        return result

    _EN_RATIO_THRESHOLD = 1.43 / 1.25

    def _test_ratio_review_reason(self, input_data: dict, dc):
        """fa/ft oranı sonucu etkileyebilirse gerekçe metni, etkilemezse None."""
        if abs(dc.design_temperature - dc.hydrotest_temperature) < 1e-9:
            return None  # aynı sıcaklık → fa = ft, oran 1
        materials = input_data.get("materials", []) or []
        project = input_data.get("project")
        if project is not None:
            ids = {
                c.material_id
                for coll in (project.shell_sections, project.heads, project.cones)
                for c in coll
            }
            materials = [m for m in materials if m.material_id in ids] or materials
        missing = [m.material_id for m in materials if m.allowable_stress_test_temp is None]
        if missing or not materials:
            return (
                f"fa/ft oranı uygulanmadı: tasarım {dc.design_temperature} °C, test "
                f"{dc.hydrotest_temperature} °C ve test gerilmesi eksik "
                f"({', '.join(missing) or 'malzeme yok'}). Oran > "
                f"{self._EN_RATIO_THRESHOLD:.3f} ise 1.25·Ps·fa/ft terimi 1.43·Ps'i aşar ve "
                "test basıncı olması gerekenden DÜŞÜK kalır. Malzemede 'Test sıcaklığında S' girin."
            )
        worst = max(m.allowable_stress_test_temp / m.allowable_stress for m in materials)
        if worst > self._EN_RATIO_THRESHOLD:
            return (
                f"fa/ft = {worst:.3f} > {self._EN_RATIO_THRESHOLD:.3f}: 1.25·Ps·fa/ft terimi "
                "1.43·Ps'i aşabilir ve bu formül fa/ft'yi uygulamıyor. Oranın hangi malzemeden "
                "seçileceği lisanslı EN 13445-5 10.2.3.3.1 metniyle doğrulanmalıdır."
            )
        return None

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

    def _unsupported_result(
        self,
        *,
        component_id: str = "",
        component_type: str,
        calculation_type: str,
        clause: str,
        reason: str,
        status: str = "not_calculated",
    ) -> CalculationResult:
        """EN kapsamı dışındaki yolu açıkça raporla.

        Özellikle önemli olan, burada ASME hesabına fallback yapılmamasıdır.
        """
        result = CalculationResult(
            component_id=component_id,
            component_type=component_type,
            calculation_type=calculation_type,
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=clause,
        )
        if status == "out_of_scope":
            result.set_out_of_scope(reason)
        else:
            result.set_not_calculated(reason)
        return result

    # ------------------------------------------------------------------
    # E01 — sessiz boşlukları kapat: ASME'de hesaplanıp EN'de hesaplanmayan her
    # kontrol raporda açık NOT_CALCULATED / OUT_OF_SCOPE satırı olarak görünür.
    # Madde numarası doğrulanmadığı için kaynak yalnızca genel "EN 13445-3" ile
    # belirtilir (K6). ASME'ye hiçbir fallback yoktur.
    # ------------------------------------------------------------------
    _NO_ASME_FALLBACK = "no ASME fallback is used; independent review required."

    def calculate_cone_thickness(self, input_data: dict) -> CalculationResult:
        """E02 — EN 13445-3, 7.6.4 konik gövde iç basınç kalınlığı (verified=False)."""
        cone = input_data["cone"]
        dc = input_data["design_conditions"]
        result = CalculationResult(
            component_id=cone.cone_id,
            component_type="cone",
            calculation_type="thickness",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="EN 13445-3, 7.6.4",
            formula_reference="e_con = P·Di/(2fz − P)·1/cos α",
        )
        mat = self._find_material(input_data.get("materials", []), cone.material_id)
        if mat is None:
            result.set_not_calculated(f"Material '{cone.material_id}' not found")
            return result
        z = self._joint_coefficient(input_data.get("welds", []), cone.weld_joint_id)
        P, f, alpha = dc.design_pressure, mat.allowable_stress, cone.half_apex_angle
        C_int, C_ext = cone.internal_corrosion_allowance, cone.external_corrosion_allowance
        Di = cone.large_diameter + 2 * C_int  # en elverişsiz nokta: büyük uç, korozyonlu (V-16)
        result.input_snapshot = {
            "P_MPa": P, "Di_large_mm": cone.large_diameter, "Di_corroded_mm": Di, "f_MPa": f, "z": z,
            "alpha_deg": alpha, "C_int_mm": C_int, "C_ext_mm": C_ext,
            "mill_tolerance_pct": cone.mill_tolerance,
        }
        result.add_assumption(
            f"K4: Design stress f={f} MPa entered manually for "
            f"{mat.material_designation} at {dc.design_temperature}°C"
        )
        try:
            e = formulas.cone_thickness_internal_pressure(P, Di, f, z, alpha)
        except ValueError as exc:
            result.set_not_calculated(str(exc))
            return result
        if cone.mill_tolerance > 0:
            mt = 1.0 - cone.mill_tolerance / 100.0
        else:
            mt = 0.90
            result.add_assumption("K4: Negatif sac toleransı girilmedi; varsayılan 10.0% kullanıldı.")
        e_nom = formulas.shell_required_nominal_thickness(e, C_int + C_ext, mt)
        for name, val, unit, desc in (
            ("P", P, "MPa", "Design pressure"),
            ("Di", Di, "mm", "Corroded inside diameter at large end"),
            ("f", f, "MPa", "Design stress"),
            ("z", z, "-", "Joint coefficient"),
            ("alpha", alpha, "deg", "Half apex angle"),
            ("e_required", e, "mm", "Required thickness (7.6.4)"),
            ("mill_tolerance_factor", mt, "-", "Mill tolerance factor"),
            ("e_nominal_required", e_nom, "mm", "Required nominal thickness"),
        ):
            result.add_intermediate(name, val, unit, desc)
        result.add_assumption(
            "Di olarak büyük uç iç çapı alındı (koni boyunca en büyük gerekli kalınlık). 7.6 "
            "uygulanabilirlik sınırları ve koni uç birleşimleri bu satırda kontrol edilmez "
            "(junction_check satırına bakın)."
        )
        result.final_result, result.final_result_unit = e_nom, "mm"
        result.allowable_limit, result.allowable_limit_unit = cone.nominal_thickness, "mm"
        u = e_nom / cone.nominal_thickness
        if e_nom <= cone.nominal_thickness:
            result.set_pass(u)
            self._cap_unverified(result, "EN 13445-3, 7.6.4")
        else:
            result.set_fail(u)
            result.add_warning(
                f"Required nominal thickness {e_nom:.2f} mm exceeds "
                f"selected thickness {cone.nominal_thickness:.2f} mm"
            )
        self._apply_material_data_check(result, mat, dc, cone.nominal_thickness)
        result.material_properties_used = {
            "designation": mat.material_designation,
            "design_stress_f": f,
            "source_reference": mat.source_reference,
        }
        return result

    def _cone_mawp(self, input_data: dict) -> CalculationResult:
        """E02 — koni MAWP: 7.6.4 denkleminin P için çözümü (verified=False)."""
        cone = input_data["component"]
        dc = input_data["design_conditions"]
        t = input_data.get("nominal_thickness", cone.nominal_thickness)
        result = CalculationResult(
            component_id=cone.cone_id,
            component_type="cone",
            calculation_type="mawp",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference="EN 13445-3, 7.6.4",
            formula_reference="P = 2fz·e·cos α/(Di + e·cos α)",
        )
        mat = self._find_material(input_data.get("materials", []), cone.material_id)
        if mat is None:
            result.set_not_calculated(f"Material '{cone.material_id}' not found")
            return result
        z = self._joint_coefficient(input_data.get("welds", []), cone.weld_joint_id)
        f, alpha = mat.allowable_stress, cone.half_apex_angle
        Di = cone.large_diameter + 2 * cone.internal_corrosion_allowance
        e = t - cone.internal_corrosion_allowance - cone.external_corrosion_allowance
        result.input_snapshot = {
            "component_type": "cone", "e_actual_mm": t, "f_MPa": f, "z": z, "alpha_deg": alpha,
        }
        try:
            mawp = formulas.cone_mawp(Di, e, f, z, alpha)
        except ValueError as exc:
            result.set_not_calculated(str(exc))
            return result
        for name, val, unit, desc in (
            ("Di", Di, "mm", "Corroded inside diameter at large end"),
            ("e_corroded", e, "mm", "Corroded thickness"),
            ("alpha", alpha, "deg", "Half apex angle"),
            ("f", f, "MPa", "Design stress"),
            ("z", z, "-", "Joint coefficient"),
            ("MAWP", mawp, "MPa", "Maximum Allowable Working Pressure"),
        ):
            result.add_intermediate(name, val, unit, desc)
        result.add_assumption(
            "Koni MAWP yalnız membran denklemidir; uç birleşim sınırları (7.6.6/7.6.8) bu değere katılmadı."
        )
        result.final_result, result.final_result_unit = mawp, "MPa"
        result.set_pass()
        self._cap_unverified(result, "EN 13445-3, 7.6.4")
        self._apply_material_data_check(result, mat, dc, t)
        return result

    @staticmethod
    def _find_material(materials, material_id):
        return next((m for m in materials if m.material_id == material_id), None)

    @staticmethod
    def _joint_coefficient(welds, weld_id) -> float:
        if weld_id:
            for w in welds:
                if w.joint_id == weld_id:
                    return w.joint_coefficient
        return 1.0

    @staticmethod
    def _cap_unverified(result: CalculationResult, clause: str) -> None:
        """verified=False: doğrulanmamış formülde PASS en fazla REVIEW_REQUIRED olur."""
        if result.status == CalculationStatus.PASS:
            result.set_review_required(
                f"{clause}: formül lisanslı EN 13445-3 metniyle doğrulanmadı (verified=False); "
                "olumlu sonuç bağımsız mühendis incelemesi gerektirir."
            )

    def calculate_pneumatic_test_pressure(self, input_data: dict) -> CalculationResult:
        return self._unsupported_result(
            component_type="system",
            calculation_type="pneumatic_test",
            clause="EN 13445-5 (testing)",
            reason=f"EN 13445 pneumatic test pressure is not implemented; {self._NO_ASME_FALLBACK}",
        )

    def calculate_hydrotest_component(self, input_data: dict) -> CalculationResult:
        return self._unsupported_result(
            component_id=input_data.get("component_id", ""),
            component_type=input_data.get("component_type", "system"),
            calculation_type="hydrotest_component",
            clause="EN 13445-5 (testing)",
            reason=(
                "EN 13445 hidrostatik test statik kafası uygulanmadı; test basıncı kabın "
                f"tepesindeki değerdir, alt bileşenler daha yüksek basınç görür; {self._NO_ASME_FALLBACK}"
            ),
        )

    def check_mdmt(self, project) -> List[CalculationResult]:
        components = [
            *((s.section_id, "shell") for s in project.shell_sections),
            *((h.head_id, "head") for h in project.heads),
            *((c.cone_id, "cone") for c in project.cones),
        ] or [("", "system")]
        return [self._unsupported_result(
            component_id=cid,
            component_type=ctype,
            calculation_type="mdmt_check",
            clause="EN 13445-2/-3 (material toughness, minimum temperature)",
            reason=f"EN 13445 minimum design metal temperature check is not implemented; {self._NO_ASME_FALLBACK}",
        ) for cid, ctype in components]

    def check_supports(self, project) -> List[CalculationResult]:
        return [self._unsupported_result(
            component_id=sup.support_id,
            component_type="support",
            calculation_type=f"{sup.type}_stress",
            clause="EN 13445-3 (supports and attachments)",
            reason=f"EN 13445 support ({sup.type}) check is not implemented; {self._NO_ASME_FALLBACK}",
        ) for sup in (getattr(project, "supports", None) or [])]

    def validate_welds(self, project) -> List[CalculationResult]:
        return [self._unsupported_result(
            component_id=weld.joint_id,
            component_type="weld",
            calculation_type="weld_validation",
            clause="EN 13445-5 (examination) / EN 13445-4 (fabrication)",
            reason=(
                "EN 13445 weld validation (examination group, joint coefficient z, PWHT) is not "
                f"implemented; the entered joint coefficient is used as-is; {self._NO_ASME_FALLBACK}"
            ),
        ) for weld in project.welds]

    def check_nozzle_clashes(self, project) -> List[CalculationResult]:
        results = [self._unsupported_result(
            component_id=nozzle.tag,
            component_type="nozzle",
            calculation_type="clash_check",
            clause="EN 13445-3 (openings)",
            reason=f"EN 13445 nozzle geometry/clash and opening-limit check is not implemented; {self._NO_ASME_FALLBACK}",
        ) for nozzle in project.nozzles]
        results.append(self._unsupported_result(
            component_type="system",
            calculation_type="inspection_opening",
            clause="EN 13445-3 (inspection openings)",
            reason=f"EN 13445 inspection-opening check is not implemented; {self._NO_ASME_FALLBACK}",
        ))
        if getattr(project, "nozzle_loads", None) is not None:
            results.append(self._unsupported_result(
                component_type="nozzle",
                calculation_type="nozzle_load",
                clause="EN 13445-3 (external nozzle loads)",
                reason=f"EN 13445 nozzle external-load check is not implemented; {self._NO_ASME_FALLBACK}",
            ))
        return results

    def check_junctions(self, project) -> List[CalculationResult]:
        """E02 — EN 13445-3, 7.6.6 (büyük uç) / 7.6.8 (küçük uç) bükümsüz koni-silindir birleşimi."""
        shells = {x.section_id: x for x in project.shell_sections}
        cones = {x.cone_id: x for x in project.cones}
        return [
            self._junction(j, shells, cones, project)
            for j in (getattr(project, "junctions", None) or [])
        ]

    def _junction(self, j, shells, cones, project) -> CalculationResult:
        end = j.cone_end
        clause = {"large": "EN 13445-3, 7.6.6", "small": "EN 13445-3, 7.6.8"}.get(end, "EN 13445-3, 7.6")
        result = CalculationResult(
            component_id=j.junction_id,
            component_type="junction",
            calculation_type="junction_check",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=clause,
        )
        result.input_snapshot = j.model_dump(mode="json")
        if j.junction_type == "shell_to_shell":
            result.set_out_of_scope("Gövde-gövde birleşimi koni birleşimi değildir; EN 13445-3, 7.6 uygulanmaz.")
            return result
        if j.junction_type == "cone_to_head":
            result.set_not_calculated(
                "EN 13445 koni-bombe birleşimi uygulanmadı (7.6 koni-silindir içindir); "
                f"{self._NO_ASME_FALLBACK}"
            )
            return result
        ids = (j.left_component_id, j.right_component_id)
        cone = next((cones[i] for i in ids if i in cones), None)
        shell = next((shells[i] for i in ids if i in shells), None)
        if cone is None or shell is None or end is None:
            result.set_blocked_missing_input(
                "Koni-silindir birleşimi için bir koni, bir silindirik gövde ve açık "
                "'cone_end' (large/small) gerekir."
            )
            return result
        if j.knuckle_radius_mm:
            result.set_not_calculated(
                "Bükümlü (knuckle) birleşim prosedürü (EN 13445-3, 7.6.7) uygulanmadı; "
                f"{self._NO_ASME_FALLBACK}"
            )
            return result
        mats = project.materials
        m_s = self._find_material(mats, shell.material_id)
        m_c = self._find_material(mats, cone.material_id)
        if m_s is None or m_c is None:
            result.set_not_calculated("Birleşimdeki gövde veya koni malzemesi bulunamadı.")
            return result
        P = project.design_conditions.design_pressure
        alpha = cone.half_apex_angle
        z_j = j.weld_efficiency or 1.0
        f = min(m_s.allowable_stress, m_c.allowable_stress) * z_j
        Ci_s = shell.internal_corrosion_allowance
        e1 = shell.nominal_thickness - Ci_s - shell.external_corrosion_allowance
        e2 = cone.nominal_thickness - cone.internal_corrosion_allowance - cone.external_corrosion_allowance
        Di_new = (shell.inside_diameter if shell.inside_diameter
                  else shell.outside_diameter - 2 * shell.nominal_thickness)
        if e1 <= 0 or e2 <= 0:
            result.set_not_calculated("Korozyon payı düşüldükten sonra gövde/koni kalınlığı ≤ 0.")
            return result
        Dc = Di_new + 2 * Ci_s + e1  # silindir ortalama çapı (korozyonlu)
        cone_d = cone.large_diameter if end == "large" else cone.small_diameter
        if abs(cone_d - Di_new) > 0.01 * cone_d:
            result.add_warning(
                f"Koni {end} uç çapı {cone_d:.1f} mm, gövde iç çapı {Di_new:.1f} mm ile %1'den fazla farklı."
            )
        for name, val, unit, desc in (
            ("P", P, "MPa", "Design pressure"),
            ("alpha", alpha, "deg", "Half apex angle"),
            ("Dc", Dc, "mm", "Mean cylinder diameter at junction (corroded)"),
            ("e1", e1, "mm", "Cylinder analysis thickness"),
            ("e2", e2, "mm", "Cone analysis thickness"),
            ("f", f, "MPa", "min(f_cyl, f_cone) × z_junction"),
            ("z_junction", z_j, "-", "Junction weld efficiency"),
        ):
            result.add_intermediate(name, val, unit, desc)
        if not j.weld_efficiency:
            result.add_assumption("Birleşim kaynak verimi girilmedi; z = 1 alındı (tam muayene varsayımı).")
        result.add_assumption(
            "Birleşim kalınlığının 7.6'da tanımlı mesafeler boyunca her iki tarafta sürdürüldüğü "
            "varsayıldı; mesafe kontrolü ve 7.6 uygulanabilirlik sınırları yapılmadı."
        )
        try:
            if end == "large":
                result.formula_reference = (
                    "e_j = P·Dc·β/(2f); β = (1/3)√(Dc/e_j)·tanα/(1+1/√cosα) − 0.15"
                )
                e_j, beta = formulas.cone_large_end_required_thickness(P, Dc, f, alpha)
                e_av = min(e1, e2)
                result.add_intermediate("beta", beta, "-", "Large-end factor β at e_j")
                result.add_intermediate("e_j", e_j, "mm", "Required junction thickness")
                result.add_intermediate("e_available", e_av, "mm", "min(e1, e2)")
                result.final_result, result.final_result_unit = e_j, "mm"
                result.allowable_limit, result.allowable_limit_unit = e_av, "mm"
                u = e_j / e_av
            else:
                result.formula_reference = "P ≤ 2·f·e1/(Dc·β_H); β_H = 0.4√(Dc/e1)·tanα/τ + 0.5"
                s_, tau, beta_h = formulas.cone_small_end_beta_h(Dc, e1, e2, alpha)
                p_max = formulas.cone_small_end_max_pressure(Dc, e1, f, beta_h)
                result.add_intermediate("s", s_, "-", "e2/e1")
                result.add_intermediate("tau", tau, "-", "τ")
                result.add_intermediate("beta_H", beta_h, "-", "Small-end factor β_H")
                result.add_intermediate("P_max", p_max, "MPa", "Allowable pressure at small end")
                result.final_result, result.final_result_unit = P, "MPa"
                result.allowable_limit, result.allowable_limit_unit = p_max, "MPa"
                u = P / p_max
        except ValueError as exc:
            result.set_not_calculated(str(exc))
            return result
        if u <= 1.0:
            result.set_pass(u)
            self._cap_unverified(result, clause)
        else:
            result.set_fail(u)
            result.add_warning(f"Koni {end} uç birleşimi yetersiz: kullanım oranı {u:.3f} > 1.")
        return result

    def check_lifting_lugs(self, project) -> List[CalculationResult]:
        if getattr(project, "lifting_lugs", None) is None:
            return []
        # ASME ile aynı alt başlıklar; her biri açık OUT_OF_SCOPE satırı.
        return [self._unsupported_result(
            component_id="LUG",
            component_type="lifting_lug",
            calculation_type=check,
            clause="EN 13445-3 (attachments)",
            reason=(
                "Lifting-lug evaluation is not part of the EN 13445 route in this software; "
                f"{self._NO_ASME_FALLBACK}"
            ),
            status="out_of_scope",
        ) for check in (
            "lug_tension", "lug_shear", "lug_bearing", "lug_weld", "lug_shell_local_shear",
        )]

    def check_external_pressure(self, project) -> List[CalculationResult]:
        """EN dış basınç/vakum yolu.

        EN 13445-3 dış basınç için gereken eğri/veri paketi bu sürümde yoktur;
        hiçbir zaman ASME UG-28 değerleri kullanılmaz.
        """
        components = [
            *((s.section_id, "shell") for s in project.shell_sections),
            *((h.head_id, "head") for h in project.heads),
        ]
        if not components:
            return [self._unsupported_result(
                component_type="system",
                calculation_type="external_pressure",
                clause="EN 13445-3, Part 8",
                reason="No shell/head component was supplied for EN external-pressure review.",
            )]
        return [self._unsupported_result(
            component_id=component_id,
            component_type=component_type,
            calculation_type="external_pressure",
            clause="EN 13445-3, Part 8",
            reason=(
                "EN 13445 external-pressure/vacuum chart data and stiffening-ring "
                "verification are not implemented; result is not usable for design."
            ),
        ) for component_id, component_type in components]

    def check_load_combinations(self, project) -> List[CalculationResult]:
        """EN yük kombinasyonlarını sessizce yok saymak yerine işaretle."""
        if not project.load_combinations:
            return []
        results = []
        known_cases = {case.load_case_id for case in project.load_cases}
        for combination in project.load_combinations:
            result = self._unsupported_result(
                component_id=combination.combination_id,
                component_type="load_combination",
                calculation_type="load_combination",
                clause="EN 13445-3, 5 / EN 13445-3, 16",
                reason=(
                    "EN load-combination stress evaluation is not implemented; "
                    "this combination must be independently reviewed."
                ),
            )
            result.input_snapshot = {
                "combination_id": combination.combination_id,
                "load_case_ids": list(combination.load_case_ids),
                "load_factors": dict(combination.load_factors),
                "missing_load_case_ids": sorted(set(combination.load_case_ids) - known_cases),
                "standard": combination.standard,
                "standard_edition": combination.standard_edition,
            }
            results.append(result)
        return results

    def calculate_flange(self, input_data: dict) -> CalculationResult:
        """EN flange calculation is deliberately not routed through ASME Appendix 2."""
        flange = input_data.get("flange")
        component_id = getattr(flange, "flange_id", "") if flange is not None else ""
        return self._unsupported_result(
            component_id=component_id,
            component_type="flange",
            calculation_type="flange",
            clause="EN 13445-3, 11",
            reason="EN 13445 flange design is not implemented in this release; no ASME fallback is permitted.",
        )

    def calculate_fatigue(self, input_data: dict) -> CalculationResult:
        """EN fatigue için kontrollü sınır.

        Çevrim ve malzeme yorulma verisi olmadan sonuç üretmek yerine eksik
        girdiyi bloklar; veri verilse bile yöntem henüz tasarım sonucu üretmez.
        """
        result = self._unsupported_result(
            component_id=str(input_data.get("component_id", "")),
            component_type="system",
            calculation_type="fatigue",
            clause="EN 13445-3, 18",
            reason="EN fatigue curves and cycle-by-cycle assessment are not implemented.",
        )
        result.input_snapshot = {
            "design_cycles": input_data.get("design_cycles"),
            "material_fatigue_data": input_data.get("material_fatigue_data"),
        }
        if not input_data.get("design_cycles") or not input_data.get("material_fatigue_data"):
            result.status = CalculationStatus.BLOCKED_MISSING_INPUT
            result.add_warning("Design cycles and EN material fatigue data are required before fatigue assessment.")
        return result


__all__ = ["EN13445DesignCode"]
