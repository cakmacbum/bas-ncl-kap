"""Malzeme modeli — MaterialProperty (iskelet, kaynak §12).

V1'de kullanıcı allowable/yield/tensile değerlerini manuel girer (K4).
"""

from __future__ import annotations

from typing import Optional

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

    model_config = {"frozen": True}


__all__ = ["MaterialProperty"]
