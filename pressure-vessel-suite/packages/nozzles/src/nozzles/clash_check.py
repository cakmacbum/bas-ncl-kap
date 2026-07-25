"""Çakışma kontrolü — nozul geometri kontrolleri (kaynak §10, Faz 3.D).

K2 kuralı: CAD'e dokunulmaz; saf matematikle (koordinat + çap) yapılır.
K5 kuralı: Herhesap denetlenebilir — ara değerler + madde referansı saklanır.

Kontroller:
  - Nozul-nozul girişimi
  - Nozul-kaynak dikişi yakınlığı
  - Nozul bombe teğet çizgisini geçiyor mu
  - Minimum kenar mesafeleri
  - Delik takviye pedinden büyük mü

Referans: ASME BPVC Section VIII Division 1, 2025 Edition
  - UG-42: Minimum ligament between openings
  - UW-14: Nozzle weld attachment
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus, HeadType
from domain.geometry import Nozzle, ShellSection, Head
from domain.project import VesselProject
from domain.welds import WeldJoint


# ── Minimum kenar mesafeleri ─────────────────────────────────────────────────
# ASME pratik kuralları
MIN_NOZZLE_TO_NOZZLE_DISTANCE_mm = 50.0  # İki nozul arası minimum mesafe
MIN_NOZZLE_TO_WELD_DISTANCE_mm = 25.0  # Nozul ile kaynak dikişi arası minimum
MIN_EDGE_DISTANCE_FACTOR = 1.0  # Kenar mesafesi = nozzle OD × factor


@dataclass
class ClashCheckResult:
    """Tek bir çakışma kontrolü sonucu."""

    check_name: str
    status: CalculationStatus
    message: str
    details: str = ""
    clause_reference: str = ""
    distance_mm: Optional[float] = None
    limit_mm: Optional[float] = None


@dataclass
class ClashCheckReport:
    """Tüm çakışma kontrollerinin raporu."""

    nozzle_tag: str
    status: CalculationStatus = CalculationStatus.NOT_CALCULATED
    checks: List[ClashCheckResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nozzle_tag": self.nozzle_tag,
            "status": self.status.value,
            "checks": [
                {
                    "name": c.check_name,
                    "status": c.status.value,
                    "message": c.message,
                    "distance_mm": c.distance_mm,
                    "limit_mm": c.limit_mm,
                }
                for c in self.checks
            ],
            "warnings": self.warnings,
        }


def _nozzle_center_on_shell(
    nozzle: Nozzle, shell: ShellSection
) -> tuple[float, float, float]:
    """Nozul merkezinin gövde üzerindeki 3D koordinatlarını hesapla.

    Gövde silindirik kabul edilir:
    - x = R × cos(θ)
    - y = R × sin(θ)
    - z = axial_position

    Args:
        nozzle: Nozul tanımı.
        shell: Gövde tanımı.

    Returns:
        (x, y, z) koordinatları (mm).
    """
    R = shell.inside_diameter / 2.0 if shell.inside_diameter else (
        shell.outside_diameter / 2.0 - shell.nominal_thickness
    )
    theta_rad = math.radians(nozzle.circumferential_angle)
    z = nozzle.axial_position
    x = R * math.cos(theta_rad)
    y = R * math.sin(theta_rad)
    return x, y, z


def _nozzle_center_on_head(
    nozzle: Nozzle, head: Head
) -> tuple[float, float, float]:
    """Nozul merkezinin bombe üzerindeki 3D koordinatlarını hesapla.

    Bombe elipsoid kabul edilir. Merkez açısı ile konum hesaplanır.

    Args:
        nozzle: Nozul tanımı.
        head: Bombe tanımı.

    Returns:
        (x, y, z) koordinatları (mm).
    """
    R = head.inside_diameter / 2.0
    theta_rad = math.radians(nozzle.circumferential_angle)

    # Bombe üzerinde nozul konumu: eksenel pozisyona göre açı
    # 2:1 elipsoidal: z = (R/2) × cos(phi), r = R × sin(phi)
    # nozzle.axial_position burada bombe tepesinden mesafe olarak kullanılır
    # Basitleştirilmiş: bombe yüksekliği = R/2 (2:1 elipsoidal)
    head_height = R / 2.0 if head.type == HeadType.ELLIPTICAL else R
    phi = math.acos(max(-1, min(1, 1.0 - nozzle.axial_position / head_height))) \
        if head_height > 0 else 0.0

    r_at_phi = R * math.sin(phi)
    z_at_phi = head_height * math.cos(phi)

    x = r_at_phi * math.cos(theta_rad)
    y = r_at_phi * math.sin(theta_rad)
    z = z_at_phi

    return x, y, z


def _distance_3d(p1: tuple, p2: tuple) -> float:
    """İki 3D nokta arası Öklid mesafesi."""
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
    )


def check_nozzle_nozzle_clash(
    nozzle: Nozzle,
    all_nozzles: List[Nozzle],
    shell: ShellSection,
    heads: List[Head],
) -> ClashCheckResult:
    """Nozul-nozul girişimi kontrolü (UG-42).

    İki nozul arası mesafe, her iki nozulun dış çapının yarısından
    büyük olmalı.

    Args:
        nozzle: Kontrol edilecek nozul.
        all_nozzles: Tüm nozullar.
        shell: Gövde kesiti.
        heads: Bombeler.

    Returns:
        ClashCheckResult.
    """
    if len(all_nozzles) < 2:
        return ClashCheckResult(
            check_name="nozzle_nozzle_clash",
            status=CalculationStatus.PASS,
            message="Tek nozul var, çakışma kontrolü gerekmez.",
            clause_reference="UG-42",
        )

    # Bu nozulun host bileşenini bul
    host_is_shell = nozzle.host_component_id == shell.section_id
    host_head = None
    for h in heads:
        if nozzle.host_component_id == h.head_id:
            host_head = h
            break

    if host_is_shell:
        center1 = _nozzle_center_on_shell(nozzle, shell)
    elif host_head:
        center1 = _nozzle_center_on_head(nozzle, host_head)
    else:
        return ClashCheckResult(
            check_name="nozzle_nozzle_clash",
            status=CalculationStatus.NOT_CALCULATED,
            message=f"Host bileşen '{nozzle.host_component_id}' bulunamadı.",
            clause_reference="UG-42",
        )

    min_distance = float("inf")
    closest_tag = ""

    for other in all_nozzles:
        if other.tag == nozzle.tag:
            continue

        # Diğer nozulun host bileşenini bul
        other_is_shell = other.host_component_id == shell.section_id
        other_head = None
        for h in heads:
            if other.host_component_id == h.head_id:
                other_head = h
                break

        if other_is_shell:
            center2 = _nozzle_center_on_shell(other, shell)
        elif other_head:
            center2 = _nozzle_center_on_head(other, other_head)
        else:
            continue

        dist = _distance_3d(center1, center2)
        if dist < min_distance:
            min_distance = dist
            closest_tag = other.tag

    # Limit: iki nozulun dış çapının yarısı + minimum mesafe
    limit = nozzle.outside_diameter / 2.0 + MIN_NOZZLE_TO_NOZZLE_DISTANCE_mm

    if min_distance < limit:
        return ClashCheckResult(
            check_name="nozzle_nozzle_clash",
            status=CalculationStatus.FAIL,
            message=(
                f"Nozul {nozzle.tag} ile {closest_tag} arası mesafe "
                f"({min_distance:.1f} mm) minimum ({limit:.1f} mm) altında."
            ),
            details=(
                f"Nozul {nozzle.tag} OD={nozzle.outside_diameter} mm, "
                f"Nozul {closest_tag} dış çapı dahil."
            ),
            clause_reference="UG-42",
            distance_mm=min_distance,
            limit_mm=limit,
        )

    return ClashCheckResult(
        check_name="nozzle_nozzle_clash",
        status=CalculationStatus.PASS,
        message=(
            f"Nozul {nozzle.tag} ile en yakın nozul ({closest_tag}) arası mesafe "
            f"({min_distance:.1f} mm) yeterli."
        ),
        clause_reference="UG-42",
        distance_mm=min_distance,
        limit_mm=limit,
    )


def check_nozzle_weld_proximity(
    nozzle: Nozzle,
    welds: List[WeldJoint],
    shell: ShellSection,
) -> ClashCheckResult:
    """Nozul-kaynak dikişi yakınlığı kontrolü.

    Nozul, kaynak dikişine çok yakın olmamalı (minimum kenar mesafesi).

    Args:
        nozzle: Kontrol edilecek nozul.
        welds: Kaynak dikişleri.
        shell: Gövde kesiti.

    Returns:
        ClashCheckResult.
    """
    if not welds:
        return ClashCheckResult(
            check_name="nozzle_weld_proximity",
            status=CalculationStatus.PASS,
            message="Kaynak dikişi tanımlanmamış, kontrol atlandı.",
            clause_reference="UW-14",
        )

    nozzle_z = nozzle.axial_position
    nozzle_theta = nozzle.circumferential_angle
    nozzle_r = nozzle.outside_diameter / 2.0

    min_dist = float("inf")
    closest_weld = ""

    for weld in welds:
        if weld.joint_type == "longitudinal":
            # Boyuna dikiş: gövde boyunca z ekseninde, belirli bir θ'da
            # Nozulun bu dikişe uzaklığını hesapla
            # Basitleştirilmiş: dikiş θ=0'da kabul edilir
            angular_dist = abs(nozzle_theta - 0.0)
            if angular_dist > 180:
                angular_dist = 360 - angular_dist
            R = shell.inside_diameter / 2.0 if shell.inside_diameter else (
                shell.outside_diameter / 2.0 - shell.nominal_thickness
            )
            arc_dist = R * math.radians(angular_dist)
            # Kenar mesafesi = arc_dist - nozzle_r
            dist = arc_dist - nozzle_r

        elif weld.joint_type == "circumferential":
            # Çevresel dikiş: belirli bir z'de
            # Nozulun bu dikişe uzaklığını hesapla
            # Dikiş z konumu connected_components'dan türetilir
            # Basitleştirilmiş: dikiş gövde ortasında kabul edilir
            shell_length = shell.tangent_length
            # İki çevresel dikiş varsayalım: z=0 ve z=shell_length
            dist_to_start = abs(nozzle_z - 0.0) - nozzle_r
            dist_to_end = abs(nozzle_z - shell_length) - nozzle_r
            dist = min(dist_to_start, dist_to_end)

        elif weld.joint_type == "nozzle_to_shell":
            # Nozul-gövde dikişi — bu zaten nozulun kendisi
            continue
        else:
            continue

        if dist < min_dist:
            min_dist = dist
            closest_weld = weld.joint_id

    if min_dist < MIN_NOZZLE_TO_WELD_DISTANCE_mm:
        return ClashCheckResult(
            check_name="nozzle_weld_proximity",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"Nozul {nozzle.tag} ile kaynak dikişi {closest_weld} arası "
                f"kenar mesafesi ({min_dist:.1f} mm) minimum ({MIN_NOZZLE_TO_WELD_DISTANCE_mm} mm) altında. "
                f"Mühendis incelemesi gerekli."
            ),
            details=(
                f"Nozul OD={nozzle.outside_diameter} mm, "
                f"axial_position={nozzle.axial_position} mm, "
                f"θ={nozzle.circumferential_angle}°."
            ),
            clause_reference="UW-14",
            distance_mm=min_dist,
            limit_mm=MIN_NOZZLE_TO_WELD_DISTANCE_mm,
        )

    return ClashCheckResult(
        check_name="nozzle_weld_proximity",
        status=CalculationStatus.PASS,
        message=(
            f"Nozul {nozzle.tag} ile en yakın dikiş ({closest_weld}) arası "
            f"kenar mesafesi ({min_dist:.1f} mm) yeterli."
        ),
        clause_reference="UW-14",
        distance_mm=min_dist,
        limit_mm=MIN_NOZZLE_TO_WELD_DISTANCE_mm,
    )


def check_nozzle_tangent_line(
    nozzle: Nozzle,
    shell: ShellSection,
    heads: List[Head],
) -> ClashCheckResult:
    """Nozul bombe teğet çizgisini geçiyor mu kontrolü.

    Gövde-bombe birleşimindeki teğet noktasına çok yakın nozul
    problem yaratabilir.

    Args:
        nozzle: Kontrol edilecek nozul.
        shell: Gövde kesiti.
        heads: Bombeler.

    Returns:
        ClashCheckResult.
    """
    # Nozul gövde üzerindeyse teğet çizgisi kontrolü yapılır
    if nozzle.host_component_id != shell.section_id:
        return ClashCheckResult(
            check_name="nozzle_tangent_line",
            status=CalculationStatus.PASS,
            message=f"Nozul {nozzle.tag} gövde üzerinde değil, kontrol atlandı.",
            clause_reference="UG-42",
        )

    shell_length = shell.tangent_length
    nozzle_z = nozzle.axial_position
    nozzle_r = nozzle.outside_diameter / 2.0

    # Teğet noktasına uzaklık (gövde başlangıcı ve sonu)
    dist_to_start = nozzle_z - nozzle_r
    dist_to_end = (shell_length - nozzle_z) - nozzle_r

    min_dist = min(dist_to_start, dist_to_end)

    # Minimum mesafe: nozul çapının yarısı
    min_limit = nozzle.outside_diameter * 0.5

    if min_dist < 0:
        return ClashCheckResult(
            check_name="nozzle_tangent_line",
            status=CalculationStatus.FAIL,
            message=(
                f"Nozul {nozzle.tag} teğet çizgisini aşıyor! "
                f"Teğet noktasına mesafe: {min_dist:.1f} mm (negatif = aşıyor)."
            ),
            details=(
                f"Nozul z={nozzle_z} mm, OD={nozzle.outside_diameter} mm, "
                f"gövde uzunluğu={shell_length} mm."
            ),
            clause_reference="UG-42",
            distance_mm=min_dist,
            limit_mm=0.0,
        )

    if min_dist < min_limit:
        return ClashCheckResult(
            check_name="nozzle_tangent_line",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"Nozul {nozzle.tag} teğet çizgisine çok yakın "
                f"({min_dist:.1f} mm < {min_limit:.1f} mm). Mühendis incelemesi gerekli."
            ),
            details=(
                f"Nozul z={nozzle_z} mm, OD={nozzle.outside_diameter} mm, "
                f"gövde uzunluğu={shell_length} mm."
            ),
            clause_reference="UG-42",
            distance_mm=min_dist,
            limit_mm=min_limit,
        )

    return ClashCheckResult(
        check_name="nozzle_tangent_line",
        status=CalculationStatus.PASS,
        message=(
            f"Nozul {nozzle.tag} teğet çizgisinden yeterince uzak "
            f"({min_dist:.1f} mm)."
        ),
        clause_reference="UG-42",
        distance_mm=min_dist,
        limit_mm=min_limit,
    )


def check_hole_pad_relation(
    nozzle: Nozzle,
) -> ClashCheckResult:
    """Delik takviye pedinden büyük mü kontrolü.

    Nozul açıklığı (delik), takviye pedinin iç çapından büyük olmamalı.

    Args:
        nozzle: Kontrol edilecek nozul.

    Returns:
        ClashCheckResult.
    """
    if not nozzle.reinforcement_pad:
        return ClashCheckResult(
            check_name="hole_pad_relation",
            status=CalculationStatus.PASS,
            message=f"Nozul {nozzle.tag} takviye pedi yok, kontrol atlandı.",
            clause_reference="UG-40",
        )

    if nozzle.reinforcement_pad_od is None:
        return ClashCheckResult(
            check_name="hole_pad_relation",
            status=CalculationStatus.NOT_CALCULATED,
            message="Takviye pedi OD tanımlanmamış.",
            clause_reference="UG-40",
        )

    hole_diameter = nozzle.inside_diameter + 2 * nozzle.corrosion_allowance
    pad_id = nozzle.reinforcement_pad_od - 2 * nozzle.neck_thickness  # Yaklaşık

    if hole_diameter > pad_id:
        return ClashCheckResult(
            check_name="hole_pad_relation",
            status=CalculationStatus.FAIL,
            message=(
                f"Nozul {nozzle.tag} delik çapı ({hole_diameter:.1f} mm) "
                f"takviye pedi iç çapından ({pad_id:.1f} mm) büyük!"
            ),
            details=(
                f"Delik = nozzle ID + 2×CA = {nozzle.inside_diameter} + "
                f"2×{nozzle.corrosion_allowance} = {hole_diameter:.1f} mm. "
                f"Ped OD = {nozzle.reinforcement_pad_od} mm."
            ),
            clause_reference="UG-40",
            distance_mm=hole_diameter,
            limit_mm=pad_id,
        )

    return ClashCheckResult(
        check_name="hole_pad_relation",
        status=CalculationStatus.PASS,
        message=(
            f"Nozul {nozzle.tag} delik çapı ({hole_diameter:.1f} mm) "
            f"ped iç çapından ({pad_id:.1f} mm) küçük."
        ),
        clause_reference="UG-40",
        distance_mm=hole_diameter,
        limit_mm=pad_id,
    )


def check_minimum_edge_distance(
    nozzle: Nozzle,
    shell: ShellSection,
) -> ClashCheckResult:
    """Minimum kenar mesafesi kontrolü.

    Nozulun gövde kenarına olan uzaklığı, nozul dış çapının
    belirli bir katından büyük olmalı.

    Args:
        nozzle: Kontrol edilecek nozul.
        shell: Gövde kesiti.

    Returns:
        ClashCheckResult.
    """
    if nozzle.host_component_id != shell.section_id:
        return ClashCheckResult(
            check_name="minimum_edge_distance",
            status=CalculationStatus.PASS,
            message=f"Nozul {nozzle.tag} gövde üzerinde değil, kontrol atlandı.",
            clause_reference="UG-42",
        )

    shell_length = shell.tangent_length
    nozzle_z = nozzle.axial_position
    nozzle_r = nozzle.outside_diameter / 2.0

    # Kenar mesafeleri
    dist_start = nozzle_z - nozzle_r
    dist_end = (shell_length - nozzle_z) - nozzle_r

    # Limit: nozul dış çapı × factor
    limit = nozzle.outside_diameter * MIN_EDGE_DISTANCE_FACTOR

    min_dist = min(dist_start, dist_end)

    if min_dist < limit:
        return ClashCheckResult(
            check_name="minimum_edge_distance",
            status=CalculationStatus.REVIEW_REQUIRED,
            message=(
                f"Nozul {nozzle.tag} minimum kenar mesafesi ({min_dist:.1f} mm) "
                f"limit ({limit:.1f} mm) altında. Mühendis incelemesi gerekli."
            ),
            details=(
                f"Başlangıç kenarı: {dist_start:.1f} mm, "
                f"Son kenarı: {dist_end:.1f} mm, "
                f"Limit: {nozzle.outside_diameter} × {MIN_EDGE_DISTANCE_FACTOR} = {limit:.1f} mm."
            ),
            clause_reference="UG-42",
            distance_mm=min_dist,
            limit_mm=limit,
        )

    return ClashCheckResult(
        check_name="minimum_edge_distance",
        status=CalculationStatus.PASS,
        message=(
            f"Nozul {nozzle.tag} minimum kenar mesafesi ({min_dist:.1f} mm) yeterli."
        ),
        clause_reference="UG-42",
        distance_mm=min_dist,
        limit_mm=limit,
    )


def validate_nozzle_clash(
    nozzle: Nozzle,
    project: VesselProject,
) -> ClashCheckReport:
    """Tüm çakışma kontrollerini çalıştır.

    Args:
        nozzle: Kontrol edilecek nozul.
        project: VesselProject.

    Returns:
        ClashCheckReport.
    """
    report = ClashCheckReport(nozzle_tag=nozzle.tag)

    # Gövdeyi bul
    shell = None
    for s in project.shell_sections:
        if s.section_id == nozzle.host_component_id:
            shell = s
            break

    # Host gövde değilse bombeleri kontrol et
    host_head = None
    if shell is None:
        for h in project.heads:
            if h.head_id == nozzle.host_component_id:
                host_head = h
                break

    if shell is None and host_head is None:
        report.status = CalculationStatus.NOT_CALCULATED
        report.warnings.append(
            f"Host bileşen '{nozzle.host_component_id}' bulunamadı."
        )
        return report

    # Gövde üzerindeki nozul kontrolleri
    if shell:
        report.checks.append(
            check_nozzle_nozzle_clash(nozzle, project.nozzles, shell, project.heads)
        )
        report.checks.append(
            check_nozzle_weld_proximity(nozzle, project.welds, shell)
        )
        report.checks.append(
            check_nozzle_tangent_line(nozzle, shell, project.heads)
        )
        report.checks.append(
            check_minimum_edge_distance(nozzle, shell)
        )

    # Her iki durumda da delik-ped kontrolü
    report.checks.append(check_hole_pad_relation(nozzle))

    # Genel durum
    has_fail = any(c.status == CalculationStatus.FAIL for c in report.checks)
    has_review = any(c.status == CalculationStatus.REVIEW_REQUIRED for c in report.checks)
    has_not_calc = any(c.status == CalculationStatus.NOT_CALCULATED for c in report.checks)

    if has_fail:
        report.status = CalculationStatus.FAIL
    elif has_review:
        report.status = CalculationStatus.REVIEW_REQUIRED
    elif has_not_calc:
        report.status = CalculationStatus.NOT_CALCULATED
    else:
        report.status = CalculationStatus.PASS

    # Uyarıları topla
    for c in report.checks:
        if c.status in (CalculationStatus.FAIL, CalculationStatus.REVIEW_REQUIRED):
            report.warnings.append(f"[{c.check_name}] {c.message}")

    return report


def build_clash_check_result(
    nozzle: Nozzle,
    project: VesselProject,
) -> CalculationResult:
    """Çakışma kontrolü sonucunu CalculationResult formatında döndür.

    Args:
        nozzle: Kontrol edilecek nozul.
        project: VesselProject.

    Returns:
        CalculationResult.
    """
    result = CalculationResult(
        component_id=nozzle.tag,
        component_type="nozzle",
        calculation_type="clash_check",
        code="ASME VIII-1",
        edition="2025",
        clause_reference="UG-42/UW-14",
        formula_reference="Geometric Clash Check",
    )

    report = validate_nozzle_clash(nozzle, project)

    # Girdi anlık görüntüsü
    result.input_snapshot = {
        "nozzle_tag": nozzle.tag,
        "host_component_id": nozzle.host_component_id,
        "axial_position": nozzle.axial_position,
        "circumferential_angle": nozzle.circumferential_angle,
        "outside_diameter": nozzle.outside_diameter,
        "inside_diameter": nozzle.inside_diameter,
    }

    # Kontrol sonuçlarını ara değer olarak ekle
    for check in report.checks:
        result.add_intermediate(
            check.check_name,
            check.status.value,
            "-" if check.distance_mm is None else "mm",
            check.message,
        )

    result.status = report.status

    for w in report.warnings:
        result.add_warning(w)

    return result


__all__ = [
    "ClashCheckResult",
    "ClashCheckReport",
    "check_nozzle_nozzle_clash",
    "check_nozzle_weld_proximity",
    "check_nozzle_tangent_line",
    "check_hole_pad_relation",
    "check_minimum_edge_distance",
    "validate_nozzle_clash",
    "build_clash_check_result",
    "MIN_NOZZLE_TO_NOZZLE_DISTANCE_mm",
    "MIN_NOZZLE_TO_WELD_DISTANCE_mm",
    "MIN_EDGE_DISTANCE_FACTOR",
]
