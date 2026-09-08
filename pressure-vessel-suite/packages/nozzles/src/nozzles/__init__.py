"""Nozzles paketi — Açıklık ve takviye hesapları.

ASME VIII-1 UG-37/UG-40 area replacement method.
K2 kuralı: Hesap yalnızca project data'dan çalışır, CAD ölçüsü kullanmaz.
"""

from .nozzle_schedule import NozzleScheduleEntry, generate_nozzle_schedule
from .reinforcement import (
    AreaItem,
    NozzleReinforcementInput,
    NozzleReinforcementResult,
    build_reinforcement_calculation_result,
    calculate_reinforcement,
    check_nozzle_eligibility,
)
from .clash_check import (
    ClashCheckResult,
    ClashCheckReport,
    check_nozzle_nozzle_clash,
    check_nozzle_weld_proximity,
    check_nozzle_tangent_line,
    check_hole_pad_relation,
    check_minimum_edge_distance,
    validate_nozzle_clash,
    build_clash_check_result,
    check_inspection_opening,
)
from .position import (
    NozzlePosition,
    calculate_nozzle_position,
    calculate_nozzle_position_on_shell,
    calculate_nozzle_position_on_head,
)

__all__ = [
    # reinforcement
    "NozzleReinforcementInput",
    "NozzleReinforcementResult",
    "AreaItem",
    "calculate_reinforcement",
    "check_nozzle_eligibility",
    "build_reinforcement_calculation_result",
    # schedule
    "NozzleScheduleEntry",
    "generate_nozzle_schedule",
    # clash_check
    "ClashCheckResult",
    "ClashCheckReport",
    "check_nozzle_nozzle_clash",
    "check_nozzle_weld_proximity",
    "check_nozzle_tangent_line",
    "check_hole_pad_relation",
    "check_minimum_edge_distance",
    "validate_nozzle_clash",
    "build_clash_check_result",
    "check_inspection_opening",
    # position
    "NozzlePosition",
    "calculate_nozzle_position",
    "calculate_nozzle_position_on_shell",
    "calculate_nozzle_position_on_head",
]
