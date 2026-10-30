"""P07 — WRC 537 / 297 nozul dış yükü altyapısı.

Katsayılar SENTETİKTİR (1.0 vb.) — gerçek bülten değeri değildir; yalnız
normalizasyon/bindirme/sınıflandırma matematiğini elle hesapla sınar.
"""

import math

import pytest
from pydantic import ValidationError

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationCode, ComponentReference, DesignConditions, Head, HeadType, MaterialProperty,
    Nozzle, ProductForm, ShellSection, VesselProject,
)
from domain.nozzle_loads import NozzleLoadAnalysis, NozzleLoadEntry, WRC537_COEFFICIENT_KEYS
from nozzles import nozzle_loads as nl
from nozzles import wrc_curves as wc

ALL_ONE = {k: 1.0 for k in WRC537_COEFFICIENT_KEYS}


def _project(entries, nozzle_od=168.3, pad=False, host="S1", criterion="tresca", pressure=1.2):
    noz = Nozzle(tag="N1", host_component_id=host, axial_position=1000.0, outside_diameter=nozzle_od,
                 inside_diameter=nozzle_od - 2 * 7.11, neck_thickness=7.11, material_id="MAT-01",
                 reinforcement_pad=pad, reinforcement_pad_thickness=10.0 if pad else None,
                 reinforcement_pad_od=300.0 if pad else None)
    return VesselProject(
        project_number="P07", project_name="WRC", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=DesignConditions(operating_pressure=1.0, design_pressure=pressure,
                                           maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
                                           design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id=h, type=HeadType.HEMISPHERICAL, inside_diameter=1000.0, nominal_thickness=12.0,
                    material_id="MAT-01") for h in ("HL", "HR")],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="MAT-01")],
        materials=[MaterialProperty(material_id="MAT-01", standard_pack="ASME II-D 2025",
                                    material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
                                    temperature=20.0, allowable_stress=138.0, yield_strength=260.0,
                                    tensile_strength=485.0, source_reference="test")],
        nozzles=[noz],
        component_sequence=[ComponentReference(component_type="head", component_id="HL"),
                            ComponentReference(component_type="shell", component_id="S1"),
                            ComponentReference(component_type="head", component_id="HR")],
        nozzle_loads=NozzleLoadAnalysis(entries=entries, stress_criterion=criterion),
    )


def _run(project):
    return nl.build_nozzle_load_results(project, "ASME VIII-1", "2025")


def _iv(res, name):
    return next(v["value"] for v in res.intermediate_values if v["name"] == name)


RM, T, R0 = 506.0, 12.0, 168.3 / 2


def test_geometri_gamma_beta():
    g = nl.wrc537_geometry(RM, T, R0)
    assert g["gamma"] == pytest.approx(506 / 12)
    assert g["beta"] == pytest.approx(0.875 * R0 / RM)


def test_katsayi_yoksa_blocked_code_data():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0)]))[0]
    assert r.status.value == "BLOCKED CODE DATA"
    assert "γ = 42.17" in r.warnings[-1] or any("γ = 42.17" in w for w in r.warnings)
    assert r.final_result is None


def test_eksik_tek_katsayi_sifir_sayilmaz():
    coeffs = dict(ALL_ONE)
    coeffs["P.Mx.CD"] = None
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0, coefficients=coeffs)]))[0]
    assert r.status.value == "BLOCKED CODE DATA"
    assert any("P.Mx.CD" in w for w in r.warnings)


def test_radyal_yuk_elle_hesap_review_required():
    """P = 5000 N, K = 1: σm = (K·P/Rm)/T, σb = 6·K·P/T²; eşit iki eksen → Tresca = toplam."""
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0, coefficients=ALL_ONE,
                                       include_pressure=False)]))[0]
    sm = 5000.0 / RM / T
    sb = 6.0 * 5000.0 / T**2
    assert _iv(r, "nozzle_neck_A_outside_sigma_phi") == pytest.approx(sm + sb)
    assert _iv(r, "nozzle_neck_A_inside_sigma_phi") == pytest.approx(sm - sb)
    assert r.final_result == pytest.approx(sm + sb)
    assert r.allowable_limit == pytest.approx(3 * 138.0)
    assert r.status.value == "REVIEW REQUIRED"   # kullanıcı okuması → doğrulanmamış


def test_sinir_asiminda_fail():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=10000.0, coefficients=ALL_ONE,
                                       include_pressure=False)]))[0]
    assert r.status.value == "FAIL"
    assert r.utilization_ratio == pytest.approx((10000 / RM / T + 6e4 / 144) / 414.0)


def test_ML_antisimetri_ve_beta_normalizasyonu():
    ML = 2.0e6
    pts = nl.evaluate_wrc537(nl.NozzleLoads(ML=ML), ALL_ONE, RM, T, R0)
    by = {(p.point, p.surface): p for p in pts}
    beta = 0.875 * R0 / RM
    expected = ML / (RM**2 * beta) / T + 6.0 * ML / (RM * beta) / T**2
    assert by[("A", "outside")].sigma_x == pytest.approx(expected)
    assert by[("B", "outside")].sigma_x == pytest.approx(-expected)
    assert by[("C", "outside")].sigma_x == pytest.approx(0.0)
    assert by[("D", "inside")].sigma_phi == pytest.approx(0.0)


