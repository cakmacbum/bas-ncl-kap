"""Kaldırma kulağı (lifting lug) girdi modeli — P06.

Tüm değerler kullanıcıdan gelir (K4: uydurma varsayılan yok). Birimler: mm, MPa, derece, kg.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class LiftingLugSpec(BaseModel):
    """Kaldırma kulağı seti: aynı geometrili `lug_count` adet kulak."""

    lug_count: int = Field(..., ge=1, le=4, description="Kulak sayısı (1-4).")
    location: Literal["shell_top", "head"] = Field(
        ..., description="Konum: gövde üstü (shell_top) veya bombe (head)."
    )
    host_component_id: Optional[str] = Field(
        default=None, description="Kulağın kaynaklandığı bileşen ID'si (boşsa ilk uygun bileşen)."
    )
    plate_thickness_mm: float = Field(..., gt=0, description="Kulak plakası kalınlığı t (mm).")
    plate_width_mm: float = Field(..., gt=0, description="Delik hizasında plaka toplam genişliği b (mm).")
    hole_diameter_mm: float = Field(..., gt=0, description="Pim deliği çapı (mm).")
    pin_diameter_mm: Optional[float] = Field(
        default=None, gt=0, description="Şakle/pim çapı (mm); boşsa delik çapı alınır (varsayım sonuca yazılır)."
    )
    edge_distance_mm: float = Field(
        ..., gt=0, description="Delik merkezinden plaka üst kenarına mesafe e (mm)."
    )
    hole_height_mm: float = Field(
        ..., gt=0, description="Delik merkezinin kabuk yüzeyinden yüksekliği h (mm)."
    )
    base_width_mm: float = Field(..., gt=0, description="Kulak tabanı (kaynaklı kenar) genişliği (mm).")
    weld_length_mm: float = Field(..., gt=0, description="Kulak başına toplam kaynak boyu (mm).")
    weld_leg_mm: float = Field(..., gt=0, description="Köşe kaynak ayak ölçüsü (mm).")
    lift_angle_deg: float = Field(
        ..., ge=0, lt=90, description="Sapan açısı, düşeyden (0 = düşey sapan)."
    )
    impact_factor: float = Field(
        ..., ge=1.0, description="Darbe/dinamik katsayısı (tipik 1,5-2,0; kullanıcı seçer)."
    )
    yield_strength_MPa: float = Field(..., gt=0, description="Kulak plakası akma dayanımı Fy (MPa).")
    weld_electrode_Fu_MPa: Optional[float] = Field(
        default=None, gt=0, description="Elektrot çekme dayanımı FEXX (MPa); boşsa 482 (E70) varsayılır."
    )
    extra_mass_kg: float = Field(
        default=0.0, ge=0, description="Kap metal kütlesine ek kaldırılan kütle (izolasyon, iç parçalar...)."
    )

    @model_validator(mode="after")
    def _geometry(self) -> "LiftingLugSpec":
        if self.hole_diameter_mm >= self.plate_width_mm:
            raise ValueError("hole_diameter_mm, plate_width_mm değerinden küçük olmalı")
        if self.edge_distance_mm <= self.hole_diameter_mm / 2:
            raise ValueError("edge_distance_mm, delik yarıçapından büyük olmalı")
        return self


__all__ = ["LiftingLugSpec"]
