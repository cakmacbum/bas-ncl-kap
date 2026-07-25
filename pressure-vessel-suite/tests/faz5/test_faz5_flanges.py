"""Faz 5 — Flanges modülü testleri.

Golden-case ve durum testleri.
Referans: ASME BPVC Section VIII Division 1, Appendix 2.
"""

import pytest
from units import relative_tolerance

from flanges.formulas import (
    hydrostatic_end_force,
    bolt_load_operating,
    flange_moment,
    hub_longitudinal_stress,
    radial_flange_stress,
    tangential_flange_stress,
    average_flange_stress,
    flange_stress_check,
)
from flanges.flange_calc import FlangeCalculator

from domain import (
    DesignConditions,
    MaterialProperty,
    ProductForm,
)


# ── Formül testleri ────────────────────────────────────────────────────────────

class TestFlangeFormulas:
    """Flanş formüllerinin birim testleri."""

    def test_hydrostatic_end_force(self):
        """Appendix 2-5 — Hidrostatik uç kuvveti.

        P = 1.2 MPa, G = 500 mm
        H = π/4 × 500² × 1.2 = 196349.5 × 1.2 = 235619.4 N
        """
        H = hydrostatic_end_force(1.2, 500.0)
        assert relative_tolerance(H, 235619.4, 0.01), f"H={H}"

    def test_bolt_load_operating(self):
        """Appendix 2-5(a) — İşletme durumu cıvata yükü."""
        W = bolt_load_operating(235619.4, 50000.0)
        assert relative_tolerance(W, 285619.4, 0.01)

    def test_flange_moment(self):
        """Appendix 2-6 — Flanş momenti.

        H_D = 235619 N, h_D = 250 mm
        H_G = 50000 N, h_G = 300 mm
        H_T = 10000 N, h_T = 200 mm
        M = 235619×250 + 50000×300 + 10000×200
          = 58904750 + 15000000 + 2000000 = 75904750 N·mm
        """
        M = flange_moment(235619.0, 250.0, 50000.0, 300.0, 10000.0, 200.0)
        assert relative_tolerance(M, 75904750.0, 0.01), f"M={M}"

    def test_hub_longitudinal_stress(self):
        """Appendix 2-7 — Hub boyuna gerilme.

        M = 75904750 N·mm, f = 1.0, g1 = 25 mm, h0 = 50 mm
        S_H = 75904750×1.0 / (25²×50) = 75904750 / 31250 = 2429.0 MPa
        (Bu çok yüksek — sadece formül doğrulaması)
        """
        S_H = hub_longitudinal_stress(75904750.0, 1.0, 25.0, 50.0)
        assert relative_tolerance(S_H, 2429.0, 0.01), f"S_H={S_H}"

    def test_radial_flange_stress(self):
        """Appendix 2-7 — Radyal flanş gerilmesi.

        M = 75904750 N·mm, B = 500 mm, t = 50 mm
        S_R = 4×75904750 / (50²×500) = 303619000 / 1250000 = 242.9 MPa
        """
        S_R = radial_flange_stress(75904750.0, 500.0, 50.0, 50.0)
        assert relative_tolerance(S_R, 242.9, 0.01), f"S_R={S_R}"

    def test_tangential_flange_stress(self):
        """Appendix 2-7 — Teğetsel flanş gerilmesi.

        M = 75904750, Y = 9.0, t = 50, B = 500
        S_T = 75904750×9.0 / (50²×500) = 683142750 / 1250000 = 546.5 MPa
        """
        S_T = tangential_flange_stress(75904750.0, 9.0, 50.0, 500.0)
        assert relative_tolerance(S_T, 546.5, 0.01), f"S_T={S_T}"

    def test_flange_stress_check_pass(self):
        """Gerilme kontrolü — PASS."""
        passed, msg = flange_stress_check(100.0, 50.0, 60.0, 55.0, 138.0)
        assert passed is True

    def test_flange_stress_check_fail(self):
        """Gerilme kontrolü — FAIL (S_H > 1.5×S_allow)."""
        S_allow = 100.0
        S_H = 200.0  # 1.5×100 = 150 → 200 > 150
        passed, msg = flange_stress_check(S_H, 50.0, 60.0, 55.0, S_allow)
        assert passed is False
        assert "S_H" in msg


# ── Calculator entegrasyon testleri ───────────────────────────────────────────

class TestFlangeCalculator:
    """FlangeCalculator entegrasyon testleri."""

    @pytest.fixture
    def calc(self):
        return FlangeCalculator()

    @pytest.fixture
    def mat(self):
        return MaterialProperty(
            material_id="MAT-FLANGE",
            standard_pack="ASME II-D 2025",
            material_designation="SA-105",
            product_form=ProductForm.FORGING,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=250.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 1",
        )

    def test_flange_stress_pass(self, calc, mat):
        """Flanş gerilme kontrolü — PASS."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-01",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h0": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 300000.0,
            "moment_M": 5000000.0,  # Düşük moment → düşük gerilme
            "flange_factor_Y": 9.0,
            "flange_factor_f": 1.0,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "Appendix 2"
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_flange_stress_fail(self, calc, mat):
        """Flanş gerilme kontrolü — FAIL (yüksek moment)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-02",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h0": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 500000.0,
            "moment_M": 100000000.0,  # Çok yüksek moment
            "flange_factor_Y": 9.0,
            "flange_factor_f": 1.0,
        })
        assert r.status.value == "FAIL"

    def test_traceability(self, calc, mat):
        """K5: İzlenebilirlik."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-03",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h0": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 300000.0,
            "moment_M": 5000000.0,
        })
        assert len(r.intermediate_values) > 0
        assert r.material_properties_used != {}

    def test_moment_calculation(self, calc):
        """Moment hesaplama."""
        result = calc.calculate_moment_from_pressure({
            "P": 1.2,
            "G": 500.0,
            "B": 500.0,
            "h_D": 250.0,
            "h_G": 300.0,
            "h_T": 200.0,
            "H_p": 50000.0,
        })
        assert "H" in result
        assert "M" in result
        assert result["H"] > 0
        assert result["M"] > 0
