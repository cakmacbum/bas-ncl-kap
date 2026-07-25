"""External-pressure paketi — dış basınç ve vakum stabilite hesabı.

ASME VIII-1 UG-28 mantığı: dış basınç altındaki silindirik gövde ve bombelerin
darbe (buckling) stabilite kontrolü. Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from external_pressure.ext_pressure import ExternalPressureCalculator

__all__ = ["ExternalPressureCalculator"]
