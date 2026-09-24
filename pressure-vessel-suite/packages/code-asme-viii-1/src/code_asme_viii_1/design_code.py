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

# ASME "flanged and dished" (F&D) standart bombe geometrisi: taç yarıçapı = çap,
# büküm yarıçapı = taç yarıçapının %6'sı. UG-32(e) asgarisi de %6'dır.
ASME_FD_KNUCKLE_RATIO = 0.06


def _torispherical_radii(head, D: float, result: CalculationResult) -> tuple[float, float]:
    """Torisferik bombe için taç (L) ve büküm (r) yarıçaplarını çöz.

    Kullanıcı değer vermediyse **standart ASME F&D** geometrisi varsayılır:
    `L = D`, `r = 0.06 L`. Varsayım sessiz DEĞİLDİR — K4 gereği ara değer,
    varsayım ve uyarı olarak kaydedilir.

    Eski varsayılan `r = D/10` idi ve standart %6 bombeye kıyasla **%13 daha ince**
    kalınlık üretiyordu: daha büyük büküm yarıçapı → daha küçük M → daha ince
    bombe. Fiziksel bombe %6 bükümlüyse bu emniyetsiz taraftadır.
    Bkz. docs/validation/asme-worked-examples.md V-12.
    """
    if getattr(head, "torispherical_geometry", "standard_asme_fd") == "custom":
        if not head.crown_radius or not head.knuckle_radius:
            raise ValueError("Özel torisferik geometri için crown_radius ve knuckle_radius zorunludur")
        return head.crown_radius, head.knuckle_radius

    # F&D taç yarıçapı dış geometriye göre tanımlanır. `D` çağıran tarafta
    # korozyonlu iç çap olduğundan onu kullanmak geometriyi ve gerekli et
    # kalınlığını emniyetsiz yönde az miktarda saptırabilir. Dış çap açıkça
    # verilmişse onu kullan; yoksa nominal etten as-built dış çapı türet.
    outside_diameter = head.outside_diameter or (
        head.inside_diameter + 2.0 * head.nominal_thickness
    )
    L = head.crown_radius if head.crown_radius else outside_diameter
    if not head.crown_radius:
        result.add_assumption(
            f"K4: Taç yarıçapı girilmedi; standart ASME F&D varsayıldı "
            f"(L = dış çap = {L:.1f} mm)."
        )

    r = head.knuckle_radius if head.knuckle_radius else ASME_FD_KNUCKLE_RATIO * L
    if not head.knuckle_radius:
        result.add_assumption(
            f"K4: Büküm yarıçapı girilmedi; standart ASME F&D varsayıldı "
            f"(r = 0.06 L = {r:.1f} mm). Bombenin gerçek bükümü daha büyükse hesap "
            f"muhafazakâr, daha küçükse UG-32(e) asgarisi ihlal edilmiş demektir."
        )
        result.add_warning(
            "Büküm yarıçapı imalat çiziminden girilmelidir — varsayılan %6 (ASME F&D) "
            "kullanıldı. Bu değer gerekli kalınlığı doğrudan etkiler."
        )

    # UG-32(e) geometrik asgarileri — sessizce düzeltilmez, uyarı verilir (K4).
    if r < ASME_FD_KNUCKLE_RATIO * L:
        result.add_warning(
            f"UG-32(e): Büküm yarıçapı r = {r:.1f} mm, taç yarıçapının %6'sının "
            f"({ASME_FD_KNUCKLE_RATIO * L:.1f} mm) altında. Madde asgarisi sağlanmıyor."
        )

    return L, r


