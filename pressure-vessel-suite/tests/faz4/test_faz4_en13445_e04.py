"""E04 — EN 13445: Madde 6 f_d/f_test, test grubu → z (5.6), EN-5 hidro/pnömatik test,
EN tahliye satırı (ASME UG-125 etiketi yok). verified=False → olumlu sonuç en fazla
REVIEW_REQUIRED. Beklenen değerler elle hesaplandı (yorumlarda).
"""

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_en_13445 import EN13445DesignCode
from code_en_13445 import formulas as F
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty, ProductForm,
    ShellSection, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus as S
from pressure_relief.models import PressureReliefDevice, PressureReliefSystem

EN = EN13445DesignCode(edition="2021+A1:2023")


def _mat(**kw):
    base = dict(material_id="M", standard_pack="EN 10028-3", material_designation="P355NH",
                product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=163.0,
                yield_strength=255.0, tensile_strength=490.0, source_reference="t")
    base.update(kw)
    return MaterialProperty(**base)


def _dc(**kw):
    base = dict(operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
                operating_temperature=150.0, design_temperature=200.0,
                minimum_design_temperature=-10.0, hydrotest_temperature=200.0)
    base.update(kw)
    return DesignConditions(**base)


def _project(mat=None, weld=None, dc=None, relief=None):
    return VesselProject(
        project_number="E04", project_name="e04", calculation_code=CalculationCode.EN_13445,
        code_edition="2021", design_conditions=dc or _dc(),
        shell_sections=[ShellSection(section_id="S", inside_diameter=1000.0, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
        heads=[Head(head_id="H", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
        welds=[weld or WeldJoint(joint_id="WJ", joint_type="longitudinal")],
        materials=[mat or _mat()],
        pressure_relief=relief,
    )


def _iv(r, name):
    return next(v["value"] for v in r.intermediate_values if v["name"] == name)


# ── Madde 6 formülleri (el hesabı) ──────────────────────────────────────────

@pytest.mark.parametrize("group,props,f_d,f_t", [
    # min(255/1,5=170 ; 490/2,4=204,17) = 170 ; test 355/1,05 = 338,10
    ("ferritic", {"rp02_t": 255, "rm_20": 490, "rp02_test": 355}, 170.0, 355 / 1.05),
    # 200/1,5 = 133,33 ; test 260/1,05 = 247,62
    ("austenitic_a30", {"rp10_t": 200, "rp10_test": 260}, 200 / 1.5, 260 / 1.05),
    # max(133,33 ; min(166,67 ; 450/3=150)) = 150 ; test max(250/1,05=238,10 ; 520/2=260) = 260
    ("austenitic_a35", {"rp10_t": 200, "rm_t": 450, "rp10_test": 250, "rm_test": 520}, 150.0, 260.0),
    # min(240/1,9=126,32 ; 450/3=150) = 126,32 ; test 240/1,33 = 180,45
    ("cast", {"rp02_t": 240, "rm_20": 450, "rp02_test": 240}, 240 / 1.9, 240 / 1.33),
])
def test_nominal_stress_formulas(group, props, f_d, f_t):
    assert F.nominal_design_stress(group, props)[0] == pytest.approx(f_d, rel=1e-12)
    assert F.nominal_test_stress(group, props)[0] == pytest.approx(f_t, rel=1e-12)


def test_austenitic_a35_low_rm_falls_back_to_rp_over_1_5():
    # min(200/1,2=166,7 ; 360/3=120) = 120 < 133,3 → f = 133,3
    assert F.nominal_design_stress("austenitic_a35", {"rp10_t": 200, "rm_t": 360})[0] == pytest.approx(200 / 1.5)


@pytest.mark.parametrize("group,z", [("1a", 1.0), ("1", 1.0), ("2b", 1.0), ("3a", 0.85), ("3b", 0.85), ("4", 0.7)])
def test_testing_group_to_z(group, z):
    assert F.joint_coefficient_for_testing_group(group) == z


def test_testing_group_unknown_raises():
    with pytest.raises(ValueError):
        F.joint_coefficient_for_testing_group("5")


def test_test_pressure_formulas():
    assert F.en_hydrotest_pressure(1.2, 1.5, 1.0)[:2] == (pytest.approx(2.145), "PS")
    assert F.en_hydrotest_pressure(2.0, 1.5, 1.0)[:2] == (pytest.approx(2.5), "design_pressure")
    assert F.en_pneumatic_test_pressure(1.2, 1.25, 1.1) == pytest.approx(1.65)  # 1,1·1,2·1,25


# ── Malzeme satırı (nominal_design_stress) ──────────────────────────────────

def _stress_row(mat, dc=None):
    rows = EN.check_material_design_stress(_project(mat=mat, dc=dc))
    assert len(rows) == 1 and rows[0].calculation_type == "nominal_design_stress"
    assert rows[0].clause_reference.startswith("EN 13445-3, 6")
    return rows[0]


def test_material_without_group_is_blocked():
    r = _stress_row(_mat())
    assert r.status == S.BLOCKED_MISSING_INPUT and "en_material_group" in " ".join(r.warnings)


def test_ferritic_entered_f_within_limit_is_review_not_pass():
    # yield 255 @200 °C = Rp0,2/T (varsayım); f_d = min(170 ; 204,17) = 170 ≥ 163
    r = _stress_row(_mat(en_material_group="ferritic", en_rp02_test=355.0))
    assert r.status == S.REVIEW_REQUIRED
    assert _iv(r, "f_d") == pytest.approx(170.0)
    assert _iv(r, "f_test") == pytest.approx(355 / 1.05)
    assert r.utilization_ratio == pytest.approx(163 / 170)
    assert any("Rp0,2/T kabul edildi" in a for a in r.assumptions)


def test_ferritic_entered_f_above_limit_fails():
    r = _stress_row(_mat(en_material_group="ferritic", allowable_stress=180.0))
    assert r.status == S.FAIL and r.allowable_limit == pytest.approx(170.0)
    assert any("f_test hesaplanmadı" in w for w in r.warnings)


def test_ferritic_without_rp_at_design_temperature_is_blocked():
    # malzeme verisi 20 °C beyanlı, tasarım 200 °C → yield Rp0,2/T yerine kullanılmaz
    r = _stress_row(_mat(en_material_group="ferritic", temperature=20.0))
    assert r.status == S.BLOCKED_MISSING_INPUT and "en_rp02_t" in " ".join(r.warnings)


def test_austenitic_requires_rp10_and_elongation():
    r = _stress_row(_mat(en_material_group="austenitic_a30"))
    assert r.status == S.BLOCKED_MISSING_INPUT and "en_elongation_a_pct" in " ".join(r.warnings)
    r = _stress_row(_mat(en_material_group="austenitic_a30", en_elongation_a_pct=40.0))
    assert r.status == S.BLOCKED_MISSING_INPUT and "en_rp10_t" in " ".join(r.warnings)
    r = _stress_row(_mat(en_material_group="austenitic_a35", en_elongation_a_pct=32.0,
                         en_rp10_t=200.0, en_rm_t=450.0))
    assert r.status == S.BLOCKED_MISSING_INPUT and "A ≥ %35" in " ".join(r.warnings)


def test_austenitic_a35_hand_calc():
    r = _stress_row(_mat(en_material_group="austenitic_a35", en_elongation_a_pct=40.0,
                         en_rp10_t=200.0, en_rm_t=450.0, allowable_stress=150.0))
    assert _iv(r, "f_d") == pytest.approx(150.0)
    assert r.status == S.REVIEW_REQUIRED


# ── Test grubu → z (5.6) ────────────────────────────────────────────────────

def _shell(weld):
    p = _project(weld=weld)
    return EN.calculate_shell_thickness({
        "shell": p.shell_sections[0], "design_conditions": p.design_conditions,
        "materials": p.materials, "welds": p.welds})


def test_testing_group_3_limits_z_in_shell_calc():
    r = _shell(WeldJoint(joint_id="WJ", joint_type="longitudinal", joint_coefficient=1.0,
                         en_testing_group="3a"))
    assert _iv(r, "z") == 0.85
    # e = P·R/(fz − P/2) = 1,2·500/(163·0,85 − 0,6) = 600/137,95
    assert _iv(r, "e_circ") == pytest.approx(600 / (163 * 0.85 - 0.6), rel=1e-12)
    assert any("test grubu 3a" in w for w in r.warnings)


def test_testing_group_does_not_raise_lower_entered_z():
    r = _shell(WeldJoint(joint_id="WJ", joint_type="longitudinal", joint_coefficient=0.7,
                         en_testing_group="1a"))
    assert _iv(r, "z") == 0.7


def test_weld_validation_rows():
    over = EN.validate_welds(_project(weld=WeldJoint(
        joint_id="WJ", joint_type="longitudinal", joint_coefficient=1.0, en_testing_group="4")))[0]
    assert over.status == S.REVIEW_REQUIRED and over.allowable_limit == 0.7
    assert any("0.7" in w for w in over.warnings)
    ok = EN.validate_welds(_project(weld=WeldJoint(
        joint_id="WJ", joint_type="longitudinal", joint_coefficient=0.85, en_testing_group="3b")))[0]
    assert ok.status == S.REVIEW_REQUIRED and ok.utilization_ratio == pytest.approx(1.0)
    none = EN.validate_welds(_project())[0]
    assert none.status == S.NOT_CALCULATED and any("test grubu girilmedi" in a for a in none.assumptions)


# ── Pnömatik test ───────────────────────────────────────────────────────────

def _pneu(dc, mat=None):
    p = _project(mat=mat, dc=dc)
    return EN.calculate_pneumatic_test_pressure({
        "project": p, "design_conditions": dc, "materials": p.materials})


def test_pneumatic_without_factor_blocked():
    r = _pneu(_dc())
    assert r.status == S.BLOCKED_CODE_DATA and r.final_result is None
    assert "UG-100" not in (r.clause_reference or "")


def test_pneumatic_same_temperature_hand_calc():
    r = _pneu(_dc(en_pneumatic_test_factor=1.1))
    assert r.final_result == pytest.approx(1.1 * 1.2)  # k·Pd·1
    assert r.status == S.REVIEW_REQUIRED


def test_pneumatic_ratio_hand_calc_and_missing_ratio():
    dc = _dc(en_pneumatic_test_factor=1.1, hydrotest_temperature=20.0)
    assert _pneu(dc).status == S.BLOCKED_MISSING_INPUT
    r = _pneu(dc, _mat(allowable_stress_test_temp=163.0 * 1.2))
    assert r.final_result == pytest.approx(1.1 * 1.2 * 1.2)  # 1,584
    assert r.status == S.REVIEW_REQUIRED


# ── Tahliye: ASME UG-125 hesabı EN adı altında yok ──────────────────────────

def test_en_relief_is_not_asme_calculation():
    relief = PressureReliefSystem(enabled=True, devices=[PressureReliefDevice(
        device_id="PSV-1", device_type="safety_valve", set_pressure_mpa=1.0)])
    rows = EN.check_pressure_relief(_project(relief=relief), 2.0)
    assert [r.status for r in rows] == [S.NOT_CALCULATED]
    assert "UG-" not in rows[0].clause_reference and rows[0].final_result is None
    none = EN.check_pressure_relief(_project(), None)
    assert none[0].status == S.OUT_OF_SCOPE and "UG-" not in none[0].clause_reference


# ── Orkestratör: satırlar raporda, hata yok, madde no'lar güncel ────────────

def test_orchestrator_en_rows_and_clauses():
    res = CalculationOrchestrator(EN).run(_project(mat=_mat(en_material_group="ferritic")))
    assert not res.errors
    types = {r.calculation_type for r in res.results}
    assert {"nominal_design_stress", "pneumatic_test", "weld_validation", "pressure_relief"} <= types
    clauses = {r.clause_reference for r in res.results if r.calculation_type in ("thickness", "mawp")}
    assert clauses == {"EN 13445-3, 7.4.2", "EN 13445-3, 7.5.2"}
    assert not [r for r in res.results if "UG-" in (r.clause_reference or "")]
