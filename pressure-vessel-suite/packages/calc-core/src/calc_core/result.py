"""CalculationResult — izlenebilir hesap sonucu nesnesi (kaynak §7).

K5 kuralı: Her hesap denetlenebilir olmalı. Sonuç sadece "12 mm yeterli" değil;
ara değerler + madde referansı + malzeme gerilmesi + standart sürümü saklanır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from domain.enums import CalculationStatus


@dataclass
class CalculationResult:
    """Tek bir hesap adımının izlenebilir sonucu.

    Her hesap metodu bu nesneyi döndürür. İçerir:
    - Hangi standart maddesine dayandığı (clause_reference)
    - Formül referansı (formula_reference)
    - Girdi anlık görüntüsü (input_snapshot)
    - Kullanılan malzeme özellikleri (material_properties_used)
    - Ara değerler (intermediate_values)
    - Nihai sonuç (final_result)
    - İzin verilen sınır (allowable_limit)
    - Kullanım oranı (utilization_ratio)
    - Durum (PASS / FAIL / REVIEW_REQUIRED / NOT_CALCULATED / OUT_OF_SCOPE)
    - Uyarılar ve varsayımlar
    """

    calculation_id: str = field(default_factory=lambda: str(uuid4())[:8])
    component_id: str = ""
    component_type: str = ""  # "shell", "head", "nozzle" vb.
    calculation_type: str = ""  # "thickness", "mawp", "hydrotest" vb.

    code: str = ""  # "ASME VIII-1", "EN 13445"
    edition: str = ""  # "2025", "2021+A1:2023"

    clause_reference: str = ""  # "UG-27(c)(1)"
    formula_reference: str = ""  # "UG-27(c)(1) Eq. (1)"

    input_snapshot: Dict[str, Any] = field(default_factory=dict)
    material_properties_used: Dict[str, Any] = field(default_factory=dict)

    intermediate_values: List[Dict[str, Any]] = field(default_factory=list)

    final_result: Optional[float] = None
    final_result_unit: str = ""  # "mm", "MPa" vb.
    allowable_limit: Optional[float] = None
    allowable_limit_unit: str = ""

    utilization_ratio: Optional[float] = None  # final_result / allowable_limit

    status: CalculationStatus = CalculationStatus.NOT_CALCULATED

    warnings: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    rounding_rule: str = ""

    # §12.4 genişletme alanları
    engine_version: str = ""
    formula_key: str = ""
    load_case_id: str = ""
    reference_elevation_mm: float = 0.0
    input_snapshot_hash: str = ""
    governing: bool = False
    verified_by: Optional[str] = None
    created_at: str = ""  # ISO-8601, to_dict() tarafından otomatik doldurulur
    validity_checks: List[Dict[str, Any]] = field(default_factory=list)

    def add_intermediate(self, name: str, value: Any, unit: str = "", description: str = "") -> None:
        """Ara değer ekle (K5 — izlenebilirlik)."""
        self.intermediate_values.append({
            "name": name,
            "value": value,
            "unit": unit,
            "description": description,
        })

    def add_warning(self, warning: str) -> None:
        """Uyarı ekle."""
        self.warnings.append(warning)

    def add_assumption(self, assumption: str) -> None:
        """Varsayım ekle (K4 — varsayımları gizleme)."""
        self.assumptions.append(assumption)

    def set_pass(self, utilization: Optional[float] = None) -> None:
        """PASS durumunu ayarla."""
        self.status = CalculationStatus.PASS
        if utilization is not None:
            self.utilization_ratio = utilization

    def set_fail(self, utilization: Optional[float] = None) -> None:
        """FAIL durumunu ayarla."""
        self.status = CalculationStatus.FAIL
        if utilization is not None:
            self.utilization_ratio = utilization

    def set_not_calculated(self, reason: str = "") -> None:
        """NOT_CALCULATED durumunu ayarla."""
        self.status = CalculationStatus.NOT_CALCULATED
        if reason:
            self.add_warning(reason)

    def set_out_of_scope(self, reason: str = "") -> None:
        """OUT_OF_SCOPE durumunu ayarla."""
        self.status = CalculationStatus.OUT_OF_SCOPE
        if reason:
            self.add_warning(reason)

    def set_review_required(self, reason: str = "") -> None:
        """REVIEW_REQUIRED durumunu ayarla."""
        self.status = CalculationStatus.REVIEW_REQUIRED
        if reason:
            self.add_assumption(reason)

    def set_blocked_code_data(self, reason: str = "") -> None:
        """BLOCKED_CODE_DATA durumunu ayarla — lisanslı veri eksik (K6)."""
        self.status = CalculationStatus.BLOCKED_CODE_DATA
        if reason:
            self.add_warning(reason)

    def set_blocked_missing_input(self, reason: str = "") -> None:
        """BLOCKED_MISSING_INPUT durumunu ayarla — zorunlu girdi eksik."""
        self.status = CalculationStatus.BLOCKED_MISSING_INPUT
        if reason:
            self.add_warning(reason)

    def add_validity_check(self, name: str, passed: bool, limit: Any = None, actual: Any = None) -> None:
        """Geçerlilik kontrolü ekle."""
        self.validity_checks.append({
            "name": name,
            "passed": passed,
            "limit": limit,
            "actual": actual,
        })

    def _ensure_created_at(self) -> None:
        """created_at boşsa otomatik doldur."""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serileştirme için dict'e çevir."""
        self._ensure_created_at()
        return {
            "calculation_id": self.calculation_id,
            "component_id": self.component_id,
            "component_type": self.component_type,
            "calculation_type": self.calculation_type,
            "code": self.code,
            "edition": self.edition,
            "clause_reference": self.clause_reference,
            "formula_reference": self.formula_reference,
            "input_snapshot": self.input_snapshot,
            "material_properties_used": self.material_properties_used,
            "intermediate_values": self.intermediate_values,
            "final_result": self.final_result,
            "final_result_unit": self.final_result_unit,
            "allowable_limit": self.allowable_limit,
            "allowable_limit_unit": self.allowable_limit_unit,
            "utilization_ratio": self.utilization_ratio,
            "status": self.status.value,
            "warnings": self.warnings,
            "assumptions": self.assumptions,
            "rounding_rule": self.rounding_rule,
            # §12.4 genişletme alanları
            "engine_version": self.engine_version,
            "formula_key": self.formula_key,
            "load_case_id": self.load_case_id,
            "reference_elevation_mm": self.reference_elevation_mm,
            "input_snapshot_hash": self.input_snapshot_hash,
            "governing": self.governing,
            "verified_by": self.verified_by,
            "created_at": self.created_at,
            "validity_checks": self.validity_checks,
        }


__all__ = ["CalculationResult"]
