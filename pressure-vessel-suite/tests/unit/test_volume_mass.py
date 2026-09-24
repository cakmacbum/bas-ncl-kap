"""Hacim ve ağırlık hesaplama testleri."""

import math

import pytest

from domain import (
    CalculationCode,
    ComponentReference,
    Cone,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
)
from calc_core.volume_mass import (
    MassResult,
    VesselVolumeMassReport,
    VolumeResult,
    calculate_mass,
    calculate_vessel_volume_mass,
    cone_volume,
    head_volume,
    shell_volume,
)
from units import relative_tolerance


def test_cone_volume_is_reported_in_component_chain():
    cone = Cone(
        cone_id="C1", large_diameter=1000.0, small_diameter=500.0,
        half_apex_angle=20.0, length=1000.0, nominal_thickness=10.0,
        material_id="M1",
    )
    vr = cone_volume(cone)
    assert vr.component_type == "cone"
    assert vr.inner_volume_mm3 > 0
    assert vr.metal_volume_mm3 > 0


# ── Gövde hacmi ───────────────────────────────────────────────────────────────

class TestShellVolume:
    """Silindirik gövde hacim testleri."""

    def test_basic_shell_volume(self):
        """Temel gövde hacmi: D_i=1000, L=2000, t=12."""
        shell = ShellSection(
            section_id="S1",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="M1",
        )
        vr = shell_volume(shell)

        r_inner = 500.0
        r_outer = 512.0
        L = 2000.0

        expected_inner = math.pi * r_inner**2 * L
        expected_outer = math.pi * r_outer**2 * L

        assert relative_tolerance(vr.inner_volume_mm3, expected_inner, 0.001)
        assert relative_tolerance(vr.outer_volume_mm3, expected_outer, 0.001)
        assert vr.metal_volume_mm3 > 0
        assert vr.component_type == "shell"

    def test_shell_with_corrosion_allowance(self):
        """Korozyon payı iç hacmi küçültmeli."""
        shell_no_ca = ShellSection(
            section_id="S1",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="M1",
            internal_corrosion_allowance=0.0,
        )
        shell_with_ca = ShellSection(
            section_id="S1",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="M1",
            internal_corrosion_allowance=3.0,
        )

        vr_no = shell_volume(shell_no_ca)
        vr_with = shell_volume(shell_with_ca)

        assert vr_with.inner_volume_mm3 < vr_no.inner_volume_mm3
        # Korozyon payı metal hacmini artırmalı (daha az iç hacim → daha çok metal)
        assert vr_with.metal_volume_mm3 > vr_no.metal_volume_mm3

    def test_shell_volume_liters(self):
        """Litre dönüşümü doğru olmalı."""
        shell = ShellSection(
            section_id="S1",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="M1",
        )
        vr = shell_volume(shell)

        # 1 litre = 10^6 mm³
        expected_liters = vr.inner_volume_mm3 / 1e6
        assert relative_tolerance(vr.inner_volume_liters, expected_liters, 0.001)


# ── Bombe hacmi ───────────────────────────────────────────────────────────────

class TestHeadVolume:
    """Bombe hacim testleri."""

    def test_elliptical_head_volume(self):
        """2:1 elipsoidal bombe hacmi."""
        head = Head(
            head_id="H1",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=0.0,
        )
        vr = head_volume(head)

        # 2:1 elipsoidal: a = 500, b = 250
        # V = (2/3) × π × a² × b = (2/3) × π × 500² × 250
        expected = (2.0 / 3.0) * math.pi * 500**2 * 250
        assert relative_tolerance(vr.inner_volume_mm3, expected, 0.01)
        assert vr.metal_volume_mm3 > 0

    def test_elliptical_with_straight_flange(self):
        """Düz flanş hacmi eklenmeli."""
        head_no_sf = Head(
            head_id="H1",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=0.0,
        )
        head_with_sf = Head(
            head_id="H1",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=25.0,
        )

        vr_no = head_volume(head_no_sf)
        vr_with = head_volume(head_with_sf)

        # Düz flanş eklenince hacim artmalı
        assert vr_with.inner_volume_mm3 > vr_no.inner_volume_mm3

    def test_hemispherical_head_volume(self):
        """Yarım küresel bombe hacmi."""
        head = Head(
            head_id="H1",
            type=HeadType.HEMISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=0.0,
        )
        vr = head_volume(head)

        # Yarım küre: V = (2/3) × π × r³ = (2/3) × π × 500³
        expected = (2.0 / 3.0) * math.pi * 500**3
        assert relative_tolerance(vr.inner_volume_mm3, expected, 0.01)

    def test_head_types_produce_different_volumes(self):
        """Farklı bombe tipleri farklı hacim üretmeli."""
        d = 1000.0
        t = 12.0

        head_e = Head(head_id="H", type=HeadType.ELLIPTICAL, inside_diameter=d, nominal_thickness=t, material_id="M")
        head_h = Head(head_id="H", type=HeadType.HEMISPHERICAL, inside_diameter=d, nominal_thickness=t, material_id="M")

        vr_e = head_volume(head_e)
        vr_h = head_volume(head_h)

        # Yarım küre > elipsoidal (aynı çapta)
        assert vr_h.inner_volume_mm3 > vr_e.inner_volume_mm3


