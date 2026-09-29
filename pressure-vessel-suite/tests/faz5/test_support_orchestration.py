"""Destek orkestrasyonu (`check_supports`) — host çözümü, yük zarfı, ağırlık durumları.

Sayısal beklentiler formülden bağımsız, el hesabıdır.
"""

import math

import pytest
from pydantic import ValidationError

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationCode,
    ComponentReference,
    DesignConditions,
    ExternalLoad,
    Head,
    HeadType,
    LoadCase,
    LoadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    Support,
    VesselProject,
)

G = 9.80665


def _mat():
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4",
    )


def _project(supports, load_cases=None, chain=True, orientation=None):
    kwargs = {}
    if orientation:
        kwargs["orientation"] = orientation
    if chain:
        kwargs["component_sequence"] = [
            ComponentReference(component_type="head", component_id="HL"),
            ComponentReference(component_type="shell", component_id="S1"),
            ComponentReference(component_type="head", component_id="HR"),
        ]
    return VesselProject(
        project_number="SUP-ORCH", project_name="Support orchestration",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-10.0,
        ),
        heads=[
            Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
            Head(head_id="HR", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
        ],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0,
                                     tangent_length=2000.0, nominal_thickness=12.0,
                                     material_id="MAT-01")],
        materials=[_mat()],
        supports=supports,
        load_cases=load_cases or [],
        **kwargs,
    )


def _skirt(host="S1", loc=0.0, **kw):
    return Support(support_id="SK", type="skirt", host_component_id=host, location_mm=loc,
                   width_mm=200.0, height_mm=1500.0, diameter_mm=1024.0, thickness_mm=10.0,
                   material_id="MAT-01", **kw)


def _leg(host="S1", radius=600.0, **kw):
    return Support(support_id="LG", type="leg", host_component_id=host, location_mm=0.0,
                   width_mm=200.0, height_mm=500.0, material_id="MAT-01", leg_count=4,
                   leg_diameter_mm=100.0, leg_thickness_mm=8.0, support_radius_mm=radius, **kw)


def _run(project, idx=0):
    return ASMEVIII1DesignCode().check_supports(project)[idx]


def _iv(result, name):
    return next(v["value"] for v in result.intermediate_values if v["name"] == name)


def _lc(cid, ltype, loads, concurrent=None):
    return LoadCase(load_case_id=cid, name=cid, load_type=ltype, external_loads=loads,
                    concurrent_with=concurrent or [])


# ── 1. Host / konum kapısı ────────────────────────────────────────────────────

@pytest.mark.parametrize("host", ["S1", "HL"])
def test_skirt_base_outside_shell_interval_is_calculated_with_chain(host):
    r = _run(_project([_skirt(host=host, loc=0.0)]))
    # Host/konum kapısı geçildi (skirt hesap paketi kendi girdi bloklarını verebilir).
    assert r.status.value != "NOT CALCULATED", r.warnings
    assert _iv(r, "host_component_id") == host


def test_skirt_on_head_host_records_host():
    r = _run(_project([_skirt(host="HL")]))
    assert _iv(r, "host_component_id") == "HL"


def test_leg_on_head_host_is_calculated():
    r = _run(_project([_leg(host="HR", radius=400.0)]))
    assert r.status.value != "NOT CALCULATED", r.warnings
    assert _iv(r, "host_component_id") == "HR"


def test_saddle_position_gate_and_shell_only_host_remain():
    sad = Support(support_id="SD", type="saddle", host_component_id="S1", location_mm=99999.0,
                  width_mm=200.0, height_mm=500.0, material_id="MAT-01", contact_angle_deg=120.0)
    r = _run(_project([sad]))
    assert r.status.value == "NOT CALCULATED"
    sad2 = sad.model_copy(update={"host_component_id": "HL", "location_mm": 100.0})
    r2 = _run(_project([sad2]))
    assert r2.status.value == "NOT CALCULATED"
    assert "not a shell" in r2.warnings[0]


def test_skirt_diameter_inconsistent_with_host_warns():
    sk = _skirt().model_copy(update={"diameter_mm": 1600.0})
    r = _run(_project([sk]))
    assert any("Etek çapı" in w for w in r.warnings)
    ok = _run(_project([_skirt()]))
    assert not any("Etek çapı" in w for w in ok.warnings)


# ── 6. Fiziksel imkânsız girdiler ─────────────────────────────────────────────

def test_skirt_wall_not_less_than_half_diameter_rejected():
    with pytest.raises(ValidationError):
        Support(support_id="X", type="skirt", width_mm=1, height_mm=1, diameter_mm=100.0,
                thickness_mm=50.0, material_id="MAT-01")
    Support(support_id="X", type="skirt", width_mm=1, height_mm=1, diameter_mm=100.0,
            thickness_mm=49.0, material_id="MAT-01")


def test_leg_radius_far_beyond_host_is_not_calculated():
    r = _run(_project([_leg(radius=5000.0)]))
    assert r.status.value == "NOT CALCULATED"
    assert "yarıçap" in r.warnings[0]


