"""Test suite for EN 13445-3 Clause 8 external pressure & vacuum calculations.

Tests cover:
- Pure formulas for cylinders (8.5) and spherical shells/dished heads (8.7)
- Step-by-step hand calculation verification with relative tolerance <= 0.5%
- No external pressure returns empty list
- Vacuum condition defaults to 0.1 MPa
- PASS results are capped to REVIEW_REQUIRED (verified=False)
- Too thin shell triggers FAIL
- ASME UG-28 isolation (code == "EN 13445", clause starts with "EN 13445-3, 8.")
- Unsupported head types (FLAT) and cones return NOT_CALCULATED

Reference: EN 13445-3:2021+A1:2023 Clause 8
"""

import pytest

from domain import (
    CalculationCode,
    CalculationStatus,
    Cone,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
)
from units import relative_tolerance
from code_en_13445 import EN13445DesignCode
from code_en_13445 import external_pressure


# ── Fixtures & Project Helpers ────────────────────────────────────────────────

@pytest.fixture
def en_code():
    return EN13445DesignCode(edition="2021+A1:2023")


def make_en_project(
    p_ext: float = 0.0,
    vacuum: bool = False,
    shell_thk: float = 12.0,
    head_thk: float = 12.0,
    head_type: HeadType = HeadType.ELLIPTICAL,
    elastic_modulus: float | None = 200000.0,
    has_cone: bool = False,
) -> VesselProject:
    """Geometrik olarak tutarlı EN 13445 proje fixture oluşturucu (G01 uyumlu)."""
    dc = DesignConditions(
        operating_pressure=1.0,
        design_pressure=1.2,
        maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0,
        design_temperature=200.0,
        minimum_design_temperature=-10.0,
        corrosion_allowance_internal=2.0,
        hydrotest_temperature=20.0,
        external_pressure=p_ext,
        vacuum_condition=vacuum,
    )
    mat = MaterialProperty(
        material_id="MAT-EN-01",
        standard_pack="EN 10028-3:2017",
        material_designation="P355NH",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=163.0,
        yield_strength=295.0,
        tensile_strength=490.0,
        source_reference="EN 10028-3:2017, P355NH",
        elastic_modulus=elastic_modulus,
    )
    shell = ShellSection(
        section_id="SHELL-01",
        inside_diameter=1000.0,
        tangent_length=2000.0,
        nominal_thickness=shell_thk,
        material_id="MAT-EN-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,
    )
    head_l = Head(
        head_id="HEAD-L",
        type=head_type,
        inside_diameter=1000.0,
        nominal_thickness=head_thk,
        material_id="MAT-EN-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,
        crown_radius=1000.0 if head_type == HeadType.TORISPHERICAL else None,
        knuckle_radius=100.0 if head_type == HeadType.TORISPHERICAL else None,
    )
    head_r = Head(
        head_id="HEAD-R",
        type=head_type,
        inside_diameter=1000.0,
        nominal_thickness=head_thk,
        material_id="MAT-EN-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,
        crown_radius=1000.0 if head_type == HeadType.TORISPHERICAL else None,
        knuckle_radius=100.0 if head_type == HeadType.TORISPHERICAL else None,
    )
    cones = []
    if has_cone:
        cones.append(Cone(
            cone_id="CONE-01",
            large_diameter=1000.0,
            small_diameter=600.0,
            half_apex_angle=30.0,
            length=400.0,
            nominal_thickness=12.0,
            material_id="MAT-EN-01",
            internal_corrosion_allowance=2.0,
            mill_tolerance=10.0,
        ))

    return VesselProject(
        project_number="PRJ-EN-EXT-01",
        project_name="EN 13445 External Pressure Validation",
        calculation_code=CalculationCode.EN_13445,
        code_edition="2021+A1:2023",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        cones=cones,
        materials=[mat],
        welds=[],
    )


# ── Saf Fonksiyon ve Elle Hesaplama Testleri (Tolerans <= %0.5) ────────────────

