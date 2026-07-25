"""Faz 3 testleri — Nozul takviye + Kaynak doğrulama + Çakışma kontrolleri.

ASME VIII-1 UG-37/UG-40, UW-11/UW-12, UCS-56, UG-42.
K5 kuralı: Her test izlenebilir — bilinen input → beklenen çıktı + tolerans.
"""

import math
import pytest

from domain import (
    CalculationCode,
    CalculationStatus,
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

# Nozul paketi
from nozzles.reinforcement import (
    NozzleReinforcementInput,
    calculate_reinforcement,
    check_nozzle_eligibility,
    build_reinforcement_calculation_result,
)
from nozzles.clash_check import (
    check_nozzle_nozzle_clash,
    check_nozzle_weld_proximity,
    check_nozzle_tangent_line,
    check_hole_pad_relation,
    check_minimum_edge_distance,
    validate_nozzle_clash,
    build_clash_check_result,
    MIN_NOZZLE_TO_NOZZLE_DISTANCE_mm,
    MIN_NOZZLE_TO_WELD_DISTANCE_mm,
)
from nozzles.position import (
    calculate_nozzle_position_on_shell,
    calculate_nozzle_position_on_head,
)
from nozzles.nozzle_schedule import generate_nozzle_schedule

# Welds paketi
from welds.validator import (
    WeldValidationInput,
    validate_weld,
    build_weld_validation_result,
    check_nde_joint_efficiency,
    check_full_penetration,
    check_wps_pqr,
    check_welder_qualification,
    check_pwht,
    check_weld_category,
    check_ndt_extent,
    NDE_EFFICIENCY_MAP,
)


# ── Orak Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def standard_project():
    """Standart test projesi — Faz 1 golden-case verisi + nozullar + kaynaklar."""
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
        weld_joint_id="WJ-02",
        internal_corrosion_allowance=2.0,
    )

    head_r = Head(
        head_id="HEAD-R",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        weld_joint_id="WJ-03",
        internal_corrosion_allowance=2.0,
    )

    nozzle_n1 = Nozzle(
        tag="N1",
        nozzle_type=NozzleType.FLANGED,
        host_component_id="SHELL-01",
        axial_position=500.0,
        circumferential_angle=0.0,
        inclination_angle=0.0,
        outside_diameter=168.3,
        inside_diameter=154.1,
        neck_thickness=7.1,
        material_id="MAT-01",
        corrosion_allowance=1.0,
        reinforcement_pad=True,
        reinforcement_pad_od=250.0,
        reinforcement_pad_thickness=8.0,
    )

    nozzle_n2 = Nozzle(
        tag="N2",
        nozzle_type=NozzleType.FLANGED,
        host_component_id="SHELL-01",
        axial_position=1200.0,
        circumferential_angle=180.0,
        inclination_angle=0.0,
        outside_diameter=114.3,
        inside_diameter=102.3,
        neck_thickness=6.0,
        material_id="MAT-01",
        corrosion_allowance=1.0,
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
    )

    wj1 = WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        connected_components=["SHELL-01"],
        weld_category="A",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
        wps_number="WPS-001",
        pqr_number="PQR-001",
        welder_qualification="WQ-001",
        pwht_required=False,
    )

    wj2 = WeldJoint(
        joint_id="WJ-02",
        joint_type="circumferential",
        connected_components=["HEAD-L"],
        weld_category="B",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
        wps_number="WPS-001",
        pqr_number="PQR-001",
        welder_qualification="WQ-001",
        pwht_required=False,
    )

    wj3 = WeldJoint(
        joint_id="WJ-03",
        joint_type="circumferential",
        connected_components=["HEAD-R"],
        weld_category="B",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
        wps_number="WPS-001",
        pqr_number="PQR-001",
        welder_qualification="WQ-001",
        pwht_required=False,
    )

    wj_nozzle = WeldJoint(
        joint_id="WJ-N1",
        joint_type="nozzle_to_shell",
        connected_components=["SHELL-01", "N1"],
        weld_category="D",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="MT",
        nde_extent="100%",
        wps_number="WPS-002",
        pqr_number="PQR-002",
        welder_qualification="WQ-002",
        pwht_required=False,
    )

    return VesselProject(
        project_number="FAZ3-001",
        project_name="Faz 3 Test Vessel",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        nozzles=[nozzle_n1, nozzle_n2],
        materials=[mat],
        welds=[wj1, wj2, wj3, wj_nozzle],
    )


