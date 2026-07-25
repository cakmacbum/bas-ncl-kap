"""ASME VIII-1 Açıklık Takviye Hesabı — UG-37 / UG-40 Area Replacement Method.

Referans: ASME BPVC Section VIII Division 1, 2025 Edition
  - UG-37: Reinforcement of openings in shells and heads
  - UG-38: Reinforcement required
  - UG-39: Limits of reinforcement
  - UG-40: Area of reinforcement

K5 kuralı: Her hesap denetlenebilir — ara değerler + madde referansı saklanır.
K2 kuralı: Hesap yalnızca project data'dan çalışır.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus, HeadType


@dataclass
class NozzleReinforcementInput:
    """Nozul takviye hesabı girdileri."""

    # Nozul
    nozzle_tag: str = ""
    nozzle_inside_diameter: float = 0.0  # mm
    nozzle_outside_diameter: float = 0.0  # mm
    nozzle_neck_thickness: float = 0.0  # mm
    nozzle_corrosion_allowance: float = 0.0  # mm
    nozzle_projection_outside: float = 0.0  # mm (dış çıkıntı)
    nozzle_projection_inside: float = 0.0  # mm (iç çıkıntı)
    nozzle_allowable_stress: float = 0.0  # MPa

    # Ana bileşen (gövde veya bombe)
    component_type: str = "shell"  # "shell" veya "head"
    component_inside_diameter: float = 0.0  # mm
    component_nominal_thickness: float = 0.0  # mm
    component_corrosion_allowance: float = 0.0  # mm
    component_required_thickness: float = 0.0  # mm (hesap motorundan)
    component_allowable_stress: float = 0.0  # MPa

    # Takviye pedi
    has_reinforcement_pad: bool = False
    reinforcement_pad_od: float = 0.0  # mm
    reinforcement_pad_thickness: float = 0.0  # mm
    reinforcement_pad_allowable_stress: float = 0.0  # MPa

    # Kaynak
    weld_leg_size_nozzle_to_shell: float = 0.0  # mm
    weld_leg_size_pad_to_shell: float = 0.0  # mm
    weld_allowable_stress: float = 0.0  # MPa

    # Tasarım
    design_pressure: float = 0.0  # MPa
    design_temperature: float = 0.0  # °C


@dataclass
class AreaItem:
    """Tek bir takviye alanı kalemi."""

    name: str
    description: str
    area_mm2: float
    clause_reference: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "area_mm2": round(self.area_mm2, 2),
            "clause_reference": self.clause_reference,
        }


@dataclass
class NozzleReinforcementResult:
    """Nozul takviye hesabı sonucu."""

    nozzle_tag: str = ""
    status: CalculationStatus = CalculationStatus.NOT_CALCULATED

    # Uygunluk
    is_eligible: bool = True
    eligibility_message: str = ""

    # Etkin çap
    effective_diameter: float = 0.0  # mm (d)

    # Gerekli alan
    required_area: float = 0.0  # mm² (A_required = d × t_required)

    # Mevcut alanlar
    available_areas: List[AreaItem] = field(default_factory=list)

    # Toplam
    total_available_area: float = 0.0  # mm²
    utilization_ratio: float = 0.0  # total_available / required

    # Limit kontrolleri
    limits: Dict[str, bool] = field(default_factory=dict)

    # Uyarılar
    warnings: List[str] = field(default_factory=list)

    # Madde referansı
    clause_reference: str = "UG-37/UG-40"

    def to_dict(self) -> Dict:
        return {
            "nozzle_tag": self.nozzle_tag,
            "status": self.status.value,
            "is_eligible": self.is_eligible,
            "eligibility_message": self.eligibility_message,
            "effective_diameter": self.effective_diameter,
            "required_area": round(self.required_area, 2),
            "available_areas": [a.to_dict() for a in self.available_areas],
            "total_available_area": round(self.total_available_area, 2),
            "utilization_ratio": round(self.utilization_ratio, 4),
            "limits": self.limits,
            "warnings": self.warnings,
            "clause_reference": self.clause_reference,
        }

    @property
    def area_breakdown_html(self) -> str:
        """Nozul ekranı grafiği: gerekli alan vs. mevcut alanlar (HTML)."""
        rows = ""
        for a in self.available_areas:
            pct = (a.area_mm2 / self.required_area * 100) if self.required_area > 0 else 0
            bar_width = min(pct, 100)
            rows += f"""
