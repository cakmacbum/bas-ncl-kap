"""Faz 2 — FEA doğrulama laboratuvarı: 1/8 simetri modeli testleri (2.2, 2.8 kısmi).

Çözücü gerektirmez; yalnızca geometri önkoşulu + boolean kesim + hacim
doğrulamasını test eder. K2: FEA/CAD çıktısı hesabın kaynağı değildir — bu
testler yalnızca geometrik doğruluğu (1/8 hacim oranı) kontrol eder.

CadQuery gerektiren testler `pytest.mark.skipif(not CADQUERY_AVAILABLE)` ile
korunur (bkz. tests/cad-validation/test_cad_nozzle_integration.py:22).
"""

import pytest

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    ProductForm,
    ShellSection,
    VesselProject,
)
from fea.geometry_prep import (
    CADQUERY_AVAILABLE,
    build_eighth_symmetry_geometry,
    check_symmetry_preconditions,
)


def _design_conditions(**overrides):
    defaults = dict(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0, design_temperature=200.0, minimum_design_temperature=-10.0,
    )
    defaults.update(overrides)
    return DesignConditions(**defaults)


def _material(**overrides):
    defaults = dict(
        material_id="M1", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
        yield_strength=260.0, tensile_strength=485.0, source_reference="ASME II-D Table 1A",
    )
    defaults.update(overrides)
    return MaterialProperty(**defaults)


def _nozzle(**overrides):
    defaults = dict(
        tag="N1", host_component_id="SHELL-01", axial_position=800.0,
        outside_diameter=168.3, inside_diameter=154.1, neck_thickness=7.1,
        material_id="M1",
    )
    defaults.update(overrides)
    return Nozzle(**defaults)


def _symmetric_project(head_type=HeadType.ELLIPTICAL, head_kwargs=None):
    """Nozulsuz, iki bombesi özdeş, yalnız iç basınçlı kap — 1/8 model için geçerli."""
    head_kwargs = head_kwargs or {}
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000.0, tangent_length=2000.0,
        nominal_thickness=12.0, material_id="M1",
    )
    hl = Head(head_id="HL", type=head_type, inside_diameter=1000.0, nominal_thickness=12.0,
              material_id="M1", **head_kwargs)
    hr = Head(head_id="HR", type=head_type, inside_diameter=1000.0, nominal_thickness=12.0,
              material_id="M1", **head_kwargs)
    return VesselProject(
        project_number="P-FEA-01", project_name="FEA lab test kabı",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=_design_conditions(),
        shell_sections=[shell], heads=[hl, hr], materials=[_material()],
    )


# ── Önkoşullar — sessizce zorlama YOK (K4) ────────────────────────────────────

class TestSymmetryPreconditions:

    def test_valid_project_has_no_rejection(self):
        assert check_symmetry_preconditions(_symmetric_project()) == []

    def test_nozzle_is_rejected(self):
        project = _symmetric_project()
        project = project.model_copy(update={"nozzles": [_nozzle()]})
        reasons = check_symmetry_preconditions(project)
        assert len(reasons) == 1
        assert "nozul" in reasons[0].lower()

    def test_mismatched_heads_are_rejected(self):
        project = _symmetric_project()
        mismatched_right = project.heads[1].model_copy(update={"nominal_thickness": 20.0})
        project = project.model_copy(update={"heads": [project.heads[0], mismatched_right]})
        reasons = check_symmetry_preconditions(project)
        assert any("özdeş" in r for r in reasons)

    def test_flat_head_is_rejected(self):
        project = _symmetric_project(head_type=HeadType.FLAT)
        reasons = check_symmetry_preconditions(project)
        assert any("FLAT" in r for r in reasons)

    def test_external_pressure_is_rejected(self):
        project = _symmetric_project()
        dc = project.design_conditions.model_copy(update={"external_pressure": 0.5})
        project = project.model_copy(update={"design_conditions": dc})
        reasons = check_symmetry_preconditions(project)
        assert any("dış bas" in r.lower() for r in reasons)

    def test_vacuum_condition_is_rejected(self):
        project = _symmetric_project()
        dc = project.design_conditions.model_copy(update={"vacuum_condition": True})
        project = project.model_copy(update={"design_conditions": dc})
        reasons = check_symmetry_preconditions(project)
        assert any("vakum" in r.lower() for r in reasons)

    def test_multiple_shell_sections_are_rejected(self):
        project = _symmetric_project()
        extra_shell = project.shell_sections[0].model_copy(update={"section_id": "SHELL-02"})
        project = project.model_copy(
            update={"shell_sections": [project.shell_sections[0], extra_shell]}
        )
        reasons = check_symmetry_preconditions(project)
        assert any("Gövde kesiti" in r for r in reasons)

    def test_wrong_head_count_is_rejected(self):
        project = _symmetric_project()
        project = project.model_copy(update={"heads": [project.heads[0]]})
        reasons = check_symmetry_preconditions(project)
        assert any("Bombe say" in r for r in reasons)


# ── 1/8 kesim + hacim doğrulaması (CadQuery gerektirir) ───────────────────────

@pytest.mark.skipif(not CADQUERY_AVAILABLE, reason="CadQuery kurulu değil")
class TestEighthSymmetryVolume:
    """1/8 kesme hacmi ≈ tam hacim / 8 (kaynak: onaylanmış Faz 2 planı, 2.8)."""

    @pytest.mark.parametrize(
        "head_type,head_kwargs",
        [
            (HeadType.ELLIPTICAL, {}),
            (HeadType.TORISPHERICAL, {"crown_radius": 1000.0, "knuckle_radius": 100.0}),
            (HeadType.HEMISPHERICAL, {}),
        ],
    )
    def test_eighth_volume_ratio_is_one_eighth(self, head_type, head_kwargs):
        project = _symmetric_project(head_type=head_type, head_kwargs=head_kwargs)
        result = build_eighth_symmetry_geometry(project)

        assert result.success, result.error
        assert result.full_volume_mm3 > 0
        assert result.eighth_volume_mm3 > 0
        assert result.volume_ratio == pytest.approx(0.125, rel=1e-3)
        assert not result.warnings

    def test_z_mid_is_half_tangent_length(self):
        project = _symmetric_project()
        result = build_eighth_symmetry_geometry(project)
        assert result.z_mid_mm == pytest.approx(1000.0)

    def test_rejected_project_returns_no_shape(self):
        """Önkoşul sağlanmazsa 1/8 model üretilmez — sessizce zorlama YOK (K4)."""
        project = _symmetric_project()
        project = project.model_copy(update={"nozzles": [_nozzle()]})

        result = build_eighth_symmetry_geometry(project)

        assert not result.success
        assert result.shape is None
        assert "nozul" in result.error.lower()

    def test_step_export(self, tmp_path):
        project = _symmetric_project()
        out = tmp_path / "eighth.step"
        result = build_eighth_symmetry_geometry(project, step_output_path=out)
        assert result.success
        assert result.step_path is not None
        assert out.exists()
