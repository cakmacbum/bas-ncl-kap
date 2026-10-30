"""P06 — kaldırma kulağı: formül elle doğrulama + hat entegrasyonu."""
import math

import pytest
from pydantic import ValidationError

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty,
    ProductForm, ShellSection, VesselProject,
)
from domain.enums import CalculationStatus
from domain.lifting_lug import LiftingLugSpec
from supports.lifting_lug import GRAVITY_M_S2, evaluate_lifting_lug

LUG = dict(
    lug_count=2, location="shell_top", plate_thickness_mm=20, plate_width_mm=150,
    hole_diameter_mm=50, edge_distance_mm=75, hole_height_mm=100, base_width_mm=150,
    weld_length_mm=400, weld_leg_mm=10, lift_angle_deg=0, impact_factor=2.0,
    yield_strength_MPa=250,
)


def _project(lug=None):
    return VesselProject(
        project_number="LUG-1", project_name="lug", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
            operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id="H", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="M")],
        shell_sections=[ShellSection(section_id="S", inside_diameter=1000.0,
                                     tangent_length=2000.0, nominal_thickness=12.0, material_id="M")],
        materials=[MaterialProperty(
            material_id="M", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
            yield_strength=260.0, tensile_strength=485.0, source_reference="t")],
        lifting_lugs=lug,
    )


def test_hand_calc_vertical_sling():
    spec = LiftingLugSpec(**LUG)
    r = evaluate_lifting_lug(spec, 1000.0, 12.0, 138.0)
    Pv = 1000 * GRAVITY_M_S2 * 2.0 / 2
    c = {x.name: x for x in r.checks}
    assert r.vertical_per_lug_N == pytest.approx(Pv)
    assert r.horizontal_per_lug_N == pytest.approx(0.0, abs=1e-9)
    assert c["lug_tension"].stress_MPa == pytest.approx(Pv / (100 * 20))
    assert c["lug_shear"].stress_MPa == pytest.approx(Pv / (2 * 75 * 20))
    assert c["lug_bearing"].stress_MPa == pytest.approx(Pv / (50 * 20))
    assert c["lug_weld"].stress_MPa == pytest.approx(Pv / (0.707 * 10 * 400))
    assert c["lug_weld"].allowable_MPa == pytest.approx(0.3 * 482)
    assert all(not x.verified for x in r.checks)


def test_sling_angle_increases_load_and_adds_moment():
    a0 = evaluate_lifting_lug(LiftingLugSpec(**LUG), 1000.0, 12.0, 138.0)
    a45 = evaluate_lifting_lug(LiftingLugSpec(**{**LUG, "lift_angle_deg": 45}), 1000.0, 12.0, 138.0)
    assert a45.load_per_lug_N == pytest.approx(a0.load_per_lug_N / math.cos(math.radians(45)))
    assert a45.horizontal_per_lug_N == pytest.approx(a45.vertical_per_lug_N)
    w0 = {x.name: x for x in a0.checks}["lug_weld"].stress_MPa
    w45 = {x.name: x for x in a45.checks}["lug_weld"].stress_MPa
    assert w45 > w0


def test_four_lugs_only_two_effective():
    r = evaluate_lifting_lug(LiftingLugSpec(**{**LUG, "lug_count": 4}), 1000.0, 12.0, 138.0)
    assert r.effective_lugs == 2


@pytest.mark.parametrize("bad", [
    {"hole_diameter_mm": 150}, {"edge_distance_mm": 20}, {"lift_angle_deg": 90},
    {"impact_factor": 0.5}, {"lug_count": 0}, {"weld_leg_mm": 0},
])
def test_invalid_input_rejected(bad):
    with pytest.raises(ValidationError):
        LiftingLugSpec(**{**LUG, **bad})


def test_no_lug_input_no_results():
    assert ASMEVIII1DesignCode().check_lifting_lugs(_project()) == []


def test_pipeline_results_and_fail_on_overload():
    res = ASMEVIII1DesignCode().check_lifting_lugs(_project(LiftingLugSpec(**LUG)))
    assert {r.calculation_type for r in res} == {
        "lug_tension", "lug_shear", "lug_bearing", "lug_weld", "lug_shell_local_shear"}
    assert all(r.status == CalculationStatus.REVIEW_REQUIRED for r in res)
    weak = ASMEVIII1DesignCode().check_lifting_lugs(
        _project(LiftingLugSpec(**{**LUG, "impact_factor": 200.0})))
    assert any(r.status == CalculationStatus.FAIL for r in weak)


def test_unresolved_host_is_blocked():
    res = ASMEVIII1DesignCode().check_lifting_lugs(
        _project(LiftingLugSpec(**{**LUG, "host_component_id": "YOK"})))
    assert res[0].status == CalculationStatus.BLOCKED_MISSING_INPUT