def test_orientation_mismatch_warns():
    v_saddle = Support(support_id="SD", type="saddle", host_component_id="S1", location_mm=500.0,
                       width_mm=200.0, height_mm=500.0, material_id="MAT-01", contact_angle_deg=120.0)
    r = _run(_project([v_saddle], orientation="vertical"))
    assert any("Dikey kapta eyer" in w for w in r.warnings)
    r2 = _run(_project([_skirt()], orientation="horizontal"))
    assert any("Yatay kapta" in w for w in r2.warnings)


# ── 3. Alternatif yük durumları zarflanır ─────────────────────────────────────

def _moment_load(mx=0.0, my=0.0, **kw):
    return ExternalLoad(load_id="L", mx_nmm=mx, my_nmm=my, **kw)


def test_wind_and_seismic_alternative_cases_are_enveloped_not_summed():
    lcs = [
        _lc("WIND", LoadType.WIND, [_moment_load(mx=4e8)]),
        _lc("SEIS", LoadType.SEISMIC, [_moment_load(mx=4e8)]),
    ]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "global_overturning_moment") == pytest.approx(4e8)
    assert "load_case:" in _iv(r, "governing_moment_source")


def test_governing_case_is_reported():
    lcs = [
        _lc("WIND", LoadType.WIND, [_moment_load(mx=3e8)]),
        _lc("SEIS", LoadType.SEISMIC, [_moment_load(mx=4e8)]),
    ]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "global_overturning_moment") == pytest.approx(4e8)
    assert _iv(r, "governing_load_case") == "SEIS"


def test_explicitly_concurrent_cases_combine_but_wind_seismic_do_not():
    lcs = [
        _lc("DL", LoadType.DEAD_WEIGHT, [_moment_load(mx=3e8)], concurrent=["LIVE"]),
        _lc("LIVE", LoadType.LIVE_LOAD, [_moment_load(my=4e8)]),
    ]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "global_overturning_moment") == pytest.approx(5e8)  # SRSS(3e8, 4e8)
    lcs2 = [
        _lc("WIND", LoadType.WIND, [_moment_load(mx=3e8)], concurrent=["SEIS"]),
        _lc("SEIS", LoadType.SEISMIC, [_moment_load(my=4e8)]),
    ]
    r2 = _run(_project([_skirt()], lcs2))
    assert _iv(r2, "global_overturning_moment") == pytest.approx(4e8)  # birleşmez, zarf


def test_manual_moment_governs_over_smaller_load_case():
    lcs = [_lc("WIND", LoadType.WIND, [_moment_load(mx=4e8)])]
    r = _run(_project([_skirt(overturning_moment_Nmm=6e8)], lcs))
    assert _iv(r, "governing_moment_source").startswith("manual")


# ── 4. SRSS, Fz, elevation ────────────────────────────────────────────────────

def test_moment_components_combined_by_srss():
    lcs = [_lc("WIND", LoadType.WIND, [_moment_load(mx=3e8, my=4e8)])]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "global_overturning_moment") == pytest.approx(5e8)  # 3-4-5, cebirsel 7e8 DEĞİL


def test_horizontal_force_moment_uses_lever_arm_from_support():
    lcs = [_lc("WIND", LoadType.WIND, [ExternalLoad(load_id="W", fx_n=30e3, fy_n=40e3, elevation_mm=3000.0)])]
    r = _run(_project([_skirt(loc=1000.0)], lcs))
    assert _iv(r, "global_overturning_moment") == pytest.approx(50e3 * 2000.0)


def test_fz_adds_to_compression_weight():
    base = _iv(_run(_project([_skirt()])), "compression_weight_N")
    lcs = [_lc("DL", LoadType.DEAD_WEIGHT, [ExternalLoad(load_id="F", fz_n=1.0e5)])]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "compression_weight_N") == pytest.approx(base + 1.0e5)


def test_missing_elevation_with_horizontal_force_is_flagged_not_silent():
    lcs = [_lc("WIND", LoadType.WIND, [ExternalLoad(load_id="W", fx_n=1e4)])]
    r = _run(_project([_skirt()], lcs))
    assert _iv(r, "global_overturning_moment") == 0.0
    assert any("kaldıraç kolu 0" in a for a in r.assumptions)


# ── 5. Ağırlık durumları ──────────────────────────────────────────────────────

def test_hydrotest_weight_is_metal_plus_water_hand_calc():
    project = _project([_skirt()], chain=False)
    project = project.model_copy(update={"heads": []})
    r = _run(project)
    rho = _mat().density
    v_inner_mm3 = math.pi * 500.0**2 * 2000.0
    v_metal_mm3 = math.pi * (512.0**2 - 500.0**2) * 2000.0
    metal_kg = v_metal_mm3 / 1e9 * rho
    water_kg = v_inner_mm3 / 1e9 * 1000.0
    assert _iv(r, "empty_weight_N") == pytest.approx(metal_kg * G, rel=1e-6)
    assert _iv(r, "compression_weight_N") == pytest.approx((metal_kg + water_kg) * G, rel=1e-6)
    assert _iv(r, "hydrotest_water_mass_kg") == pytest.approx(water_kg, rel=1e-6)
    assert any("rho=1000" in a for a in r.assumptions)
