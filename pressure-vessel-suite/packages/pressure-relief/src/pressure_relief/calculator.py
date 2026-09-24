from __future__ import annotations

from calc_core.result import CalculationResult
from pressure_relief.models import PressureReliefSystem


class PressureReliefCalculator:
    """Traceable UG-125--136 input and set-pressure validation."""

    def __init__(self, code: str = "ASME VIII-1", edition: str = ""):
        self.code = code
        self.edition = edition

    def check(self, system: PressureReliefSystem | None, global_mawp: float | None) -> list[CalculationResult]:
        if system is None or not system.enabled:
            r = self._result("RELIEF-SYSTEM", "system")
            r.set_out_of_scope("Pressure relief system is not configured for this project.")
            return [r]
        if not system.devices:
            r = self._result("RELIEF-SYSTEM", "system")
            r.set_blocked_missing_input("At least one safety valve or rupture disk is required.")
            return [r]

        protected_mawp = system.protected_mawp_mpa or global_mawp
        results: list[CalculationResult] = []
        for device in system.devices:
            r = self._result(device.device_id, "pressure_relief_device")
            r.input_snapshot = {
                "device": device.model_dump(mode="json"),
                "protected_mawp_mpa": protected_mawp,
                "accumulation_limit_percent": system.accumulation_limit_percent,
            }
            r.add_intermediate("protected_mawp", protected_mawp, "MPa", "Protected vessel MAWP")
            pressure = device.relieving_pressure_mpa
            if protected_mawp is None or pressure is None:
                r.set_blocked_missing_input(
                    "Protected MAWP and valve set pressure (or rupture-disk burst pressure) are required."
                )
                results.append(r)
                continue
            r.add_intermediate("relieving_pressure", pressure, "MPa", "Set/burst pressure")
            r.allowable_limit = protected_mawp
            r.allowable_limit_unit = "MPa"
            r.final_result = pressure
            r.final_result_unit = "MPa"
            r.utilization_ratio = pressure / protected_mawp
            if pressure > protected_mawp:
                r.set_fail(r.utilization_ratio)
                r.add_warning("Set/burst pressure exceeds protected component MAWP.")
            else:
                r.set_pass(r.utilization_ratio)
            if device.accumulation_percent is None and r.status.value == "PASS":
                r.set_review_required("Accumulation must be established for the applicable relief scenario.")
            elif device.accumulation_percent is not None and device.accumulation_percent > system.accumulation_limit_percent:
                r.set_fail(r.utilization_ratio)
                r.add_warning("Accumulation exceeds the configured allowable limit.")
            r.add_intermediate("accumulation_percent", device.accumulation_percent, "%", "Relief scenario accumulation")
            if device.certified_capacity_kg_s is None and r.status.value == "PASS":
                r.set_review_required(
                    "Certified relieving capacity is missing; this validation is not a sizing calculation."
                )
            results.append(r)
        return results

    def _result(self, component_id: str, component_type: str) -> CalculationResult:
        return CalculationResult(
            component_id=component_id,
            component_type=component_type,
            calculation_type="pressure_relief",
            code=self.code,
            edition=self.edition,
            clause_reference="UG-125--136",
            formula_reference="set/burst pressure, accumulation and capacity validation",
        )


__all__ = ["PressureReliefCalculator"]
