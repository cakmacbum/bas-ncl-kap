"""P08 — App. 1-5 koni birleşimi takviyesi + etek taban halkası/ankraj.

Beklentiler el hesabıdır (formülden bağımsız).
"""

import math

import pytest

from code_asme_viii_1 import appendix_1_5 as a15
from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationCode, ComponentReference, Cone, DesignConditions, Head, HeadType, Junction,
    MaterialProperty, ProductForm, ShellSection, Support, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus
from domain.cone_base import ConeBaseInputs, ConeJunctionDesign, SkirtBaseRingInput
from supports import skirt_base_ring as sbr


# ── Appendix 1-5 saf formüller ───────────────────────────────────────────────

def test_required_ring_area_hand_calc():
    # P=1 MPa, R=500, alpha=20 deg, SE=120 MPa, Delta=0
    Q, A_r = a15.required_ring_area(1.0, 500.0, 20.0, 120.0, 0.0)
    assert Q == pytest.approx(250.0)
    assert A_r == pytest.approx(250.0 * 500.0 * math.tan(math.radians(20)) / 120.0)  # ~379 mm2
    _, A_half = a15.required_ring_area(1.0, 500.0, 20.0, 120.0, 10.0)
    assert A_half == pytest.approx(A_r * 0.5)
    _, A_zero = a15.required_ring_area(1.0, 500.0, 20.0, 120.0, 25.0)
    assert A_zero == 0.0


def test_effective_width():
    assert a15.effective_width(500.0, 10.0) == pytest.approx(0.78 * math.sqrt(5000.0))
    assert a15.effective_width(500.0, 10.0, 60.0) == pytest.approx(0.78 * math.sqrt(10000.0))


# ── Proje üzerinden junction ─────────────────────────────────────────────────

def _mat():
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4", density=7850.0,
    )


def _project(cone_t=8.0, cone_base=None, supports=None, alpha=20.0):
    return VesselProject(
        project_number="P08", project_name="Cone", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
            operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="MAT-01"),
               Head(head_id="HR", type=HeadType.HEMISPHERICAL, inside_diameter=600.0,
                    nominal_thickness=12.0, material_id="MAT-01")],
        shell_sections=[
            ShellSection(section_id="S1", inside_diameter=1000.0, tangent_length=1000.0,
                         nominal_thickness=10.0, material_id="MAT-01"),
            ShellSection(section_id="S2", inside_diameter=600.0, tangent_length=1000.0,
                         nominal_thickness=10.0, material_id="MAT-01")],
        cones=[Cone(cone_id="C1", large_diameter=1000.0, small_diameter=600.0,
                    half_apex_angle=alpha, length=500.0, nominal_thickness=cone_t,
                    material_id="MAT-01")],
        component_sequence=[
            ComponentReference(component_type="head", component_id="HL"),
            ComponentReference(component_type="shell", component_id="S1"),
            ComponentReference(component_type="cone", component_id="C1"),
            ComponentReference(component_type="shell", component_id="S2"),
            ComponentReference(component_type="head", component_id="HR")],
        junctions=[Junction(junction_id="J1", left_component_id="S1", right_component_id="C1",
                            junction_type="cone_to_shell", cone_end="large",
                            weld_joint_id="W1", weld_efficiency=1.0)],
        welds=[WeldJoint(joint_id="W1", joint_type="circumferential", joint_efficiency=1.0)],
        materials=[_mat()], supports=supports or [], cone_base=cone_base,
    )


def _junction_result(project):
    return ASMEVIII1DesignCode().check_junctions(project)[0]


def test_junction_calculates_ring_area():
    r = _junction_result(_project())
    vals = {v["name"]: v["value"] for v in r.intermediate_values}
    assert "A_r" in vals and "A_e" in vals
    # el hesabı: P=1,2; R_c = 500 (korozyon yok); alpha 20; SE = 138
    assert vals["A_r"] == pytest.approx(1.2 * 500 / 2 * 500 * math.tan(math.radians(20)) / 138.0, rel=1e-6)
    assert r.status in (CalculationStatus.REVIEW_REQUIRED, CalculationStatus.FAIL)


