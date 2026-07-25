"""1/8 simetri modeli — analiz geometrisi hazırlığı (FEA doğrulama laboratuvarı, Faz 2 — 2.2).

Kapalı bir basınçlı kabı desteklerinden/mesnetlerinden sabitleyerek çözmek,
sınır şartının kendisinden kaynaklanan yapay (gerçek dışı) gerilme yığılmaları
üretir; bu, kapalı-form ASME hesabıyla anlamlı bir karşılaştırmayı imkânsız
kılar. Bunun yerine kap üç simetri düzleminde (x=0, y=0, orta boy düzlemi
z=L/2) 1/8'e kesilir. Üç düzlemde de normal deplasman sıfırlanınca rijit
cisim hareketi tamamen kalkar, yapay gerilme sıfır olur ve eleman sayısı
sekizde birine iner.

Bu simetri yalnızca aşağıdaki önkoşullar sağlandığında geçerlidir (aksi halde
1/8 kesim geometrik olarak YANLIŞ bir model üretir):
  - Nozul yok (nozul simetriyi bozar).
  - İki bombe (sol + sağ) birbirinin aynısı (tip, çap, kalınlık, taç/büküm
    yarıçapı, düz flanş boyu) — orta boy düzlemi ancak böyle bir simetri
    düzlemidir.
  - Tek, üniform gövde kesiti (mevcut `cad_engine.build_vessel()` zaten yalnızca
    `project.shell_sections[0]`'ı modelliyor; birden fazla kesit varsa kullanıcı
    verisi sessizce göz ardı edilmiş olur — K4 bunu engeller).
  - Yalnız iç basınç (dış basınç/vakum kollaps modu simetrik olmayabilir).
  - Destek/mesnet CAD geometrisine hiç dahil değil (`packages/supports` ayrı,
    harici girdilerle çalışır — bkz. modül sonundaki not).

Önkoşul sağlanmazsa analiz sessizce zorlanmaz (K4): `check_symmetry_preconditions`
ret sebeplerini döner, `build_eighth_symmetry_geometry` bunları `error` alanında
raporlar.

K2: CAD/FEA hesabın kaynağı DEĞİLDİR — geometri üretimi hiçbir gerilme/kalınlık
hesabı yapmaz, PASS üretmez. Bu dosyada ayrıca `check_material_elastic_properties`
bulunur; bu fonksiyon bir `CalculationResult` döner ama yalnızca eksik malzeme
verisi durumunda BLOCKED_CODE_DATA raporlar — asla PASS/FAIL yazmaz (K2/K4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    import cadquery as cq

    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False

from calc_core.result import CalculationResult
from domain.enums import HeadType
from domain.geometry import Head
from domain.project import VesselProject

from cad_engine.vessel_builder import build_vessel, export_step

# Orta boy düzlemi + iki dik simetri düzlemi için "özdeşlik" ölçütü — yalnızca
# geometriyi (dolayısıyla CAD şeklini) etkileyen bombe alanları karşılaştırılır.
# material_id/weld_joint_id/head_id gibi tanımlayıcılar kasıtlı olarak dışarıda
# bırakılır (iki bombe farklı malzeme ID'sine sahip olsa bile geometrik olarak
# özdeşse simetri düzlemi geçerlidir).
_HEAD_GEOMETRY_FIELDS = (
    "type",
    "inside_diameter",
    "nominal_thickness",
    "straight_flange_length",
    "crown_radius",
    "knuckle_radius",
)


def _check_cadquery() -> None:
    if not CADQUERY_AVAILABLE:
        raise ImportError(
            "CadQuery kurulu değil. Yüklemek için: pip install cadquery"
        )


@dataclass
class EighthSymmetryResult:
    """1/8 simetri modeli üretim sonucu.

    K2: Bu sonuç bir hesap değildir — yalnızca geometri + doğrulanabilir
    ara değerler (hacim oranı vb.) taşır.
    """

    shape: Optional[object] = None  # CadQuery shape (1/8 kesilmiş model)
    step_path: Optional[str] = None
    full_volume_mm3: float = 0.0
    eighth_volume_mm3: float = 0.0
    volume_ratio: float = 0.0  # eighth / full — beklenen ≈ 0.125
    z_mid_mm: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.shape is not None and self.error is None


def check_symmetry_preconditions(project: VesselProject) -> List[str]:
    """1/8 simetri modeli önkoşullarını denetle.

    Sağlanmayan her koşul için insan-okunur bir ret sebebi döner; liste boşsa
    önkoşullar tamamdır. Sessizce zorlama YOK (K4) — burada toplanan sebepler
    çağıran tarafta reddin gerekçesi olarak raporlanır.
    """
    reasons: List[str] = []

    if project.nozzles:
        reasons.append(
            f"Nozul(lar) tanımlı ({len(project.nozzles)} adet) — 1/8 simetri modeli "
            "yalnızca nozulsuz kaplar için geçerlidir (nozul üç simetri düzlemini de bozar)."
        )

    if len(project.shell_sections) != 1:
        reasons.append(
            f"Gövde kesiti sayısı {len(project.shell_sections)} (1 olmalı) — 1/8 model "
            "yalnızca tek, üniform gövde kesitli kaplar için tanımlıdır."
        )

    if len(project.heads) != 2:
        reasons.append(
            f"Bombe sayısı {len(project.heads)} (2 olmalı) — 1/8 simetri modeli iki "
            "bombeli kapalı kap varsayar."
        )
    else:
        left, right = project.heads[0], project.heads[1]
        if left.type == HeadType.FLAT or right.type == HeadType.FLAT:
            reasons.append(
                "Düz kapak (FLAT) bombe tipi 1/8 simetri modelini desteklemez — "
                "düz kapak mukavemet hesabı zaten V1'de NOT_CALCULATED (K2); FEA "
                "karşılaştırması için elliptical/torispherical/hemispherical kullanın."
            )
        else:
            mismatches = _head_geometry_mismatches(left, right)
            if mismatches:
                reasons.append(
                    "İki bombe geometrik olarak özdeş değil (fark: "
                    + ", ".join(mismatches)
                    + ") — orta boy düzlemi (z=L/2) bu durumda bir simetri düzlemi olamaz."
                )

    dc = project.design_conditions
    if dc.external_pressure > 0 or dc.vacuum_condition:
        reasons.append(
            "Kapta dış basınç/vakum koşulu tanımlı — 1/8 model yalnızca iç basınç "
            "yükü için geçerlidir (dış basınç/vakum kollaps modu simetrik olmayabilir)."
        )

    return reasons


def check_material_elastic_properties(project: VesselProject) -> Optional[CalculationResult]:
    """Kapla ilişkili malzemelerin lineer-elastik verisini (E, ν) denetle.

    FEA lab, kapalı-form ASME/EN hesaplarının aksine lineer-elastik malzeme
    modeli (elastisite modülü + Poisson oranı) gerektirir. Bu alanlar
    `MaterialProperty`de opsiyoneldir (K3/K6 — telifli tablo gömülmez, kullanıcı
    girer); biri bile eksikse laboratuvar **varsayım atamadan** durur (K4).

    Args:
        project: VesselProject. Yalnızca gövde/bombelerin referans ettiği
            malzemeler denetlenir (projedeki kullanılmayan malzemeler değil).

    Returns:
        Eksik veri yoksa None (laboratuvar devam edebilir). Eksikse
        `status=BLOCKED_CODE_DATA` olan bir `CalculationResult` — asla
        PASS/FAIL üretmez (K2).
    """
    material_ids = sorted(
        {shell.material_id for shell in project.shell_sections}
        | {head.material_id for head in project.heads}
    )

    missing: List[str] = []
    for material_id in material_ids:
        mat = project.get_material(material_id)
        if mat is None:
            missing.append(f"{material_id}: proje malzeme listesinde tanımlı değil")
            continue
        if mat.elastic_modulus is None:
            missing.append(f"{material_id}: elastic_modulus (E) girilmemiş")
        if mat.poisson_ratio is None:
            missing.append(f"{material_id}: poisson_ratio (ν) girilmemiş")

    if not missing:
        return None

    result = CalculationResult(
        component_id="vessel",
        component_type="system",
        calculation_type="fea_material_data_check",
        code="FEA",
        clause_reference="Faz 2 FEA doğrulama laboratuvarı — lineer-elastik malzeme önkoşulu",
    )
    result.input_snapshot = {"material_ids_checked": material_ids}
    result.add_assumption(
        "FEA lab yalnızca kullanıcının girdiği elastic_modulus/poisson_ratio "
        "değerlerini kullanır; standart tablosundan varsayılan ATANMAZ (K4/K6)."
    )
    result.set_blocked_code_data(
        "FEA lab için gerekli lineer-elastik malzeme verisi eksik: "
        + "; ".join(missing)
        + ". Laboratuvar bu veriler girilmeden devam edemez."
    )
    return result


def _head_geometry_mismatches(left: Head, right: Head) -> List[str]:
    """İki bombenin geometrik alanlarını karşılaştır; farklı olanların adını döndür."""
    return [
        f for f in _HEAD_GEOMETRY_FIELDS
        if getattr(left, f, None) != getattr(right, f, None)
    ]


def _octant_cutting_box(bbox, z_mid: float, margin_mm: float = 50.0):
    """x∈[0,∞), y∈[0,∞), z∈[z_mid,∞) yarım-uzayını kesen, modeli tamamen
    kapsayacak kadar büyük bir kesme kutusu üret.

    Model x<0/y<0'a hiç taşmıyorsa (kap ekseni X=Y=0 merkezli inşa edildiği
    için beklenen durum budur) kutu [0, x_max]×[0, y_max]×[z_mid, z_max]
    aralığını kaplar; bu şekilde `shape.intersect(box)` tam olarak istenen
    1/8 dilimini üretir.
    """
    _check_cadquery()
    x_max = bbox.xmax + margin_mm
    y_max = bbox.ymax + margin_mm
    z_max = bbox.zmax + margin_mm
    dz = z_max - z_mid

    return (
        cq.Workplane("XY")
        .workplane(offset=z_mid)
        .moveTo(x_max / 2.0, y_max / 2.0)
        .rect(x_max, y_max)
        .extrude(dz)
    )


def build_eighth_symmetry_geometry(
    project: VesselProject,
    step_output_path: Optional[str | Path] = None,
    volume_ratio_tolerance_pct: float = 2.0,
) -> EighthSymmetryResult:
    """Projeden 1/8 simetri modeli üret.

    Args:
        project: VesselProject (yalnızca `project.shell_sections[0]` +
            `project.heads[0:2]` kullanılır — mevcut `cad_engine.build_vessel()`
            davranışıyla tutarlı).
        step_output_path: Verilirse 1/8 model bu yola STEP olarak yazılır.
        volume_ratio_tolerance_pct: Hacim oranı (1/8 hacim / tam hacim) beklenen
            %12.5'ten bu yüzdeden fazla sapıyorsa uyarı eklenir (geometri
            önkoşulları sağlansa bile beklenmedik bir asimetriye işaret edebilir).

    Returns:
        EighthSymmetryResult — önkoşul sağlanmazsa veya CAD üretimi başarısız
        olursa `error` doldurulur, `shape` None kalır.
    """
    reasons = check_symmetry_preconditions(project)
    if reasons:
        return EighthSymmetryResult(
            shape=None,
            error="1/8 simetri modeli önkoşulu sağlanmadı: " + "; ".join(reasons),
        )

    _check_cadquery()

    cad_result = build_vessel(project)
    if not cad_result.success:
        return EighthSymmetryResult(
            shape=None, error=f"Tam kap CAD modeli üretilemedi: {cad_result.error}"
        )

    shell = project.shell_sections[0]
    z_mid = shell.tangent_length / 2.0

    full_solid = cad_result.shape.val()
    full_volume = full_solid.Volume()
    if full_volume <= 0:
        return EighthSymmetryResult(
            shape=None, error="Tam kap CAD modelinin hacmi sıfır/negatif — kesim yapılamaz."
        )

    try:
        bbox = full_solid.BoundingBox()
        box = _octant_cutting_box(bbox, z_mid)
        eighth = cad_result.shape.intersect(box)
        eighth_solid = eighth.val()
    except Exception as e:
        return EighthSymmetryResult(shape=None, error=f"1/8 kesim (boolean intersect) hatası: {e}")

    eighth_volume = eighth_solid.Volume()
    ratio = eighth_volume / full_volume if full_volume > 0 else 0.0

    result = EighthSymmetryResult(
        shape=eighth,
        full_volume_mm3=full_volume,
        eighth_volume_mm3=eighth_volume,
        volume_ratio=ratio,
        z_mid_mm=z_mid,
    )

    diff_pct = abs(ratio - 0.125) / 0.125 * 100.0
    if diff_pct > volume_ratio_tolerance_pct:
        result.warnings.append(
            f"1/8 kesim hacim oranı {ratio:.4f} (beklenen ≈0.125, sapma %{diff_pct:.2f}) "
            "— geometri önkoşulları sağlanmış görünse de beklenmedik bir asimetri olabilir; "
            "mühendis incelemesi gerekir."
        )

    if step_output_path is not None:
        try:
            result.step_path = export_step(eighth, step_output_path)
        except Exception as e:
            result.warnings.append(f"STEP export hatası: {e}")

    return result


__all__ = [
    "CADQUERY_AVAILABLE",
    "EighthSymmetryResult",
    "check_symmetry_preconditions",
    "check_material_elastic_properties",
    "build_eighth_symmetry_geometry",
]
