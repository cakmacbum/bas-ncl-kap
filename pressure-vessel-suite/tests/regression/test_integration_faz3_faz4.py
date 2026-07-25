"""Entegrasyon testleri — Faz 3/4 modüllerinin pipeline'a ve rapora bağlanması.

Bu testler, salt-okunur kısıt yüzünden ajanların bağlayamadığı entegrasyonu doğrular:
  - Orchestrator artık gerçek nozul takviye + kaynak doğrulama + çakışma sonucu üretir.
  - Rapor, PED sınıflandırma sonucu ve ESR matrisiyle gerçek veriyle dolar.
"""

import pytest

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    NozzleType,
    ProductForm,
    ShellSection,
    VesselProject,
    WeldJoint,
)
from code_asme_viii_1 import ASMEVIII1DesignCode
from calc_core.orchestrator import CalculationOrchestrator


@pytest.fixture
def project():
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0,
    )
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000, tangent_length=2000,
        nominal_thickness=12, material_id="M1", weld_joint_id="WJ-01",
        internal_corrosion_allowance=2.0, mill_tolerance=12.5,
    )
    hl = Head(head_id="HL", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    hr = Head(head_id="HR", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    n1 = Nozzle(
        tag="N1", nozzle_type=NozzleType.FLANGED, host_component_id="SHELL-01",
        axial_position=800, circumferential_angle=90, outside_diameter=168.3,
        inside_diameter=154.1, neck_thickness=7.1, material_id="M1",
        reinforcement_pad=True, reinforcement_pad_od=300, reinforcement_pad_thickness=10,
    )
    mat = MaterialProperty(
        material_id="M1", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="ASME II-D", density=7850,
    )
    wj = WeldJoint(
        joint_id="WJ-01", joint_type="longitudinal", weld_category="A",
        joint_efficiency=1.0, nde_method="RT-1", nde_extent="100%",
    )
    return VesselProject(
        project_number="INT-001", project_name="Integration Vessel", customer="X",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=dc, shell_sections=[shell], heads=[hl, hr],
        nozzles=[n1], materials=[mat], welds=[wj],
    )


@pytest.fixture
def calc_result(project):
    orch = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025"))
    return orch.run(project)


# ── B) Orchestrator entegrasyonu ──────────────────────────────────────────────

def test_orchestrator_produces_real_nozzle_result(calc_result):
    """Nozul takviye hesabı pipeline'da gerçek sonuç (PASS/FAIL) üretir."""
    noz = [r for r in calc_result.results if r.calculation_type == "nozzle_reinforcement"]
    assert len(noz) == 1
    assert noz[0].status.value in ("PASS", "FAIL")
    assert noz[0].clause_reference == "UG-37/UG-40"
    names = {iv["name"] for iv in noz[0].intermediate_values}
    assert {"A_required", "A1", "A2", "A_total"}.issubset(names)


def test_orchestrator_produces_weld_validation(calc_result):
    """Kaynak doğrulama sonucu pipeline'a girer."""
    welds = [r for r in calc_result.results if r.calculation_type == "weld_validation"]
    assert len(welds) == 1
    assert welds[0].component_id == "WJ-01"


def test_orchestrator_produces_clash_check(calc_result):
    """Nozul çakışma kontrolü sonucu pipeline'a girer."""
    clash = [r for r in calc_result.results if r.calculation_type == "clash_check"]
    assert len(clash) == 1
    assert clash[0].component_id == "N1"


# ── C) Report entegrasyonu ────────────────────────────────────────────────────

def test_report_nozzle_area_table_rendered(project, calc_result):
    """Rapor nozul alan tablosunu gerçek veriyle gösterir (placeholder yok)."""
    from report_engine.generator import ReportGenerator
    html = ReportGenerator().generate(project, calc_result).html_content
    assert "Takviye Alan Analizi" in html
    assert "A_required = d × t_required" in html
    assert "Faz 3'te uygulanacaktır" not in html


def test_report_weld_map_rendered(project, calc_result):
    """Rapor kaynak haritasını doğrulama sonucuyla gösterir."""
    from report_engine.generator import ReportGenerator
    html = ReportGenerator().generate(project, calc_result).html_content
    assert "Kaynak Haritası ve Doğrulama" in html
    assert "WJ-01" in html
    assert "Faz 3'te uygulanacaktır" not in html


def test_report_ped_scope_with_result(project, calc_result):
    """ped_result verilince 6. bölüm gerçek kategori/modülle dolar."""
    from ped_2014_68_eu import (
        PEDClassificationEngine, ClassificationInput, FluidClassification,
        EquipmentType, FluidPhasePED, GHSClassification,
    )
    from report_engine.generator import ReportGenerator

    ped = PEDClassificationEngine().classify(ClassificationInput(
        equipment_type=EquipmentType.VESSEL, ps_mpa=1.5, volume_liters=1600.0,
        ts_min_c=-10.0, ts_max_c=200.0,
        fluids=[FluidClassification(
            fluid_name="Air", phase=FluidPhasePED.GAS,
            ghs_classifications=[GHSClassification.HIGH_PRESSURE_GAS],
        )],
    ))
    html = ReportGenerator().generate(project, calc_result, ped_result=ped).html_content
    assert "PED Kategorisi" in html
    assert "Uygunluk Modülleri" in html
    # PED çalıştırılmadı notu OLMAMALI
    assert "PED sınıflandırması bu rapor için çalıştırılmadı" not in html


def test_report_esr_matrix_with_compliance(project, calc_result):
    """compliance verilince 19. bölüm gerçek ESR maddeleriyle dolar."""
    from compliance import ESRMatrix
    from report_engine.generator import ReportGenerator

    esr = ESRMatrix.default_for_vessel()
    html = ReportGenerator().generate(project, calc_result, compliance=esr).html_content
    assert "Temel Güvenlik Gereklilikleri" in html
    assert "uygulanabilir madde" in html
    assert "Faz 4'te" not in html
