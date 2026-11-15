"""ASME VIII-1 Açıklık Takviye Hesabı — UG-37 / UG-40 Area Replacement Method.

Referans: ASME BPVC Section VIII Division 1, 2025 Edition
  - UG-36(c)(3): Küçük açıklıklarda ek takviye muafiyeti (yalnız (-a) kaynaklı dalı)
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
from typing import Any, Dict, List, Optional

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus, HeadType


# UG-36(c)(3)(-a) boyut sınırları (mm). Yalnız madde atfı ve sayısal sınır tutulur (K6).
UG36C3_CLAUSE = "UG-36(c)(3)"
UG36C3_THICKNESS_THRESHOLD_MM = 10.0   # gerekli kalınlık eşiği (3/8 in)
UG36C3_DIAMETER_LIMIT_THIN_MM = 89.0   # t_eşik ≤ 10 mm iken bitmiş açıklık sınırı (3½ in)
UG36C3_DIAMETER_LIMIT_THICK_MM = 60.0  # t_eşik > 10 mm iken bitmiş açıklık sınırı (2⅜ in)


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
    # UG-37(a) E1: açıklık Kategori B dışı dikişten geçiyorsa o dikişin verimi;
    # None = dikişten geçmiyor (E1=1, K4 varsayımı uyarı olarak yazılır).
    opening_weld_joint_efficiency: Optional[float] = None
    # UG-36(c)(3) kullanıcı beyanları:
    # (1) no_rapid_pressure_fluctuation_confirmed: kap hızlı basınç dalgalanmasına maruz değil
    # (2) opening_spacing_confirmed: komşu açıklık aralığı koşulları sağlanıyor
    # (3) welded_attachment_confirmed: bağlantı kaynaklı (dişli/saplamalı/genişletmeli tip değil)
    # Kod bunları doğrulayamaz; üçü birden True olmadan muafiyet uygulanmaz.
    no_rapid_pressure_fluctuation_confirmed: bool = False
    opening_spacing_confirmed: bool = False
    welded_attachment_confirmed: bool = False
    # Boş değilse UG-36(c)(3) adaylığı tümüyle devre dışı kalır (çağıran taraf,
    # eşik kalınlığını güvenle belirleyemediği host tiplerinde gerekçeyi yazar).
    ug36c3_not_applicable_reason: str = ""


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
    # Bilgi notları ve varsayımlar (durumu düşürmez; K4/K5 görünürlük)
    notices: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    validity_checks: List[Dict[str, Any]] = field(default_factory=list)

    # UG-36(c)(3) küçük açıklık muafiyeti
    ug36c3_candidate: bool = False  # (-a) boyut sınırı içinde mi
    ug36c3_applied: bool = False    # muafiyet sonuca uygulandı mı
    ug36c3_finished_diameter: float = 0.0    # mm (eğimde d/cosα)
    ug36c3_threshold_thickness: float = 0.0  # mm (tr + CA)
    ug36c3_diameter_limit: float = 0.0       # mm (89 veya 60)

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
            "notices": self.notices,
            "assumptions": self.assumptions,
            "validity_checks": self.validity_checks,
            "ug36c3_candidate": self.ug36c3_candidate,
            "ug36c3_applied": self.ug36c3_applied,
            "ug36c3_finished_diameter": round(self.ug36c3_finished_diameter, 3),
            "ug36c3_threshold_thickness": round(self.ug36c3_threshold_thickness, 3),
            "ug36c3_diameter_limit": self.ug36c3_diameter_limit,
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


@dataclass
class UG36C3SizeCheck:
    """UG-36(c)(3)(-a) geometrik adaylık değerlendirmesi (yalnız boyut)."""

    candidate: bool = False
    finished_diameter: float = 0.0    # mm
    threshold_thickness: float = 0.0  # mm
    diameter_limit: float = 0.0       # mm
    reason: str = ""                  # aday değilse neden


def evaluate_ug36c3_size(inp: NozzleReinforcementInput) -> UG36C3SizeCheck:
    """UG-36(c)(3)(-a) boyut sınırını değerlendir — muafiyeti UYGULAMAZ.

    Bitmiş açıklık (standarttaki tanımı programda DOĞRULANMADI → muhafazakâr yorum):
    korozyonlu nozul iç çapı (ID + 2·CA_nozul) ile nozul dış çapının büyüğü
    (set-in nozulda gövdedeki delik nozul dış çapıdır); dış çap girilmemişse
    nominal ID + 2·tn alınır. Eğimli nozulda sonuç d/cosα.
    Eşik kalınlığı gerçek et değil GEREKLİ kalınlıktır; muhafazakâr yorumla
    t_eşik = tr + host korozyon payı alınır. t_eşik ≤ 10 mm → sınır 89 mm,
    aksi hâlde 60 mm (sınır değerler dahil). Yalnız kaynaklı (-a) dalı; (-b) yok.
    Dalgalanma ve (-c)/(-d) aralık koşulları burada DEĞERLENDİRİLMEZ.
    """
    chk = UG36C3SizeCheck()
    if inp.ug36c3_not_applicable_reason:
        chk.reason = inp.ug36c3_not_applicable_reason
        return chk
    angle = float(getattr(inp, "nozzle_inclination_angle", 0.0) or 0.0)
    if angle < 0 or angle >= 90:
        chk.reason = "Eğim açısı geçersiz."
        return chk
    tr = inp.component_required_thickness
    if not (tr > 0) or not math.isfinite(tr):
        chk.reason = "Host gerekli kalınlığı (tr) yok veya ≤ 0; eşik belirlenemez."
        return chk
    d_corroded = inp.nozzle_inside_diameter + 2 * inp.nozzle_corrosion_allowance
    if not (d_corroded > 0) or inp.component_corrosion_allowance < 0:
        chk.reason = "Açıklık çapı / korozyon payı geçersiz."
        return chk
    od = inp.nozzle_outside_diameter
    if not (od > 0) or not math.isfinite(od):
        od = inp.nozzle_inside_diameter + 2 * inp.nozzle_neck_thickness
    d_opening = max(d_corroded, od)
    chk.finished_diameter = d_opening / math.cos(math.radians(angle))
    chk.threshold_thickness = tr + inp.component_corrosion_allowance
    chk.diameter_limit = (
        UG36C3_DIAMETER_LIMIT_THIN_MM
        if chk.threshold_thickness <= UG36C3_THICKNESS_THRESHOLD_MM
        else UG36C3_DIAMETER_LIMIT_THICK_MM
    )
    chk.candidate = chk.finished_diameter <= chk.diameter_limit
    if not chk.candidate:
        chk.reason = (
            f"Bitmiş açıklık (muhafazakâr: korozyonlu iç çap ile dış çapın büyüğü) "
            f"{chk.finished_diameter:.2f} mm > sınır {chk.diameter_limit:.0f} mm "
            f"(eşik kalınlığı tr+CA = {chk.threshold_thickness:.2f} mm)."
        )
    return chk


def check_nozzle_eligibility(inp: NozzleReinforcementInput) -> tuple[bool, str]:
    """Açıklık izinli mi kontrol et (UG-36).

    UG-36(a): Genel limit — d ≤ D/2 (açıklık çapı, ana bileşen çapının yarısını geçmemeli).
    Küçük açıklık muafiyeti UG-36(c)(3)'tür; boyut adaylığı `evaluate_ug36c3_size`
    ile, uygulanması `calculate_reinforcement` içinde kullanıcı beyanına bağlı yapılır.
    Bu fonksiyon yalnız UG-36(a) genel limitini kontrol eder; mesaja boyut adaylığı
    bilgi notu olarak eklenir (hesaba etkisi yoktur).

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

    # UG-36(c)(3)(-a) boyut adaylığı — yalnız bilgilendirme
    size = evaluate_ug36c3_size(inp)
    if size.candidate:
        return True, (
            f"Açıklık UG-36 kapsamına uygun. "
            f"Not: bitmiş açıklık {size.finished_diameter:.1f} mm, {UG36C3_CLAUSE}(-a) boyut "
            f"sınırı ({size.diameter_limit:.0f} mm; eşik kalınlığı "
            f"{size.threshold_thickness:.2f} mm) içinde. Muafiyet yalnız dalgalanma ve "
            f"komşu açıklık aralığı koşulları beyan edilirse uygulanır."
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

    # UG-37(a): E1 yalnız açıklık Kategori B dışı dikişten geçiyorsa < 1 olur
    # (dikişsiz kabukta tr zaten E=1 ile hesaplanır, B-07). Girdi yoksa E1=1.
    E1 = inp.opening_weld_joint_efficiency
    if E1 is None:
        E1 = 1.0
        result.warnings.append(
            "K4: E1=1 varsayıldı (açıklık kaynak dikişinden geçmiyor kabulü, UG-37(a)); "
            "dikişten geçiyorsa opening_weld_joint_efficiency girilmeli."
        )
    elif not (0 < E1 <= 1):
        result.status = CalculationStatus.FAIL
        result.warnings.append(f"opening_weld_joint_efficiency geçersiz ({E1}); (0, 1] olmalı.")
        return result

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
    neck_check_performed = False  # trn gerçekten UG-27 formülünden mi geldi
    if Sn > 0 and inp.design_pressure > 0:
        denom = Sn - 0.6 * inp.design_pressure
        trn = inp.design_pressure * Rn / denom if denom > 0 else tn
        neck_check_performed = denom > 0

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

    # ── 8. UG-36(c)(3) küçük açıklık muafiyeti ────────────────────────────────
    size = evaluate_ug36c3_size(inp)
    result.ug36c3_candidate = size.candidate
    result.ug36c3_finished_diameter = size.finished_diameter
    result.ug36c3_threshold_thickness = size.threshold_thickness
    result.ug36c3_diameter_limit = size.diameter_limit
    if size.candidate:
        _apply_ug36c3(
            inp, result, size,
            tn=tn, trn=trn, neck_check_performed=neck_check_performed,
            area_sufficient=total >= A_required, angle=angle,
        )
    elif (
        inp.no_rapid_pressure_fluctuation_confirmed
        or inp.opening_spacing_confirmed
        or inp.welded_attachment_confirmed
    ):
        result.notices.append(
            f"{UG36C3_CLAUSE} beyanı verildi ancak muafiyet uygulanmadı: "
            f"{size.reason} UG-37 alan hesabı esas alındı."
        )
    if result.ug36c3_applied:
        return result

    # ── 9. Durum ──────────────────────────────────────────────────────────────
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


def _apply_ug36c3(
    inp: NozzleReinforcementInput,
    result: NozzleReinforcementResult,
    size: UG36C3SizeCheck,
    *,
    tn: float,
    trn: float,
    neck_check_performed: bool,
    area_sufficient: bool,
    angle: float,
) -> None:
    """Boyut adayı açıklıkta UG-36(c)(3) muafiyetini uygula ya da nedenini yaz.

    Muafiyet yalnız şu durumda uygulanır: kullanıcı beyanı var, açıklık kaynak
    dikişinden geçmiyor ve nozul boynunun kendi basınç kontrolü (tn ≥ trn)
    gerçekten yapılmış ve sağlanıyor. Aksi hâlde çağıran UG-37 alan hesabıyla
    devam eder (`result.ug36c3_applied` False kalır).
    """
    size_txt = (
        f"bitmiş açıklık (muhafazakâr maks. çap) {size.finished_diameter:.2f} mm ≤ "
        f"{size.diameter_limit:.0f} mm; "
        f"eşik kalınlığı tr+CA = {size.threshold_thickness:.2f} mm"
    )

    missing = []
    if not inp.no_rapid_pressure_fluctuation_confirmed:
        missing.append("no_rapid_pressure_fluctuation_confirmed (kap hızlı basınç dalgalanmasına maruz değil)")
    if not inp.opening_spacing_confirmed:
        missing.append("opening_spacing_confirmed (komşu açıklık aralığı)")
    if not inp.welded_attachment_confirmed:
        missing.append("welded_attachment_confirmed (kaynaklı bağlantı)")

    if missing:
        missing_str = ", ".join(missing)
        result.notices.append(
            f"Açıklık {UG36C3_CLAUSE}(-a) boyut sınırı içinde ({size_txt}); ancak "
            f"kullanıcı beyanı eksik olduğu için muafiyet UYGULANMADI: "
            f"{missing_str}. UG-37 alan hesabı esas alındı."
        )
        return

    # Dikiş üzerinde muafiyet reddedilir; "geçti" kaydı eklenmeden çıkılır.
    if inp.opening_weld_joint_efficiency is not None:
        result.notices.append(
            f"{UG36C3_CLAUSE} muafiyeti UYGULANMADI: açıklık kaynak dikişinden geçiyor "
            "(E1 girildi). Dikiş üzerindeki muaf açıklıklar için UW-14 ek koşulları bu "
            "programda doğrulanmıyor; UG-37 alan hesabı esas alındı."
        )
        return

    # Beyan var: geçerlilik kayıtları (K5)
    neck_ok = neck_check_performed and tn >= trn
    result.validity_checks.extend([
        {
            "name": f"{UG36C3_CLAUSE}(-a) bitmiş açıklık çapı ≤ sınır",
            "passed": True,
            "limit": size.diameter_limit,
            "actual": round(size.finished_diameter, 3),
        },
        {
            "name": (
                f"{UG36C3_CLAUSE}(-a) eşik kalınlığı tr+CA "
                f"({'≤' if size.threshold_thickness <= UG36C3_THICKNESS_THRESHOLD_MM else '>'} 10 mm "
                f"→ çap sınırı {size.diameter_limit:.0f} mm)"
            ),
            "passed": True,
            "limit": UG36C3_THICKNESS_THRESHOLD_MM,
            "actual": round(size.threshold_thickness, 3),
        },
        {
            "name": "Nozul boynu tn ≥ trn (UG-27 / UG-45(a))",
            "passed": neck_ok,
            "limit": round(trn, 3),
            "actual": round(tn, 3),
        },
    ])

    if not neck_ok:
        why = (
            f"nozul boynu kalınlığı tn={tn:.2f} mm, kendi iç basınç gereği trn={trn:.2f} mm altında"
            if neck_check_performed
            else "nozul boynunun iç basınç kontrolü yapılamadı "
                 "(basınç/izin verilen gerilme eksik veya geçersiz)"
        )
        result.notices.append(
            f"{UG36C3_CLAUSE} muafiyeti UYGULANMADI: {why}. Boyun basınç kontrolü "
            "(UG-27/UG-45) muafiyetle atlanamaz; UG-37 alan hesabı esas alındı."
        )
        return

    # ── Muafiyet uygulanır ────────────────────────────────────────────────────
    result.ug36c3_applied = True
    result.clause_reference = f"{UG36C3_CLAUSE}; UG-37/UG-40"
    result.assumptions.extend([
        f"K4 ({UG36C3_CLAUSE}): Kullanıcı beyanı — kap hızlı basınç dalgalanmasına maruz "
        "değil. Program doğrulamadı.",
        f"K4 ({UG36C3_CLAUSE}(-c)/(-d)): Kullanıcı beyanı — komşu takviyesiz açıklıklarla "
        "merkez aralığı koşulları sağlanıyor. Program doğrulamadı.",
        f"K4 ({UG36C3_CLAUSE}(-a)): Kullanıcı beyanı — bağlantı kaynaklı (dişli/saplamalı/"
        "genişletmeli tip değil). Program doğrulamadı.",
        f"K4 ({UG36C3_CLAUSE}(-a)): Eşik kalınlığı muhafazakâr yorumla tr + host korozyon "
        f"payı = {size.threshold_thickness:.2f} mm alındı (tr girdisi = "
        f"{inp.component_required_thickness:.2f} mm); tr'nin host bileşenin tam gerekli "
        "kalınlığını temsil ettiği kabul edildi.",
        f"K4 ({UG36C3_CLAUSE}(-a)): 'Bitmiş açıklık' ölçüsü muhafazakâr yorumla korozyonlu "
        "iç çap ile nozul dış çapının büyüğü alındı "
        f"(= {size.finished_diameter:.2f} mm); standardın tanımı programda doğrulanmadı.",
    ])
    result.notices.append(
        f"{UG36C3_CLAUSE}(-a) muafiyeti uygulandı ({size_txt}): açıklık, yapının kendinde "
        "olan dışında ek takviye gerektirmez. UG-37 alan değerleri, kullanım oranı ve "
        "nihai sonuç (A_total / A_required) YALNIZ BİLGİ amaçlıdır; kabul ölçütü değildir."
    )
    if not area_sufficient:
        result.notices.append(
            f"Bilgi: UG-37 alan hesabına göre mevcut alan {result.total_available_area:.1f} mm², "
            f"gerekli alan {result.required_area:.1f} mm² (oran {result.utilization_ratio:.3f}). "
            f"{UG36C3_CLAUSE} muafiyeti nedeniyle bu fark FAIL üretmedi."
        )
    result.notices.append(
        "Muafiyet yalnız takviye alanını kapsar; nozul boynu Tablo UG-45 minimumu, kaynak "
        "boyutları (UW-16) ve dış yükler ayrıca doğrulanmalıdır."
    )

    if angle > 0.0:
        result.status = CalculationStatus.REVIEW_REQUIRED
        result.warnings.append(
            f"Eğik nozul (α={angle:g}°): {UG36C3_CLAUSE} boyut kontrolünde bitmiş açıklık "
            "d/cos(α) izdüşümüyle yaklaşıklandı; eğik/hillside açıklıkta bitmiş açıklık "
            "ölçüsü doğrulanmadı. Sonuç nihai değildir — mühendis incelemesi gerekir."
        )
    else:
        result.status = CalculationStatus.PASS


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
        "no_rapid_pressure_fluctuation_confirmed": inp.no_rapid_pressure_fluctuation_confirmed,
        "opening_spacing_confirmed": inp.opening_spacing_confirmed,
        "welded_attachment_confirmed": inp.welded_attachment_confirmed,
        "ug36c3_candidate": reinp.ug36c3_candidate,
        "ug36c3_applied": reinp.ug36c3_applied,
    }
    result.clause_reference = reinp.clause_reference
    if reinp.ug36c3_applied:
        result.formula_reference = (
            f"{UG36C3_CLAUSE}(-a) small-opening exemption; "
            "Area Replacement Method (informative)"
        )

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
    for note in reinp.notices:
        result.add_notice(note)
    for a in reinp.assumptions:
        result.add_assumption(a)
    for vc in reinp.validity_checks:
        result.add_validity_check(vc["name"], vc["passed"], vc.get("limit"), vc.get("actual"))

    return result


__all__ = [
    "NozzleReinforcementInput",
    "NozzleReinforcementResult",
    "AreaItem",
    "calculate_reinforcement",
    "check_nozzle_eligibility",
    "evaluate_ug36c3_size",
    "UG36C3SizeCheck",
    "build_reinforcement_calculation_result",
]
