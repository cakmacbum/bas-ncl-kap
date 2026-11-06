"""E02 — EN 13445-3 koni (7.6.4), koni uç birleşimleri (7.6.6 / 7.6.8) ve düz kapak (10.4).

El hesabı değerleri bu dosyadaki `math` ifadeleriyle değil, aşağıda yorumda gösterilen
açık sayılarla sabitlenmiştir. Formüller lisanslı metinle doğrulanmadı (verified=False):
olumlu sonuç PASS değil REVIEW_REQUIRED olmalıdır. Grafik katsayısı (düz kapak C) koda
gömülmez: girilmezse BLOCKED_CODE_DATA.
"""

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_en_13445 import EN13445DesignCode, formulas
from domain import (
    CalculationCode, Cone, DesignConditions, Head, HeadType, MaterialProperty, ProductForm,
    ShellSection, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus
from domain.geometry import Junction

RR = CalculationStatus.REVIEW_REQUIRED


# ── Formül el hesapları (P=1.2 MPa, f=163 MPa, α=30°) ────────────────────────

def test_cone_thickness_hand_calc():
    # e = 1.2·1000/(2·163·1 − 1.2)/cos30 = 3.694581/0.866025 = 4.26613 mm
    assert formulas.cone_thickness_internal_pressure(1.2, 1000.0, 163.0, 1.0, 30.0) == pytest.approx(4.266135, rel=1e-6)


def test_cone_alpha_zero_equals_cylinder_form():
    # α=0 -> 7.4.2 silindir biçimi P·Di/(2fz − P)
    assert formulas.cone_thickness_internal_pressure(1.2, 1000.0, 163.0, 0.85, 0.0) == pytest.approx(
        1.2 * 1000.0 / (2 * 163.0 * 0.85 - 1.2))


def test_cone_mawp_hand_calc_and_inverse():
    # P = 2·163·12·0.866025/(1000 + 12·0.866025) = 3387.89/1010.392 = 3.35305 MPa
    p = formulas.cone_mawp(1000.0, 12.0, 163.0, 1.0, 30.0)
    assert p == pytest.approx(3.353046, rel=1e-6)
    # ters: bu basınçta gerekli kalınlık tam 12 mm
    assert formulas.cone_thickness_internal_pressure(p, 1000.0, 163.0, 1.0, 30.0) == pytest.approx(12.0, rel=1e-9)


def test_large_end_fixed_point_hand_calc():
    # Dc=1012: β(e) = (1/3)·√(1012/e)·0.57735/(1 + 1/√0.866025) − 0.15
    # sabit nokta e_j = 1.2·1012·β/(326) -> e_j ≈ 4.5787 mm, β ≈ 1.2291
    e_j, beta = formulas.cone_large_end_required_thickness(1.2, 1012.0, 163.0, 30.0)
    assert e_j == pytest.approx(4.578729, rel=1e-6)
    assert beta == pytest.approx(1.229138, rel=1e-6)
    assert e_j == pytest.approx(1.2 * 1012.0 * beta / (2 * 163.0), rel=1e-9)


def test_large_end_no_junction_demand_at_zero_angle():
    e_j, beta = formulas.cone_large_end_required_thickness(1.2, 1012.0, 163.0, 0.0)
    assert e_j == 0.0 and beta < 0


def test_small_end_beta_h_both_branches():
    # s=1: τ = 1 + √(1·2/(2·0.866025)) = 2.07457; β_H = 0.4·√(512/12)·0.57735/τ + 0.5 = 1.22714
    s, tau, bh = formulas.cone_small_end_beta_h(512.0, 12.0, 12.0, 30.0)
    assert (s, tau, bh) == pytest.approx((1.0, 2.074570, 1.227136), rel=1e-6)
    # P_max = 2·163·12/(512·1.227136) = 6.22639 MPa
    assert formulas.cone_small_end_max_pressure(512.0, 12.0, 163.0, bh) == pytest.approx(6.226388, rel=1e-6)
    # s=2/3 < 1: τ = s·√(s/cosα) + √((1+s²)/2) = 1.43476; β_H = 1.55139
    s, tau, bh = formulas.cone_small_end_beta_h(512.0, 12.0, 8.0, 30.0)
    assert (tau, bh) == pytest.approx((1.434758, 1.551393), rel=1e-6)


def test_flat_end_hand_calc():
    # e = 0.4·1000·√(1.2/163) = 34.3208 mm ; P(e=40) = 163·(40/400)² = 1.63 MPa
    assert formulas.flat_end_thickness(1.2, 1000.0, 163.0, 0.4) == pytest.approx(34.320753, rel=1e-6)
    assert formulas.flat_end_mawp(1000.0, 40.0, 163.0, 0.4) == pytest.approx(1.63, rel=1e-9)


# ── DesignCode / orkestratör ─────────────────────────────────────────────────

def _project(*, cone_t=12.0, shell_di=1000.0, cone_end="large", flat_c=0.4, head_t=40.0, knuckle=None):
    return VesselProject(
        project_number="E02", project_name="cone-flat", calculation_code=CalculationCode.EN_13445,
        code_edition="2021",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
            operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id="H", type=HeadType.FLAT, inside_diameter=shell_di, nominal_thickness=head_t,
                    material_id="M", mill_tolerance=10.0, en_flat_end_factor_c=flat_c)],
        shell_sections=[ShellSection(section_id="S", inside_diameter=shell_di, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
        cones=[Cone(cone_id="K", large_diameter=1000.0, small_diameter=500.0, half_apex_angle=30.0,
                    length=433.0, nominal_thickness=cone_t, material_id="M", mill_tolerance=10.0)],
        junctions=[Junction(junction_id="J", left_component_id="S", right_component_id="K",
                            junction_type="cone_to_shell", cone_end=cone_end, knuckle_radius_mm=knuckle)],
        welds=[WeldJoint(joint_id="WJ", joint_type="longitudinal", weld_category="A", full_penetration=True)],
        materials=[MaterialProperty(
            material_id="M", standard_pack="EN 10028-3", material_designation="P355NH",
            product_form=ProductForm.PLATE, temperature=20.0, allowable_stress=163.0,
            yield_strength=295.0, tensile_strength=490.0, source_reference="t")],
    )


def _run(**kw):
    return CalculationOrchestrator(EN13445DesignCode(edition="2021")).run(_project(**kw))


def _row(res, calc_type, cid):
    rows = [r for r in res.results if r.calculation_type == calc_type and r.component_id == cid]
    assert len(rows) == 1, (calc_type, cid, rows)
    return rows[0]


def test_flat_head_thickness_and_mawp_review_required():
    res = _run()
    t = _row(res, "thickness", "H")
    assert t.status == RR and t.clause_reference == "EN 13445-3, 10.4"
    assert t.final_result == pytest.approx(34.320753 / 0.90, rel=1e-6)  # %10 sac toleransı
    m = _row(res, "mawp", "H")
    assert m.status == RR and m.final_result == pytest.approx(1.63, rel=1e-9)


def test_flat_head_thin_fails():
    t = _row(_run(head_t=30.0), "thickness", "H")
    assert t.status == CalculationStatus.FAIL


def test_flat_head_without_en_factor_is_blocked_not_asme():
    res = _run(flat_c=None)
    for ct in ("thickness", "mawp"):
        r = _row(res, ct, "H")
        assert r.status == CalculationStatus.BLOCKED_CODE_DATA
        assert r.final_result is None
    res.get_global_mawp()
    assert not _row(res, "mawp", "H").governing


def test_cone_thin_fails():
    r = _row(_run(cone_t=4.5), "thickness", "K")  # gerekli nominal 4.7402 mm
    assert r.status == CalculationStatus.FAIL
    assert r.final_result == pytest.approx(4.266135 / 0.90, rel=1e-6)


def test_large_end_junction_fails_when_thin():
    # e_av = min(12, 4.5) = 4.5 < e_j(Dc=1012) = 4.5787
    r = _row(_run(cone_t=4.5), "junction_check", "J")
    assert r.status == CalculationStatus.FAIL
    assert r.final_result == pytest.approx(4.578729, rel=1e-6)
    assert r.allowable_limit == pytest.approx(4.5)


def test_small_end_junction_hand_calc():
    # gövde Di=500 -> Dc = 512, e1=e2=12 -> P_max = 6.22639 MPa, P=1.2 -> REVIEW_REQUIRED
    r = _row(_run(shell_di=500.0, cone_end="small"), "junction_check", "J")
    assert r.status == RR and r.clause_reference == "EN 13445-3, 7.6.8"
    assert r.allowable_limit == pytest.approx(6.226388, rel=1e-6)
    assert r.utilization_ratio == pytest.approx(1.2 / 6.226388, rel=1e-6)


def test_knuckled_junction_is_explicit_not_calculated():
    r = _row(_run(knuckle=50.0), "junction_check", "J")
    assert r.status == CalculationStatus.NOT_CALCULATED
    assert "7.6.7" in " ".join(r.warnings)


def test_missing_cone_end_is_blocked():
    r = _row(_run(cone_end=None), "junction_check", "J")
    assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
