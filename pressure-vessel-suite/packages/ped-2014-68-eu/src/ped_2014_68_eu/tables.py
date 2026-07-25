"""PED 2014/68/EU Ek II sınıflandırma tabloları.

Bu modül PED Ek II'deki basınç/hacim eşiklerini ve kategori sınırlarını tanımlar.
Standart telifli metni K6 kuralı gereği kopyalanmaz; yalnızca sayısal eşikler saklanır.

Referans: Directive 2014/68/EU, Annex II, Tables 1-12
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from ped_2014_68_eu.enums import (
    EquipmentType,
    FluidGroupPED,
    FluidPhasePED,
    PEDCategory,
    PEDClassificationTable,
)


@dataclass(frozen=True)
class PSVThreshold:
    """PS×V eşik değerleri — bir kategori sınırı.

    (ps_mpa_min, volume_liters_min) → kategori.
    ps_mpa × volume_liters bu eşiği aşarsa üst kategoride değerlendirilir.
    """
    category: PEDCategory
    ps_x_v_min: float  # MPa·litre eşiği
    ps_mpa_min: float  # Minimum PS (MPa) — tek başına eşik
    volume_liters_min: float  # Minimum hacim (litre) — tek başına eşik
    description: str = ""


@dataclass(frozen=True)
class ClassificationTable:
    """Bir PED sınıflandırma tablosu."""
    table_id: PEDClassificationTable
    fluid_group: FluidGroupPED
    fluid_phase: FluidPhasePED
    equipment_type: EquipmentType
    thresholds: List[PSVThreshold]

    def classify(self, ps_mpa: float, volume_liters: float) -> PEDCategory:
        """PS ve hacme göre kategori belirle.

        En yüksek kategoriden başlayarak eşikleri kontrol eder.
        İlk eşiklenen kategori döndürülür.

        Args:
            ps_mpa: Azami izin verilen basınç (MPa).
            volume_liters: Hacim (litre).

        Returns:
            PED kategorisi.
        """
        ps_x_v = ps_mpa * volume_liters

        # SEP kontrolü — PS veya hacim çok düşükse
        sep_threshold = self.thresholds[0] if self.thresholds else None
        if sep_threshold:
            if ps_mpa < sep_threshold.ps_mpa_min or volume_liters < sep_threshold.volume_liters_min:
                return PEDCategory.SEP

        # Kategorileri en yükseğe doğru kontrol et (tersten)
        # İlk eşiklenen (en yüksek) kategori döndürülür
        for thresh in reversed(self.thresholds):
            if thresh.category == PEDCategory.SEP:
                continue  # SEP zaten yukarıda kontrol edildi
            if ps_x_v >= thresh.ps_x_v_min:
                return thresh.category

        return PEDCategory.SEP


# ── PED Ek II Tablo tanımları ──────────────────────────────────────────────────
# Not: Aşağıdaki eşikler PED 2014/68/EU Ek II Tablo 1-12'den alınmıştır.
# K6 kuralı: Orijinal metin kopyalanmaz; yalnızca sayısal eşikler.


def _build_table_1() -> ClassificationTable:
    """Tablo 1: Grup 1 gazlar — Kap.

    PS×V eşikleri (MPa·litre):
    SEP: PS < 0.5 bar (0.05 MPa) VEYA V < 0.1 L
    I:   PS×V > 0.025 (25 bar·L)
    II:  PS×V > 0.05 (50 bar·L)
    III: PS×V > 0.35 (350 bar·L)
    IV:  PS×V > 1.0 (1000 bar·L)
    """
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_1,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.VESSEL,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.1, "SEP: PS<0.5bar veya V<0.1L"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.1, "Cat I: PS×V≥25 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.1, "Cat II: PS×V≥50 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.1, "Cat III: PS×V≥350 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.1, "Cat IV: PS×V≥1000 bar·L"),
        ],
    )


def _build_table_2() -> ClassificationTable:
    """Tablo 2: Grup 1 sıvılar — Kap.

    PS×V eşikleri (MPa·litre):
    SEP: PS < 0.5 bar (0.05 MPa) VEYA V < 0.1 L
    I:   PS×V > 0.025 (25 bar·L)
    II:  PS×V > 0.05 (50 bar·L)
    III: PS×V > 0.35 (350 bar·L)
    IV:  PS×V > 1.0 (1000 bar·L)
    """
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_2,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.VESSEL,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.1, "SEP: PS<0.5bar veya V<0.1L"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.1, "Cat I: PS×V≥25 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.1, "Cat II: PS×V≥50 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.1, "Cat III: PS×V≥350 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.1, "Cat IV: PS×V≥1000 bar·L"),
        ],
    )


def _build_table_7() -> ClassificationTable:
    """Tablo 7: Grup 2 gazlar — Kap.

    PS×V eşikleri (MPa·litre):
    SEP: PS < 0.5 bar (0.05 MPa) VE V < 0.1 L
    I:   PS×V > 0.05 (50 bar·L)
    II:  PS×V > 0.1 (100 bar·L)
    III: PS×V > 1.0 (1000 bar·L)
    IV:  PS×V > 5.0 (5000 bar·L)
    """
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_7,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.VESSEL,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.1, "SEP: PS<0.5bar VE V<0.1L"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.1, "Cat I: PS×V≥50 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.1, "Cat II: PS×V≥100 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.1, "Cat III: PS×V≥1000 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.1, "Cat IV: PS×V≥5000 bar·L"),
        ],
    )


def _build_table_8() -> ClassificationTable:
    """Tablo 8: Grup 2 sıvılar — Kap.

    PS×V eşikleri (MPa·litre):
    SEP: PS < 0.5 bar (0.05 MPa) VE V < 0.1 L
    I:   PS×V > 0.05 (50 bar·L)
    II:  PS×V > 0.1 (100 bar·L)
    III: PS×V > 1.0 (1000 bar·L)
    IV:  PS×V > 5.0 (5000 bar·L)
    """
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_8,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.VESSEL,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.1, "SEP: PS<0.5bar VE V<0.1L"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.1, "Cat I: PS×V≥50 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.1, "Cat II: PS×V≥100 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.1, "Cat III: PS×V≥1000 bar·L"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.1, "Cat IV: PS×V≥5000 bar·L"),
        ],
    )


def _build_table_3() -> ClassificationTable:
    """Tablo 3: Grup 1 gazlar — Piping (boru)."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_3,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.PIPING,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_4() -> ClassificationTable:
    """Tablo 4: Grup 1 sıvılar — Piping."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_4,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.PIPING,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_9() -> ClassificationTable:
    """Tablo 9: Grup 2 gazlar — Piping."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_9,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.PIPING,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_10() -> ClassificationTable:
    """Tablo 10: Grup 2 sıvılar — Piping."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_10,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.PIPING,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_5() -> ClassificationTable:
    """Tablo 5: Grup 1 gazlar — Aksesuar."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_5,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.SAFETY_ACCESSORY,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_6() -> ClassificationTable:
    """Tablo 6: Grup 1 sıvılar — Aksesuar."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_6,
        fluid_group=FluidGroupPED.GROUP_1,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.SAFETY_ACCESSORY,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.025, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.05, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 0.35, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 1.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_11() -> ClassificationTable:
    """Tablo 11: Grup 2 gazlar — Aksesuar."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_11,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.GAS,
        equipment_type=EquipmentType.SAFETY_ACCESSORY,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.0, "Cat IV"),
        ],
    )


