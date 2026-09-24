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
    cone_volume,
    head_volume,
    shell_volume,
)
from calc_core.verification import (
    GoldenCase,
    TolerancePolicy,
    VerificationReport,
    assert_monotonic,
    validate_result,
    validate_suite,
    verify_golden_case,
)
from calc_core.load_engine import (
    GlobalLoadState,
    aggregate_load_case,
    combine_load_cases,
    governing_state,
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
    "cone_volume",
    "ProjectRevisionService",
    "RevisionRecord",
    "RevisionUpdateResult",
    "GlobalLoadState",
    "aggregate_load_case",
    "combine_load_cases",
    "governing_state",
    "GoldenCase",
    "TolerancePolicy",
    "VerificationReport",
    "assert_monotonic",
    "validate_result",
    "validate_suite",
    "verify_golden_case",
]
