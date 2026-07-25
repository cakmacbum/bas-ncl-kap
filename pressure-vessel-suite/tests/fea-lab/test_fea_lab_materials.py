"""Faz 2 — FEA doğrulama laboratuvarı: malzeme elastik özellikleri testleri (2.1, 2.8 kısmi).

`MaterialProperty.elastic_modulus` / `poisson_ratio` opsiyoneldir (K3/K6 —
kullanıcı girer, standart tablosu gömülmez). Boş bırakılırsa laboratuvar
BLOCKED_CODE_DATA ile durur ve **varsayılan atamaz** (K4). Bu modül CadQuery
gerektirmez — yalnızca domain modeli + malzeme veri denetimini test eder.
"""

import pytest

from domain import (
    CalculationCode,
    CalculationStatus,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    VesselProject,
)
from fea.geometry_prep import check_material_elastic_properties


def _material(**overrides):
    defaults = dict(
        material_id="M1", standard_pack="ASME II-D 2025", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
        yield_strength=260.0, tensile_strength=485.0, source_reference="ASME II-D Table 1A",
    )
    defaults.update(overrides)
    return MaterialProperty(**defaults)


def _project(materials):
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0, design_temperature=200.0, minimum_design_temperature=-10.0,
    )
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000.0, tangent_length=2000.0,
        nominal_thickness=12.0, material_id="M1",
    )
    hl = Head(head_id="HL", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
              nominal_thickness=12.0, material_id="M1")
    hr = Head(head_id="HR", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
              nominal_thickness=12.0, material_id="M1")
    return VesselProject(
        project_number="P", project_name="t", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell],
        heads=[hl, hr], materials=materials,
    )


# ── MaterialProperty modeli — geriye dönük uyum + yeni alan doğrulaması ──────

class TestMaterialPropertyElasticFields:

    def test_fields_default_to_none(self):
        """Yeni alanlar opsiyonel; mevcut çağrılar hâlâ çalışmalı (geriye dönük uyum)."""
        mat = _material()
        assert mat.elastic_modulus is None
        assert mat.poisson_ratio is None

    def test_valid_values_accepted(self):
        mat = _material(elastic_modulus=200000.0, poisson_ratio=0.3)
        assert mat.elastic_modulus == 200000.0
        assert mat.poisson_ratio == 0.3

    def test_elastic_modulus_must_be_positive(self):
        with pytest.raises(ValueError):
            _material(elastic_modulus=0.0)
        with pytest.raises(ValueError):
            _material(elastic_modulus=-200000.0)

    def test_poisson_ratio_must_be_in_open_interval(self):
        with pytest.raises(ValueError):
            _material(poisson_ratio=0.0)
        with pytest.raises(ValueError):
            _material(poisson_ratio=0.5)
        with pytest.raises(ValueError):
            _material(poisson_ratio=0.6)


# ── Laboratuvar önkoşulu: eksik veri → BLOCKED_CODE_DATA, varsayım atanmaz ───

class TestMaterialElasticDataGate:

    def test_missing_elastic_modulus_blocks_lab(self):
        mat = _material()  # elastic_modulus / poisson_ratio boş
        project = _project([mat])

        result = check_material_elastic_properties(project)

        assert result is not None
        assert result.status == CalculationStatus.BLOCKED_CODE_DATA
        assert "elastic_modulus" in " ".join(result.warnings)

    def test_missing_poisson_ratio_blocks_lab(self):
        mat = _material(elastic_modulus=200000.0)  # poisson_ratio hâlâ boş
        project = _project([mat])

        result = check_material_elastic_properties(project)

        assert result is not None
        assert result.status == CalculationStatus.BLOCKED_CODE_DATA
        assert "poisson_ratio" in " ".join(result.warnings)

    def test_no_silent_default_is_assigned(self):
        """K4: Alan boşsa laboratuvar bir varsayılan DEĞER atamaz — yalnızca durur."""
        mat = _material()
        project = _project([mat])

        result = check_material_elastic_properties(project)

        # BLOCKED_CODE_DATA sonrasında dahi malzeme nesnesinin kendisi değişmemeli.
        assert project.get_material("M1").elastic_modulus is None
        assert project.get_material("M1").poisson_ratio is None
        assert result.final_result is None  # hiçbir sayısal sonuç üretilmedi

    def test_missing_material_reference_blocks_lab(self):
        """Gövde/bombenin referans ettiği malzeme proje listesinde yoksa da durur."""
        project = _project([])  # material_id="M1" tanımlı değil
        result = check_material_elastic_properties(project)
        assert result is not None
        assert result.status == CalculationStatus.BLOCKED_CODE_DATA

    def test_complete_data_returns_none(self):
        """Tüm veriler doluysa laboratuvar devam edebilir — engelleyici sonuç yok."""
        mat = _material(elastic_modulus=200000.0, poisson_ratio=0.3)
        project = _project([mat])

        result = check_material_elastic_properties(project)

        assert result is None
