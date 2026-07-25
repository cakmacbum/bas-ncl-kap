"""Faz 5 — Supports modülü testleri.

Golden-case ve durum testleri — Zick analizi (saddle) ve skirt.
"""

import pytest
import math
from units import relative_tolerance

from supports.formulas import (
    saddle_reaction,
    zick_longitudinal_bending,
    zick_circumferential_saddle,
    zick_circumferential_crown,
    zick_shear_stress,
    saddle_stress_limits,
    skirt_bending_stress,
    skirt_compression_stress,
    skirt_combined_stress,
    skirt_base_pressure,
)
from supports.support_calc import SupportCalculator

from domain import (
    DesignConditions,
    MaterialProperty,
    ProductForm,
    ShellSection,
)


# ── Zick formül testleri ──────────────────────────────────────────────────────

class TestZickFormulas:
    """Zick analizi formüllerinin birim testleri."""

    def test_saddle_reaction(self):
        """Saddle reaksiyon kuvveti.

        W = 500000 N, n = 2 → Q = 250000 N
        """
        Q = saddle_reaction(500000.0, 2)
        assert relative_tolerance(Q, 250000.0, 0.001)

    def test_zick_longitudinal_bending(self):
        """Zick S1 — boyuna eğilme gerilmesi.

        Q = 250000 N, L = 4000 mm, R_m = 506 mm, t = 12 mm
        A = 800 mm, h = 0 mm
        K1 = 1 - (2×800/4000) / (1+0) = 1 - 0.4 = 0.6
        S1 = 250000×4000 / (4×π×506²×12) × 0.6
           = 1000000000 / (4×3.14159×256036×12) × 0.6
           = 1000000000 / 38610432 × 0.6
           = 25.9 × 0.6 = 15.54 MPa
        """
        S1 = zick_longitudinal_bending(250000.0, 4000.0, 506.0, 12.0, 800.0, 0.0)
        assert S1 > 0
        assert relative_tolerance(S1, 15.54, 0.05), f"S1={S1}"

    def test_zick_circumferential_saddle(self):
        """Zick S2 — saddle'da çevresel gerilme.

        Q = 250000 N, R_m = 506 mm, t = 12 mm, b = 200 mm
        eff = 200 + 1.56×sqrt(506×12) = 200 + 1.56×77.97 = 200 + 121.6 = 321.6
        S2 = 250000 / (4×12×321.6) = 250000 / 15436.8 = 16.2 MPa
        """
        S2 = zick_circumferential_saddle(250000.0, 506.0, 12.0, 200.0)
        assert S2 > 0
        assert relative_tolerance(S2, 16.2, 0.05), f"S2={S2}"

    def test_zick_circumferential_crown(self):
        """Zick S3 — taç noktasında çevresel gerilme."""
        S3 = zick_circumferential_crown(250000.0, 506.0, 12.0, 200.0, 4000.0)
        assert S3 > 0

    def test_zick_shear_stress(self):
        """Zick S4 — kesme gerilmesi."""
        S4 = zick_shear_stress(250000.0, 506.0, 12.0, 800.0, 4000.0)
        assert S4 > 0

    def test_saddle_stress_limits(self):
        """Saddle gerilme limitleri.

        S_allow = 138 MPa → limit = 0.67×138 = 92.46 MPa
        """
        S1_l, S2_l, S3_l, S4_l = saddle_stress_limits(138.0)
        assert relative_tolerance(S1_l, 92.46, 0.01)
        assert S1_l == S2_l == S3_l == S4_l


# ── Skirt formül testleri ─────────────────────────────────────────────────────

