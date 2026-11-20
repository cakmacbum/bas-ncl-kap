"""Paket A1+A2 — MAWP düzeltmeleri ve durum kontrolleri testleri.

Kapsam:
- A1: ASME VIII-1 UG-34 düz kapak MAWP korozyonlu çap (d = D) ve gidiş-dönüş testi (CA > 0).
- A1: Dairesel olmayan düz kapak (flat_z_factor) için NOT_CALCULATED kontrolü.
- A2: MAWP < P iken FAIL durumu ve uyarı mesajı (ASME gövde, bombe; EN gövde, koni).
- A2: MAWP >= P iken PASS ve utilization = P / MAWP.
- A2: Statik kafa düzeltmesinde corrected_mawp < P iken FAIL ve global MAWP yönetimi.
"""

import math
import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_asme_viii_1 import ASMEVIII1DesignCode
from code_en_13445 import EN13445DesignCode
from domain import (
    CalculationCode,
    Cone,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
    WeldJoint,
)
from domain import ComponentReference
from domain.enums import CalculationStatus


@pytest.fixture
def asme_code():
    return ASMEVIII1DesignCode(edition="2025")


@pytest.fixture
def en_code():
    return EN13445DesignCode(edition="2021")


@pytest.fixture
def base_material():
    return MaterialProperty(
        material_id="MAT-01",
        standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=138.0,
        yield_strength=260.0,
        tensile_strength=485.0,
        source_reference="ASME II-D",
    )


@pytest.fixture
def en_material():
    return MaterialProperty(
        material_id="MAT-EN",
        standard_pack="EN 10028-3",
        material_designation="P355NH",
        product_form=ProductForm.PLATE,
        temperature=20.0,
        allowable_stress=163.0,
        yield_strength=295.0,
        tensile_strength=490.0,
        source_reference="EN 10028-3",
    )


@pytest.fixture
def base_weld():
    return WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        weld_category="A",
        joint_efficiency=1.0,
        full_penetration=True,
    )


# ── A1: Düz Kapak MAWP Çapı ve Gidiş-Dönüş (Round-Trip) Testleri ──────────────

