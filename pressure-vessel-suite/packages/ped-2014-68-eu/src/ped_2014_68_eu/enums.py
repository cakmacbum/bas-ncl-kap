"""PED 2014/68/EU enum'ları."""

from __future__ import annotations

from enum import Enum


class EquipmentType(str, Enum):
    """PED Ek II'deki ekipman tipleri."""
    VESSEL = "vessel"
    PIPING = "piping"
    SAFETY_ACCESSORY = "safety_accessory"
    PRESSURE_ACCESSORY = "pressure_accessory"
    ASSEMBLY = "assembly"


class FluidGroupPED(str, Enum):
    """PED akışkan grupları (CLP'ye göre).

    Grup 1: Patlayıcı, oksitleyici, yanıcı, toksik, çok toksik vb.
    Grup 2: Grup 1'de yer almayan tüm akışkanlar.
    """
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"
    UNCLASSIFIED = "Unclassified"


class FluidPhasePED(str, Enum):
    """Akışkan fazı (PED sınıflandırması)."""
    GAS = "gas"          # Gaz, buhar
    LIQUID = "liquid"    # Sıvı (buhar basıncı 0.5 bar'dan düşük)


class StateOfCharge(str, Enum):
    """Akışkan durumu (gaz/sıvı)."""
    GASEOUS = "gaseous"    # Gaz halinde
    LIQUEFIED = "liquefied"  # Sıvılaştırılmış gaz
    DISSOLVED = "dissolved"  # Çözünmüş gaz


class GHSClassification(str, Enum):
    """CLP/GHS tehlike sınıfları (PED sınıflandırması için)."""
    EXPLOSIVE = "Explosive"
    OXIDIZING = "Oxidizing"
    FLAMMABLE_GAS = "Flammable Gas"
    FLAMMABLE_LIQUID = "Flammable Liquid"
    FLAMMABLE_SOLID = "Flammable Solid"
    PYROPHORIC = "Pyrophoric"
    SELF_REACTIVE = "Self-Reactive"
    ORGANIC_PEROXIDE = "Organic Peroxide"
    TOXIC = "Toxic"
    VERY_TOXIC = "Very Toxic"
    CORROSIVE = "Corrosive"
    HIGH_PRESSURE_GAS = "High-Pressure Gas"
    OTHER = "Other"


class PEDCategory(str, Enum):
    """PED kategorileri."""
    SEP = "SEP"  # Sound Engineering Practice
    CATEGORY_I = "Category I"
    CATEGORY_II = "Category II"
    CATEGORY_III = "Category III"
    CATEGORY_IV = "Category IV"


class PEDClassificationTable(str, Enum):
    """PED Ek II sınıflandırma tabloları."""
    TABLE_1 = "Table 1"  # Grup 1 gazlar — kap
    TABLE_2 = "Table 2"  # Grup 1 sıvılar — kap
    TABLE_3 = "Table 3"  # Grup 1 gazlar — boru
    TABLE_4 = "Table 4"  # Grup 1 sıvılar — boru
    TABLE_5 = "Table 5"  # Grup 1 gazlar — aksesuar
    TABLE_6 = "Table 6"  # Grup 1 sıvılar — aksesuar
    TABLE_7 = "Table 7"  # Grup 2 gazlar — kap
    TABLE_8 = "Table 8"  # Grup 2 sıvılar — kap
    TABLE_9 = "Table 9"  # Grup 2 gazlar — boru
    TABLE_10 = "Table 10"  # Grup 2 sıvılar — boru
    TABLE_11 = "Table 11"  # Grup 2 gazlar — aksesuar
    TABLE_12 = "Table 12"  # Grup 2 sıvılar — aksesuar


class ConformityModule(str, Enum):
    """PED uygunluk modülleri (Bölüm II, Madde 14)."""
    # Modül A: İç üretim kontrolü
    A = "A"
    # Modül A2: İç üretim kontrolü + izlenen teslimatta deneme
    A2 = "A2"
    # Modül B: AB tip incelemesi
    B = "B"
    # Modül C2: Üretim süreci kalite güvencesi (izlenen teslimatta deneme)
    C2 = "C2"
    # Modül D: Üretim kalite güvencesi
    D = "D"
    # Modül D1: Üretim kalite güvencesi (tam set)
    D1 = "D1"
    # Modül E: Ürün kalite güvencesi
    E = "E"
    # Modül E1: Ürün kalite güvencesi (tam set)
    E1 = "E1"
    # Modül F: Ürün doğrulaması
    F = "F"
    # Modül G: Birim doğrulama
    G = "G"
    # Modül H: Tam kalite güvencesi
    H = "H"
    # Modül H1: Tam kalite güvencesi + tasarım incelemesi
    H1 = "H1"
    # SEP: Sound Engineering Practice — CE yok
    NONE = "None"


class NotifyBodyRequired(str, Enum):
    """Onaylanmış kuruluş gerekliliği."""
    NOT_REQUIRED = "Not Required"
    REQUIRED = "Required"
    OPTIONAL = "Optional"


class HeatedStatus(str, Enum):
    """Isıtma durumu."""
    NOT_HEATED = "Not Heated"
    FIRED = "Fired"           # Ateşleme
    EXTERNALLY_HEATED = "Externally Heated"  # Dıştan ısıtma


__all__ = [
    "EquipmentType",
    "FluidGroupPED",
    "FluidPhasePED",
    "StateOfCharge",
    "GHSClassification",
    "PEDCategory",
    "PEDClassificationTable",
    "ConformityModule",
    "NotifyBodyRequired",
    "HeatedStatus",
]