# ── Ağırlık ───────────────────────────────────────────────────────────────────

class TestMass:
    """Ağırlık hesaplama testleri."""

    def test_basic_mass_calculation(self):
        """Temel ağırlık: V × ρ."""
        # 1 m³ = 10^9 mm³
        # 7850 kg/m³ × 1 m³ = 7850 kg
        mass = calculate_mass(1e9, 7850.0)
        assert relative_tolerance(mass, 7850.0, 0.001)

    def test_mass_zero_volume(self):
        """Sıfır hacim → sıfır ağırlık."""
        assert calculate_mass(0.0, 7850.0) == 0.0

    def test_mass_with_different_density(self):
        """Farklı yoğunluk → farklı ağırlık."""
        mass_steel = calculate_mass(1e9, 7850.0)
        mass_aluminum = calculate_mass(1e9, 2700.0)
        assert mass_steel > mass_aluminum


# ── Tam rapor ─────────────────────────────────────────────────────────────────

class TestVesselVolumeMassReport:
    """Kap hacim + ağırlık raporu testleri."""

    @pytest.fixture
    def sample_project(self):
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=2.0,
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
        )
        head_l = Head(
            head_id="HEAD-L",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
            straight_flange_length=25.0,
        )
        head_r = Head(
            head_id="HEAD-R",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
            straight_flange_length=25.0,
        )
        mat = MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
            density=7850.0,
        )
        return VesselProject(
            project_number="VM-001",
            project_name="Volume Mass Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            heads=[head_l, head_r],
            materials=[mat],
        )

    def test_report_has_all_components(self, sample_project):
        """Rapor tüm bileşenleri içermeli."""
        report = calculate_vessel_volume_mass(sample_project)
        assert len(report.volume_results) == 3  # 1 shell + 2 heads
        assert len(report.mass_results) == 3

    def test_total_inner_volume_positive(self, sample_project):
        """Toplam iç hacim pozitif olmalı."""
        report = calculate_vessel_volume_mass(sample_project)
        assert report.total_inner_volume_mm3 > 0
        assert report.total_inner_volume_liters > 0
        assert report.total_inner_volume_m3 > 0

    def test_total_metal_mass_positive(self, sample_project):
        """Toplam metal ağırlığı pozitif olmalı."""
        report = calculate_vessel_volume_mass(sample_project)
        assert report.total_metal_mass_kg > 0

    def test_report_to_dict(self, sample_project):
        """Rapor dict'e çevrilebilmeli."""
        report = calculate_vessel_volume_mass(sample_project)
        d = report.to_dict()
        assert "total_inner_volume_liters" in d
        assert "total_metal_mass_kg" in d
        assert len(d["components"]) == 3

    def test_mass_increases_with_thickness(self, sample_project):
        """Kalınlık artınca ağırlık artmalı."""
        thin = sample_project.model_copy()
        # İnce versiyon
        thin_shell = sample_project.shell_sections[0].model_copy(update={"nominal_thickness": 8.0})
        thin = thin.model_copy(update={"shell_sections": [thin_shell]})

        thick_shell = sample_project.shell_sections[0].model_copy(update={"nominal_thickness": 20.0})
        thick = sample_project.model_copy(update={"shell_sections": [thick_shell]})

        report_thin = calculate_vessel_volume_mass(thin)
        report_thick = calculate_vessel_volume_mass(thick)

        assert report_thick.total_metal_mass_kg > report_thin.total_metal_mass_kg

    def test_volume_liters_reasonable(self, sample_project):
        """Hacim makul aralıkta olmalı (D=1m, L=2m → ~1500 litre civarı)."""
        report = calculate_vessel_volume_mass(sample_project)
        # Silindir: π × 0.498² × 2.0 ≈ 1558 litre
        # + 2 bombe ≈ 130 litre
        # Toplam ≈ 1688 litre
        assert 1000 < report.total_inner_volume_liters < 2500

    def test_volume_mass_follows_explicit_component_sequence(self, sample_project):
        cone = Cone(
            cone_id="C1", large_diameter=1000.0, small_diameter=800.0,
            half_apex_angle=10.0, length=500.0, nominal_thickness=10.0,
            material_id=sample_project.shell_sections[0].material_id,
        )
        project = sample_project.model_copy(update={
            "cones": [cone],
            "component_sequence": [
                ComponentReference(component_type="head", component_id="HEAD-L"),
                ComponentReference(component_type="shell", component_id="SHELL-01"),
                ComponentReference(component_type="cone", component_id="C1"),
                ComponentReference(component_type="head", component_id="HEAD-R"),
            ],
        })
        report = calculate_vessel_volume_mass(project)
        assert [item.component_id for item in report.volume_results] == [
            "HEAD-L", "SHELL-01", "C1", "HEAD-R"
        ]
