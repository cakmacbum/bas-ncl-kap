"""N01 (T-2.14): Nozzle.opening_weld_joint_efficiency -> ASME UG-37(a) takviye hesabı bağlantısı."""
import pytest

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import DesignConditions, MaterialProperty, Nozzle, NozzleType, ShellSection
from domain.enums import ProductForm


def _run(e1):
    dc = DesignConditions(design_pressure=1.2, design_temperature=200.0, operating_pressure=1.0,
                          maximum_allowable_pressure_ps=1.2, operating_temperature=150.0,
                          minimum_design_temperature=-10.0)
    shell = ShellSection(section_id="S", inside_diameter=1000.0, tangent_length=2000.0,
                         nominal_thickness=12.0, internal_corrosion_allowance=2.0, material_id="M")
    mat = MaterialProperty(
        material_id="M", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
        yield_strength=260.0, tensile_strength=485.0, source_reference="t")
    nz = Nozzle(tag="N1", nozzle_type=NozzleType.FLANGED, host_component_id="S", axial_position=500.0,
                outside_diameter=168.3, inside_diameter=154.1, neck_thickness=7.1,
                corrosion_allowance=1.0, material_id="M", opening_weld_joint_efficiency=e1)
    return ASMEVIII1DesignCode().calculate_nozzle({
        "nozzle": nz, "design_conditions": dc, "materials": [mat],
        "shell_sections": [shell], "heads": []})


def _iv(res, name):
    return next(float(i["value"]) for i in res.intermediate_values if i.get("name") == name)


def test_e1_reaches_reinforcement_and_reduces_available_area():
    base, e1 = _run(None), _run(0.85)
    assert any("E1=1 varsayıldı" in w for w in base.warnings)
    assert not any("E1=1 varsayıldı" in w for w in e1.warnings)
    assert _iv(e1, "A1") < _iv(base, "A1")
    assert _iv(e1, "A_total") < _iv(base, "A_total")
    assert _iv(e1, "A_required") == pytest.approx(_iv(base, "A_required"))  # tr E=1 (B-07)


def test_e1_schema_rejects_out_of_range():
    with pytest.raises(Exception):
        Nozzle(tag="N", host_component_id="S", axial_position=0, outside_diameter=100,
               inside_diameter=80, neck_thickness=5, material_id="M", opening_weld_joint_efficiency=1.2)
