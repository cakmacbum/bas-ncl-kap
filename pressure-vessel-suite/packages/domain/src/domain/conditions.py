"""Tasarım koşulları — DesignConditions modeli.

K4 kuralı: Çalışma basıncı ≠ Tasarım basıncı ≠ PS (ayrı alanlar).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DesignConditions(BaseModel):
    """Tasarım koşulları (kaynak §6).

    Çalışma basıncı (operating), tasarım basıncı (design) ve azami izin verilen
    basınç (PS / MAWP_ps) ayrı ayrı tutulur. Program bunları birbirine eşit varsaymaz.
    """

    # ── Basınç ────────────────────────────────────────────────────────────────
    operating_pressure: float = Field(
        ..., gt=0, description="Çalışma basıncı (MPa). Ekipmanın normal çalışma sırasındaki basınç."
    )
    design_pressure: float = Field(
        ..., gt=0,
        description="Tasarım basıncı (MPa). Hesapların dayandığı basınç. "
                    "Çalışma basıncından yüksek olabilir.",
    )
    maximum_allowable_pressure_ps: float = Field(
        ..., gt=0,
        description="Azami izin verilen basınç / PS (MPa). PED ve isim plakası için kullanılan değer.",
    )

    # ── Sıcaklık ──────────────────────────────────────────────────────────────
    operating_temperature: float = Field(
        ..., description="Çalışma sıcaklığı (°C)."
    )
    design_temperature: float = Field(
        ..., description="Tasarım sıcaklığı (°C). Malzeme gerilmesi bu sıcaklıkta değerlendirilir."
    )
    minimum_design_temperature: float = Field(
        ..., description="Asgari tasarım sıcaklığı (°C). Tokluk kontrolü için."
    )

    # ── Dış basınç / vakum ────────────────────────────────────────────────────
    external_pressure: float = Field(
        default=0.0, ge=0,
        description="Dış basınç (MPa). UG-28/UG-33 kontrolü çalışır; gövde/bombe için "
                    "UG-28 A/B çizelge faktörleri girilmemişse BLOCKED_CODE_DATA döner (K6).",
    )
    vacuum_condition: bool = Field(
        default=False,
        description="Vakum koşulu var mı? UG-28 kontrolü çalışır; aynı K6 gerekçesiyle "
                    "A/B faktörleri girilmemişse BLOCKED_CODE_DATA döner.",
    )

    # ── Test ──────────────────────────────────────────────────────────────────
    hydrotest_temperature: float = Field(
        default=20.0,
        description="Hidrostatik test sıcaklığı (°C). Varsayılan: 20°C.",
    )

    # ── Korozyon ──────────────────────────────────────────────────────────────
    corrosion_allowance_internal: float = Field(
        default=0.0, ge=0,
        description="İç korozyon payı (mm).",
    )
    corrosion_allowance_external: float = Field(
        default=0.0, ge=0,
        description="Dış korozyon payı (mm). V1'de genellikle 0.",
    )

    # ── Statik kafa ──────────────────────────────────────────────────────────
    fluid_density_kg_m3: float = Field(
        default=0.0, ge=0,
        description="Akışkan yoğunluğu (kg/m³). Statik kafa düzeltmesi için. 0 = düzelleme yok.",
    )

    # ── Darbe testi ────────────────────────────────────────────────────────
    impact_test_temperature_C: Optional[float] = Field(
        default=None,
        description="Darbe (Charpy) testinin yapıldığı sıcaklık (°C). Girilirse "
                    "UCS-66 muafiyet değerlendirmesinde kullanılır. Boş = test yok.",
    )

    model_config = {"frozen": True}
