"""Malzeme modeli — MaterialProperty (iskelet, kaynak §12).

V1'de kullanıcı allowable/yield/tensile değerlerini manuel girer (K4).

Faz 2 (FEA doğrulama laboratuvarı): elastic_modulus / poisson_ratio opsiyonel
alanları eklendi. Bu değerler yalnızca FEA lab'ının lineer-elastik malzeme
modeli için kullanılır; kapalı-form ASME/EN hesaplarının hiçbiri bu alanlara
dokunmaz (K1 — mühendislik formülleri code-* paketlerinde, burada değil).
Boş bırakılırsa FEA lab BLOCKED_CODE_DATA ile durur; varsayılan ATANMAZ (K4).
"""

from __future__ import annotations

from typing import Literal, Optional, List

from pydantic import BaseModel, Field

from domain.enums import ProductForm


class MaterialProperty(BaseModel):
    """Malzeme özellikleri (kaynak §12).

    Standart sürümü + ürün formu + kalınlık + sıcaklık + ısıl işlem +
    kaynaklı/kaynaksız duruma göre izin verilen gerilme değişebilir.
    """

    material_id: str = Field(..., description="Malzeme tanım ID'si (proje içinde benzersiz).")
    standard_pack: str = Field(
        ..., description="Standart paketi tanımı (ör. 'ASME II-D 2025', 'EN 10028-3:2017')."
    )
    material_designation: str = Field(
        ..., description="Malzeme adı (ör. 'SA-516 Gr.70', 'P355NH')."
    )
    product_form: ProductForm = Field(
        ..., description="Ürün formu (plate, forging, seamless_pipe vb.)."
    )
    thickness_min: float = Field(
        default=0.0, ge=0, description="Minimum kalınlık (mm)."
    )
    thickness_max: float = Field(
        default=999.0, gt=0, description="Maksimum kalınlık (mm)."
    )
    temperature: float = Field(
        ..., description="Verilerin geçerli olduğu sıcaklık (°C)."
    )
    allowable_stress: float = Field(
        ..., gt=0, description="İzin verilen gerilme (MPa)."
    )
    allowable_stress_test_temp: Optional[float] = Field(
        default=None, gt=0,
        description=(
            "Test sıcaklığındaki izin verilen gerilme (MPa). UG-99(b)/UG-100 LSR = "
            "S_test/S_design oranı için gerekir; girilmezse ve tasarım/test sıcaklığı "
            "farklıysa test basıncı sonucu REVIEW_REQUIRED olur (K4)."
        ),
    )
    yield_strength: float = Field(
        ..., gt=0, description="Akma dayanımı (MPa)."
    )
    tensile_strength: float = Field(
        ..., gt=0, description="Çekme dayanımı (MPa)."
    )
    source_reference: str = Field(
        ..., description="Kaynak doküman referansı (ör. 'ASME II-D Table 1A, Line 4')."
    )
    source_revision: str = Field(
        default="", description="Kaynak sürümü."
    )
    density: float = Field(
        default=7850.0, gt=0,
        description="Yoğunluk (kg/m³). Karbon çeliği varsayılan: 7850.",
    )
    notes: Optional[str] = Field(
        default=None, description="Ek notlar."
    )

    # ── MDMT / UCS-66 ─────────────────────────────────────────────────────────
    # UCS-66 eğri grubu malzemeye bağlıdır (Şekil UCS-66'da A/B/C/D eğrileri).
    # K3/K6: eğri ataması standart tablosundan gelir, buraya gömülmez —
    # kullanıcı malzeme belgesine bakıp girer. Girilmezse MDMT kontrolü
    # BLOCKED_MISSING_INPUT verir, tahmin edilmez (K4).
    ucs66_curve_group: Optional[str] = Field(
        default=None,
        pattern="^[ABCD]$",
        description="UCS-66 eğri grubu (A/B/C/D). Malzeme belgesinden girilir; "
                    "girilmezse MDMT kontrolü bloke olur, varsayılan atanmaz.",
    )

    # ── E04: EN 13445-3 Madde 6 — nominal tasarım gerilmesi girdileri ─────────
    # Hepsi opsiyonel; kullanıcı malzeme sertifikası / EN 10028 vb. tablodan girer
    # (K3/K6: tablo gömülmez). Grup girilmezse EN f üst sınırı kontrolü
    # BLOCKED_MISSING_INPUT olur; elle girilen allowable_stress yine kullanılır (K4).
    en_material_group: Optional[Literal["ferritic", "austenitic_a30", "austenitic_a35", "cast"]] = Field(
        default=None,
        description="EN 13445-3 Madde 6 malzeme grubu: ferritic (östenitik dışı haddelenmiş çelik), "
                    "austenitic_a30 (A ≥ %30), austenitic_a35 (A ≥ %35), cast (döküm çelik).",
    )
    en_elongation_a_pct: Optional[float] = Field(
        default=None, gt=0, lt=100, description="Kopma uzaması A (%) — östenitik alt grubu doğrulamak için."
    )
    en_rp02_t: Optional[float] = Field(default=None, gt=0, description="Rp0,2/T tasarım sıcaklığında (MPa).")
    en_rp10_t: Optional[float] = Field(default=None, gt=0, description="Rp1,0/T tasarım sıcaklığında (MPa).")
    en_rm_20: Optional[float] = Field(default=None, gt=0, description="Rm/20 oda sıcaklığında min. çekme (MPa).")
    en_rm_t: Optional[float] = Field(default=None, gt=0, description="Rm/T tasarım sıcaklığında (MPa).")
    en_rp02_test: Optional[float] = Field(default=None, gt=0, description="Rp0,2 test sıcaklığında (MPa).")
    en_rp10_test: Optional[float] = Field(default=None, gt=0, description="Rp1,0 test sıcaklığında (MPa).")
    en_rm_test: Optional[float] = Field(default=None, gt=0, description="Rm test sıcaklığında (MPa).")

    # ── Faz 2: FEA doğrulama laboratuvarı — lineer-elastik özellikler ─────────
    # Opsiyonel; kullanıcı girer, tablo gömülmez (K3/K6). Yalnızca FEA lab
    # tüketir — kapalı-form ASME/EN hesap motorları bu alanları OKUMAZ.
    elastic_modulus: Optional[float] = Field(
        default=None, gt=0,
        description="Elastisite modülü E (MPa), tasarım sıcaklığında. Yalnızca "
                    "FEA doğrulama laboratuvarı için; boşsa lab BLOCKED_CODE_DATA "
                    "döner (varsayım atanmaz, K4).",
    )
    poisson_ratio: Optional[float] = Field(
        default=None, gt=0, lt=0.5,
        description="Poisson oranı ν (birimsiz, 0 < ν < 0.5). Yalnızca FEA "
                    "doğrulama laboratuvarı için; boşsa lab BLOCKED_CODE_DATA "
                    "döner (varsayım atanmaz, K4).",
    )

    # Faz B: lisanslı veri paketinden alınan sıcaklık eğrileri. Ekstrapolasyon
    # yapılmaz; aralık dışı bir sıcaklık hesaplamayı bloke eder.
    allowable_stress_temperature_points: List[tuple[float, float]] = Field(default_factory=list)
    yield_temperature_points: List[tuple[float, float]] = Field(default_factory=list)
    elastic_modulus_temperature_points: List[tuple[float, float]] = Field(default_factory=list)
    pwht_required: Optional[bool] = Field(default=None)
    impact_test_required: Optional[bool] = Field(default=None)
    weld_restrictions: List[str] = Field(default_factory=list)
    data_checksum: str = Field(default="", description="İçe aktarılan kayıt checksum'ı.")

    model_config = {"frozen": True}


__all__ = ["MaterialProperty"]
