"""Welds paketi — Kaynak ve NDT modeli.

ASME VIII-1 UW-11/UW-12/UCS-56 kontrolleri.
K5 kuralı: Herhesap denetlenebilir.
"""

from domain.welds import WeldJoint
from .validator import (
    WeldValidationInput,
    WeldValidationResult,
    WeldCheckResult,
    validate_weld,
    build_weld_validation_result,
    check_nde_joint_efficiency,
    check_full_penetration,
    check_wps_pqr,
    check_welder_qualification,
    check_pwht,
    check_weld_category,
    check_ndt_extent,
    NDE_EFFICIENCY_MAP,
)

__all__ = [
    # domain model (re-export)
    "WeldJoint",
    # validator
    "WeldValidationInput",
    "WeldValidationResult",
    "WeldCheckResult",
    "validate_weld",
    "build_weld_validation_result",
    "check_nde_joint_efficiency",
    "check_full_penetration",
    "check_wps_pqr",
    "check_welder_qualification",
    "check_pwht",
    "check_weld_category",
    "check_ndt_extent",
    "NDE_EFFICIENCY_MAP",
]
