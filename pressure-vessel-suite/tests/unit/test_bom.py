"""P09 — BOM + maliyet tahmini testleri."""

import math

import pytest

from calc_core.bom import build_bom
from domain import (
    CalculationCode, DesignConditions, Head, HeadType, MaterialProperty,
    Nozzle, ProductForm, ShellSection, Support, VesselProject,
)
from domain.bom import CostInputs


def _project(**extra):
    mat = MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="test",
    )
    return VesselProject(
        project_number="BOM-1", project_name="bom",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-10.0,
        ),
        heads=[Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="MAT-01")],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0,
                                     tangent_length=2000.0, nominal_thickness=12.0,
                                     material_id="MAT-01")],
        materials=[mat], **extra,
    )


def test_shell_line_matches_volume_mass():
    rep = build_bom(_project())
    shell = next(l for l in rep.lines if l.part.startswith("Gövde"))
    expected = math.pi * (512.0**2 - 500.0**2) * 2000.0 / 1e9 * 7850.0
    assert shell.unit_mass_kg == pytest.approx(expected, rel=1e-9)
    assert rep.mass_complete


def test_nozzle_pipe_mass_includes_host_wall():
    nz = Nozzle(tag="N1", host_component_id="S1", axial_position=500.0,
                outside_diameter=168.3, inside_diameter=146.3, neck_thickness=11.0,
                outside_projection=150.0, inside_projection=0.0, material_id="MAT-01")
    rep = build_bom(_project(nozzles=[nz]))
    line = next(l for l in rep.lines if l.part == "Nozul N1")
    length = 150.0 + 12.0
    expected = math.pi / 4 * (168.3**2 - 146.3**2) * length / 1e9 * 7850.0
    assert line.unit_mass_kg == pytest.approx(expected, rel=1e-9)


def test_saddle_mass_missing_is_flagged_not_invented():
    sp = Support(support_id="SAD-1", type="saddle", width_mm=200.0, height_mm=500.0,
                 material_id="MAT-01")
    rep = build_bom(_project(supports=[sp]))
    line = next(l for l in rep.lines if l.part == "Eyer SAD-1")
    assert line.unit_mass_kg is None
    assert not rep.mass_complete
    assert any("EKSİK" in w for w in rep.warnings)


def test_cost_not_calculated_without_inputs():
    cost = build_bom(_project()).cost
    assert cost["status"] == "NOT_CALCULATED"
    assert cost["total_eur"] is None


def test_cost_partial_then_complete():
    partial = build_bom(_project(cost_inputs=CostInputs(
        material_price_eur_per_kg={"MAT-01": 2.0}))).cost
    assert partial["status"] == "INCOMPLETE"
    assert partial["total_eur"] is None and partial["missing"]
    full = build_bom(_project(cost_inputs=CostInputs(
        material_price_eur_per_kg={"MAT-01": 2.0}, welding_hours=10.0,
        labor_rate_eur_per_hour=50.0, ndt_cost_eur=100.0, paint_cost_eur=200.0))).cost
    assert full["status"] == "OK"
    mat_cost = next(i for i in full["items"] if i["item"] == "Malzeme MAT-01")["cost_eur"]
    assert full["total_eur"] == pytest.approx(mat_cost + 500.0 + 100.0 + 200.0, abs=0.02)