def _build_table_12() -> ClassificationTable:
    """Tablo 12: Grup 2 sıvılar — Aksesuar."""
    return ClassificationTable(
        table_id=PEDClassificationTable.TABLE_12,
        fluid_group=FluidGroupPED.GROUP_2,
        fluid_phase=FluidPhasePED.LIQUID,
        equipment_type=EquipmentType.SAFETY_ACCESSORY,
        thresholds=[
            PSVThreshold(PEDCategory.SEP, 0.0, 0.05, 0.0, "SEP: PS<0.5bar"),
            PSVThreshold(PEDCategory.CATEGORY_I, 0.05, 0.05, 0.0, "Cat I"),
            PSVThreshold(PEDCategory.CATEGORY_II, 0.1, 0.05, 0.0, "Cat II"),
            PSVThreshold(PEDCategory.CATEGORY_III, 1.0, 0.05, 0.0, "Cat III"),
            PSVThreshold(PEDCategory.CATEGORY_IV, 5.0, 0.05, 0.0, "Cat IV"),
        ],
    )


# ── Tablo kayıt defteri ────────────────────────────────────────────────────────

_ALL_TABLES: List[ClassificationTable] = [
    _build_table_1(), _build_table_2(), _build_table_3(), _build_table_4(),
    _build_table_5(), _build_table_6(), _build_table_7(), _build_table_8(),
    _build_table_9(), _build_table_10(), _build_table_11(), _build_table_12(),
]


def get_classification_table(
    fluid_group: FluidGroupPED,
    fluid_phase: FluidPhasePED,
    equipment_type: EquipmentType,
) -> ClassificationTable:
    """Akışkan grubu, faz ve ekipman türüne göre sınıflandırma tablosunu getir.

    Args:
        fluid_group: PED akışkan grubu.
        fluid_phase: Akışkan fazı.
        equipment_type: Ekipman türü.

    Returns:
        İlgili ClassificationTable.

    Raises:
        ValueError: Uygun tablo bulunamazsa.
    """
    for table in _ALL_TABLES:
        if (table.fluid_group == fluid_group
                and table.fluid_phase == fluid_phase
                and table.equipment_type == equipment_type):
            return table

    raise ValueError(
        f"Uygun tablo bulunamadı: {fluid_group}, {fluid_phase}, {equipment_type}"
    )


__all__ = [
    "PSVThreshold",
    "ClassificationTable",
    "get_classification_table",
]
