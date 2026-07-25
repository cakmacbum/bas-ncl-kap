"""Domain modelleri — birim testleri."""

import pytest
from pydantic import ValidationError

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    NozzleType,
    Orientation,
    ProductForm,
    ShellSection,
    VesselProject,
    WeldJoint,
)


# ── DesignConditions ──────────────────────────────────────────────────────────

class TestDesignConditions:
    """DesignConditions model testleri."""

    def _make_conditions(self, **kwargs):
        defaults = dict(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        defaults.update(kwargs)
        return DesignConditions(**defaults)

    def test_valid_conditions(self):
        dc = self._make_conditions()
        assert dc.operating_pressure == 1.0
        assert dc.design_pressure == 1.2
        assert dc.maximum_allowable_pressure_ps == 1.5

    def test_three_pressures_independent(self):
        """K4: Çalışma ≠ Tasarım ≠ PS — ayrı alanlar."""
        dc = self._make_conditions()
        assert dc.operating_pressure != dc.design_pressure
        assert dc.design_pressure != dc.maximum_allowable_pressure_ps

    def test_frozen(self):
        dc = self._make_conditions()
        with pytest.raises(ValidationError):
            dc.operating_pressure = 2.0

    def test_negative_pressure_rejected(self):
        with pytest.raises(ValidationError):
            self._make_conditions(operating_pressure=-1.0)

    def test_zero_pressure_rejected(self):
        with pytest.raises(ValidationError):
            self._make_conditions(design_pressure=0.0)

    def test_default_corrosion_zero(self):
        dc = self._make_conditions()
        assert dc.corrosion_allowance_internal == 0.0
        assert dc.corrosion_allowance_external == 0.0

    def test_default_test_temperature(self):
        dc = self._make_conditions()
        assert dc.hydrotest_temperature == 20.0


# ── ShellSection ──────────────────────────────────────────────────────────────

class TestShellSection:
    """ShellSection model testleri."""

    def _make_shell(self, **kwargs):
        defaults = dict(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        defaults.update(kwargs)
        return ShellSection(**defaults)

    def test_valid_shell(self):
        s = self._make_shell()
        assert s.inside_diameter == 1000.0
        assert s.nominal_thickness == 12.0

    def test_outside_diameter_only(self):
        s = self._make_shell(inside_diameter=None, outside_diameter=1024.0)
        assert s.outside_diameter == 1024.0

    def test_no_diameter_rejected(self):
        with pytest.raises(ValidationError):
            self._make_shell(inside_diameter=None)

    def test_default_mill_tolerance_zero(self):
        s = self._make_shell()
        assert s.mill_tolerance == 0.0


# ── Head ──────────────────────────────────────────────────────────────────────

class TestHead:
    """Head model testleri."""

    def _make_head(self, **kwargs):
        defaults = dict(
            head_id="HEAD-L",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        defaults.update(kwargs)
        return Head(**defaults)

    def test_valid_elliptical(self):
        h = self._make_head()
        assert h.type == HeadType.ELLIPTICAL
        assert h.inside_diameter == 1000.0

    def test_torispherical_with_radii(self):
        h = self._make_head(
            type=HeadType.TORISPHERICAL,
            crown_radius=1000.0,
            knuckle_radius=100.0,
        )
        assert h.crown_radius == 1000.0
        assert h.knuckle_radius == 100.0

    def test_hemispherical(self):
        h = self._make_head(type=HeadType.HEMISPHERICAL)
        assert h.type == HeadType.HEMISPHERICAL

    def test_default_straight_flange(self):
        h = self._make_head()
        assert h.straight_flange_length == 25.0


# ── Nozzle ────────────────────────────────────────────────────────────────────

class TestNozzle:
    """Nozzle model testleri."""

    def _make_nozzle(self, **kwargs):
        defaults = dict(
            tag="N1",
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-01",
        )
        defaults.update(kwargs)
        return Nozzle(**defaults)

    def test_valid_nozzle(self):
        n = self._make_nozzle()
        assert n.tag == "N1"
        assert n.axial_position == 500.0
        assert n.circumferential_angle == 0.0

    def test_radyal_nozzle(self):
        """V1: Radyal nozul (α = 0)."""
        n = self._make_nozzle(inclination_angle=0.0)
        assert n.inclination_angle == 0.0

    def test_circumferential_angle_range(self):
        n = self._make_nozzle(circumferential_angle=180.0)
        assert n.circumferential_angle == 180.0

    def test_invalid_angle(self):
        with pytest.raises(ValidationError):
            self._make_nozzle(circumferential_angle=400.0)

    def test_default_no_reinforcement_pad(self):
        n = self._make_nozzle()
        assert n.reinforcement_pad is False


# ── MaterialProperty ──────────────────────────────────────────────────────────

class TestMaterialProperty:
    """MaterialProperty model testleri."""

    def _make_material(self, **kwargs):
        defaults = dict(
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
        defaults.update(kwargs)
        return MaterialProperty(**defaults)

    def test_valid_material(self):
        m = self._make_material()
        assert m.allowable_stress == 138.0
        assert m.yield_strength == 260.0

    def test_frozen(self):
        m = self._make_material()
        with pytest.raises(ValidationError):
            m.allowable_stress = 150.0

    def test_default_thickness_range(self):
        m = self._make_material()
        assert m.thickness_min == 0.0
        assert m.thickness_max == 999.0


# ── WeldJoint ─────────────────────────────────────────────────────────────────

class TestWeldJoint:
    """WeldJoint model testleri."""

    def test_valid_weld(self):
        w = WeldJoint(
            joint_id="WJ-01",
            joint_type="longitudinal",
            joint_efficiency=1.0,
        )
        assert w.joint_efficiency == 1.0
        assert w.full_penetration is True

    def test_joint_efficiency_range(self):
        w = WeldJoint(joint_id="WJ-02", joint_type="circumferential", joint_efficiency=0.7)
        assert w.joint_efficiency == 0.7

    def test_invalid_efficiency(self):
        with pytest.raises(ValidationError):
            WeldJoint(joint_id="WJ-03", joint_type="test", joint_efficiency=1.5)


# ── VesselProject ─────────────────────────────────────────────────────────────

class TestVesselProject:
    """VesselProject model testleri."""

    def _make_project(self, **kwargs):
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        head_l = Head(
            head_id="HEAD-L",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        head_r = Head(
            head_id="HEAD-R",
            type=HeadType.ELLIPTICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
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
        )
        defaults = dict(
            project_number="PRJ-001",
            project_name="Test Vessel",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            heads=[head_l, head_r],
            materials=[mat],
        )
        defaults.update(kwargs)
        return VesselProject(**defaults)

    def test_valid_project(self):
        p = self._make_project()
        assert p.project_number == "PRJ-001"
        assert p.calculation_code == CalculationCode.ASME_VIII_1
        assert len(p.shell_sections) == 1
        assert len(p.heads) == 2

    def test_get_material(self):
        p = self._make_project()
        mat = p.get_material("MAT-01")
        assert mat is not None
        assert mat.allowable_stress == 138.0

    def test_get_material_not_found(self):
        p = self._make_project()
        assert p.get_material("NONEXISTENT") is None

    def test_default_orientation(self):
        p = self._make_project()
        assert p.orientation == Orientation.VERTICAL