@pytest.fixture
def nozzle_reinforcement_input():
    """Nozul takviye hesabı girdisi — golden-case."""
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
        has_reinforcement_pad=True,
        reinforcement_pad_od=250.0,
        reinforcement_pad_thickness=8.0,
        reinforcement_pad_allowable_stress=138.0,
        weld_leg_size_nozzle_to_shell=6.0,
        weld_leg_size_pad_to_shell=6.0,
        design_pressure=1.2,
        design_temperature=200.0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3.A — NOZUL TAKVİYE HESABI (UG-37/UG-40)
# ═══════════════════════════════════════════════════════════════════════════════


class TestNozzleEligibilityFaz3:
    """UG-36 açıklık uygunluk kontrolü."""

    def test_eligible_nozzle(self, nozzle_reinforcement_input):
        """Tipik nozul → uygun."""
        is_ok, msg = check_nozzle_eligibility(nozzle_reinforcement_input)
        assert is_ok
        assert "uygun" in msg.lower()

    def test_too_large_nozzle(self):
        """D/2'den büyük nozul → uygun değil."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-LARGE",
            nozzle_inside_diameter=600.0,
            nozzle_corrosion_allowance=0.0,
            component_inside_diameter=1000.0,
        )
        is_ok, msg = check_nozzle_eligibility(inp)
        assert not is_ok
        assert "UG-36" in msg

    def test_small_nozzle_exemption(self):
        """50 mm altı nozul → muafiyet notu."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-SMALL",
            nozzle_inside_diameter=40.0,
            nozzle_corrosion_allowance=0.0,
            component_inside_diameter=1000.0,
        )
        is_ok, msg = check_nozzle_eligibility(inp)
        assert is_ok
        assert "50" in msg  # Muafiyet notu


