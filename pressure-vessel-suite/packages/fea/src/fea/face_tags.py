"""Yüzey etiketleme — geometrik yeniden tanıma (FEA doğrulama laboratuvarı, Faz 2 — 2.3).

Boolean işlemlerden (ör. 1/8 simetri kesimi, `geometry_prep.py`) sonra CadQuery/OCCT
yüzey indeksleri değişir — bu modül yüzey NUMARASINA hiç güvenmez. Her yüzeyi
kendi geometrik imzasıyla tanır:
  - kap eksenine (global Z ekseni) uzaklık,
  - yüzey tipi (CYLINDER / CONE / SPHERE / TORUS / PLANE),
  - dış normal yönü (eksene göre içe mi dışa mı bakıyor),
  - alan, eksenel (z) konum.

Etiketler: SHELL_INNER, SHELL_OUTER, HEAD_L_INNER, HEAD_R_INNER, SYM_X, SYM_Y, SYM_Z
(+ tamlık için HEAD_L_OUTER / HEAD_R_OUTER — yalnızca *_INNER etiketli yüzeylere
basınç uygulanır, OUTER etiketleri iz sürülebilirlik için tutulur).

K4: Bir yüzey yukarıdaki imzalardan hiçbirine güvenle uymuyorsa (ör. belirsiz
işaretli normal, tanınmayan yüzey tipi, beklenmeyen konumda düzlem) "muhtemelen
şudur" diye VARSAYIM YAPILMAZ — yüzey `unclassified` listesine düşer ve
`FaceTaggingResult.error` doldurulur; analiz orada durur.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False

from domain.geometry import ShellSection

# Yalnızca bu etiketlere basınç uygulanır (kap içindeki ıslak yüzeyler).
PRESSURE_TAGS: Tuple[str, ...] = ("SHELL_INNER", "HEAD_L_INNER", "HEAD_R_INNER")
SYMMETRY_TAGS: Tuple[str, ...] = ("SYM_X", "SYM_Y", "SYM_Z")
ALL_KNOWN_TAGS: Tuple[str, ...] = (
    "SHELL_INNER", "SHELL_OUTER",
    "HEAD_L_INNER", "HEAD_L_OUTER",
    "HEAD_R_INNER", "HEAD_R_OUTER",
    "SYM_X", "SYM_Y", "SYM_Z",
)

# Radyal normal ile eksenden-dışa vektörü arasındaki iç çarpımın işareti sınıfı
# belirler; kutba çok yakın facetlerde bile bu değer ~0.01 mertebesinde kalıp
# işaret değiştirmediği (ampirik doğrulama, bkz. rapor) için eşik çok küçük
# tutulabilir — asıl amaç tam sıfır/dejenere durumu ayıklamak.
_DOT_AMBIGUOUS_EPS = 1e-9
_RADIAL_DEGENERATE_EPS = 1e-6  # mm — eksen üzerindeki (r≈0) noktalar
_AXIS_ALIGN_EPS = 1e-3  # simetri düzlemi normali eksenle ne kadar hizalı olmalı


def _check_cadquery() -> None:
    if not CADQUERY_AVAILABLE:
        raise ImportError(
            "CadQuery kurulu değil. Yüklemek için: pip install cadquery"
        )


@dataclass
class TaggedFace:
    """Tek bir yüzeyin etiketi + geometrik imzası (izlenebilirlik için, K5)."""

    tag: str
    face: object  # CadQuery Face
    center: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    area: float
    geom_type: str


@dataclass
class FaceTaggingResult:
    """Bir shape'in tüm yüzeylerinin etiketleme sonucu."""

    tags: Dict[str, List[TaggedFace]] = field(default_factory=dict)
    unclassified: List[TaggedFace] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and not self.unclassified

    def get(self, tag: str) -> List[TaggedFace]:
        return self.tags.get(tag, [])

    def _add(self, tag: str, tf: TaggedFace) -> None:
        self.tags.setdefault(tag, []).append(tf)


def _shell_radii(shell: ShellSection) -> Tuple[float, float]:
    """Gövde iç/dış yarıçapı (mm) — `cad_engine.vessel_builder._shell_radii` ile
    aynı basit geometriyi (CAD üretiminden bağımsız olarak) yeniden türetir.
    Bu bir mühendislik formülü değildir (K1 kapsamı dışı); yalnızca çap/kalınlık
    aritmetiğidir.
    """
    if shell.inside_diameter:
        inner_r = shell.inside_diameter / 2.0
        outer_r = inner_r + shell.nominal_thickness
    else:
        outer_r = shell.outside_diameter / 2.0
        inner_r = outer_r - shell.nominal_thickness
    return inner_r, outer_r


