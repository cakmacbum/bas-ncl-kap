"""Yük durumu modelleri — LoadCase, LoadCombination, ExternalLoad.

§7.2'deki 15 zorunlu load-case şablonu ve kombinasyon matrisi.
K7 kuralı: Bu modeller standarttan bağımsızdır.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class LoadType(str, Enum):
    """Yük tipi."""
    PRESSURE = "pressure"
    DEAD_WEIGHT = "dead_weight"
    OPERATING = "operating"
    LIVE_LOAD = "live_load"
    WIND = "wind"
    SEISMIC = "seismic"
    THERMAL = "thermal"
    SNOW = "snow"
    FLUID_WEIGHT = "fluid_weight"
    EXTERNAL = "external"
    HYDROTEST = "hydrotest"
    PNEUMATIC_TEST = "pneumatic_test"
    TRANSPORT = "transport"
    LIFTING = "lifting"
    VACUUM = "vacuum"
    ACCIDENTAL = "accidental"


class LoadDirection(str, Enum):
    """Yök yönü."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    AXIAL = "axial"
    RADIAL = "radial"
    CIRCUMFERENTIAL = "circumferential"


class LoadCase(BaseModel):
    """Tek bir yük durumu.

    §7.2'deki şablonlardan biri veya özel bir durum.
    """

    load_case_id: str = Field(..., description="Yük durumu kimliği (ör. 'LC-001').")
    name: str = Field(..., description="Yük durumu adı (ör. 'Operating', 'Hydrotest').")
    load_type: LoadType = Field(..., description="Yük tipi.")
    description: str = Field(default="", description="Açıklama.")

    # Basınç
    pressure_mpa: float = Field(
        default=0.0, ge=0,
        description="Bu durumdaki basınç (MPa)."
    )

    # Sıcaklık
    temperature_c: float = Field(
        default=20.0,
        description="Bu durumdaki sıcaklık (°C)."
    )

    # Dış yükler
    external_loads: List["ExternalLoad"] = Field(
        default_factory=list,
        description="Bu durumdaki dış yükler."
    )

    # Statik kafa
    fluid_density_kg_m3: float = Field(
        default=0.0, ge=0,
        description="Akışkan yoğunluğu (kg/m³). Statik kafa hesabı için."
    )
    fluid_level_mm: float = Field(
        default=0.0, ge=0,
        description="Akışkan seviyesi (mm). Referans kottan itibaren."
    )

    # Rüzgâr / Deprem
    wind_speed_m_s: float = Field(
        default=0.0, ge=0,
        description="Rüzgâr hızı (m/s)."
    )
    seismic_zone_factor: float = Field(
        default=0.0, ge=0,
        description="Deprem bölgesel faktörü."
    )

    # Kombinasyon
    is_envelope: bool = Field(
        default=False,
        description="Bu durum bir zarf (envelope) durumu mu?"
    )
    concurrent_with: List[str] = Field(
        default_factory=list,
        description="Eşzamanlı olabileceği diğer yük durumu ID'leri."
    )


class ExternalLoad(BaseModel):
    """Dış yük bileşeni.

    6 bileşenli yük: Fx, Fy, Fz, Mx, My, Mz.
    """

    load_id: str = Field(..., description="Yük kimliği.")
    component_id: str = Field(
        default="",
        description="Yükün uygulandığı bileşen (nozul, destek vb.)."
    )

    # Kuvvet (N)
    fx_n: float = Field(default=0.0, description="X ekseni kuvveti (N).")
    fy_n: float = Field(default=0.0, description="Y ekseni kuvveti (N).")
    fz_n: float = Field(default=0.0, description="Z ekseni kuvveti (N).")

    # Moment (N·mm)
    mx_nmm: float = Field(default=0.0, description="X ekseni momenti (N·mm).")
    my_nmm: float = Field(default=0.0, description="Y ekseni momenti (N·mm).")
    mz_nmm: float = Field(default=0.0, description="Z ekseni momenti (N·mm).")

    # Konum
    elevation_mm: float = Field(
        default=0.0,
        description="Yükün uygulandığı kot (mm). Referans kottan itibaren."
    )
    direction: LoadDirection = Field(
        default=LoadDirection.VERTICAL,
        description="Ana yük yönü."
    )


