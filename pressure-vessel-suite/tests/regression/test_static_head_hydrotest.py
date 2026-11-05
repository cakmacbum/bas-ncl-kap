"""T-2.8 / H01 — UG-99 hidrotest: bileşen bazında P_test + ρ_su·g·h ve test gerilmesi (el hesabı)."""
from __future__ import annotations

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from calc_core.verification import validate_result
from code_asme_viii_1 import ASMEVIII1DesignCode, formulas
from code_en_13445 import EN13445DesignCode
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty,
    ProductForm, ShellSection, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus, Orientation
from domain.project import ComponentReference

RHO, G = 1000.0, 9.81
S = 138.0


def _project(orient=Orientation.VERTICAL, seq=True, s_test=S, sy=260.0,
             code=CalculationCode.ASME_VIII_1) -> VesselProject:
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0,
    )
    shell = ShellSection(section_id="S1", inside_diameter=1000, tangent_length=2000,
                         nominal_thickness=12, material_id="M1", weld_joint_id="WJ",
                         internal_corrosion_allowance=2.0, mill_tolerance=12.5)
    hb = Head(head_id="HB", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    ht = Head(head_id="HT", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    mat = MaterialProperty(
        material_id="M1", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=S,
        allowable_stress_test_temp=s_test, yield_strength=sy, tensile_strength=485,
        source_reference="ASME II-D", density=7850)
    wj = WeldJoint(joint_id="WJ", joint_type="longitudinal", weld_category="A",
                   joint_efficiency=1.0, nde_method="RT-1", nde_extent="100%")
    sequence = ([ComponentReference(component_type="head", component_id="HB"),
                 ComponentReference(component_type="shell", component_id="S1"),
                 ComponentReference(component_type="head", component_id="HT")] if seq else [])
    return VesselProject(
        project_number="T", project_name="T", calculation_code=code,
        code_edition="2025", design_conditions=dc, shell_sections=[shell], heads=[hb, ht],
        materials=[mat], welds=[wj], orientation=orient, component_sequence=sequence)


def _run(project, dcode=None):
    res = CalculationOrchestrator(dcode or ASMEVIII1DesignCode(edition="2025")).run(project)
    hydro = next(r for r in res.results if r.calculation_type == "hydrotest")
    comps = {r.component_id: r for r in res.results if r.calculation_type == "hydrotest_component"}
    return hydro, comps


def _iv(r, name):
    return next(i["value"] for i in r.intermediate_values if i["name"] == name)


# El hesabı: gövde UG-27 MAWP (korozyonlu): t = 12·0,875 − 2 = 8,5; R = 502
MAWP_S1 = S * 1.0 * 8.5 / (502 + 0.6 * 8.5)
# Eliptik UG-32(d): D = 1004, t = 10 → 2SEt/(D + 0,2t)
MAWP_H = 2 * S * 10 / (1004 + 0.2 * 10)
P_TEST = 1.3 * MAWP_S1 * 1.0  # LSR = 138/138


def test_formul_el_hesabi():
    # 10 m su: 1000·9,81·10 = 98100 Pa = 0,0981 MPa
    assert formulas.hydrotest_local_pressure(1.0, 10_000.0) == pytest.approx(1.0981, rel=1e-12)
    assert formulas.hydrotest_membrane_stress(2.0, 1.0, 138.0) == pytest.approx(276.0)
    with pytest.raises(ValueError):
        formulas.hydrotest_local_pressure(1.0, -1.0)


def test_dikey_her_bilesen_h_ve_p_local():
    hydro, c = _run(_project())
    assert hydro.final_result == pytest.approx(P_TEST, rel=1e-12)
    # Kotlar: alt bombe 250 + 25 = 275 → toplam 275 + 2000 + 275 = 2550 mm
    expected_h = {"HB": 2550.0, "S1": 2275.0, "HT": 275.0}
    for cid, h in expected_h.items():
        r = c[cid]
        assert _iv(r, "h") == pytest.approx(h)
        assert r.reference_elevation_mm == pytest.approx(h)
        assert r.final_result == pytest.approx(P_TEST + RHO * G * h / 1e9, rel=1e-12)
        assert r.status == CalculationStatus.PASS
        assert validate_result(r) == []
    # Gerilme: σ = S·P_local/MAWP
    p_s1 = P_TEST + RHO * G * 2.275 / 1e6
    assert _iv(c["S1"], "sigma_test") == pytest.approx(S * p_s1 / MAWP_S1, rel=1e-12)
    assert c["S1"].utilization_ratio == pytest.approx(S * p_s1 / MAWP_S1 / 260.0, rel=1e-12)
    p_hb = P_TEST + RHO * G * 2.55 / 1e6
    assert _iv(c["HB"], "sigma_test") == pytest.approx(S * p_hb / MAWP_H, rel=1e-12)
    assert _iv(hydro, "P_test_local_max") == pytest.approx(p_hb, rel=1e-12)


def test_yatay_h_ic_cap():
    _, c = _run(_project(orient=Orientation.HORIZONTAL, seq=False))
    for cid in ("S1", "HB", "HT"):
        assert _iv(c[cid], "h") == pytest.approx(1000.0)
        assert c[cid].final_result == pytest.approx(P_TEST + RHO * G * 1.0 / 1e6, rel=1e-12)
        assert c[cid].status == CalculationStatus.PASS


def test_kot_yok_acik_uyari_review_sessiz_sifir_yok():
    _, c = _run(_project(seq=False))
    assert set(c) == {"S1", "HB", "HT"}
    for r in c.values():
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert any("Statik su kolonu eklenemedi" in w for w in r.warnings)
        assert r.final_result == pytest.approx(P_TEST, rel=1e-12)  # asgari, sıfır değil


def test_akma_asilirsa_fail():
    _, c = _run(_project(sy=150.0))
    # Gövde: σ ≈ 1,3·138 + su ≈ 180 MPa > 150
    assert c["S1"].status == CalculationStatus.FAIL
    assert c["S1"].utilization_ratio > 1.0


def test_lsr_eksikse_bilesen_de_review():
    _, c = _run(_project(s_test=None))
    for r in c.values():
        assert r.status == CalculationStatus.REVIEW_REQUIRED


def test_en13445_hidrotestine_dokunulmaz_yalniz_not():
    hydro, c = _run(_project(code=CalculationCode.EN_13445),
                    EN13445DesignCode(edition="2021+A1:2023"))
    assert c == {}
    assert any("Bileşen bazlı hidrotest statik su kolonu" in a for a in hydro.assumptions)