def _uv_center(face) -> Tuple[Tuple[float, float, float], "BRepAdaptor_Surface"]:
    """Yüzeyin parametrik orta noktasını (u,v ortalaması) döndür.

    `Face.Center()` (kütle merkezi) trimlenmiş yüzeylerde yüzeyin ÜZERİNDE
    olmayabilir (ör. dar konik bantlar) ve `normalAt()` projeksiyonu bu durumda
    başarısız olur. Parametrik orta nokta her zaman yüzey üzerindedir.
    """
    ad = BRepAdaptor_Surface(face.wrapped)
    u0, u1 = ad.FirstUParameter(), ad.LastUParameter()
    v0, v1 = ad.FirstVParameter(), ad.LastVParameter()
    um, vm = (u0 + u1) / 2.0, (v0 + v1) / 2.0
    pnt = ad.Value(um, vm)
    return (pnt.X(), pnt.Y(), pnt.Z()), ad


def _classify_symmetry_plane(
    center: Tuple[float, float, float],
    normal: Tuple[float, float, float],
    z_mid: Optional[float],
    tolerance_mm: float,
) -> Optional[str]:
    """PLANE yüzeyi simetri düzlemi mi (SYM_X/SYM_Y/SYM_Z)? Değilse None
    (sessizce başka bir şey varsayılmaz — çağıran taraf unclassified'a ekler).
    """
    abs_n = (abs(normal[0]), abs(normal[1]), abs(normal[2]))
    dominant = abs_n.index(max(abs_n))

    if dominant == 0:  # normal ~ ±X
        if abs_n[0] >= 1.0 - _AXIS_ALIGN_EPS and abs(center[0]) <= tolerance_mm:
            return "SYM_X"
    elif dominant == 1:  # normal ~ ±Y
        if abs_n[1] >= 1.0 - _AXIS_ALIGN_EPS and abs(center[1]) <= tolerance_mm:
            return "SYM_Y"
    else:  # normal ~ ±Z
        if (
            z_mid is not None
            and abs_n[2] >= 1.0 - _AXIS_ALIGN_EPS
            and abs(center[2] - z_mid) <= tolerance_mm
        ):
            return "SYM_Z"
    return None


def _classify_cylinder(
    ad: "BRepAdaptor_Surface",
    inner_r: float,
    outer_r: float,
    tolerance_mm: float,
) -> Optional[str]:
    """CYLINDER yüzeyi gövde iç/dış yüzeyi mi? Değilse None."""
    cyl = ad.Cylinder()
    axis_dir = cyl.Axis().Direction()
    if abs(abs(axis_dir.Z()) - 1.0) > _AXIS_ALIGN_EPS:
        return None  # kap ekseni (global Z) ile hizalı değil — beklenmedik

    radius = cyl.Radius()
    if abs(radius - inner_r) <= tolerance_mm:
        return "SHELL_INNER"
    if abs(radius - outer_r) <= tolerance_mm:
        return "SHELL_OUTER"
    return None


def _classify_curved_head_face(
    center: Tuple[float, float, float],
    normal: Tuple[float, float, float],
    tangent_length: float,
    tolerance_mm: float,
) -> Optional[str]:
    """CONE/SPHERE/TORUS (bombe cidarı facetleri) yüzeyi HEAD_L/R_INNER/OUTER mi?

    Yöntem: yüzey merkezinden kap eksenine (global Z) dik uzaklık vektörü
    (radyal yön) ile yüzeyin dış normali arasındaki iç çarpımın işareti.
    Dış yüzeyde normal radyal yönle aynı yönlü (dış çarpım > 0), iç yüzeyde
    ters yönlü (< 0) olur. Bu, kutup noktasına yakın facetlerde de (küçük
    ama sıfırdan farklı iç çarpım büyüklüğü) işaret tutarlılığını korur —
    bkz. modül raporundaki ampirik doğrulama.
    """
    z = center[2]
    if z < -tolerance_mm:
        side = "L"
    elif z > tangent_length + tolerance_mm:
        side = "R"
    else:
        return None  # gövde aralığında eğrisel yüzey beklenmiyor — belirsiz

    rlen = math.hypot(center[0], center[1])
    if rlen < _RADIAL_DEGENERATE_EPS:
        return None  # tam eksen üzerinde — radyal yön tanımsız

    radial_x, radial_y = center[0] / rlen, center[1] / rlen
    dot = normal[0] * radial_x + normal[1] * radial_y
    if abs(dot) < _DOT_AMBIGUOUS_EPS:
        return None  # işaret belirsiz — tahmin yapma (K4)

    io = "OUTER" if dot > 0 else "INNER"
    return f"HEAD_{side}_{io}"