class ASMEVIII1DesignCode(DesignCode):
    """ASME VIII Division 1 hesap eklentisi.

    Uygulanan maddeler:
    - UG-27: Silindirik gövde, iç basınç
    - UG-32: Bombeler (ellipsoidal, torispherical, hemispherical)
    - UG-99: Hidrostatik test basıncı
    """

    def __init__(self, edition: str = "2025"):
        self._edition = edition

    def _apply_ug16b_minimum(
        self, result: CalculationResult, nominal_thickness: float, corrosion_allowance: float
    ) -> None:
        """UG-16(b) — mutlak minimum kalınlık kontrolü (korozyon payı hariç).

        Basınçtan gelen gerekli kalınlık hesabı bağımsız bir kontroldür; bu
        onun yerine geçmez, üstüne eklenir. Seçilen (nominal) kalınlıktan
        korozyon payı düşüldüğünde kalan net kalınlık, malzeme veya basınçtan
        bağımsız olarak 1.5 mm'nin altına düşemez (ASME VIII-1 UG-16(b)).
        Ana kalınlık kontrolü PASS olsa bile bu ihlal sonucu FAIL'e çevirir —
        sessizce görmezden gelinmez (K4).
        """
        if not nominal_thickness or nominal_thickness <= 0:
            return  # Zaten NOT_CALCULATED — burada tekrar değerlendirmeye gerek yok.
        net_thickness = nominal_thickness - corrosion_allowance
        if net_thickness >= formulas.UG16B_MINIMUM_THICKNESS_MM:
            return
        result.add_warning(
            f"UG-16(b): Seçilen kalınlık, korozyon payı düşüldükten sonra "
            f"{net_thickness:.2f} mm — ASME VIII-1 mutlak minimum "
            f"{formulas.UG16B_MINIMUM_THICKNESS_MM} mm'nin altında."
        )
        if result.status == CalculationStatus.PASS:
            result.set_fail(result.utilization_ratio or 1.0)

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

        # Korozyonlu iç yarıçap — UG-27'nin R'si "korozyonlu durumdaki iç yarıçap"tır.
        # İç korozyon metali İÇ yüzeyden yer, yani iç yarıçap BÜYÜR: R_c = R + C.
        # (Dış ölçüler değişmez.) Doğrulama: yayınlanmış vakada Do=86", t=1.000",
        # C=0.125" için referans yazılım R = 42.125" = 42.000" + C kullanıyor —
        # bkz. docs/validation/asme-worked-examples.md V-16.
        R_corroded = R + C

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
                P=P, R=R_corroded, S=S, E=E
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
        # K4: Negatif sac toleransı girilmediyse sektör tipiği varsayılır.
        # Değer makul ama sonucu ~%12.5 etkiler — sessiz kalmaz.
        if shell.mill_tolerance > 0:
            mt_factor = 1.0 - shell.mill_tolerance / 100.0
        else:
            mt_factor = 0.875
            result.add_assumption(
                "K4: Negatif sac toleransı girilmedi; "
                f"varsayılan {(1 - 0.875) * 100:.1f}% kullanıldı."
            )
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
        self._apply_ug16b_minimum(result, shell.nominal_thickness, C)

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
        S = mat.allowable_stress
        C = head.internal_corrosion_allowance

        # Korozyonlu iç ölçüler — UG-32 formülleri korozyonlu durumu ister.
        # İç korozyon iç yüzeyden metal yediği için iç çap BÜYÜR: D_c = D + 2C.
        # Bkz. gövde hesabındaki aynı gerekçe ve V-16.
        D = head.inside_diameter + 2 * C
        R = D / 2.0

        result.input_snapshot = {
            "P_MPa": P,
            "D_new_mm": head.inside_diameter,
            "D_corroded_mm": D,
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
                if head.crown_depth:
                    t, K = formulas.head_elliptical_thickness_general(P, D, head.crown_depth, S, E)
                else:
                    t, K = formulas.head_elliptical_thickness(P, D, S, E)
                result.add_intermediate("K_factor", K, "-", "2:1 elliptical head factor")
                result.add_intermediate("t_required", t, "mm", "Required thickness")

            elif head.type == HeadType.TORISPHERICAL:
                result.clause_reference = "UG-32(e)"
                result.formula_reference = "UG-32(e)"
                L, r = _torispherical_radii(head, D, result)
                t, M = formulas.head_torispherical_thickness_full(P, L, r, S, E)
                result.add_intermediate("L", L, "mm", "Crown radius")
                result.add_intermediate("r", r, "mm", "Knuckle radius")
                result.add_intermediate("M_factor", M, "-", "M factor")
                result.add_intermediate("t_required", t, "mm", "Required thickness")

            elif head.type == HeadType.HEMISPHERICAL:
                result.clause_reference = "UG-32(f)"
                result.formula_reference = "UG-32(f)"
                t = formulas.head_hemispherical_thickness(P, R, S, E)
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
                # `D` yukarıda zaten korozyonlu çapa çevrildi (D_new + 2C).
                # CA=0.0 geçiliyor: korozyon payı aşağıdaki ortak
                # `shell_required_nominal_thickness` adımında BİR KEZ ekleniyor —
                # diğer bombe tipleriyle aynı desen. Eskiden hem burada hem orada
                # eklendiği için kalınlık %5-25 fazla çıkıyordu (V-17).
                if head.flat_z_factor is not None:
                    t = formulas.flat_head_thickness_non_circular(
                        P, D, S, E, C_attach, head.flat_z_factor, CA=0.0
                    )
                    result.clause_reference = "UG-34(c)(3)"
                    result.formula_reference = "UG-34(c)(3)"
                else:
                    t = formulas.flat_head_thickness(P, D, S, E, C_attach, CA=0.0)
                result.add_intermediate("C_attach", C_attach, "-", "UG-34 attachment factor")
                result.add_intermediate("d_corroded", D, "mm", "Corroded diameter")
                result.add_intermediate("t_required", t, "mm", "Required thickness")
            else:
                result.set_not_calculated(f"Unknown head type: {head.type}")
                return result

        except ValueError as e:
            result.set_not_calculated(str(e))
            return result

        # Nominal kalınlık
        # K4: Negatif sac toleransı girilmediyse sektör tipiği varsayılır.
        # Değer makul ama sonucu ~%12.5 etkiler — sessiz kalmaz.
        if head.mill_tolerance > 0:
            mt_factor = 1.0 - head.mill_tolerance / 100.0
        else:
            mt_factor = 0.875
            result.add_assumption(
                "K4: Negatif sac toleransı girilmedi; "
                f"varsayılan {(1 - 0.875) * 100:.1f}% kullanıldı."
            )
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
        self._apply_ug16b_minimum(result, head.nominal_thickness, C)

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
                "component_type": "shell" | "head" | "cone",
                "component": ShellSection | Head | Cone,
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

        # Bileşen kimliği — gövde/bombe/koni farklı alan adları kullanıyor.
        component_id = next(
            (getattr(component, attr) for attr in ("section_id", "head_id", "cone_id")
             if hasattr(component, attr)),
            "",
        )
        result = CalculationResult(
            component_id=component_id,
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
                # Korozyonlu iç yarıçap (bkz. calculate_shell_thickness, V-16).
                R = R + C
                result.clause_reference = "UG-27(c)(1)"
                mawp = formulas.mawp_from_shell(R, t_actual, S, E, C)
                result.add_intermediate("R", R, "mm", "Corroded inside radius")
                result.add_intermediate("t_actual", t_actual, "mm", "Actual thickness")
                result.add_intermediate("C", C, "mm", "Corrosion allowance")
                result.add_intermediate("t_corroded", t_actual - C, "mm", "Corroded thickness")

            elif comp_type == "cone":
                # Koni MAWP'i eskiden HİÇ hesaplanmıyordu: `cone_mawp` yazılmıştı
                # ama hiçbir yerden çağrılmıyordu. Global MAWP = min(tüm MAWP'ler)
                # olduğu için sınırlayıcı bir konik geçiş sessizce görünmüyordu —
                # hem MAWP hem de ona dayanan test basıncı yüksek çıkıyordu. V-19.
                cone = component
                D = cone.large_diameter + 2 * C  # korozyonlu iç çap (V-16)
                result.clause_reference = "UG-32(g)"
                mawp = formulas.cone_mawp(D, t_actual, S, E, cone.half_apex_angle, C)
                result.add_intermediate("D_large_corroded", D, "mm", "Corroded large diameter")
                result.add_intermediate("alpha_deg", cone.half_apex_angle, "deg", "Half apex angle")
                result.add_intermediate("t_actual", t_actual, "mm", "Actual thickness")

            elif comp_type == "head":
                from domain.enums import HeadType
                head = component
                # Korozyonlu iç çap (bkz. calculate_head_thickness, V-16).
                D = head.inside_diameter + 2 * C
                if head.type == HeadType.ELLIPTICAL:
                    result.clause_reference = "UG-32(d)"
                    mawp = formulas.mawp_from_ellipsoidal_head(D, t_actual, S, E, C)
                elif head.type == HeadType.TORISPHERICAL:
                    result.clause_reference = "UG-32(e)"
                    L, r = _torispherical_radii(head, D, result)
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

    @staticmethod
    def _governing_test_material(input_data: dict, materials: list):
        """Liste sırası yerine bağlı basınç taşıyan malzemeyi belirle."""
        project = input_data.get("project")
        if project is None:
            candidates = list(materials)
        else:
            material_ids = {
                component.material_id
                for collection in (project.shell_sections, project.heads, project.cones)
                for component in collection
            }
            candidates = [material for material in materials if material.material_id in material_ids]
            if not candidates:
                candidates = list(materials)
        return min(candidates, key=lambda material: material.allowable_stress)

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
        mat = self._governing_test_material(input_data, materials)
        S_design = mat.allowable_stress

        # V1'de test sıcaklığındaki gerilme = tasarım sıcaklığındaki gerilme varsayımı
        # (daha düşük sıcaklık → genellikle daha yüksek gerilme → ratio ≥ 1.0)
        S_test = S_design  # Konservatif varsayım

        result.add_assumption(
            f"K4: Test temperature allowable stress = design temperature allowable stress "
            f"({S_design} MPa). Ratio = 1.0 (conservative). Governing material: {mat.material_id}."
        )

        # UG-99(b) tabanı MAWP'dir. Endnote yalnızca MAWP hesaplanmadığında tasarım
        # basıncına izin verir; bu suite MAWP'yi hesapladığı için taban MAWP olmalı.
        # MAWP ≥ P_tasarım olduğundan, tasarım basıncına düşmek Kod'un istediğinden
        # DÜŞÜK test basıncı üretir (emniyetsiz yön) — bu yüzden K4 varsayımı yazılır.
        P_design = dc.design_pressure
        global_mawp = input_data.get("global_mawp")
        if global_mawp is not None and global_mawp > 0:
            pressure_basis = global_mawp
            basis_label = "MAWP"
        else:
            pressure_basis = P_design
            basis_label = "P_design"
            result.add_assumption(
                "K4: MAWP hesaplanamadığı için UG-99(b) tabanı olarak tasarım basıncı "
                f"({P_design} MPa) kullanıldı (UG-99(b) endnote muafiyeti). MAWP "
                "hesaplanabilseydi test basıncı daha yüksek çıkardı — bu değer "
                "Kod'un asgarisinin altında kalabilir."
            )
            result.add_warning(
                "Test basıncı MAWP yerine tasarım basıncından türetildi; MAWP "
                "hesaplanabilir hale geldiğinde yeniden hesaplanmalıdır."
            )

        p_test = formulas.hydrotest_pressure_asme(pressure_basis, S_test, S_design)

        result.input_snapshot = {
            "pressure_basis_MPa": pressure_basis,
            "pressure_basis_type": basis_label,
            "P_design_MPa": P_design,
            "S_test_MPa": S_test,
            "S_design_MPa": S_design,
            "hydrotest_temperature_C": dc.hydrotest_temperature,
        }

        result.add_intermediate(
            "pressure_basis", pressure_basis, "MPa",
            f"UG-99(b) pressure basis ({basis_label})",
        )
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

        mat = self._governing_test_material(input_data, materials)
        S_design = mat.allowable_stress
        S_test = S_design  # Konservatif varsayım (hidrotest ile aynı)

        result.add_assumption(
            f"K4: Test temperature allowable stress = design temperature allowable stress "
            f"({S_design} MPa). Ratio = 1.0 (conservative). Governing material: {mat.material_id}."
        )

        # UG-100 tabanı da MAWP'dir — UG-99(b) ile aynı gerekçe.
        P_design = dc.design_pressure
        global_mawp = input_data.get("global_mawp")
        if global_mawp is not None and global_mawp > 0:
            pressure_basis = global_mawp
            basis_label = "MAWP"
        else:
            pressure_basis = P_design
            basis_label = "P_design"
            result.add_assumption(
                "K4: MAWP hesaplanamadığı için UG-100 tabanı olarak tasarım basıncı "
                f"({P_design} MPa) kullanıldı. Kod'un asgarisinin altında kalabilir."
            )

        p_test = formulas.pneumatic_test_pressure(pressure_basis, S_test, S_design)

        result.input_snapshot = {
            "pressure_basis_MPa": pressure_basis,
            "pressure_basis_type": basis_label,
            "P_design_MPa": P_design,
            "S_test_MPa": S_test,
            "S_design_MPa": S_design,
            "test_temperature_C": dc.hydrotest_temperature,
        }

        result.add_intermediate(
            "pressure_basis", pressure_basis, "MPa",
            f"UG-100 pressure basis ({basis_label})",
        )
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
            nozzle_inclination_angle=nozzle.inclination_angle,
        )
        return build_reinforcement_calculation_result(inp)

    def calculate_flange(self, input_data: dict) -> CalculationResult:
        """Appendix 2 flanş stres rotası; B16 rating hesabından ayrıdır."""
        try:
            from flanges import FlangeCalculator
        except ImportError:
            return super().calculate_flange(input_data)
        flange = input_data["flange"]
        mat = next((m for m in input_data.get("materials", [])
                    if m.material_id == flange.material_id), None)
        if mat is None:
            return FlangeCalculator(self.code_name, self.code_edition).check_flange_stress({
                "flange": {"tag": flange.flange_id, "material_id": flange.material_id},
                "design_conditions": input_data["design_conditions"], "materials": [],
            })
        # M, bolt load and Y/f are deliberately explicit: no silent Appendix 2 factors.
        payload = {
            "flange": {"tag": flange.flange_id, "type": flange.type,
                       "A": flange.outside_diameter, "B": flange.inside_diameter,
                       "t": flange.thickness, "g1": flange.hub_small_thickness,
                       "h0": flange.hub_length, "material_id": flange.material_id},
            "design_conditions": input_data["design_conditions"],
            "materials": input_data.get("materials", []),
            "bolt_load_W": input_data.get("bolt_load_W", 0.0),
            "moment_M": input_data.get("moment_M", 0.0),
        }
        if input_data.get("flange_factor_Y") is not None:
            payload["flange_factor_Y"] = input_data["flange_factor_Y"]
        if input_data.get("flange_factor_f") is not None:
            payload["flange_factor_f"] = input_data["flange_factor_f"]
        return FlangeCalculator(self.code_name, self.code_edition).check_flange_stress(payload)

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
            linked_components = [
                component
                for collection in (project.shell_sections, project.heads, project.cones)
                for component in collection
                if component.weld_joint_id == weld.joint_id
            ]
            comp_thickness = max(
                (component.nominal_thickness for component in linked_components),
                default=0.0,
            )
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
        """Nozul çakışma/geometri kontrolleri (nozzles paketine delege eder).

        Nozul-bazlı kontrollere ek olarak, proje-seviyesi UG-46 muayene
        açıklığı kontrolünü de aynı gruba ekler (bkz. `check_inspection_opening`).
        """
        try:
            from nozzles import build_clash_check_result, check_inspection_opening
        except ImportError:
            return []

        results = [build_clash_check_result(nozzle, project) for nozzle in project.nozzles]
        results.append(check_inspection_opening(project))
        return results

    def check_mdmt(self, project) -> list:
        """MDMT/UCS-66 kontrolü (mdmt paketine delege eder).

        Her basınç taşıyan bileşen için ayrı kontrol. Malzemede UCS-66 eğri grubu
        girilmemişse `MDMTCalculator` `BLOCKED_MISSING_INPUT` döndürür — eğri
        grubu **tahmin edilmez** (K4). Eğri ataması malzeme belgesinden okunur.
        """
        try:
            from mdmt import MDMTCalculator, UCS66CurveGroup
        except ImportError:
            return []

        calc = MDMTCalculator(code=self.code_name, edition=self.code_edition)
        materials = project.materials
        results = []

        by_key = {
            **{("shell", c.section_id): c for c in project.shell_sections},
            **{("head", c.head_id): c for c in project.heads},
            **{("cone", c.cone_id): c for c in project.cones},
        }
        sequence = getattr(project, "component_sequence", None) or []
        unresolved_refs = []
        if sequence:
            declared_keys = [
                *(('shell', c.section_id) for c in project.shell_sections),
                *(('head', c.head_id) for c in project.heads),
                *(('cone', c.cone_id) for c in project.cones),
            ]
            sequence_keys = [(ref.component_type, ref.component_id) for ref in sequence]
            declared_counts = {key: declared_keys.count(key) for key in set(declared_keys)}
            sequence_counts = {key: sequence_keys.count(key) for key in set(sequence_keys)}
            for key, expected_count in declared_counts.items():
                actual_count = sequence_counts.get(key, 0)
                if actual_count != expected_count:
                    issue = "missing from" if actual_count < expected_count else "duplicated in"
                    unresolved_refs.append(f"{key[0]}:{key[1]} {issue} component_sequence")
            components = []
            for ref in sequence:
                component = by_key.get((ref.component_type, ref.component_id))
                if component is None:
                    unresolved_refs.append(f"{ref.component_type}:{ref.component_id}")
                else:
                    components.append(component)
        else:
            components = list(project.shell_sections) + list(project.heads) + list(project.cones)
        for comp in components:
            group = None
            for m in materials:
                if m.material_id == comp.material_id:
                    raw = getattr(m, "ucs66_curve_group", None)
                    if raw:
                        try:
                            group = UCS66CurveGroup(raw)
                        except ValueError:
                            # Unknown material metadata must not abort all MDMT
                            # checks. None makes this component explicitly blocked.
                            group = None
                    break
            results.append(calc.check_mdmt({
                "component": comp,
                "design_conditions": project.design_conditions,
                "materials": materials,
                "curve_group": group,
                "nominal_thickness_mm": comp.nominal_thickness,
                "impact_test_temperature_C": getattr(
                    project.design_conditions, "impact_test_temperature_C", None
                ),
            }))

        calculated = [r for r in results if r.final_result is not None]
        if calculated or unresolved_refs:
            governing = max(calculated, key=lambda r: r.final_result, default=None)
            summary = CalculationResult(
                component_id="MDMT-GOVERNING",
                component_type="system",
                calculation_type="mdmt_check",
                code=self.code_name,
                edition=self.code_edition,
                clause_reference="UCS-66",
                formula_reference="UCS-66 governing component envelope",
            )
            complete = (
                not unresolved_refs
                and len(results) == len(components)
                and bool(components)
                and all(
                    r.final_result is not None
                    and r.status.value not in (
                        "BLOCKED MISSING INPUT", "BLOCKED CODE DATA",
                        "NOT CALCULATED", "OUT OF SCOPE",
                    )
                    for r in results
                )
            )
            # Yöneten değer adayını eksik/uygulanamaz bileşenler varken kap
            # sonucu gibi yayımlamayız. Aday, denetim için snapshot'ta kalır.
            summary.final_result = governing.final_result if complete and governing else None
            summary.final_result_unit = "°C"
            summary.allowable_limit = project.design_conditions.minimum_design_temperature
            summary.allowable_limit_unit = "°C"
            summary.input_snapshot = {
                "governing_component_id": governing.component_id if governing else None,
                "governing_component_type": governing.component_type if governing else None,
                "governing_material": governing.material_properties_used.get("designation", "") if governing else "",
                "provisional_governing_mdmt_C": governing.final_result if governing else None,
                "component_count": len(components),
                "unresolved_component_references": unresolved_refs,
                "minimum_design_temperature_C": project.design_conditions.minimum_design_temperature,
            }
            if governing:
                summary.add_intermediate(
                    "governing_mdmt", governing.final_result, "°C",
                    "Highest component MDMT limit"
                )
                summary.add_intermediate(
                    "governing_component_id", governing.component_id, "-",
                    "Component controlling the MDMT envelope"
                )
                summary.add_intermediate(
                    "governing_material", governing.material_properties_used.get("designation", ""), "-",
                    "Material controlling the MDMT envelope"
                )
            summary.add_assumption(
                "Governing MDMT is the highest component UCS-66 limit; all component checks remain traceable above."
            )
            if unresolved_refs or any(
                r.final_result is None or r.status.value in (
                    "BLOCKED MISSING INPUT", "BLOCKED CODE DATA",
                    "NOT CALCULATED", "OUT OF SCOPE",
                ) for r in results
            ):
                summary.set_blocked_missing_input(
                    "Governing MDMT cannot be confirmed: at least one pressure-bearing component "
                    "is unresolved, lacks UCS-66 input, or has no applicable calculation. "
                    "The candidate value is retained for review only."
                )
            elif governing and governing.status.value == "FAIL":
                summary.set_fail()
            else:
                summary.set_review_required(
                    "Governing MDMT envelope is preliminary until UCS-66 chart verification is completed."
                )
            summary.governing = True
            results.append(summary)

        return results

    def check_junctions(self, project) -> list:
        """Appendix 1-4/1-5 koni ucu bağlantıları için kapsam ve girdi iskeleti.

        Bu metot geometri/topoloji girdilerini kontrol edip raporlar. Kodda
        birleşim gerilmesi çözümü olmadığı için tam girdilerde de sayısal
        yeterlilik sonucu üretmez.
        """
        results = []
        component_maps = {
            "shell": {s.section_id: s for s in getattr(project, "shell_sections", [])},
            "head": {h.head_id: h for h in getattr(project, "heads", [])},
            "cone": {c.cone_id: c for c in getattr(project, "cones", [])},
        }
        sequence = getattr(project, "component_sequence", None) or []

        for junction in getattr(project, "junctions", []) or []:
            result = CalculationResult(
                component_id=junction.junction_id,
                component_type="junction",
                calculation_type="junction_check",
                code=self.code_name,
                edition=self.code_edition,
                clause_reference="Appendix 1-4/1-5",
                formula_reference="Cone junction input envelope",
            )
            result.input_snapshot = junction.model_dump(mode="json")
            result.add_intermediate("left_component_id", junction.left_component_id, "-", "Sol bağlantı bileşeni")
            result.add_intermediate("right_component_id", junction.right_component_id, "-", "Sağ bağlantı bileşeni")
            result.add_intermediate("junction_type", junction.junction_type, "-", "Birleşim tipi")
            result.add_intermediate("cone_end", junction.cone_end or "", "-", "Açıkça beyan edilen koni ucu")
            result.add_intermediate("weld_joint_id", junction.weld_joint_id or "", "-", "Birleşim kaynak kimliği")
            result.add_intermediate("weld_efficiency", junction.weld_efficiency, "-", "Beyan edilen kaynak verimi")
            result.add_intermediate("large_end_diameter", junction.large_end_diameter, "mm", "Beyan edilen büyük uç çapı")
            result.add_intermediate("small_end_diameter", junction.small_end_diameter, "mm", "Beyan edilen küçük uç çapı")
            result.add_intermediate("knuckle_radius_mm", junction.knuckle_radius_mm, "mm", "Beyan edilen geçiş büküm yarıçapı")

            def resolve_type(component_id):
                sequence_types = {
                    ref.component_type for ref in sequence
                    if ref.component_id == component_id
                }
                if sequence_types:
                    return next(iter(sequence_types)) if len(sequence_types) == 1 else None
                matches = [kind for kind, items in component_maps.items() if component_id in items]
                return matches[0] if len(matches) == 1 else None

            left_type = resolve_type(junction.left_component_id)
            right_type = resolve_type(junction.right_component_id)
            left_obj = component_maps.get(left_type, {}).get(junction.left_component_id)
            right_obj = component_maps.get(right_type, {}).get(junction.right_component_id)
            for side, component_id, component_type, component in (
                ("left", junction.left_component_id, left_type, left_obj),
                ("right", junction.right_component_id, right_type, right_obj),
            ):
                result.add_intermediate(f"{side}_component_type", component_type or "unknown", "-", "Zincirdeki bileşen tipi")
                if component is None:
                    result.add_validity_check(f"{side}_component_resolves", False, actual=component_id)
                else:
                    result.add_validity_check(f"{side}_component_resolves", True, actual=component_id)

            if left_type == "cone" and junction.left_component_id in component_maps["cone"]:
                cone = component_maps["cone"][junction.left_component_id]
            elif right_type == "cone" and junction.right_component_id in component_maps["cone"]:
                cone = component_maps["cone"][junction.right_component_id]
            else:
                cone = None
            if cone:
                result.add_intermediate("cone_component_id", cone.cone_id, "-", "Birleşime bağlı koni")
                result.add_intermediate("cone_large_diameter", cone.large_diameter, "mm", "Koni büyük uç iç çapı")
                result.add_intermediate("cone_small_diameter", cone.small_diameter, "mm", "Koni küçük uç iç çapı")
                result.add_intermediate("cone_half_apex_angle", cone.half_apex_angle, "deg", "Koni yarı tepe açısı")
                result.add_intermediate("cone_nominal_thickness", cone.nominal_thickness, "mm", "Koni anma et kalınlığı")

            issues = []
            if not sequence:
                issues.append("component_sequence yok; iki bileşenin komşuluğu teyit edilemiyor")
            else:
                left_positions = [i for i, ref in enumerate(sequence)
                                  if ref.component_id == junction.left_component_id]
                right_positions = [i for i, ref in enumerate(sequence)
                                   if ref.component_id == junction.right_component_id]
                left_index = left_positions[0] if len(left_positions) == 1 else None
                right_index = right_positions[0] if len(right_positions) == 1 else None
                adjacent = (left_index is not None and right_index is not None
                            and abs(left_index - right_index) == 1)
                result.add_validity_check("components_are_adjacent", adjacent,
                                          actual=(left_index, right_index))
                if not adjacent:
                    issues.append("bağlanan bileşenler zincirde komşu değil veya zincirde bulunmuyor")

            expected_other_type = {"cone_to_shell": "shell", "cone_to_head": "head"}.get(junction.junction_type)
            if junction.junction_type == "shell_to_shell":
                result.add_validity_check("junction_type_in_cone_scope", False, actual=junction.junction_type)
            elif expected_other_type:
                endpoint_types = (left_type, right_type)
                type_ok = endpoint_types.count("cone") == 1 and endpoint_types.count(expected_other_type) == 1
                result.add_validity_check("junction_type_matches_endpoints", type_ok,
                                          actual=endpoint_types)
                if not type_ok:
                    issues.append(f"{junction.junction_type} tipi bir koni ve bir {expected_other_type} ucu gerektirir")
            if cone and junction.cone_end is None:
                issues.append("cone_end (large/small) açıkça belirtilmeli; yön zincir sırasından varsayılmıyor")
            if cone:
                declared_cone_diameters = (
                    ("large_end_diameter", junction.large_end_diameter, cone.large_diameter),
                    ("small_end_diameter", junction.small_end_diameter, cone.small_diameter),
                )
                for field_name, declared, actual in declared_cone_diameters:
                    if declared is not None and not math.isclose(declared, actual, rel_tol=1e-9, abs_tol=1e-6):
                        issues.append(
                            f"{field_name}={declared:g} mm koni girdisiyle uyuşmuyor ({actual:g} mm)"
                        )
                other = right_obj if left_type == "cone" else left_obj
                other_type = right_type if left_type == "cone" else left_type
                if other is not None and other_type in ("shell", "head"):
                    adjacent_diameter = other.inside_diameter
                    if adjacent_diameter is None and other_type == "shell" and other.outside_diameter is not None:
                        adjacent_diameter = other.outside_diameter - 2.0 * other.nominal_thickness
                    result.add_intermediate(
                        "adjacent_component_inside_diameter", adjacent_diameter, "mm",
                        "Komşu shell/head gerçek iç çapı"
                    )
                    if adjacent_diameter is None:
                        endpoint_ok = False
                        issues.append("komşu bileşenin iç çapı tanımlanmamış")
                    else:
                        matches_large = math.isclose(adjacent_diameter, cone.large_diameter, rel_tol=1e-6, abs_tol=0.01)
                        matches_small = math.isclose(adjacent_diameter, cone.small_diameter, rel_tol=1e-6, abs_tol=0.01)
                        endpoint_ok = (
                            (junction.cone_end == "large" and matches_large)
                            or (junction.cone_end == "small" and matches_small)
                        )
                    result.add_validity_check(
                        "cone_end_matches_adjacent_diameter", endpoint_ok,
                        actual={"cone_end": junction.cone_end, "adjacent_diameter_mm": adjacent_diameter},
                    )
                    if junction.cone_end is not None and not endpoint_ok:
                        issues.append("cone_end seçimi komşu bileşenin iç çapıyla uyuşmuyor")
            if cone and cone.half_apex_angle > 30 and junction.knuckle_radius_mm is None:
                issues.append("yarı tepe açısı 30° üzerinde; knuckle_radius_mm girdisi eksik")
            if junction.weld_joint_id is None:
                issues.append("weld_joint_id eksik; birleşim kaynağı bağlanmamış")
            elif not any(w.joint_id == junction.weld_joint_id for w in getattr(project, "welds", [])):
                issues.append(f"weld_joint_id '{junction.weld_joint_id}' projedeki kaynak listesinde bulunmuyor")
            if junction.weld_efficiency is None:
                issues.append("weld_efficiency eksik; birleşim kaynak verimi belirtilmemiş")
            if cone and cone.half_apex_angle > 30:
                result.add_warning(
                    "Koni yarı tepe açısı 30° üzerinde; geçiş detayının knuckle/torikonik "
                    "uygulanabilirliği mühendis incelemesi gerektirir."
                )
            if junction.analysis_status == "SUPPORTED":
                result.add_warning("analysis_status=SUPPORTED beyanı hesap kapsamını etkinleştirmez; solver bu sürümde uygulanmamıştır.")

            if junction.junction_type == "shell_to_shell":
                result.set_out_of_scope("shell_to_shell bu koni ucu kontrolü kapsamında değil.")
            elif issues:
                result.set_blocked_missing_input("Junction girdisi/topolojisi tamamlanmalı: " + "; ".join(issues))
            else:
                result.set_out_of_scope(
                    "Girdi ve bağlantı topolojisi kaydedildi. Appendix 1-4/1-5 koni ucu "
                    "gerilme/yeterlilik çözümü bu sürümde uygulanmadı; sayısal sonuç üretilmedi."
                )
            results.append(result)
        return results

    def check_supports(self, project) -> list:
        """Destek kontrolü (supports paketine delege eder).

        Ağırlık `calc_core.volume_mass` üzerinden hesaplanır — ayrı bir ağırlık
        girdisi istenmez (tek kaynak). Varsayılan **boş kap**; sıvı ağırlığı
        dahil edilmez ve bu varsayım sonuca yazılır (K4).
        """
        supports = getattr(project, "supports", None)
        if not supports:
            return []

        try:
            from supports import SupportCalculator
        except ImportError:
            return []
        from calc_core.volume_mass import calculate_vessel_volume_mass

        vm = calculate_vessel_volume_mass(project)
        weight_N = vm.total_metal_mass_kg * 9.80665

        calc = SupportCalculator(code=self.code_name, edition=self.code_edition)
        shells_by_id = {s.section_id: s for s in project.shell_sections}
        if not shells_by_id:
            results = []
            for sup in supports:
                r = CalculationResult(
                    component_id=sup.support_id,
                    component_type="support",
                    calculation_type=f"{sup.type}_stress",
                    code=self.code_name,
                    edition=self.code_edition,
                )
                r.set_not_calculated("Support checks require a resolvable host shell section.")
                results.append(r)
            return results

        def component_axial_length(ref):
            """Return an axial envelope for global support positions."""
            if ref.component_type == "shell":
                component = shells_by_id.get(ref.component_id)
                return component.tangent_length if component else None
            if ref.component_type == "cone":
                cone = next((c for c in project.cones if c.cone_id == ref.component_id), None)
                return cone.length if cone else None
            if ref.component_type == "head":
                head = next((h for h in project.heads if h.head_id == ref.component_id), None)
                return (head.crown_depth or head.inside_diameter / 4.0) + head.straight_flange_length if head else None
            return None

        def shell_global_start(shell_id):
            sequence = getattr(project, "component_sequence", None) or []
            if not sequence:
                # A legacy single-shell vessel has an unambiguous local origin.
                # With multiple shells, an explicit host ID alone cannot map a
                # global station to that shell without the ordered chain.
                return 0.0 if len(shells_by_id) == 1 else None
            position = 0.0
            matches = 0
            start = None
            for ref in sequence:
                if ref.component_type == "shell" and ref.component_id == shell_id:
                    matches += 1
                    start = position
                length = component_axial_length(ref)
                if length is None:
                    return None
                position += length
            return start if matches == 1 else None

        saddles_by_host = {}
        for saddle in (s for s in supports if s.type == "saddle"):
            # Two Zick supports must act on the same shell section.
            saddle_host = getattr(saddle, "host_component_id", None)
            if saddle_host is None and len(shells_by_id) == 1:
                saddle_host = next(iter(shells_by_id))
            saddles_by_host.setdefault(saddle_host, []).append(saddle)
        results = []
        for sup in supports:
            host_id = getattr(sup, "host_component_id", None)
            if host_id:
                shell = shells_by_id.get(host_id)
                if shell is None:
                    r = CalculationResult(
                        component_id=sup.support_id,
                        component_type="support",
                        calculation_type=f"{sup.type}_stress",
                        code=self.code_name,
                        edition=self.code_edition,
                    )
                    r.set_not_calculated(f"Support host component '{host_id}' is not a shell section.")
                    results.append(r)
                    continue
            elif len(shells_by_id) == 1:
                shell = next(iter(shells_by_id.values()))
            else:
                r = CalculationResult(
                    component_id=sup.support_id,
                    component_type="support",
                    calculation_type=f"{sup.type}_stress",
                    code=self.code_name,
                    edition=self.code_edition,
                )
                r.set_not_calculated(
                    "Multiple shell sections exist; support.host_component_id is required."
                )
                results.append(r)
                continue

            host_start = shell_global_start(shell.section_id)
            if host_start is None:
                r = CalculationResult(
                    component_id=sup.support_id,
                    component_type="support",
                    calculation_type=f"{sup.type}_stress",
                    code=self.code_name,
                    edition=self.code_edition,
                )
                r.set_not_calculated(
                    f"Shell host '{shell.section_id}' cannot be resolved uniquely in component_sequence; "
                    "the sequence may contain missing, unknown, or duplicate component references."
                )
                results.append(r)
                continue

            host_end = host_start + shell.tangent_length
            if not (host_start <= sup.location_mm <= host_end):
                r = CalculationResult(
                    component_id=sup.support_id,
                    component_type="support",
                    calculation_type=f"{sup.type}_stress",
                    code=self.code_name,
                    edition=self.code_edition,
                )
                r.set_not_calculated(
                    f"Support position {sup.location_mm:g} mm is outside host shell "
                    f"'{shell.section_id}' global interval [{host_start:g}, {host_end:g}] mm."
                )
                results.append(r)
                continue

            manual_moment = getattr(sup, "overturning_moment_Nmm", 0.0) or 0.0
            global_moment = 0.0
            global_horizontal = 0.0
            for load_case in getattr(project, "load_cases", []) or []:
                for load in getattr(load_case, "external_loads", []) or []:
                    horizontal = math.hypot(load.fx_n, load.fy_n)
                    lever = max(0.0, (load.elevation_mm or 0.0) - sup.location_mm)
                    global_horizontal += horizontal
                    global_moment += horizontal * lever + abs(load.mx_nmm) + abs(load.my_nmm)
            overturning_moment = max(manual_moment, global_moment)
            payload = {
                "support": {
                    "tag": sup.support_id,
                    "host_component_id": shell.section_id,
                    "type": sup.type,
                    "location_mm": sup.location_mm,
                    "width_mm": sup.width_mm,
                    "height_mm": sup.height_mm,
                    "diameter_mm": getattr(sup, "diameter_mm", None),
                    "thickness_mm": getattr(sup, "thickness_mm", None),
                    "n_legs": getattr(sup, "leg_count", None),
                    "leg_diameter_mm": getattr(sup, "leg_diameter_mm", None),
                    "leg_thickness_mm": getattr(sup, "leg_thickness_mm", None),
                    "support_radius_mm": getattr(sup, "support_radius_mm", None),
                    "base_plate_area_mm2": getattr(sup, "base_plate_area_mm2", None),
                    "anchor_bolt_count": getattr(sup, "anchor_bolt_count", None),
                    "anchor_bolt_diameter_mm": getattr(sup, "anchor_bolt_diameter_mm", None),
                    "anchor_tension_allowable_N": getattr(sup, "anchor_tension_allowable_N", None),
                    "anchor_shear_allowable_N": getattr(sup, "anchor_shear_allowable_N", None),
                    "lateral_load_N": getattr(sup, "lateral_load_N", 0.0) or 0.0,
                    "contact_angle_deg": getattr(sup, "contact_angle_deg", None),
                },
                "shell": shell,
                "vessel_length": shell.tangent_length,
                "host_axial_start_mm": host_start,
                "total_weight_N": weight_N,
                "materials": project.materials,
                "design_conditions": project.design_conditions,
                "overturning_moment_Nmm": overturning_moment,
                "global_horizontal_load_N": global_horizontal,
                "global_overturning_moment_Nmm": global_moment,
                "skirt_material_id": sup.material_id,
            }
            if sup.type == "saddle":
                # İki eyer arası mesafe konumlardan türetilir; tek eyer varsa
                # Zick geçersizdir — hesap paketi bunu kendi raporlar.
                host_saddles = saddles_by_host.get(shell.section_id, [])
                if len(host_saddles) >= 2:
                    locs = sorted(s.location_mm for s in host_saddles)
                    payload["saddle_distance"] = locs[-1] - locs[0]
                    payload["saddle_from_end"] = max(0.0, locs[0] - host_start)
                r = calc.check_saddle(payload)
            elif sup.type == "skirt":
                r = calc.check_skirt(payload)
            elif sup.type == "leg":
                r = calc.check_leg_support(payload)
            else:
                continue

            r.add_intermediate("host_component_id", shell.section_id, "-", "Resolved support host shell")
            r.add_intermediate("host_axial_start", host_start, "mm", "Resolved host start on global vessel axis")
            r.add_intermediate("global_horizontal_load", global_horizontal, "N", "Resultant horizontal external load")
            r.add_intermediate("global_overturning_moment", global_moment, "N·mm", "External-load moment about support location")
            if global_moment > 0.0:
                r.add_assumption(
                    "Global support action derived from load-case external loads; "
                    "load combination and code-specific envelope review remains required."
                )
            r.add_assumption(
                f"K4: Destek yükü boş kap ağırlığından türetildi "
                f"({vm.total_metal_mass_kg:.0f} kg metal). Sıvı, izolasyon ve iç "
                f"ekipman ağırlıkları dahil DEĞİL."
            )
            if r.status == CalculationStatus.PASS:
                r.set_review_required(
                    "Destek fiziği Faz A'da yaklaşık kapsamda; skirt/leg/saddle sonuçları mühendis incelemesi ister."
                )
            if sup.type in ("skirt", "leg") and overturning_moment <= 0:
                r.add_assumption(
                    "Devirme momenti girilmedi (0 N·mm) — rüzgâr ve deprem yükleri "
                    "destek gerilmesine YANSITILMADI."
                )
            results.append(r)

        return results

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
        # A/B değerleri kullanıcıdan bileşen bazında alınır (gövde/bombe farklı
        # L/Do ve Do/t oranlarına sahip olduğu için tek bir proje-seviyesi çift
        # yanlış olurdu) — girilmemişse blokaj. Blokaj kararı artık uyarı
        # metnindeki "chart" kelimesine değil, doğrudan A/B değerine bakar;
        # metin değişse bile kilit davranışı bozulmaz.
        for shell in project.shell_sections:
            a_val = getattr(shell, "ug28_strain_factor_a", None) or 0.0
            b_val = getattr(shell, "ug28_allowable_stress_b", None) or 0.0
            r = calc.check_shell_external_pressure({
                "shell": shell,
                "design_conditions": dc,
                "materials": project.materials,
                "strain_factor_A": a_val,
                "allowable_stress_B": b_val,
            })
            if r.status == CalculationStatus.NOT_CALCULATED and (a_val <= 0 or b_val <= 0):
                r.set_blocked_code_data(
                    "UG-28 A/B faktörleri girilmedi. Geometri adımında gövde için "
                    "Şekil G ve malzeme çizelgesinden okunan değerleri girin "
                    "(K6: çizelge repoda tutulmaz)."
                )
            results.append(r)

        for head in project.heads:
            a_val = getattr(head, "ug28_strain_factor_a", None) or 0.0
            b_val = getattr(head, "ug28_allowable_stress_b", None) or 0.0
            r = calc.check_head_external_pressure({
                "head": head,
                "design_conditions": dc,
                "materials": project.materials,
                "strain_factor_A": a_val,
                "allowable_stress_B": b_val,
            })
            if r.status == CalculationStatus.NOT_CALCULATED and (a_val <= 0 or b_val <= 0):
                r.set_blocked_code_data(
                    "UG-33 A/B faktörleri girilmedi. Geometri adımında bombe için "
                    "Şekil G ve malzeme çizelgesinden okunan değerleri girin "
                    "(K6: çizelge repoda tutulmaz)."
                )
            results.append(r)

        # No cone external-pressure solver is implemented. Retain per-component
        # applicability so cones do not disappear from review for vacuum cases.
        for cone in project.cones:
            r = CalculationResult(
                component_id=cone.cone_id,
                component_type="cone",
                calculation_type="external_pressure",
                code=self.code_name,
                edition=self.code_edition,
                clause_reference="UG-28",
                formula_reference="Cone external-pressure applicability",
            )
            r.set_out_of_scope(
                "Conical-section external-pressure stability is not implemented; "
                "no allowable or PASS result is reported."
            )
            r.input_snapshot = {
                "external_pressure_MPa": external_pressure,
                "vacuum_condition": bool(dc.vacuum_condition),
                "cone_id": cone.cone_id,
            }
            results.append(r)

        # Vakum kontrolü
        if dc.vacuum_condition:
            for vshell in project.shell_sections:
                a_val = getattr(vshell, "ug28_strain_factor_a", None) or 0.0
                b_val = getattr(vshell, "ug28_allowable_stress_b", None) or 0.0
                r = calc.check_vacuum_stability({
                    "shell": vshell,
                    "design_conditions": dc,
                    "materials": project.materials,
                    "strain_factor_A": a_val,
                    "allowable_stress_B": b_val,
                })
                if r.status == CalculationStatus.NOT_CALCULATED and (a_val <= 0 or b_val <= 0):
                    r.set_blocked_code_data(
                        "Vakum stabilite kontrolü için UG-28 A/B faktörleri girilmedi "
                        "(K6: çizelge repoda tutulmaz)."
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
        S = mat.allowable_stress
        C = cone.internal_corrosion_allowance
        # Korozyonlu iç çap (bkz. calculate_shell_thickness, V-16).
        D = cone.large_diameter + 2 * C
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
        # K4: Negatif sac toleransı girilmediyse sektör tipiği varsayılır.
        # Değer makul ama sonucu ~%12.5 etkiler — sessiz kalmaz.
        if cone.mill_tolerance > 0:
            mt_factor = 1.0 - cone.mill_tolerance / 100.0
        else:
            mt_factor = 0.875
            result.add_assumption(
                "K4: Negatif sac toleransı girilmedi; "
                f"varsayılan {(1 - 0.875) * 100:.1f}% kullanıldı."
            )
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
        self._apply_ug16b_minimum(result, cone.nominal_thickness, C)

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "source_reference": mat.source_reference,
        }

        return result


__all__ = ["ASMEVIII1DesignCode"]
