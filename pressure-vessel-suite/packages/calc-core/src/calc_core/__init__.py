"""Calc-core paketi — ortak hesap altyapısı.

K5 kuralı: Her hesap denetlenebilir olmalı (CalculationResult).
K7 kuralı: Domain modelinden bağımsız (DesignCode arayüzü).
"""

from calc_core.code_interface import DesignCode
from calc_core.orchestrator import CalculationOrchestrator, OrchestratorResult
from calc_core.result import CalculationResult
from calc_core.revision_service import ProjectRevisionService, RevisionRecord, RevisionUpdateResult
from calc_core.volume_mass import (
    MassResult,
    VesselVolumeMassReport,
    VolumeResult,
    calculate_mass,
    calculate_vessel_volume_mass,
    head_volume,
    shell_volume,
)

__all__ = [
    "CalculationResult",
    "DesignCode",
    "CalculationOrchestrator",
    "OrchestratorResult",
    "VolumeResult",
    "MassResult",
    "VesselVolumeMassReport",
    "shell_volume",
    "head_volume",
    "calculate_mass",
    "calculate_vessel_volume_mass",
    "ProjectRevisionService",
    "RevisionRecord",
    "RevisionUpdateResult",
]
