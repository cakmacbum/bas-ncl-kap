"""Proje modeli — VesselProject.

Bu, basınçlı kap tasarımının ana veri konteynerıdır.
Tüm hesaplar bu nesneyi girdi alır.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from domain.conditions import DesignConditions
from domain.enums import CalculationCode, Orientation
from domain.geometry import Cone, Head, Nozzle, ShellSection, Support
from domain.load_cases import LoadCase, LoadCombination
from domain.materials import MaterialProperty
from domain.welds import WeldJoint


class FluidInfo(BaseModel):
    """Akışkan bilgisi."""

    name: str = Field(..., description="Akışkan adı.")
    phase: str = Field(
        default="gas",
        description="Akışkan fazı: gas, liquid, steam.",
    )
    group: str = Field(
        default="Group 2",
        description="Akışkan grubu (PED: Group 1 veya Group 2).",
    )
    hazard_classes: List[str] = Field(
        default_factory=list,
        description="CLP tehlike sınıfları (PED sınıflandırması için).",
    )


class VesselProject(BaseModel):
    """Basınçlı kap projesi — ana veri modeli.

    K7 kuralı: Standarttan bağımsız; ASME/EN kuralları code plugin'lerinde uygulanır.
    """

    # ── Proje bilgileri ───────────────────────────────────────────────────────
    project_number: str = Field(..., description="Proje numarası.")
    project_name: str = Field(..., description="Proje adı.")
    customer: str = Field(default="", description="Müşteri.")
    revision: str = Field(default="A", description="Revizyon.")
    calculation_code: CalculationCode = Field(
        ..., description="Hesap standardı (ASME VIII-1 veya EN 13445)."
    )
    code_edition: str = Field(
        ..., description="Standart sürümü (ör. '2025', '2021+A1:2023')."
    )
    unit_system: str = Field(
        default="SI", description="Birim sistemi (SI, Imperial)."
    )

    # ── Tasarım ömrü ──────────────────────────────────────────────────────────
    design_life: Optional[int] = Field(
        default=None, ge=0, description="Tasarım ömrü (yıl)."
    )
    design_cycles: Optional[int] = Field(
        default=None, ge=0, description="Tasarım çevrim sayısı."
    )
    orientation: Orientation = Field(
        default=Orientation.VERTICAL, description="Kap yönü."
    )

    # ── Koşullar ──────────────────────────────────────────────────────────────
    design_conditions: DesignConditions = Field(
        ..., description="Tasarım koşulları."
    )

    # ── Akışkan ───────────────────────────────────────────────────────────────
    fluid: Optional[FluidInfo] = Field(
        default=None, description="Akışkan bilgisi."
    )

    # ── Bileşenler ────────────────────────────────────────────────────────────
    shell_sections: List[ShellSection] = Field(
        default_factory=list, description="Gövde kesitleri."
    )
    heads: List[Head] = Field(
        default_factory=list, description="Bombeler."
    )
    cones: List[Cone] = Field(
        default_factory=list, description="Konik bölümler / reducer."
    )
    nozzles: List[Nozzle] = Field(
        default_factory=list, description="Nozullar."
    )
    supports: List[Support] = Field(
        default_factory=list,
        description="Kap destekleri (eyer/etek/ayak). Boşsa destek kontrolü yapılmaz.",
    )
    welds: List[WeldJoint] = Field(
        default_factory=list, description="Kaynak dikişleri."
    )

    # ── Malzeme ───────────────────────────────────────────────────────────────
    materials: List[MaterialProperty] = Field(
        default_factory=list, description="Malzeme özellikleri."
    )

    # ── Yük durumları ────────────────────────────────────────────────────────
    load_cases: List[LoadCase] = Field(
        default_factory=list, description="Yük durumları."
    )
    load_combinations: List[LoadCombination] = Field(
        default_factory=list, description="Yük kombinasyonları."
    )

    # ── Metadata ──────────────────────────────────────────────────────────────
    input_file_hash: Optional[str] = Field(
        default=None, description="Girdi dosyası hash'i (JSON kaydetme sırasında üretilir)."
    )

    def get_material(self, material_id: str) -> Optional[MaterialProperty]:
        """ID ile malzeme getir."""
        for mat in self.materials:
            if mat.material_id == material_id:
                return mat
        return None

    def get_weld(self, weld_joint_id: str) -> Optional[WeldJoint]:
        """ID ile kaynak dikişi getir."""
        for w in self.welds:
            if w.joint_id == weld_joint_id:
                return w
        return None


__all__ = ["VesselProject", "FluidInfo"]
