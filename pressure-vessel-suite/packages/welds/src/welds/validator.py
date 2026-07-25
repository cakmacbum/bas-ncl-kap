"""Kaynak doğrulama motoru — ASME VIII-1 kaynak + NDT kontrolleri (kaynak §9).

K5 kuralı: Herhesap denetlenebilir — ara değerler + madde referansı saklanır.
K7 kuralı: Domain modelinden bağımsız; hesap kuralları burada tanımlanır.

Kontroller:
  - NDT kapsamı ↔ kaynak verimi (joint efficiency) uyumu
  - Tam nüfuziyet gerekli mi
  - Nozul kaynak tipi hesapta kabul edilen tip mi
  - WPS/PQR bilgileri girilmiş mi
  - Kaynakçı yeterliliği eklenmiş mi
  - PWHT gerekliliği değerlendirilmiş mi

Referans: ASME BPVC Section VIII Division 1, 2025 Edition
  - UW-11: NDE requirements and joint efficiency
  - UW-12: Weld joint categories (A, B, C, D)
  - UCS-56: PWHT requirements
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus
from domain.welds import WeldJoint


# ── NDE → Joint Efficiency eşleştirmesi (ASME UW-11) ─────────────────────────
# Tablo UW-12(b): NDE kapsamına göre izin verilen joint efficiency
NDE_EFFICIENCY_MAP: Dict[str, Dict[str, float]] = {
    "RT-1": {"full": 1.0, "spot": 0.85, "none": 0.70},
    "RT-2": {"full": 1.0, "spot": 0.85, "none": 0.70},
    "RT-3": {"full": 0.90, "spot": 0.85, "none": 0.70},
    "UT": {"full": 1.0, "spot": 0.85, "none": 0.70},
    "VT": {"full": 0.70, "spot": 0.70, "none": 0.70},
    "MT": {"full": 0.70, "spot": 0.70, "none": 0.70},
    "PT": {"full": 0.70, "spot": 0.70, "none": 0.70},
}

# ASME UW-11(a)(5)(b): Full RT/UT gerektiren durumlar
FULL_NDE_REQUIRED_CATEGORIES = {"A", "B"}  # Category A ve B dikişlerinde full RT gerekli
FULL_NDE_REQUIRED_THICKNESS_mm = 38.1  # 1.5 in üzeri kalınlıkta full RT zorunlu

# Kategori D (nozul) dikişlerinde tam nüfuziyet genellikle zorunlu
CATEGORY_D_FULL_PENETRATION = True


@dataclass
class WeldValidationInput:
    """Kaynak doğrulama girdisi."""

    weld: WeldJoint
    connected_component_thickness: float = 0.0  # mm
    is_nozzle_weld: bool = False
    nozzle_tag: str = ""
    design_pressure: float = 0.0  # MPa
    design_temperature: float = 0.0  # °C
    material_p_number: int = 0  # ASME IX P-Number
    requires_impact_test: bool = False


@dataclass
class WeldCheckResult:
    """Tek bir kontrol sonucu."""

    check_name: str
    status: CalculationStatus
    message: str
    clause_reference: str = ""
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None


@dataclass
class WeldValidationResult:
    """Kaynak doğrulama sonucu."""

    joint_id: str
    joint_type: str
    status: CalculationStatus = CalculationStatus.NOT_CALCULATED

    # Kontrol sonuçları
    checks: List[WeldCheckResult] = field(default_factory=list)

    # Uyarılar
    warnings: List[str] = field(default_factory=list)

    # Öneriler
    recommendations: List[str] = field(default_factory=list)

    # NDE bilgileri
    nde_method: str = ""
    nde_extent: str = ""
    required_joint_efficiency: float = 1.0
    actual_joint_efficiency: float = 1.0

    # Madde referansı
    clause_reference: str = "UW-11/UW-12"

    def to_dict(self) -> Dict:
        return {
            "joint_id": self.joint_id,
            "joint_type": self.joint_type,
            "status": self.status.value,
            "checks": [
                {
                    "name": c.check_name,
                    "status": c.status.value,
                    "message": c.message,
                    "clause_reference": c.clause_reference,
                }
                for c in self.checks
            ],
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "nde_method": self.nde_method,
            "nde_extent": self.nde_extent,
            "required_joint_efficiency": self.required_joint_efficiency,
            "actual_joint_efficiency": self.actual_joint_efficiency,
        }


def _parse_nde_extent(nde_extent: Optional[str]) -> str:
    """NDE kapsamını normalize et."""
    if not nde_extent:
        return "none"
    extent_lower = nde_extent.lower().strip()
    if "100" in extent_lower or "full" in extent_lower:
        return "full"
    elif "spot" in extent_lower:
        return "spot"
    else:
        return "none"


def _get_max_allowed_efficiency(nde_method: Optional[str], nde_extent: Optional[str]) -> float:
    """NDE yöntemine ve kapsamına göre izin verilen maksimum joint efficiency.

    ASME UW-11 tablolarına göre.
    """
    if not nde_method:
        return 0.70  # NDE yoksa maksimum 0.70

    method = nde_method.upper().strip()
    extent = _parse_nde_extent(nde_extent)

    # Bilinen NDE yöntemleri
    for key in NDE_EFFICIENCY_MAP:
        if key in method:
            return NDE_EFFICIENCY_MAP[key].get(extent, 0.70)

    return 0.70  # Bilinmeyen yöntem → konservatif


def check_nde_joint_efficiency(inp: WeldValidationInput) -> WeldCheckResult:
    """NDT kapsamı ↔ kaynak verimi uyumu kontrolü (UW-11).

    ASME UW-11: Belirli bir joint efficiency elde etmek için
    karşılık gelen NDE kapsamı gerekir.
    """
    weld = inp.weld

    # Gerçek joint efficiency
    actual_je = weld.joint_efficiency

    # NDE'den beklenen maksimum joint efficiency
    max_allowed = _get_max_allowed_efficiency(weld.nde_method, weld.nde_extent)

    # Düşük NDE ile yüksek joint efficiency kullanılamaz
    if actual_je > max_allowed + 0.001:  # Tolerans
        return WeldCheckResult(
            check_name="nde_joint_efficiency",
            status=CalculationStatus.FAIL,
            message=(
                f"Kaynak verimi (E={actual_je:.2f}), NDE kapsamına göre "
                f"izin verilen maksimum değerden ({max_allowed:.2f}) yüksek. "
                f"NDE: {weld.nde_method or 'None'}, Kapsam: {weld.nde_extent or 'None'}."
            ),
            clause_reference="UW-11(a)",
            expected_value=max_allowed,
            actual_value=actual_je,
        )

    return WeldCheckResult(
        check_name="nde_joint_efficiency",
        status=CalculationStatus.PASS,
        message=(
            f"Kaynak verimi (E={actual_je:.2f}) NDE kapsamına uygun "
            f"(maks. izin verilen: {max_allowed:.2f})."
        ),
        clause_reference="UW-11(a)",
        expected_value=max_allowed,
        actual_value=actual_je,
    )


def check_full_penetration(inp: WeldValidationInput) -> WeldCheckResult:
    """Tam nüfuziyet kontrolü (UW-11(a)(2)).

    ASME'de basınç taşıyan dikişlerin çoğu tam nüfuziyet gerektirir.
    """
    weld = inp.weld

    # Kategori A ve B dikişleri tam nüfuziyet gerektirir
    if weld.weld_category in FULL_NDE_REQUIRED_CATEGORIES:
        if not weld.full_penetration:
            return WeldCheckResult(
                check_name="full_penetration",
                status=CalculationStatus.FAIL,
                message=(
                    f"Kategori {weld.weld_category} dikişi tam nüfuziyet gerektirir "
                    f"(full_penetration=False)."
                ),
                clause_reference="UW-11(a)(2)",
            )

    # Kategori D (nozul) dikişleri de tam nüfuziyet gerektirir
    if weld.weld_category == "D" and CATEGORY_D_FULL_PENETRATION:
        if not weld.full_penetration:
            return WeldCheckResult(
                check_name="full_penetration",
                status=CalculationStatus.FAIL,
                message=(
                    "Kategori D (nozul) dikişi tam nüfuziyet gerektirir "
                    "(full_penetration=False)."
                ),
                clause_reference="UW-11(a)(2)",
            )

    return WeldCheckResult(
        check_name="full_penetration",
        status=CalculationStatus.PASS,
        message=f"Tam nüfuziyet kontrolü geçti (full_penetration={weld.full_penetration}).",
        clause_reference="UW-11(a)(2)",
    )


def check_wps_pqr(inp: WeldValidationInput) -> WeldCheckResult:
    """WPS/PQR bilgileri kontrolü.

    Kaynak prosedürü (WPS) ve prosedür yeterlilik kaydı (PQR) olmalı.
    Eksikse REVIEW_REQUIRED.
    """
    weld = inp.weld

    missing = []
    if not weld.wps_number:
        missing.append("WPS")
    if not weld.pqr_number:
        missing.append("PQR")

    if missing:
        return WeldCheckResult(
            check_name="wps_pqr",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"Eksik kaynak prosedür bilgisi: {', '.join(missing)}. "
                f"Mühendis incelemesi gerekli."
            ),
            clause_reference="ASME IX, QW-100",
        )

    return WeldCheckResult(
        check_name="wps_pqr",
        status=CalculationStatus.PASS,
        message=f"WPS ({weld.wps_number}) ve PQR ({weld.pqr_number}) tanımlı.",
        clause_reference="ASME IX, QW-100",
    )


def check_welder_qualification(inp: WeldValidationInput) -> WeldCheckResult:
    """Kaynakçı yeterliliği kontrolü.

    Kaynakçı yeterlilik referansı olmalı.
    Eksikse REVIEW_REQUIRED.
    """
    weld = inp.weld

    if not weld.welder_qualification:
        return WeldCheckResult(
            check_name="welder_qualification",
            status=CalculationStatus.REVIEW_REQUIRED,
            message="Kaynakçı yeterlilik referansı girilmemiş. Mühendis incelemesi gerekli.",
            clause_reference="ASME IX, QW-300",
        )

    return WeldCheckResult(
        check_name="welder_qualification",
        status=CalculationStatus.PASS,
        message=f"Kaynakçı yeterliliği tanımlı: {weld.welder_qualification}.",
        clause_reference="ASME IX, QW-300",
    )


def check_pwht(inp: WeldValidationInput) -> WeldCheckResult:
    """PWHT (Post Weld Heat Treatment) gereklilik kontrolü (UCS-56).

    ASME VIII-1 UCS-56: P-1, P-3 gibi bazı malzeme grupları ve belirli
    kalınlıklar üzerinde PWHT zorunlu.
    """
    weld = inp.weld
    thickness = inp.connected_component_thickness

    # Basitleştirilmiş PWHT gereklilik kuralları (UCS-56 Tablo UCS-56.1)
    # P-Number 1 (karbon çeliği) için: t > 38 mm → PWHT zorunlu
    pwht_required = False
    reason = ""

    if inp.material_p_number in (1, 3) and thickness > 38.1:
        pwht_required = True
        reason = (
            f"P-Number {inp.material_p_number}, kalınlık {thickness:.1f} mm > 38.1 mm "
            f"→ UCS-56'ya göre PWHT zorunlu."
        )
    elif inp.material_p_number in (1, 3) and thickness > 25.4:
        pwht_required = True
        reason = (
            f"P-Number {inp.material_p_number}, kalınlık {thickness:.1f} mm > 25.4 mm "
            f"→ UCS-56'ya göre PWHT önerilir."
        )

    # PWHT zorunlu ama değerlendirilmemiş
    if pwht_required and weld.pwht_required is None:
        return WeldCheckResult(
            check_name="pwht",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"PWHT gerekliliği değerlendirilmemiş. {reason}"
            ),
            clause_reference="UCS-56",
        )

    # PWHT zorunlu ama yapılmayacak
    if pwht_required and weld.pwht_required is False:
        return WeldCheckResult(
            check_name="pwht",
            status=CalculationStatus.FAIL,
            message=(
                f"PWHT zorunlu ancak pwht_required=False olarak işaretlenmiş. {reason}"
            ),
            clause_reference="UCS-56",
        )

    # PWHT gerekmiyor veya doğru işaretlenmiş
    return WeldCheckResult(
        check_name="pwht",
        status=CalculationStatus.PASS,
        message=(
            f"PWHT kontrolü geçti (pwht_required={weld.pwht_required})."
            + (f" {reason}" if reason else "")
        ),
        clause_reference="UCS-56",
    )


def check_weld_category(inp: WeldValidationInput) -> WeldCheckResult:
    """Kaynak kategorisi kontrolü (UW-12).

    ASME UW-12: Dikiş kategorileri A, B, C, D.
    Basınçlı kap bileşenlerinde kategori tanımlı olmalı.
    """
    weld = inp.weld

    if not weld.weld_category:
        return WeldCheckResult(
            check_name="weld_category",
            status=CalculationStatus.REVIEW_REQUIRED,
            message="Kaynak kategorisi tanımlanmamış. UW-12'ye göre kategori belirlenmeli.",
            clause_reference="UW-12",
        )

    valid_categories = {"A", "B", "C", "D"}
    if weld.weld_category not in valid_categories:
        return WeldCheckResult(
            check_name="weld_category",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"Geçersiz kaynak kategorisi: '{weld.weld_category}'. "
                f"UW-12'ye göre A, B, C veya D olmalı."
            ),
            clause_reference="UW-12",
        )

    return WeldCheckResult(
        check_name="weld_category",
        status=CalculationStatus.PASS,
        message=f"Kaynak kategorisi '{weld.weld_category}' geçerli.",
        clause_reference="UW-12",
    )


def check_ndt_extent(inp: WeldValidationInput) -> WeldCheckResult:
    """NDE kapsamı kontrolü.

    Kaynak kalınlığı belirli bir eşiği aştığında full RT/UT zorunlu.
    """
    weld = inp.weld
    thickness = inp.connected_component_thickness

    # Kalınlık kontrolü (UW-11(a)(5)(b))
    if thickness > FULL_NDE_REQUIRED_THICKNESS_mm:
        extent = _parse_nde_extent(weld.nde_extent)
        if extent != "full":
            return WeldCheckResult(
                check_name="ndt_extent",
                status=CalculationStatus.REVIEW_REQUIRED,
                message=(
                    f"Kalınlık {thickness:.1f} mm > {FULL_NDE_REQUIRED_THICKNESS_mm} mm "
                    f"olduğu için full NDE gerekebilir. Mevcut kapsam: '{weld.nde_extent}'. "
                    f"UW-11(a)(5)(b)'ye göre değerlendirilmeli."
                ),
                clause_reference="UW-11(a)(5)(b)",
            )

    return WeldCheckResult(
        check_name="ndt_extent",
        status=CalculationStatus.PASS,
        message=f"NDE kapsamı '{weld.nde_extent or 'None'}' yeterli.",
        clause_reference="UW-11(a)(5)(b)",
    )


def validate_weld(inp: WeldValidationInput) -> WeldValidationResult:
    """Tüm kaynak kontrollerini çalıştır.

    Args:
        inp: Kaynak doğrulama girdisi.

    Returns:
        WeldValidationResult.
    """
    weld = inp.weld

    result = WeldValidationResult(
        joint_id=weld.joint_id,
        joint_type=weld.joint_type,
        nde_method=weld.nde_method or "",
        nde_extent=weld.nde_extent or "",
        actual_joint_efficiency=weld.joint_efficiency,
    )

    # Kontrolleri çalıştır
    checks = [
        check_weld_category(inp),
        check_nde_joint_efficiency(inp),
        check_full_penetration(inp),
        check_ndt_extent(inp),
        check_wps_pqr(inp),
        check_welder_qualification(inp),
        check_pwht(inp),
    ]

    result.checks = checks

    # NDE bilgisi
    result.required_joint_efficiency = _get_max_allowed_efficiency(
        weld.nde_method, weld.nde_extent
    )

    # Genel durum: en kötü durum
    has_fail = any(c.status == CalculationStatus.FAIL for c in checks)
    has_review = any(c.status == CalculationStatus.REVIEW_REQUIRED for c in checks)
    has_not_calc = any(c.status == CalculationStatus.NOT_CALCULATED for c in checks)

    if has_fail:
        result.status = CalculationStatus.FAIL
    elif has_review:
        result.status = CalculationStatus.REVIEW_REQUIRED
    elif has_not_calc:
        result.status = CalculationStatus.NOT_CALCULATED
    else:
        result.status = CalculationStatus.PASS

    # Uyarıları topla
    for c in checks:
        if c.status == CalculationStatus.FAIL:
            result.warnings.append(f"[{c.check_name}] {c.message}")
        elif c.status == CalculationStatus.REVIEW_REQUIRED:
            result.recommendations.append(f"[{c.check_name}] {c.message}")

    return result


def build_weld_validation_result(inp: WeldValidationInput) -> CalculationResult:
    """Kaynak doğrulama sonucunu CalculationResult formatında döndür.

    Orchestrator entegrasyonu için.

    Args:
        inp: Kaynak doğrulama girdisi.

    Returns:
        CalculationResult.
    """
    weld = inp.weld

    result = CalculationResult(
        component_id=weld.joint_id,
        component_type="weld",
        calculation_type="weld_validation",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UW-11/UW-12",
        formula_reference="Weld Joint Validation",
    )

    validation = validate_weld(inp)

    # Girdi anlık görüntüsü
    result.input_snapshot = {
        "joint_id": weld.joint_id,
        "joint_type": weld.joint_type,
        "weld_category": weld.weld_category,
        "joint_efficiency": weld.joint_efficiency,
        "nde_method": weld.nde_method,
        "nde_extent": weld.nde_extent,
        "full_penetration": weld.full_penetration,
        "wps_number": weld.wps_number,
        "pqr_number": weld.pqr_number,
        "welder_qualification": weld.welder_qualification,
        "pwht_required": weld.pwht_required,
    }

    # Ara değerler
    result.add_intermediate(
        "actual_joint_efficiency",
        validation.actual_joint_efficiency,
        "-",
        "Kaynak verimi (E)",
    )
    result.add_intermediate(
        "max_allowed_efficiency",
        validation.required_joint_efficiency,
        "-",
        "NDE kapsamına göre izin verilen maks. E",
    )
    result.add_intermediate(
        "nde_method",
        validation.nde_method,
        "-",
        "NDE yöntemi",
    )
    result.add_intermediate(
        "nde_extent",
        validation.nde_extent,
        "-",
        "NDE kapsamı",
    )

    # Kontrol sonuçlarını ara değer olarak ekle
    for check in validation.checks:
        result.add_intermediate(
            check.check_name,
            check.status.value,
            "-",
            check.message,
        )

    # Sonuç
    result.final_result = validation.actual_joint_efficiency
    result.final_result_unit = "-"
    result.allowable_limit = validation.required_joint_efficiency
    result.allowable_limit_unit = "-"
    result.utilization_ratio = (
        validation.actual_joint_efficiency / validation.required_joint_efficiency
        if validation.required_joint_efficiency > 0
        else 0.0
    )

    result.status = validation.status

    for w in validation.warnings:
        result.add_warning(w)
    for r in validation.recommendations:
        result.add_assumption(r)

    return result


__all__ = [
    "WeldValidationInput",
    "WeldValidationResult",
    "WeldCheckResult",
    "validate_weld",
    "build_weld_validation_result",
    "check_nde_joint_efficiency",
    "check_full_penetration",
    "check_wps_pqr",
    "check_welder_qualification",
    "check_pwht",
    "check_weld_category",
    "check_ndt_extent",
    "NDE_EFFICIENCY_MAP",
]
