"""Calc-core — CalculationResult ve Orchestrator testleri."""

import pytest

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus


class TestCalculationResult:
    """CalculationResult testleri."""

    def test_default_status_not_calculated(self):
        r = CalculationResult()
        assert r.status == CalculationStatus.NOT_CALCULATED

    def test_add_intermediate(self):
        r = CalculationResult()
        r.add_intermediate("PR", 1.2, "MPa", "Design pressure")
        assert len(r.intermediate_values) == 1
        assert r.intermediate_values[0]["name"] == "PR"
        assert r.intermediate_values[0]["value"] == 1.2

    def test_add_warning(self):
        r = CalculationResult()
        r.add_warning("Test warning")
        assert "Test warning" in r.warnings

    def test_add_assumption(self):
        r = CalculationResult()
        r.add_assumption("K4: User entered allowable stress")
        assert len(r.assumptions) == 1

    def test_set_pass(self):
        r = CalculationResult()
        r.set_pass(utilization=0.85)
        assert r.status == CalculationStatus.PASS
        assert r.utilization_ratio == 0.85

    def test_set_fail(self):
        r = CalculationResult()
        r.set_fail(utilization=1.15)
        assert r.status == CalculationStatus.FAIL
        assert r.utilization_ratio == 1.15

    def test_set_not_calculated(self):
        r = CalculationResult()
        r.set_not_calculated("Module not implemented")
        assert r.status == CalculationStatus.NOT_CALCULATED
        assert "Module not implemented" in r.warnings

    def test_set_out_of_scope(self):
        r = CalculationResult()
        r.set_out_of_scope("External pressure not supported")
        assert r.status == CalculationStatus.OUT_OF_SCOPE

    def test_set_review_required(self):
        r = CalculationResult()
        r.set_review_required("Unusual condition")
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert "Unusual condition" in r.assumptions

    def test_to_dict(self):
        r = CalculationResult(
            component_id="SHELL-01",
            component_type="shell",
            calculation_type="thickness",
            code="ASME VIII-1",
            edition="2025",
            clause_reference="UG-27(c)(1)",
        )
        r.set_pass(utilization=0.85)
        d = r.to_dict()
        assert d["component_id"] == "SHELL-01"
        assert d["status"] == "PASS"
        assert d["clause_reference"] == "UG-27(c)(1)"

    def test_full_traceability(self):
        """K5: Herhesap denetlenebilir olmalı — tüm alanlar dolu."""
        r = CalculationResult(
            component_id="SHELL-01",
            component_type="shell",
            calculation_type="thickness",
            code="ASME VIII-1",
            edition="2025",
            clause_reference="UG-27(c)(1)",
            formula_reference="UG-27(c)(1) Eq. (1)",
        )
        r.input_snapshot = {"P": 1.2, "D": 1000, "S": 138, "E": 1.0}
        r.material_properties_used = {"designation": "SA-516 Gr.70", "allowable_stress": 138}
        r.add_intermediate("PR", 1.2, "MPa", "Design pressure")
        r.add_intermediate("R", 500.0, "mm", "Inside radius")
        r.add_intermediate("S", 138.0, "MPa", "Allowable stress")
        r.add_intermediate("E", 1.0, "-", "Joint efficiency")
        r.add_intermediate("C", 2.0, "mm", "Corrosion allowance")
        r.add_intermediate("t_required", 6.38, "mm", "Required thickness")
        r.add_intermediate("t_mill", 0.875, "-", "Mill tolerance factor")
        r.add_intermediate("t_nominal", 7.29, "mm", "Nominal thickness required")
        r.final_result = 7.29
        r.final_result_unit = "mm"
        r.allowable_limit = 12.0
        r.allowable_limit_unit = "mm"
        r.set_pass(utilization=7.29 / 12.0)
        r.rounding_rule = "round_up_to_nearest_0.5"

        d = r.to_dict()
        assert d["code"] == "ASME VIII-1"
        assert d["clause_reference"] == "UG-27(c)(1)"
        assert len(d["intermediate_values"]) == 8
        assert d["final_result"] == 7.29
        assert d["status"] == "PASS"

    # ── §12.4 genişletme testleri ────────────────────────────────────────────

    def test_new_enum_values(self):
        """A1: Yeni CalculationStatus değerleri."""
        from domain.enums import CalculationStatus
        assert CalculationStatus.BLOCKED_CODE_DATA.value == "BLOCKED CODE DATA"
        assert CalculationStatus.BLOCKED_MISSING_INPUT.value == "BLOCKED MISSING INPUT"

    def test_new_field_defaults(self):
        """A1: §12.4 alanlarının default değerleri."""
        r = CalculationResult()
        assert r.engine_version == ""
        assert r.formula_key == ""
        assert r.load_case_id == ""
        assert r.reference_elevation_mm == 0.0
        assert r.input_snapshot_hash == ""
        assert r.governing is False
        assert r.verified_by is None
        assert r.created_at == ""
        assert r.validity_checks == []

    def test_set_blocked_code_data(self):
        """A1: set_blocked_code_data durumu."""
        r = CalculationResult()
        r.set_blocked_code_data("Chart data not available")
        assert r.status == CalculationStatus.BLOCKED_CODE_DATA
        assert "Chart data not available" in r.warnings

    def test_set_blocked_missing_input(self):
        """A1: set_blocked_missing_input durumu."""
        r = CalculationResult()
        r.set_blocked_missing_input("UG-34 C coefficient not provided")
        assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
        assert "UG-34 C coefficient not provided" in r.warnings

    def test_add_validity_check(self):
        """A1: add_validity_check metodu."""
        r = CalculationResult()
        r.add_validity_check("thickness_check", passed=True, limit=10.0, actual=8.5)
        assert len(r.validity_checks) == 1
        vc = r.validity_checks[0]
        assert vc["name"] == "thickness_check"
        assert vc["passed"] is True
        assert vc["limit"] == 10.0
        assert vc["actual"] == 8.5

    def test_to_dict_includes_new_fields(self):
        """A1: to_dict() yeni alanları içerir."""
        r = CalculationResult(
            engine_version="1.0.0",
            formula_key="UG-27-C1",
            load_case_id="LC-001",
            reference_elevation_mm=1500.0,
            governing=True,
            verified_by="engineer@example.com",
        )
        r.created_at = "2026-07-24T10:00:00+00:00"
        r.add_validity_check("test", passed=True)
        d = r.to_dict()
        assert d["engine_version"] == "1.0.0"
        assert d["formula_key"] == "UG-27-C1"
        assert d["load_case_id"] == "LC-001"
        assert d["reference_elevation_mm"] == 1500.0
        assert d["governing"] is True
        assert d["verified_by"] == "engineer@example.com"
        assert d["created_at"] == "2026-07-24T10:00:00+00:00"
        assert len(d["validity_checks"]) == 1

    def test_created_at_auto_fill(self):
        """A1: to_dict() çağrıldığında created_at otomatik doldurulur."""
        r = CalculationResult()
        assert r.created_at == ""
        d = r.to_dict()
        assert d["created_at"] != ""  # ISO-8601 formatında doldurulmalı
