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

TORI_CLAUSE = "EN 13445-3, 7.5.3"
# E04 madde düzeltmesi: eski "5.4.2 / 5.5.x" numaraları EN 13445-3'te bu konuların maddesi
# değildi; iç basınç kabukları Madde 7'dedir (7.4.2 silindir, 7.5.2 yarım küre, 7.5.4
# elipsoidal). Numaralar bellekten; lisanslı metinle doğrulanmadı (verified=False).
SHELL_CLAUSE = "EN 13445-3, 7.4.2"
HEMI_CLAUSE = "EN 13445-3, 7.5.2"
ELLIP_CLAUSE = "EN 13445-3, 7.5.4"
ELLIP_FORMULA_NOTE = "K = Di/(2hi); R = Di(0,44K+0,02), r = Di(0,5/K−0,08) → 7.5.3 es/ey/eb, β"
Z_CLAUSE = "EN 13445-3, 5.6"
STRESS_CLAUSE = "EN 13445-3, 6"
HYDRO_CLAUSE = "EN 13445-5, 10.2.3.3.1"
PNEU_CLAUSE = "EN 13445-5, 10.2.3.3 (pnömatik; alt madde no doğrulanmadı)"
RELIEF_CLAUSE = "EN 13445 kapsamı dışı — tahliye: EN ISO 4126 / EN 764-7 (madde no doğrulanmadı)"


def _torispherical_radii_en(head, Di: float, C: float, result: CalculationResult):
    """E03: EN torisferik bombe için korozyonlu taç (R) ve büküm (r) iç yarıçapları.

    B-09 kaldırıldı: büküm yarıçapı artık varsayılmaz (eski r = 0,10·D Korbbogen
    varsayımı yok). r girilmezse hesap BLOCKED_MISSING_INPUT olur ve None döner.
    Taç yarıçapı girilmezse R = Di (7.5.3.1 R ≤ De sınırına yakın, ey/eb'yi
    büyüten muhafazakâr seçim) varsayımı kayda geçer (K4).
    İç korozyon iç yüzeyden metal yer → R ve r, C kadar büyür (V-16).
    """
    if not head.knuckle_radius:
        result.set_blocked_missing_input(
            f"{TORI_CLAUSE}: büküm yarıçapı (knuckle_radius) girilmedi. EN tam prosedürü "
            "(β, ey, eb, uygulanabilirlik) r'ye doğrudan bağlıdır; varsayılan atanmaz "
            "(eski B-09 r = 0,10·D varsayımı kaldırıldı). İmalat çiziminden girin."
        )
        return None
    if head.crown_radius:
        R0 = head.crown_radius
    else:
        R0 = head.inside_diameter
        result.add_assumption(
            f"K4: Taç yarıçapı girilmedi; R = Di = {R0:.1f} mm varsayıldı (muhafazakâr)."
        )
    return R0 + C, head.knuckle_radius + C


def _tori_outside_diameter(head, nominal: float) -> float:
    return head.outside_diameter if head.outside_diameter else head.inside_diameter + 2.0 * nominal


def _ellipsoidal_radii_en(head, Dc: float, result: CalculationResult):
    """E06: EN 13445-3, 7.5.4 — elipsoidal bombe → eşdeğer torisferik (R, r).

    K = Di/(2·hi) nominal (korozyonsuz) şekilden; hi = crown_depth. hi girilmezse
    standart 2:1 (K = 2) varsayımı kayda geçer (K4). R, r korozyonlu iç çap Dc ile
    hesaplanır (Dc·katsayı; r küçük kalır → β büyük, muhafazakâr). 1,7 < K < 2,2
    dışında prosedür yok → OUT_OF_SCOPE, None döner. Sınır/katsayılar bellekten.
    """
    if head.crown_depth:
        K = formulas.ellipsoidal_shape_factor(head.inside_diameter, head.crown_depth)
    else:
        K = 2.0
        result.add_assumption(
            f"K4: Elipsoidal bombe iç derinliği (crown_depth) girilmedi; standart 2:1 "
            f"(hi = Di/4 = {head.inside_diameter / 4.0:.1f} mm, K = 2) varsayıldı."
        )
    result.add_validity_check(
        f"{ELLIP_CLAUSE} {formulas.ELLIPSOIDAL_K_MIN} < K < {formulas.ELLIPSOIDAL_K_MAX}",
        formulas.ellipsoidal_in_scope(K), formulas.ELLIPSOIDAL_K_MAX, round(K, 4),
    )
    if not formulas.ellipsoidal_in_scope(K):
        result.set_out_of_scope(
            f"{ELLIP_CLAUSE}: K = Di/(2hi) = {K:.3f}; eşdeğer torisferik prosedürü yalnız "
            f"{formulas.ELLIPSOIDAL_K_MIN} < K < {formulas.ELLIPSOIDAL_K_MAX} için geçerli "
            "(sınır bellekten, verified=False). DBA (Ek B/C) veya başka yöntem gerekir."
        )
        return None
    Rc, rc = formulas.ellipsoidal_equivalent_radii(Dc, K)
    result.add_intermediate("K", K, "-", "Ellipsoidal shape factor Di/(2hi) (7.5.4)")
    result.add_assumption(
        f"{ELLIP_CLAUSE}: elipsoidal bombe eşdeğer torisferik olarak hesaplandı — "
        f"R = Di·(0,44K + 0,02) = {Rc:.2f} mm, r = Di·(0,5/K − 0,08) = {rc:.2f} mm "
        f"(K = {K:.3f}, Di korozyonlu). K tanımı, katsayılar ve 1,7 < K < 2,2 sınırı bellekten; "
        "lisanslı metinle doğrulanmadı (verified=False)."
    )
    return K, Rc, rc


