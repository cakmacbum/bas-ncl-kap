"""PED sınıflandırma modelleri.

PED 2014/68/EU Ek II sınıflandırması için girdi ve çıktı modelleri.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from ped_2014_68_eu.enums import (
    ConformityModule,
    EquipmentType,
    FluidGroupPED,
    FluidPhasePED,
    GHSClassification,
    HeatedStatus,
    NotifyBodyRequired,
    PEDCategory,
    PEDClassificationTable,
)


class FluidClassification(BaseModel):
    """Tek bir akışkanın PED sınıflandırması.

    CLP/GHS sınıflandırmasına göre akışkan grubu belirlenir.
    Birden fazla akışkan varsa en yüksek kategoriyi oluşturan esas alınır.
    """

    fluid_name: str = Field(..., description="Akışkan adı.")
    phase: FluidPhasePED = Field(..., description="Akışkan fazı (gaz/sıvı).")
    ghs_classifications: List[GHSClassification] = Field(
        default_factory=list,
        description="CLP/GHS tehlike sınıfları.",
    )
    fluid_group: FluidGroupPED = Field(
        default=FluidGroupPED.UNCLASSIFIED,
        description="PED akışkan grubu (CLP sınıflandırmasından otomatik belirlenir).",
    )
    is_group1: bool = Field(
        default=False,
        description="Grup 1 akışkan mı? (CLP sınıflandırmasına göre).",
    )

    @model_validator(mode="after")
    def _determine_group(self) -> "FluidClassification":
        """CLP sınıflandırmasına göre akışkan grubunu belirle."""
        if self.fluid_group != FluidGroupPED.UNCLASSIFIED:
            return self

        # Grup 1 sınıflandırmaları
        group1_classes = {
            GHSClassification.EXPLOSIVE,
            GHSClassification.OXIDIZING,
            GHSClassification.FLAMMABLE_GAS,
            GHSClassification.FLAMMABLE_LIQUID,
            GHSClassification.FLAMMABLE_SOLID,
            GHSClassification.PYROPHORIC,
            GHSClassification.SELF_REACTIVE,
            GHSClassification.ORGANIC_PEROXIDE,
            GHSClassification.TOXIC,
            GHSClassification.VERY_TOXIC,
            GHSClassification.CORROSIVE,
        }

        if any(c in group1_classes for c in self.ghs_classifications):
            self.fluid_group = FluidGroupPED.GROUP_1
            self.is_group1 = True
        else:
            self.fluid_group = FluidGroupPED.GROUP_2
            self.is_group1 = False

        return self


class ClassificationInput(BaseModel):
    """PED sınıflandırma girdileri.

    PED 2014/68/EU Ek II'ye göre sınıflandırma için gerekli tüm parametreler.
    """

    # ── Ekipman bilgileri ─────────────────────────────────────────────────────
    equipment_type: EquipmentType = Field(
        ..., description="Ekipman türü (kap, boru, aksesuar)."
    )
    is_assembly: bool = Field(
        default=False,
        description="Assembly (montaj) mi? Birden fazla parçanın birleşimi.",
    )
    is_fired: bool = Field(
        default=False,
        description="Ateşlemeli mi? (ör. buhar kazanı).",
    )
    heated_status: HeatedStatus = Field(
        default=HeatedStatus.NOT_HEATED,
        description="Isıtma durumu.",
    )

    # ── Basınç ve hacim ──────────────────────────────────────────────────────
    ps_mpa: float = Field(
        ..., gt=0,
        description="Azami izin verilen basınç / PS (MPa).",
    )
    volume_liters: float = Field(
        ..., gt=0,
        description="Hacim (litre).",
    )
    dn_mm: Optional[float] = Field(
        default=None, gt=0,
        description="Nominal çap / DN (mm). Boru ve aksesuarlar için.",
    )

    # ── Sıcaklık ──────────────────────────────────────────────────────────────
    ts_min_c: float = Field(
        ..., description="Asgari çalışma sıcaklığı (°C).",
    )
    ts_max_c: float = Field(
        ..., description="Azami çalışma sıcaklığı (°C).",
    )

    # ── Akışkan bilgileri ─────────────────────────────────────────────────────
    fluids: List[FluidClassification] = Field(
        ..., min_length=1,
        description="Akışkan listesi. Birden fazlaysa en yüksek kategoriyi oluşturan esas.",
    )

    # ── Grup 1/2 doğrudan belirleme (opsiyonel) ──────────────────────────────
    explicit_fluid_group: Optional[FluidGroupPED] = Field(
        default=None,
        description="Akışkan grubu doğrudan belirtilmişse (CLP sınıflandırması yerine).",
    )

    @model_validator(mode="after")
    def _validate_fluids(self) -> "ClassificationInput":
        """Akışkan doğrulamaları."""
        if not self.fluids:
            raise ValueError("En az bir akışkan tanımlanmalı.")
        return self


class ClassificationResult(BaseModel):
    """PED sınıflandırma sonucu.

    PED 2014/68/EU Ek II sınıflandırmasının tüm çıktıları.
    """

    # ── Kapsam ────────────────────────────────────────────────────────────────
    in_scope: bool = Field(
        default=True,
        description="PED kapsamında mı?",
    )
    scope_reason: str = Field(
        default="",
        description="Kapsam dışı ise nedeni.",
    )

    # ── Ekipman bilgileri ─────────────────────────────────────────────────────
    equipment_type: EquipmentType = Field(
        ..., description="Ekipman türü.",
    )
    is_assembly: bool = Field(default=False, description="Assembly mi?")

    # ── Akışkan ───────────────────────────────────────────────────────────────
    fluid_group: FluidGroupPED = Field(
        ..., description="Belirlenen akışkan grubu."
    )
    fluid_phase: FluidPhasePED = Field(
        ..., description="Baskın akışkan fazı."
    )
    determining_fluid: str = Field(
        default="",
        description="Sınıflandırmayı belirleyen akışkan.",
    )

    # ── Sınıflandırma ─────────────────────────────────────────────────────────
    classification_table: PEDClassificationTable = Field(
        ..., description="Kullanılan sınıflandırma tablosu."
    )
    ps_mpa: float = Field(..., description="PS (MPa).")
    volume_liters: float = Field(..., description="Hacim (litre).")
    ps_x_v: float = Field(..., description="PS × V (MPa·litre).")
    category: PEDCategory = Field(..., description="PED kategorisi.")

    # ── Modül eşleştirmesi ────────────────────────────────────────────────────
    conformity_modules: List[ConformityModule] = Field(
        ..., description="Uygunluk modülleri."
    )
    module_description: str = Field(
        default="",
        description="Modül eşleştirmesi açıklaması.",
    )

    # ── Onaylanmış kuruluş ────────────────────────────────────────────────────
    notify_body_required: NotifyBodyRequired = Field(
        ..., description="Onaylanmış kuruluş gerekliliği."
    )

    # ── CE ─────────────────────────────────────────────────────────────────────
    ce_marking_applicable: bool = Field(
        ..., description="CE işaretleme uygulanabilir mi?"
    )

    # ── Ek bilgiler ───────────────────────────────────────────────────────────
    warnings: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    intermediate_values: List[Dict] = Field(default_factory=list)

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def add_assumption(self, assumption: str) -> None:
        self.assumptions.append(assumption)

    def add_intermediate(self, name: str, value, description: str = "") -> None:
        self.intermediate_values.append({
            "name": name,
            "value": value,
            "description": description,
        })


__all__ = ["ClassificationInput", "ClassificationResult", "FluidClassification"]
