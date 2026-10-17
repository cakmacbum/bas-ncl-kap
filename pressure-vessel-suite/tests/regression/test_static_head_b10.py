"""B-10 regresyon: statik kafa düzeltmesi ölü kod olmamalı, atlama sessiz olmamalı."""
from __future__ import annotations

import pytest

from calc_core.orchestrator import CalculationOrchestrator, OrchestratorResult
from calc_core.result import CalculationResult
from code_asme_viii_1 import ASMEVIII1DesignCode
from domain import CalculationCode, DesignConditions, VesselProject

G = 9.80665


def _project(rho: float) -> VesselProject:
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=200.0, design_temperature=200.0,
        minimum_design_temperature=-10.0, fluid_density_kg_m3=rho,
    )
    return VesselProject(
        project_number="T", project_name="T", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc,
    )


def _orch() -> CalculationOrchestrator:
    return CalculationOrchestrator(ASMEVIII1DesignCode())


def _mawp(elev: float = 0.0) -> CalculationResult:
    r = CalculationResult(component_type="shell", calculation_type="mawp",
                          code="ASME", edition="2025", reference_elevation_mm=elev)
    r.final_result = 2.0
    r.final_result_unit = "MPa"
    r.set_pass()
    return r


def test_kot_var_mawp_dusuyor():
    res = OrchestratorResult()
    r = _mawp(elev=3000.0)
    res.add(r)
    _orch()._apply_static_head_correction(_project(1000.0), res)
    expected = 2.0 - 1000.0 * G * 3.0 * 1e-6
    assert r.final_result == pytest.approx(expected, rel=1e-12)
    names = {iv["name"] for iv in r.intermediate_values}
    assert {"static_head_delta_P", "MAWP_corrected"} <= names


def test_kot_yok_yogunluk_var_uyari_ve_mawp_ayni():
    res = OrchestratorResult()
    r = _mawp(elev=0.0)
    res.add(r)
    _orch()._apply_static_head_correction(_project(1000.0), res)
    assert r.final_result == 2.0
    assert any("Statik kafa uygulanmadı" in a for a in r.assumptions)


def test_yogunluk_sifir_eski_davranis():
    res = OrchestratorResult()
    r = _mawp(elev=3000.0)
    res.add(r)
    _orch()._apply_static_head_correction(_project(0.0), res)
    assert r.final_result == 2.0
    assert any("Akışkan yoğunluğu girilmedi" in a for a in r.assumptions)
    assert not any("Statik kafa uygulanmadı" in a for a in r.assumptions)
