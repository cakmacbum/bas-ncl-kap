"""Geometri modelleri — ShellSection, Head, Nozzle.

K7 kuralı: Bu modeller standarttan bağımsızdır; ASME/EN kuralları code plugin'lerinde uygulanır.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator

from domain.enums import HeadType, NozzleType


class ShellSection(BaseModel):
    """Silindirik gövde kesiti (kaynak §6).

    İç çap veya dış çaptan biri girilir; diğeri et kalınlığından türetilir.
    """

    section_id: str = Field(..., description="Gövde kesit tanımı (ör. 'SHELL-01').")
    inside_diameter: Optional[float] = Field(
        default=None, gt=0, description="İç çap (mm)."
    )
    outside_diameter: Optional[float] = Field(
        default=None, gt=0, description="Dış çap (mm)."
    )
    tangent_length: float = Field(
        ..., gt=0, description="Teğet noktası uzunluğu (mm)."
    )
    nominal_thickness: float = Field(
        ..., gt=0, description="Nominal et kalınlığı (mm)."
    )
    material_id: str = Field(
        ..., description="Malzeme tanımı (Materials listesindeki ID)."
    )
    weld_joint_id: Optional[str] = Field(
        default=None, description="Kaynak dikişi ID'si (WeldJoint listesindeki)."
    )
    internal_corrosion_allowance: float = Field(
        default=0.0, ge=0, description="İç korozyon payı (mm)."
    )
    external_corrosion_allowance: float = Field(
        default=0.0, ge=0, description="Dış korozyon payı (mm)."
    )
    mill_tolerance: float = Field(
        default=0.0, ge=0,
        description="Negatif sac toleransı (%). ASME'de genellikle 12.5% (0.875 tabaka).",
    )
    forming_thinning: float = Field(
        default=0.0, ge=0,
        description="Şekillendirme incelmesi (mm). Bomba formundan kaynaklanan.",
    )

    @model_validator(mode="after")
    def _check_diameter(self) -> "ShellSection":
        if self.inside_diameter is None and self.outside_diameter is None:
            raise ValueError("inside_diameter veya outside_diameter'dan en az biri girilmeli.")
        return self


class Head(BaseModel):
    """Bombe (kaynak §6).

    Tip: elliptical, torispherical, hemispherical, flat.
    """

    head_id: str = Field(..., description="Bombe tanımı (ör. 'HEAD-L', 'HEAD-R').")
    type: HeadType = Field(..., description="Bombe tipi.")
    inside_diameter: float = Field(
        ..., gt=0, description="İç çap (mm). Gövde iç çapıyla aynı olmalı."
    )
    crown_radius: Optional[float] = Field(
        default=None, gt=0,
        description="Taç yarıçapı (mm). Torispherical için; diğer tiplerde inside_diameter'dan türetilir.",
    )
    knuckle_radius: Optional[float] = Field(
        default=None, gt=0,
        description="Büküm yarıçapı (mm). Torispherical için zorunlu.",
    )
    straight_flange_length: float = Field(
        default=25.0, ge=0,
        description="Düz flanş uzunluğu (mm). Varsayılan: 25 mm.",
    )
    nominal_thickness: float = Field(
        ..., gt=0, description="Nominal et kalınlığı (mm)."
    )
    material_id: str = Field(
        ..., description="Malzeme tanımı."
    )
    weld_joint_id: Optional[str] = Field(
        default=None, description="Kaynak dikişi ID'si."
    )
    internal_corrosion_allowance: float = Field(
        default=0.0, ge=0, description="İç korozyon payı (mm)."
    )
    external_corrosion_allowance: float = Field(
        default=0.0, ge=0, description="Dış korozyon payı (mm)."
    )
    mill_tolerance: float = Field(
        default=0.0, ge=0, description="Negatif sac toleransı (%)."
    )
    forming_thinning: float = Field(
        default=0.0, ge=0, description="Şekillendirme incelmesi (mm)."
    )
    flat_attachment_factor: Optional[float] = Field(
        default=None, gt=0,
        description="UG-34 C katsayısı — bağlantı tipi çizimine göre (ör. 0.13, 0.20, 0.33). "
                    "Kullanıcı girer (K4/K6). Yalnızca düz kapak (FLAT) tipi için.",
    )


class Nozzle(BaseModel):
    """Nozul (kaynak §6).

    Konum üç koordinatla tanımlanır: eksenel z, çevresel açı θ, eğim açısı α.
    V1'de radyal nozullar (α = 0) desteklenir.
    """

    tag: str = Field(..., description="Nozul etiketi (ör. 'N1', 'N2').")
    nozzle_type: NozzleType = Field(
        default=NozzleType.FLANGED, description="Nozul tipi."
    )
    host_component_id: str = Field(
        ..., description="Yerleştiği bileşen ID'si (ShellSection veya Head)."
    )
    axial_position: float = Field(
        ..., ge=0,
        description="Eksenel konum — gövde başlangıcından itibaren (mm).",
    )
    circumferential_angle: float = Field(
        default=0.0, ge=0, lt=360,
        description="Çevresel açı θ (derece). 0 = üst, 90 = yan.",
    )
    inclination_angle: float = Field(
        default=0.0, ge=0, le=90,
        description="Eğim açısı α (derece). 0 = radyal (dik).",
    )
    head_position_diameter: Optional[float] = Field(
        default=None, gt=0,
        description="Bombe merkez ekseninden ölçülen yerleşim çapı (mm). "
                    "Yalnızca host bombe ise geçerli; verilirse axial_position "
                    "yerine bu kullanılır (imalat çiziminden okunan ölçü).",
    )
    outside_diameter: float = Field(
        ..., gt=0, description="Dış çap (mm)."
    )
    inside_diameter: float = Field(
        ..., gt=0, description="İç çap (mm)."
    )
    neck_thickness: float = Field(
        ..., gt=0, description="Boyun et kalınlığı (mm)."
    )
    inside_projection: float = Field(
        default=0.0, ge=0, description="İç çıkıntı (mm)."
    )
    outside_projection: float = Field(
        default=0.0, ge=0, description="Dış çıkıntı (mm)."
    )
    size_designation: Optional[str] = Field(
        default=None,
        description="Katalogdan seçilen anma ölçüsü (ör. '1½\" SCH40'). K5: "
                    "raporda hangi katalog satırının kullanıldığı görünsün diye "
                    "saklanır; hesaba girmez.",
    )
    material_id: str = Field(
        ..., description="Malzeme tanımı."
    )
    corrosion_allowance: float = Field(
        default=0.0, ge=0, description="Korozyon payı (mm)."
    )
    reinforcement_pad: bool = Field(
        default=False, description="Takviye pedi var mı?"
    )
    reinforcement_pad_thickness: Optional[float] = Field(
        default=None, gt=0, description="Takviye pedi kalınlığı (mm)."
    )
    reinforcement_pad_od: Optional[float] = Field(
        default=None, gt=0, description="Takviye pedi dış çapı (mm)."
    )


class Cone(BaseModel):
    """Konik bölüm / reducer (kaynak §6).

    UG-32(g) + Appendix 1-4/1-5 koni-geçiş hesapları için.
    """

    cone_id: str = Field(..., description="Koni tanımı (ör. 'CONE-01').")
    large_diameter: float = Field(
        ..., gt=0, description="Büyük çap (mm). İç çap."
    )
    small_diameter: float = Field(
        ..., gt=0, description="Küçük çap (mm). İç çap."
    )
    half_apex_angle: float = Field(
        ..., ge=0, le=80,
        description="Yarı tepe açısı (derece). 30° üzeri uyarı gerektirir."
    )
    length: float = Field(
        ..., gt=0, description="Koni uzunluğu (mm)."
    )
    nominal_thickness: float = Field(
        ..., gt=0, description="Nominal et kalınlığı (mm)."
    )
    material_id: str = Field(
        ..., description="Malzeme tanımı."
    )
    weld_joint_id: Optional[str] = Field(
        default=None, description="Kaynak dikişi ID'si."
    )
    internal_corrosion_allowance: float = Field(
        default=0.0, ge=0, description="İç korozyon payı (mm)."
    )
    mill_tolerance: float = Field(
        default=0.0, ge=0, description="Negatif sac toleransı (%)."
    )


class Support(BaseModel):
    """Kap desteği — eyer (saddle), etek (skirt) veya ayak (leg).

    `supports` paketi bugüne dek hesap hattına bağlı değildi çünkü projede
    destek tanımı yoktu; bu model o boşluğu kapatır. Ağırlık burada İSTENMEZ —
    `calc_core.volume_mass` üzerinden hesaplanır (tek kaynak, K5).
    """

    support_id: str = Field(..., description="Destek tanımı (ör. 'SAD-01').")
    type: str = Field(
        ..., pattern="^(saddle|skirt|leg)$",
        description="Destek tipi: saddle | skirt | leg.",
    )
    location_mm: float = Field(
        default=0.0, ge=0,
        description="Kap ekseni boyunca konum (mm). Etek için taban kotu.",
    )
    width_mm: float = Field(
        ..., gt=0, description="Destek genişliği (mm). Eyerde temas genişliği."
    )
    height_mm: float = Field(
        ..., gt=0, description="Destek yüksekliği (mm)."
    )
    material_id: str = Field(..., description="Malzeme tanımı.")
    contact_angle_deg: Optional[float] = Field(
        default=None, ge=0, le=180,
        description="Eyer sarma açısı (derece). Zick analizi için; yalnız saddle.",
    )
    leg_count: Optional[int] = Field(
        default=None, gt=0,
        description="Ayak sayısı. Yalnız leg tipinde geçerli.",
    )


__all__ = ["ShellSection", "Head", "Nozzle", "Cone", "Support"]