class TestSkirtFormulas:
    """Skirt formüllerinin birim testleri."""

    def test_skirt_bending_stress(self):
        """Skirt eğilme gerilmesi.

        M = 50000000 N·mm, D = 1000 mm, t = 10 mm
        S = 4×50000000 / (π×1000²×10) = 200000000 / 31415927 = 6.37 MPa
        """
        S = skirt_bending_stress(50000000.0, 1000.0, 10.0)
        assert relative_tolerance(S, 6.37, 0.01), f"S={S}"

    def test_skirt_compression_stress(self):
        """Skirt basma gerilmesi.

        W = 200000 N, D = 1000 mm, t = 10 mm
        S = 200000 / (π×1000×10) = 200000 / 31415.9 = 6.37 MPa
        """
        S = skirt_compression_stress(200000.0, 1000.0, 10.0)
        assert relative_tolerance(S, 6.37, 0.01), f"S={S}"

    def test_skirt_combined_stress(self):
        """Skirt birleşik gerilme."""
        S = skirt_combined_stress(6.37, 6.37)
        assert relative_tolerance(S, 12.74, 0.01)

    def test_skirt_base_pressure(self):
        """Skirt temel basıncı."""
        P = skirt_base_pressure(200000.0, 50000000.0, 1000.0, 10.0)
        assert P > 0


# ── Calculator entegrasyon testleri ───────────────────────────────────────────

class TestSupportCalculator:
    """SupportCalculator entegrasyon testleri."""

    @pytest.fixture
    def calc(self):
        return SupportCalculator()

    @pytest.fixture
    def shell(self):
        return ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=4000.0,
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

    def test_saddle_pass(self, calc, shell, mat):
        """Saddle kontrolü — PASS (düşük ağırlık)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_saddle({
            "support": {
                "tag": "SADDLE-01",
                "type": "saddle",
                "width_mm": 200.0,
                "height_mm": 0.0,
            },
            "shell": shell,
            "vessel_length": 4000.0,
            "saddle_distance": 4000.0,
            "saddle_from_end": 800.0,
            "total_weight_N": 100000.0,  # Düşük ağırlık
            "materials": [mat],
            "design_conditions": dc,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "Zick Analysis"
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_saddle_fail(self, calc, shell, mat):
        """Saddle kontrolü — FAIL (çok yüksek ağırlık)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_saddle({
            "support": {
                "tag": "SADDLE-02",
                "type": "saddle",
                "width_mm": 200.0,
                "height_mm": 0.0,
            },
            "shell": shell,
            "vessel_length": 4000.0,
            "saddle_distance": 4000.0,
            "saddle_from_end": 800.0,
            "total_weight_N": 5000000.0,  # Çok yüksek ağırlık
            "materials": [mat],
            "design_conditions": dc,
        })
        assert r.status.value == "FAIL"

    def test_saddle_traceability(self, calc, shell, mat):
        """K5: Saddle izlenebilirlik."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_saddle({
            "support": {"tag": "SADDLE-03", "type": "saddle", "width_mm": 200.0},
            "shell": shell,
            "total_weight_N": 100000.0,
            "materials": [mat],
            "design_conditions": dc,
        })
        assert len(r.intermediate_values) > 0

    def test_skirt_pass(self, calc, mat):
        """Skirt kontrolü — PASS."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_skirt({
            "support": {
                "tag": "SKIRT-01",
                "type": "skirt",
                "diameter_mm": 1000.0,
                "thickness_mm": 10.0,
                "height_mm": 2000.0,
            },
            "total_weight_N": 200000.0,
            "overturning_moment_Nmm": 50000000.0,
            "materials": [mat],
            "design_conditions": dc,
            "skirt_material_id": "MAT-01",
        })
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_skirt_fail(self, calc, mat):
        """Skirt kontrolü — FAIL (yüksek moment)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_skirt({
            "support": {
                "tag": "SKIRT-02",
                "type": "skirt",
                "diameter_mm": 1000.0,
                "thickness_mm": 10.0,
                "height_mm": 2000.0,
            },
            "total_weight_N": 5000000.0,
            "overturning_moment_Nmm": 5000000000.0,  # Çok yüksek moment
            "materials": [mat],
            "design_conditions": dc,
            "skirt_material_id": "MAT-01",
        })
        assert r.status.value == "FAIL"
