"""BOM maliyet girdileri (P09) — tüm birim fiyatları kullanıcı girer (K4/K6).

Varsayılan fiyat YOKTUR; boş girdi = maliyet hesaplanmaz ve uyarı üretilir.
"""

from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field


class CostInputs(BaseModel):
    """Maliyet tahmini için kullanıcı birim fiyatları."""

    material_price_eur_per_kg: Dict[str, float] = Field(
        default_factory=dict,
        description="material_id -> €/kg. Girilmeyen malzeme için malzeme maliyeti hesaplanmaz.",
    )
    welding_hours: Optional[float] = Field(default=None, ge=0, description="Kaynak/işçilik süresi (saat).")
    labor_rate_eur_per_hour: Optional[float] = Field(default=None, ge=0, description="Saat ücreti (€/saat).")
    ndt_cost_eur: Optional[float] = Field(default=None, ge=0, description="NDT toplam bedeli (€).")
    paint_cost_eur: Optional[float] = Field(default=None, ge=0, description="Boya/kaplama toplam bedeli (€).")