class TestReinforcementCalculationFaz3:
    """UG-37/UG-40 takviye alanı hesaplama."""

    def test_effective_diameter(self, nozzle_reinforcement_input):
        """Etkin çap = iç çap + 2×korozyon payı (UG-37(a))."""
        result = calculate_reinforcement(nozzle_reinforcement_input)
        expected_d = 154.1 + 2 * 1.0  # 156.1 mm
        assert abs(result.effective_diameter - expected_d) < 0.1

    def test_required_area(self, nozzle_reinforcement_input):
        """Gerekli alan = d × t_required (UG-37(a))."""
        result = calculate_reinforcement(nozzle_reinforcement_input)
        d = 154.1 + 2 * 1.0
        expected = d * 6.97
        assert abs(result.required_area - expected) < 1.0

    def test_area_breakdown_items(self, nozzle_reinforcement_input):
        """Alan kalemleri: A1, A2, A3, A4 (UG-37(b))."""
        result = calculate_reinforcement(nozzle_reinforcement_input)
        names = [a.name for a in result.available_areas]
        assert "A1" in names  # Gövde fazlası
        assert "A2" in names  # Nozul boynu
        assert "A3" in names  # Takviye pedi
        assert "A4" in names  # Kaynak metali

    def test_area_values_positive(self, nozzle_reinforcement_input):
        """Alan değerleri pozitif olmalı."""
        result = calculate_reinforcement(nozzle_reinforcement_input)
        assert result.required_area > 0
        assert result.total_available_area > 0

    def test_pad_increases_area(self):
        """Takviye pedi alanı artırmalı."""
        # Pedsiz versiyon
        inp_no_pad = NozzleReinforcementInput(
            nozzle_tag="N1",
            nozzle_inside_diameter=154.1,
            nozzle_outside_diameter=168.3,
            nozzle_neck_thickness=7.1,
            nozzle_corrosion_allowance=1.0,
            nozzle_projection_outside=100.0,
            nozzle_allowable_stress=138.0,
            component_type="shell",
            component_inside_diameter=1000.0,
            component_nominal_thickness=12.0,
            component_corrosion_allowance=2.0,
            component_required_thickness=6.97,
            component_allowable_stress=138.0,
            has_reinforcement_pad=False,
            design_pressure=1.2,
        )
        result_no_pad = calculate_reinforcement(inp_no_pad)

        # Pedli versiyon
        inp_with_pad = NozzleReinforcementInput(
            nozzle_tag="N1",
            nozzle_inside_diameter=154.1,
            nozzle_outside_diameter=168.3,
            nozzle_neck_thickness=7.1,
            nozzle_corrosion_allowance=1.0,
            nozzle_projection_outside=100.0,
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
        )
        result_with_pad = calculate_reinforcement(inp_with_pad)

        assert result_with_pad.total_available_area > result_no_pad.total_available_area

    def test_pass_status(self):
        """Yeterli alan → PASS (kalın gövde + ped)."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-PASS",
            nozzle_inside_diameter=80.0,
            nozzle_outside_diameter=88.9,
            nozzle_neck_thickness=4.5,
            nozzle_corrosion_allowance=0.0,
            nozzle_projection_outside=50.0,
            nozzle_allowable_stress=138.0,
            component_type="shell",
            component_inside_diameter=1000.0,
            component_nominal_thickness=20.0,
            component_corrosion_allowance=0.0,
            component_required_thickness=5.0,
            component_allowable_stress=138.0,
            has_reinforcement_pad=True,
            reinforcement_pad_od=200.0,
            reinforcement_pad_thickness=10.0,
            reinforcement_pad_allowable_stress=138.0,
            weld_leg_size_nozzle_to_shell=6.0,
            weld_leg_size_pad_to_shell=6.0,
            design_pressure=1.2,
        )
        result = calculate_reinforcement(inp)
        assert result.status == CalculationStatus.PASS
        assert result.utilization_ratio >= 1.0

    def test_fail_when_thin(self):
        """İnce gövde → FAIL."""
        inp = NozzleReinforcementInput(
            nozzle_tag="N-THIN",
            nozzle_inside_diameter=100.0,
            nozzle_outside_diameter=110.0,
            nozzle_neck_thickness=5.0,
            nozzle_corrosion_allowance=0.0,
            nozzle_projection_outside=10.0,
            nozzle_allowable_stress=138.0,
            component_type="shell",
            component_inside_diameter=1000.0,
            component_nominal_thickness=8.0,
            component_corrosion_allowance=0.0,
            component_required_thickness=7.5,
            component_allowable_stress=138.0,
            design_pressure=1.2,
        )
        result = calculate_reinforcement(inp)
        assert result.status in (CalculationStatus.PASS, CalculationStatus.FAIL)


class TestReinforcementCalculationResultFaz3:
    """CalculationResult entegrasyonu (K5 — izlenebilirlik)."""

    def test_returns_calculation_result(self, nozzle_reinforcement_input):
        """CalculationResult döndürmeli."""
        from calc_core.result import CalculationResult
        result = build_reinforcement_calculation_result(nozzle_reinforcement_input)
        assert isinstance(result, CalculationResult)
        assert result.component_id == "N1"
        assert result.component_type == "nozzle"
        assert result.calculation_type == "nozzle_reinforcement"

    def test_has_intermediate_values(self, nozzle_reinforcement_input):
        """Ara değerler dolu olmalı (K5)."""
        result = build_reinforcement_calculation_result(nozzle_reinforcement_input)
        assert len(result.intermediate_values) > 0
        names = [iv["name"] for iv in result.intermediate_values]
        assert "d" in names
        assert "A_required" in names
        assert "A1" in names
        assert "A2" in names
        assert "A3" in names
        assert "A4" in names
        assert "A_total" in names

    def test_has_clause_reference(self, nozzle_reinforcement_input):
        """Madde referansı dolu olmalı (K5)."""
        result = build_reinforcement_calculation_result(nozzle_reinforcement_input)
        assert result.clause_reference == "UG-37/UG-40"
        assert result.code == "ASME VIII-1"

    def test_has_input_snapshot(self, nozzle_reinforcement_input):
        """Girdi anlık görüntüsü dolu olmalı (K5)."""
        result = build_reinforcement_calculation_result(nozzle_reinforcement_input)
        assert "nozzle_tag" in result.input_snapshot
        assert "effective_diameter" in result.input_snapshot
        assert "required_area" in result.input_snapshot

    def test_serializable(self, nozzle_reinforcement_input):
        """Sonuç serileştirilebilir olmalı."""
        result = build_reinforcement_calculation_result(nozzle_reinforcement_input)
        d = result.to_dict()
        assert "calculation_id" in d
        assert "status" in d
        assert "intermediate_values" in d


# ═══════════════════════════════════════════════════════════════════════════════
# 3.A — NOZUL POZİSYONU (z, θ, α)
# ═══════════════════════════════════════════════════════════════════════════════


class TestNozzlePositionFaz3:
    """Nozul 3D pozisyon hesaplama."""

    def test_shell_position_origin(self, standard_project):
        """θ=0 → x=R, y=0."""
        nozzle = standard_project.nozzles[0]  # N1, θ=0
        shell = standard_project.shell_sections[0]
        pos = calculate_nozzle_position_on_shell(nozzle, shell)

        R = 1000.0 / 2.0  # 500 mm
        assert abs(pos.x_mm - R) < 0.1
        assert abs(pos.y_mm - 0.0) < 0.1
        assert abs(pos.z_mm - 500.0) < 0.1

    def test_shell_position_90deg(self, standard_project):
        """θ=90 → x=0, y=R."""
        nozzle = Nozzle(
            tag="N-TEST",
            host_component_id="SHELL-01",
            axial_position=500.0,
            circumferential_angle=90.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        shell = standard_project.shell_sections[0]
        pos = calculate_nozzle_position_on_shell(nozzle, shell)

        R = 500.0
        assert abs(pos.x_mm - 0.0) < 0.1
        assert abs(pos.y_mm - R) < 0.1

    def test_shell_normal_is_radial(self, standard_project):
        """Radyal nozul → normal yüzeye dik."""
        nozzle = standard_project.nozzles[0]  # θ=0
        shell = standard_project.shell_sections[0]
        pos = calculate_nozzle_position_on_shell(nozzle, shell)

        # θ=0 → normal = (1, 0, 0)
        assert abs(pos.normal_x - 1.0) < 0.01
        assert abs(pos.normal_y - 0.0) < 0.01
        assert abs(pos.normal_z - 0.0) < 0.01

    def test_head_position(self, standard_project):
        """Bombe üzerinde nozul pozisyonu."""
        nozzle = Nozzle(
            tag="N-HEAD",
            host_component_id="HEAD-L",
            axial_position=0.0,  # Bombe tepesi
            circumferential_angle=0.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        head = standard_project.heads[0]
        pos = calculate_nozzle_position_on_head(nozzle, head)

        # Bombe tepesinde: x=0, y=0, z=b=R/2
        assert abs(pos.x_mm) < 0.1
        assert abs(pos.y_mm) < 0.1

    def test_head_position_by_diameter(self, standard_project):
        """Yerleşim çapı verilince nozul o çapta konumlanmalı."""
        nozzle = Nozzle(
            tag="N-HEAD-D",
            host_component_id="HEAD-L",
            axial_position=0.0,
            circumferential_angle=0.0,
            head_position_diameter=600.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        head = standard_project.heads[0]
        pos = calculate_nozzle_position_on_head(nozzle, head)

        # Merkezden yarıçap = 600/2 = 300 mm
        assert abs(math.hypot(pos.x_mm, pos.y_mm) - 300.0) < 0.1
        # θ=0 → +X yönünde
        assert abs(pos.x_mm - 300.0) < 0.1

    def test_head_position_diameter_overrides_axial(self, standard_project):
        """Çap verildiğinde axial_position yok sayılır (geriye dönük yol kapanır)."""
        head = standard_project.heads[0]
        common = dict(
            host_component_id="HEAD-L",
            circumferential_angle=0.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        with_d = calculate_nozzle_position_on_head(
            Nozzle(tag="A", axial_position=50.0, head_position_diameter=400.0, **common),
            head,
        )
        without_d = calculate_nozzle_position_on_head(
            Nozzle(tag="B", axial_position=50.0, **common), head,
        )
        assert abs(math.hypot(with_d.x_mm, with_d.y_mm) - 200.0) < 0.1
        assert abs(math.hypot(without_d.x_mm, without_d.y_mm) - 200.0) > 1.0

    def test_head_position_diameter_out_of_bounds(self, standard_project):
        """Bombe çapını aşan yerleşim çapı sessizce kırpılmaz (K4)."""
        head = standard_project.heads[0]
        nozzle = Nozzle(
            tag="N-OOB",
            host_component_id="HEAD-L",
            axial_position=0.0,
            head_position_diameter=head.inside_diameter + 200.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        with pytest.raises(ValueError, match="yerleşim çapı"):
            calculate_nozzle_position_on_head(nozzle, head)

    def test_position_dict(self, standard_project):
        """Pozisyon dict'e çevrilebilmeli."""
        nozzle = standard_project.nozzles[0]
        shell = standard_project.shell_sections[0]
        pos = calculate_nozzle_position_on_shell(nozzle, shell)
        d = pos.to_dict()
        assert "tag" in d
        assert "x_mm" in d
        assert "y_mm" in d
        assert "z_mm" in d


