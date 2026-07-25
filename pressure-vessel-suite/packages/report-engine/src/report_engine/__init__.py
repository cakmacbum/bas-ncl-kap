"""Report Engine — HTML/PDF rapor üretimi.

K6 kuralı: Standart telifli metni kopyalanmaz; yalnızca madde referansı saklanır.
İzlenebilirlik bloğu her raporda bulunur (kaynak §11).
"""

from .generator import ReportGenerator, ReportResult
from .traceability import TraceabilityBlock, build_traceability

__all__ = [
    "ReportGenerator",
    "ReportResult",
    "TraceabilityBlock",
    "build_traceability",
]