class LoadCombination(BaseModel):
    """Yük kombinasyonu.

    §4 kombinasyon matrisine göre eşzamanlı yüklerin birleşimi.
    """

    combination_id: str = Field(..., description="Kombinasyon kimliği (ör. 'LC-COMB-001').")
    name: str = Field(..., description="Kombinasyon adı.")
    description: str = Field(default="", description="Açıklama.")

    # Katılan yük durumları
    load_case_ids: List[str] = Field(
        ...,
        description="Bu kombinasyona katılan yük durumu ID'leri."
    )

    # Yük faktörleri (her yük durumu için)
    load_factors: dict = Field(
        default_factory=dict,
        description="Yük durumu ID → faktör eşlemesi. Boş = hepsi 1.0."
    )

    # Eşzamanlılık
    is_concurrent: bool = Field(
        default=True,
        description="Yükler eşzamanlı mı uygulanır?"
    )

    # Standart
    standard: str = Field(
        default="",
        description="Kombinasyon standardı (ör. 'ASCE 7', 'EN 1991-1-1')."
    )
    standard_edition: str = Field(
        default="",
        description="Standart sürümü."
    )

    # Durum
    is_governing: bool = Field(
        default=False,
        description="Bu kombinasyon yöneten mi?"
    )


# 15 zorunlu load-case şablonu (§7.2)
MANDATORY_LOAD_CASE_TEMPLATES = [
    {"load_type": LoadType.DEAD_WEIGHT, "name": "Empty / Dead Weight", "description": "Boş kap ağırlığı"},
    {"load_type": LoadType.OPERATING, "name": "Operating", "description": "Çalışma koşulları (basınç + sıcaklık + akışkan)"},
    {"load_type": LoadType.FLUID_WEIGHT, "name": "Full / Flooded", "description": "Tam dolu (test veya çalışma)"},
    {"load_type": LoadType.HYDROTEST, "name": "Hydrotest", "description": "Hidrostatik test"},
    {"load_type": LoadType.PNEUMATIC_TEST, "name": "Pneumatic Test", "description": "Pnömatik test"},
    {"load_type": LoadType.WIND, "name": "Wind (Operating)", "description": "Rüzgâr + çalışma"},
    {"load_type": LoadType.WIND, "name": "Wind (Empty)", "description": "Rüzgâr + boş"},
    {"load_type": LoadType.SEISMIC, "name": "Seismic (Operating)", "description": "Deprem + çalışma"},
    {"load_type": LoadType.SEISMIC, "name": "Seismic (Empty)", "description": "Deprem + boş"},
    {"load_type": LoadType.THERMAL, "name": "Thermal Expansion", "description": "Genişme/ büzülme"},
    {"load_type": LoadType.SNOW, "name": "Snow / Ice", "description": "Kar / buz yükü"},
    {"load_type": LoadType.TRANSPORT, "name": "Transport", "description": "Taşıma"},
    {"load_type": LoadType.LIFTING, "name": "Lifting", "description": "Kaldırma"},
    {"load_type": LoadType.VACUUM, "name": "Vacuum", "description": "Vakum koşulu"},
    {"load_type": LoadType.ACCIDENTAL, "name": "Accidental / Upset", "description": "Olağanüstü durum"},
]


# Eşzamanlı olmayan yükler (§4 kombinasyon matrisi)
NON_CONCURRENT_LOAD_PAIRS = [
    (LoadType.HYDROTEST, LoadType.WIND),
    (LoadType.HYDROTEST, LoadType.SEISMIC),
    (LoadType.PNEUMATIC_TEST, LoadType.WIND),
    (LoadType.PNEUMATIC_TEST, LoadType.SEISMIC),
    (LoadType.WIND, LoadType.SEISMIC),  # Genellikle birlikte alınmaz
]


def generate_wind_load_cases(
    wind_speed_m_s: float,
    exposure_category: str = "C",
    directionality_factor: float = 0.85,
) -> List[LoadCase]:
    """Rüzgâr yük durumları oluştur (ASCE 7 / EN 1991-1-4).

    Args:
        wind_speed_m_s: Rüzgâr hızı (m/s).
        exposure_category: Maruz kalma kategorisi (A, B, C, D).
        directionality_factor: Yön faktörü Kd.

    Returns:
        Rüzgâr yük durumları listesi.
    """
    return [
        LoadCase(
            load_case_id="LC-WIND-OP",
            name="Wind (Operating)",
            load_type=LoadType.WIND,
            description=f"Rüzgâr ({wind_speed_m_s} m/s) + çalışma koşulları",
            wind_speed_m_s=wind_speed_m_s,
        ),
        LoadCase(
            load_case_id="LC-WIND-EMPTY",
            name="Wind (Empty)",
            load_type=LoadType.WIND,
            description=f"Rüzgâr ({wind_speed_m_s} m/s) + boş kap",
            wind_speed_m_s=wind_speed_m_s,
        ),
    ]


