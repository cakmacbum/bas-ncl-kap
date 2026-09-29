"""Yayın-öncesi doğrulama kapısı (validate_suite) üretim hattı bağlantısı.

Politika: `warnings` PASS'i geçersiz kılar; `notices` (bilgilendirme/güvenlik notu) kılmaz.
"""

import json
from pathlib import Path

import pytest

from calc_core import CalculationOrchestrator, validate_result, validate_suite
from calc_core.result import CalculationResult
from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain.project import VesselProject

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "vessel_project_five_component.json"


def _project_test_temp_equals_design() -> VesselProject:
    proj = VesselProject.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))
    dc = proj.design_conditions
    dc2 = dc.model_copy(update={"hydrotest_temperature": dc.design_temperature})
    return proj.model_copy(update={"design_conditions": dc2})


def test_full_run_with_pneumatic_notices_passes_gate():
    res = CalculationOrchestrator(ASMEVIII1DesignCode()).run(_project_test_temp_equals_design())
    report = validate_suite(res.results)
    assert report.passed is True, report.errors
    pneu = [r for r in res.results if r.calculation_type == "pneumatic_test"]
    assert pneu and all(len(r.notices) >= 2 for r in pneu)


def test_pass_with_real_warning_is_still_rejected():
    r = CalculationResult(component_id="X")
    r.final_result = 1.0
    r.set_pass()
    r.add_warning("gerçek uyarı")
    assert any("PASS" in e for e in validate_result(r))
    assert validate_suite([r]).passed is False


def test_pass_with_notice_only_is_accepted():
    r = CalculationResult(component_id="X")
    r.final_result = 1.0
    r.set_pass()
    r.add_notice("bilgi")
    assert validate_result(r) == []


def test_notices_serialized():
    r = CalculationResult(component_id="X")
    r.add_notice("not-1")
    d = r.to_dict()
    assert d["notices"] == ["not-1"]
    assert d["warnings"] == []
