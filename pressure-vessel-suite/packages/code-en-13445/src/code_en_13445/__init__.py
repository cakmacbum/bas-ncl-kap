"""EN 13445 hesap eklentisi — Pressure Vessel Suite.

EN 13445 Unfired pressure vessels standardına göre hesaplar.
calc-core DesignCode arayüzünü uygular.

K1 kuralı: Formüller yalnızca bu hesap eklentisinde.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.
K7 kuralı: Domain modelinden bağımsız.

Referans: EN 13445:2021+A1:2023
"""

from code_en_13445.design_code import EN13445DesignCode
from code_en_13445.formulas import (
    shell_thickness_internal_pressure,
    head_elliptical_thickness,
    head_torispherical_thickness,
    head_hemispherical_thickness,
    mawp_from_shell,
    mawp_from_head,
    ped_test_pressure,
)

__all__ = [
    "EN13445DesignCode",
    "shell_thickness_internal_pressure",
    "head_elliptical_thickness",
    "head_torispherical_thickness",
    "head_hemispherical_thickness",
    "mawp_from_shell",
    "mawp_from_head",
    "ped_test_pressure",
]
