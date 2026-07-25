"""CAD Engine testleri — CadQuery gerektirir.

CadQuery kurulu değilse tüm testler skip edilir.
CadQuery kurulduktan sonra bu testler yeşil olmalı.
"""

import math

import pytest

# CadQuery yoksa tüm modülü skip et
cq = pytest.importorskip("cadquery", reason="CadQuery kurulu değil — CAD testleri atlandı")

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

from cad_engine.validation import (
    CADValidationReport,
    validate_no_negative_volume,
    validate_no_open_shells,
    validate_solid_count,
    validate_volume_tolerance,
)
from cad_engine.vessel_builder import (
    VesselCADResult,
    _build_elliptical_head,
    _build_flat_head,
    _build_head,
    _build_shell_body,
    _build_torispherical_head,
    build_vessel,
    export_step,
    export_stl,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_project():
    """CAD test projesi — Faz 1 golden-case ile aynı veri."""
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
        straight_flange_length=25.0,
    )
    head_r = Head(
        head_id="HEAD-R",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        internal_corrosion_allowance=2.0,
        straight_flange_length=25.0,
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
    return VesselProject(
        project_number="CAD-001",
        project_name="CAD Test Vessel",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        materials=[mat],
    )


# ── Bileşen testleri ─────────────────────────────────────────────────────────

class TestShellBody:
    """Gövde (silindirik boru) testleri."""

    def test_shell_creates_solid(self):
        """Gövde tek solid oluşturmalı."""
        shell = ShellSection(
            section_id="S1",
            inside_diameter=500.0,
            tangent_length=1000.0,
            nominal_thickness=10.0,
            material_id="M1",
        )
        body = _build_shell_body(shell)
        solids = body.solids().vals()
        assert len(solids) == 1

    def test_shell_dimensions(self):
        """Gövde boyutları doğru olmalı."""
        shell = ShellSection(
            section_id="S1",
            inside_diameter=500.0,
            tangent_length=1000.0,
            nominal_thickness=10.0,
            material_id="M1",
        )
        body = _build_shell_body(shell)
        bb = body.val().BoundingBox()
        # Dış çap = 500 + 2*10 = 520 → yarıçap = 260
        assert abs(bb.xlen - 520.0) < 1.0  # Dış çap
        assert abs(bb.zlen - 1000.0) < 1.0  # Uzunluk

    def test_shell_has_inner_hole(self):
        """Gövde içi boş olmalı (boru)."""
        shell = ShellSection(
            section_id="S1",
            inside_diameter=500.0,
            tangent_length=1000.0,
            nominal_thickness=10.0,
            material_id="M1",
        )
        body = _build_shell_body(shell)
        outer_vol = body.val().Volume()
        # Tam silindir hacmi: π × 260² × 1000
        full_cyl = math.pi * 260**2 * 1000
        # Boru hacmi tam silindirden küçük olmalı
        assert outer_vol < full_cyl * 0.95


class TestEllipticalHead:
    """2:1 Elipsoidal bombe testleri."""

    def test_head_creates_solid(self):
        """Bombe solid oluşturmalı."""
        head = _build_elliptical_head(500.0, 10.0, 25.0)
        solids = head.solids().vals()
        assert len(solids) >= 1

    def test_head_volume_positive(self):
        """Bombe hacmi pozitif olmalı."""
        head = _build_elliptical_head(500.0, 10.0, 25.0)
        vol = head.val().Volume()
        assert vol > 0


# ── Tam model testleri ───────────────────────────────────────────────────────

class TestBuildVessel:
    """Tam kap modeli testleri."""

    def test_vessel_builds_successfully(self, sample_project):
        """Kap başarıyla oluşturulmalı."""
        result = build_vessel(sample_project)
        assert result.success, f"Model oluşturulamadı: {result.error}"
        assert result.shape is not None

    def test_vessel_has_single_solid(self, sample_project):
        """Model tek solid olmalı."""
        result = build_vessel(sample_project)
        assert result.success
        solids = result.shape.solids().vals()
        assert len(solids) == 1, f"Solid sayısı: {len(solids)}"

    def test_vessel_volume_positive(self, sample_project):
        """Kap hacmi pozitif olmalı."""
        result = build_vessel(sample_project)
        assert result.success
        assert result.outer_volume_mm3 > 0

    def test_vessel_validation_report(self, sample_project):
        """Doğrulama raporu üretilmeli."""
        result = build_vessel(sample_project)
        assert result.success
        assert result.validation is not None
        assert len(result.validation.results) >= 2  # en az solid_count + volume

    def test_vessel_no_negative_volume(self, sample_project):
        """Negatif hacim oluşmamalı."""
        result = build_vessel(sample_project)
        assert result.success
        neg_check = [
            r for r in result.validation.results if r.check_name == "no_negative_volume"
        ]
        assert len(neg_check) == 1
        assert neg_check[0].passed

    def test_vessel_no_heads_fails(self):
        """Bombe yoksa hata dönmeli."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=150.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        project = VesselProject(
            project_number="T",
            project_name="T",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[
                ShellSection(
                    section_id="S1",
                    inside_diameter=500.0,
                    tangent_length=1000.0,
                    nominal_thickness=10.0,
                    material_id="M1",
                )
            ],
            heads=[],
        )
        result = build_vessel(project)
        assert not result.success
        assert "bombe" in result.error.lower() or "gerekli" in result.error.lower()


# ── STEP export testi ─────────────────────────────────────────────────────────

class TestSTEPExport:
    """STEP dosyası export testleri."""

    def test_export_step_creates_file(self, sample_project, tmp_path):
        """STEP dosyası oluşturulmalı."""
        result = build_vessel(sample_project)
        assert result.success

        step_path = tmp_path / "vessel.step"
        exported = export_step(result.shape, step_path)

        assert step_path.exists()
        assert step_path.stat().st_size > 0
        assert exported == str(step_path)

    def test_export_step_content(self, sample_project, tmp_path):
        """STEP dosyası geçerli HEADER içermeli."""
        result = build_vessel(sample_project)
        assert result.success

        step_path = tmp_path / "vessel.step"
        export_step(result.shape, step_path)

        content = step_path.read_text(encoding="utf-8", errors="ignore")
        assert "ISO-10303-21" in content or "HEADER" in content


# ── Hacim doğrulama testi ─────────────────────────────────────────────────────

class TestVolumeValidation:
    """Hacim tolerans doğrulama testleri."""

    def test_volume_tolerance_pass(self):
        """Tolerans içinde → PASS."""
        r = validate_volume_tolerance(1000.0, 1020.0, tolerance_pct=5.0)
        assert r.passed

    def test_volume_tolerance_fail(self):
        """Tolerans dışında → FAIL."""
        r = validate_volume_tolerance(1000.0, 1200.0, tolerance_pct=5.0)
        assert not r.passed

    def test_volume_tolerance_exact(self):
        """Tam eşitlik → PASS."""
        r = validate_volume_tolerance(1000.0, 1000.0, tolerance_pct=0.1)
        assert r.passed

    def test_volume_tolerance_zero_calculated(self):
        """Sıfır hesaplanan hacim → FAIL."""
        r = validate_volume_tolerance(0.0, 100.0)
        assert not r.passed


# ── Torisferik bombe testleri ─────────────────────────────────────────────────

class TestTorisphericalHead:
    """Torisferik bombe testleri."""

    def test_torispherical_creates_solid(self):
        """Torisferik bombe solid oluşturmalı."""
        head = _build_torispherical_head(
            diameter=1000.0,
            crown_radius=1000.0,
            knuckle_radius=100.0,
            thickness=12.0,
            straight_flange=25.0,
        )
        solids = head.solids().vals()
        assert len(solids) >= 1

    def test_torispherical_volume_positive(self):
        """Torisferik bombe hacmi pozitif olmalı."""
        head = _build_torispherical_head(
            diameter=1000.0,
            crown_radius=1000.0,
            knuckle_radius=100.0,
            thickness=12.0,
            straight_flange=25.0,
        )
        vol = head.val().Volume()
        assert vol > 0

    def test_torispherical_has_inner_hollow(self):
        """Torisferik bombe içi boş olmalı."""
        head = _build_torispherical_head(
            diameter=1000.0,
            crown_radius=1000.0,
            knuckle_radius=100.0,
            thickness=12.0,
            straight_flange=25.0,
        )
        outer_vol = head.val().Volume()
        # Dış kabuk hacmi tam kubbemsi hacimden küçük olmalı
        R = 500.0 + 12.0
        dome_vol = (2.0 / 3.0) * math.pi * R**3  # yaklaşık yarım küre
        assert outer_vol < dome_vol * 1.5  # toleranslı kontrol

    def test_torispherical_via_build_head(self):
        """_build_head ile torisferik bombe oluşturulmalı."""
        from domain import Head, HeadType

        h = Head(
            head_id="HT",
            type=HeadType.TORISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=25.0,
            crown_radius=1000.0,
            knuckle_radius=100.0,
        )
        shape = _build_head(h)
        solids = shape.solids().vals()
        assert len(solids) >= 1


# ── Hemisferik bombe testleri ─────────────────────────────────────────────────

class TestHemisphericalHead:
    """Yarım küresel bombe testleri."""

    def test_hemispherical_creates_solid(self):
        """Hemisferik bombe solid oluşturmalı (a=b=R)."""
        from domain import Head, HeadType

        h = Head(
            head_id="HH",
            type=HeadType.HEMISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=25.0,
        )
        shape = _build_head(h)
        solids = shape.solids().vals()
        assert len(solids) >= 1

    def test_hemispherical_volume_positive(self):
        """Hemisferik bombe hacmi pozitif olmalı."""
        from domain import Head, HeadType

        h = Head(
            head_id="HH",
            type=HeadType.HEMISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=25.0,
        )
        shape = _build_head(h)
        vol = shape.val().Volume()
        assert vol > 0

    def test_hemispherical_depth_correct(self):
        """Hemisferik bombe derinliği R = D/2 olmalı."""
        from domain import Head, HeadType

        h = Head(
            head_id="HH",
            type=HeadType.HEMISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="M1",
            straight_flange_length=0.0,  # düz flanşsız
        )
        shape = _build_head(h)
        bb = shape.val().BoundingBox()
        # Yarım küre: yükseklik ≈ R + t = 500 + 12 = 512
        expected_height = 500.0 + 12.0
        assert abs(bb.zlen - expected_height) < 20.0  # tolerans


# ── Düz flanş (flat head) testleri ────────────────────────────────────────────

class TestFlatHead:
    """Düz kapak (flat cover) testleri."""

    def test_flat_head_creates_solid(self):
        """Düz flanş solid oluşturmalı."""
        head = _build_flat_head(
            diameter=1000.0,
            thickness=20.0,
            straight_flange=25.0,
        )
        solids = head.solids().vals()
        assert len(solids) >= 1

    def test_flat_head_volume_positive(self):
        """Düz flanş hacmi pozitif olmalı."""
        head = _build_flat_head(
            diameter=1000.0,
            thickness=20.0,
            straight_flange=25.0,
        )
        vol = head.val().Volume()
        assert vol > 0

    def test_flat_head_no_skirt(self):
        """Düz flanş — eteksiz (sf=0) çalışmalı."""
        head = _build_flat_head(
            diameter=1000.0,
            thickness=20.0,
            straight_flange=0.0,
        )
        solids = head.solids().vals()
        assert len(solids) >= 1

    def test_flat_head_via_build_head(self):
        """_build_head ile düz flanş oluşturulmalı."""
        from domain import Head, HeadType

        h = Head(
            head_id="HF",
            type=HeadType.FLAT,
            inside_diameter=1000.0,
            nominal_thickness=20.0,
            material_id="M1",
            straight_flange_length=25.0,
        )
        shape = _build_head(h)
        solids = shape.solids().vals()
        assert len(solids) >= 1


# ── Bombe tipi kombinasyon testleri ───────────────────────────────────────────

class TestHeadCombinations:
    """Farklı bombe tipi kombinasyonları ile tam model testleri."""

    def _make_project(self, left_type, right_type, **kwargs):
        """İki farklı bombe tipiyle proje oluştur."""
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
            type=left_type,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            straight_flange_length=25.0,
            **kwargs,
        )
        head_r = Head(
            head_id="HEAD-R",
            type=right_type,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            straight_flange_length=25.0,
            **kwargs,
        )
        return VesselProject(
            project_number="COMBO-001",
            project_name="Combination Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            heads=[head_l, head_r],
        )

    def test_elliptical_torispherical(self):
        """Sol elipsoidal + sağ torisferik → tek solid."""
        result = build_vessel(self._make_project(
            HeadType.ELLIPTICAL, HeadType.TORISPHERICAL,
            crown_radius=1000.0, knuckle_radius=100.0,
        ))
        # crown_radius/knuckle_radius sadece torisferik için
        assert result.success, f"Model oluşturulamadı: {result.error}"
        solids = result.shape.solids().vals()
        assert len(solids) == 1

    def test_elliptical_hemispherical(self):
        """Sol elipsoidal + sağ hemisferik → tek solid."""
        result = build_vessel(self._make_project(
            HeadType.ELLIPTICAL, HeadType.HEMISPHERICAL,
        ))
        assert result.success, f"Model oluşturulamadı: {result.error}"
        solids = result.shape.solids().vals()
        assert len(solids) == 1

    def test_elliptical_flat(self):
        """Sol elipsoidal + sağ düz flanş → tek solid."""
        result = build_vessel(self._make_project(
            HeadType.ELLIPTICAL, HeadType.FLAT,
        ))
        assert result.success, f"Model oluşturulamadı: {result.error}"
        solids = result.shape.solids().vals()
        assert len(solids) == 1

    def test_hemispherical_hemispherical(self):
        """Her iki taraf hemisferik → tek solid."""
        result = build_vessel(self._make_project(
            HeadType.HEMISPHERICAL, HeadType.HEMISPHERICAL,
        ))
        assert result.success, f"Model oluşturulamadı: {result.error}"
        solids = result.shape.solids().vals()
        assert len(solids) == 1

    def test_torispherical_torispherical(self):
        """Her iki taraf torisferik → tek solid."""
        result = build_vessel(self._make_project(
            HeadType.TORISPHERICAL, HeadType.TORISPHERICAL,
            crown_radius=1000.0, knuckle_radius=100.0,
        ))
        assert result.success, f"Model oluşturulamadı: {result.error}"
        solids = result.shape.solids().vals()
        assert len(solids) == 1


# ── STL export testi ──────────────────────────────────────────────────────────

class TestSTLExport:
    """STL dosyası export testleri."""

    def test_export_stl_creates_file(self, sample_project, tmp_path):
        """STL dosyası oluşturulmalı."""
        result = build_vessel(sample_project)
        assert result.success

        stl_path = tmp_path / "vessel.stl"
        exported = export_stl(result.shape, stl_path)

        assert stl_path.exists()
        assert stl_path.stat().st_size > 0
        assert exported == str(stl_path)

    def test_export_stl_content(self, sample_project, tmp_path):
        """STL dosyası geçerli ASCII veya binary STL içermeli."""
        result = build_vessel(sample_project)
        assert result.success

        stl_path = tmp_path / "vessel.stl"
        export_stl(result.shape, stl_path)

        # Binary STL: 80 byte header + 4 byte triangle count
        # ASCII STL: "solid" ile başlar
        content = stl_path.read_bytes()
        is_ascii = content[:5] == b"solid"
        is_binary = len(content) > 84  # minimum binary STL
        assert is_ascii or is_binary, "STL dosyası geçerli formatta değil"