class TestA1FlatHeadMawp:
    """A1 düzeltmesi: Düz kapak MAWP'de korozyonlu iç çap D kullanılır."""

    def test_flat_head_round_trip_with_corrosion(self, asme_code, base_material, base_weld):
        """CA > 0 iken kalınlık yolunun verdiği t_required ile MAWP hesabı ≈ P (±%0,1)."""
        P = 1.5  # MPa
        D_inside = 800.0  # mm
        ca_i = 3.0  # mm
        ca_o = 1.0  # mm
        C_attach = 0.33

        dc = DesignConditions(
            operating_pressure=1.2,
            design_pressure=P,
            maximum_allowable_pressure_ps=2.0,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=ca_i,
        )

        flat_head = Head(
            head_id="HEAD-FLAT",
            type=HeadType.FLAT,
            inside_diameter=D_inside,
            nominal_thickness=50.0,
            material_id=base_material.material_id,
            weld_joint_id=base_weld.joint_id,
            internal_corrosion_allowance=ca_i,
            external_corrosion_allowance=ca_o,
            mill_tolerance=12.5,  # her iki yolda aynı sac toleransı (0 -> kalınlık yolu varsayılan %12,5 alır)
            flat_attachment_factor=C_attach,
        )

        # 1. Kalınlık hesabı
        thick_res = asme_code.calculate_head_thickness({
            "head": flat_head,
            "design_conditions": dc,
            "materials": [base_material],
            "welds": [base_weld],
            "code_edition": "2025",
        })
        t_req = thick_res.final_result
        assert t_req is not None and t_req > 0

        # 2. Kalınlık yolunun hesapladığı t_required ile MAWP hesabı
        # (t_req = gerekli nominal; MAWP yolu aynı mill_tolerance ile teslim kalınlığına çevirir)
        mawp_res = asme_code.calculate_mawp({
            "component_type": "head",
            "component": flat_head,
            "design_conditions": dc,
            "materials": [base_material],
            "welds": [base_weld],
            "nominal_thickness": t_req,
            "code_edition": "2025",
        })

        calculated_mawp = mawp_res.final_result
        # Gidiş-dönüş ±%0,1 (rel=0.001) içinde tam olarak P'ye eşit olmalı
        assert calculated_mawp == pytest.approx(P, rel=1e-3)
        # d_corroded ara değeri D = inside_diameter + 2*C olmalı
        assert mawp_res.intermediate_values
        d_inter = next(iv["value"] for iv in mawp_res.intermediate_values if iv["name"] == "d_corroded")
        assert d_inter == pytest.approx(D_inside + 2 * ca_i)

    def test_flat_head_non_circular_z_factor_not_calculated(self, asme_code, base_material, base_weld):
        """flat_z_factor girildiğinde MAWP sessizce atlanmaz; açıkça NOT_CALCULATED döner."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=2.0,
        )

        flat_head_non_circ = Head(
            head_id="HEAD-NON-CIRC",
            type=HeadType.FLAT,
            inside_diameter=600.0,
            nominal_thickness=40.0,
            material_id=base_material.material_id,
            weld_joint_id=base_weld.joint_id,
            internal_corrosion_allowance=2.0,
            flat_attachment_factor=0.33,
            flat_z_factor=1.25,  # Dairesel olmayan kapak Z faktörü
        )

        res = asme_code.calculate_mawp({
            "component_type": "head",
            "component": flat_head_non_circ,
            "design_conditions": dc,
            "materials": [base_material],
            "welds": [base_weld],
            "nominal_thickness": 40.0,
            "code_edition": "2025",
        })

        assert res.status == CalculationStatus.NOT_CALCULATED
        assert any("UG-34(c)(3)" in w for w in res.warnings)


# ── A2: MAWP < P FAIL, MAWP >= P PASS Testleri ───────────────────────────────

class TestA2MawpPassFailStatus:
    """A2: MAWP satırı durumu tasarım basıncı P ile kıyaslanarak belirlenir (DEC-008)."""

    def test_asme_shell_mawp_below_design_pressure_fails(self, asme_code, base_material, base_weld):
        """ASME silindirik gövdede MAWP < P ise FAIL ve uyarı verilmeli."""
        P = 2.0  # MPa
        dc = DesignConditions(
            operating_pressure=1.5,
            design_pressure=P,
            maximum_allowable_pressure_ps=2.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=2.0,
        )
        # Çok ince gövde: t_nom = 4.0 mm, mill_tolerance %12.5 -> t_actual = 3.5 mm, net cidar = 1.5 mm
        shell = ShellSection(
            section_id="SHELL-THIN",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=4.0,
            material_id=base_material.material_id,
            weld_joint_id=base_weld.joint_id,
            internal_corrosion_allowance=2.0,
            mill_tolerance=12.5,
        )

        res = asme_code.calculate_mawp({
            "component_type": "shell",
            "component": shell,
            "design_conditions": dc,
            "materials": [base_material],
            "welds": [base_weld],
            "nominal_thickness": shell.nominal_thickness,
            "code_edition": "2025",
        })

        assert res.final_result is not None
        assert res.final_result < P
        assert res.status == CalculationStatus.FAIL
        assert res.utilization_ratio == pytest.approx(P / res.final_result)
        assert any("tasarım basıncının" in w and "altında" in w for w in res.warnings)

    def test_asme_shell_mawp_above_design_pressure_passes(self, asme_code, base_material, base_weld):
        """ASME silindirik gövdede MAWP >= P ise PASS ve utilization = P / MAWP."""
        P = 1.0  # MPa
        dc = DesignConditions(
            operating_pressure=0.8,
            design_pressure=P,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=2.0,
        )
        shell = ShellSection(
            section_id="SHELL-OK",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=16.0,
            material_id=base_material.material_id,
            weld_joint_id=base_weld.joint_id,
            internal_corrosion_allowance=2.0,
            mill_tolerance=12.5,
        )

        res = asme_code.calculate_mawp({
            "component_type": "shell",
            "component": shell,
            "design_conditions": dc,
            "materials": [base_material],
            "welds": [base_weld],
            "nominal_thickness": shell.nominal_thickness,
            "code_edition": "2025",
        })

        assert res.final_result is not None
        assert res.final_result >= P
        assert res.status == CalculationStatus.PASS
        assert res.utilization_ratio == pytest.approx(P / res.final_result)

    def test_en_shell_mawp_below_design_pressure_fails(self, en_code, en_material):
        """EN 13445 silindirik gövdede MAWP < P ise FAIL ve uyarı verilmeli."""
        P = 2.5  # MPa
        dc = DesignConditions(
            operating_pressure=2.0,
            design_pressure=P,
            maximum_allowable_pressure_ps=3.0,
            operating_temperature=20.0,
            design_temperature=20.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=1.0,
        )
        shell = ShellSection(
            section_id="SHELL-EN-THIN",
            inside_diameter=1000.0,
            tangent_length=1500.0,
            nominal_thickness=3.0,  # İnce cidar
            material_id=en_material.material_id,
            internal_corrosion_allowance=1.0,
        )

        res = en_code.calculate_mawp({
            "component_type": "shell",
            "component": shell,
            "design_conditions": dc,
            "materials": [en_material],
            "welds": [],
            "nominal_thickness": shell.nominal_thickness,
            "code_edition": "2021",
        })

        assert res.final_result is not None
        assert res.final_result < P
        assert res.status == CalculationStatus.FAIL
        assert res.utilization_ratio == pytest.approx(P / res.final_result)
        assert any("tasarım basıncının" in w and "altında" in w for w in res.warnings)

    def test_en_cone_mawp_below_design_pressure_fails(self, en_code, en_material):
        """EN 13445 konide (_cone_mawp) MAWP < P ise FAIL ve uyarı verilmeli."""
        P = 3.0  # MPa
        dc = DesignConditions(
            operating_pressure=2.0,
            design_pressure=P,
            maximum_allowable_pressure_ps=3.5,
            operating_temperature=20.0,
            design_temperature=20.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=1.0,
        )
        cone = Cone(
            cone_id="CONE-EN-THIN",
            large_diameter=1000.0,
            small_diameter=500.0,
            half_apex_angle=30.0,
            length=433.0,
            nominal_thickness=3.0,
            material_id=en_material.material_id,
            internal_corrosion_allowance=1.0,
        )

        res = en_code.calculate_mawp({
            "component_type": "cone",
            "component": cone,
            "design_conditions": dc,
            "materials": [en_material],
            "welds": [],
            "nominal_thickness": cone.nominal_thickness,
            "code_edition": "2021",
        })

        assert res.final_result is not None
        assert res.final_result < P
        assert res.status == CalculationStatus.FAIL
        assert res.utilization_ratio == pytest.approx(P / res.final_result)
        assert any("tasarım basıncının" in w and "altında" in w for w in res.warnings)


# ── A2: Statik Kafa Düzeltmesi ve Global MAWP ─────────────────────────────────

def _kalin_bombe(hid, mat, weld):
    return Head(
        head_id=hid, type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
        nominal_thickness=40.0, material_id=mat.material_id, weld_joint_id=weld.joint_id,
        internal_corrosion_allowance=0.0, mill_tolerance=12.5,
    )


class TestA2StaticHeadAndGlobalMawp:
    """Statik kafa düzeltmesi sonrası MAWP < P kontrolü."""

    def test_static_head_drops_mawp_below_design_pressure(self, asme_code, base_material, base_weld):
        """Statik kafa MAWP'yi tasarım basıncının altına düşürdüğünde FAIL olmalı."""
        P = 1.0  # MPa
        # Sıvı seviyesi 50 m (50000 mm), su yoğunluğu 1000 kg/m³ -> delta_p ≈ 0.49 MPa
        dc = DesignConditions(
            operating_pressure=0.8,
            design_pressure=P,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=0.0,
            fluid_density_kg_m3=1000.0,
            liquid_level_mm=50000.0,
        )

        # Ham MAWP ≈ 1.3 MPa (> P) olacak şekilde gövde
        # t = 5.0 mm, R = 500 mm, S = 138 MPa -> MAWP = 138 * 1 * 5 / (500 + 0.6 * 5) = 1.37 MPa
        shell = ShellSection(
            section_id="S-TALL",
            inside_diameter=1000.0,
            tangent_length=50000.0,
            nominal_thickness=5.0,
            material_id=base_material.material_id,
            weld_joint_id=base_weld.joint_id,
            internal_corrosion_allowance=0.0,
            mill_tolerance=0.0,
        )

        project = VesselProject(
            project_number="P-STATIC",
            project_name="Static Head Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            heads=[_kalin_bombe("HL", base_material, base_weld), _kalin_bombe("HR", base_material, base_weld)],
            component_sequence=[
                ComponentReference(component_type="head", component_id="HL"),
                ComponentReference(component_type="shell", component_id="S-TALL"),
                ComponentReference(component_type="head", component_id="HR"),
            ],
            materials=[base_material],
            welds=[base_weld],
        )

        orch = CalculationOrchestrator(asme_code)
        res = orch.run(project)

        mawp_rows = [r for r in res.results if r.calculation_type == "mawp" and r.component_id == "S-TALL"]
        assert len(mawp_rows) == 1
        mawp_r = mawp_rows[0]

        # delta_p ≈ 0.49 MPa, corrected_mawp ≈ 1.37 - 0.49 = 0.88 MPa < P (1.0 MPa)
        assert mawp_r.final_result < P
        assert mawp_r.status == CalculationStatus.FAIL
        assert mawp_r.utilization_ratio == pytest.approx(P / mawp_r.final_result)
        assert any("tasarım basıncının" in w and "altında" in w for w in mawp_r.warnings)
