"""FEA paketi — iskelet + adapter.

Parametrik CAD → basitleştirilmiş geometri → Gmsh mesh → CalculiX/Code_Aster
→ stress linearization → code acceptance. Çözücü kurulu değilse modülü
"REVIEW REQUIRED / mesh ve sınır şartları mühendis onayı gerektirir" ile
iskelet bırakır; sahte "PASS" ÜRETMEZ.

Ek doğrulama modülüdür; çekirdeğin yerine geçmez.

K1 kuralı: Formüller yalnızca bu pakette.
K5 kuralı: Her hesap denetlenebilir (CalculationResult).
"""

from fea.fea_adapter import FEAdapter

__all__ = ["FEAdapter"]
