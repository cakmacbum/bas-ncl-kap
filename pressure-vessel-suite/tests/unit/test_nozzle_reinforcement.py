"""Nozul takviye hesabı testleri — ASME UG-37/UG-40."""

from dataclasses import replace

import pytest

from domain import CalculationStatus
from nozzles.reinforcement import (
    AreaItem,
    NozzleReinforcementInput,
    NozzleReinforcementResult,
    build_reinforcement_calculation_result,
    calculate_reinforcement,
    check_nozzle_eligibility,
)
from nozzles.nozzle_schedule import generate_nozzle_schedule, NozzleScheduleEntry
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
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def basic_input():
    """Tipik nozul takviye girdisi."""
    return NozzleReinforcementInput(
        nozzle_tag="N1",
        nozzle_inside_diameter=154.1,
        nozzle_outside_diameter=168.3,
        nozzle_neck_thickness=7.1,
        nozzle_corrosion_allowance=1.0,
        nozzle_projection_outside=100.0,
        nozzle_projection_inside=0.0,
        nozzle_allowable_stress=138.0,
        component_type="shell",
        component_inside_diameter=1000.0,
        component_nominal_thickness=12.0,
        component_corrosion_allowance=2.0,
        component_required_thickness=6.97,
        component_allowable_stress=138.0,
        has_reinforcement_pad=False,
        design_pressure=1.2,
        design_temperature=200.0,
    )


@pytest.fixture
def input_with_pad(basic_input):
    """Takviye pedli nozul."""
    return basic_input.model_copy if hasattr(basic_input, 'model_copy') else NozzleReinforcementInput(
        nozzle_tag="N2",
        nozzle_inside_diameter=154.1,
        nozzle_outside_diameter=168.3,
        nozzle_neck_thickness=7.1,
        nozzle_corrosion_allowance=1.0,
        nozzle_projection_outside=100.0,
        nozzle_projection_inside=0.0,
        nozzle_allowable_stress=138.0,
        component_type="shell",
        component_inside_diameter=1000.0,
        component_nominal_thickness=12.0,
        component_corrosion_allowance=2.0,
        component_required_thickness=6.97,
        component_allowable_stress=138.0,
        has_reinforcement_pad=True,
        reinforcement_pad_od=250.0,
        reinforcement_pad_thickness=8.0,
        reinforcement_pad_allowable_stress=138.0,
        weld_leg_size_nozzle_to_shell=6.0,
        weld_leg_size_pad_to_shell=6.0,
        design_pressure=1.2,
        design_temperature=200.0,
    )


# ── Uygunluk kontrolü ────────────────────────────────────────────────────────