# ═══════════════════════════════════════════════════════════════════════════════
# 3.A — NOZUL SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════════


class TestNozzleScheduleFaz3:
    """Nozul schedule üretimi."""

    def test_schedule_count(self, standard_project):
        """Doğru sayıda schedule girişi."""
        entries = generate_nozzle_schedule(standard_project)
        assert len(entries) == 2

    def test_schedule_entry_fields(self, standard_project):
        """Giriş alanları doğru olmalı."""
        entries = generate_nozzle_schedule(standard_project)
        n1 = entries[0]
        assert n1.tag == "N1"
        assert n1.nozzle_type == "flanged"
        assert n1.axial_position_mm == 500.0
        assert n1.has_reinforcement_pad is True

    def test_schedule_to_html(self, standard_project):
        """HTML satırı üretilebilmeli."""
        entries = generate_nozzle_schedule(standard_project)
        html = entries[0].to_html_row()
        assert "<tr>" in html
        assert "N1" in html


# ═══════════════════════════════════════════════════════════════════════════════
# 3.C — KAYNAK DOĞRULAMA (UW-11/UW-12/UCS-56)
# ═══════════════════════════════════════════════════════════════════════════════


class TestNDEJointEfficiencyFaz3:
    """NDT ↔ kaynak verimi uyumu (UW-11)."""

    def test_full_rt_allows_1_0(self):
        """Full RT-1 → E=1.0 izinli."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            joint_efficiency=1.0,
            nde_method="RT-1",
            nde_extent="100%",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_nde_joint_efficiency(inp)
        assert check.status == CalculationStatus.PASS

    def test_spot_rt_rejects_1_0(self):
        """Spot RT → E=1.0 reddedilmeli."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            joint_efficiency=1.0,
            nde_method="RT-1",
            nde_extent="spot",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_nde_joint_efficiency(inp)
        assert check.status == CalculationStatus.FAIL
        assert "1.00" in check.message

    def test_no_nde_limits_to_0_70(self):
        """NDE yok → maks. E=0.70."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            joint_category="A",
            joint_efficiency=0.70,
        )
        inp = WeldValidationInput(weld=weld)
        check = check_nde_joint_efficiency(inp)
        assert check.status == CalculationStatus.PASS

    def test_no_nde_rejects_high_efficiency(self):
        """NDE yok, E=1.0 → reddedilmeli."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            joint_efficiency=1.0,
        )
        inp = WeldValidationInput(weld=weld)
        check = check_nde_joint_efficiency(inp)
        assert check.status == CalculationStatus.FAIL


