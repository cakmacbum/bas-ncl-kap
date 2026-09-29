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
    nozzle_inclination_angle: float = 0.0  # derece, 0=radyal


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

    # UG-40 boyutsal limitleri (mm) — K5: raporda görünsün
    dimension_limits: Dict[str, float] = field(default_factory=dict)

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
            "dimension_limits": {k: round(v, 3) for k, v in self.dimension_limits.items()},
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
    angle = float(getattr(inp, "nozzle_inclination_angle", 0.0) or 0.0)
    if angle < 0 or angle >= 90:
        return False, "Nozzle inclination must be in [0, 90) degrees"
    projection = 1.0 / math.cos(math.radians(angle))
    d = (inp.nozzle_inside_diameter + 2 * inp.nozzle_corrosion_allowance) * projection
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

    # Bütün alanlar nozul eksenine paralel bir **kesit düzleminde** hesaplanır ve
    # açıklığın iki yanını birden kapsar — bu yüzden A2/A3/A4'te 2 çarpanı vardır.
    # (A1 zaten `2L - d` genişliğiyle iki yanı içerir.)

    # ── 1. Etkin çap (d) ve korozyonlu kalınlıklar — UG-37 ───────────────────
    d = inp.nozzle_inside_diameter + 2 * inp.nozzle_corrosion_allowance
    Rn = d / 2.0
    result.effective_diameter = d

    t = inp.component_nominal_thickness - inp.component_corrosion_allowance  # gövde/bombe
    tn = inp.nozzle_neck_thickness - inp.nozzle_corrosion_allowance          # nozul boynu
    te = inp.reinforcement_pad_thickness if inp.has_reinforcement_pad else 0.0
    tr = inp.component_required_thickness

    # ── 2. Dayanım azaltma faktörleri (fr) — UG-37(a) ────────────────────────
    # fr = malzeme izin verilen gerilme oranı, 1.0'ı aşamaz.
    Sv = inp.component_allowable_stress
    Sn = inp.nozzle_allowable_stress or Sv
    Sp = inp.reinforcement_pad_allowable_stress or Sv
    fr1 = fr2 = min(1.0, Sn / Sv) if Sv > 0 else 1.0
    fr4 = min(1.0, Sp / Sv) if Sv > 0 else 1.0

    # Radyal nozulda F = 1.0. Eğik nozulda 1/cos(α) yalnız açıklığın kesit
    # düzlemindeki izdüşümünü (elips) yaklaşıklar; UG-37'nin eğik/hillside
    # yöntemiyle doğrulanmış DEĞİLDİR ve Şekil UG-37 F faktörüyle aynı şey
    # değildir. Bu yüzden α > 0 sonucu aşağıda PASS yerine REVIEW_REQUIRED olur (K4).
    angle = float(getattr(inp, "nozzle_inclination_angle", 0.0) or 0.0)
    projection = 1.0 / math.cos(math.radians(angle))
    F = projection

    # E1 = 1.0: açıklık kaynak dikişinden geçmiyor varsayımı.
    E1 = 1.0

    # ── 3. Gerekli takviye alanı — UG-37(c) ──────────────────────────────────
    # A = d·tr·F + 2·tn·tr·F·(1 - fr1)
    A_required = d * tr * F + 2 * tn * tr * F * (1 - fr1)
    result.required_area = A_required

    if A_required <= 0:
        result.status = CalculationStatus.NOT_CALCULATED
        result.warnings.append("Gerekli takviye alanı sıfır veya negatif.")
        return result

    # ── 4. UG-40 takviye sınırları ────────────────────────────────────────────
    # Duvara paralel (eksenden): d veya Rn + tn + t — büyük olan.
    L_par = max(d, Rn + tn + t)
    # Duvara dik: 2.5·t veya 2.5·tn (+ ped varsa te) — küçük olan.
    L_norm = min(2.5 * t, 2.5 * tn + te)
    # İçe doğru: h, 2.5·t, 2.5·tn — en küçüğü.
    L_in = min(inp.nozzle_projection_inside, 2.5 * t, 2.5 * tn)

    result.dimension_limits.update({
        "d": d,
        "limit_parallel_from_centerline": L_par,
        "limit_parallel_total_width": 2 * L_par,
        "limit_normal": L_norm,
        "limit_inward": L_in,
    })

    # ── 5. Mevcut alanlar ─────────────────────────────────────────────────────

    # A1 — gövde/bombe fazla kalınlığı, UG-37(c)
    t_excess = E1 * t - F * tr
    A1 = max(
        (2 * L_par - d) * t_excess - 2 * tn * t_excess * (1 - fr1),
        2 * (t + tn) * t_excess - 2 * tn * t_excess * (1 - fr1),
    )
    A1 = max(0.0, A1)
    result.available_areas.append(AreaItem(
        name="A1",
        description=(
            f"Gövde/bombe fazlası: (2×{L_par:.1f} − {d:.1f}) × ({E1:.2f}×{t:.2f} − {tr:.2f})"
        ),
        area_mm2=A1,
        clause_reference="UG-37(c)",
    ))

    # A2 — nozul boynunun dışa çıkan kısmı, UG-37(c)
    # Nozul boynu gerekli kalınlığı trn — UG-27(c)(1), nozul kendi yarıçapıyla.
    trn = 0.0
    if Sn > 0 and inp.design_pressure > 0:
        denom = Sn - 0.6 * inp.design_pressure
        trn = inp.design_pressure * Rn / denom if denom > 0 else tn

    # UG-45(a) — nozul boynu minimum kalınlığı (basitleştirilmiş).
    # Tam UG-45 iki kriterin BÜYÜĞÜNÜ ister: (a) nozulun kendi iç basınç
    # tasarım kalınlığı — trn yukarıda zaten hesaplanıyor — ve (b) Tablo
    # UG-45'teki standart boru schedule minimumu. Tablo UG-45 telifli ASME
    # verisi olduğu için burada GÖMÜLMEZ (K6); yalnız (a) bacağı kontrol
    # edilir ve bu eksiklik açıkça yazılır — sessizce "geçti" denmez.
    if trn > 0 and tn < trn:
        result.warnings.append(
            f"UG-45(a) basitleştirilmiş kontrol: nozul boyun kalınlığı "
            f"{tn:.2f} mm, kendi iç basınç tasarım kalınlığı {trn:.2f} mm'nin "
            f"altında. Not: Tablo UG-45 (standart boru schedule minimumu) bu "
            f"kontrole dahil DEĞİL (K6) — imalat öncesi ayrıca doğrulanmalı."
        )
    h_out_eff = min(L_norm, inp.nozzle_projection_outside) if inp.nozzle_projection_outside > 0 else L_norm
    A2 = max(0.0, 2 * h_out_eff * (tn - trn) * fr2)
    result.available_areas.append(AreaItem(
        name="A2",
        description=f"Nozul boynu (dışa): 2 × {h_out_eff:.1f} × ({tn:.2f} − {trn:.2f}) × {fr2:.2f}",
        area_mm2=A2,
        clause_reference="UG-37(c)",
    ))

    # A3 — nozul boynunun içe çıkan kısmı, UG-37(c)
    # İçeri giren boru tümüyle takviyedir: fazla kalınlık değil, TAM kalınlık sayılır.
    A3 = max(0.0, 2 * L_in * tn * fr2)
    result.available_areas.append(AreaItem(
        name="A3",
        description=f"Nozul boynu (içe): 2 × {L_in:.1f} × {tn:.2f} × {fr2:.2f}",
        area_mm2=A3,
        clause_reference="UG-37(c)",
    ))

    # A4 — kaynak metali, UG-37(c)
    # Kesitin iki yanında birer köşe kaynağı: 2 × (w²/2) = w².
    A4 = 0.0
    a4_parts = []
    if inp.weld_leg_size_nozzle_to_shell > 0:
        w = inp.weld_leg_size_nozzle_to_shell
        A4 += w * w * fr2
        a4_parts.append(f"nozul-gövde {w:.1f}²")
    if inp.has_reinforcement_pad and inp.weld_leg_size_pad_to_shell > 0:
        w = inp.weld_leg_size_pad_to_shell
        A4 += w * w * fr4
        a4_parts.append(f"ped-gövde {w:.1f}²")
    result.available_areas.append(AreaItem(
        name="A4",
        description="Kaynak metali: " + (" + ".join(a4_parts) if a4_parts else "yok"),
        area_mm2=A4,
        clause_reference="UG-37(c)" if A4 > 0 else "—",
    ))

    # A5 — takviye pedi, UG-37(c)
    # Pedin yalnız UG-40 sınırı içinde kalan kısmı sayılır (dışı işe yaramaz).
    A5 = 0.0
    pad_width_used = 0.0
    if inp.has_reinforcement_pad and inp.reinforcement_pad_od > 0 and te > 0:
        pad_od_eff = min(inp.reinforcement_pad_od, 2 * L_par)
        pad_width_used = max(0.0, pad_od_eff - d - 2 * tn)
        A5 = pad_width_used * te * fr4
        if inp.reinforcement_pad_od > 2 * L_par:
            result.warnings.append(
                f"Takviye pedi dış çapı ({inp.reinforcement_pad_od:.1f} mm) UG-40 sınırını "
                f"({2 * L_par:.1f} mm) aşıyor; sınır dışı kalan kısım takviye sayılmadı."
            )
    result.available_areas.append(AreaItem(
        name="A5",
        description=f"Takviye pedi: {pad_width_used:.1f} × {te:.2f} × {fr4:.2f}",
        area_mm2=A5,
        clause_reference="UG-37(c)" if A5 > 0 else "—",
    ))

    # ── 6. Toplam ve değerlendirme ────────────────────────────────────────────
    total = A1 + A2 + A3 + A4 + A5
    result.total_available_area = total
    result.utilization_ratio = total / A_required if A_required > 0 else 0.0

    # ── 7. Limit kontrolleri ──────────────────────────────────────────────────
    result.limits["ug40_pad_within_limit"] = (
        not inp.has_reinforcement_pad or inp.reinforcement_pad_od <= 2 * L_par
    )
    result.limits["neck_thickness_adequate"] = tn >= trn
    if tn < trn:
        result.warnings.append(
            f"Nozul boynu kalınlığı ({tn:.2f} mm), iç basınç gereği ({trn:.2f} mm) altında."
        )

    # ── 6. Durum ──────────────────────────────────────────────────────────────
    if total >= A_required:
        result.status = CalculationStatus.PASS
        if angle > 0.0:
            result.status = CalculationStatus.REVIEW_REQUIRED
            result.warnings.append(
                f"Eğik nozul (α={angle:g}°): alan yerine koyma 1/cos(α) izdüşümüyle "
                "yaklaşıklandı; UG-37 eğik/hillside yöntemi ve F faktörü doğrulanmadı. "
                "Sonuç nihai değildir — mühendis incelemesi gerekir."
            )
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
