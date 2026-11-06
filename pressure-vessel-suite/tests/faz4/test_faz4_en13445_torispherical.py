"""E03 — EN 13445-3, 7.5.3 torisferik bombe tam prosedürü (es / ey / eb, β 7.5.3.5).

El hesabı değerleri yorumdaki açık sayılarla sabitlenmiştir. Formüller lisanslı metinle
doğrulanmadı (verified=False): olumlu sonuç PASS değil REVIEW_REQUIRED olmalıdır.
B-09 kaldırıldı: büküm yarıçapı girilmezse BLOCKED_MISSING_INPUT (varsayılan r yok).
"""

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_en_13445 import EN13445DesignCode, formulas
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty, ProductForm,
    ShellSection, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus

RR = CalculationStatus.REVIEW_REQUIRED
FB = 275.0 / 1.5  # 183.333 MPa


# ── β (7.5.3.5) el hesabı: e = 10, R = 1000 → Y = 0.01, Z = 2, N = 1.006 − 1/6.8561 = 0.860146 ──

def test_beta_hand_calc_all_branches():
    # β0.1  = N·(−0.1833·8 + 1.0383·4 − 1.2943·2 + 0.837)  = 0.860146·0.9352 = 0.804407
    # β0.06 = N·(−0.3635·8 + 2.2124·4 − 3.2937·2 + 1.8873) = 0.860146·1.2415 = 1.067869
    # β0.2  = max(0.95·(0.56 − 0.0194 − 0.00825); 0.5)      = 0.505733
    assert formulas.torispherical_beta(10.0, 1000.0, 100.0, 1000.0) == pytest.approx(0.804407, rel=1e-5)
    assert formulas.torispherical_beta(10.0, 1000.0, 60.0, 1000.0) == pytest.approx(1.067869, rel=1e-5)
    assert formulas.torispherical_beta(10.0, 1000.0, 200.0, 1000.0) == pytest.approx(0.505733, rel=1e-5)
    # X = 0.08 → 25·(0.02·β0.06 + 0.02·β0.1) = 0.936138 ; X = 0.15 → 10·(0.05·β0.1 + 0.05·β0.2) = 0.655070
    assert formulas.torispherical_beta(10.0, 1000.0, 80.0, 1000.0) == pytest.approx(0.936138, rel=1e-5)
    assert formulas.torispherical_beta(10.0, 1000.0, 150.0, 1000.0) == pytest.approx(0.655070, rel=1e-5)


def test_beta_y_capped_at_004_and_floor_05():
    # e/R > 0.04 → Y = 0.04 (β değişmez); β0.2 tabanı 0.5
    assert formulas.torispherical_beta(60.0, 1000.0, 100.0, 1000.0) == pytest.approx(
        formulas.torispherical_beta(40.0, 1000.0, 100.0, 1000.0), rel=1e-12)
    assert formulas.torispherical_beta(40.0, 1000.0, 200.0, 1000.0) == pytest.approx(0.5, rel=1e-12)


def test_beta_outside_r_over_di_range_raises():
    with pytest.raises(ValueError):
        formulas.torispherical_beta(10.0, 1000.0, 50.0, 1000.0)


# ── Kalınlık (7.5.3.2) el hesabı: P=1.2, Di=R=1000, r=100, f=163, z=1, fb=183.333 ──

def test_thickness_hand_calc():
    # es = 1.2·1000/(326 − 0.6) = 3.687769
    # eb = 950·[1.2/(111·183.333)·10^0.825]^(2/3) = 950·(3.9411e-4)^(2/3) = 5.106635
    # ey: sabit nokta e = β(e)·1.2·950/163 ; e = 6.30228 → Y = 0.0063023, Z = 2.20050,
    #     N = 0.847358, β = 0.901116 → 0.901116·6.993865 = 6.30228 (yöneten)
    d = formulas.head_torispherical_thickness(1.2, 1000.0, 1000.0, 100.0, 163.0, 1.0, FB)
    assert d["es"] == pytest.approx(3.687769, rel=1e-6)
    assert d["eb"] == pytest.approx(5.106635, rel=1e-6)
    assert d["ey"] == pytest.approx(6.302281, rel=1e-6)
    assert d["beta"] == pytest.approx(0.901116, rel=1e-5)
    assert d["governing"] == "ey" and d["e"] == d["ey"]
    # sabit nokta tutarlılığı
    assert d["ey"] == pytest.approx(d["beta"] * 1.2 * 950.0 / 163.0, rel=1e-9)


def test_crown_governs_for_large_knuckle():
    # r = 0.2·Di → β küçük; es = 3.687769 yönetir
    d = formulas.head_torispherical_thickness(1.2, 1000.0, 1000.0, 200.0, 163.0, 1.0, FB)
    assert d["governing"] == "es" and d["e"] == pytest.approx(3.687769, rel=1e-6)


def test_weld_factor_only_in_crown_equation():
    d1 = formulas.head_torispherical_thickness(1.2, 1000.0, 1000.0, 100.0, 163.0, 1.0, FB)
    d2 = formulas.head_torispherical_thickness(1.2, 1000.0, 1000.0, 100.0, 163.0, 0.7, FB)
    assert d2["es"] > d1["es"]
    assert d2["ey"] == pytest.approx(d1["ey"], rel=1e-12) and d2["eb"] == pytest.approx(d1["eb"], rel=1e-12)


