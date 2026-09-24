"""Faz E1: hesap sonucu doğrulama ve golden-case yardımcıları."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus


@dataclass(frozen=True)
class TolerancePolicy:
    """Sayısal karşılaştırma politikası (mutlak + bağıl tolerans)."""

    absolute: float = 1e-9
    relative: float = 1e-6

    def __post_init__(self) -> None:
        if not math.isfinite(self.absolute) or not math.isfinite(self.relative):
            raise ValueError("Toleranslar sonlu sayılar olmalıdır.")
        if self.absolute < 0 or self.relative < 0:
            raise ValueError("Toleranslar negatif olamaz.")

    def compare(self, actual: float, expected: float) -> bool:
        if not math.isfinite(actual) or not math.isfinite(expected):
            return False
        scale = max(abs(actual), abs(expected), 1.0)
        return abs(actual - expected) <= max(self.absolute, self.relative * scale)


@dataclass(frozen=True)
class GoldenCase:
    """Bağımsız referans sonucu olan tek doğrulama vakası."""

    name: str
    expected: Mapping[str, float]
    tolerance: TolerancePolicy = field(default_factory=TolerancePolicy)
    applicability: Callable[[Any], bool] | None = None
    boundary: str = "normal"


@dataclass
class VerificationReport:
    """Bir vaka/suite doğrulamasının denetlenebilir özeti."""

    case_name: str
    passed: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"case_name": self.case_name, "passed": self.passed,
                "checks": list(self.checks), "errors": list(self.errors)}


def _finite(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, Mapping):
        return all(_finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite(v) for v in value)
    return True


def validate_result(result: CalculationResult) -> list[str]:
    """Sonuçta NaN/inf, geçersiz oran veya uygunsuz PASS var mı kontrol et."""
    errors: list[str] = []
    if not _finite(result.to_dict()):
        errors.append("Sonuç NaN/inf içeriyor.")
    if result.status == CalculationStatus.PASS and result.final_result is None:
        errors.append("PASS sonucu final_result içermiyor.")
    if result.utilization_ratio is not None and result.utilization_ratio < 0:
        errors.append("Kullanım oranı negatif olamaz.")
    if result.status == CalculationStatus.PASS and result.warnings:
        errors.append("Uyarı içeren sonuç PASS olarak yayınlanamaz.")
    return errors


def verify_golden_case(case: GoldenCase, actual: Mapping[str, float], subject: Any = None) -> VerificationReport:
    """Beklenen bağımsız değerleri tolerans politikasıyla karşılaştır."""
    report = VerificationReport(case_name=case.name, passed=True)
    if case.applicability is not None and not case.applicability(subject):
        report.passed = False
        report.errors.append("Vaka uygulanabilirlik koşulunu sağlamıyor.")
        return report
    for key, expected in case.expected.items():
        value = actual.get(key)
        try:
            numeric_value = float(value) if value is not None else math.nan
        except (TypeError, ValueError, OverflowError):
            numeric_value = math.nan
        ok = case.tolerance.compare(numeric_value, expected)
        report.checks.append({"key": key, "expected": expected, "actual": value, "passed": ok})
        if not ok:
            report.passed = False
            report.errors.append(f"{key}: beklenen {expected}, gerçek {value}.")
    return report


def assert_monotonic(values: Sequence[float], increasing: bool = True) -> bool:
    """Property test yardımcı fonksiyonu."""
    pairs = zip(values, values[1:])
    return all(a <= b for a, b in pairs) if increasing else all(a >= b for a, b in pairs)


def validate_suite(results: Iterable[CalculationResult]) -> VerificationReport:
    """Bir hesap koşusundaki tüm sonuçların yayınlanabilirlik kontrolü."""
    report = VerificationReport(case_name="calculation-run", passed=True)
    for result in results:
        errors = validate_result(result)
        report.checks.append({"calculation_id": result.calculation_id, "passed": not errors})
        if errors:
            report.passed = False
            report.errors.extend(f"{result.component_id}: {error}" for error in errors)
    return report


__all__ = ["GoldenCase", "TolerancePolicy", "VerificationReport", "assert_monotonic",
           "validate_result", "validate_suite", "verify_golden_case"]
