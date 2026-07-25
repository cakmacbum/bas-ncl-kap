"""Domain paketi — standarttan bağımsız veri modelleri.

K7 kuralı: Bu modeller ASME/EN/CAD/PDF'den bağımsızdır.
Hesap kuralları code plugin'lerinde uygulanır.
"""

from domain.conditions import DesignConditions
from domain.enums import (
    CalculationCode,
    CalculationStatus,
    FluidGroup,
    FluidPhase,
    HeadType,
    NozzleType,
    Orientation,
    ProductForm,
)
from domain.geometry import Cone, Head, Nozzle, ShellSection
from domain.load_cases import (
    ExternalLoad,
    LoadCase,
    LoadCombination,
    LoadDirection,
    LoadType,
    MANDATORY_LOAD_CASE_TEMPLATES,
    NON_CONCURRENT_LOAD_PAIRS,
    generate_structural_load_cases,
    generate_wind_load_cases,
    generate_seismic_load_cases,
    generate_transport_load_cases,
    generate_lifting_load_cases,
)
from domain.materials import MaterialProperty
from domain.persistence import compute_input_hash, load_project_json, save_project_json
from domain.project import FluidInfo, VesselProject
from domain.welds import WeldJoint

__all__ = [
    # Enums
    "CalculationCode",
    "CalculationStatus",
    "FluidGroup",
    "FluidPhase",
    "HeadType",
    "LoadDirection",
    "LoadType",
    "NozzleType",
    "Orientation",
    "ProductForm",
    # Models
    "DesignConditions",
    "ExternalLoad",
    "FluidInfo",
    "Head",
    "Cone",
    "LoadCase",
    "LoadCombination",
    "MaterialProperty",
    "Nozzle",
    "ShellSection",
    "VesselProject",
    "WeldJoint",
    # Constants
    "MANDATORY_LOAD_CASE_TEMPLATES",
    "NON_CONCURRENT_LOAD_PAIRS",
    # Functions
    "generate_structural_load_cases",
    "generate_wind_load_cases",
    "generate_seismic_load_cases",
    "generate_transport_load_cases",
    "generate_lifting_load_cases",
    # Persistence
    "compute_input_hash",
    "save_project_json",
    "load_project_json",
]