def test_fb_cold_spun_austenitic_factor():
    assert formulas.torispherical_fb(275.0) == pytest.approx(183.3333, rel=1e-6)
    assert formulas.torispherical_fb(275.0, cold_spun_austenitic=True) == pytest.approx(1.6 * 183.3333, rel=1e-6)


# ── MAWP (7.5.3.4) el hesabı + ikiye bölme tersi: ea = 10 ──

def test_max_pressure_hand_calc_and_bisection_inverse():
    # Ps = 2·163·10/(1000 + 5) = 3.243781
    # Py = 163·10/(0.804407·950) = 2.132986   (yöneten)
    # Pb = 111·183.333·(10/950)^1.5·0.1^0.825 = 3.288357
    m = formulas.torispherical_max_pressure(1000.0, 1000.0, 100.0, 10.0, 163.0, 1.0, FB)
    assert m["Ps"] == pytest.approx(3.243781, rel=1e-6)
    assert m["Py"] == pytest.approx(2.132986, rel=1e-6)
    assert m["Pb"] == pytest.approx(3.288357, rel=1e-6)
    assert m["governing"] == "Py" and m["P_max"] == m["Py"]
    assert m["P_bisect"] == pytest.approx(m["P_max"], rel=1e-9)
    # ters yön: bu basınçta gerekli kalınlık 10 mm
    d = formulas.head_torispherical_thickness(m["P_max"], 1000.0, 1000.0, 100.0, 163.0, 1.0, FB)
    assert d["e"] == pytest.approx(10.0, rel=1e-7)


def test_applicability_limits():
    names = {n: ok for n, ok, *_ in formulas.torispherical_applicability(1000.0, 1024.0, 1000.0, 100.0, 6.3, 9.0)}
    assert all(names.values()) and len(names) == 6
    bad = {n: ok for n, ok, *_ in formulas.torispherical_applicability(1000.0, 1024.0, 1100.0, 50.0, 90.0, 0.5)}
    assert not bad["7.5.3.1 r >= 0.06·Di"]
    assert not bad["7.5.3.1 r >= 2·e"]
    assert not bad["7.5.3.1 e <= 0.08·De"]
    assert not bad["7.5.3.1 ea >= 0.001·De"]
    assert not bad["7.5.3.1 R <= De"]
    assert bad["7.5.3.1 r <= 0.2·Di"]


def test_mawp_from_head_torispherical_refuses_old_formula():
    with pytest.raises(ValueError):
        formulas.mawp_from_head("torispherical", 1000.0, 12.0, 163.0, 1.0, 1000.0, 100.0, 2.0)


# ── DesignCode / orkestratör ─────────────────────────────────────────────────

def _project(*, knuckle=100.0, crown=1000.0, head_t=12.0):
    return VesselProject(
        project_number="E03", project_name="tori", calculation_code=CalculationCode.EN_13445,
        code_edition="2021",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
            operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id="H", type=HeadType.TORISPHERICAL, inside_diameter=1000.0,
                    crown_radius=crown, knuckle_radius=knuckle, torispherical_geometry="custom"
                    if knuckle else "standard_asme_fd",
                    nominal_thickness=head_t, material_id="M", mill_tolerance=10.0,
                    internal_corrosion_allowance=2.0)],
        shell_sections=[ShellSection(section_id="S", inside_diameter=1000.0, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
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


def _iv(r, name):
    return next(i["value"] for i in r.intermediate_values if i["name"] == name)


def test_design_code_thickness_review_required_with_corrosion():
    # C = 2 → Di = 1004, R = 1002, r = 102 ; fb = 295/1.5 = 196.667
    # ey = 6.282310 (yöneten) ; nominal = (6.282310 + 2)/0.90 = 9.202567 ≤ 12
    t = _row(_run(), "thickness", "H")
    assert t.status == RR and t.clause_reference == "EN 13445-3, 7.5.3"
    assert _iv(t, "R") == pytest.approx(1002.0) and _iv(t, "r") == pytest.approx(102.0)
    assert _iv(t, "ey") == pytest.approx(6.282310, rel=1e-6)
    assert _iv(t, "governing") == "ey"
    assert t.final_result == pytest.approx(9.202567, rel=1e-6)
    assert all(c["passed"] for c in t.validity_checks)


def test_design_code_mawp_review_required():
    # ea = 12 − 2 = 10 ; Py = 163·10/(0.800030·952.3) = 2.139476 (yöneten)
    m = _row(_run(), "mawp", "H")
    assert m.status == RR
    assert m.final_result == pytest.approx(2.139476, rel=1e-6)
    assert _iv(m, "governing") == "Py"


def test_thin_head_fails():
    t = _row(_run(head_t=9.0), "thickness", "H")
    assert t.status == CalculationStatus.FAIL


def test_missing_knuckle_radius_is_blocked_no_b09_default():
    res = _run(knuckle=None)
    for ct in ("thickness", "mawp"):
        r = _row(res, ct, "H")
        assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
        assert r.final_result is None
        assert not any("0.10" in a or "Korbbogen" in a for a in r.assumptions)


def test_applicability_violation_is_out_of_scope():
    # r = 50 + 2 = 52 < 0.06·1004 = 60.24 → prosedür geçersiz
    res = _run(knuckle=50.0)
    for ct in ("thickness", "mawp"):
        r = _row(res, ct, "H")
        assert r.status == CalculationStatus.OUT_OF_SCOPE
        assert any(not c["passed"] and "0.06" in c["name"] for c in r.validity_checks)
