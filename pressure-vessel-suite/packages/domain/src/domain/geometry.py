"""Geometri modelleri — ShellSection, Head, Nozzle.

K7 kuralı: Bu modeller standarttan bağımsızdır; ASME/EN kuralları code plugin'lerinde uygulanır.
"""

from __future__ import annotations

from typing import Literal, Optional

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
    ug28_strain_factor_a: Optional[float] = Field(
        default=None, gt=0,
        description="UG-28 Şekil G'den okunan A faktörü. K6: çizelge repoda tutulmaz, "
                    "kullanıcı lisanslı baskıdan okur. Boşsa dış basınç kontrolü bloke olur.",
    )
    ug28_allowable_stress_b: Optional[float] = Field(
        default=None, gt=0,
        description="UG-28 malzeme çizelgesinden okunan B faktörü (MPa). Aynı K6 gerekçesi.",
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
    torispherical_geometry: Literal["standard_asme_fd", "custom"] = Field(
        default="standard_asme_fd",
        description="Torisferik geometri rotası; özel geometri için yarıçaplar zorunludur.",
    )
    outside_diameter: Optional[float] = Field(default=None, gt=0, description="Dış çap (mm).")
    crown_depth: Optional[float] = Field(default=None, gt=0, description="Eliptik bombe derinliği h (mm).")
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
    flat_z_factor: Optional[float] = Field(default=None, gt=0, description="UG-34(c)(3) Z faktörü.")
    ug28_strain_factor_a: Optional[float] = Field(
        default=None, gt=0,
        description="UG-33 için Şekil G'den okunan A faktörü. K6: çizelge repoda tutulmaz.",
    )
    ug28_allowable_stress_b: Optional[float] = Field(
        default=None, gt=0,
        description="UG-33 malzeme çizelgesinden okunan B faktörü (MPa). Aynı K6 gerekçesi.",
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


class Junction(BaseModel):
    """Koni ucu ile komşu basınç taşıyan eleman birleşimi girdisi."""

    junction_id: str = Field(...)
    left_component_id: str = Field(...)
    right_component_id: str = Field(...)
    junction_type: Literal["cone_to_shell", "cone_to_head", "shell_to_shell"]
    cone_end: Optional[Literal["large", "small"]] = Field(
        default=None,
        description=(
            "Koni ucu birleşimi için birleşen uç. Topoloji komşuluğundan çıkarılmaz; "
            "tasarımcı tarafından açıkça belirtilmelidir."
        ),
    )
    weld_joint_id: Optional[str] = Field(default=None)
    weld_efficiency: Optional[float] = Field(default=None, gt=0, le=1)
    large_end_diameter: Optional[float] = Field(default=None, gt=0)
    small_end_diameter: Optional[float] = Field(default=None, gt=0)
    knuckle_radius_mm: Optional[float] = Field(default=None, gt=0)
    analysis_status: Literal["INPUT_ONLY", "REVIEW_REQUIRED", "SUPPORTED"] = "INPUT_ONLY"


class Flange(BaseModel):
    """Appendix 2 flanş girdisi; rating ve hesap rotası ayrıdır."""
    flange_id: str
    type: str = Field(default="integral", pattern="^(integral|loose)$")
    inside_diameter: float = Field(..., gt=0)
    outside_diameter: float = Field(..., gt=0)
    thickness: float = Field(..., gt=0)
    hub_small_thickness: float = Field(..., gt=0)
    hub_length: float = Field(..., gt=0)
    material_id: str
    gasket_m: Optional[float] = Field(default=None, gt=0)
    gasket_y: Optional[float] = Field(default=None, gt=0)
    bolt_count: Optional[int] = Field(default=None, gt=0)
    bolt_area: Optional[float] = Field(default=None, gt=0)
    bolt_allowable_stress: Optional[float] = Field(default=None, gt=0)
    # K6: Y ve f lisanslı ASME Appendix 2 (Şekil 2-7.1 / tablolar) çizelgesinden
    # KULLANICI tarafından okunur; koda gömülmez, boşsa hesap BLOCKED_MISSING_INPUT.
    flange_factor_Y: Optional[float] = Field(default=None, gt=0)
    flange_factor_f: Optional[float] = Field(default=None, gt=0)
    # K6: Şekil 2-7.1 boyutsuz faktörleri F, V, T, U de lisanslı eğrilerden kullanıcı
    # tarafından okunur; koda gömülmez/interpolasyon yapılmaz. Biri boşsa hesap bloke.
    flange_factor_F: Optional[float] = Field(default=None, gt=0)
    flange_factor_V: Optional[float] = Field(default=None, gt=0)
    flange_factor_T: Optional[float] = Field(default=None, gt=0)
    flange_factor_U: Optional[float] = Field(default=None, gt=0)
    # Appendix 2 g1: hub kalınlığı, BÜYÜK uç (flanş sırtı). `hub_small_thickness` = g0.
    # Varsayılan yok (K4): boşsa hesap bloke.
    hub_large_thickness: Optional[float] = Field(default=None, gt=0)
    # K6: W (cıvata tasarım yükü, N) ve M (flanşa etkiyen toplam moment, N·mm)
    # kullanıcının Appendix 2 çalışma sayfasından gelir; program hesaplamaz.
    # gt=0: moment bu modelde pozitif büyüklük olarak girilir; 0 girilirse gerilmeler
    # sıfır çıkıp sahte PASS üreteceğinden 0 geçersizdir. Boş = hesap bloke (varsayılan yok).
    bolt_load_W_N: Optional[float] = Field(default=None, gt=0)
    moment_M_Nmm: Optional[float] = Field(default=None, gt=0)
    rating_standard: Optional[str] = Field(default=None)


class WrcCoefficientEntry(BaseModel):
    """Bir WRC 107/537 nokta (A/B/C/D) x yük (P/ML/MC/VL/VC) için dört boyutsuz katsayı.

    K6: katsayılar lisanslı WRC bülteninden okunur, programda YOKTUR. `None` =
    okunmadı (hesap bloklanır, sıfır sayılmaz); bültende gerçekten sıfır olan
    bileşen açıkça 0.0 girilir.
    """

    Nx: Optional[float] = Field(default=None, description="Eksenel (boyuna) membran katsayısı.")
    Ny: Optional[float] = Field(default=None, description="Çevresel membran katsayısı.")
    Mx: Optional[float] = Field(default=None, description="Eksenel eğilme momenti katsayısı.")
    My: Optional[float] = Field(default=None, description="Çevresel eğilme momenti katsayısı.")


_WRC_POINTS = ("A", "B", "C", "D")
_WRC_LOADS = ("P", "ML", "MC", "VL", "VC")


class Support(BaseModel):
    """Kap desteği — eyer (saddle), etek (skirt) veya ayak (leg).

    `supports` paketi bugüne dek hesap hattına bağlı değildi çünkü projede
    destek tanımı yoktu; bu model o boşluğu kapatır. Ağırlık burada İSTENMEZ —
    `calc_core.volume_mass` üzerinden hesaplanır (tek kaynak, K5).
    """

    support_id: str = Field(..., description="Destek tanımı (ör. 'SAD-01').")
    host_component_id: Optional[str] = Field(
        default=None,
        description="Desteğin bağlandığı basınç taşıyan bileşen kimliği."
    )
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
    diameter_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Etek ORTALAMA çapı (mm) — dış/iç çap değil. Yalnız skirt tipinde.",
    )
    skirt_allowable_compressive_MPa: Optional[float] = Field(
        default=None, gt=0,
        description="UG-23(b) izin verilen basma gerilmesi B (MPa); tasarım sıcaklığında "
                    "Fig. çizelgesinden okunur (A = 0,125/(R/t)). Program bu değeri içermez "
                    "(K6); boşsa etek basma/burkulma kontrolü BLOCKED_CODE_DATA. Yalnız skirt.",
    )
    skirt_weld_efficiency: Optional[float] = Field(
        default=None, gt=0, le=1,
        description="Etek kaynak/birleşim verimi E (0<E<=1); çekme tarafı S·E. Boşsa "
                    "0,6 VARSAYILIR ve sonuca yazılır (K4). Yalnız skirt.",
    )
    thickness_mm: Optional[float] = Field(
        default=None, gt=0, description="Etek et kalınlığı (mm). Yalnız skirt tipinde."
    )
    material_id: str = Field(..., description="Malzeme tanımı.")
    contact_angle_deg: Optional[float] = Field(
        default=None, ge=0, le=180,
        description="Eyer sarma açısı (derece). Zick analizi için; yalnız saddle. "
                    "K katsayılarını okumak içindir (hesapta doğrudan kullanılmaz).",
    )
    saddle_stiffened: Optional[bool] = Field(
        default=None,
        description="Eyer düzleminde halka (ring) takviyesi var mı (yalnız saddle). "
                    "None = girilmedi → Zick hesabı bloke.",
    )
    zick_K1: Optional[float] = Field(
        default=None, gt=0,
        description="Zick K1 (eyer kesiti boyuna eğilme; Moss PVDM 3-10 / Zick 1951 Tablo I). "
                    "K6: tablo repoda tutulmaz, kullanıcı θ ve halka durumuna göre okur. "
                    "Halkalı / başlık-destekli (A ≤ R/2) durumda π sabiti kodla verilir.",
    )
    zick_K2: Optional[float] = Field(
        default=None, gt=0,
        description="Zick K2 (kabuk teğetsel kesme). Halkalı durumda 1/π kodla verilir. K6.",
    )
    zick_K3: Optional[float] = Field(
        default=None, gt=0,
        description="Zick K3 (başlık kesmesi; yalnız A ≤ R/2, halkasız). Moss adlandırması. K6.",
    )
    zick_K6: Optional[float] = Field(
        default=None, gt=0,
        description="Zick K6 (eyer boynuzu çevresel eğilme sabiti; θ ve A/R'ye bağlı). K6.",
    )
    zick_K7: Optional[float] = Field(
        default=None, gt=0,
        description="Zick K7 (eyer altı kabuk çevresel basma sabiti; θ'ya bağlı). K6.",
    )
    leg_count: Optional[int] = Field(
        default=None, gt=0,
        description="Ayak sayısı. Yalnız leg tipinde geçerli.",
    )
    leg_diameter_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak dış çapı (mm). Yalnız leg tipinde."
    )
    leg_thickness_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak et kalınlığı (mm). Yalnız leg tipinde."
    )
    leg_pad_length_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak-gövde bağlantı pedi boyu (mm); yalnız leg tipinde."
    )
    leg_pad_width_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak-gövde bağlantı pedi eni (mm); yalnız leg tipinde."
    )
    leg_pad_thickness_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak-gövde bağlantı pedi kalınlığı (mm); yalnız leg tipinde."
    )
    support_radius_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Ayakların kap ekseninden dağılım yarıçapı (mm). Moment hesabı için.",
    )
    base_plate_area_mm2: Optional[float] = Field(
        default=None, gt=0, description="Ayak taban plakası alanı (mm²)."
    )
    anchor_bolt_count: Optional[int] = Field(
        default=None, gt=0, description="Ankraj cıvatası adedi. Uplift kontrolü için."
    )
    anchor_bolt_diameter_mm: Optional[float] = Field(
        default=None, gt=0, description="Ankraj cıvatası nominal çapı (mm)."
    )
    anchor_tension_allowable_N: Optional[float] = Field(
        default=None, gt=0, description="Bir ankraj cıvatası için izin verilen çekme (N)."
    )
    anchor_shear_allowable_N: Optional[float] = Field(
        default=None, gt=0, description="Bir ankraj cıvatası için izin verilen kesme (N)."
    )
    leg_attachment: Optional[str] = Field(
        default=None, pattern="^(shell|bottom_head)$",
        description="Ayak bağlantı yeri: shell (gövde çevresi + ped) | bottom_head (alt bombe altı). "
                    "WRC 107 lokal gerilme yalnız shell için hesaplanır. Yalnız leg tipinde.",
    )
    leg_section_type: Optional[str] = Field(
        default=None, pattern="^(pipe|channel|box|angle)$",
        description="Ayak kesit tipi. None = eski davranış (boru: leg_diameter_mm/leg_thickness_mm, "
                    "yalnız leg_stress). Dolu ise ayak kesit/kaynak/taban plakası/WRC "
                    "alt kontrolleri de çalışır. Yalnız leg tipinde.",
    )
    leg_profile_height_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Profil yüksekliği h (U: h, kutu: H, köşebent: düşey kol a) (mm). K6: katalog gömülü değil.",
    )
    leg_profile_width_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Profil genişliği b (U: flanş genişliği, kutu: B, köşebent: yatay kol b) (mm).",
    )
    leg_web_thickness_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Gövde kalınlığı s (U); kutuda et kalınlığı t; köşebentte kol kalınlığı t (mm).",
    )
    leg_flange_thickness_mm: Optional[float] = Field(
        default=None, gt=0, description="Flanş kalınlığı t (yalnız U profil) (mm).",
    )
    leg_unbraced_length_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Burkulma boyu L (mm). Boşsa destek yüksekliği (height_mm) kullanılır ve sonuca yazılır.",
    )
    leg_eccentricity_mm: Optional[float] = Field(
        default=None, ge=0,
        description="Gövde dış yüzünden ayak ağırlık merkezine mesafe e (mm) = moment kolu.",
    )
    leg_effective_length_factor_K: Optional[float] = Field(
        default=None, gt=0,
        description="Etkin boy katsayısı K. Boşsa 2,1 (serbest uçlu konsol, AISC) varsayılır ve sonuca yazılır.",
    )
    leg_pad_contact_ratio: Optional[float] = Field(
        default=None, gt=0, le=1,
        description="Profilin pede kaynaklı/temaslı kontur oranı (0-1). Ayak->ped kaynak grubunun "
                    "boyu bu oranla ölçeklenir. Boşsa 1,0 (tam kontur) varsayılır.",
    )
    base_plate_length_mm: Optional[float] = Field(
        default=None, gt=0, description="Taban plakası boyu L (profil yüksekliği yönünde) (mm)."
    )
    base_plate_width_mm: Optional[float] = Field(
        default=None, gt=0, description="Taban plakası eni W (mm)."
    )
    base_plate_thickness_mm: Optional[float] = Field(
        default=None, gt=0, description="Taban plakası kalınlığı (mm)."
    )
    base_plate_yield_MPa: Optional[float] = Field(
        default=None, gt=0, description="Taban plakası akma dayanımı Fy (MPa)."
    )
    foundation_bearing_allowable_MPa: Optional[float] = Field(
        default=None, gt=0,
        description="Temel/beton izin verilen yataklık basıncı (MPa). Kullanıcı girdisi; boşsa kontrol edilmez.",
    )
    pad_to_shell_weld_leg_mm: Optional[float] = Field(
        default=None, gt=0, description="Ped->gövde köşe kaynağı bacağı z (mm)."
    )
    leg_to_pad_weld_leg_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak->ped köşe kaynağı bacağı z (mm)."
    )
    leg_to_base_plate_weld_leg_mm: Optional[float] = Field(
        default=None, gt=0, description="Ayak->taban plakası köşe kaynağı bacağı z (mm)."
    )
    weld_electrode_strength_MPa: Optional[float] = Field(
        default=None, gt=0, description="Elektrot dayanımı Fexx (MPa); boşsa kaynak kontrolü bloke."
    )
    weld_min_leg_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Asgari köşe kaynağı bacağı (mm), kullanıcı girdisi (AWS D1.1 tablosu K6 gereği gömülü değil).",
    )
    wrc_coefficients: Optional[dict[str, dict[str, WrcCoefficientEntry]]] = Field(
        default=None,
        description="WRC 107/537 katsayıları: nokta (A/B/C/D) -> yük (P/ML/MC/VL/VC) -> {Nx,Ny,Mx,My}. "
                    "Lisanslı bültenden okunur (K6); boşsa/eksikse wrc_local_stress BLOCKED_CODE_DATA.",
    )
    lateral_load_N: float = Field(
        default=0.0, ge=0,
        description="Destek tabanına aktarılan yatay kuvvet (N); ankraj kesme kontrolü için.",
    )
    overturning_moment_Nmm: float = Field(
        default=0.0, ge=0,
        description="Devirme momenti (N·mm) — rüzgâr/deprem. Yalnız skirt ve leg. "
                    "0 = moment yok; bu varsayım sonuca yazılır.",
    )

    @model_validator(mode="after")
    def _check_wrc_keys(self) -> "Support":
        if self.wrc_coefficients:
            for pt, loads in self.wrc_coefficients.items():
                if pt not in _WRC_POINTS:
                    raise ValueError(f"wrc_coefficients nokta anahtarı A/B/C/D olmalı: {pt!r}")
                for ld in loads:
                    if ld not in _WRC_LOADS:
                        raise ValueError(
                            f"wrc_coefficients yük anahtarı {'/'.join(_WRC_LOADS)} olmalı: {ld!r}"
                        )
        return self

    @model_validator(mode="after")
    def _check_skirt_wall_physical(self) -> "Support":
        # Etek et kalınlığı çap/2'ye ulaşırsa halka kesit dolu diske dejenere olur
        # (iç çap <= 0); fiziksel olarak imkânsız girdi.
        if (
            self.type == "skirt"
            and self.diameter_mm is not None
            and self.thickness_mm is not None
            and self.thickness_mm >= self.diameter_mm / 2.0
        ):
            raise ValueError(
                "Etek et kalınlığı çapın yarısından küçük olmalı (thickness_mm < diameter_mm/2)."
            )
        return self


__all__ = ["ShellSection", "Head", "Nozzle", "Cone", "Junction", "Flange", "Support", "WrcCoefficientEntry"]
