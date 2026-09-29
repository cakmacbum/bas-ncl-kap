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


_GRAVITY_M_S2 = 9.80665
# Ayak alt kontrollerinin (kesit/kaynak/taban plakası/WRC) okuduğu Support alanları.
_LEG_DETAIL_FIELDS = (
    "leg_attachment", "leg_section_type", "leg_profile_height_mm", "leg_profile_width_mm",
    "leg_web_thickness_mm", "leg_flange_thickness_mm", "leg_unbraced_length_mm",
    "leg_eccentricity_mm", "leg_effective_length_factor_K", "leg_pad_length_mm",
    "leg_pad_width_mm", "leg_pad_thickness_mm", "leg_pad_contact_ratio",
    "base_plate_length_mm", "base_plate_width_mm", "base_plate_thickness_mm",
    "base_plate_yield_MPa", "foundation_bearing_allowable_MPa",
    "pad_to_shell_weld_leg_mm", "leg_to_pad_weld_leg_mm", "leg_to_base_plate_weld_leg_mm",
    "weld_electrode_strength_MPa", "weld_min_leg_mm", "wrc_coefficients",
)
_HYDROTEST_WATER_DENSITY_KG_M3 = 1000.0  # K4 varsayımı: hidrotest ortamı su


def _support_load_envelope(project, support_location_mm: float) -> dict:
    """Yük durumlarından destek yük ZARFI (alternatif durumlar toplanmaz).

    Her yük durumu ayrı değerlendirilir; `concurrent_with` ile açıkça eşzamanlı
    işaretlenen durumlar (NON_CONCURRENT_LOAD_PAIRS dışındaysa) aynı grupta
    birleşir. Grup içinde: yatay yük Σ√(Fx²+Fy²); moment = √((ΣMx)²+(ΣMy)²)
    (SRSS) + Σ yatay·kaldıraç (yön bilinmediğinden aritmetik toplam, muhafazakâr).
    Zarf: gruplar arası en büyük moment/yatay yük; Fz zarfı ayrı max/min.
    Fz işaret kuralı domain'de tanımlı DEĞİL; K4 varsayımı: Fz>0 aşağı (basma).
    """
    from domain.load_cases import NON_CONCURRENT_LOAD_PAIRS

    cases = list(getattr(project, "load_cases", None) or [])
    by_id = {c.load_case_id: c for c in cases}

    def non_concurrent(a, b) -> bool:
        return any({a.load_type, b.load_type} == {l, r} for l, r in NON_CONCURRENT_LOAD_PAIRS)

    env = {
        "moment_Nmm": 0.0, "moment_case": None,
        "horizontal_N": 0.0, "horizontal_case": None,
        "fz_max_N": 0.0, "fz_min_N": 0.0,
        "per_case": [], "notes": [],
    }
    seen_groups = set()
    for case in cases:
        members = [case] + [
            by_id[i] for i in (case.concurrent_with or [])
            if i in by_id and i != case.load_case_id and not non_concurrent(case, by_id[i])
        ]
        key = frozenset(c.load_case_id for c in members)
        if key in seen_groups:
            continue
        seen_groups.add(key)
        label = "+".join(c.load_case_id for c in members)
        loads = [ld for c in members for ld in (c.external_loads or [])]
        if not loads:
            continue
        horizontal = sum(math.hypot(ld.fx_n, ld.fy_n) for ld in loads)
        m_direct = math.hypot(sum(ld.mx_nmm for ld in loads), sum(ld.my_nmm for ld in loads))
        m_lever = sum(
            math.hypot(ld.fx_n, ld.fy_n) * max(0.0, (ld.elevation_mm or 0.0) - support_location_mm)
            for ld in loads
        )
        if any(
            math.hypot(ld.fx_n, ld.fy_n) > 0.0 and (ld.elevation_mm or 0.0) <= support_location_mm
            for ld in loads
        ):
            env["notes"].append(
                f"Yük durumu {label}: yatay kuvvet var ama yük kotu (elevation_mm) destek kotunun "
                f"({support_location_mm:g} mm) üstünde girilmemiş; kaldıraç kolu 0 alındı, "
                f"kuvvetin momenti HESAPLANAMADI (yalnız girilen Mx/My kullanıldı)."
            )
        moment = m_direct + m_lever
        fz = sum(ld.fz_n for ld in loads)
        env["per_case"].append({"case": label, "moment_Nmm": moment, "horizontal_N": horizontal, "fz_N": fz})
        if moment > env["moment_Nmm"]:
            env["moment_Nmm"], env["moment_case"] = moment, label
        if horizontal > env["horizontal_N"]:
            env["horizontal_N"], env["horizontal_case"] = horizontal, label
        env["fz_max_N"] = max(env["fz_max_N"], fz)
        env["fz_min_N"] = min(env["fz_min_N"], fz)
    return env


