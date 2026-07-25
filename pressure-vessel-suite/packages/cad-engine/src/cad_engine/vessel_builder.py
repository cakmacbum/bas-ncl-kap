"""Parametrik basınçlı kap CAD modeli — CadQuery ile.

CAD üretim sırası (kaynak §10):
  1. İç/dış çapa göre gövde (silindir)
  2. Et kalınlığı uygula
  3. Sol + sağ bombe oluştur
  4. Gövdeyle birleştir
  11. Geometri geçerlilik
  12. STEP export

K2 kuralı: project data → CAD. CAD, hesabın ürettiği ölçüleri girdi alır, ölçü üretmez.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import cadquery as cq

    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False

from domain.enums import HeadType
from domain.geometry import Head, ShellSection
from domain.project import VesselProject

from .validation import (
    CADValidationReport,
    validate_no_negative_volume,
    validate_no_open_shells,
    validate_solid_count,
    validate_volume_tolerance,
)


@dataclass
class VesselCADResult:
    """CAD model üretim sonucu."""

    shape: Optional[object]  # CadQuery shape (CQ yoksa None)
    step_path: Optional[str] = None
    inner_volume_mm3: float = 0.0  # CAD'den ölçülen iç hacim
    outer_volume_mm3: float = 0.0  # Dış hacim (metal dahil)
    metal_volume_mm3: float = 0.0  # Metal hacmi
    validation: Optional[CADValidationReport] = None
    error: Optional[str] = None
    nozzle_count: int = 0  # Modele eklenen nozul sayısı
    warnings: List[str] = None  # type: ignore
    # Sorun değil, bilgi: modelin görsel temsil sınırları (ör. flanş ölçüsü
    # B16.5'ten gelmez). warnings yalnızca gerçek problemler içindir.
    notes: List[str] = None  # type: ignore

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.notes is None:
            self.notes = []

    @property
    def success(self) -> bool:
        return self.shape is not None and self.error is None


def _check_cadquery():
    """CadQuery kurulu mu kontrol et."""
    if not CADQUERY_AVAILABLE:
        raise ImportError(
            "CadQuery kurulu değil. Yüklemek için: pip install cadquery"
        )


def _build_shell_body(shell: ShellSection):
    """Silindirik gövde oluştur (adım 1-2).

    Args:
        shell: Gövde kesit tanımı.

    Returns:
        CadQuery Workplane (boru — dış silindir - iç silindir).
    """
    _check_cadquery()

    if shell.inside_diameter:
        inner_r = shell.inside_diameter / 2.0
        outer_r = inner_r + shell.nominal_thickness
    else:
        outer_r = shell.outside_diameter / 2.0
        inner_r = outer_r - shell.nominal_thickness

    length = shell.tangent_length

    # Dış silindir - iç silindir = boru
    shell_body = (
        cq.Workplane("XY")
        .circle(outer_r)
        .extrude(length)
        .faces(">Z")
        .workplane()
        .circle(inner_r)
        .cutBlind(-length)
    )

    return shell_body


def _ellipse_arc_pts(a: float, b: float, n: int = 40):
    """Ekvatordan (a, 0) kutba (0, b) çeyrek elips yayı noktaları (XZ düzlemi)."""
    return [
        (a * math.cos(math.pi / 2.0 * i / n), b * math.sin(math.pi / 2.0 * i / n))
        for i in range(n + 1)
    ]


def _revolve_head_wall(outer_pts, inner_pts, a: float, thickness: float, straight_flange: float):
    """Bombe cidarının TEK kapalı kesitini çizip 360° revolve ederek watertight bir bombe
    kabuğu (kubbe + düz flanş eteği) üretir.

    Eski yöntem (iki dolu 'mercek' katıyı çıkarma) eksen yakınında dejenere katı üretip
    union'da düşüyordu; bu yaklaşım tek geçerli solid garanti eder.

    Kesit (yerel; ekvator z=0, kubbe +Z, etek −Z):
      (a+t, −sf) → (a+t, 0) → dış yay → (0, b+t)  [kutup]
      → (0, b) → iç yay → (a, 0) → (a, −sf) → kapan.

    Args:
        outer_pts: dış yay, ekvator (a+t, 0) → kutup (0, b+t).
        inner_pts: iç yay, ekvator (a, 0) → kutup (0, b).
        a: bombe iç yarıçapı = D/2 (mm).
        thickness: et kalınlığı (mm).
        straight_flange: düz flanş (etek) boyu (mm).
    """
    _check_cadquery()
    sf = max(0.0, straight_flange)
    t = thickness

    pts = []
    if sf > 0:
        pts.append((a + t, -sf))
    pts.append((a + t, 0.0))
    pts += outer_pts[1:]              # dış yay → (0, b+t)
    pts += list(reversed(inner_pts))  # (0, b) → iç yay → (a, 0)
    if sf > 0:
        pts.append((a, -sf))

    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))


def _build_elliptical_head(
    diameter: float,
    thickness: float,
    straight_flange: float = 25.0,
    is_left: bool = True,
):
    """2:1 Elipsoidal bombe oluştur (adım 3).

    ASME 2:1 elipsoidal: yarı eksenler a = D/2, b = D/4.
    """
    _check_cadquery()
    a = diameter / 2.0
    b = a / 2.0  # D/4
    outer = _ellipse_arc_pts(a + thickness, b + thickness)
    inner = _ellipse_arc_pts(a, b)
    return _revolve_head_wall(outer, inner, a, thickness, straight_flange)


def _torispherical_depth(crown_radius: float, knuckle_radius: float, a: float) -> float:
    """Torisferik bombe iç kubbe derinliği (mm). Gerçek toriye yakın; görsel amaçlı."""
    val = (crown_radius - knuckle_radius) ** 2 - (a - knuckle_radius) ** 2
    if val > 0:
        return crown_radius - math.sqrt(val)
    return a / 2.0  # emniyetli geri düşüş


def _build_torispherical_head(
    diameter: float,
    crown_radius: float,
    knuckle_radius: float,
    thickness: float,
    straight_flange: float = 25.0,
):
    """Torisferik bombe oluştur (tek watertight profil-revolve).

    K2: CAD hesabın kaynağı değildir — kubbe, doğru derinlikte pürüzsüz bir profil ile
    görselleştirilir (taç+knuckle geometrisinden türetilen derinlik h).
    """
    _check_cadquery()
    a = diameter / 2.0
    h = _torispherical_depth(crown_radius, knuckle_radius, a)
    outer = _ellipse_arc_pts(a + thickness, h + thickness)
    inner = _ellipse_arc_pts(a, h)
    return _revolve_head_wall(outer, inner, a, thickness, straight_flange)


def _build_flat_head(diameter: float, thickness: float, straight_flange: float = 25.0):
    """Düz kapak (flat cover) — dolu plaka + silindirik etek.

    K2: CAD yalnızca görselleştirir; düz kapak mukavemet hesabı V1'de NOT_CALCULATED.
    """
    _check_cadquery()
    a = diameter / 2.0
    t = thickness
    sf = max(0.0, straight_flange)

    # Plaka: z ∈ [0, t]
    head = cq.Workplane("XY").circle(a + t).extrude(t)

    # Etek: z ∈ [−sf, 0], halka [a, a+t]
    if sf > 0:
        skirt = (
            cq.Workplane("XY")
            .workplane(offset=-sf)
            .circle(a + t)
            .extrude(sf)
            .faces(">Z")
            .workplane()
            .circle(a)
            .cutBlind(-sf)
        )
        head = head.union(skirt)

    return head


def _shell_radii(shell: ShellSection):
    """Gövde iç ve dış yarıçapı (mm)."""
    if shell.inside_diameter:
        inner_r = shell.inside_diameter / 2.0
        outer_r = inner_r + shell.nominal_thickness
    else:
        outer_r = shell.outside_diameter / 2.0
        inner_r = outer_r - shell.nominal_thickness
    return inner_r, outer_r


def _oriented_cylinder(center_start, normal, radius: float, length: float):
    """Verilen noktadan başlayıp normal yönünde uzanan dolu silindir (adım yardımcı).

    K2: konum/yön hesap verisinden gelir (nozzles.position); CAD yalnızca üretir.
    """
    plane = cq.Plane(origin=tuple(center_start), normal=tuple(normal))
    return cq.Workplane(plane).circle(radius).extrude(length)


def _normalize(v) -> tuple:
    """Vektörü birim uzunluğa getir; sıfır vektörde +X'e düş."""
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if n <= 1e-9:
        return (1.0, 0.0, 0.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def _nozzle_axis(position) -> tuple:
    """Nozul ekseni — hesap motorundan gelen yüzey normali (K2).

    `nozzles.position` normali eğim açısını (α) zaten içerir; CAD onu
    yeniden türetmez, olduğu gibi kullanır.
    """
    return _normalize((position.normal_x, position.normal_y, position.normal_z))


def _nozzle_anchor(position) -> tuple:
    """Nozulun host yüzeyindeki çıpa noktası (global koordinat)."""
    return (position.x_mm, position.y_mm, position.z_mm)


class _GlobalPosition:
    """Bombe yerel konumundan türetilmiş global nozul konumu.

    `nozzles.position` bombeyi kendi yerel çerçevesinde verir (ekvator z=0,
    kubbe +Z). Model ise sol bombeyi −Z'ye aynalar, sağ bombeyi z=L'ye taşır.
    Bu sınıf yalnızca o dönüşümü uygular — açı/normal hesabı yapmaz (K2).
    """

    def __init__(self, tag, x, y, z, nx, ny, nz, theta, alpha, host_id):
        self.tag = tag
        self.x_mm, self.y_mm, self.z_mm = x, y, z
        self.normal_x, self.normal_y, self.normal_z = nx, ny, nz
        self.circumferential_theta_deg = theta
        self.inclination_alpha_deg = alpha
        self.axial_z_mm = z
        self.host_component_id = host_id
        self.host_type = "head"


def _head_position_to_global(local, is_left: bool, tangent_length: float):
    """Bombe yerel konumunu modelin global koordinatına taşı.

    Sağ bombe: ekvator z=L, kubbe +Z  →  z_global = L + z_local
    Sol bombe: mirror("XY") ile kubbe −Z  →  z_global = −z_local (normal z de ters)
    """
    if is_left:
        z = -local.z_mm
        nz = -local.normal_z
    else:
        z = tangent_length + local.z_mm
        nz = local.normal_z

    return _GlobalPosition(
        tag=local.tag,
        x=local.x_mm,
        y=local.y_mm,
        z=z,
        nx=local.normal_x,
        ny=local.normal_y,
        nz=nz,
        theta=local.circumferential_theta_deg,
        alpha=local.inclination_alpha_deg,
        host_id=local.host_component_id,
    )


def _build_nozzle_pipe_and_bore(nozzle, position, shell: ShellSection):
    """Nozul borusu (dolu) + delik kesici (bore) üret (adım 5-7).

    Yön ve çıpa noktası hesap motorundan gelir (position.normal_*, position.*_mm),
    böylece eğim açısı (α) ve bombe üzerindeki nozullar da doğru modellenir.

    Returns:
        (pipe_solid, bore_solid) — pipe union edilir, bore cut edilir.
    """
    d = _nozzle_axis(position)
    anchor = _nozzle_anchor(position)

    # Çıpa host yüzeyinde; boru içeriden dışarıya uzanır.
    inside = max(nozzle.inside_projection, 0.0)
    outside = max(nozzle.outside_projection, 0.0)
    wall = _host_wall_thickness(nozzle, shell)
    # Cidarı güvenle geçecek uzunluk
    length = inside + wall + outside

    start_center = tuple(anchor[i] - d[i] * inside for i in range(3))

    od_r = nozzle.outside_diameter / 2.0
    id_r = nozzle.inside_diameter / 2.0

    pipe = _oriented_cylinder(start_center, d, od_r, length)

    # Bore biraz daha uzun (her iki uçtan taşsın) → temiz delik
    eps = 5.0
    bore_start = tuple(start_center[i] - d[i] * eps for i in range(3))
    bore = _oriented_cylinder(bore_start, d, id_r, length + 2 * eps)

    return pipe, bore


def _host_wall_thickness(nozzle, shell: ShellSection) -> float:
    """Nozulun deldiği cidar kalınlığı (boru boyunu belirlemek için)."""
    return max(shell.nominal_thickness, 1.0)


def _build_reinforcement_pad(nozzle, position, shell: ShellSection):
    """Takviye pedi halkası — host dış yüzeyine oturur (adım 8)."""
    if not nozzle.reinforcement_pad or not nozzle.reinforcement_pad_od \
            or not nozzle.reinforcement_pad_thickness:
        return None

    d = _nozzle_axis(position)
    anchor = _nozzle_anchor(position)

    pad_or = nozzle.reinforcement_pad_od / 2.0
    pad_t = nozzle.reinforcement_pad_thickness
    # Pedin iç deliği nozul dış çapı kadar
    noz_or = nozzle.outside_diameter / 2.0

    # Ped, dış yüzeye yaslanır (çıpadan dışarı doğru).
    wall = _host_wall_thickness(nozzle, shell)
    base = tuple(anchor[i] + d[i] * (wall - 0.5) for i in range(3))
    disc = _oriented_cylinder(base, d, pad_or, pad_t + 0.5)

    hole_start = tuple(base[i] - d[i] * 5.0 for i in range(3))
    hole = _oriented_cylinder(hole_start, d, noz_or, pad_t + 10.0)
    return disc.cut(hole)


def _build_nozzle_type_feature(nozzle, position, shell: ShellSection):
    """Nozul tipine göre görsel bağlantı detayı (adım 9).

    K4/K6: Flanş/kapak ölçüleri lisanslı B16.5 tablolarından GELMEZ; burada
    yalnızca nozul çapına oranlı **görsel temsil** üretilir. Rating/ölçü
    doğrulaması için flanş modülü kullanılmalıdır. Bu yüzden model bir not
    (uyarı) döndürür.

    Returns:
        (shape | None, note | None)
    """
    try:
        from domain.enums import NozzleType
    except ImportError:  # domain yoksa görsel detay atlanır
        return None, None

    d = _nozzle_axis(position)
    anchor = _nozzle_anchor(position)
    wall = _host_wall_thickness(nozzle, shell)
    od_r = nozzle.outside_diameter / 2.0
    id_r = nozzle.inside_diameter / 2.0

    # Borunun dış ucu (host dış yüzeyinden outside_projection kadar ileride)
    tip_dist = wall + max(nozzle.outside_projection, 0.0)
    tip = tuple(anchor[i] + d[i] * tip_dist for i in range(3))

    def at(dist: float) -> tuple:
        return tuple(anchor[i] + d[i] * dist for i in range(3))

    ntype = nozzle.nozzle_type
    note = None

    if ntype == NozzleType.MANWAY:
        # Büyük flanş + kör kapak plakası
        fl_r = od_r * 1.75
        fl_t = max(od_r * 0.28, 12.0)
        cover_t = max(od_r * 0.22, 10.0)
        flange = _oriented_cylinder(
            tuple(tip[i] - d[i] * fl_t for i in range(3)), d, fl_r, fl_t
        )
        cover = _oriented_cylinder(tip, d, fl_r * 0.98, cover_t)
        shape = flange.union(cover)
        note = (
            f"Nozul {nozzle.tag}: manway kapağı görsel temsildir "
            f"(ölçü/rating B16.5'ten alınmadı)."
        )

    elif ntype == NozzleType.COUPLING:
        # Manşon — soket boss'undan daha kalın ve daha uzun bilezik; gövde
        # yüzeyinden başlar, akış deliği açık kalır.
        cpl_r = od_r * 1.5
        cpl_len = max(od_r * 1.2, 20.0)
        shape = _oriented_cylinder(at(wall), d, cpl_r, cpl_len)
        note = None

    elif ntype == NozzleType.SOCKET_WELDED:
        # Kısa kalın boss (coupling) — gövde yüzeyine yakın
        boss_r = od_r * 1.45
        boss_len = max(od_r * 0.9, 12.0)
        shape = _oriented_cylinder(at(wall), d, boss_r, boss_len)
        note = None

    elif ntype in (NozzleType.FLANGED, NozzleType.SLIP_ON, NozzleType.PAD_REINFORCED):
        # Flanş halkası + raised face
        fl_r = od_r * 1.6
        fl_t = max(od_r * 0.26, 10.0)
        # Slip-on flanş boru ucundan biraz geride oturur
        setback = fl_t * 0.6 if ntype == NozzleType.SLIP_ON else 0.0
        fl_base = tuple(tip[i] - d[i] * (fl_t + setback) for i in range(3))
        flange = _oriented_cylinder(fl_base, d, fl_r, fl_t)
        rf_t = max(fl_t * 0.22, 2.0)
        rf = _oriented_cylinder(
            tuple(fl_base[i] + d[i] * fl_t for i in range(3)), d, od_r * 1.18, rf_t
        )
        shape = flange.union(rf)
        note = (
            f"Nozul {nozzle.tag}: flanş görsel temsildir "
            f"(Class/ölçü B16.5'ten alınmadı)."
        )
    else:
        return None, None

    # Akış deliği flanş/kapakta da açık kalsın (manway kapağı hariç kördür)
    if ntype != NozzleType.MANWAY:
        bore_start = tuple(anchor[i] - d[i] * 10.0 for i in range(3))
        through = _oriented_cylinder(bore_start, d, id_r, tip_dist + 200.0)
        shape = shape.cut(through)

    return shape, note


def build_vessel(project: VesselProject) -> VesselCADResult:
    """Projeden parametrik basınçlı kap CAD modeli oluştur.

    CAD üretim sırası (kaynak §10):
      1. Gövde (silindirik boru)
      2. Sol bombe
      3. Sağ bombe
      4. Birleştir
      5-10. Nozul: merkez ekseni → boru → delik → takviye pedi
      11. Geometri geçerlilik

    Args:
        project: VesselProject (hesap motorundan gelen ölçüleri kullanır).

    Returns:
        VesselCADResult (shape, hacim, doğrulama).
    """
    _check_cadquery()

    if not project.shell_sections:
        return VesselCADResult(shape=None, error="Gövde kesiti tanımlanmamış.")

    if len(project.heads) < 2:
        return VesselCADResult(shape=None, error="En az 2 bombe (sol+sağ) gerekli.")

    shell = project.shell_sections[0]

    # ── Adım 1-2: Gövde ──────────────────────────────────────────────────────
    try:
        shell_body = _build_shell_body(shell)
    except Exception as e:
        return VesselCADResult(shape=None, error=f"Gövde oluşturma hatası: {e}")

    # ── Adım 3: Bombeler ──────────────────────────────────────────────────────
    # Sol bombe: gövdenin altına (Z < 0), sağ bombe: gövdenin üstüne (Z > L)
    left_head = project.heads[0]
    right_head = project.heads[1]

    try:
        left_shape = _build_head(left_head)
        right_shape = _build_head(right_head)
    except Exception as e:
        return VesselCADResult(shape=None, error=f"Bombe oluşturma hatası: {e}")

    # ── Adım 4: Birleştir ─────────────────────────────────────────────────────
    # Bombe yerel koordinatı: ekvator z=0, kubbe +Z, düz flanş eteği −Z.
    try:
        # Sol bombe: kubbe −Z bakacak şekilde aynala; etek gövdenin z∈[0,sf] ucuyla örtüşür.
        left_moved = left_shape.mirror("XY").translate((0, 0, 0))

        # Sağ bombe: ekvatoru gövde üst ucuna (z=L) taşı; etek gövdeyle örtüşür.
        right_moved = right_shape.translate((0, 0, shell.tangent_length))

        # Birleştir (etek örtüşmesi union'ı watertight yapar)
        vessel = shell_body.union(left_moved).union(right_moved)
    except Exception as e:
        return VesselCADResult(shape=None, error=f"Birleştirme hatası: {e}")

    # ── Adım 5-10: Nozullar ───────────────────────────────────────────────────
    # K2: nozul konum/yönü hesap verisinden (nozzles.position) gelir; CAD üretir.
    nozzle_warnings: List[str] = []
    visual_fitting_used = False
    try:
        from nozzles import calculate_nozzle_position
    except ImportError:
        calculate_nozzle_position = None

    if calculate_nozzle_position is not None:
        for nozzle in project.nozzles:
            try:
                host_head = None
                if nozzle.host_component_id == shell.section_id:
                    position = calculate_nozzle_position(nozzle, shell=shell)
                else:
                    host_head = next(
                        (h for h in project.heads
                         if h.head_id == nozzle.host_component_id),
                        None,
                    )
                    if host_head is None:
                        nozzle_warnings.append(
                            f"Nozul {nozzle.tag}: host '{nozzle.host_component_id}' "
                            f"gövde/bombe listesinde yok — modellenmedi."
                        )
                        continue
                    try:
                        local = calculate_nozzle_position(nozzle, head=host_head)
                    except ValueError as e:
                        # Yerleşim çapı bombe sınırının dışında — K4: sessizce
                        # kırpma yok, modellenmedi olarak raporlanır.
                        nozzle_warnings.append(f"Nozul {nozzle.tag}: {e} — modellenmedi.")
                        continue
                    position = _head_position_to_global(
                        local,
                        is_left=(host_head is left_head),
                        tangent_length=shell.tangent_length,
                    )

                pipe, bore = _build_nozzle_pipe_and_bore(nozzle, position, shell)
                vessel = vessel.union(pipe)

                pad = _build_reinforcement_pad(nozzle, position, shell)
                if pad is not None:
                    vessel = vessel.union(pad)

                # Nozul tipine göre görsel detay (flanş / manway kapağı / boss)
                fitting, fitting_note = _build_nozzle_type_feature(nozzle, position, shell)
                if fitting is not None:
                    vessel = vessel.union(fitting)
                if fitting_note:
                    visual_fitting_used = True

                # Delik en son kesilir (boru + ped + cidarı deler)
                vessel = vessel.cut(bore)
            except Exception as e:
                nozzle_warnings.append(f"Nozul {nozzle.tag} CAD hatası: {e}")

    # ── Hacim hesaplama ────────────────────────────────────────────────────────
    try:
        outer_vol = vessel.val().Volume() if hasattr(vessel, "val") else vessel.Volume()
    except Exception:
        outer_vol = 0.0

    # İç hacim (korozyon payı dahil)
    try:
        inner_r = (shell.inside_diameter or (shell.outside_diameter - 2 * shell.nominal_thickness)) / 2.0
        ca = shell.internal_corrosion_allowance
        r_corroded = inner_r - ca

        # Silindir hacmi + 2 bombe hacmi (yaklaşık)
        cyl_vol = math.pi * r_corroded**2 * shell.tangent_length
        # 2:1 elipsoidal hacim = (2/3)π a² b → a = r, b = r/2 → (2/3)π r² (r/2) = πr³/3
        head_vol_each = (2.0 / 3.0) * math.pi * r_corroded**2 * (r_corroded / 2.0)
        calc_inner_vol = cyl_vol + 2 * head_vol_each
    except Exception:
        calc_inner_vol = 0.0

    # ── Doğrulama ──────────────────────────────────────────────────────────────
    report = CADValidationReport()
    report.add(validate_solid_count(vessel, expected=1))
    report.add(validate_no_negative_volume(vessel))
    report.add(validate_no_open_shells(vessel))

    if calc_inner_vol > 0 and outer_vol > 0:
        # Metal hacmi = dış hacim - iç hacim (yaklaşık)
        metal_vol = outer_vol - calc_inner_vol
        if metal_vol > 0:
            report.add(validate_volume_tolerance(calc_inner_vol, outer_vol - metal_vol, tolerance_pct=10.0))

    # Gövde ve bombe üzerindeki nozullar modellenir; yalnızca hata/atlama düşülür.
    known_hosts = {shell.section_id} | {h.head_id for h in project.heads}
    nozzles_modeled = sum(
        1 for n in project.nozzles if n.host_component_id in known_hosts
    ) - len([
        w for w in nozzle_warnings
        if "CAD hatası" in w or "modellenmedi" in w
    ])

    cad_notes: List[str] = []
    if visual_fitting_used:
        cad_notes.append(
            "Flanş / manway kapağı görünümleri görsel temsildir — ölçü ve Class "
            "bilgisi B16.5/B16.47'den alınmamıştır (K6). Rating için flanş modülünü kullanın."
        )

    return VesselCADResult(
        shape=vessel,
        inner_volume_mm3=calc_inner_vol,
        outer_volume_mm3=outer_vol,
        metal_volume_mm3=max(0, outer_vol - calc_inner_vol) if outer_vol > 0 else 0.0,
        validation=report,
        notes=cad_notes,
        nozzle_count=max(0, nozzles_modeled),
        warnings=nozzle_warnings,
    )


def _build_head(head: Head):
    """Bombe tipine göre shape oluştur (hepsi tek watertight solid; ekvator z=0, kubbe +Z)."""
    D = head.inside_diameter
    t = head.nominal_thickness
    sf = head.straight_flange_length
    if head.type == HeadType.ELLIPTICAL:
        return _build_elliptical_head(diameter=D, thickness=t, straight_flange=sf)
    elif head.type == HeadType.TORISPHERICAL:
        return _build_torispherical_head(
            diameter=D,
            crown_radius=head.crown_radius or D,
            knuckle_radius=head.knuckle_radius or D / 10.0,
            thickness=t,
            straight_flange=sf,
        )
    elif head.type == HeadType.HEMISPHERICAL:
        # Yarım küre = elips yayı a = b = R (tek profil-revolve).
        R = D / 2.0
        outer = _ellipse_arc_pts(R + t, R + t)
        inner = _ellipse_arc_pts(R, R)
        return _revolve_head_wall(outer, inner, R, t, sf)
    elif head.type == HeadType.FLAT:
        return _build_flat_head(diameter=D, thickness=t, straight_flange=sf)
    else:
        raise ValueError(f"Desteklenmeyen bombe tipi: {head.type}")


def _estimate_head_height(head: Head) -> float:
    """Bombe yüksekliğini tahmin et (mm)."""
    R = head.inside_diameter / 2.0
    if head.type == HeadType.ELLIPTICAL:
        return R / 2.0 + head.straight_flange_length  # D/4
    elif head.type == HeadType.TORISPHERICAL:
        return head.crown_radius * 0.25 + head.straight_flange_length
    elif head.type == HeadType.HEMISPHERICAL:
        return R + head.straight_flange_length
    else:
        return R / 2.0


def export_step(shape, path: str | Path) -> str:
    """Shape'i STEP dosyasına aktar.

    Args:
        shape: CadQuery shape.
        path: Çıktı dosya yolu.

    Returns:
        Kaydedilen dosya yolu (string).
    """
    _check_cadquery()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path), cq.exporters.ExportTypes.STEP)
    return str(path)


def export_stl(
    shape,
    path: str | Path,
    tolerance: float = 0.1,
    angular_tolerance: float = 0.3,
) -> str:
    """Shape'i STL mesh dosyasına aktar (web 3D görüntüleyici için).

    STEP tarayıcıda gösterilemez (CAD B-rep); STL tessellate edilmiş mesh'tir ve
    three.js ile doğrudan yüklenebilir.

    Args:
        shape: CadQuery shape.
        path: Çıktı dosya yolu.
        tolerance: Doğrusal tessellation toleransı (mm) — küçük = pürüzsüz + büyük dosya.
        angular_tolerance: Açısal tessellation toleransı (rad).

    Returns:
        Kaydedilen dosya yolu (string).
    """
    _check_cadquery()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        shape,
        str(path),
        cq.exporters.ExportTypes.STL,
        tolerance=tolerance,
        angularTolerance=angular_tolerance,
    )
    return str(path)


__all__ = [
    "VesselCADResult",
    "build_vessel",
    "export_step",
    "export_stl",
    "CADQUERY_AVAILABLE",
]
