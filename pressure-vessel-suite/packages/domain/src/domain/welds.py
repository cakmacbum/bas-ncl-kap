"""Kaynak modeli — WeldJoint (iskelet, kaynak §9).

V1'de temel alanlar kullanılır; ileride WPS/PQR/kaynakçı detayları eklenir.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class WeldJoint(BaseModel):
    """Kaynak dikişi tanımı (kaynak §9)."""

    joint_id: str = Field(..., description="Kaynak dikişi ID'si (ör. 'WJ-01').")
    joint_type: str = Field(
        ...,
        description="Dikiş tipi (ör. 'longitudinal', 'circumferential', 'nozzle_to_shell').",
    )
    connected_components: List[str] = Field(
        default_factory=list,
        description="Bağlı bileşen ID'leri (ShellSection, Head, Nozzle).",
    )
    weld_category: Optional[str] = Field(
        default=None,
        description="Kaynak kategorisi (ASME: A, B, C, D).",
    )
    weld_process: Optional[str] = Field(
        default=None,
        description="Kaynak proses (ör. 'SMAW', 'GTAW', 'SAW').",
    )
    full_penetration: bool = Field(
        default=True, description="Tam nüfuziyetli mi?"
    )
    joint_efficiency: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Kaynak verimi / Joint Efficiency (E). ASME: 0.7–1.0.",
    )
    joint_coefficient: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Birimleştirme katsayısı / Joint Coefficient (z). EN 13445.",
    )
    nde_method: Optional[str] = Field(
        default=None,
        description="NDE muayene yöntemi (ör. 'RT-1', 'RT-2', 'UT', 'VT').",
    )
    nde_extent: Optional[str] = Field(
        default=None,
        description="NDE kapsamı (ör. '100%', 'spot', 'none').",
    )
    wps_number: Optional[str] = Field(
        default=None, description="WPS numarası."
    )
    pqr_number: Optional[str] = Field(
        default=None, description="PQR numarası."
    )
    welder_qualification: Optional[str] = Field(
        default=None, description="Kaynakçı yeterlilik referansı."
    )
    pwht_required: Optional[bool] = Field(
        default=None,
        description="PWHT (Post Weld Heat Treatment) gerekli mi?",
    )
    pwht_procedure: Optional[str] = Field(
        default=None, description="PWHT prosedür referansı."
    )


__all__ = ["WeldJoint"]
