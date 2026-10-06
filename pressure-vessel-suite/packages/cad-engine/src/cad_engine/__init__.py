"""CAD Engine — CadQuery ile parametrik basınçlı kap modeli ve STEP üretimi.

K2 kuralı: CAD hesabın kaynağı değildir.
project data → hesap motoru (ayrı)
project data → CAD motoru (ayrı)

CadQuery opsiyoneldir — kurulu değilse ImportError yükseltilir.
"""

from .validation import (
    CADValidationReport,
    CADValidationResult,
    validate_no_negative_volume,
    validate_no_open_shells,
    validate_solid_count,
    validate_volume_tolerance,
)
from .vessel_builder import CADQUERY_AVAILABLE, VesselCADResult, build_vessel, export_step
from .step_import import StepRecognition, recognize_step

__all__ = [
    "CADQUERY_AVAILABLE",
    "VesselCADResult",
    "build_vessel",
    "export_step",
    "StepRecognition",
    "recognize_step",
    "CADValidationReport",
    "CADValidationResult",
    "validate_solid_count",
    "validate_no_negative_volume",
    "validate_no_open_shells",
    "validate_volume_tolerance",
]