def test_MC_yalniz_C_D():
    pts = nl.evaluate_wrc537(nl.NozzleLoads(Mc=1.0e6), ALL_ONE, RM, T, R0)
    by = {(p.point, p.surface): p for p in pts}
    assert by[("A", "outside")].sigma_phi == 0.0
    assert by[("C", "outside")].sigma_phi == pytest.approx(-by[("D", "outside")].sigma_phi)


def test_kesme_burulma_muhafazakar_toplam():
    Mt, Vc, VL = 1.0e6, 3000.0, 2000.0
    pts = nl.evaluate_wrc537(nl.NozzleLoads(Mt=Mt, Vc=Vc, VL=VL), {}, RM, T, R0)
    by = {p.point: p for p in pts}
    tt = Mt / (2 * math.pi * R0**2 * T)
    assert by["A"].tau == pytest.approx(tt + Vc / (math.pi * R0 * T))
    assert by["C"].tau == pytest.approx(tt + VL / (math.pi * R0 * T))


def test_yalniz_kesme_yukunde_egri_gerekmez():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Mt_Nmm=1.0e6)]))[0]
    assert r.status.value == "REVIEW REQUIRED"   # eğri kullanılmadı ama doğrulanmamış kapı/varsayım
    # Saf kesme Tresca = 2τ
    tt = 1.0e6 / (2 * math.pi * R0**2 * T)
    assert _iv(r, "nozzle_neck_A_outside_PL_Pb_Q") >= 2 * tt - 1e-9


def test_esdeger_gerilme():
    assert nl.equivalent_stress(100.0, -100.0, 0.0) == pytest.approx(200.0)
    assert nl.equivalent_stress(100.0, -100.0, 0.0, "von_mises") == pytest.approx(math.sqrt(3) * 100.0)
    assert nl.equivalent_stress(0.0, 0.0, 50.0) == pytest.approx(100.0)


def test_d_over_D_kapsam_disi():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0, coefficients=ALL_ONE)],
                      nozzle_od=406.4))[0]
    assert r.status.value == "OUT OF SCOPE"
    assert "WRC 297" in r.warnings[-1] or any("WRC 297" in w for w in r.warnings)


def test_bombe_host_kapsam_disi():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0)], host="HL"))[0]
    assert r.status.value == "OUT OF SCOPE"


def test_pedli_iki_konum():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=1000.0, coefficients=ALL_ONE)], pad=True))[0]
    assert _iv(r, "pad_edge_r0") == pytest.approx(150.0)
    assert _iv(r, "nozzle_neck_T") == pytest.approx(22.0)
    assert r.status.value in ("REVIEW REQUIRED", "FAIL")


def test_wrc297_her_zaman_blocked():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1", method="WRC297", Fr_N=5000.0)]))[0]
    assert r.calculation_type == "nozzle_load_wrc297"
    assert r.status.value == "BLOCKED CODE DATA"
    assert _iv(r, "T_over_t") == pytest.approx(12.0 / 7.11)


def test_yuk_yok_ve_nozul_yok():
    r = _run(_project([NozzleLoadEntry(nozzle_tag="N1")]))[0]
    assert r.status.value == "NOT CALCULATED"
    r = _run(_project([NozzleLoadEntry(nozzle_tag="NX", Fr_N=1.0)]))[0]
    assert r.status.value == "NOT CALCULATED"


def test_domain_dogrulama():
    with pytest.raises(ValidationError):
        NozzleLoadEntry(nozzle_tag="N1", coefficients={"P.Nphi.XY": 1.0})
    with pytest.raises(ValidationError):
        NozzleLoadAnalysis(entries=[NozzleLoadEntry(nozzle_tag="N1"), NozzleLoadEntry(nozzle_tag="N1")])
    NozzleLoadEntry(nozzle_tag="N1", method="WRC297", coefficients={"shell.P.Nphi": 1.0})


def test_egri_tablosu_bos_ve_sentetik_arama():
    assert wc.WRC537_CURVES == {} and wc.WRC297_CURVES == {}
    syn = {"P.Nphi.AB": {"source": "sentetik", "verified": False, "x1": [10.0, 50.0],
                         "x2": [0.1, 0.2], "values": [[1.0, 2.0], [3.0, 4.0]]}}
    assert wc.lookup("P.Nphi.AB", 30.0, 0.15, syn)["value"] == pytest.approx(2.5)
    with pytest.raises(wc.WrcCurveError):
        wc.lookup("P.Nphi.AB", 60.0, 0.15, syn)   # kırpma yok
    assert wc.resolve("P.Nphi.AB", {"P.Nphi.AB": 9.0}, 30.0, 0.15, syn)["source"] == "user"


def test_tasarim_kodu_akisi():
    code = ASMEVIII1DesignCode()
    p = _project([NozzleLoadEntry(nozzle_tag="N1", Fr_N=5000.0)])
    types = [r.calculation_type for r in code.check_nozzle_clashes(p)]
    assert "nozzle_load_wrc537" in types
    p2 = p.model_copy(update={"nozzle_loads": None})
    assert "nozzle_load_wrc537" not in [r.calculation_type for r in code.check_nozzle_clashes(p2)]
