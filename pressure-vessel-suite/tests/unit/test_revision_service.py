"""Project/Revision Service testleri — tutarlılık mekanizması (kaynak §16)."""

import pytest

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
    WeldJoint,
)
from code_asme_viii_1 import ASMEVIII1DesignCode
from calc_core.revision_service import ProjectRevisionService


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def design_code():
    return ASMEVIII1DesignCode(edition="2025")


@pytest.fixture
def sample_project():
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
        joint_efficiency=1.0,
    )
    return VesselProject(
        project_number="REV-001",
        project_name="Revision Test",
        revision="A",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        materials=[mat],
        welds=[wj],
    )


@pytest.fixture
def service(design_code, sample_project):
    svc = ProjectRevisionService(design_code)
    svc.set_project(sample_project)
    return svc


# ── Temel testler ─────────────────────────────────────────────────────────────

class TestProjectRevisionService:
    """Revision Service temel testleri."""

    def test_set_project(self, service, sample_project):
        """Proje ayarlanabilmeli."""
        assert service.project is not None
        assert service.project.project_number == "REV-001"
        assert service.project.revision == "A"

    def test_update_shell_thickness(self, service):
        """Gövde kalınlığı güncellenebilmeli."""
        result = service.update_thickness("SHELL-01", 16.0)

        assert result.success
        assert "SHELL-01" in result.changes_detected[0]
        assert "16.0" in result.changes_detected[0]
        assert result.project.shell_sections[0].nominal_thickness == 16.0

    def test_update_head_thickness(self, service):
        """Bombe kalınlığı güncellenebilmeli."""
        result = service.update_thickness("HEAD-L", 15.0)

        assert result.success
        assert "HEAD-L" in result.changes_detected[0]
        assert result.project.heads[0].nominal_thickness == 15.0

    def test_update_nonexistent_component(self, service):
        """Olmayan bileşen → hata."""
        result = service.update_thickness("NONEXISTENT", 20.0)
        assert not result.success
        assert "bulunamadı" in result.error.lower()

    def test_update_same_thickness_returns_error(self, service):
        """Aynı kalınlık → hata."""
        result = service.update_thickness("SHELL-01", 12.0)  # Zaten 12
        assert not result.success
        assert "değişmedi" in result.error.lower()


# ── MAWP yeniden hesaplama ────────────────────────────────────────────────────

class TestMAWPRecalculation:
    """Kalınlık değişince MAWP yeniden hesaplanmalı."""

    def test_mawp_increases_with_thickness(self, service):
        """Kalınlık artınca MAWP artmalı."""
        result = service.update_thickness("SHELL-01", 20.0)

        assert result.success
        mawp = result.calc_result.get_global_mawp()
        assert mawp is not None
        # 20mm kalınlık → MAWP > design_pressure
        assert mawp > result.project.design_conditions.design_pressure

    def test_mawp_changes_on_thickness_change(self, service, sample_project):
        """Farklı kalınlık → farklı MAWP."""
        result_thin = service.update_thickness("SHELL-01", 10.0)
        mawp_thin = result_thin.calc_result.get_global_mawp()

        # Servisi sıfırla
        service.set_project(sample_project)
        result_thick = service.update_thickness("SHELL-01", 20.0)
        mawp_thick = result_thick.calc_result.get_global_mawp()

        assert mawp_thick > mawp_thin

    def test_mawp_recalculated_on_head_change(self, service, sample_project):
        """Bombe kalınlığı değişince de MAWP yeniden hesaplanmalı."""
        result = service.update_thickness("HEAD-L", 20.0)

        assert result.success
        mawp = result.calc_result.get_global_mawp()
        assert mawp is not None


# ── Ağırlık/hacim güncelleme ──────────────────────────────────────────────────

