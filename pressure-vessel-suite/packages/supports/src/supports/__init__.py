"""Supports paketi — yatay kap eyer (saddle) ve dikey kap etek (skirt) destek hesapları.

Zick analizi mantığı ile saddle; temel basıncı ve gerilme kontrolü ile skirt.
Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from supports.support_calc import SupportCalculator

__all__ = ["SupportCalculator"]
