"""Faz 4.B — Compliance modülü testleri.

ESR matrisi, DoC taslağı, isim plakası, risk analizi, teknik dosya indeksi.
"""

import pytest

from compliance import (
    ESRMatrix,
    ESRItem,
    DeclarationOfConformity,
    NameplateInfo,
    RiskAnalysis,
    RiskItem,
    TechnicalFileIndex,
    TechnicalFileItem,
)
from compliance.esr_matrix import ESRComplianceStatus


# ── ESR Matrisi testleri ──────────────────────────────────────────────────────

class TestESRMatrix:
    """ESR matrisi testleri."""

    def test_default_vessel_has_items(self):
        """Varsayılan kap ESR matrisi kalem içermeli."""
        matrix = ESRMatrix.default_for_vessel()
        assert len(matrix.items) > 0
        # PED Ek I temel maddeleri
        clauses = [i.clause for i in matrix.items]
        assert "4.1" in clauses  # Design for adequate strength
        assert "4.8" in clauses  # Protection against exceeding limits
        assert "5.1" in clauses  # Material properties
        assert "7.1" in clauses  # Permanent joining
        assert "8.1" in clauses  # Hydrostatic test
        assert "9" in clauses    # Marking

    def test_update_status(self):
        """Durum güncelleme çalışmalı."""
        matrix = ESRMatrix.default_for_vessel()
        updated = matrix.update_status(
            "4.1",
            ESRComplianceStatus.APPLIED,
            evidence="ASME VIII-1 calculation report",
        )
        assert updated is True
        item = next(i for i in matrix.items if i.clause == "4.1")
        assert item.status == ESRComplianceStatus.APPLIED
        assert item.evidence == "ASME VIII-1 calculation report"

    def test_update_nonexistent_clause(self):
        """Olmayan madde → False dönmeli."""
        matrix = ESRMatrix.default_for_vessel()
        updated = matrix.update_status("99.99", ESRComplianceStatus.APPLIED)
        assert updated is False

    def test_counts(self):
        """Durum sayıları doğru olmalı."""
        matrix = ESRMatrix.default_for_vessel()
        matrix.update_status("4.1", ESRComplianceStatus.APPLIED, evidence="Test")
        matrix.update_status("4.2", ESRComplianceStatus.NOT_APPLIED)

        assert matrix.get_applied_count() == 1
        assert matrix.get_not_applied_count() == 1
        assert matrix.get_applicable_count() == 2

    def test_to_html(self):
        """HTML çıktı üretmeli."""
        matrix = ESRMatrix.default_for_vessel()
        html = matrix.to_html()
        assert "<table>" in html
        assert "4.1" in html


# ── Nameplate testleri ────────────────────────────────────────────────────────

class TestNameplateInfo:
    """İsim plakası testleri."""

    def test_nameplate_creation(self):
        """İsim plakası oluşturulabilmeli."""
        np = NameplateInfo(
            manufacturer_name="Test Manufacturer",
            year_of_manufacture=2025,
            equipment_type="Pressure Vessel",
            serial_number="SN-001",
            maximum_allowable_pressure_ps=1.5,
            maximum_allowable_temperature_ts_max=200.0,
            minimum_allowable_temperature_ts_min=-10.0,
            volume_liters=500.0,
            test_pressure=2.145,
            design_code="EN 13445",
            design_code_edition="2021+A1:2023",
            ped_category="Category III",
            fluid_group="Group 2",
            conformity_module="B+D",
        )
        assert np.manufacturer_name == "Test Manufacturer"
        assert np.serial_number == "SN-001"
        assert np.ce_marking is True

    def test_nameplate_markdown(self):
        """Markdown çıktı üretmeli."""
        np = NameplateInfo(
            manufacturer_name="ACME",
            year_of_manufacture=2025,
            equipment_type="Vessel",
            serial_number="V-001",
            maximum_allowable_pressure_ps=1.0,
            maximum_allowable_temperature_ts_max=150.0,
            minimum_allowable_temperature_ts_min=-10.0,
            volume_liters=100.0,
            test_pressure=1.43,
            design_code="EN 13445",
            design_code_edition="2021",
            ped_category="Category II",
            fluid_group="Group 2",
            conformity_module="A2",
        )
        md = np.to_markdown()
        assert "ACME" in md
        assert "V-001" in md
        assert "Category II" in md

    def test_nameplate_html(self):
        """HTML çıktı üretmeli."""
        np = NameplateInfo(
            manufacturer_name="ACME",
            year_of_manufacture=2025,
            equipment_type="Vessel",
            serial_number="V-001",
            maximum_allowable_pressure_ps=1.0,
            maximum_allowable_temperature_ts_max=150.0,
            minimum_allowable_temperature_ts_min=-10.0,
            volume_liters=100.0,
            test_pressure=1.43,
            design_code="EN 13445",
            design_code_edition="2021",
            ped_category="Category II",
            fluid_group="Group 2",
            conformity_module="A2",
        )
        html = np.to_html()
        assert "<table>" in html
        assert "ACME" in html


# ── DoC testleri ──────────────────────────────────────────────────────────────

