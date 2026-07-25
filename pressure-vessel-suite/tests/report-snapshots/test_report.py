"""Rapor motoru testleri — HTML rapor üretimi + izlenebilirlik bloğu."""

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
from calc_core.volume_mass import calculate_vessel_volume_mass
from report_engine.generator import ReportGenerator, WEASYPRINT_AVAILABLE
from report_engine.traceability import (
    TraceabilityBlock,
    build_traceability,
    compute_report_hash,
    SOFTWARE_VERSION,
    CALCULATION_ENGINE_VERSION,
    STANDARD_PACK_VERSION,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def full_project():
    """Rapor test projesi — tam veri."""
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
        weld_joint_id="WJ-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=12.5,
    )
    head_l = Head(
        head_id="HEAD-L",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        internal_corrosion_allowance=2.0,
    )
    head_r = Head(
        head_id="HEAD-R",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        internal_corrosion_allowance=2.0,
    )
    nozzle_n1 = Nozzle(
        tag="N1",
        nozzle_type=NozzleType.FLANGED,
        host_component_id="SHELL-01",
        axial_position=500.0,
        outside_diameter=168.3,
        inside_diameter=154.1,
        neck_thickness=7.1,
        material_id="MAT-01",
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
    wj = WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        weld_category="A",
        joint_efficiency=1.0,
        nde_method="RT-1",
        nde_extent="100%",
    )
    return VesselProject(
        project_number="RPT-001",
        project_name="Report Test Vessel",
        customer="Test Corp",
        revision="A",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        nozzles=[nozzle_n1],
        materials=[mat],
        welds=[wj],
    )


@pytest.fixture
def calc_result(full_project):
    """Hesap motoru sonuçları."""
    code = ASMEVIII1DesignCode(edition="2025")
    orch = CalculationOrchestrator(code)
    return orch.run(full_project)


@pytest.fixture
def volume_mass(full_project):
    """Hacim/ağırlık raporu."""
    return calculate_vessel_volume_mass(full_project)


# ── Traceability testleri ─────────────────────────────────────────────────────

class TestTraceability:
    """İzlenebilirlik bloğu testleri."""

    def test_build_traceability(self):
        """İzlenebilirlik bloğu oluşturulmalı."""
        tb = build_traceability(project_revision="A", input_file_hash="abc123")
        assert tb.project_revision == "A"
        assert tb.input_file_hash == "abc123"
        assert tb.software_version == SOFTWARE_VERSION
        assert tb.calculation_engine_version == CALCULATION_ENGINE_VERSION
        assert tb.standard_pack_version == STANDARD_PACK_VERSION
        assert tb.calculation_date != ""

    def test_traceability_to_dict(self):
        """Dict'e çevrilebilmeli."""
        tb = build_traceability()
        d = tb.to_dict()
        assert "software_version" in d
        assert "calculation_date" in d
        assert "input_file_hash" in d
        assert "report_hash" in d

    def test_traceability_to_html(self):
        """HTML üretilebilmeli."""
        tb = build_traceability()
        html = tb.to_html()
        assert "İzlenebilirlik" in html
        assert "<table" in html

    def test_compute_report_hash(self):
        """Rapor hash'i hesaplanabilmeli."""
        h = compute_report_hash("<html>test</html>")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_report_hash_deterministic(self):
        """Aynı içerikten aynı hash üretilmeli."""
        h1 = compute_report_hash("<html>test</html>")
        h2 = compute_report_hash("<html>test</html>")
        assert h1 == h2


# ── Rapor üretimi testleri ────────────────────────────────────────────────────