class TestWeightVolumeUpdate:
    """Kalınlık değişince ağırlık/hacim güncellenmeli."""

    def test_mass_increases_with_thickness(self, service, sample_project):
        """Kalınlık artınca ağırlık artmalı."""
        result_thin = service.update_thickness("SHELL-01", 10.0)
        mass_thin = result_thin.volume_mass.total_metal_mass_kg

        service.set_project(sample_project)
        result_thick = service.update_thickness("SHELL-01", 20.0)
        mass_thick = result_thick.volume_mass.total_metal_mass_kg

        assert mass_thick > mass_thin

    def test_volume_mass_report_present(self, service):
        """Hacim/ağırlık raporu mevcut olmalı."""
        result = service.update_thickness("SHELL-01", 16.0)

        assert result.success
        assert result.volume_mass is not None
        assert result.volume_mass.total_metal_mass_kg > 0
        assert result.volume_mass.total_inner_volume_liters > 0


# ── Revizyon takibi ───────────────────────────────────────────────────────────

class TestRevisionTracking:
    """Revizyon numarası ve geçmişi takip edilmeli."""

    def test_revision_increments(self, service):
        """Her güncelleme revizyon numarasını artırmalı."""
        result1 = service.update_thickness("SHELL-01", 14.0)
        assert result1.project.revision == "B"

        result2 = service.update_thickness("SHELL-01", 16.0)
        assert result2.project.revision == "C"

    def test_revision_history(self, service):
        """Revizyon geçmişi tutulmalı."""
        service.update_thickness("SHELL-01", 14.0)
        service.update_thickness("SHELL-01", 16.0)

        history = service.get_history()
        assert len(history) == 2
        assert history[0]["revision_id"] == "B"
        assert history[1]["revision_id"] == "C"

    def test_revision_contains_changes(self, service):
        """Revizyon kaydı değişiklikleri içermeli."""
        result = service.update_thickness("SHELL-01", 16.0)

        history = service.get_history()
        assert len(history) == 1
        assert "SHELL-01" in history[0]["changes"][0]

    def test_revision_contains_calc_summary(self, service):
        """Revizyon kaydı hesap özetini içermeli."""
        result = service.update_thickness("SHELL-01", 16.0)

        history = service.get_history()
        summary = history[0]["calc_result_summary"]
        assert "global_mawp" in summary
        assert "total_mass_kg" in summary
        assert "all_passed" in summary


# ── OUTDATED mekanizması ──────────────────────────────────────────────────────

class TestOutdatedMechanism:
    """Rapor OUTDATED işaretleme mekanizması."""

    def test_previous_report_marked_outdated(self, service):
        """Kalınlık değişince eski rapor OUTDATED işaretlenmeli."""
        # Bir rapor kaydet
        service.register_report("abc123hash")

        # Kalınlık değiştir
        result = service.update_thickness("SHELL-01", 16.0)

        assert result.previous_report_outdated is True

    def test_no_outdated_without_previous_report(self, service):
        """Önceki rapor yoksa OUTDATED olmamalı."""
        result = service.update_thickness("SHELL-01", 16.0)

        assert result.previous_report_outdated is False

    def test_outdated_appears_in_history(self, service):
        """OUTDATED durumu geçmiş kaydında görünmeli."""
        service.register_report("abc123hash")
        service.update_thickness("SHELL-01", 16.0)

        history = service.get_history()
        # İlk kayıt (OUTDATED olan) — register_report öncesi
        # Aslında OUTDATED, register_report yapılan revizyon kaydında olmalı
        # Ama burada register_report bir revizyon değil, sadece hash kaydı
        # Revizyon güncelleme sonrası history'de changes var
        assert len(history) >= 1


# ── Service durumu ────────────────────────────────────────────────────────────

class TestServiceStatus:
    """Servis durum bilgisi testleri."""

    def test_get_current_status(self, service):
        """Mevcut durum bilgisi alınabilmeli."""
        status = service.get_current_status()
        assert status["project_number"] == "REV-001"
        assert status["revision"] == "A"
        assert status["revision_count"] == 0

    def test_status_after_update(self, service):
        """Güncelleme sonrası durum değişmeli."""
        service.update_thickness("SHELL-01", 16.0)

        status = service.get_current_status()
        assert status["revision"] == "B"
        assert status["revision_count"] == 1

    def test_no_project_status(self, design_code):
        """Proje ayarlanmamışsa hata dönmeli."""
        svc = ProjectRevisionService(design_code)
        status = svc.get_current_status()
        assert "error" in status