class TestDeclarationOfConformity:
    """EU Declaration of Conformity testleri."""

    def test_doc_creation(self):
        """DoC oluşturulabilmeli."""
        doc = DeclarationOfConformity(
            manufacturer_name="ACME Pressure Vessels",
            equipment_description="1000L Air Receiver",
            equipment_type="Pressure Vessel",
            serial_number="AR-2025-001",
            ped_category="Category II",
            conformity_module="A2",
            harmonised_standards=["EN 13445:2021+A1:2023"],
        )
        assert doc.manufacturer_name == "ACME Pressure Vessels"
        assert doc.serial_number == "AR-2025-001"
        assert len(doc.harmonised_standards) == 1

    def test_doc_markdown(self):
        """Markdown çıktı üretmeli."""
        doc = DeclarationOfConformity(
            manufacturer_name="ACME",
            equipment_description="Test Vessel",
            equipment_type="Vessel",
            serial_number="V-001",
            ped_category="Category I",
            conformity_module="A",
        )
        md = doc.to_markdown()
        assert "EU DECLARATION OF CONFORMITY" in md
        assert "ACME" in md
        assert "Article 14" in md

    def test_doc_html(self):
        """HTML çıktı üretmeli."""
        doc = DeclarationOfConformity(
            manufacturer_name="ACME",
            equipment_description="Test Vessel",
            equipment_type="Vessel",
            serial_number="V-001",
            ped_category="Category I",
            conformity_module="A",
        )
        html = doc.to_html()
        assert "<table>" in html
        assert "EU DECLARATION OF CONFORMITY" in html


# ── Risk analizi testleri ─────────────────────────────────────────────────────

class TestRiskAnalysis:
    """Risk analizi testleri."""

    def test_default_risk_analysis(self):
        """Varsayılan risk analizi kalem içermeli."""
        analysis = RiskAnalysis.default_for_pressure_vessel()
        assert len(analysis.items) > 0
        # En az 3 tehlike olmalı
        assert len(analysis.items) >= 3

    def test_high_risks(self):
        """Yüksek risk kalemleri filtrelenebilmeli."""
        analysis = RiskAnalysis.default_for_pressure_vessel()
        high_risks = analysis.get_high_risks()
        assert len(high_risks) > 0

    def test_residual_high_risks(self):
        """Kalan yüksek risk filtrelenmeli."""
        analysis = RiskAnalysis.default_for_pressure_vessel()
        # Varsayılan analizde tüm kalan riskler düşük olmalı
        residual_high = analysis.get_residual_high_risks()
        assert len(residual_high) == 0

    def test_add_risk(self):
        """Yeni risk eklenebilmeli."""
        analysis = RiskAnalysis.default_for_pressure_vessel()
        initial_count = len(analysis.items)
        analysis.add_risk(RiskItem(
            hazard_id="H-999",
            hazard_description="Test hazard",
            severity=RiskSeverity.MEDIUM,
            probability=RiskProbability.LOW,
            risk_level=RiskLevel.LOW,
        ))
        assert len(analysis.items) == initial_count + 1

    def test_to_html(self):
        """HTML çıktı üretmeli."""
        analysis = RiskAnalysis.default_for_pressure_vessel()
        html = analysis.to_html()
        assert "<table>" in html
        assert "H-001" in html


# ── Teknik dosya indeksi testleri ─────────────────────────────────────────────

class TestTechnicalFileIndex:
    """Teknik dosya indeksi testleri."""

    def test_default_index(self):
        """Varsayılan indeks kalem içermeli."""
        index = TechnicalFileIndex.default_for_vessel()
        assert len(index.items) > 0
        assert index.retention_years == 10

    def test_completion_tracking(self):
        """Tamamlanma takibi çalışmalı."""
        index = TechnicalFileIndex.default_for_vessel()
        assert index.get_completed_count() == 0
        assert index.get_completion_percentage() == 0.0

        # Bir kalemi tamamla
        index.items[0].status = "Completed"
        assert index.get_completed_count() == 1
        assert index.get_completion_percentage() > 0

    def test_add_item(self):
        """Yeni kalem eklenebilmeli."""
        index = TechnicalFileIndex.default_for_vessel()
        initial_count = len(index.items)
        index.add_item(TechnicalFileItem(
            item_id="TF-999",
            item_type=TechnicalFileItemType.OTHER,
            description="Test item",
        ))
        assert len(index.items) == initial_count + 1

    def test_to_html(self):
        """HTML çıktı üretmeli."""
        index = TechnicalFileIndex.default_for_vessel()
        html = index.to_html()
        assert "<table>" in html
        assert "10 yıl" in html


# ── Import testleri ───────────────────────────────────────────────────────────

class TestImports:
    """Tüm compliance bileşenleri import edilebilmeli."""

    def test_import_esr_matrix(self):
        from compliance.esr_matrix import ESRMatrix, ESRItem, ESRComplianceStatus
        assert ESRMatrix is not None

    def test_import_declaration(self):
        from compliance.declaration import DeclarationOfConformity, NameplateInfo
        assert DeclarationOfConformity is not None

    def test_import_risk_analysis(self):
        from compliance.risk_analysis import RiskAnalysis, RiskItem
        assert RiskAnalysis is not None

    def test_import_technical_file(self):
        from compliance.technical_file import TechnicalFileIndex, TechnicalFileItem
        assert TechnicalFileIndex is not None


# Import for risk test
from compliance.risk_analysis import RiskSeverity, RiskProbability, RiskLevel
from compliance.technical_file import TechnicalFileItemType