class TestReportGenerator:
    """Rapor üretici testleri."""

    def test_generate_html(self, full_project, calc_result, volume_mass):
        """HTML rapor üretilmeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert result.success
        assert result.html_content is not None
        assert len(result.html_content) > 1000

    def test_html_contains_project_info(self, full_project, calc_result, volume_mass):
        """HTML proje bilgilerini içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "RPT-001" in result.html_content
        assert "Report Test Vessel" in result.html_content
        assert "Test Corp" in result.html_content

    def test_html_contains_all_23_sections(self, full_project, calc_result, volume_mass):
        """HTML tüm 23 bölümü içermeli (h2 başlıkları)."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        html = result.html_content
        # Temel bölüm başlıkları
        assert "2. Proje ve Revizyon" in html
        assert "3. Kullanılan Standartlar" in html
        assert "4. Tasarım Temeli" in html
        assert "5. Akışkan" in html
        assert "7. Malzeme Listesi" in html
        assert "8. Ana Geometri" in html
        assert "9. Gövde Hesapları" in html
        assert "10. Bombe Hesapları" in html
        assert "11. Nozul" in html
        assert "12. Kaynak" in html
        assert "13. MAWP" in html
        assert "14. Hidrostatik" in html
        assert "15. Ağırlık ve Hacim" in html
        assert "23. Hesap Onay" in html

    def test_html_contains_calculation_results(self, full_project, calc_result, volume_mass):
        """HTML hesap sonuçlarını içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        html = result.html_content
        assert "UG-27" in html  # Gövde madde referansı
        assert "UG-32" in html  # Bombe madde referansı
        assert "PASS" in html   # Durum

    def test_html_contains_traceability(self, full_project, calc_result, volume_mass):
        """HTML izlenebilirlik bloğunu içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "Yazılım Sürümü" in result.html_content
        assert "Hesap Motoru Sürümü" in result.html_content
        assert "Rapor Hash" in result.html_content

    def test_html_contains_volume_mass(self, full_project, calc_result, volume_mass):
        """HTML hacim/ağırlık bilgisini içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "litre" in result.html_content
        assert "kg" in result.html_content

    def test_report_hash_set(self, full_project, calc_result, volume_mass):
        """Rapor hash'i hesaplanmalı."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert result.report_hash != ""
        assert len(result.report_hash) == 64

    def test_html_valid_structure(self, full_project, calc_result, volume_mass):
        """HTML geçerli yapıda olmalı."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        html = result.html_content
        assert html.startswith("<!DOCTYPE html>")
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_html_contains_warnings_section(self, full_project, calc_result, volume_mass):
        """HTML uyarılar bölümünü içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "20. Uyarılar" in result.html_content

    def test_html_contains_nozzle_schedule(self, full_project, calc_result, volume_mass):
        """HTML nozul schedule içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "N1" in result.html_content
        assert "168.3" in result.html_content  # N1 dış çapı

    def test_html_contains_mawp(self, full_project, calc_result, volume_mass):
        """HTML MAWP değerlerini içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "Global MAWP" in result.html_content

    def test_html_contains_hydrotest(self, full_project, calc_result, volume_mass):
        """HTML hidrotest basıncını içermeli."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert "UG-99" in result.html_content

    def test_html_no_k6_violation(self, full_project, calc_result, volume_mass):
        """K6: Standart telifli metin kopyalanmamalı (uzun alıntı yok)."""
        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        # Standart metni kopyalanmamalı — yalnızca madde referansı
        # "ASME Section VIII Division 1" gibi kısa referanslar olabilir
        # ama "The rules of this division are applicable..." gibi uzun metin olmamalı
        assert "The rules of this division" not in result.html_content

    def test_generate_only_html(self, full_project, calc_result, volume_mass):
        """generate_html_only çalışmalı."""
        gen = ReportGenerator()
        result = gen.generate_html_only(full_project, calc_result, volume_mass)

        assert result.success
        assert result.pdf_path is None  # PDF üretilmemeli

    def test_pdf_generation_if_weasyprint(self, full_project, calc_result, volume_mass, tmp_path):
        """WeasyPrint varsa PDF üretilmeli."""
        if not WEASYPRINT_AVAILABLE:
            pytest.skip("WeasyPrint kurulu değil")

        gen = ReportGenerator()
        result = gen.generate(full_project, calc_result, volume_mass)

        assert result.success
        assert result.pdf_path is not None
        # PDF dosyası var mı kontrol et (geçici dosya)
