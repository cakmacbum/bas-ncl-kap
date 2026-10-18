"""K3: UG-37(a) E1 ve UCS-66 coincident stress ratio (bağımsız beklenen değerler)."""
from types import SimpleNamespace

import pytest

from mdmt import MDMTCalculator, UCS66CurveGroup
from nozzles.reinforcement import NozzleReinforcementInput, calculate_reinforcement


def _nozzle(**kw):
    base = dict(
        nozzle_tag="N1", nozzle_inside_diameter=154.1, nozzle_outside_diameter=168.3,
        nozzle_neck_thickness=7.1, nozzle_corrosion_allowance=1.0,
        nozzle_allowable_stress=138.0, component_inside_diameter=1000.0,
        component_nominal_thickness=12.0, component_corrosion_allowance=2.0,
        component_required_thickness=6.97, component_allowable_stress=138.0,
        design_pressure=1.2, design_temperature=200.0,
    )
    base.update(kw)
    return NozzleReinforcementInput(**base)


def _a1(res):
    return next(a for a in res.available_areas if a.name == "A1").area_mm2


def test_e1_default_is_one_with_k4_warning():
    res = calculate_reinforcement(_nozzle())
    # d=156.1, t=10, tr=6.97, fr1=1 -> A1 = 156.1*(10-6.97)
    assert _a1(res) == pytest.approx(156.1 * 3.03, rel=1e-6)
    assert any("E1=1 varsayıldı" in w for w in res.warnings)


def test_e1_less_than_one_reduces_a1_ug37a():
    res = calculate_reinforcement(_nozzle(opening_weld_joint_efficiency=0.85))
    assert _a1(res) == pytest.approx(156.1 * (0.85 * 10 - 6.97), rel=1e-6)
    assert not any("E1=1 varsayıldı" in w for w in res.warnings)
    # A_required E1'den etkilenmez (tr dikişsiz kabuk için E=1, B-07)
    assert res.required_area == pytest.approx(156.1 * 6.97, rel=1e-6)


def test_e1_invalid_fails():
    res = calculate_reinforcement(_nozzle(opening_weld_joint_efficiency=1.2))
    assert res.status.value == "FAIL"


def _mdmt(ratio):
    comp = SimpleNamespace(section_id="S1", material_id="M1")
    dc = SimpleNamespace(minimum_design_temperature=-20.0)
    return MDMTCalculator().check_mdmt({
        "component": comp, "design_conditions": dc, "materials": [],
        "curve_group": UCS66CurveGroup.B, "nominal_thickness_mm": 20.0,
        "impact_test_temperature_C": None, "coincident_stress_ratio": ratio,
    })


def test_mdmt_ratio_recorded_not_applied():
    r = _mdmt(0.5)
    assert r.final_result == -29.0  # azaltma uygulanmadı (K6)
    assert r.input_snapshot["coincident_stress_ratio"] == 0.5
    assert any("uygulanmadı" in w for w in r.warnings)
    assert r.status.value != "PASS"


def test_mdmt_ratio_missing_warns_and_invalid_blocks():
    assert any("girilmedi" in w for w in _mdmt(None).warnings)
    assert _mdmt(1.5).status.value.startswith("BLOCKED")
