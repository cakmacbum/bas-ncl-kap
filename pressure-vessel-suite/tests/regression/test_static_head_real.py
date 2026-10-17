"""B-10 gerçek düzeltme: liquid_level_mm + geometriden bileşen taban kotu → MAWP statik kafa."""
from __future__ import annotations

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_asme_viii_1 import ASMEVIII1DesignCode
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty,
    ProductForm, ShellSection, VesselProject, WeldJoint,
)
from domain.enums import Orientation
from domain.project import ComponentReference

G = 9.80665


def _project(rho=1000.0, level=None, orient=Orientation.VERTICAL, seq=True) -> VesselProject:
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0, fluid_density_kg_m3=rho, liquid_level_mm=level,
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
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="ASME II-D", density=7850)
    wj = WeldJoint(joint_id="WJ", joint_type="longitudinal", weld_category="A",
                   joint_efficiency=1.0, nde_method="RT-1", nde_extent="100%")
    sequence = ([ComponentReference(component_type="head", component_id="HB"),
                 ComponentReference(component_type="shell", component_id="S1"),
                 ComponentReference(component_type="head", component_id="HT")] if seq else [])
    return VesselProject(
        project_number="T", project_name="T", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell], heads=[hb, ht],
        materials=[mat], welds=[wj], orientation=orient, component_sequence=sequence)


def _mawp(project):
    res = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025")).run(project)
    return {r.component_id: r for r in res.results if r.calculation_type == "mawp"}


def _base():
    return {k: v.final_result for k, v in _mawp(_project(rho=0.0)).items()}


def test_dikey_alt_bombe_tam_h_ust_gövde_daha_kucuk():
    base = _base()
    m = _mawp(_project(level=3000.0))
    # alt bombe tabanı datum 0 → h = 3000
    assert m["HB"].final_result == pytest.approx(base["HB"] - 1000 * G * 3.0 * 1e-6, rel=1e-12)
    assert m["HB"].reference_elevation_mm == 3000.0
    # alt bombe: derinlik 250 + düz flanş 25 = 275 → gövde tabanı 275, üst bombe 2275
    assert m["S1"].reference_elevation_mm == pytest.approx(2725.0)
    assert m["S1"].final_result == pytest.approx(base["S1"] - 1000 * G * 2.725 * 1e-6, rel=1e-12)
    assert m["HT"].reference_elevation_mm == pytest.approx(725.0)
    assert m["HT"].final_result == pytest.approx(base["HT"] - 1000 * G * 0.725 * 1e-6, rel=1e-12)
    assert m["HT"].reference_elevation_mm < m["S1"].reference_elevation_mm < m["HB"].reference_elevation_mm


def test_dikey_sivi_ust_bombe_tabaninin_altinda_h_sifir():
    base = _base()
    m = _mawp(_project(level=1000.0))
    assert m["HT"].reference_elevation_mm == 0.0
    assert m["HT"].final_result == pytest.approx(base["HT"])
    assert any("taban kotunun altında" in a for a in m["HT"].assumptions)


def test_yatay_h_sivi_seviyesi():
    base = _base()
    m = _mawp(_project(level=800.0, orient=Orientation.HORIZONTAL, seq=False))
    assert m["S1"].final_result == pytest.approx(base["S1"] - 1000 * G * 0.8 * 1e-6, rel=1e-12)
    assert m["HB"].reference_elevation_mm == 800.0


def test_seviye_yok_uyari_korunur_sayilar_ayni():
    base = _base()
    m = _mawp(_project(level=None))
    for k, r in m.items():
        assert r.final_result == pytest.approx(base[k])
        assert any("Statik kafa uygulanmadı" in a for a in r.assumptions)
        assert any("Hidrotest statik kafası" in a for a in r.assumptions)


def test_dikey_sira_yok_kot_uydurulmaz():
    base = _base()
    m = _mawp(_project(level=3000.0, seq=False))
    for k, r in m.items():
        assert r.reference_elevation_mm == 0.0
        assert r.final_result == pytest.approx(base[k])
        assert any("Statik kafa uygulanmadı" in a for a in r.assumptions)


def test_yogunluk_sifir_eski_davranis():
    base = _base()
    m = _mawp(_project(rho=0.0, level=3000.0))
    for k, r in m.items():
        assert r.final_result == pytest.approx(base[k])
        assert any("Akışkan yoğunluğu girilmedi" in a for a in r.assumptions)


def test_tutarsiz_dizi_hesabi_cokertmez_kot_uydurulmaz():
    """component_sequence tanımsız bir kimlik içerse bile hesap çökmez; kot uydurulmaz."""
    project = _project(level=3000.0)
    bad = project.component_sequence + [
        ComponentReference(component_type="shell", component_id="YOK-99")
    ]
    project = project.model_copy(update={"component_sequence": bad})
    base = _base()
    m = _mawp(project)  # KeyError fırlatmamalı
    for cid in ("HB", "S1", "HT"):
        assert m[cid].final_result == pytest.approx(base[cid], rel=1e-12)
        assert m[cid].reference_elevation_mm == 0.0