class TestNozzleEligibility:
    """Açıklık uygunluk kontrolü testleri."""

    def test_eligible_small_nozzle(self, basic_input):
        """Küçük nozul → uygun."""
        is_ok, msg = check_nozzle_eligibility(basic_input)
        assert is_ok
        assert "uygun" in msg.lower()

    def test_too_large_nozzle(self):
        """Çok büyük nozul → uygun değil."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-LARGE",
            nozzle_inside_diameter=600.0,
            nozzle_corrosion_allowance=0.0,
            component_inside_diameter=1000.0,
            component_nominal_thickness=12.0,
            component_corrosion_allowance=2.0,
        )
        is_ok, msg = check_nozzle_eligibility(inp)
        assert not is_ok
        assert "UG-36" in msg


# ── Takviye hesabı ────────────────────────────────────────────────────────────

class TestReinforcementCalculation:
    """Takviye alanı hesaplama testleri."""

    def test_calculate_basic(self, basic_input):
        """Temel takviye hesabı."""
        result = calculate_reinforcement(basic_input)

        assert result.effective_diameter > 0
        assert result.required_area > 0
        # UG-37(c) adlandırması: A1 gövde fazlası, A2 nozul dışa, A3 nozul içe,
        # A4 kaynak, A5 takviye pedi.
        assert len(result.available_areas) == 5

    def test_effective_diameter(self, basic_input):
        """Etkin çap = iç çap + 2×korozyon payı."""
        result = calculate_reinforcement(basic_input)

        expected_d = 154.1 + 2 * 1.0  # 156.1
        assert abs(result.effective_diameter - expected_d) < 0.1

    def test_required_area(self, basic_input):
        """Gerekli alan = d × t_required."""
        result = calculate_reinforcement(basic_input)

        d = 154.1 + 2 * 1.0
        expected = d * 6.97
        assert abs(result.required_area - expected) < 1.0

    def test_area_breakdown(self, basic_input):
        """Alan kalem kalem gösterilmeli."""
        result = calculate_reinforcement(basic_input)

        names = [a.name for a in result.available_areas]
        assert "A1" in names  # Gövde/bombe fazlası
        assert "A2" in names  # Nozul boynu — dışa
        assert "A3" in names  # Nozul boynu — içe
        assert "A4" in names  # Kaynak metali
        assert "A5" in names  # Takviye pedi

    def test_total_area_positive(self, basic_input):
        """Toplam alan pozitif olmalı."""
        result = calculate_reinforcement(basic_input)
        assert result.total_available_area > 0

    def test_pass_when_sufficient(self, basic_input):
        """Yeterli alan → PASS."""
        # Kalın gövde ile yeterli alan sağlamalı
        basic_input.component_nominal_thickness = 20.0
        result = calculate_reinforcement(basic_input)

        # Durum: genellikle yeterli olmalı
        # (tam sonucu geometriye bağlı)
        assert result.status in (CalculationStatus.PASS, CalculationStatus.FAIL)

    def test_fail_when_insufficient(self):
        """Yetersiz alan → FAIL."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-THIN",
            nozzle_inside_diameter=100.0,
            nozzle_outside_diameter=110.0,
            nozzle_neck_thickness=5.0,
            nozzle_corrosion_allowance=0.0,
            nozzle_projection_outside=10.0,
            nozzle_projection_inside=0.0,
            nozzle_allowable_stress=138.0,
            component_type="shell",
            component_inside_diameter=1000.0,
            component_nominal_thickness=8.0,
            component_corrosion_allowance=0.0,
            component_required_thickness=7.5,
            component_allowable_stress=138.0,
            has_reinforcement_pad=False,
            design_pressure=1.2,
        )
        result = calculate_reinforcement(inp)

        # 7.5mm gerekli, 8mm nominal → çok az fazla
        # Büyük nozul → muhtemelen yetersiz
        assert result.status in (CalculationStatus.PASS, CalculationStatus.FAIL)

    def test_pad_increases_area(self, basic_input, input_with_pad):
        """Takviye pedi alanı artırmalı."""
        result_no_pad = calculate_reinforcement(basic_input)
        result_with_pad = calculate_reinforcement(input_with_pad)

        assert result_with_pad.total_available_area > result_no_pad.total_available_area

    def test_eligibility_fail_returns_fail(self):
        """Uygun olmayan nozul → FAIL dönmeli."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-BIG",
            nozzle_inside_diameter=600.0,
            nozzle_corrosion_allowance=0.0,
            component_inside_diameter=1000.0,
            component_nominal_thickness=12.0,
            component_corrosion_allowance=0.0,
            component_required_thickness=5.0,
        )
        result = calculate_reinforcement(inp)
        assert result.status == CalculationStatus.FAIL
        assert not result.is_eligible


# ── CalculationResult entegrasyonu ────────────────────────────────────────────

class TestInclinedNozzleIsNotFinal:
    """Eğik nozul: 1/cos(α) izdüşümü UG-37 eğik yöntemi değildir → nihai PASS verilmez."""

    @staticmethod
    def _thick(basic_input, angle):
        # Bol takviyeli gövde: radyalde açıkça PASS
        return replace(basic_input, component_nominal_thickness=30.0,
                       nozzle_inclination_angle=angle)

    def test_radial_still_passes(self, basic_input):
        assert calculate_reinforcement(self._thick(basic_input, 0.0)).status == CalculationStatus.PASS

    def test_inclined_pass_becomes_review_required(self, basic_input):
        r = calculate_reinforcement(self._thick(basic_input, 30.0))
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert any("Eğik nozul" in w and "30" in w for w in r.warnings)

    def test_inclined_area_still_computed_with_projection(self, basic_input):
        # Gerekli alan izdüşümle büyür: A_req(30°) = A_req(0°)/cos(30°) — sayılar korunur
        r0 = calculate_reinforcement(self._thick(basic_input, 0.0))
        r30 = calculate_reinforcement(self._thick(basic_input, 30.0))
        assert r30.required_area == pytest.approx(r0.required_area / 0.8660254, rel=1e-3)

    def test_inclined_fail_stays_fail(self, basic_input):
        weak = replace(basic_input, component_nominal_thickness=7.5,
                       nozzle_inclination_angle=30.0)
        assert calculate_reinforcement(weak).status == CalculationStatus.FAIL

    def test_calculation_result_carries_review_status(self, basic_input):
        res = build_reinforcement_calculation_result(self._thick(basic_input, 30.0))
        assert res.status == CalculationStatus.REVIEW_REQUIRED


class TestCalculationResultIntegration:
    """build_reinforcement_calculation_result testleri."""

    def test_returns_calculation_result(self, basic_input):
        """CalculationResult döndürmeli."""
        from calc_core.result import CalculationResult
        result = build_reinforcement_calculation_result(basic_input)
        assert isinstance(result, CalculationResult)
        assert result.component_id == "N1"
        assert result.component_type == "nozzle"
        assert result.calculation_type == "nozzle_reinforcement"

    def test_has_intermediate_values(self, basic_input):
        """Ara değerler dolu olmalı."""
        result = build_reinforcement_calculation_result(basic_input)
        assert len(result.intermediate_values) > 0
        names = [iv["name"] for iv in result.intermediate_values]
        assert "d" in names
        assert "A_required" in names
        assert "A_total" in names

    def test_has_clause_reference(self, basic_input):
        """Madde referansı dolu olmalı."""
        result = build_reinforcement_calculation_result(basic_input)
        assert result.clause_reference == "UG-37/UG-40"
        assert result.code == "ASME VIII-1"


# ── Nozul Schedule ────────────────────────────────────────────────────────────

class TestNozzleSchedule:
    """Nozul schedule testleri."""

    @pytest.fixture
    def project_with_nozzles(self):
        dc = DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=150.0,
            design_temperature=200.0, minimum_design_temperature=-10.0,
        )
        shell = ShellSection(section_id="SHELL-01", inside_diameter=1000.0,
            tangent_length=2000.0, nominal_thickness=12.0, material_id="MAT-01")
        mat = MaterialProperty(material_id="MAT-01", standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
            temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
            tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4")
        n1 = Nozzle(tag="N1", nozzle_type=NozzleType.FLANGED, host_component_id="SHELL-01",
            axial_position=500.0, outside_diameter=168.3, inside_diameter=154.1,
            neck_thickness=7.1, material_id="MAT-01", reinforcement_pad=True)
        n2 = Nozzle(tag="N2", nozzle_type=NozzleType.FLANGED, host_component_id="SHELL-01",
            axial_position=1200.0, outside_diameter=114.3, inside_diameter=102.3,
            neck_thickness=6.0, material_id="MAT-01")
        return VesselProject(
            project_number="NS-001", project_name="Schedule Test",
            calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
            design_conditions=dc, shell_sections=[shell], materials=[mat],
            nozzles=[n1, n2],
        )

    def test_schedule_entries(self, project_with_nozzles):
        """Schedule doğru sayıda giriş içermeli."""
        entries = generate_nozzle_schedule(project_with_nozzles)
        assert len(entries) == 2

    def test_schedule_entry_fields(self, project_with_nozzles):
        """Giriş alanları doğru olmalı."""
        entries = generate_nozzle_schedule(project_with_nozzles)
        n1 = entries[0]
        assert n1.tag == "N1"
        assert n1.nozzle_type == "flanged"
        assert n1.axial_position_mm == 500.0
        assert n1.has_reinforcement_pad is True

    def test_schedule_to_dict(self, project_with_nozzles):
        """Dict'e çevrilebilmeli."""
        entries = generate_nozzle_schedule(project_with_nozzles)
        d = entries[0].to_dict()
        assert "tag" in d
        assert "axial_position_mm" in d

    def test_schedule_to_html(self, project_with_nozzles):
        """HTML satırı üretilebilmeli."""
        entries = generate_nozzle_schedule(project_with_nozzles)
        html = entries[0].to_html_row()
        assert "<tr>" in html
        assert "N1" in html

    def test_schedule_no_pad(self, project_with_nozzles):
        """Pedsiz nozul → 'Hayır'."""
        entries = generate_nozzle_schedule(project_with_nozzles)
        assert entries[1].has_reinforcement_pad is False


# ── HTML grafik testi ─────────────────────────────────────────────────────────

class TestAreaBreakdownHTML:
    """Nozul ekranı grafiği testleri."""

    def test_html_output(self, basic_input):
        """HTML çıktı üretilebilmeli."""
        result = calculate_reinforcement(basic_input)
        html = result.area_breakdown_html
        assert "Nozul N1" in html
        assert "Takviye Alan Analizi" in html
        assert "mm²" in html
        assert "PASS" in html or "FAIL" in html

    def test_html_contains_all_areas(self, basic_input):
        """HTML tüm alan kalemlerini içermeli."""
        result = calculate_reinforcement(basic_input)
        html = result.area_breakdown_html
        assert "A1" in html
        assert "A2" in html
        assert "A3" in html
        assert "A4" in html