def tag_vessel_faces(
    shape,
    shell: ShellSection,
    z_mid: Optional[float] = None,
    tolerance_mm: float = 1.0,
) -> FaceTaggingResult:
    """Bir kap shape'inin (tam model veya 1/8 kesilmiş model) tüm yüzeylerini etiketle.

    Args:
        shape: CadQuery Workplane veya Shape (tek solid).
        shell: Gövde kesiti (iç/dış yarıçap + gövde uzunluğu referansı için).
        z_mid: Verilirse (1/8 model bekleniyorsa) orta boy simetri düzleminin
            z konumu (mm); SYM_Z bu değere göre aranır. None ise SYM_Z aranmaz
            (tam/kesilmemiş model için beklenen durum) ve eksikliği hata SAYILMAZ.
        tolerance_mm: Yarıçap/konum karşılaştırmalarında izin verilen tolerans (mm).

    Returns:
        FaceTaggingResult. Sınıflandırılamayan yüzey varsa veya (z_mid verildiği
        halde) simetri düzlemlerinden biri bulunamazsa `error` doldurulur (K4 —
        "muhtemelen budur" varsayımı yapılmaz, analiz durur).
    """
    _check_cadquery()

    solid = shape.val() if hasattr(shape, "val") else shape
    inner_r, outer_r = _shell_radii(shell)
    tangent_length = shell.tangent_length

    result = FaceTaggingResult()

    for f in solid.Faces():
        geom_type = f.geomType()
        center, ad = _uv_center(f)
        try:
            normal_v = f.normalAt(cq.Vector(*center))
            normal = (normal_v.x, normal_v.y, normal_v.z)
        except Exception as e:
            tf = TaggedFace(
                tag="UNCLASSIFIED", face=f, center=center, normal=(0.0, 0.0, 0.0),
                area=f.Area(), geom_type=geom_type,
            )
            result.unclassified.append(tf)
            result.error = (
                result.error or ""
            ) + f"Yüzey normali hesaplanamadı ({geom_type} @ {center}): {e}. "
            continue

        tag: Optional[str] = None
        if geom_type == "PLANE":
            tag = _classify_symmetry_plane(center, normal, z_mid, tolerance_mm)
        elif geom_type == "CYLINDER":
            tag = _classify_cylinder(ad, inner_r, outer_r, tolerance_mm)
        elif geom_type in ("CONE", "SPHERE", "TORUS"):
            tag = _classify_curved_head_face(center, normal, tangent_length, tolerance_mm)
        # Diğer yüzey tipleri (BSPLINE, BEZIER, OTHER, ...) tanınmaz — tag None kalır.

        tf = TaggedFace(
            tag=tag or "UNCLASSIFIED", face=f, center=center, normal=normal,
            area=f.Area(), geom_type=geom_type,
        )
        if tag is None:
            result.unclassified.append(tf)
        else:
            result._add(tag, tf)

    if result.unclassified:
        result.error = (
            (result.error or "")
            + f"{len(result.unclassified)} yüzey sınıflandırılamadı — "
            "'muhtemelen iç/dış yüzeydir' varsayımı yapılmadı (K4); analiz durur."
        )
    elif z_mid is not None:
        missing_sym = [t for t in SYMMETRY_TAGS if not result.get(t)]
        if missing_sym:
            result.error = (
                "1/8 model bekleniyordu ancak simetri düzlemi yüzeyleri bulunamadı: "
                + ", ".join(missing_sym)
                + " — geometri beklendiği gibi kesilmemiş olabilir."
            )

    return result


__all__ = [
    "CADQUERY_AVAILABLE",
    "PRESSURE_TAGS",
    "SYMMETRY_TAGS",
    "ALL_KNOWN_TAGS",
    "TaggedFace",
    "FaceTaggingResult",
    "tag_vessel_faces",
]