class TestEN13445ExternalPressureFormulas:
    """EN 13445-3 Madde 8 saf matematik ve el hesabı doğrulama testleri."""

    def test_cylinder_analysis_thickness(self):
        """Analiz kalınlığı e_a = e - c - delta_e kontrolü."""
        # e = 12.0 mm, c = 2.0 mm, mill_tolerance = 10% -> delta_e = 1.2 mm -> ea = 8.8 mm
        ea = external_pressure.cylinder_analysis_thickness(12.0, 2.0, 10.0)
        assert abs(ea - 8.8) < 1e-9

        # mill_tolerance = 0 -> varsayılan %10
        ea_def = external_pressure.cylinder_analysis_thickness(12.0, 2.0, 0.0)
        assert abs(ea_def - 8.8) < 1e-9

    def test_cylinder_effective_length(self):
        """Takviye halkasız boy L = L_tangent + (1/3)*d1 + (1/3)*d2 kontrolü."""
        # 2000 + 250/3 + 250/3 = 2166.6667 mm
        L = external_pressure.cylinder_effective_length(2000.0, 250.0, 250.0)
        assert relative_tolerance(L, 2166.6667, 0.001)

    def test_cylinder_hand_calculation(self):
        """Silindirik gövde adım adım el hesabı doğrulaması (EN 13445-3, 8.5).

        Adım adım el hesabı:
        ---------------------
        Girdiler:
          E = 200 000 MPa, nu = 0.3
          sigma_e = 295.0 MPa (P355NH, 200 °C)
          e = 12.0 mm, c = 2.0 mm, delta_e = 1.2 mm (%10)
          e_a = 12.0 - 2.0 - 1.2 = 8.8 mm
          Di = 1000.0 mm, c = 2.0 mm -> R_corroded = 502.0 mm
          R_mean = 502.0 + 8.8 / 2 = 506.4 mm
          tangent_length = 2000.0 mm, 2:1 elipsoidal bombe derinliği d = 250.0 mm
          L = 2000.0 + 2 * (250.0 / 3) = 2166.6667 mm

        Elastik göçme p_m (8.5.2):
          Z = pi * R / L = pi * 506.4 / 2166.6667 = 0.734267
          Z^2 = 0.539148, Z^4 = 0.290680
          12 * (1 - nu^2) = 12 * 0.91 = 10.92
          bending_coeff = 8.8^2 / (10.92 * 506.4^2) = 2.76538e-5
          prefactor = 200000 * 8.8 / 506.4 = 3475.5134 MPa

          n = 2: epsilon = 0.0044207 -> p_m = 15.364 MPa
          n = 3: epsilon = 0.0006301 -> p_m = 2.190 MPa
          n = 4: epsilon = 0.00050689 -> p_m = 1.7617 MPa (minimum)
          n = 5: epsilon = 0.0007045 -> p_m = 2.4485 MPa
          Sonuç: governing_n = 4, p_m = 1.7617 MPa

        Akma basıncı p_y (8.5.2):
          p_y = sigma_e * e_a / R = 295.0 * 8.8 / 506.4 = 5.1264 MPa

        Oran ve Şekil 8.5-5:
          p_m / p_y = 1.7617 / 5.1264 = 0.34365 <= 1.0
          p_r / p_y = 0.5 * 0.34365 = 0.17183
          p_r = 0.17183 * 5.1264 = 0.88085 MPa

        İzin verilen basınç (S = 1.5):
          p_allow = p_r / 1.5 = 0.88085 / 1.5 = 0.5872 MPa
        """
        E = 200000.0
        sigma_e = 295.0
        ea = 8.8
        R = 506.4
        L = 2166.6667

        # 1. Elastik göçme basıncı ve dalga sayısı
        pm, n = external_pressure.cylinder_elastic_instability_pressure(E, ea, R, L)
        assert n == 4
        assert relative_tolerance(pm, 1.7617, 0.005)  # <= %0.5

        # 2. Akma basıncı
        py = external_pressure.cylinder_yield_pressure(sigma_e, ea, R)
        assert relative_tolerance(py, 5.1264, 0.005)  # <= %0.5

        # 3. İzin verilen dış basınç
        res = external_pressure.cylinder_external_pressure_allowable(E, sigma_e, ea, R, L, S=1.5)
        assert res["n"] == 4
        assert relative_tolerance(res["p_m"], 1.7617, 0.005)
        assert relative_tolerance(res["p_y"], 5.1264, 0.005)
        assert relative_tolerance(res["p_r"], 0.88085, 0.005)
        assert relative_tolerance(res["p_allow"], 0.5872, 0.005)

    def test_sphere_hand_calculation(self):
        """Küresel kabuk / bombe adım adım el hesabı doğrulaması (EN 13445-3, 8.7).

        Adım adım el hesabı:
        ---------------------
        Girdiler:
          E = 200 000 MPa, sigma_e = 295.0 MPa
          Taç yarıçapı R = 1002.0 mm (R_original = 1000 mm + c = 2 mm)
          e_a = 12.0 - 2.0 - 1.2 = 8.8 mm

        Elastik göçme p_m (8.7):
          p_m = 1.21 * E * (e_a^2 / R^2)
              = 1.21 * 200000 * (8.8 / 1002.0)^2
              = 242000 * 7.713117e-5 = 18.6657 MPa

        Akma basıncı p_y (8.7):
          p_y = 2 * sigma_e * e_a / R
              = 2 * 295.0 * 8.8 / 1002.0 = 5.1816 MPa

        Oran ve Şekil 8.7-1:
          p_m / p_y = 18.6657 / 5.1816 = 3.6023 > 1.0
          p_r / p_y = 1.0 - 0.5 / 3.6023 = 1.0 - 0.1388 = 0.8612
          p_r = 0.8612 * 5.1816 = 4.4624 MPa

        İzin verilen dış basınç (S = 1.5):
          p_allow = p_r / 1.5 = 4.4624 / 1.5 = 2.9749 MPa
        """
        E = 200000.0
        sigma_e = 295.0
        ea = 8.8
        R = 1002.0

        pm = external_pressure.sphere_elastic_instability_pressure(E, ea, R)
        assert relative_tolerance(pm, 18.6657, 0.005)  # <= %0.5

        py = external_pressure.sphere_yield_pressure(sigma_e, ea, R)
        assert relative_tolerance(py, 5.1816, 0.005)  # <= %0.5

        res = external_pressure.sphere_external_pressure_allowable(E, sigma_e, ea, R, S=1.5)
        assert relative_tolerance(res["p_m"], 18.6657, 0.005)
        assert relative_tolerance(res["p_y"], 5.1816, 0.005)
        assert relative_tolerance(res["pm_over_py"], 3.6023, 0.005)
        assert relative_tolerance(res["p_r"], 4.4624, 0.005)
        assert relative_tolerance(res["p_allow"], 2.9749, 0.005)

    def test_curves_behavior(self):
        """Şekil 8.5-5 ve 8.7-1 eğrisinin parçalı davranışı."""
        assert external_pressure.curve_figure_8_5_5(-0.1) == 0.0
        assert external_pressure.curve_figure_8_5_5(0.0) == 0.0
        assert external_pressure.curve_figure_8_5_5(0.5) == 0.25
        assert external_pressure.curve_figure_8_5_5(1.0) == 0.5
        assert abs(external_pressure.curve_figure_8_5_5(2.0) - 0.75) < 1e-9
        assert abs(external_pressure.curve_figure_8_5_5(10.0) - 0.95) < 1e-9
        assert external_pressure.curve_figure_8_7_1(2.0) == external_pressure.curve_figure_8_5_5(2.0)