def _tori_fb(mat, result: CalculationResult) -> float:
    fb = formulas.torispherical_fb(mat.yield_strength)
    result.add_assumption(
        f"{TORI_CLAUSE}.2: fb = Rp0,2/T / 1,5 = {mat.yield_strength:g}/1,5 = {fb:.2f} MPa; "
        f"Rp0,2/T olarak malzemenin yield_strength değeri ({mat.temperature:g} °C beyanlı) alındı. "
        "Soğuk sıvanmış dikişsiz östenitik bombe için izin verilen 1,6 katı UYGULANMADI (muhafazakâr)."
    )
    return fb


_TORI_GEOMETRY_CHECKS = ("7.5.3.1 r <= 0.2·Di", "7.5.3.1 r >= 0.06·Di", "7.5.3.1 R <= De")


def _tori_geometry_out_of_scope(result: CalculationResult, Di, De, R, r) -> bool:
    """Kalınlıktan bağımsız 7.5.3.1 sınırları (β yalnız 0,06 ≤ r/Di ≤ 0,2 için tanımlı).

    Aşılırsa prosedür hiç koşturulmaz: sonuç OUT_OF_SCOPE (sessiz hesap yok).
    """
    checks = [c for c in formulas.torispherical_applicability(Di, De, R, r, 0.0)
              if c[0] in _TORI_GEOMETRY_CHECKS]
    failed = _tori_apply_checks(result, checks)
    if failed:
        result.set_out_of_scope(
            f"{TORI_CLAUSE}.1 uygulanabilirlik sınırı aşıldı: " + "; ".join(failed)
            + ". Bu prosedür geçerli değil — DBA (Ek B/C) veya başka yöntem gerekir."
        )
    return bool(failed)


def _tori_apply_checks(result: CalculationResult, checks) -> list[str]:
    failed = []
    for name, ok, limit, actual in checks:
        result.add_validity_check(name, ok, round(limit, 4), round(actual, 4))
        if not ok:
            failed.append(f"{name} (sınır {limit:.3f}, gerçek {actual:.3f})")
    return failed