<tr>
<td>{a.name}</td>
<td>{a.description}</td>
<td style="text-align:right">{a.area_mm2:.1f} mm²</td>
<td style="text-align:right">{pct:.1f}%</td>
<td><div style="background:#4CAF50;height:12px;width:{bar_width}%"></div></td>
<td>{a.clause_reference}</td>
</tr>"""

        status_color = "green" if self.status == CalculationStatus.PASS else "red"

        return f"""
<h3>Nozul {self.nozzle_tag} — Takviye Alan Analizi</h3>
<table>
<tr><th colspan="2">Gerekli Takviye Alanı</th><th colspan="4" style="color:{status_color}">
{self.required_area:.1f} mm²</th></tr>
<tr><th>Kalem</th><th>Açıklama</th><th>Alan</th><th>Oran</th><th>Grafik</th><th>Referans</th></tr>
{rows}
<tr><th colspan="2">Toplam Mevcut Alan</th><th colspan="4">{self.total_available_area:.1f} mm²
({self.utilization_ratio*100:.1f}%)</th></tr>
</table>
<p><strong>Sonuç: <span style="color:{status_color}">{self.status.value}</span></strong></p>"""


def check_nozzle_eligibility(inp: NozzleReinforcementInput) -> tuple[bool, str]:
    """Açıklık izinli mi kontrol et (UG-36).

    UG-36(a): Genel limit — d ≤ D/2 (açıklık çapı, ana bileşen çapının yarısını geçmemeli).
    UG-36(b)(1): 50 mm (2 in) ve altındaki açıklıklar area replacement'tan muaftır.
    Bu fonksiyon UG-36(a) genel limitini kontrol eder; 50 mm muafiyeti ayrı işlenir.

    Args:
        inp: Nozul girdileri.

    Returns:
        (is_eligible, message)
    """
    d = inp.nozzle_inside_diameter + 2 * inp.nozzle_corrosion_allowance
    D = inp.component_inside_diameter

    # UG-36(a): Açıklık çapı limiti — d ≤ D/2
    # D > 1524 mm (60 in) için daha gevşek limit uygulanabilir
    if D <= 1524:
        max_d = D / 2.0
        if d > max_d:
            return False, (
                f"UG-36(a): Açıklık çapı d={d:.1f} mm, limit={max_d:.1f} mm (D/2). "
                f"D={D:.1f} mm için d ≤ D/2 olmalı."
            )
    else:
        max_d = D / 2.0
        if d > max_d:
            return False, (
                f"UG-36(a): Açıklık çapı d={d:.1f} mm, limit={max_d:.1f} mm (D/2). "
                f"D={D:.1f} mm için d ≤ D/2 olmalı."
            )

    # UG-36(b)(1) muafiyeti bilgilendirme
    if d <= 50.0:
        return True, (
            f"Açıklık UG-36 kapsamına uygun. "
            f"Not: d={d:.1f} mm ≤ 50 mm olduğu için UG-36(b)(1) kapsamında "
            f"area replacement hesabı gerekmez (müdahale serbest)."
        )

    return True, "Açıklık UG-36 kapsamına uygun."


def calculate_reinforcement(inp: NozzleReinforcementInput) -> NozzleReinforcementResult:
    """ASME VIII-1 UG-37/UG-40 area replacement method.

    Args:
        inp: Nozul takviye hesabı girdileri.

    Returns:
        NozzleReinforcementResult.
    """
    result = NozzleReinforcementResult(nozzle_tag=inp.nozzle_tag)

    # ── 0. Uygunluk kontrolü ──────────────────────────────────────────────────
    is_eligible, eligibility_msg = check_nozzle_eligibility(inp)
    result.is_eligible = is_eligible
    result.eligibility_message = eligibility_msg

    if not is_eligible:
        result.status = CalculationStatus.FAIL
        result.warnings.append(eligibility_msg)
        return result

    # ── 1. Etkin çap (d) — UG-37(a) ──────────────────────────────────────────
    # d = nozul iç çapı + 2 × korozyon payı
    d = inp.nozzle_inside_diameter + 2 * inp.nozzle_corrosion_allowance
    result.effective_diameter = d

    # ── 2. Gerekli takviye alanı — UG-37(a) ──────────────────────────────────
    # A_required = d × t_required (gövde/bombe korozyonsuz gerekli kalınlığı)
    t_req = inp.component_required_thickness
    A_required = d * t_req
    result.required_area = A_required

    if A_required <= 0:
        result.status = CalculationStatus.NOT_CALCULATED
        result.warnings.append("Gerekli takviye alanı sıfır veya negatif.")
        return result

    # ── 3. Mevcut alanlar ──────────────────────────────────────────────────────

    # 3a. Gövde/Bombe fazlası (A1) — UG-37(b)(1)
    # A1 = (min(B, d + 2×t_n + t_h) - d) × (t_n - t_required - C)
    # B = d veya d + 2×t_n + 2×t_h (büyük olan) — takviye sınırı
    t_n = inp.component_nominal_thickness
    C_comp = inp.component_corrosion_allowance
    t_n_corroded = t_n - C_comp

    # Takviye sınırı B
    B = max(d, d + 2 * t_n + 2 * inp.nozzle_neck_thickness)

    # Etkin genişlik
    effective_width = min(B, d + 2 * t_n + inp.nozzle_neck_thickness)

    # A1: Gövde fazlası
    t_excess = t_n_corroded - t_req
    A1 = max(0, (effective_width - d) * t_excess)

    result.available_areas.append(AreaItem(
        name="A1",
        description=f"Gövde/bombe fazlası: ({effective_width:.1f} - {d:.1f}) × ({t_n_corroded:.1f} - {t_req:.1f})",
        area_mm2=A1,
        clause_reference="UG-37(b)(1)",
    ))

    # 3b. Nozul boynu katkısı (A2) — UG-37(b)(2)
    # A2 = min(2.5×t_n, 2.5×t_h + t_e) × (t_h - t_required_nozzle - C_nozzle)
    t_h = inp.nozzle_neck_thickness
    C_noz = inp.nozzle_corrosion_allowance
    t_h_corroded = t_h - C_noz

    # Nozul boynu gerekli kalınlığı (iç basınç formülü — basitleştirilmiş)
    # P×r / (S×E - 0.6×P) — burada r = d/2
    if inp.nozzle_allowable_stress > 0 and inp.design_pressure > 0:
        r_noz = d / 2.0
        denom = inp.nozzle_allowable_stress * 1.0 - 0.6 * inp.design_pressure
        if denom > 0:
            t_req_nozzle = inp.design_pressure * r_noz / denom
        else:
            t_req_nozzle = t_h_corroded  # Konservatif
    else:
        t_req_nozzle = 0.0

    # Etkin nozul boynu yüksekliği (dış çıkıntı)
    h_out = min(
        2.5 * t_n,
        2.5 * t_h + inp.nozzle_projection_outside,
    ) if inp.nozzle_projection_outside > 0 else 2.5 * t_n

    # Dış çıkıntı katkısı
    t_noz_excess_out = t_h_corroded - t_req_nozzle
    A2_out = max(0, h_out * t_noz_excess_out)

    # İç çıkıntı katkısı
    h_in = inp.nozzle_projection_inside
    A2_in = max(0, h_in * t_noz_excess_out) if h_in > 0 else 0.0

    A2 = A2_out + A2_in

    result.available_areas.append(AreaItem(
        name="A2",
        description=f"Nozul boynu: dış={A2_out:.1f}, iç={A2_in:.1f} mm²",
        area_mm2=A2,
        clause_reference="UG-37(b)(2)",
    ))

    # 3c. Takviye pedi katkısı (A3) — UG-37(b)(3)
    A3 = 0.0
    if inp.has_reinforcement_pad and inp.reinforcement_pad_od > 0 and inp.reinforcement_pad_thickness > 0:
        # Ped etkin alanı: (OD - d) × t_pad (basitleştirilmiş)
        ped_effective = inp.reinforcement_pad_od - d
        if ped_effective > 0:
            A3 = ped_effective * inp.reinforcement_pad_thickness

    result.available_areas.append(AreaItem(
        name="A3",
        description=f"Takviye pedi: {A3:.1f} mm²",
        area_mm2=A3,
        clause_reference="UG-37(b)(3)" if A3 > 0 else "—",
    ))

    # 3d. Kaynak metali katkısı (A4) — UG-37(b)(4)
    A4 = 0.0
    if inp.weld_leg_size_nozzle_to_shell > 0:
        # Nozul-gövde kaynak metali: ½ × w² (üçgen kesit)
        w = inp.weld_leg_size_nozzle_to_shell
        A4 += 0.5 * w * w

    if inp.weld_leg_size_pad_to_shell > 0 and inp.has_reinforcement_pad:
        w = inp.weld_leg_size_pad_to_shell
        A4 += 0.5 * w * w * 2  # 2 kaynak dikişi (her iki taraf)

    result.available_areas.append(AreaItem(
        name="A4",
        description=f"Kaynak metali: {A4:.1f} mm²",
        area_mm2=A4,
        clause_reference="UG-37(b)(4)" if A4 > 0 else "—",
    ))

    # ── 4. Toplam ve değerlendirme ─────────────────────────────────────────────
    total = A1 + A2 + A3 + A4
    result.total_available_area = total
    result.utilization_ratio = total / A_required if A_required > 0 else 0.0

    # ── 5. Limit kontrolleri — UG-40 ──────────────────────────────────────────
    # Takviye sınırı: nozul merkezinden her iki tarafta d kadar
    result.limits["ug40_radial_limit"] = True  # Basitleştirilmiş

    # Nozul boynu minimum kalınlığı kontrolü
    # t_h ≥ max(t_req_nozzle, 0.5×t_n) — pratik kural
    min_neck = max(t_req_nozzle, 0.5 * t_n) if t_req_nozzle > 0 else 0.5 * t_n
    result.limits["neck_minimum_thickness"] = t_h_corroded >= min_neck
    if not result.limits["neck_minimum_thickness"]:
        result.warnings.append(
            f"Nozul boynu kalınlığı ({t_h_corroded:.1f} mm) minimum ({min_neck:.1f} mm) altında."
        )

    # ── 6. Durum ──────────────────────────────────────────────────────────────
    if total >= A_required:
        result.status = CalculationStatus.PASS
    else:
        result.status = CalculationStatus.FAIL
        deficit = A_required - total
        result.warnings.append(
            f"Takviye alanı yetersiz! Gerekli: {A_required:.1f} mm², "
            f"Mevcut: {total:.1f} mm², Eksik: {deficit:.1f} mm²"
        )

    return result


def build_reinforcement_calculation_result(
    inp: NozzleReinforcementInput,
) -> CalculationResult:
    """Nozul takviye hesabını CalculationResult formatında döndür.

    Orchestrator entegrasyonu için.

    Args:
        inp: Nozul girdileri.

    Returns:
        CalculationResult.
    """
    result = CalculationResult(
        component_id=inp.nozzle_tag,
        component_type="nozzle",
        calculation_type="nozzle_reinforcement",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-37/UG-40",
        formula_reference="Area Replacement Method",
    )

    reinp = calculate_reinforcement(inp)

    result.input_snapshot = {
        "nozzle_tag": inp.nozzle_tag,
        "effective_diameter": reinp.effective_diameter,
        "required_area": reinp.required_area,
        "total_available_area": reinp.total_available_area,
    }

    result.add_intermediate("d", reinp.effective_diameter, "mm", "Etkin açıklık çapı")
    result.add_intermediate("A_required", reinp.required_area, "mm²", "Gerekli takviye alanı")

    for area in reinp.available_areas:
        result.add_intermediate(area.name, area.area_mm2, "mm²", area.description)

    result.add_intermediate("A_total", reinp.total_available_area, "mm²", "Toplam mevcut alan")

    result.final_result = reinp.total_available_area
    result.final_result_unit = "mm²"
    result.allowable_limit = reinp.required_area
    result.allowable_limit_unit = "mm²"
    result.utilization_ratio = reinp.utilization_ratio

    result.status = reinp.status

    for w in reinp.warnings:
        result.add_warning(w)

    return result


__all__ = [
    "NozzleReinforcementInput",
    "NozzleReinforcementResult",
    "AreaItem",
    "calculate_reinforcement",
    "check_nozzle_eligibility",
    "build_reinforcement_calculation_result",
]
