"""CAD doğrulama kontrolleri — geometri geçerlilik (kaynak §10).

K2 kuralı: CAD hesabın kaynağı değildir — doğrulamalar yalnızca
üretilmiş model üzerinde yapılır, hesaba geri beslemez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CADValidationResult:
    """Tek bir CAD doğrulama sonucu."""

    check_name: str
    passed: bool
    message: str
    expected: Optional[float] = None
    actual: Optional[float] = None
    tolerance_pct: Optional[float] = None


@dataclass
class CADValidationReport:
    """Tüm CAD doğrulama sonuçlarının raporu."""

    results: List[CADValidationResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed_checks(self) -> List[CADValidationResult]:
        return [r for r in self.results if not r.passed]

    def add(self, result: CADValidationResult) -> None:
        self.results.append(result)

    def to_dict(self) -> dict:
        return {
            "all_passed": self.all_passed,
            "checks": [
                {
                    "name": r.check_name,
                    "passed": r.passed,
                    "message": r.message,
                    "expected": r.expected,
                    "actual": r.actual,
                    "tolerance_pct": r.tolerance_pct,
                }
                for r in self.results
            ],
        }


def _get_solids(shape):
    """Workplane veya Shape'den solid listesini al.

    CadQuery 2.x: Workplane → .val().Solids() veya .solids().vals()
    CadQuery Shape → .Solids() doğrudan çalışır.
    """
    try:
        # CadQuery 2.x Workplane
        if hasattr(shape, "solids") and callable(shape.solids):
            return shape.solids().vals()
    except Exception:
        pass
    try:
        # CadQuery Shape (Solid, Compound)
        if hasattr(shape, "Solids") and callable(shape.Solids):
            return shape.Solids()
    except Exception:
        pass
    return []


def _get_volume(shape) -> float:
    """Workplane veya Shape'den hacmi al."""
    try:
        solid = shape.val()
        if hasattr(solid, "Volume"):
            return solid.Volume()
    except Exception:
        pass
    try:
        return shape.Volume()
    except Exception:
        pass
    return 0.0


def _get_occt_shape(shape):
    """Workplane veya Shape'den OCC shape (wrapped) al."""
    try:
        solid = shape.val()
        if hasattr(solid, "wrapped"):
            return solid.wrapped
    except Exception:
        pass
    try:
        if hasattr(shape, "wrapped"):
            return shape.wrapped
    except Exception:
        pass
    return None


def validate_solid_count(shape, expected: int = 1) -> CADValidationResult:
    """Model tek/beklenen sayıda solid mi?

    Args:
        shape: CadQuery Workplane veya shape.
        expected: Beklenen solid sayısı.
    """
    try:
        solids = _get_solids(shape)
        count = len(solids)
        return CADValidationResult(
            check_name="solid_count",
            passed=count == expected,
            message=f"Solid sayısı: {count} (beklenen: {expected})",
            expected=float(expected),
            actual=float(count),
        )
    except Exception as e:
        return CADValidationResult(
            check_name="solid_count",
            passed=False,
            message=f"Solid sayısı kontrolü başarısız: {e}",
        )


def validate_no_negative_volume(shape) -> CADValidationResult:
    """Negatif hacim oluşmuş mu?

    CadQuery/OCC'de negatif hacim boolean hatalarından kaynaklanabilir.
    """
    try:
        volume = _get_volume(shape)
        if volume > 0:
            return CADValidationResult(
                check_name="no_negative_volume",
                passed=True,
                message=f"Hacim: {volume:.2f} mm³ (pozitif)",
                actual=volume,
            )
        return CADValidationResult(
            check_name="no_negative_volume",
            passed=False,
            message=f"Hacim: {volume:.2f} mm³ (NEGATİF!)",
            actual=volume,
        )
    except Exception as e:
        return CADValidationResult(
            check_name="no_negative_volume",
            passed=False,
            message=f"Hacim kontrolü başarısız: {e}",
        )


def validate_no_open_shells(shape) -> CADValidationResult:
    """Açık kabuk / bozuk yüzey var mı?

    Basit kontrol: shape kapalı bir solid mi?
    """
    try:
        # CadQuery shape'in Closed() metodu varsa kullan
        try:
            solid = shape.val() if hasattr(shape, "val") else shape
            if hasattr(solid, "Closed"):
                is_closed = solid.Closed()
                return CADValidationResult(
                    check_name="no_open_shells",
                    passed=is_closed,
                    message=f"Geometri {'kapalı' if is_closed else 'AÇIK kabuk!'}",
                )
        except Exception:
            pass

        # Fallback: solid sayısı > 0 ise kapalı kabul et
        solids = _get_solids(shape)
        return CADValidationResult(
            check_name="no_open_shells",
            passed=len(solids) > 0,
            message=f"Solid sayısı: {len(solids)} (açık kabuk yok varsayımı)",
        )
    except Exception as e:
        return CADValidationResult(
            check_name="no_open_shells",
            passed=False,
            message=f"Açık kabuk kontrolü başarısız: {e}",
        )


def validate_volume_tolerance(
    calculated_volume: float,
    cad_volume: float,
    tolerance_pct: float = 5.0,
) -> CADValidationResult:
    """Hesaplanan iç hacim ↔ CAD hacmi tolerans içinde mi?

    Args:
        calculated_volume: Hesap motorundan gelen hacim (mm³).
        cad_volume: CAD modelinden ölçülen hacim (mm³).
        tolerance_pct: İzin verilen sapma yüzdesi (varsayılan %5).
    """
    if calculated_volume <= 0:
        return CADValidationResult(
            check_name="volume_tolerance",
            passed=False,
            message=f"Hesaplanan hacim geçersiz: {calculated_volume}",
        )

    diff_pct = abs(cad_volume - calculated_volume) / calculated_volume * 100.0
    passed = diff_pct <= tolerance_pct

    return CADValidationResult(
        check_name="volume_tolerance",
        passed=passed,
        message=(
            f"Hacim farkı: {diff_pct:.2f}% "
            f"(hesap: {calculated_volume:.0f}, CAD: {cad_volume:.0f}, "
            f"tolerans: %{tolerance_pct})"
        ),
        expected=calculated_volume,
        actual=cad_volume,
        tolerance_pct=tolerance_pct,
    )


__all__ = [
    "CADValidationResult",
    "CADValidationReport",
    "validate_solid_count",
    "validate_no_negative_volume",
    "validate_no_open_shells",
    "validate_volume_tolerance",
]