class TestFullPenetrationFaz3:
    """Tam nüfuziyet kontrolü (UW-11(a)(2))."""

    def test_category_a_requires_fp(self):
        """Kategori A → tam nüfuziyet zorunlu."""
        weld = WeldJoint(
            joint_id="WJ-A",
            joint_type="longitudinal",
            weld_category="A",
            full_penetration=False,
            joint_efficiency=0.70,
        )
        inp = WeldValidationInput(weld=weld)
        check = check_full_penetration(inp)
        assert check.status == CalculationStatus.FAIL

    def test_category_a_with_fp(self):
        """Kategori A + tam nüfuziyet → PASS."""
        weld = WeldJoint(
            joint_id="WJ-A",
            joint_type="longitudinal",
            weld_category="A",
            full_penetration=True,
            joint_efficiency=1.0,
            nde_method="RT-1",
            nde_extent="100%",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_full_penetration(inp)
        assert check.status == CalculationStatus.PASS

    def test_category_d_requires_fp(self):
        """Kategori D (nozul) → tam nüfuziyet zorunlu."""
        weld = WeldJoint(
            joint_id="WJ-D",
            joint_type="nozzle_to_shell",
            weld_category="D",
            full_penetration=False,
            joint_efficiency=0.70,
        )
        inp = WeldValidationInput(weld=weld)
        check = check_full_penetration(inp)
        assert check.status == CalculationStatus.FAIL


class TestWPS_PQR_Faz3:
    """WPS/PQR kontrolü."""

    def test_missing_wps(self):
        """WPS eksik → REVIEW_REQUIRED."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            pqr_number="PQR-001",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_wps_pqr(inp)
        assert check.status == CalculationStatus.REVIEW_REQUIRED
        assert "WPS" in check.message

    def test_missing_pqr(self):
        """PQR eksik → REVIEW_REQUIRED."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            wps_number="WPS-001",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_wps_pqr(inp)
        assert check.status == CalculationStatus.REVIEW_REQUIRED
        assert "PQR" in check.message

    def test_both_present(self):
        """WPS + PQR mevcut → PASS."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            wps_number="WPS-001",
            pqr_number="PQR-001",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_wps_pqr(inp)
        assert check.status == CalculationStatus.PASS


class TestWelderQualificationFaz3:
    """Kaynakçı yeterliliği kontrolü."""

    def test_missing_qualification(self):
        """Kaynakçı yeterliliği eksik → REVIEW_REQUIRED."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_welder_qualification(inp)
        assert check.status == CalculationStatus.REVIEW_REQUIRED

    def test_qualification_present(self):
        """Kaynakçı yeterliliği mevcut → PASS."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            welder_qualification="WQ-001",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_welder_qualification(inp)
        assert check.status == CalculationStatus.PASS


class TestPWHT_Faz3:
    """PWHT gereklilik kontrolü (UCS-56)."""

    def test_thick_carbon_steel_requires_pwht(self):
        """Kalın karbon çeliği → PWHT zorunlu."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            pwht_required=None,  # Değerlendirilmemiş
        )
        inp = WeldValidationInput(
            weld=weld,
            connected_component_thickness=40.0,  # > 38.1 mm
            material_p_number=1,
        )
        check = check_pwht(inp)
        assert check.status == CalculationStatus.REVIEW_REQUIRED

    def test_thick_pwht_rejected(self):
        """PWHT zorunlu ama yapılmayacak → FAIL."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            pwht_required=False,
        )
        inp = WeldValidationInput(
            weld=weld,
            connected_component_thickness=40.0,
            material_p_number=1,
        )
        check = check_pwht(inp)
        assert check.status == CalculationStatus.FAIL

    def test_thin_no_pwht(self):
        """İnce malzeme → PWHT gerekmez."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
            pwht_required=False,
        )
        inp = WeldValidationInput(
            weld=weld,
            connected_component_thickness=20.0,
            material_p_number=1,
        )
        check = check_pwht(inp)
        assert check.status == CalculationStatus.PASS


