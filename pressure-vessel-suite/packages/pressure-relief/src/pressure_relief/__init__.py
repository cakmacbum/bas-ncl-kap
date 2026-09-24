"""Pressure relief devices (ASME VIII-1 UG-125--136)."""

from pressure_relief.models import PressureReliefDevice, PressureReliefSystem


def __getattr__(name: str):
    if name == "PressureReliefCalculator":
        from pressure_relief.calculator import PressureReliefCalculator
        return PressureReliefCalculator
    raise AttributeError(name)

__all__ = ["PressureReliefDevice", "PressureReliefSystem", "PressureReliefCalculator"]
