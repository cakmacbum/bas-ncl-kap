"""P08 girdileri — koni birleşimi (App. 1-5) ek girdileri ve etek taban halkası/ankraj.

`VesselProject.cone_base` tek opsiyonel alanı bu konteyneri taşır. Tüm değerler
KULLANICI girdisidir; çizelge/eğri değerleri koda gömülmez (K6), boş bırakılanlar
varsayılana düşerse sonuca varsayım olarak yazılır (K4).
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class ConeJunctionDesign(BaseModel):
    """Bir koni birleşiminin (Junction) App. 1-5 ek girdileri."""

    junction_id: str = Field(..., description="İlgili Junction.junction_id.")
    delta_deg: Optional[float] = Field(
        default=None, ge=0, le=60,
        description="App. 1-5 Table 1-5.2 Δ (derece); lisanslı çizelgeden OKUNUR (K6, "
                    "koda gömülmez). Boşsa Δ=0 (güvenli taraf) alınır ve sonuca yazılır.",
    )
    extra_ring_area_mm2: float = Field(
        default=0.0, ge=0,
        description="Birleşimde ayrıca eklenen takviye halkası kesit alanı (mm²).",
    )


class SkirtBaseRingInput(BaseModel):
    """Etek taban halkası + ankraj + beton yataklık girdileri (Moss PVDM 3-9 / Jawad-Farr)."""

    support_id: Optional[str] = Field(
        default=None, description="İlgili skirt Support kimliği; boşsa tek skirt'e uygulanır."
    )
    ring_outer_diameter_mm: float = Field(..., gt=0)
    ring_inner_diameter_mm: float = Field(..., gt=0)
    ring_thickness_mm: float = Field(..., gt=0)
    ring_yield_MPa: float = Field(..., gt=0, description="Halka akma dayanımı Fy (MPa).")
    ring_allowable_bending_MPa: Optional[float] = Field(
        default=None, gt=0,
        description="Halka izin verilen eğilme gerilmesi. Boşsa 0,66·Fy VARSAYILIR (K4).",
    )
    bolt_circle_diameter_mm: float = Field(..., gt=0)
    bolt_count: int = Field(..., gt=0)
    bolt_diameter_mm: float = Field(..., gt=0, description="Cıvata nominal çapı (mm).")
    bolt_stress_area_mm2: Optional[float] = Field(
        default=None, gt=0,
        description="Cıvata çekme gerilme alanı (mm²). Boşsa 0,75·(π/4·d²) VARSAYILIR (K4).",
    )
    bolt_corrosion_allowance_mm: float = Field(default=0.0, ge=0)
    bolt_allowable_tension_MPa: Optional[float] = Field(
        default=None, gt=0, description="Cıvata izin verilen çekme gerilmesi (K6: kullanıcı girer)."
    )
    bolt_allowable_shear_MPa: Optional[float] = Field(
        default=None, gt=0, description="Cıvata izin verilen kesme gerilmesi (K6)."
    )
    concrete_fc_MPa: float = Field(..., gt=0, description="Beton karakteristik basınç dayanımı f'c.")
    concrete_allowable_bearing_MPa: Optional[float] = Field(
        default=None, gt=0,
        description="Beton izin verilen yataklık basıncı. Boşsa 0,85·f'c/2,31 (AISC 360 J8 ASD) VARSAYILIR (K4).",
    )
    modular_ratio_n: Optional[float] = Field(
        default=None, gt=0,
        description="n = Es/Ec. Boşsa Ec=4700·√f'c (ACI 318), Es=200000 MPa ile hesaplanır (K4).",
    )

    @model_validator(mode="after")
    def _check(self) -> "SkirtBaseRingInput":
        if self.ring_inner_diameter_mm >= self.ring_outer_diameter_mm:
            raise ValueError("ring_inner_diameter_mm < ring_outer_diameter_mm olmalı.")
        return self


class ConeBaseInputs(BaseModel):
    """P08 girdi konteyneri."""

    junctions: List[ConeJunctionDesign] = Field(default_factory=list)
    skirt_base_ring: Optional[SkirtBaseRingInput] = None


__all__ = ["ConeJunctionDesign", "SkirtBaseRingInput", "ConeBaseInputs"]