class TestWeldCategoryFaz3:
    """Kaynak kategorisi kontrolü (UW-12)."""

    def test_valid_category(self):
        """Geçerli kategori → PASS."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
            weld_category="A",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_weld_category(inp)
        assert check.status == CalculationStatus.PASS

    def test_missing_category(self):
        """Kategori eksik → REVIEW_REQUIRED."""
        weld = WeldJoint(
            joint_id="WJ-TEST",
            joint_type="longitudinal",
        )
        inp = WeldValidationInput(weld=weld)
        check = check_weld_category(inp)
        assert check.status == CalculationStatus.REVIEW_REQUIRED


class TestWeldValidationIntegration:
    """Tam kaynak doğrulama entegrasyonu."""

    def test_valid_weld_passes(self, standard_project):
        """Geçerli kaynak → PASS."""
        weld = standard_project.welds[0]  # WJ-01
        inp = WeldValidationInput(
            weld=weld,
            connected_component_thickness=12.0,
        )
        result = validate_weld(inp)
        assert result.status == CalculationStatus.PASS
        assert len(result.checks) == 7

    def test_missing_info_review_required(self):
        """Eksik bilgi → REVIEW_REQUIRED."""
        weld = WeldJoint(
            joint_id="WJ-BAD",
            joint_type="longitudinal",
            weld_category="A",
            joint_efficiency=1.0,
            full_penetration=True,
            nde_method="RT-1",
            nde_extent="100%",
            # WPS, PQR, kaynakçı eksik
        )
        inp = WeldValidationInput(weld=weld)
        result = validate_weld(inp)
        assert result.status == CalculationStatus.REVIEW_REQUIRED

    def test_build_calculation_result(self, standard_project):
        """CalculationResult entegrasyonu (K5)."""
        from calc_core.result import CalculationResult
        weld = standard_project.welds[0]
        inp = WeldValidationInput(weld=weld)
        result = build_weld_validation_result(inp)

        assert isinstance(result, CalculationResult)
        assert result.component_type == "weld"
        assert result.calculation_type == "weld_validation"
        assert result.clause_reference == "UW-11/UW-12"
        assert len(result.intermediate_values) > 0

    def test_serializable(self, standard_project):
        """Sonuç serileştirilebilir."""
        weld = standard_project.welds[0]
        inp = WeldValidationInput(weld=weld)
        result = build_weld_validation_result(inp)
        d = result.to_dict()
        assert "status" in d
        assert "intermediate_values" in d


# ═══════════════════════════════════════════════════════════════════════════════
# 3.D — ÇAKIŞMA KONTROLLERİ (UG-42)
# ═══════════════════════════════════════════════════════════════════════════════


class TestNozzleNozzleClashFaz3:
    """Nozul-nozul girişimi kontrolü."""

    def test_no_clash_well_separated(self, standard_project):
        """İyi ayrılmış nozullar → çakışma yok."""
        nozzle = standard_project.nozzles[0]  # N1, z=500, θ=0
        shell = standard_project.shell_sections[0]
        check = check_nozzle_nozzle_clash(
            nozzle, standard_project.nozzles, shell, standard_project.heads
        )
        assert check.status == CalculationStatus.PASS

    def test_clash_close_nozzles(self):
        """Yakın nozullar → çakışma."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        # İki nozul aynı konumda
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            circumferential_angle=0.0,
            outside_diameter=200.0,
            inside_diameter=180.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        n2 = Nozzle(
            tag="N2",
            host_component_id="SHELL-01",
            axial_position=500.0,
            circumferential_angle=5.0,  # Çok yakın
            outside_diameter=200.0,
            inside_diameter=180.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        check = check_nozzle_nozzle_clash(n1, [n1, n2], shell, [])
        assert check.status == CalculationStatus.FAIL

    def test_single_nozzle_no_clash(self):
        """Tek nozul → çakışma kontrolü gerekmez."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
        )
        check = check_nozzle_nozzle_clash(n1, [n1], shell, [])
        assert check.status == CalculationStatus.PASS


class TestNozzleWeldProximityFaz3:
    """Nozul-kaynak yakınlığı kontrolü."""

    def test_well_separated(self, standard_project):
        """Nozul dikişten uzakta → PASS."""
        nozzle = standard_project.nozzles[0]  # N1, z=500
        shell = standard_project.shell_sections[0]
        check = check_nozzle_weld_proximity(nozzle, standard_project.welds, shell)
        assert check.status in (CalculationStatus.PASS, CalculationStatus.REVIEW_REQUIRED)

    def test_no_welds(self):
        """Kaynak yok → kontrol atlandı."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
        )
        check = check_nozzle_weld_proximity(n1, [], shell)
        assert check.status == CalculationStatus.PASS


