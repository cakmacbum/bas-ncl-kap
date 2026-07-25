"""Faz 5 — External-pressure modülü testleri.

Golden-case ve durum testleri.
Referans: ASME BPVC Section VIII Division 1, UG-28.
"""

import pytest
from units import relative_tolerance

from external_pressure.formulas import (
    ExternalPressureResult,
    shell_external_pressure_allowable,
    shell_external_pressure_required_thickness,
    head_external_pressure_allowable,
)
from external_pressure.ext_pressure import ExternalPressureCalculator

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
)


# ── Formül testleri ────────────────────────────────────────────────────────────

class TestExternalPressureFormulas:
    """Dış basınç formüllerinin birim testleri."""

    def test_shell_allowable_pressure_basic(self):
        """UG-28 — Temel izin verilen dış basınç.

        D = 1024 mm, L = 2000 mm, t = 12 mm
        L/D = 1.953, D/t = 85.33
        A = 0.0003 (grafik), B = 80 MPa (grafik)
        P_allow = 4×80 / (3×85.33) = 320 / 256 = 1.25 MPa
        """
        P_allow, detail = shell_external_pressure_allowable(
            D=1024.0, L=2000.0, t=12.0, A=0.0003, B=80.0, P_external=0.5,
        )
        assert relative_tolerance(P_allow, 1.25, 0.01), f"P_allow={P_allow}"
        assert relative_tolerance(detail.L_over_D, 1.953, 0.01)
        assert relative_tolerance(detail.D_over_t, 85.33, 0.01)

    def test_shell_allowable_pressure_pass(self):
        """Dış basınç P_allow altında → PASS."""
        P_allow, _ = shell_external_pressure_allowable(
            D=1024.0, L=2000.0, t=12.0, A=0.0003, B=80.0, P_external=0.5,
        )
        assert P_allow > 0.5

    def test_shell_allowable_pressure_fail(self):
        """Dış basınç P_allow üstünde → FAIL."""
        P_allow, _ = shell_external_pressure_allowable(
            D=1024.0, L=2000.0, t=12.0, A=0.0003, B=80.0, P_external=2.0,
        )
        assert P_allow < 2.0

    def test_head_allowable_pressure(self):
        """UG-33 — Bombe dış basınç.

        D = 1000 mm, t = 12 mm, A = 0.0003, B = 80 MPa
        P_allow = 8×80×12 / (3×1000) = 7680/3000 = 2.56 MPa
        """
        P_allow, detail = head_external_pressure_allowable(
            D=1000.0, t=12.0, A=0.0003, B=80.0,
        )
        assert relative_tolerance(P_allow, 2.56, 0.01), f"P_allow={P_allow}"

    def test_shell_required_thickness(self):
        """Dış basınç için gerekli kalınlık."""
        t_req, detail = shell_external_pressure_required_thickness(
            D=1024.0, L=2000.0, P_external=0.5, A=0.0003, B=80.0, C=2.0,
        )
        # P = 4B/(3×D/t) → D/t = 4B/(3P) = 320/1.5 = 213.33 → t = 1024/213.33 = 4.8
        # t_required = 4.8 + 2.0 = 6.8 mm
        assert t_req > 0
        assert t_req > 4.0  # korozyon payı dahil

    def test_invalid_inputs(self):
        """Geçersiz girdiler → ValueError."""
        with pytest.raises(ValueError):
            shell_external_pressure_allowable(D=0, L=2000, t=12, A=0.0003, B=80, P_external=0.5)
        with pytest.raises(ValueError):
            shell_external_pressure_allowable(D=1024, L=2000, t=12, A=0, B=80, P_external=0.5)


# ── Calculator entegrasyon testleri ───────────────────────────────────────────

class TestExternalPressureCalculator:
    """ExternalPressureCalculator entegrasyon testleri."""

    @pytest.fixture
    def calc(self):
        return ExternalPressureCalculator()

    @pytest.fixture
    def ext_dc(self):
        return DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            external_pressure=0.5,
            corrosion_allowance_internal=2.0,
        )

    @pytest.fixture
    def shell(self):
        return ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
        )

    @pytest.fixture
    def mat(self):
        return MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
        )

    def test_pass_scenario(self, calc, ext_dc, shell, mat):
        """Dış basınç yeterli kalınlıkla → PASS."""
        r = calc.check_shell_external_pressure({
            "shell": shell,
            "design_conditions": ext_dc,
            "materials": [mat],
            "strain_factor_A": 0.0003,
            "allowable_stress_B": 80.0,
            "unstiffened_length": 2000.0,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "UG-28"
        assert r.status.value == "PASS"
        assert r.final_result is not None
        assert r.final_result > 0

    def test_fail_scenario(self, calc, shell, mat):
        """Yüksek dış basınç → FAIL."""
        dc_high = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            external_pressure=3.0,  # Çok yüksek
            corrosion_allowance_internal=2.0,
        )
        r = calc.check_shell_external_pressure({
            "shell": shell,
            "design_conditions": dc_high,
            "materials": [mat],
            "strain_factor_A": 0.0003,
            "allowable_stress_B": 80.0,
        })
        assert r.status.value == "FAIL"

    def test_no_external_pressure(self, calc, shell, mat):
        """Dış basınç yok → NOT_CALCULATED."""
        dc_none = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            external_pressure=0.0,
        )
        r = calc.check_shell_external_pressure({
            "shell": shell,
            "design_conditions": dc_none,
            "materials": [mat],
        })
        assert r.status.value == "NOT CALCULATED"

    def test_missing_ab_factors(self, calc, ext_dc, shell, mat):
        """A/B faktörleri eksik → NOT_CALCULATED."""
        r = calc.check_shell_external_pressure({
            "shell": shell,
            "design_conditions": ext_dc,
            "materials": [mat],
            "strain_factor_A": 0.0,
            "allowable_stress_B": 0.0,
        })
        assert r.status.value == "NOT CALCULATED"

    def test_traceability(self, calc, ext_dc, shell, mat):
        """K5: İzlenebilirlik — ara değerler dolu."""
        r = calc.check_shell_external_pressure({
            "shell": shell,
            "design_conditions": ext_dc,
            "materials": [mat],
            "strain_factor_A": 0.0003,
            "allowable_stress_B": 80.0,
        })
        assert len(r.intermediate_values) > 0
        assert r.clause_reference != ""
        assert r.material_properties_used != {}

    def test_head_check(self, calc, ext_dc, mat):
        """Bombe dış basınç kontrolü."""
        head = Head(
            head_id="HEAD-L",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
        )
        r = calc.check_head_external_pressure({
            "head": head,
            "design_conditions": ext_dc,
            "materials": [mat],
            "strain_factor_A": 0.0003,
            "allowable_stress_B": 80.0,
        })
        assert r.clause_reference == "UG-33"
        assert r.status.value == "PASS"