class EN13445DesignCode(DesignCode):
    """EN 13445 hesap eklentisi.

    Uygulanan maddeler:
    - EN 13445-3, 7.4.2: Silindirik gövde, iç basınç
    - EN 13445-3, 7.5.2 yarım küre; 7.5.4 elipsoidal → eşdeğer torisferik + 7.5.3 (E06) — verified=False
    - EN 13445-3, 7.5.3: Torisferik bombe tam prosedürü (es/ey/eb, β) — verified=False
    - EN 13445-3, 6: nominal tasarım gerilmesi f_d / f_test kontrolü — verified=False
    - EN 13445-3, 5.6 + EN 13445-5 test grubu → z — verified=False
    - EN 13445-5, 10.2.3.3.1 hidrostatik ve pnömatik test basıncı — verified=False
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
            clause_reference=SHELL_CLAUSE,
            formula_reference="e = P·Di/(2fz − P) (7.4-1); boyuna kontrol program eki",
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

        # Birimleştirme katsayısı (z) — EN 13445-3, 5.6 (test grubu girildiyse sınırlanır)
        z = self._z_for(welds, shell.weld_joint_id, result)

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
        tori_review = False
        elliptical_review = False
        tori_failed: list[str] = []
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

        # Birimleştirme katsayısı (z) — EN 13445-3, 5.6
        z = self._z_for(welds, head.weld_joint_id, result)

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
            if head.type in (HeadType.ELLIPTICAL, HeadType.TORISPHERICAL):
                if head.type == HeadType.ELLIPTICAL:
                    result.clause_reference = ELLIP_CLAUSE
                    result.formula_reference = ELLIP_FORMULA_NOTE
                    elliptical_review = True
                    ell = _ellipsoidal_radii_en(head, D, result)
                    if ell is None:
                        return result
                    _, Rc, rc = ell
                else:
                    result.clause_reference = TORI_CLAUSE
                    result.formula_reference = "7.5-1/7.5-2/7.5-3, β: 7.5.3.5"
                    radii = _torispherical_radii_en(head, D, C, result)
                    if radii is None:
                        return result
                    Rc, rc = radii
                De = _tori_outside_diameter(head, head.nominal_thickness)
                if _tori_geometry_out_of_scope(result, D, De, Rc, rc):
                    return result
                fb = _tori_fb(mat, result)
                tori = formulas.head_torispherical_thickness(P, D, Rc, rc, f, z, fb)
                e = tori["e"]
                tori_review = True
                mt = 1.0 - head.mill_tolerance / 100.0 if head.mill_tolerance > 0 else 0.90
                ea = head.nominal_thickness * mt - C - head.forming_thinning
                result.add_intermediate("Di", D, "mm", "Corroded inside diameter")
                result.add_intermediate("De", De, "mm", "Outside diameter")
                result.add_intermediate("R", Rc, "mm", "Corroded inside crown radius")
                result.add_intermediate("r", rc, "mm", "Corroded inside knuckle radius")
                result.add_intermediate("fb", fb, "MPa", "Buckling design stress (7.5.3.2)")
                result.add_intermediate("beta", tori["beta"], "-", "β at e = ey (7.5.3.5)")
                result.add_intermediate("es", tori["es"], "mm", "Crown thickness (7.5-1)")
                result.add_intermediate("ey", tori["ey"], "mm", "Knuckle yield thickness (7.5-2)")
                result.add_intermediate("eb", tori["eb"], "mm", "Knuckle buckling thickness (7.5-3)")
                result.add_intermediate("governing", tori["governing"], "-", "Governing equation")
                result.add_intermediate("e_required", e, "mm", "Required thickness max(es, ey, eb)")
                tori_failed = _tori_apply_checks(
                    result, [c for c in formulas.torispherical_applicability(D, De, Rc, rc, e, ea)
                             if c[0] not in _TORI_GEOMETRY_CHECKS]
                )
                result.add_assumption(
                    "EN 13445-3, 7.5.3 tam prosedürü (es/ey/eb, β denklem biçimi 7.5.3.5) bellekten "
                    "uygulandı; lisanslı metinle doğrulanmadı (verified=False). z yalnız taç (es) "
                    "denkleminde; bombe tek kalınlık kabul edildi (taç/büküm ayrı kalınlık yok)."
                )

            elif head.type == HeadType.HEMISPHERICAL:
                result.clause_reference = HEMI_CLAUSE
                result.formula_reference = "e = P·R/(2fz − 0,5P)"
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
        if elliptical_review:
            self._elliptical_7_5_4_review(result)
        if tori_review:
            self._cap_unverified(result, TORI_CLAUSE)
            if tori_failed:
                result.set_out_of_scope(
                    f"{TORI_CLAUSE}.1 uygulanabilirlik sınırı aşıldı: " + "; ".join(tori_failed)
                    + ". Bu prosedür geçerli değil — DBA (Ek B/C) veya başka yöntem gerekir."
                )
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
        tori_review = False
        elliptical_review = False
        tori_failed: list[str] = []

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

        # Birimleştirme katsayısı — EN 13445-3, 5.6
        z = self._z_for(welds, getattr(component, "weld_joint_id", None), result)

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
                result.clause_reference = SHELL_CLAUSE
                mawp = formulas.mawp_from_shell(R, t_actual, f, z, C)
                result.add_intermediate("R", R, "mm", "Corroded inside radius")
                result.add_intermediate("e_actual", t_actual, "mm", "Actual thickness")
                result.add_intermediate("C", C, "mm", "Corrosion allowance")
                result.add_intermediate("e_corroded", t_actual - C, "mm", "Corroded thickness")

            elif comp_type == "head":
                from domain.enums import HeadType
                head = component
                D = head.inside_diameter + 2 * C  # korozyonlu iç çap (V-16)
                if head.type in (HeadType.ELLIPTICAL, HeadType.TORISPHERICAL):
                    if head.type == HeadType.ELLIPTICAL:
                        result.clause_reference = ELLIP_CLAUSE
                        result.formula_reference = "7.5.4 → 7.5.3.4 Ps/Py/Pb (inverse by bisection)"
                        elliptical_review = True
                        ell = _ellipsoidal_radii_en(head, D, result)
                        if ell is None:
                            return result
                        _, Rc, rc = ell
                    else:
                        result.clause_reference = TORI_CLAUSE
                        result.formula_reference = "7.5.3.4 Ps/Py/Pb (inverse by bisection)"
                        radii = _torispherical_radii_en(head, D, C, result)
                        if radii is None:
                            return result
                        Rc, rc = radii
                    De = _tori_outside_diameter(head, t_actual)
                    if _tori_geometry_out_of_scope(result, D, De, Rc, rc):
                        return result
                    fb = _tori_fb(mat, result)
                    ea = t_actual - C
                    tm = formulas.torispherical_max_pressure(D, Rc, rc, ea, f, z, fb)
                    mawp = tm["P_bisect"]
                    tori_review = True
                    result.add_intermediate("R", Rc, "mm", "Corroded inside crown radius")
                    result.add_intermediate("r", rc, "mm", "Corroded inside knuckle radius")
                    result.add_intermediate("ea", ea, "mm", "Analysis thickness")
                    result.add_intermediate("fb", fb, "MPa", "Buckling design stress (7.5.3.2)")
                    result.add_intermediate("beta", tm["beta"], "-", "β at e = ea (7.5.3.5)")
                    result.add_intermediate("Ps", tm["Ps"], "MPa", "Crown limit")
                    result.add_intermediate("Py", tm["Py"], "MPa", "Knuckle yield limit")
                    result.add_intermediate("Pb", tm["Pb"], "MPa", "Knuckle buckling limit")
                    result.add_intermediate("governing", tm["governing"], "-", "Governing limit")
                    tori_failed = _tori_apply_checks(
                        result, [c for c in formulas.torispherical_applicability(D, De, Rc, rc, ea, ea)
                                 if c[0] not in _TORI_GEOMETRY_CHECKS]
                    )
                elif head.type == HeadType.HEMISPHERICAL:
                    result.clause_reference = HEMI_CLAUSE
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
        if elliptical_review:
            self._elliptical_7_5_4_review(result)
        if tori_review:
            self._cap_unverified(result, TORI_CLAUSE)
            if tori_failed:
                result.set_out_of_scope(
                    f"{TORI_CLAUSE}.1 uygulanabilirlik sınırı aşıldı: " + "; ".join(tori_failed)
                    + ". MAWP bu prosedürle geçerli değil."
                )
        self._apply_material_data_check(result, mat, dc, t_actual)
        result.material_properties_used = {
            "designation": mat.material_designation,
            "design_stress_f": f,
            "source_reference": mat.source_reference,
        }

        return result

    def calculate_hydrotest_pressure(self, input_data: dict) -> CalculationResult:
        """E04 — EN 13445-5, 10.2.3.3.1 hidrostatik test basıncı.

        Pt = max(1,25·Pd·fa/fT ; 1,43·PS)  (Pd tasarım basıncı; fa test, fT tasarım
        sıcaklığındaki nominal tasarım gerilmesi). 1,25/1,43 PED Ek I 7.4 ile
        tutarlıdır; fa/fT'li biçim bellekten (verified=False).
        """
        dc = input_data["design_conditions"]
        result = CalculationResult(
            component_type="system",
            calculation_type="hydrotest",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=HYDRO_CLAUSE,
            formula_reference="Pt = max(1.25·Pd·fa/fT ; 1.43·PS)",
        )
        ps, pd = dc.maximum_allowable_pressure_ps, dc.design_pressure
        ratio = self._stress_ratio(input_data, dc)
        r_used = ratio["ratio"] if ratio["ratio"] is not None else 1.0
        p_test, limiter, p_pd, p_ps = formulas.en_hydrotest_pressure(pd, ps, r_used)

        result.input_snapshot = {
            "PS_MPa": ps,
            "Pd_MPa": pd,
            "P_operating_max_MPa": dc.operating_pressure,
            "fa_fT_by_material": ratio["by_material"],
            "limiter": limiter,
            "design_temperature_C": dc.design_temperature,
            "hydrotest_temperature_C": dc.hydrotest_temperature,
        }
        result.add_intermediate("PS", ps, "MPa", "Maximum allowable pressure (PS)")
        result.add_intermediate("Pd", pd, "MPa", "Design pressure")
        result.add_intermediate("P_operating_max", dc.operating_pressure, "MPa", "Max operating pressure (info)")
        result.add_intermediate("fa_fT", r_used, "-", "Stress ratio test/design temperature used")
        result.add_intermediate("P_from_pd", p_pd, "MPa", "1.25 × Pd × fa/fT")
        result.add_intermediate("P_from_ps", p_ps, "MPa", "1.43 × PS")
        result.add_intermediate("P_test", p_test, "MPa", "EN 13445-5 hydrostatic test pressure")
        result.add_intermediate("limiter", limiter, "-", "Limiter")
        result.add_assumption(
            f"Pt = max(1.25 × {pd:g} × {r_used:.4g}, 1.43 × {ps:g}) = {p_test:.4f} MPa ({limiter}). "
            "1,25 terimi çalışma basıncıyla değil tasarım basıncı Pd ile kurulur (EN 13445-5; "
            "eski sürüm çalışma basıncını kullanıyordu)."
        )
        result.add_assumption(
            "Bileşen bazında test durumu gerilme kontrolü (f_test, statik sıvı kafası) bu satırda "
            "yapılmaz; f_test değerleri nominal_design_stress satırlarında raporlanır."
        )
        result.final_result = p_test
        result.final_result_unit = "MPa"

        if ratio["missing"]:
            reason = (
                f"fa/ft oranı uygulanamadı: tasarım {dc.design_temperature} °C, test "
                f"{dc.hydrotest_temperature} °C ve test gerilmesi eksik "
                f"({', '.join(ratio['missing'])}). Sonuç fa/fT = 1 ile alt sınırdır; oran > "
                f"{self._EN_RATIO_THRESHOLD_TEXT} ise 1.25·Pd·fa/ft terimi 1.43·PS'i aşar ve "
                "test basıncı olması gerekenden DÜŞÜK kalır. Malzemede 'Test sıcaklığında S' girin."
            )
            result.add_warning(reason)
            result.set_review_required(reason)
        elif limiter == "design_pressure" and abs(r_used - 1.0) > 1e-9:
            reason = (
                f"fa/fT = {r_used:.3f} ile 1.25·Pd·fa/fT terimi belirleyici (> 1.43·PS). "
                f"{HYDRO_CLAUSE} biçimi bellekten uygulandı (verified=False); çok malzemede oranın "
                "seçimi (en büyük oran kullanıldı) lisanslı metinle doğrulanmalıdır."
            )
            result.add_warning(reason)
            result.set_review_required(reason)
        else:
            # Oran 1 (aynı sıcaklık) veya 1,43·PS en büyük oranla bile belirleyici:
            # sonuç fa/fT biçiminden ve oran seçiminden bağımsızdır.
            result.set_pass()
        return result

    _EN_RATIO_THRESHOLD_TEXT = "1.43·PS/(1.25·Pd)"

    def _stress_ratio(self, input_data: dict, dc) -> dict:
        """fa/fT: malzemenin test sıcaklığı gerilmesi / tasarım gerilmesi (basınçlı parçalar).

        Aynı sıcaklıkta oran 1. Çok malzemede EN büyük oran seçilir (en yüksek Pt);
        hepsi raporlanır. Test gerilmesi eksikse ``missing`` dolu, ``ratio`` None.
        """
        if abs(dc.design_temperature - dc.hydrotest_temperature) < 1e-9:
            return {"ratio": 1.0, "by_material": {}, "missing": []}
        materials = input_data.get("materials", []) or []
        project = input_data.get("project")
        if project is not None:
            ids = {
                c.material_id
                for coll in (project.shell_sections, project.heads, project.cones)
                for c in coll
            }
            materials = [m for m in materials if m.material_id in ids] or materials
        if not materials:
            return {"ratio": None, "by_material": {}, "missing": ["malzeme yok"]}
        missing = [m.material_id for m in materials if m.allowable_stress_test_temp is None]
        by_mat = {
            m.material_id: m.allowable_stress_test_temp / m.allowable_stress
            for m in materials if m.allowable_stress_test_temp is not None
        }
        if missing:
            return {"ratio": None, "by_material": by_mat, "missing": missing}
        return {"ratio": max(by_mat.values()), "by_material": by_mat, "missing": []}

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
        z = self._z_for(input_data.get("welds", []), cone.weld_joint_id, result)
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
        z = self._z_for(input_data.get("welds", []), cone.weld_joint_id, result)
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
    def _z_for(welds, weld_id, result: CalculationResult | None = None) -> float:
        """E04 — dikişin z'si; EN 13445-5 test grubu girildiyse 5.6 sınırına indirilir."""
        weld = next((w for w in welds if w.joint_id == weld_id), None) if weld_id else None
        if weld is None:
            return 1.0
        z = weld.joint_coefficient
        group = getattr(weld, "en_testing_group", None)
        if group:
            z_max = formulas.joint_coefficient_for_testing_group(group)
            if z > z_max + 1e-12:
                if result is not None:
                    result.add_assumption(
                        f"{Z_CLAUSE}: dikiş {weld.joint_id} test grubu {group} → z ≤ {z_max:g}; "
                        f"girilen z = {z:g} yerine z = {z_max:g} kullanıldı."
                    )
                    result.add_warning(
                        f"Dikiş {weld.joint_id}: girilen z = {z:g}, test grubu {group} için izin "
                        f"verilen {z_max:g}'den büyük; hesapta {z_max:g} kullanıldı."
                    )
                z = z_max
        return z

    @staticmethod
    def _cap_unverified(result: CalculationResult, clause: str) -> None:
        """verified=False: doğrulanmamış formülde PASS en fazla REVIEW_REQUIRED olur."""
        if result.status == CalculationStatus.PASS:
            result.set_review_required(
                f"{clause}: formül lisanslı EN 13445-3 metniyle doğrulanmadı (verified=False); "
                "olumlu sonuç bağımsız mühendis incelemesi gerektirir."
            )

    def calculate_pneumatic_test_pressure(self, input_data: dict) -> CalculationResult:
        """E04 — EN 13445-5 pnömatik test basıncı: Pt = k·Pd·fa/fT (verified=False).

        k lisanslı EN 13445-5 metninden kullanıcı girer (DesignConditions.
        en_pneumatic_test_factor); programa gömülmez. ASME UG-100 kullanılmaz.
        """
        dc = input_data["design_conditions"]
        result = CalculationResult(
            component_type="system",
            calculation_type="pneumatic_test",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=PNEU_CLAUSE,
            formula_reference="Pt = k·Pd·fa/fT",
        )
        k = getattr(dc, "en_pneumatic_test_factor", None)
        result.input_snapshot = {
            "Pd_MPa": dc.design_pressure, "k": k,
            "design_temperature_C": dc.design_temperature,
            "test_temperature_C": dc.hydrotest_temperature,
        }
        if not k:
            result.set_blocked_code_data(
                "EN 13445-5 pnömatik test katsayısı k girilmedi (DesignConditions."
                "en_pneumatic_test_factor). Katsayı lisanslı EN 13445-5 metninden okunur ve programa "
                f"gömülmez (K6); {self._NO_ASME_FALLBACK}"
            )
            return result
        ratio = self._stress_ratio(input_data, dc)
        if ratio["missing"]:
            result.set_blocked_missing_input(
                "Pnömatik test için fa/fT gerekir: tasarım ve test sıcaklığı farklı, test "
                f"sıcaklığı gerilmesi eksik ({', '.join(ratio['missing'])})."
            )
            return result
        p_test = formulas.en_pneumatic_test_pressure(dc.design_pressure, ratio["ratio"], k)
        for name, val, unit, desc in (
            ("Pd", dc.design_pressure, "MPa", "Design pressure"),
            ("k", k, "-", "Pneumatic test factor (user, EN 13445-5)"),
            ("fa_fT", ratio["ratio"], "-", "Stress ratio test/design temperature (max)"),
            ("P_test", p_test, "MPa", "EN 13445-5 pneumatic test pressure"),
        ):
            result.add_intermediate(name, val, unit, desc)
        result.add_assumption(
            "Pnömatik test basıncı Pt = k·Pd·fa/fT biçimiyle hesaplandı (biçim bellekten, verified=False). "
            "EN 13445-5'in pnömatik teste ek şartları (ek NDT, güvenlik önlemleri, depolanan enerji "
            "sınırları) bu satırda kontrol edilmez."
        )
        result.final_result, result.final_result_unit = p_test, "MPa"
        result.set_pass()
        self._cap_unverified(result, PNEU_CLAUSE)
        return result

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
        """E04 — EN 13445-5 test grubu → EN 13445-3, 5.6 z eşlemesi (verified=False)."""
        return [self._validate_weld_en(weld) for weld in project.welds]

    def _validate_weld_en(self, weld) -> CalculationResult:
        result = CalculationResult(
            component_id=weld.joint_id,
            component_type="weld",
            calculation_type="weld_validation",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=f"{Z_CLAUSE} / EN 13445-5 (test grupları)",
            formula_reference="test grubu 1·2 → z=1; 3 → z=0,85; 4 → z=0,7",
        )
        group = getattr(weld, "en_testing_group", None)
        z = weld.joint_coefficient
        result.input_snapshot = {
            "joint_coefficient_z": z, "en_testing_group": group,
            "nde_method": weld.nde_method, "nde_extent": weld.nde_extent,
        }
        if not group:
            result.add_assumption(
                f"K4: EN 13445-5 test grubu girilmedi; girilen z = {z:g} olduğu gibi kullanıldı."
            )
            result.set_not_calculated(
                "EN 13445 weld validation needs the EN 13445-5 testing group (WeldJoint.en_testing_group); "
                f"the entered joint coefficient z = {z:g} is used as-is (assumption); PWHT/NDE extent "
                f"not checked; {self._NO_ASME_FALLBACK}"
            )
            return result
        z_max = formulas.joint_coefficient_for_testing_group(group)
        result.add_intermediate("testing_group", group, "-", "EN 13445-5 testing group")
        result.add_intermediate("z_entered", z, "-", "Entered joint coefficient")
        result.add_intermediate("z_max", z_max, "-", "Max z for testing group (5.6)")
        result.final_result, result.allowable_limit = z, z_max
        result.add_assumption(
            "NDT kapsamının test grubuyla uyumu, test grubu 4'ün malzeme/kalınlık kısıtları ve PWHT "
            "bu satırda kontrol edilmez; tablo bellekten (verified=False)."
        )
        if z > z_max + 1e-12:
            msg = (
                f"Girilen z = {z:g}, test grubu {group} için izin verilen {z_max:g}'den büyük; "
                f"EN hesaplarında z = {z_max:g} kullanıldı. Girdiyi düzeltin."
            )
            result.add_warning(msg)
            result.set_review_required(msg)
        else:
            result.set_pass(z / z_max)
            self._cap_unverified(result, Z_CLAUSE)
        return result

    def check_material_design_stress(self, project) -> List[CalculationResult]:
        """E04 — EN 13445-3 Madde 6: girilen f ≤ azami nominal tasarım gerilmesi f_d; f_test raporu."""
        used = []
        for coll, attr in ((project.shell_sections, "material_id"), (project.heads, "material_id"),
                           (project.cones, "material_id"), (project.nozzles, "material_id")):
            for c in coll:
                mid = getattr(c, attr, None)
                if mid and mid not in used:
                    used.append(mid)
        dc = project.design_conditions
        return [self._material_stress_row(m, dc) for m in project.materials if m.material_id in used]

    def _material_stress_row(self, mat, dc) -> CalculationResult:
        result = CalculationResult(
            component_id=mat.material_id,
            component_type="material",
            calculation_type="nominal_design_stress",
            code=self.code_name,
            edition=self.code_edition,
            clause_reference=f"{STRESS_CLAUSE} (alt madde no doğrulanmadı)",
        )
        group = getattr(mat, "en_material_group", None)
        f_in = mat.allowable_stress
        result.input_snapshot = {
            "material": mat.material_designation, "en_material_group": group, "f_entered_MPa": f_in,
            "design_temperature_C": dc.design_temperature, "test_temperature_C": dc.hydrotest_temperature,
        }
        if not group:
            result.set_blocked_missing_input(
                f"{STRESS_CLAUSE}: malzeme grubu (en_material_group) girilmedi; girilen f = {f_in:g} MPa'nın "
                "Madde 6 üst sınırına uygunluğu kontrol edilemedi. Bileşen hesapları elle girilen f ile "
                "sürer (K4)."
            )
            return result
        a_min = formulas.EN_AUSTENITIC_MIN_ELONGATION.get(group)
        if a_min is not None:
            a = getattr(mat, "en_elongation_a_pct", None)
            if a is None:
                result.set_blocked_missing_input(
                    f"{group}: kopma uzaması A (en_elongation_a_pct) gerekli (A ≥ %{a_min:g} beyanı doğrulanmalı)."
                )
                return result
            result.add_intermediate("A", a, "%", "Elongation after fracture")
            if a < a_min:
                result.set_blocked_missing_input(
                    f"{group} grubu A ≥ %{a_min:g} ister, girilen A = %{a:g}; doğru malzeme grubunu girin."
                )
                return result
        props = {
            "rp02_t": mat.en_rp02_t, "rp10_t": mat.en_rp10_t, "rm_20": mat.en_rm_20, "rm_t": mat.en_rm_t,
            "rp02_test": mat.en_rp02_test, "rp10_test": mat.en_rp10_test, "rm_test": mat.en_rm_test,
        }
        if props["rp02_t"] is None and abs(mat.temperature - dc.design_temperature) < 1e-6:
            props["rp02_t"] = mat.yield_strength
            result.add_assumption(
                f"K4: Rp0,2/T girilmedi; yield_strength = {mat.yield_strength:g} MPa "
                f"({mat.temperature:g} °C beyanlı = tasarım sıcaklığı) Rp0,2/T kabul edildi."
            )
        if props["rm_20"] is None:
            props["rm_20"] = mat.tensile_strength
            result.add_assumption(
                f"K4: Rm/20 girilmedi; tensile_strength = {mat.tensile_strength:g} MPa oda sıcaklığı "
                "asgari çekme dayanımı kabul edildi."
            )
        need_d, need_t = formulas.EN_STRESS_REQUIRED_PROPERTIES[group]
        missing = [k for k in need_d if props[k] is None]
        if missing:
            result.set_blocked_missing_input(
                f"{STRESS_CLAUSE} ({group}): f_d için gerekli malzeme özelliği eksik: "
                + ", ".join(f"en_{k}" for k in missing) + ". Değer uydurulmaz."
            )
            return result
        for k in need_d:
            result.add_intermediate(k, props[k], "MPa", f"{k} (design)")
        f_d, form = formulas.nominal_design_stress(group, props)
        result.formula_reference = f"f_d = {form}"
        result.add_intermediate("f_d", f_d, "MPa", "Max nominal design stress (Clause 6)")
        result.add_intermediate("f_entered", f_in, "MPa", "Entered design stress used in calcs")
        missing_t = [k for k in need_t if props[k] is None]
        if missing_t:
            result.add_warning(
                "f_test hesaplanmadı: test sıcaklığı özelliği eksik (" + ", ".join(f"en_{k}" for k in missing_t) + ")."
            )
        else:
            f_test, form_t = formulas.nominal_test_stress(group, props)
            result.add_intermediate("f_test", f_test, "MPa", f"Max nominal test stress = {form_t}")
        result.final_result, result.final_result_unit = f_in, "MPa"
        result.allowable_limit, result.allowable_limit_unit = f_d, "MPa"
        u = f_in / f_d
        if u > 1.0 + 1e-9:
            result.set_fail(u)
            result.add_warning(
                f"Girilen f = {f_in:g} MPa, Madde 6 azami f_d = {f_d:.2f} MPa'yı aşıyor; bileşen hesapları "
                "emniyetsiz tarafta."
            )
        else:
            result.set_pass(u)
            self._cap_unverified(result, STRESS_CLAUSE)
        return result

    def check_pressure_relief(self, project, global_mawp=None) -> List[CalculationResult]:
        """E04 — EN rotasında ASME UG-125–136 hesabı EN adı altında sunulmaz."""
        system = getattr(project, "pressure_relief", None)

        def row(cid, ctype):
            return CalculationResult(
                component_id=cid, component_type=ctype, calculation_type="pressure_relief",
                code=self.code_name, edition=self.code_edition, clause_reference=RELIEF_CLAUSE,
            )

        if system is None or not system.enabled:
            r = row("RELIEF-SYSTEM", "system")
            r.set_out_of_scope("Pressure relief system is not configured for this project.")
            return [r]
        rows = []
        for device in (system.devices or []):
            r = row(device.device_id, "pressure_relief_device")
            r.input_snapshot = {"device": device.model_dump(mode="json")}
            r.set_not_calculated(
                "EN rotasında tahliye cihazı kontrolü uygulanmadı (EN ISO 4126 / EN 764-7 / PED Ek I 2.11); "
                "ASME UG-125–136 sonucu EN adı altında sunulmaz; bağımsız değerlendirme gerekir."
            )
            rows.append(r)
        if not rows:
            r = row("RELIEF-SYSTEM", "system")
            r.set_not_calculated("Tahliye sistemi tanımlı ama cihaz yok; EN rotasında kontrol uygulanmadı.")
            rows.append(r)
        return rows

    def _elliptical_7_5_4_review(self, result: CalculationResult) -> None:
        """E06 (E04 uyarısının yerine): 7.5.4 eşdeğer torisferik uygulandı ama doğrulanmadı."""
        msg = (
            f"{ELLIP_CLAUSE}: elipsoidal bombe eşdeğer torisferik (R, r) + 7.5.3 prosedürüyle "
            "hesaplandı (eski küre denklemi kaldırıldı). K tanımı, R/r katsayıları ve 1,7 < K < 2,2 "
            "sınırı bellekten; lisanslı metinle doğrulanmadı (verified=False) — bağımsız inceleme gerekir."
        )
        result.add_warning(msg)
        if result.status == CalculationStatus.PASS:
            result.set_review_required(msg)

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
