"""Domain enum'ları — standarttan bağımsız."""

from __future__ import annotations

from enum import Enum


class CalculationStatus(str, Enum):
    """Hesap sonucu durumları (kaynak §0.2)."""
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW REQUIRED"
    NOT_CALCULATED = "NOT CALCULATED"
    OUT_OF_SCOPE = "OUT OF SCOPE"
    BLOCKED_CODE_DATA = "BLOCKED CODE DATA"
    BLOCKED_MISSING_INPUT = "BLOCKED MISSING INPUT"


class HeadType(str, Enum):
    """Bombe tipleri."""
    ELLIPTICAL = "elliptical"
    TORISPHERICAL = "torispherical"
    HEMISPHERICAL = "hemispherical"
    FLAT = "flat"


class Orientation(str, Enum):
    """Kap yönü."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class CalculationCode(str, Enum):
    """Hesap standardı."""
    ASME_VIII_1 = "ASME VIII-1"
    EN_13445 = "EN 13445"


class FluidPhase(str, Enum):
    """Akışkan fazı."""
    GAS = "gas"
    LIQUID = "liquid"
    STEAM = "steam"


class FluidGroup(str, Enum):
    """Akışkan grubu (PED)."""
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"


class ProductForm(str, Enum):
    """Ürün formu."""
    PLATE = "plate"
    FORGING = "forging"
    SEAMLESS_PIPE = "seamless_pipe"
    WELDED_PIPE = "welded_pipe"
    BAR = "bar"
    CASTING = "casting"


class NozzleType(str, Enum):
    """Nozul tipleri."""
    SLIP_ON = "slip_on"
    SOCKET_WELDED = "socket_welded"
    COUPLING = "coupling"  # Manşon — gövdeye kaynaklı kısa kalın bilezik
    MANWAY = "manway"
    FLANGED = "flanged"
    PAD_REINFORCED = "pad_reinforced"


__all__ = [
    "CalculationStatus",
    "HeadType",
    "Orientation",
    "CalculationCode",
    "FluidPhase",
    "FluidGroup",
    "ProductForm",
    "NozzleType",
]
