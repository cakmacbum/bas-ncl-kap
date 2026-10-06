"""STEP tanıyıcı — kullanıcının STEP modelinden dönel kap geometrisini ÖNERİ olarak çıkarır.

K2 kuralı: CAD hesabın kaynağı değildir. Buradan çıkan her değer sihirbaz formuna yalnızca
öneri olarak gider; kullanıcı onaylamadan hiçbir hesaba girmez.
K4 kuralı: sessiz varsayım yok. Tanınmayan her öğe `unrecognized` listesinde, her varsayım
`warnings` listesinde açıkça raporlanır. Malzeme / P / T / E / korozyon payı dosyada yoktur ve
her yanıtta `not_in_file` ile bildirilir.

Kapsam (V1):
  - Tek kapalı katı; ortak eksenli silindir gövde (iç + dış silindir) + iki bombe.
  - Bombe tipleri: yarım küre, gerçek torisferik (küre + torus yüzeyleri), 2:1 elipsoidal
    (dönel yüzey ya da çokyüzlü yaklaşım), düz kapak.
  - Gövde üzerindeki radyal nozullar (OD / ID / boyun kalınlığı / eksenel konum / θ).
  - Koni, bombe nozulu, eğik/eksen dışı nozul, çoklu gövde, destek vb. → `unrecognized`
    (status PARTIAL).
  - Kutu, çoklu katı, kalınlıksız yüzey modeli, okunamayan dosya → REJECTED + Türkçe sebep.
  - CAD çekirdeği (OCP/CadQuery) yoksa → BLOCKED. Hiçbir durumda exception sızdırmaz.

Koordinat kuralları (SPEC §8):
  - Eksenel koordinat silindir ekseni boyuncadır; "sol" bombe eksende küçük koordinattakidir.
    Eksen ≈ ±Z ise yön +Z'ye çevrilir.
  - θ, `nozzles/position.py` ile aynı: eksen ≈ Z iken +X'ten, +Y'ye doğru (derece, 0–360).
    Eksen Z değilse referans keyfidir → θ güveni "low" + uyarı.
  - Nozul eksenel konumu sol tanjant hattından (gövde iç silindirinin sol ucu) ölçülür.
  - Birim dosyadan okunur; OCC okuyucu değerleri mm'ye çevirir. Okunamazsa mm kabul + uyarı.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:  # CAD çekirdeği opsiyonel — yoksa BLOCKED döneriz (exception yok).
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepGProp import BRepGProp, BRepGProp_Face
    from OCP.BRepTools import BRepTools
    from OCP.GeomAbs import (
        GeomAbs_Circle,
        GeomAbs_Cone,
        GeomAbs_Cylinder,
        GeomAbs_Plane,
        GeomAbs_Sphere,
        GeomAbs_SurfaceOfRevolution,
        GeomAbs_Torus,
    )
    from OCP.gp import gp_Pnt, gp_Vec
    from OCP.GProp import GProp_GProps
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import (
        TopAbs_EDGE,
        TopAbs_FACE,
        TopAbs_SHELL,
        TopAbs_SOLID,
        TopAbs_VERTEX,
    )
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    CAD_KERNEL_AVAILABLE = True
except ImportError:  # pragma: no cover - ortam bağımlı
    CAD_KERNEL_AVAILABLE = False


NOT_IN_FILE: Tuple[str, ...] = (
    "material",
    "design_pressure",
    "design_temperature",
    "joint_efficiency",
    "corrosion_allowance",
)

# SPEC §8 — 2:1 elips: h/D = 0.25 ± 0.005 ; yarım küre h/D = 0.5 ± 0.005
_RATIO_TOL = 0.005
_PROFILE_FIT_TOL = 0.005  # profil uydurma kalıntısı / a (göreli)

Vec = Tuple[float, float, float]


# ── Sonuç veri yapıları (S-3 JSON şemasının birebir karşılığı) ────────────────


@dataclass
class RecognizedField:
    """Tek bir önerilen değer. value: sayı (mm / derece) ya da metin."""

    value: Any
    confidence: str = "high"  # "high" | "medium" | "low"
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "confidence": self.confidence, "note": self.note}


@dataclass
class StepSource:
    filename: Optional[str]
    unit: str = "mm"
    unit_scale: float = 1.0  # 1 dosya birimi = unit_scale mm
    solid_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "unit": self.unit,
            "unit_scale": self.unit_scale,
            "solid_count": self.solid_count,
        }


@dataclass
class ShellRecognition:
    inside_diameter: RecognizedField
    nominal_thickness: RecognizedField
    tangent_length: RecognizedField

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inside_diameter": self.inside_diameter.to_dict(),
            "nominal_thickness": self.nominal_thickness.to_dict(),
            "tangent_length": self.tangent_length.to_dict(),
        }


@dataclass
class HeadRecognition:
    side: str  # "left" | "right"
    type: RecognizedField
    inside_diameter: RecognizedField
    nominal_thickness: RecognizedField
    straight_flange_length: Optional[RecognizedField]
    crown_radius: Optional[RecognizedField] = None
    knuckle_radius: Optional[RecognizedField] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "side": self.side,
            "type": self.type.to_dict(),
            "inside_diameter": self.inside_diameter.to_dict(),
            "nominal_thickness": self.nominal_thickness.to_dict(),
            "straight_flange_length": (
                self.straight_flange_length.to_dict() if self.straight_flange_length else None
            ),
            "crown_radius": self.crown_radius.to_dict() if self.crown_radius else None,
            "knuckle_radius": self.knuckle_radius.to_dict() if self.knuckle_radius else None,
        }


@dataclass
class NozzleRecognition:
    tag: str
    outside_diameter: RecognizedField
    inside_diameter: RecognizedField
    neck_thickness: RecognizedField
    axial_position: RecognizedField
    circumferential_angle: RecognizedField
    outside_projection: RecognizedField

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "outside_diameter": self.outside_diameter.to_dict(),
            "inside_diameter": self.inside_diameter.to_dict(),
            "neck_thickness": self.neck_thickness.to_dict(),
            "axial_position": self.axial_position.to_dict(),
            "circumferential_angle": self.circumferential_angle.to_dict(),
            "outside_projection": self.outside_projection.to_dict(),
        }


@dataclass
class UnrecognizedFeature:
    feature: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {"feature": self.feature, "reason": self.reason}


@dataclass
class StepRecognition:
    """STEP tanıma sonucu. `to_dict()` → ORKESTRA S-3 JSON şeması."""

    status: str  # "RECOGNIZED" | "PARTIAL" | "REJECTED" | "BLOCKED"
    source: StepSource
    shell: Optional[ShellRecognition] = None
    heads: List[HeadRecognition] = field(default_factory=list)
    nozzles: List[NozzleRecognition] = field(default_factory=list)
    unrecognized: List[UnrecognizedFeature] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    not_in_file: List[str] = field(default_factory=lambda: list(NOT_IN_FILE))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "source": self.source.to_dict(),
            "shell": self.shell.to_dict() if self.shell else None,
            "heads": [h.to_dict() for h in self.heads],
            "nozzles": [n.to_dict() for n in self.nozzles],
            "unrecognized": [u.to_dict() for u in self.unrecognized],
            "warnings": list(self.warnings),
            "not_in_file": list(self.not_in_file),
        }


# ── Küçük vektör yardımcıları ────────────────────────────────────────────────


def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a: Vec, k: float) -> Vec:
    return (a[0] * k, a[1] * k, a[2] * k)


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a: Vec) -> float:
    return math.sqrt(_dot(a, a))


def _unit(a: Vec) -> Vec:
    n = _norm(a)
    return (1.0, 0.0, 0.0) if n < 1e-12 else _mul(a, 1.0 / n)


def _xyz(p) -> Vec:
    return (p.X(), p.Y(), p.Z())


def _r2(v: float) -> float:
    """SPEC §8: uzunluklar 0.01 mm hassasiyetle verilir."""
    return round(float(v), 2)


# ── Birim okuma ──────────────────────────────────────────────────────────────

_UNIT_PATTERNS = (
    (re.compile(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", re.I), "mm", 1.0),
    (re.compile(r"SI_UNIT\s*\(\s*\.CENTI\.\s*,\s*\.METRE\.\s*\)", re.I), "cm", 10.0),
    (re.compile(r"SI_UNIT\s*\(\s*\$\s*,\s*\.METRE\.\s*\)", re.I), "m", 1000.0),
    (re.compile(r"CONVERSION_BASED_UNIT\s*\(\s*'INCH'", re.I), "inch", 25.4),
    (re.compile(r"CONVERSION_BASED_UNIT\s*\(\s*'FOOT'", re.I), "ft", 304.8),
)


def _detect_unit(text: str) -> Tuple[Optional[str], float]:
    """Dosyadaki uzunluk birimini bul. Bulunamazsa (None, 1.0)."""
    found = [(name, scale) for rx, name, scale in _UNIT_PATTERNS if rx.search(text)]
    if not found:
        return None, 1.0
    if len({n for n, _ in found}) > 1:
        # Birden çok uzunluk birimi — ilkini al, çağıran uyarı yazar.
        return found[0][0] + "?", found[0][1]
    return found[0]


# ── OCC yardımcıları ─────────────────────────────────────────────────────────


def _explore(shape, kind, avoid=None) -> list:
    exp = TopExp_Explorer(shape, kind, avoid) if avoid is not None else TopExp_Explorer(shape, kind)
    out = []
    while exp.More():
        out.append(exp.Current())
        exp.Next()
    return out


@dataclass
class _FaceInfo:
    face: Any
    kind: str  # "plane" | "cylinder" | "cone" | "sphere" | "torus" | "revolution" | "other"
    area: float
    samples: List[Vec]  # profil için güvenilir noktalar
    centroid: Vec
    mid_point: Vec
    normal: Vec  # yüz yönelimi dikkate alınmış (malzemeden dışa)
    axis_loc: Optional[Vec] = None
    axis_dir: Optional[Vec] = None
    radius: Optional[float] = None
    minor_radius: Optional[float] = None
    # sınıflandırma
    axisym: bool = False
    role: str = ""  # "shell_in" | "shell_out" | "left" | "right" | "nozzle" | "other"


_KIND = {}
if CAD_KERNEL_AVAILABLE:
    _KIND = {
        GeomAbs_Plane: "plane",
        GeomAbs_Cylinder: "cylinder",
        GeomAbs_Cone: "cone",
        GeomAbs_Sphere: "sphere",
        GeomAbs_Torus: "torus",
        GeomAbs_SurfaceOfRevolution: "revolution",
    }


def _edge_points(edge, n: int = 8) -> List[Vec]:
    c = BRepAdaptor_Curve(edge)
    t0, t1 = c.FirstParameter(), c.LastParameter()
    if not (math.isfinite(t0) and math.isfinite(t1)):
        return []
    return [_xyz(c.Value(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]


def _face_info(face) -> _FaceInfo:
    ad = BRepAdaptor_Surface(face)
    kind = _KIND.get(ad.GetType(), "other")

    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face, props)
    area = props.Mass()
    centroid = _xyz(props.CentreOfMass())

    umin, umax, vmin, vmax = BRepTools.UVBounds_s(face)
    um, vm = 0.5 * (umin + umax), 0.5 * (vmin + vmax)
    p, v = gp_Pnt(), gp_Vec()
    BRepGProp_Face(face).Normal(um, vm, p, v)
    normal = _unit((v.X(), v.Y(), v.Z()))
    mid_point = _xyz(p)

    info = _FaceInfo(face, kind, area, [], centroid, mid_point, normal)

    if kind == "cylinder":
        cyl = ad.Cylinder()
        info.axis_loc, info.axis_dir = _xyz(cyl.Axis().Location()), _xyz(cyl.Axis().Direction())
        info.radius = cyl.Radius()
    elif kind == "cone":
        cone = ad.Cone()
        info.axis_loc, info.axis_dir = _xyz(cone.Axis().Location()), _xyz(cone.Axis().Direction())
    elif kind == "sphere":
        sph = ad.Sphere()
        info.axis_loc, info.radius = _xyz(sph.Location()), sph.Radius()
    elif kind == "torus":
        tor = ad.Torus()
        info.axis_loc, info.axis_dir = _xyz(tor.Axis().Location()), _xyz(tor.Axis().Direction())
        info.radius, info.minor_radius = tor.MajorRadius(), tor.MinorRadius()
    elif kind == "revolution":
        ax = ad.AxeOfRevolution()
        info.axis_loc, info.axis_dir = _xyz(ax.Location()), _xyz(ax.Direction())
    elif kind == "plane":
        info.axis_dir = _xyz(ad.Plane().Axis().Direction())

    # Profil örnekleri:
    #  - koni: yalnız dairesel kenarlar (çokyüzlü bombede köşe noktaları gerçek profil
    #    üzerindedir; dikiş çizgileri kiriştir, kullanılmaz),
    #  - düzlem: kenar noktaları (UV kutusu disk dışına taşar),
    #  - diğerleri: kenar noktaları + UV ızgarası (alttaki dönel yüzey profili verir).
    samples: List[Vec] = []
    edges = _explore(face, TopAbs_EDGE)
    if kind == "cone":
        for e in edges:
            ca = BRepAdaptor_Curve(TopoDS.Edge_s(e))
            if ca.GetType() == GeomAbs_Circle:
                samples.extend(_edge_points(TopoDS.Edge_s(e), 4))
        for vx in _explore(face, TopAbs_VERTEX):
            samples.append(_xyz(BRep_Tool.Pnt_s(TopoDS.Vertex_s(vx))))
    else:
        for e in edges:
            samples.extend(_edge_points(TopoDS.Edge_s(e), 8))
        if kind != "plane" and all(math.isfinite(x) for x in (umin, umax, vmin, vmax)):
            n = 8
            for i in range(n + 1):
                for j in range(n + 1):
                    samples.append(
                        _xyz(ad.Value(umin + (umax - umin) * i / n, vmin + (vmax - vmin) * j / n))
                    )
    info.samples = samples or [centroid]
    return info


# ── Eksen çerçevesi ──────────────────────────────────────────────────────────


@dataclass
class _Frame:
    origin: Vec
    d: Vec  # eksen yönü (birim)
    x_ref: Vec
    y_ref: Vec
    axis_is_z: bool

    def s(self, p: Vec) -> float:
        return _dot(_sub(p, self.origin), self.d)

    def r(self, p: Vec) -> float:
        w = _sub(p, self.origin)
        return _norm(_sub(w, _mul(self.d, _dot(w, self.d))))

    def on_axis(self, p: Vec, tol: float) -> bool:
        return self.r(p) <= tol

    def parallel(self, v: Vec, ang_tol: float = 2e-3) -> bool:
        return _norm(_cross(_unit(v), self.d)) <= ang_tol

    def coaxial(self, loc: Optional[Vec], direction: Optional[Vec], tol: float) -> bool:
        return (
            loc is not None
            and direction is not None
            and self.parallel(direction)
            and self.on_axis(loc, tol)
        )


def _make_frame(loc: Vec, direction: Vec) -> _Frame:
    d = _unit(direction)
    axis_is_z = abs(d[2]) >= 0.999
    if axis_is_z:
        if d[2] < 0:
            d = _mul(d, -1.0)
        x_ref = _unit(_sub((1.0, 0.0, 0.0), _mul(d, d[0])))
    else:
        k = max(range(3), key=lambda i: abs(d[i]))
        if d[k] < 0:
            d = _mul(d, -1.0)
        x_ref = _unit(_sub((0.0, 0.0, 1.0), _mul(d, d[2])))
    y_ref = _cross(d, x_ref)
    return _Frame(loc, d, x_ref, y_ref, axis_is_z)


# ── Ana giriş ────────────────────────────────────────────────────────────────


def recognize_step(path, filename: Optional[str] = None) -> StepRecognition:
    """STEP dosyasından dönel kap geometrisini tanı (öneri; K2).

    Hiçbir durumda exception fırlatmaz: CAD çekirdeği yoksa BLOCKED, dosya okunamaz /
    geçersizse REJECTED döner.

    Args:
        path: STEP dosya yolu.
        filename: Kullanıcıya gösterilecek özgün dosya adı (yoksa yol adından).

    Returns:
        StepRecognition (`to_dict()` → S-3 JSON).
    """
    try:
        fname = filename if filename is not None else Path(path).name
    except Exception:
        fname = filename
    source = StepSource(filename=fname)

    if not CAD_KERNEL_AVAILABLE:
        return StepRecognition(
            status="BLOCKED",
            source=source,
            warnings=["CAD motoru (CadQuery/OCP) kurulu değil — STEP dosyası tanınamadı."],
        )

    try:
        return _recognize(Path(path), source)
    except Exception as exc:  # K4: sızdırma yok, açık sebep
        return _rejected(
            source, "file", f"Dosya işlenirken beklenmeyen hata: {type(exc).__name__}: {exc}"
        )


def _rejected(source: StepSource, feature: str, reason: str, warnings=None) -> StepRecognition:
    return StepRecognition(
        status="REJECTED",
        source=source,
        unrecognized=[UnrecognizedFeature(feature, reason)],
        warnings=list(warnings or []),
    )


def _recognize(path: Path, source: StepSource) -> StepRecognition:
    warnings: List[str] = []

    if not path.is_file():
        return _rejected(source, "file", "Dosya bulunamadı.")

    # ── Birim (dosyadan) ──
    try:
        text = path.read_bytes().decode("latin-1", errors="replace")
    except OSError as exc:
        return _rejected(source, "file", f"Dosya okunamadı: {exc}")
    if "ISO-10303-21" not in text[:4096]:
        return _rejected(source, "file", "Dosya STEP (ISO-10303-21) biçiminde değil.")
    unit, scale = _detect_unit(text)
    if unit is None:
        unit, scale = "mm", 1.0
        warnings.append("Dosyada uzunluk birimi bulunamadı — mm kabul edildi; ölçüleri doğrulayın.")
    elif unit.endswith("?"):
        unit = unit[:-1]
        warnings.append(f"Dosyada birden çok uzunluk birimi var — '{unit}' kullanıldı.")
    source.unit, source.unit_scale = unit, scale
    del text

    # ── Oku (OCC değerleri mm'ye çevirir) ──
    try:
        Interface_Static.SetCVal_s("xstep.cascade.unit", "MM")
    except Exception:
        pass
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        return _rejected(source, "file", "STEP dosyası ayrıştırılamadı (bozuk ya da desteklenmeyen içerik).", warnings)
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape is None or shape.IsNull():
        return _rejected(source, "file", "STEP dosyasında aktarılabilir geometri yok.", warnings)

    solids = _explore(shape, TopAbs_SOLID)
    source.solid_count = len(solids)
    if not solids:
        free = _explore(shape, TopAbs_FACE)
        why = (
            "Dosyada katı (solid) yok, yalnız yüzey/kabuk var — kalınlıksız model tanınamaz; "
            "et kalınlığı verilmiş katı model gerekir."
            if free
            else "Dosyada katı geometri yok."
        )
        return _rejected(source, "solid", why, warnings)
    if len(solids) > 1:
        return _rejected(
            source,
            "solid",
            f"Dosyada {len(solids)} ayrı katı var — V1 tek parça (birleştirilmiş) kap katısı ister.",
            warnings,
        )
    solid = TopoDS.Solid_s(solids[0])
    for sh in _explore(solid, TopAbs_SHELL):
        if not BRep_Tool.IsClosed_s(sh):
            return _rejected(source, "solid", "Katı kapalı değil (açık kabuk) — geçerli hacim yok.", warnings)
    if not BRepCheck_Analyzer(solid).IsValid():
        warnings.append("Katı, OCC geometri geçerlilik kontrolünden geçmedi — sonuçları dikkatle doğrulayın.")

    faces = [_face_info(TopoDS.Face_s(f)) for f in _explore(solid, TopAbs_FACE)]
    return _analyze(faces, source, warnings)


# ── Geometri analizi ─────────────────────────────────────────────────────────


def _analyze(faces: List[_FaceInfo], source: StepSource, warnings: List[str]) -> StepRecognition:
    unrec: List[UnrecognizedFeature] = []

    cylinders = [f for f in faces if f.kind == "cylinder"]
    if not cylinders:
        return _rejected(
            source, "shell", "Silindirik gövde bulunamadı — dönel basınçlı kap tanınmadı.", warnings
        )

    main = max(cylinders, key=lambda f: f.area)
    fr = _make_frame(main.axis_loc, main.axis_dir)
    big_r = max((f.radius for f in cylinders if fr.coaxial(f.axis_loc, f.axis_dir, 1.0)), default=main.radius)
    ltol = max(0.02, 1e-5 * big_r)

    # Eksenel simetri sınıflaması
    for f in faces:
        if f.kind in ("cylinder", "cone", "torus", "revolution"):
            f.axisym = fr.coaxial(f.axis_loc, f.axis_dir, ltol * 5)
        elif f.kind == "sphere":
            f.axisym = fr.on_axis(f.axis_loc, ltol * 5)
        elif f.kind == "plane":
            f.axisym = fr.parallel(f.axis_dir)
        else:
            f.axisym = False

    def concave(f: _FaceInfo) -> bool:
        # Normal eksene doğru → iç yüzey (boşluk tarafı)
        w = _sub(f.mid_point, fr.origin)
        radial = _sub(w, _mul(fr.d, _dot(w, fr.d)))
        return _dot(f.normal, radial) < 0

    co_cyl = [f for f in cylinders if f.axisym]
    inner_c = [f for f in co_cyl if concave(f)]
    outer_c = [f for f in co_cyl if not concave(f)]
    if not inner_c or not outer_c:
        return _rejected(
            source,
            "shell",
            "Eş eksenli iç ve dış silindir çifti yok (dolu çubuk ya da içi boş olmayan model) — "
            "gövde tanınamadı.",
            warnings,
        )
    ri_face = max(inner_c, key=lambda f: f.area)
    ro_face = max(outer_c, key=lambda f: f.area)
    ri, ro = ri_face.radius, ro_face.radius
    if ro <= ri + ltol:
        return _rejected(source, "shell", "Dış silindir iç silindirden büyük değil — et kalınlığı yok.", warnings)
    rtol = max(ltol, 1e-4 * ri)

    shell_in = [f for f in inner_c if abs(f.radius - ri) <= rtol]
    shell_out = [f for f in outer_c if abs(f.radius - ro) <= rtol]
    for f in shell_in:
        f.role = "shell_in"
    for f in shell_out:
        f.role = "shell_out"

    s_in = [fr.s(p) for f in shell_in for p in f.samples]
    z0, z1 = min(s_in), max(s_in)
    L = z1 - z0
    if L <= ltol:
        return _rejected(source, "shell", "Gövde silindirinin boyu sıfır.", warnings)

    # Düz flanş: iç silindir yüzü uçlara yakın dairesel dikişlerle bölünmüşse ölçülür.
    sf_left, sf_right = _straight_flange_splits(shell_in, fr, z0, z1, ri, rtol)

    shell = ShellRecognition(
        inside_diameter=RecognizedField(_r2(2 * ri), "high"),
        nominal_thickness=RecognizedField(_r2(ro - ri), "high"),
        tangent_length=RecognizedField(
            _r2(L), "high", "Gövde iç silindirinin eksenel boyu (bombe başlangıçları arası)."
        ),
    )

    # Diğer eş eksenli silindirler: gövde aralığında farklı çap → çoklu gövde / kademe
    for f in co_cyl:
        if f.role:
            continue
        ss = [fr.s(p) for p in f.samples]
        if min(ss) < z1 - ltol and max(ss) > z0 + ltol:
            f.role = "other"
            unrec.append(
                UnrecognizedFeature(
                    "multiple_shells",
                    f"Gövde aralığında farklı çaplı eş eksenli silindir (Ø{_r2(2 * f.radius)} mm) — "
                    "çoklu gövde / kademeli çap / iç eleman V1'de tanınmaz.",
                )
            )

    # ── Nozul grupları (eş eksenli olmayan silindirler) ──
    nozzles, nozzle_groups = _nozzle_groups(faces, fr, ltol, ro, z0, z1)

    # Nozul gruplarına ait olmayan simetrik olmayan yüzleri ata
    for f in faces:
        if f.role or f.axisym:
            continue
        for g in nozzle_groups:
            if g.owns(f):
                f.role = "nozzle"
                g.faces.append(f)
                break

    # ── Bölgelere ayır ──
    left, right, stray_sym, stray_nonsym_shell = [], [], [], []
    for f in faces:
        if f.role:
            continue
        ss = [fr.s(p) for p in f.samples]
        if max(ss) <= z0 + ltol * 5:
            left.append(f)
            f.role = "left"
        elif min(ss) >= z1 - ltol * 5:
            right.append(f)
            f.role = "right"
        elif f.axisym:
            stray_sym.append(f)
        else:
            stray_nonsym_shell.append(f)

    if stray_sym:
        kinds = sorted({f.kind for f in stray_sym})
        cone = "cone" in kinds
        unrec.append(
            UnrecognizedFeature(
                "cone" if cone else "unknown",
                (
                    "Gövde aralığında konik yüzey — koni/konik geçiş V1'de tanınmaz."
                    if cone
                    else f"Gövde aralığında tanınmayan dönel yüzey(ler): {', '.join(kinds)}."
                ),
            )
        )
    if stray_nonsym_shell:
        unrec.append(
            UnrecognizedFeature(
                "unknown",
                f"Gövde üzerinde nozul olarak tanınmayan {len(stray_nonsym_shell)} yüz "
                "(destek, kulak, eğik/eksen dışı bağlantı vb.) — V1'de tanınmaz.",
            )
        )
    for g in nozzle_groups:
        if g.unrec is not None:
            unrec.append(g.unrec)

    # ── Bombeler ──
    center = _add(fr.origin, _mul(fr.d, 0.5 * (z0 + z1)))
    heads: List[HeadRecognition] = []
    head_ok = True
    for side, region, z_t, sign, sf in (
        ("left", left, z0, -1.0, sf_left),
        ("right", right, z1, +1.0, sf_right),
    ):
        head, head_unrec, head_warn = _analyze_head(side, region, fr, z_t, sign, center, ri, ltol, sf)
        unrec.extend(head_unrec)
        warnings.extend(head_warn)
        if head is None:
            head_ok = False
        else:
            heads.append(head)
    if not head_ok:
        heads = []  # S-3: 0 veya 2 eleman

    if not fr.axis_is_z:
        warnings.append(
            "Kap ekseni Z değil — θ referansı keyfi seçildi (eksene dik düzleme izdüşen +Z); "
            "nozul açılarını doğrulayın."
        )

    status = "RECOGNIZED" if (len(heads) == 2 and not unrec) else "PARTIAL"
    return StepRecognition(
        status=status,
        source=source,
        shell=shell,
        heads=heads,
        nozzles=nozzles,
        unrecognized=unrec,
        warnings=warnings,
    )


def _straight_flange_splits(shell_in, fr: _Frame, z0, z1, ri, rtol):
    """İç silindir yüzlerinin uçlara yakın iç sınırlarından düz flanş boyunu çıkar.

    Bombe eteği gövdeyle aynı yüzeyde birleşmişse (dikiş yok) düz flanş dosyadan
    ayırt edilemez → None.
    """
    cuts = set()
    for f in shell_in:
        for e in _explore(f.face, TopAbs_EDGE):
            ca = BRepAdaptor_Curve(TopoDS.Edge_s(e))
            if ca.GetType() != GeomAbs_Circle:
                continue
            c = ca.Circle()
            if not fr.coaxial(_xyz(c.Location()), _xyz(c.Axis().Direction()), rtol * 5):
                continue
            if abs(c.Radius() - ri) > rtol:
                continue
            cuts.add(round(fr.s(_xyz(c.Location())), 3))
    L = z1 - z0
    inner = sorted(z for z in cuts if z0 + rtol < z < z1 - rtol)
    left = [z - z0 for z in inner if z - z0 <= 0.25 * L]
    right = [z1 - z for z in inner if z1 - z <= 0.25 * L]
    return (min(left) if left else None), (min(right) if right else None)


# ── Nozullar ─────────────────────────────────────────────────────────────────


@dataclass
class _NozzleGroup:
    loc: Vec
    direction: Vec
    faces: List[_FaceInfo]
    max_radius: float
    radial_dir: Vec = (1.0, 0.0, 0.0)
    unrec: Optional[UnrecognizedFeature] = None

    def line_dist(self, p: Vec) -> float:
        w = _sub(p, self.loc)
        return _norm(_sub(w, _mul(self.direction, _dot(w, self.direction))))

    def owns(self, f: _FaceInfo) -> bool:
        lim = self.max_radius * 1.1 + 1.0
        return all(self.line_dist(p) <= lim for p in (f.centroid, f.mid_point))


def _nozzle_groups(faces, fr: _Frame, ltol, ro, z0, z1):
    groups: List[_NozzleGroup] = []
    for f in faces:
        if f.kind != "cylinder" or f.axisym:
            continue
        d = _unit(f.axis_dir)
        for g in groups:
            if _norm(_cross(d, g.direction)) <= 2e-3 and g.line_dist(f.axis_loc) <= ltol * 5:
                g.faces.append(f)
                g.max_radius = max(g.max_radius, f.radius)
                break
        else:
            groups.append(_NozzleGroup(f.axis_loc, d, [f], f.radius))
    for g in groups:
        for f in g.faces:
            f.role = "nozzle"

    recognized: List[Tuple[float, float, NozzleRecognition]] = []
    for g in groups:
        # Ana eksenle en yakın yaklaşım
        d, n = fr.d, g.direction
        w0 = _sub(g.loc, fr.origin)
        c = _cross(d, n)
        cn = _norm(c)
        centroid = _mul(
            (sum(f.centroid[0] for f in g.faces), sum(f.centroid[1] for f in g.faces), sum(f.centroid[2] for f in g.faces)),
            1.0 / len(g.faces),
        )
        s_c = fr.s(centroid)
        if cn < 1e-6:
            # Ana eksene paralel, eksen dışı silindir
            region_head = s_c < z0 or s_c > z1
            g.unrec = UnrecognizedFeature(
                "head_nozzle" if region_head else "unknown",
                (
                    "Bombe üzerinde eksene paralel nozul/öğe — bombe nozulu V1'de tanınmaz."
                    if region_head
                    else "Gövde eksenine paralel, eksen dışı silindirik öğe — V1'de tanınmaz."
                ),
            )
            continue
        dist = abs(_dot(w0, c)) / cn
        # Kesişim noktasının ana eksen koordinatı
        # w0 + t n = s d + (dik) → en yakın noktalar
        b = _dot(d, n)
        dw, nw = _dot(d, w0), _dot(n, w0)
        denom = 1.0 - b * b
        s_int = (dw - b * nw) / denom
        perpendicular = abs(b) <= 2e-3
        intersects = dist <= max(ltol * 10, 0.5)
        in_shell = z0 - ltol <= s_int <= z1 + ltol

        if not intersects:
            g.unrec = UnrecognizedFeature(
                "offset_nozzle",
                "Ekseni kap eksenini kesmeyen (teğetsel/eksen dışı) nozul — V1'de tanınmaz.",
            )
            continue
        if not in_shell or s_c < z0 - ltol or s_c > z1 + ltol:
            g.unrec = UnrecognizedFeature(
                "head_nozzle", "Bombe üzerinde nozul — bombe nozulu V1'de tanınmaz."
            )
            continue
        if not perpendicular:
            ang = math.degrees(math.acos(min(1.0, abs(b))))
            g.unrec = UnrecognizedFeature(
                "oblique_nozzle",
                f"Eğik nozul (eksenle açı {ang:.1f}°, radyal değil) — V1'de tanınmaz.",
            )
            continue

        p_int = _add(fr.origin, _mul(fr.d, s_int))
        u = n if _dot(_sub(centroid, p_int), n) >= 0 else _mul(n, -1.0)
        g.radial_dir = u

        def is_concave(f: _FaceInfo) -> bool:
            w = _sub(f.mid_point, p_int)
            radial = _sub(w, _mul(u, _dot(w, u)))
            return _dot(f.normal, radial) < 0

        bores = sorted({round(f.radius, 4) for f in g.faces if is_concave(f)})
        outs = sorted({round(f.radius, 4) for f in g.faces if not is_concave(f)})
        if not bores or not outs or min(outs) <= bores[0]:
            g.unrec = UnrecognizedFeature(
                "unknown",
                "Gövde üzerinde boyun çapı/deliği ayırt edilemeyen radyal silindirik öğe — V1'de tanınmaz.",
            )
            continue
        r_id = bores[0]
        r_od = min(o for o in outs if o > r_id)
        extra = [o for o in outs if o > r_od + ltol]

        # θ: nozzles/position.py — +X'ten (eksen ≈ Z iken)
        theta = math.degrees(math.atan2(_dot(u, fr.y_ref), _dot(u, fr.x_ref))) % 360.0
        if theta >= 359.995:
            theta = 0.0

        # Dış çıkıntı: nozula ait yüzlerin eksen boyunca en uç noktası − gövde dış yarıçapı
        tip = max(_dot(_sub(p, p_int), u) for f in g.faces for p in f.samples)
        proj_note = "Gövde dış yüzeyinden nozulun en uç noktasına (varsa flanş yüzü dahil) ölçüldü."
        recognized.append(
            (
                s_int - z0,
                theta,
                NozzleRecognition(
                    tag="",
                    outside_diameter=RecognizedField(
                        _r2(2 * r_od),
                        "medium" if extra else "high",
                        (
                            "Boyunda ek eş eksenli silindirler var (flanş/ped?): Ø"
                            + ", Ø".join(str(_r2(2 * e)) for e in extra)
                            + " mm — en küçük dış çap boyun kabul edildi."
                        )
                        if extra
                        else None,
                    ),
                    inside_diameter=RecognizedField(_r2(2 * r_id), "high"),
                    neck_thickness=RecognizedField(_r2(r_od - r_id), "medium" if extra else "high"),
                    axial_position=RecognizedField(
                        _r2(s_int - z0), "high", "Sol tanjant hattından nozul eksenine (mm)."
                    ),
                    circumferential_angle=RecognizedField(
                        round(theta, 2),
                        "high" if fr.axis_is_z else "low",
                        None if fr.axis_is_z else "Kap ekseni Z değil — θ referansı keyfi.",
                    ),
                    outside_projection=RecognizedField(_r2(max(0.0, tip - ro)), "medium", proj_note),
                ),
            )
        )

    recognized.sort(key=lambda t: (round(t[0], 2), t[1]))
    out = []
    for i, (_, _, nz) in enumerate(recognized, start=1):
        nz.tag = f"N{i}"
        out.append(nz)
    return out, groups


# ── Bombeler ─────────────────────────────────────────────────────────────────


def _fit_ellipse_depth(pts: Sequence[Tuple[float, float]], a: float) -> Tuple[float, float]:
    """h = H·sqrt(1 − (r/a)²) en küçük kareler. Döner: (H, max göreli kalıntı / a)."""
    num = den = 0.0
    us = []
    for r, h in pts:
        u = math.sqrt(max(0.0, 1.0 - (min(r, a) / a) ** 2))
        us.append(u)
        num += h * u
        den += u * u
    if den <= 1e-12:
        return 0.0, float("inf")
    H = num / den
    res = max(abs(h - H * u) for (r, h), u in zip(pts, us)) / a
    return H, res


def _analyze_head(side, region, fr: _Frame, z_t, sign, center, ri, ltol, sf):
    """Tek bombe bölgesini tanı. Döner: (HeadRecognition | None, unrecognized, warnings)."""
    unrec: List[UnrecognizedFeature] = []
    warns: List[str] = []
    label = "Sol" if side == "left" else "Sağ"

    def depth(p: Vec) -> float:
        return sign * (fr.s(p) - z_t)

    if not region:
        return None, [UnrecognizedFeature("head", f"{label} bombe bulunamadı (gövde ucu açık ya da tanınmadı).")], warns

    nonsym = [f for f in region if not f.axisym]
    if nonsym:
        unrec.append(
            UnrecognizedFeature(
                "head_nozzle",
                f"{label} bombe üzerinde simetrik olmayan öğe ({len(nonsym)} yüz; bombe nozulu vb.) — "
                "V1'de tanınmaz.",
            )
        )

    # Eksen üzerindeki küçük eş eksenli silindirler → merkez bombe nozulu
    sym = [f for f in region if f.axisym]
    small_cyl = [f for f in sym if f.kind == "cylinder" and f.radius < 0.95 * ri]
    r_cut = 0.0
    if small_cyl:
        r_cut = max(f.radius for f in small_cyl) * 1.05 + ltol
        unrec.append(
            UnrecognizedFeature(
                "head_nozzle", f"{label} bombe merkezinde eksenel nozul — bombe nozulu V1'de tanınmaz."
            )
        )

    def is_inner(f: _FaceInfo) -> bool:
        return _dot(f.normal, _sub(center, f.mid_point)) > 0

    prof = [f for f in sym if f not in small_cyl and not (f.kind == "cylinder" and f.radius < 0.95 * ri)]
    inner = [f for f in prof if is_inner(f)]
    outer = [f for f in prof if not is_inner(f)]

    def pts(fs):
        out = []
        for f in fs:
            for p in f.samples:
                r = fr.r(p)
                if r >= r_cut:
                    out.append((r, max(0.0, depth(p))))
        return out

    p_in, p_out = pts(inner), pts(outer)
    if not p_in or not p_out:
        unrec.append(UnrecognizedFeature("head", f"{label} bombenin iç/dış yüzeyi ayırt edilemedi."))
        return None, unrec, warns

    a = max(r for r, _ in p_in)
    a_o = max(r for r, _ in p_out)
    id_field = RecognizedField(_r2(2 * a), "high")
    if abs(a - ri) > max(ltol * 5, 1e-3 * ri):
        id_field = RecognizedField(
            _r2(2 * a), "medium", f"Bombe iç çapı gövdeden farklı (gövde Ø{_r2(2 * ri)} mm)."
        )
        warns.append(f"{label} bombe iç çapı (Ø{_r2(2 * a)}) gövde iç çapından (Ø{_r2(2 * ri)}) farklı.")

    if sf is not None:
        sf_field = RecognizedField(
            _r2(sf), "medium", "İç silindir yüzündeki dikişten ölçüldü (tanjant boyunun içinde)."
        )
    else:
        # K4: yer tutucu değer önerilmez — alan null, sebep uyarıda.
        sf_field = None
        warns.append(
            f"{label} bombe düz flanşı gövde silindiriyle aynı yüzeyde birleşmiş — dosyadan "
            "ayırt edilemez. Değeri formdan/çizimden girin."
        )

    kinds_in = [f.kind for f in inner]
    kinds_out = [f.kind for f in outer]
    max_h_in = max(h for _, h in p_in)

    def finish(type_val, conf, note, t, t_conf="high", t_note=None, rc=None, rk=None):
        return (
            HeadRecognition(
                side=side,
                type=RecognizedField(type_val, conf, note),
                inside_diameter=id_field,
                nominal_thickness=RecognizedField(_r2(t), t_conf, t_note),
                straight_flange_length=sf_field,
                crown_radius=rc,
                knuckle_radius=rk,
            ),
            unrec,
            warns,
        )

    # ── Gerçek torisferik: küre (taç) + torus (hamut) ──
    if "sphere" in kinds_in and "torus" in kinds_in:
        sph_in = [f for f in inner if f.kind == "sphere"]
        tor_in = [f for f in inner if f.kind == "torus"]
        sph_out = [f for f in outer if f.kind == "sphere"]
        Rc = max(sph_in, key=lambda f: f.area).radius
        rk = max(tor_in, key=lambda f: f.area).minor_radius
        major = max(tor_in, key=lambda f: f.area).radius
        if abs(major - (a - rk)) > max(ltol * 5, 2e-3 * a):
            warns.append(f"{label} torisferik bombe: torus büyük yarıçapı D/2 − rk ile tutarsız.")
        if sph_out:
            t = max(sph_out, key=lambda f: f.area).radius - Rc
            t_conf = "high"
        else:
            t = max(h for _, h in p_out) - max_h_in
            t_conf = "medium"
        return finish(
            "torispherical", "high", None, t, t_conf,
            rc=RecognizedField(_r2(Rc), "high", "İç taç küresi yarıçapı."),
            rk=RecognizedField(_r2(rk), "high", "İç hamut (torus) yarıçapı."),
        )

    # ── Koni ──
    cones_in = [f for f in inner if f.kind == "cone"]
    curved_in = [f for f in inner if f.kind not in ("plane", "cone")]
    if cones_in and not curved_in and len(cones_in) <= 2:
        unrec.append(UnrecognizedFeature("cone", f"{label} uçta konik bombe/geçiş — koni V1'de tanınmaz."))
        return None, unrec, warns

    # ── Düz kapak ──
    if all(k == "plane" for k in kinds_in) and max_h_in <= ltol * 5:
        planes_out = [f for f in outer if f.kind == "plane"]
        if not planes_out:
            unrec.append(UnrecognizedFeature("head", f"{label} düz kapağın dış yüzü bulunamadı."))
            return None, unrec, warns
        t = max(max(0.0, depth(p)) for f in planes_out for p in f.samples)
        return finish("flat", "high", None, t)

    # ── Yarım küre (analitik) ──
    if kinds_in and all(k == "sphere" for k in kinds_in):
        R = max((f for f in inner), key=lambda f: f.area).radius
        sph_out = [f for f in outer if f.kind == "sphere"]
        if abs(R - a) <= max(ltol * 5, 2e-3 * a) and sph_out:
            t = max(sph_out, key=lambda f: f.area).radius - R
            return finish("hemispherical", "high", None, t)
        unrec.append(
            UnrecognizedFeature(
                "head",
                f"{label} bombe küresel kap (R={_r2(R)} mm ≠ D/2) ve hamut yok — V1'de tanınmaz.",
            )
        )
        return None, unrec, warns

    # ── Profil uydurma (elips / küre; dönel yüzey ya da çokyüzlü) ──
    faceted = len(cones_in) >= 4
    H, res = _fit_ellipse_depth(p_in, a)
    if not math.isfinite(res) or res > _PROFILE_FIT_TOL:
        hint = (
            " Torisferikse STEP'in analitik küre + torus yüzeyleri içermesi gerekir."
            if faceted
            else ""
        )
        unrec.append(
            UnrecognizedFeature(
                "head", f"{label} bombe profili elips/küreye uymuyor (sapma {res * 100:.2f}% · D/2).{hint}"
            )
        )
        return None, unrec, warns
    H_o, res_o = _fit_ellipse_depth(p_out, a_o)
    t_crown = H_o - H
    t_eq = a_o - a
    t_note = None
    t_conf = "medium" if faceted else "high"
    if abs(t_crown - t_eq) > max(ltol * 10, 0.01 * t_eq):
        t_note = f"Tepe kalınlığı {_r2(t_crown)} mm, ekvatordaki {_r2(t_eq)} mm — tepe değeri önerildi."
        t_conf = "medium"
    ratio = H / (2 * a)
    note = (
        f"Çokyüzlü (faceted) yüzey; profil köşe noktalarından uyduruldu, h/D = {ratio:.4f}."
        if faceted
        else f"Profil uydurma, h/D = {ratio:.4f}."
    )
    conf = "medium" if faceted else "high"
    if abs(ratio - 0.5) <= _RATIO_TOL:
        return finish("hemispherical", conf, note, t_crown, t_conf, t_note)
    if abs(ratio - 0.25) <= _RATIO_TOL:
        return finish("elliptical", conf, note, t_crown, t_conf, t_note)
    unrec.append(
        UnrecognizedFeature(
            "head",
            f"{label} bombe eliptik, desteklenmeyen h/D oranı {ratio:.3f} "
            "(yalnız 2:1 = 0.25 ve yarım küre = 0.5 desteklenir).",
        )
    )
    return None, unrec, warns


__all__ = [
    "CAD_KERNEL_AVAILABLE",
    "NOT_IN_FILE",
    "RecognizedField",
    "StepSource",
    "ShellRecognition",
    "HeadRecognition",
    "NozzleRecognition",
    "UnrecognizedFeature",
    "StepRecognition",
    "recognize_step",
]
