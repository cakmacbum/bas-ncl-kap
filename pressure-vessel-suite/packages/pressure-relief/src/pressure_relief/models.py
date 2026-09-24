from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PressureReliefDevice(BaseModel):
    """A single safety valve or rupture disk in the protected system."""

    device_id: str = Field(..., min_length=1)
    device_type: Literal["safety_valve", "rupture_disk"]
    protected_component_id: Optional[str] = None
    set_pressure_mpa: Optional[float] = Field(default=None, gt=0)
    burst_pressure_mpa: Optional[float] = Field(default=None, gt=0)
    accumulation_percent: Optional[float] = Field(default=None, ge=0, le=100)
    blowdown_percent: Optional[float] = Field(default=None, ge=0, le=100)
    certified_capacity_kg_s: Optional[float] = Field(default=None, gt=0)
    fluid_orifice_area_mm2: Optional[float] = Field(default=None, gt=0)
    certification_reference: Optional[str] = None

    @property
    def relieving_pressure_mpa(self) -> Optional[float]:
        return self.set_pressure_mpa or self.burst_pressure_mpa


class PressureReliefSystem(BaseModel):
    """Project-level relief design basis."""

    enabled: bool = False
    protected_mawp_mpa: Optional[float] = Field(default=None, gt=0)
    accumulation_limit_percent: float = Field(default=10.0, gt=0, le=100)
    devices: list[PressureReliefDevice] = Field(default_factory=list)
    notes: str = ""
