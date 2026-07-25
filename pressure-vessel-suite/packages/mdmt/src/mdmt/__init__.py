"""MDMT paketi — Minimum Design Metal Temperature hesapları.

ASME VIII-1 UCS-66 mantığı: Malzeme eğri grubu, muafiyet kontrolü,
sıcaklık indirimi hesapları.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from mdmt.mdmt_calc import MDMTCalculator, UCS66CurveGroup, UCS66_MDMT_LIMITS

__all__ = ["MDMTCalculator", "UCS66CurveGroup", "UCS66_MDMT_LIMITS"]