def generate_seismic_load_cases(
    zone_factor: float,
    importance_factor: float = 1.0,
    response_modification: float = 3.0,
) -> List[LoadCase]:
    """Deprem yük durumları oluştur (ASCE 7 / EN 1998-4 / TBDY).

    Args:
        zone_factor: Deprem bölgesel faktörü (Z veya ag).
        importance_factor: Önem faktörü (I veya Ie).
        response_modification: Tepki modifikasyon faktörü (R).

    Returns:
        Deprem yük durumları listesi.
    """
    return [
        LoadCase(
            load_case_id="LC-SEISMIC-OP",
            name="Seismic (Operating)",
            load_type=LoadType.SEISMIC,
            description=f"Deprem (Z={zone_factor}) + çalışma koşulları",
            seismic_zone_factor=zone_factor,
        ),
        LoadCase(
            load_case_id="LC-SEISMIC-EMPTY",
            name="Seismic (Empty)",
            load_type=LoadType.SEISMIC,
            description=f"Deprem (Z={zone_factor}) + boş kap",
            seismic_zone_factor=zone_factor,
        ),
    ]


def generate_transport_load_cases() -> List[LoadCase]:
    """Taşıma yük durumları oluştur."""
    return [
        LoadCase(
            load_case_id="LC-TRANSPORT-H",
            name="Transport (Horizontal)",
            load_type=LoadType.TRANSPORT,
            description="Yatay taşıma",
        ),
        LoadCase(
            load_case_id="LC-TRANSPORT-V",
            name="Transport (Vertical)",
            load_type=LoadType.TRANSPORT,
            description="Dikey taşıma",
        ),
    ]


def generate_lifting_load_cases() -> List[LoadCase]:
    """Kaldırma yük durumları oluştur."""
    return [
        LoadCase(
            load_case_id="LC-LIFT-VERTICAL",
            name="Lifting (Vertical)",
            load_type=LoadType.LIFTING,
            description="Dikey kaldırma",
        ),
        LoadCase(
            load_case_id="LC-LIFT-TILT",
            name="Lifting (Tilted)",
            load_type=LoadType.LIFTING,
            description="Eğik kaldırma",
        ),
    ]


def generate_structural_load_cases(
    wind_speed_m_s: float = 0.0,
    seismic_zone_factor: float = 0.0,
    include_transport: bool = False,
    include_lifting: bool = False,
    standard: str = "ASCE 7",
) -> List[LoadCase]:
    """Yapısal yük durumları oluştur (§7.10 structural_design_basis seçici).

    Args:
        wind_speed_m_s: Rüzgâr hızı (m/s). 0 = rüzgâr yok.
        seismic_zone_factor: Deprem faktörü. 0 = deprem yok.
        include_transport: Taşıma durumları eklensin mi?
        include_lifting: Kaldırma durumları eklensin mi?
        standard: Standart seçimi.

    Returns:
        Yapısal yük durumları listesi.
    """
    cases = []

    if wind_speed_m_s > 0:
        cases.extend(generate_wind_load_cases(wind_speed_m_s))

    if seismic_zone_factor > 0:
        cases.extend(generate_seismic_load_cases(seismic_zone_factor))

    if include_transport:
        cases.extend(generate_transport_load_cases())

    if include_lifting:
        cases.extend(generate_lifting_load_cases())

    return cases


def validate_load_combination(
    load_cases: List[LoadCase], combination: LoadCombination
) -> List[str]:
    """Bir kombinasyonun referans ve eşzamanlılık kurallarını doğrula.

    Bu yordam hesap yapmaz; bir kombinasyonun sessizce boş/yanlış yüklerle
    çalıştırılmasını önlemek için deterministik hata listesi döndürür.
    Boş liste geçerli olduğunu belirtir.
    """
    by_id = {case.load_case_id: case for case in load_cases}
    errors: List[str] = []
    if not combination.load_case_ids:
        errors.append("Combination must reference at least one load case.")
        return errors
    missing = [case_id for case_id in combination.load_case_ids if case_id not in by_id]
    if missing:
        errors.append(f"Unknown load case id(s): {', '.join(missing)}")
    factors = combination.load_factors
    unknown_factor_ids = [case_id for case_id in factors if case_id not in combination.load_case_ids]
    if unknown_factor_ids:
        errors.append(f"Load factors reference non-member case(s): {', '.join(unknown_factor_ids)}")
    if combination.is_concurrent:
        selected = [by_id[case_id].load_type for case_id in combination.load_case_ids if case_id in by_id]
        for left, right in NON_CONCURRENT_LOAD_PAIRS:
            if left in selected and right in selected:
                errors.append(f"Non-concurrent load types combined: {left.value} + {right.value}")
    return errors


__all__ = [
    "LoadType",
    "LoadDirection",
    "LoadCase",
    "ExternalLoad",
    "LoadCombination",
    "MANDATORY_LOAD_CASE_TEMPLATES",
    "NON_CONCURRENT_LOAD_PAIRS",
    "generate_wind_load_cases",
    "generate_seismic_load_cases",
    "generate_transport_load_cases",
    "generate_lifting_load_cases",
    "generate_structural_load_cases",
    "validate_load_combination",
]