def _host_outer_diameters(project, host_type: str, host) -> tuple:
    """Host bileşenin dış çap aralığı (min, max) mm; bilinmiyorsa (None, None)."""
    try:
        if host_type == "cone":
            t = host.nominal_thickness
            return host.small_diameter + 2.0 * t, host.large_diameter + 2.0 * t
        if getattr(host, "outside_diameter", None):
            d = host.outside_diameter
        elif getattr(host, "inside_diameter", None):
            d = host.inside_diameter + 2.0 * host.nominal_thickness
        else:
            return None, None
        return d, d
    except (AttributeError, TypeError):
        return None, None


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

    def _apply_material_data_check(
        self, result: CalculationResult, mat, dc, nominal_thickness: float
    ) -> None:
        """Malzeme S değerinin bu tasarım noktası için geçerliliğini denetle.

        Sonuç "S, tasarım sıcaklığında girildi" varsayımına dayanır ama malzemenin
        `temperature` ve `thickness_min/max` alanları hiçbir yerde kıyaslanmıyordu:
        yanlış sıcaklıktaki bir S ile sayısal PASS çıkabilirdi. Uyuşmazlık
        sessizce geçilmez — uyarı yazılır, PASS → REVIEW_REQUIRED olur (K4).
        Sıcaklık kıyası, S'nin gerçek tablo değeri olduğunu kanıtlamaz; yalnız
        girilen S'nin hangi sıcaklık için olduğu beyanını doğrular.
        """
        issues = []
        if abs(mat.temperature - dc.design_temperature) > 1e-6:
            issues.append(
                f"Malzeme '{mat.material_id}' S değeri {mat.temperature:g} °C için girilmiş; "
                f"tasarım sıcaklığı {dc.design_temperature:g} °C. S bu sıcaklıkta doğrulanmadı."
            )
        if nominal_thickness and not (mat.thickness_min <= nominal_thickness <= mat.thickness_max):
            issues.append(
                f"Nominal kalınlık {nominal_thickness:g} mm, malzeme '{mat.material_id}' veri "
                f"aralığının [{mat.thickness_min:g}, {mat.thickness_max:g}] mm dışında."
            )
        for issue in issues:
            result.add_warning(issue)
        if issues and result.status == CalculationStatus.PASS:
            result.set_review_required(issues[0])

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
        self._apply_material_data_check(result, mat, dc, shell.nominal_thickness)

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
        self._apply_material_data_check(result, mat, dc, head.nominal_thickness)

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
        self._apply_material_data_check(result, mat, dc, t_actual)
        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "source_reference": mat.source_reference,
        }

        return result

    @staticmethod
    def _test_candidate_materials(input_data: dict, materials: list) -> list:
        """Projede basınç taşıyan parçalara bağlı malzemeler (yoksa hepsi)."""
        project = input_data.get("project")
        if project is None:
            return list(materials)
        material_ids = {
            component.material_id
            for collection in (project.shell_sections, project.heads, project.cones)
            for component in collection
        }
        candidates = [material for material in materials if material.material_id in material_ids]
        return candidates or list(materials)

    @staticmethod
    def _governing_test_material(input_data: dict, materials: list):
        """Liste sırası yerine bağlı basınç taşıyan malzemeyi belirle."""
        candidates = ASMEVIII1DesignCode._test_candidate_materials(input_data, materials)
        return min(candidates, key=lambda material: material.allowable_stress)

    @staticmethod
    def _test_stress_ratio(input_data: dict, materials: list, dc) -> dict:
        """UG-99(b)/UG-100 LSR — basınç parçalarındaki en küçük S_test/S_design oranı.

        Döner: {S_test, S_design, ratio, material_id, complete, missing, basis}
        - Tüm aday malzemelerde `allowable_stress_test_temp` varsa: oran malzeme
          bazında hesaplanır, en küçüğü belirleyicidir (complete=True).
        - Değilse ve tasarım sıcaklığı = test sıcaklığı ise: S_test = S_design
          gerçek eşitliktir (aynı tablo noktası), LSR = 1 (complete=True).
        - Aksi halde test gerilmesi bilinmiyor: LSR=1 yalnız yedek değerdir ve
          emniyetsiz olabilir (oran normalde ≥ 1) → complete=False (K4).
        """
        candidates = ASMEVIII1DesignCode._test_candidate_materials(input_data, materials)
        if all(m.allowable_stress_test_temp is not None for m in candidates):
            governing = min(
                candidates, key=lambda m: m.allowable_stress_test_temp / m.allowable_stress
            )
            return {
                "S_test": governing.allowable_stress_test_temp,
                "S_design": governing.allowable_stress,
                "ratio": governing.allowable_stress_test_temp / governing.allowable_stress,
                "material_id": governing.material_id,
                "complete": True,
                "missing": [],
                "basis": "material",
            }
        governing = min(candidates, key=lambda m: m.allowable_stress)
        missing = [m.material_id for m in candidates if m.allowable_stress_test_temp is None]
        same_temp = abs(dc.design_temperature - dc.hydrotest_temperature) < 1e-9
        return {
            "S_test": governing.allowable_stress,
            "S_design": governing.allowable_stress,
            "ratio": 1.0,
            "material_id": governing.material_id,
            "complete": same_temp,
            "missing": [] if same_temp else missing,
            "basis": "same_temperature" if same_temp else "assumed",
        }

    def _apply_test_stress_ratio(self, result: CalculationResult, info: dict, dc, clause: str) -> None:
        """LSR kaynağını sonuca yaz; bilinmiyorsa uyarı ekle (statüyü çağıran verir)."""
        if info["basis"] == "material":
            result.add_assumption(
                f"{clause} LSR = min(S_test/S_design) = {info['ratio']:.4f}; belirleyici malzeme "
                f"{info['material_id']} (S_test={info['S_test']} MPa, S_design={info['S_design']} MPa)."
            )
        elif info["basis"] == "same_temperature":
            result.add_assumption(
                f"{clause} Tasarım ve test sıcaklığı aynı ({dc.hydrotest_temperature} °C): "
                f"S_test = S_design ({info['S_design']} MPa), LSR = 1.0. Belirleyici malzeme: "
                f"{info['material_id']}."
            )
        else:
            result.add_assumption(
                f"K4: Test sıcaklığındaki izin verilen gerilme girilmedi; LSR=1.0 yedek değer "
                f"olarak kullanıldı (belirleyici malzeme {info['material_id']})."
            )
            result.add_warning(
                f"Test gerilmesi eksik ({', '.join(info['missing'])}): tasarım sıcaklığı "
                f"{dc.design_temperature} °C, test sıcaklığı {dc.hydrotest_temperature} °C. "
                "S_test/S_design normalde ≥ 1'dir; LSR=1 test basıncını olması gerekenden DÜŞÜK "
                "verebilir (emniyetsiz yön). Malzemede 'Test sıcaklığında S' değerini girin."
            )

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

        # UG-99(b): LSR = basınç parçalarındaki en küçük S_test/S_design oranı.
        # Oran normalde ≥ 1 olduğundan, test gerilmesi bilinmeyip LSR=1 alınırsa
        # test basıncı olması gerekenden DÜŞÜK kalabilir (emniyetsiz) — K4.
        stress = self._test_stress_ratio(input_data, materials, dc)
        S_design, S_test = stress["S_design"], stress["S_test"]
        self._apply_test_stress_ratio(result, stress, dc, "UG-99(b):")

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
        if stress["complete"]:
            result.set_pass()
        else:
            result.set_review_required(
                "Test sıcaklığındaki izin verilen gerilme girilmedi; LSR=1 varsayımı test "
                "basıncını olması gerekenden düşük verebilir."
            )

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

        # UG-100: LSR mantığı hidrostatik testle aynıdır (bkz. UG-99(b)).
        stress = self._test_stress_ratio(input_data, materials, dc)
        S_design, S_test = stress["S_design"], stress["S_test"]
        self._apply_test_stress_ratio(result, stress, dc, "UG-100:")

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
        if stress["complete"]:
            result.set_pass()
        else:
            result.set_review_required(
                "Test sıcaklığındaki izin verilen gerilme girilmedi; LSR=1 varsayımı test "
                "basıncını olması gerekenden düşük verebilir."
            )

        # Pnömatik test güvenlik notları: zorunlu bilgilendirme, durumu düşüren uyarı değil.
        result.add_notice(
            "Pnömatik test hidrostatik testten daha tehlikelidir. "
            "Yüksek enerji depolayan bir testtir; uygun güvenlik önlemleri alınmalı."
        )
        result.add_notice(
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
        # M, bolt load and Y/f/F/V/T/U are deliberately explicit: no silent Appendix 2 factors.
        # W/M: kullanıcı girdisi (Appendix 2 çalışma sayfası); program hesaplamaz (K6).
        payload = {
            "flange": {"tag": flange.flange_id, "type": flange.type,
                       "A": flange.outside_diameter, "B": flange.inside_diameter,
                       "t": flange.thickness,
                       # Appendix 2: g0 = küçük uç, g1 = büyük uç (flanş sırtı) hub kalınlığı.
                       "g0": flange.hub_small_thickness,
                       "g1": getattr(flange, "hub_large_thickness", None),
                       "h": flange.hub_length, "material_id": flange.material_id},
            "design_conditions": input_data["design_conditions"],
            "materials": input_data.get("materials", []),
            "bolt_load_W": input_data.get("bolt_load_W"),
            "moment_M": input_data.get("moment_M"),
        }
        if input_data.get("flange_factor_Y") is not None:
            payload["flange_factor_Y"] = input_data["flange_factor_Y"]
        if input_data.get("flange_factor_f") is not None:
            payload["flange_factor_f"] = input_data["flange_factor_f"]
        # K6: Şekil 2-7.1 faktörleri F/V/T/U kullanıcı girdisidir; boşsa None → bloke.
        for key in ("F", "V", "T", "U"):
            val = getattr(flange, f"flange_factor_{key}", None)
            if val is not None:
                payload[f"flange_factor_{key}"] = val
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
        weight_empty_N = vm.total_metal_mass_kg * _GRAVITY_M_S2
        # Hidrotest: metal + su (rho=1000 kg/m3, K4 varsayımı) — iç hacim korozyon payı düşülmüş.
        water_mass_kg = vm.total_inner_volume_m3 * _HYDROTEST_WATER_DENSITY_KG_M3
        weight_hydro_N = weight_empty_N + water_mass_kg * _GRAVITY_M_S2

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

        sequence_all = getattr(project, "component_sequence", None) or []

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

        def component_global_start(kind, component_id):
            if not sequence_all:
                # A legacy single-shell vessel has an unambiguous local origin.
                # With multiple shells, an explicit host ID alone cannot map a
                # global station to that shell without the ordered chain.
                return 0.0 if (kind == "shell" and len(shells_by_id) == 1) else None
            position = 0.0
            matches = 0
            start = None
            for ref in sequence_all:
                if ref.component_type == kind and ref.component_id == component_id:
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
            def blocked(message, _sup=sup):
                r = CalculationResult(
                    component_id=_sup.support_id,
                    component_type="support",
                    calculation_type=f"{_sup.type}_stress",
                    code=self.code_name,
                    edition=self.code_edition,
                )
                r.set_not_calculated(message)
                results.append(r)

            # Host çözümü: eyer YALNIZ gövdeye oturur; etek ve ayak gövde, bombe
            # veya koni üzerinde olabilir (etek tabanı gövde aralığının dışındadır).
            host_id = getattr(sup, "host_component_id", None)
            host_type, host = None, None
            if host_id:
                if host_id in shells_by_id:
                    host_type, host = "shell", shells_by_id[host_id]
                elif sup.type != "saddle":
                    head = next((h for h in project.heads if h.head_id == host_id), None)
                    cone = next((c for c in project.cones if c.cone_id == host_id), None)
                    if head is not None:
                        host_type, host = "head", head
                    elif cone is not None:
                        host_type, host = "cone", cone
                if host is None:
                    if sup.type == "saddle":
                        blocked(f"Support host component '{host_id}' is not a shell section.")
                    else:
                        blocked(f"Support host component '{host_id}' is not a shell, head or cone of the project.")
                    continue
            elif len(shells_by_id) == 1:
                host_type, host = "shell", next(iter(shells_by_id.values()))
            else:
                blocked("Multiple shell sections exist; support.host_component_id is required.")
                continue
            host_id = host.section_id if host_type == "shell" else (host.head_id if host_type == "head" else host.cone_id)
            # Hesap paketlerine geçen "shell": host gövde; bombe/koni hostunda ilk gövde (yalnız uyumluluk).
            shell = host if host_type == "shell" else next(iter(shells_by_id.values()))
            host_axial_length = component_axial_length(
                type("Ref", (), {"component_type": host_type, "component_id": host_id})
            ) or shell.tangent_length

            host_start = component_global_start(host_type, host_id)
            if sup.type == "saddle":
                if host_start is None:
                    blocked(
                        f"Shell host '{shell.section_id}' cannot be resolved uniquely in component_sequence; "
                        "the sequence may contain missing, unknown, or duplicate component references."
                    )
                    continue
                host_end = host_start + shell.tangent_length
                if not (host_start <= sup.location_mm <= host_end):
                    blocked(
                        f"Support position {sup.location_mm:g} mm is outside host shell "
                        f"'{shell.section_id}' global interval [{host_start:g}, {host_end:g}] mm."
                    )
                    continue
            elif sequence_all and host_start is None:
                # Etek/ayak için konum-aralığı kapısı YOK; ama zincir tanımlıysa host
                # zincirde tek ve çözümlenebilir olmalı (tutarsız proje).
                blocked(
                    f"Support host '{host_id}' cannot be resolved uniquely in component_sequence; "
                    "the sequence may contain missing, unknown, or duplicate component references."
                )
                continue

            orchestration_warnings = []
            host_d_min, host_d_max = _host_outer_diameters(project, host_type, host)
            if sup.type == "skirt" and sup.diameter_mm and host_d_min:
                if sup.diameter_mm < 0.85 * host_d_min or sup.diameter_mm > 1.15 * host_d_max:
                    orchestration_warnings.append(
                        f"Etek çapı {sup.diameter_mm:g} mm, host '{host_id}' dış çap aralığından "
                        f"[{host_d_min:g}, {host_d_max:g}] mm (±%15 tolerans) sapıyor; etek-host süreklilik/"
                        f"geometri uyumu mühendis kontrolü ister."
                    )
            if sup.type == "leg" and sup.support_radius_mm and host_d_max:
                if sup.support_radius_mm > host_d_max:  # r > 2 x host dış yarıçapı
                    blocked(
                        f"Ayak dağılım yarıçapı {sup.support_radius_mm:g} mm, host '{host_id}' dış "
                        f"yarıçapının ({host_d_max / 2.0:g} mm) 2 katından büyük; gerçekçi değil, girdiyi düzeltin."
                    )
                    continue
                if sup.support_radius_mm > host_d_max / 2.0 * 1.25:
                    orchestration_warnings.append(
                        f"Ayak dağılım yarıçapı {sup.support_radius_mm:g} mm, host dış yarıçapından "
                        f"({host_d_max / 2.0:g} mm) belirgin büyük; konsol/traversli ayak düzeni doğrulanmalı."
                    )
            orientation = getattr(getattr(project, "orientation", None), "value", getattr(project, "orientation", None))
            if orientation == "vertical" and sup.type == "saddle":
                orchestration_warnings.append("Dikey kapta eyer desteği: tipik düzen değildir (eyer yatay kaplar içindir); tip seçimi doğrulanmalı.")
            if orientation == "horizontal" and sup.type in ("skirt", "leg"):
                orchestration_warnings.append(f"Yatay kapta {sup.type} desteği: tipik düzen değildir (yatay kaplarda eyer kullanılır); tip seçimi doğrulanmalı.")

            # Yük zarfı: alternatif yük durumları (rüzgâr / deprem / hidrotest ...) TOPLANMAZ.
            manual_moment = getattr(sup, "overturning_moment_Nmm", 0.0) or 0.0
            env = _support_load_envelope(project, sup.location_mm)
            global_moment = env["moment_Nmm"]
            global_horizontal = env["horizontal_N"]
            overturning_moment = max(manual_moment, global_moment)
            if overturning_moment <= 0.0:
                moment_source = "none"
            elif manual_moment >= global_moment:
                moment_source = "manual (support.overturning_moment_Nmm)"
            else:
                moment_source = f"load_case:{env['moment_case']}"
            # Ağırlık durumları: basma = hidrotest (metal + su) + en büyük aşağı Fz;
            # kaldırma/uplift = boş metal + en küçük (yukarı) Fz.
            compression_weight_N = weight_hydro_N + max(0.0, env["fz_max_N"])
            uplift_weight_N = max(0.0, weight_empty_N + min(0.0, env["fz_min_N"]))
            payload = {
                "support": {
                    "tag": sup.support_id,
                    "host_component_id": host_id,
                    "type": sup.type,
                    "location_mm": sup.location_mm,
                    "width_mm": sup.width_mm,
                    "height_mm": sup.height_mm,
                    "diameter_mm": getattr(sup, "diameter_mm", None),
                    "thickness_mm": getattr(sup, "thickness_mm", None),
                    "skirt_allowable_compressive_MPa": getattr(sup, "skirt_allowable_compressive_MPa", None),
                    "skirt_weld_efficiency": getattr(sup, "skirt_weld_efficiency", None),
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
                    "saddle_stiffened": getattr(sup, "saddle_stiffened", None),
                    "zick_K1": getattr(sup, "zick_K1", None),
                    "zick_K2": getattr(sup, "zick_K2", None),
                    "zick_K3": getattr(sup, "zick_K3", None),
                    "zick_K6": getattr(sup, "zick_K6", None),
                    "zick_K7": getattr(sup, "zick_K7", None),
                },
                "shell": shell,
                "vessel_length": host_axial_length if host_type != "shell" else shell.tangent_length,
                "host_axial_start_mm": host_start,
                # total_weight_N = BASMA durumu (hidrotest: metal + su); geriye dönük uyumlu anahtar.
                # empty_weight_N = KALDIRMA/uplift için boş metal ağırlığı (hesap paketleri henüz okumuyor).
                "total_weight_N": compression_weight_N,
                "empty_weight_N": uplift_weight_N,
                # Hesap paketlerinin okuduğu ad: yükselme/çekme kontrolü boş (min) ağırlıkla yapılır.
                "min_weight_N": uplift_weight_N,
                "host_component_type": host_type,
                "host_outer_diameter_mm": host_d_max,
                "materials": project.materials,
                "design_conditions": project.design_conditions,
                "overturning_moment_Nmm": overturning_moment,
                "global_horizontal_load_N": global_horizontal,
                "global_overturning_moment_Nmm": global_moment,
                "skirt_material_id": sup.material_id,
            }
            if sup.type == "saddle":
                # Zick girdileri: tüm eyer konumları (>=3 → kapsam dışı, tek → hesaplanmaz),
                # teğet-teğet L ve teğet başlangıcı (zincirden), başlık derinliği H (başlık tanımından).
                from supports import formulas as _saddle_formulas

                saddle_notes = []
                host_saddles = saddles_by_host.get(shell.section_id, [])
                payload["saddle_positions_mm"] = sorted(s.location_mm for s in host_saddles)
                payload["weight_case"] = "hidrotest (metal + su) + en büyük aşağı Fz — basma durumu"
                _pos, _t_start, _t_end, _n_cyl, _resolvable = 0.0, None, None, 0, True
                for _ref in sequence_all:
                    _len = component_axial_length(_ref)
                    if _len is None:
                        _resolvable = False
                        break
                    if _ref.component_type in ("shell", "cone"):
                        _t_start = _pos if _t_start is None else _t_start
                        _t_end = _pos + _len
                        _n_cyl += 1
                    _pos += _len
                if not sequence_all:
                    _t_start, _t_end, _n_cyl = 0.0, shell.tangent_length, 1
                if _resolvable and _t_start is not None:
                    payload["tangent_start_mm"] = _t_start
                    payload["vessel_length"] = _t_end - _t_start
                if _n_cyl > 1:
                    saddle_notes.append(
                        "Zick sabit et kalınlığı varsayar; teğet-teğet aralıkta birden fazla silindirik/konik "
                        "bileşen var — host gövde kalınlığı kullanıldı, diğer bileşenler ayrıca doğrulanmalı."
                    )
                _seq_head_ids = {_r.component_id for _r in sequence_all if _r.component_type == "head"}
                _heads = [_h for _h in project.heads if not _seq_head_ids or _h.head_id in _seq_head_ids]
                if _heads:
                    try:
                        _depths = [_saddle_formulas.zick_head_depth(_h) for _h in _heads]
                        payload["head_depth_mm"] = max(_depths)
                        if max(_depths) - min(_depths) > 0.01 * max(max(_depths), 1.0):
                            saddle_notes.append(
                                "Başlık derinlikleri farklı; Zick simetrik başlık varsayar — en büyük H kullanıldı."
                            )
                    except ValueError:
                        pass
                    payload["head_thickness_mm"] = min(
                        _h.nominal_thickness - _h.internal_corrosion_allowance - _h.external_corrosion_allowance
                        for _h in _heads
                    )
                _weld = project.get_weld(shell.weld_joint_id) if shell.weld_joint_id else None
                payload["joint_efficiency"] = _weld.joint_efficiency if _weld else None
                r = calc.check_saddle(payload)
                for _note in saddle_notes:
                    r.add_warning(_note)
            elif sup.type == "skirt":
                r = calc.check_skirt(payload)
            elif sup.type == "leg":
                for _f in _LEG_DETAIL_FIELDS:
                    payload["support"][_f] = getattr(sup, _f, None)
                r = calc.check_leg_support(payload)
                # leg_section_type boş → yalnız leg_stress (eski boru-ayak davranışı);
                # dolu → dört alt kontrol de üretilir ve leg_stress özetine bağlanır.
                leg_details = calc.check_leg_detail(payload)
                calc.summarize_leg(r, leg_details)
                if not leg_details and any(
                    getattr(sup, _f, None) is not None
                    for _f in _LEG_DETAIL_FIELDS
                    if _f not in ("leg_pad_length_mm", "leg_pad_width_mm", "leg_pad_thickness_mm")
                ):
                    r.add_warning(
                        "Ayak ped/kaynak/taban plakası/WRC alanları girildi ancak leg_section_type boş: "
                        "alt kontroller (leg_section_check, leg_weld_check, base_plate_check, "
                        "wrc_local_stress) ÇALIŞTIRILMADI; yalnız boru-ayak leg_stress hesaplandı."
                    )
            else:
                continue

            r.add_intermediate("host_component_id", host_id, "-", f"Resolved support host ({host_type})")
            if host_start is not None:
                r.add_intermediate("host_axial_start", host_start, "mm", "Resolved host start on global vessel axis")
            r.add_intermediate("global_horizontal_load", global_horizontal, "N", "Envelope (max over load cases) horizontal external load")
            r.add_intermediate("global_overturning_moment", global_moment, "N·mm", "Envelope (max over load cases) moment about support location")
            r.add_intermediate("governing_moment_source", moment_source, "-", "Governing overturning-moment source (manual vs load case)")
            r.add_intermediate("governing_load_case", env["moment_case"] or "-", "-", "Load case governing the external-load moment envelope")
            r.add_intermediate("compression_weight_N", compression_weight_N, "N", "Compression weight: hydrotest (metal + water) + max downward Fz")
            r.add_intermediate("empty_weight_N", uplift_weight_N, "N", "Uplift/lifting weight: empty metal + min Fz")
            r.add_intermediate("hydrotest_water_mass_kg", water_mass_kg, "kg", "Water mass = rho * inner volume (rho = 1000 kg/m3, K4)")
            if global_moment > 0.0:
                r.add_assumption(
                    "Global support action derived from load-case external loads as an ENVELOPE (max over "
                    "load cases; alternative cases such as wind and seismic are NOT summed). Within a case: "
                    "moment = SRSS(sum Mx, sum My) + sum(H x lever), arithmetic add is conservative; "
                    "governing case: " + str(env["moment_case"]) + ". Code-specific combination review remains required."
                )
            for note in env["notes"]:
                r.add_assumption("K4: " + note)
            if env["fz_max_N"] != 0.0 or env["fz_min_N"] != 0.0:
                r.add_assumption(
                    "K4: Fz sign convention is not defined in the domain; Fz > 0 assumed downward (adds to "
                    "compression weight), Fz < 0 upward (reduces uplift weight)."
                )
            r.add_assumption(
                f"K4: Destek yükü iki ağırlık durumundan türetildi: boş metal "
                f"{vm.total_metal_mass_kg:.0f} kg ve hidrotest (metal + su, rho=1000 kg/m3, iç hacim "
                f"{vm.total_inner_volume_m3:.3f} m3 -> {water_mass_kg:.0f} kg su). Basma kontrolü hidrotest "
                f"ağırlığıyla, kaldırma/uplift boş ağırlıkla ilgilidir; işletme sıvısı, izolasyon ve iç "
                f"ekipman ağırlıkları dahil DEĞİL."
            )
            for w in orchestration_warnings:
                r.add_warning(w)
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
            if sup.type == "leg":
                for _d in leg_details:
                    _d.add_intermediate("host_component_id", host_id, "-", f"Resolved support host ({host_type})")
                    results.append(_d)

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
        self._apply_material_data_check(result, mat, dc, cone.nominal_thickness)

        result.material_properties_used = {
            "designation": mat.material_designation,
            "allowable_stress": S,
            "yield_strength": mat.yield_strength,
            "tensile_strength": mat.tensile_strength,
            "source_reference": mat.source_reference,
        }

        return result


__all__ = ["ASMEVIII1DesignCode"]
