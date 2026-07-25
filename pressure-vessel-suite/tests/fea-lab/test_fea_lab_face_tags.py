"""Faz 2 — FEA doğrulama laboratuvarı: yüzey etiketleme testleri (2.3, 2.8 kısmi).

Boolean işlemlerden (1/8 kesim) sonra yüzey NUMARASINA güvenilmediğini,
yüzeylerin geometrik imzayla (kap eksenine uzaklık, yüzey tipi, normal yönü,
eksenel konum) doğru sınıflandırıldığını doğrular. Bilinen (elliptical/
torispherical/hemispherical) geometrilerde beklenen etiketlerin çıktığı ve
hiçbir yüzeyin sessizce yanlış varsayılmadığı (K4) test edilir.

CadQuery gerektirir; kurulu değilse tüm modül atlanır (bkz.
tests/cad-validation/test_cad_nozzle_integration.py:22).
"""

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
)
from cad_engine.vessel_builder import CADQUERY_AVAILABLE, build_vessel
from fea.face_tags import ALL_KNOWN_TAGS, PRESSURE_TAGS, SYMMETRY_TAGS, tag_vessel_faces
from fea.geometry_prep import build_eighth_symmetry_geometry

pytestmark = pytest.mark.skipif(not CADQUERY_AVAILABLE, reason="CadQuery kurulu değil")


def _project(head_type=HeadType.ELLIPTICAL, head_kwargs=None):
    head_kwargs = head_kwargs or {}
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0, design_temperature=200.0, minimum_design_temperature=-10.0,
    )
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000.0, tangent_length=2000.0,
        nominal_thickness=12.0, material_id="M1",
    )
    hl = Head(head_id="HL", type=head_type, inside_diameter=1000.0, nominal_thickness=12.0,
              material_id="M1", **head_kwargs)
    hr = Head(head_id="HR", type=head_type, inside_diameter=1000.0, nominal_thickness=12.0,
              material_id="M1", **head_kwargs)
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200.0, allowable_stress=138.0,
        yield_strength=260.0, tensile_strength=485.0, source_reference="x",
    )
    return VesselProject(
        project_number="P", project_name="t", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell],
        heads=[hl, hr], materials=[mat],
    ), shell


class TestFaceTagsOnFullModel:
    """Kesilmemiş (tam) modelde her iki bombe de mevcut — HEAD_L ve HEAD_R ayrı ayrı çıkmalı."""

    def test_known_tags_present(self):
        project, shell = _project()
        cad_result = build_vessel(project)
        assert cad_result.success

        result = tag_vessel_faces(cad_result.shape, shell, z_mid=None)

        assert result.success, result.error
        assert len(result.get("SHELL_INNER")) == 1
        assert len(result.get("SHELL_OUTER")) == 1
        assert len(result.get("HEAD_L_INNER")) > 0
        assert len(result.get("HEAD_R_INNER")) > 0
        # Kesilmemiş modelde simetri kesim yüzeyi yok — beklenen davranış.
        for sym_tag in SYMMETRY_TAGS:
            assert result.get(sym_tag) == []

    def test_shell_radii_match_expected(self):
        project, shell = _project()
        cad_result = build_vessel(project)
        result = tag_vessel_faces(cad_result.shape, shell, z_mid=None)

        inner_face = result.get("SHELL_INNER")[0]
        outer_face = result.get("SHELL_OUTER")[0]
        inner_r = (inner_face.center[0] ** 2 + inner_face.center[1] ** 2) ** 0.5
        outer_r = (outer_face.center[0] ** 2 + outer_face.center[1] ** 2) ** 0.5
        assert inner_r == pytest.approx(500.0, abs=1.0)
        assert outer_r == pytest.approx(512.0, abs=1.0)

    def test_no_unclassified_faces(self):
        project, shell = _project()
        cad_result = build_vessel(project)
        result = tag_vessel_faces(cad_result.shape, shell, z_mid=None)
        assert result.unclassified == []


class TestFaceTagsOnEighthModel:
    """1/8 kesilmiş modelde yalnızca bir bombe (kesimde kalan taraf) + 3 simetri yüzeyi olmalı."""

    def test_symmetry_and_pressure_tags_present(self):
        project, shell = _project()
        eighth = build_eighth_symmetry_geometry(project)
        assert eighth.success, eighth.error

        result = tag_vessel_faces(eighth.shape, shell, z_mid=eighth.z_mid_mm)

        assert result.success, result.error
        for sym_tag in SYMMETRY_TAGS:
            assert len(result.get(sym_tag)) == 1, f"{sym_tag} tam olarak 1 yüzey olmalı"
        assert len(result.get("SHELL_INNER")) == 1
        assert len(result.get("SHELL_OUTER")) == 1
        # Yalnızca bir bombe kalmalı (orta boy düzleminin ötesindeki taraf).
        heads_present = [
            t for t in ("HEAD_L_INNER", "HEAD_R_INNER") if result.get(t)
        ]
        assert len(heads_present) == 1

    def test_missing_symmetry_planes_would_error(self):
        """z_mid verilip simetri düzlemi bulunamazsa hata verilmeli (tam modelde beklenen)."""
        project, shell = _project()
        cad_result = build_vessel(project)
        # Kasıtlı olarak tam (kesilmemiş) modeli, kesilmiş model bekleyen bir
        # z_mid ile etiketle — simetri yüzeyleri bulunamamalı.
        result = tag_vessel_faces(cad_result.shape, shell, z_mid=1000.0)
        assert not result.success
        assert result.error is not None

    @pytest.mark.parametrize(
        "head_type,head_kwargs",
        [
            (HeadType.TORISPHERICAL, {"crown_radius": 1000.0, "knuckle_radius": 100.0}),
            (HeadType.HEMISPHERICAL, {}),
        ],
    )
    def test_other_head_types_also_classify_cleanly(self, head_type, head_kwargs):
        project, shell = _project(head_type=head_type, head_kwargs=head_kwargs)
        eighth = build_eighth_symmetry_geometry(project)
        assert eighth.success, eighth.error

        result = tag_vessel_faces(eighth.shape, shell, z_mid=eighth.z_mid_mm)
        assert result.success, result.error


def test_all_known_tags_constant_matches_pressure_and_symmetry():
    """PRESSURE_TAGS + SYMMETRY_TAGS, ALL_KNOWN_TAGS'in bir alt kümesi olmalı."""
    for tag in PRESSURE_TAGS:
        assert tag in ALL_KNOWN_TAGS
    for tag in SYMMETRY_TAGS:
        assert tag in ALL_KNOWN_TAGS