def test_junction_delta_reduces_area_and_thin_cone_fails():
    base = _junction_result(_project())
    with_delta = _junction_result(_project(cone_base=ConeBaseInputs(
        junctions=[ConeJunctionDesign(junction_id="J1", delta_deg=10.0)])))
    a0 = next(v["value"] for v in base.intermediate_values if v["name"] == "A_r")
    a1 = next(v["value"] for v in with_delta.intermediate_values if v["name"] == "A_r")
    assert a1 == pytest.approx(a0 * 0.5)
    assert any("Delta = 0" in a for a in base.assumptions)
    assert not any("Delta = 0" in a for a in with_delta.assumptions)


def test_junction_above_30_deg_out_of_scope():
    r = _junction_result(_project(alpha=35.0))
    assert r.status in (CalculationStatus.OUT_OF_SCOPE, CalculationStatus.BLOCKED_MISSING_INPUT)


# ── Taban halkası ────────────────────────────────────────────────────────────

def _ring(**kw):
    d = dict(ring_outer_diameter_mm=1300.0, ring_inner_diameter_mm=900.0, ring_thickness_mm=30.0,
             ring_yield_MPa=250.0, bolt_circle_diameter_mm=1200.0, bolt_count=12,
             bolt_diameter_mm=30.0, bolt_allowable_tension_MPa=140.0,
             bolt_allowable_shear_MPa=80.0, concrete_fc_MPa=25.0)
    d.update(kw)
    return SkirtBaseRingInput(**d)


def test_section_no_moment_is_uniform():
    A = math.pi * (650.0**2 - 450.0**2)
    s = sbr.solve_ring_section(1.0e6, 0.0, 650.0, 450.0, 600.0, 12, 500.0, 8.0)
    assert s["fc_max"] == pytest.approx(1.0e6 / A)
    assert s["sigma_bolt_max"] == 0.0


def test_section_equilibrium_with_bolt_tension():
    W, M = 4.0e5, 6.0e8
    r_o, r_i, R_b, N, A_b, n = 650.0, 450.0, 600.0, 12, 500.0, 8.0
    s = sbr.solve_ring_section(W, M, r_o, r_i, R_b, N, A_b, n)
    assert s["tension"] and s["sigma_bolt_max"] > 0
    c, xna = s["c"], s["x_na"]
    C = sum(c * (x - xna) * dA for x, dA in sbr._concrete_strips(r_o, r_i) if x > xna)
    xb = sbr._bolt_positions(R_b, N, 0.0)
    T = sum(n * c * (xna - x) * A_b for x in xb if x < xna)
    Mom = sum(c * (x - xna) * x * dA for x, dA in sbr._concrete_strips(r_o, r_i) if x > xna) \
        + sum(n * c * (xna - x) * A_b * (-x) for x in xb if x < xna)
    assert C - T == pytest.approx(W, rel=1e-6)
    assert Mom == pytest.approx(M, rel=1e-6)


def _support_result(ring, M_load=True):
    sk = Support(support_id="SK", type="skirt", host_component_id="S1", location_mm=0.0,
                 width_mm=200.0, height_mm=1500.0, diameter_mm=1024.0, thickness_mm=10.0,
                 material_id="MAT-01", overturning_moment_Nmm=5.0e8 if M_load else 0.0)
    p = _project(supports=[sk], cone_base=ConeBaseInputs(skirt_base_ring=ring))
    return [r for r in ASMEVIII1DesignCode().check_supports(p)
            if r.calculation_type == "skirt_base_ring"][0]


def test_base_ring_in_support_results():
    r = _support_result(_ring())
    assert r.status in (CalculationStatus.REVIEW_REQUIRED, CalculationStatus.FAIL)
    names = {v["name"] for v in r.intermediate_values}
    assert {"fc_max", "sigma_bolt", "t_required_bearing", "t_ring"} <= names


def test_base_ring_missing_bolt_allowable_blocks():
    r = _support_result(_ring(bolt_allowable_tension_MPa=None))
    assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT


def test_base_ring_absent_input_out_of_scope():
    sk = Support(support_id="SK", type="skirt", host_component_id="S1", location_mm=0.0,
                 width_mm=200.0, height_mm=1500.0, diameter_mm=1024.0, thickness_mm=10.0,
                 material_id="MAT-01")
    rows = ASMEVIII1DesignCode().check_supports(_project(supports=[sk]))
    br = [r for r in rows if r.calculation_type == "skirt_base_ring"][0]
    assert br.status == CalculationStatus.OUT_OF_SCOPE


def test_base_ring_thin_ring_fails():
    r = _support_result(_ring(ring_thickness_mm=3.0))
    assert r.status == CalculationStatus.FAIL