# ── Entegrasyon Testleri (EN13445DesignCode.check_external_pressure) ───────────

class TestEN13445ExternalPressureIntegration:
    """EN13445DesignCode.check_external_pressure entegrasyon testleri."""

    def test_no_external_pressure_returns_empty_list(self, en_code):
        """Dış basınç yok (external_pressure=0 ve vacuum=False) -> boş liste []."""
        prj = make_en_project(p_ext=0.0, vacuum=False)
        results = en_code.check_external_pressure(prj)
        assert results == []

    def test_vacuum_condition_sets_p_0_1(self, en_code):
        """Vakum seçildiğinde (vacuum=True, p_ext=0) P = 0.1 MPa uygulanmalı."""
        prj = make_en_project(p_ext=0.0, vacuum=True)
        results = en_code.check_external_pressure(prj)
        assert len(results) == 3  # 1 shell + 2 heads
        for r in results:
            assert r.input_snapshot["P_ext_MPa"] == 0.1

    def test_pass_capped_to_review_required(self, en_code):
        """PASS asla dönmez — unverified formül olduğu için REVIEW_REQUIRED olmalı."""
        # Standart 12 mm cidar 0.1 MPa vakumda kolayca taşır (P_ext <= P_allow)
        prj = make_en_project(p_ext=0.1, vacuum=True)
        results = en_code.check_external_pressure(prj)
        assert len(results) > 0
        for r in results:
            assert r.status == CalculationStatus.REVIEW_REQUIRED
            assert any("verified=False" in msg for msg in r.warnings + r.assumptions)

    def test_thin_shell_fails(self, en_code):
        """Çok ince kabuk veya yüksek dış basınç -> FAIL."""
        # Nominal thickness 2.5 mm, corrosion 2.0 mm, mill_tolerance 10% -> ea = 0.25 mm
        # P_ext = 0.5 MPa (p_allow ~ 0.005 MPa)
        prj = make_en_project(p_ext=0.5, shell_thk=2.5, head_thk=2.5)
        results = en_code.check_external_pressure(prj)
        shell_res = next(r for r in results if r.component_type == "shell")
        assert shell_res.status == CalculationStatus.FAIL
        assert shell_res.utilization_ratio > 1.0

    def test_no_asme_fallback_code_and_clause(self, en_code):
        """ASME'ye asla fallback yok: code == 'EN 13445' ve clause 'EN 13445-3, 8.' ile başlar."""
        prj = make_en_project(p_ext=0.1)
        results = en_code.check_external_pressure(prj)
        assert len(results) == 3

        shell_res = next(r for r in results if r.component_type == "shell")
        assert shell_res.code == "EN 13445"
        assert shell_res.clause_reference.startswith("EN 13445-3, 8.5")

        for head_res in [r for r in results if r.component_type == "head"]:
            assert head_res.code == "EN 13445"
            assert head_res.clause_reference.startswith("EN 13445-3, 8.7")

    def test_unsupported_flat_head(self, en_code):
        """Düz kapak bombe tipi dış basınçta NOT_CALCULATED dönmeli."""
        prj = make_en_project(p_ext=0.1, head_type=HeadType.FLAT)
        results = en_code.check_external_pressure(prj)
        head_res = next(r for r in results if r.component_type == "head")
        assert head_res.status == CalculationStatus.NOT_CALCULATED
        assert head_res.clause_reference.startswith("EN 13445-3, 8.")
        assert any("flat head" in msg.lower() for msg in head_res.warnings)

    def test_unsupported_cone(self, en_code):
        """Konik bölüm bu pakette dış basınçta NOT_CALCULATED dönmeli."""
        prj = make_en_project(p_ext=0.1, has_cone=True)
        results = en_code.check_external_pressure(prj)
        cone_res = next(r for r in results if r.component_type == "cone")
        assert cone_res.status == CalculationStatus.NOT_CALCULATED
        assert cone_res.clause_reference.startswith("EN 13445-3, 8.")
        assert any("cone" in msg.lower() for msg in cone_res.warnings)

    def test_intermediate_values_and_traceability(self, en_code):
        """K5 denetlenebilirlik: p_m, p_y, p_r, L, n ara değerlerde bulunmalı."""
        prj = make_en_project(p_ext=0.1)
        results = en_code.check_external_pressure(prj)
        shell_res = next(r for r in results if r.component_type == "shell")
        names = [iv["name"] for iv in shell_res.intermediate_values]
        for expected in ("p_m", "p_y", "p_r", "p_allow", "L", "n", "e_a", "R"):
            assert expected in names, f"{expected} ara değerlerde bulunamadı"

    def test_material_elastic_modulus_fallback(self, en_code):
        """Malzemede elastic_modulus yoksa 200 000 MPa varsayılmalı ve uyarı eklenmeli."""
        prj = make_en_project(p_ext=0.1, elastic_modulus=None)
        results = en_code.check_external_pressure(prj)
        shell_res = next(r for r in results if r.component_type == "shell")
        assert shell_res.input_snapshot["E_MPa"] == 200000.0
        warnings_and_assumptions = " ".join(shell_res.warnings + shell_res.assumptions)
        assert "200000" in warnings_and_assumptions