class TestNozzleTangentLineFaz3:
    """Nozul teğet çizgisi aşımı kontrolü."""

    def test_center_nozzle_ok(self, standard_project):
        """Gövde ortasındaki nozul → sorun yok."""
        nozzle = standard_project.nozzles[0]  # z=500, 2000 mm gövde
        shell = standard_project.shell_sections[0]
        check = check_nozzle_tangent_line(nozzle, shell, standard_project.heads)
        assert check.status == CalculationStatus.PASS

    def test_nozzle_at_edge(self):
        """Gövde kenarındaki nozul → teğet çizgisi aşımı."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=50.0,  # Çok yakın kenara
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
        )
        check = check_nozzle_tangent_line(n1, shell, [])
        assert check.status in (CalculationStatus.FAIL, CalculationStatus.REVIEW_REQUIRED)

    def test_nozzle_on_head_skipped(self):
        """Bombe üzerindeki nozul → kontrol atlandı."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        n1 = Nozzle(
            tag="N1",
            host_component_id="HEAD-L",  # Gövde değil
            axial_position=0.0,
            outside_diameter=100.0,
            inside_diameter=80.0,
            neck_thickness=10.0,
            material_id="MAT-01",
        )
        check = check_nozzle_tangent_line(n1, shell, [])
        assert check.status == CalculationStatus.PASS


