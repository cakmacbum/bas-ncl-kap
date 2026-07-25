"""Flanges paketi — flanş hesabı (ASME VIII-1 Appendix 2 mantığı).

Moment, gerilme kontrolleri ve flanş boyutlandırma.
Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from flanges.flange_calc import FlangeCalculator
from flanges import formulas

__all__ = ["FlangeCalculator", "formulas"]
