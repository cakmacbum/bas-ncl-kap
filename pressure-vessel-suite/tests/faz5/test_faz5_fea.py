"""Faz 5 — FEA iskelet modülü testleri.

Çözücü kurulu olmasa bile iskelet modülünün doğru REVIEW_REQUIRED
ürettiğini doğrular. Sahte "PASS" ÜRETMEZ.
"""

import pytest

from fea.fea_adapter import FEAdapter, FEAConfig
from fea import FEAdapter as FEAdapterImport

from domain import (
    DesignConditions,
    ShellSection,
)


# ── İskelet testleri ──────────────────────────────────────────────────────────

class TestFEAAdapter:
    """FEAdapter iskelet modülü testleri."""

    @pytest.fixture
    def adapter(self):
        return FEAdapter(FEAConfig(solver="calculix", mesh_size=10.0))

    @pytest.fixture
    def shell(self):
        return ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )

    def test_review_required_when_solver_missing(self, adapter, shell):
        """Çözücü kurulu değilse → REVIEW_REQUIRED.

        Bu test sahte PASS ÜRETMEZ — iskelet modülü doğru davranışı doğrular.
        """
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )

        r = adapter.run_analysis({
            "shell": shell,
            "design_conditions": dc,
        })

        # REVIEW_REQUIRED olmalı — asla PASS olmamalı
        assert r.status.value == "REVIEW REQUIRED"
        assert r.code == "FEA"
        assert r.clause_reference == "ASME VIII-2 Part 5"
        assert "solver" in str(r.input_snapshot).lower() or "calculix" in str(r.input_snapshot)

    def test_never_produces_fake_pass(self, adapter, shell):
        """Sahte PASS ÜRETMEZ — iskelet modülü asla PASS dönmez."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )

        r = adapter.run_analysis({"shell": shell, "design_conditions": dc})

        # Asla PASS olmamalı
        assert r.status.value != "PASS"
        assert r.status.value != "NOT CALCULATED"  # NOT_CALCULATED da olmamalı
        assert r.status.value == "REVIEW REQUIRED"

    def test_skeleton_intermediates(self, adapter, shell):
        """İskelet ara değerleri dolu olmalı."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )

        r = adapter.run_analysis({"shell": shell, "design_conditions": dc})

        # Ara değerler dolu olmalı
        assert len(r.intermediate_values) > 0

        # Stress linearization iskeleti
        sl_names = [iv["name"] for iv in r.intermediate_values]
        assert "stress_linearization_membrane" in sl_names
        assert "stress_linearization_bending" in sl_names
        assert "stress_linearization_peak" in sl_names
        assert "code_acceptance_status" in sl_names

    def test_assumptions_present(self, adapter, shell):
        """Varsayımlar dolu olmalı (K4)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )

        r = adapter.run_analysis({"shell": shell, "design_conditions": dc})

        assert len(r.assumptions) > 0
        # İskelet modülü varsayımı
        assert any("iskelet" in a.lower() or "skeleton" in a.lower() for a in r.assumptions)

    def test_mesh_quality_report(self, adapter):
        """Mesh kalite raporu iskelet modunda."""
        mq = adapter.get_mesh_quality_report()
        assert mq.quality_pass is False
        assert len(mq.warnings) > 0

    def test_classify_stress_not_evaluated(self, adapter):
        """Gerilme sınıflandırması iskelet modunda."""
        result = adapter.classify_stress(100.0, 50.0, 20.0, 138.0)
        assert result["status"] == "NOT_EVALUATED"

    def test_config_defaults(self):
        """Varsayılan yapılandırma."""
        config = FEAConfig()
        assert config.solver == "calculix"
        assert config.mesh_size == 10.0
        assert config.element_type == "C3D10"
        assert config.linear_elastic is True

    def test_import(self):
        """FEAdapter import edilebilir."""
        assert FEAdapterImport is not None