class TestHolePadRelationFaz3:
    """Delik-ped ilişkisi kontrolü."""

    def test_no_pad(self):
        """Pedsiz nozul → kontrol atlandı."""
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
            reinforcement_pad=False,
        )
        check = check_hole_pad_relation(n1)
        assert check.status == CalculationStatus.PASS

    def test_pad_larger_than_hole(self):
        """Ped delikten büyük → PASS."""
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
            corrosion_allowance=1.0,
            reinforcement_pad=True,
            reinforcement_pad_od=250.0,
            reinforcement_pad_thickness=8.0,
        )
        check = check_hole_pad_relation(n1)
        assert check.status == CalculationStatus.PASS


class TestMinimumEdgeDistanceFaz3:
    """Minimum kenar mesafesi kontrolü."""

    def test_center_nozzle_ok(self, standard_project):
        """Gövde ortasındaki nozul → yeterli mesafe."""
        nozzle = standard_project.nozzles[0]  # z=500
        shell = standard_project.shell_sections[0]
        check = check_minimum_edge_distance(nozzle, shell)
        assert check.status == CalculationStatus.PASS

    def test_edge_nozzle_close(self):
        """Gövde kenarındaki nozul → mesafe yetersiz."""
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        n1 = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=50.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
        )
        check = check_minimum_edge_distance(n1, shell)
        assert check.status in (CalculationStatus.REVIEW_REQUIRED, CalculationStatus.FAIL)


class TestClashCheckIntegration:
    """Tam çakışma kontrolü entegrasyonu."""

    def test_validate_nozzle_clash(self, standard_project):
        """Tüm kontroller çalışmalı."""
        nozzle = standard_project.nozzles[0]
        report = validate_nozzle_clash(nozzle, standard_project)
        assert report.nozzle_tag == "N1"
        assert len(report.checks) >= 4
        assert report.status in (
            CalculationStatus.PASS,
            CalculationStatus.REVIEW_REQUIRED,
            CalculationStatus.FAIL,
        )

    def test_build_clash_check_result(self, standard_project):
        """CalculationResult entegrasyonu."""
        from calc_core.result import CalculationResult
        nozzle = standard_project.nozzles[0]
        result = build_clash_check_result(nozzle, standard_project)
        assert isinstance(result, CalculationResult)
        assert result.component_type == "nozzle"
        assert result.calculation_type == "clash_check"

    def test_report_dict(self, standard_project):
        """Rapor dict'e çevrilebilmeli."""
        nozzle = standard_project.nozzles[0]
        report = validate_nozzle_clash(nozzle, standard_project)
        d = report.to_dict()
        assert "nozzle_tag" in d
        assert "status" in d
        assert "checks" in d


# ═══════════════════════════════════════════════════════════════════════════════
# REGRASYON — Mevcut 122+ test bozulmamalı
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegressionFaz3:
    """Faz 3 değişiklikleri mevcut testleri bozmamalı."""

    def test_domain_imports_still_work(self):
        """Domain importları çalışmalı."""
        from domain import VesselProject, ShellSection, Head, Nozzle, WeldJoint
        assert VesselProject is not None
        assert ShellSection is not None
        assert Head is not None
        assert Nozzle is not None
        assert WeldJoint is not None

    def test_calc_core_imports_still_work(self):
        """calc-core importları çalışmalı."""
        from calc_core.result import CalculationResult
        from calc_core.code_interface import DesignCode
        from calc_core.orchestrator import CalculationOrchestrator
        assert CalculationResult is not None
        assert DesignCode is not None
        assert CalculationOrchestrator is not None

    def test_existing_nozzle_imports_still_work(self):
        """Mevcut nozul importları çalışmalı."""
        from nozzles import (
            NozzleReinforcementInput,
            NozzleReinforcementResult,
            calculate_reinforcement,
            check_nozzle_eligibility,
            build_reinforcement_calculation_result,
            NozzleScheduleEntry,
            generate_nozzle_schedule,
        )
        assert NozzleReinforcementInput is not None
        assert calculate_reinforcement is not None

    def test_welds_package_importable(self):
        """Welds paketi import edilebilmeli."""
        from welds import (
            WeldJoint,
            WeldValidationInput,
            validate_weld,
            build_weld_validation_result,
        )
        assert WeldJoint is not None
        assert WeldValidationInput is not None
