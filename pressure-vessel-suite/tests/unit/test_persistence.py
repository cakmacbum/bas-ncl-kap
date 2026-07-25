"""JSON kaydetme/yükleme + SHA-256 hash — round-trip testleri."""

import json
import tempfile
from pathlib import Path

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
    compute_input_hash,
    load_project_json,
    save_project_json,
)


@pytest.fixture
def sample_project():
    """Round-trip test projesi."""
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
    )
    wj = WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        joint_efficiency=1.0,
    )
    return VesselProject(
        project_number="RT-001",
        project_name="Round-Trip Test",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        materials=[mat],
        welds=[wj],
    )


class TestComputeInputHash:
    """SHA-256 hash üretimi testleri."""

    def test_deterministic(self, sample_project):
        """Aynı projeden iki kez üretilen hash aynı olmalı."""
        h1 = compute_input_hash(sample_project)
        h2 = compute_input_hash(sample_project)
        assert h1 == h2

    def test_hex_format(self, sample_project):
        """Hash 64 karakterlik hex string olmalı."""
        h = compute_input_hash(sample_project)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_projects_different_hash(self, sample_project):
        """Farklı projeler farklı hash üretmeli."""
        other = sample_project.model_copy(update={"project_number": "RT-002"})
        assert compute_input_hash(sample_project) != compute_input_hash(other)

    def test_hash_ignores_input_file_hash_field(self, sample_project):
        """Hash hesaplanırken input_file_hash alanı göz ardı edilmeli."""
        h1 = compute_input_hash(sample_project)
        with_hash = sample_project.model_copy(update={"input_file_hash": "dummy"})
        h2 = compute_input_hash(with_hash)
        assert h1 == h2


class TestSaveLoadRoundTrip:
    """Kaydet → yükle → eşit round-trip testleri."""

    def test_roundtrip_equality(self, sample_project, tmp_path):
        """Kaydet → yükle → veri aynı olmalı."""
        fpath = tmp_path / "test_project.json"
        saved = save_project_json(sample_project, fpath)

        loaded = load_project_json(fpath)

        # Temel alanlar eşit
        assert loaded.project_number == sample_project.project_number
        assert loaded.project_name == sample_project.project_name
        assert loaded.calculation_code == sample_project.calculation_code
        assert loaded.code_edition == sample_project.code_edition
        assert loaded.design_conditions.operating_pressure == sample_project.design_conditions.operating_pressure
        assert len(loaded.shell_sections) == len(sample_project.shell_sections)
        assert len(loaded.heads) == len(sample_project.heads)
        assert len(loaded.materials) == len(sample_project.materials)

    def test_roundtrip_hash_set(self, sample_project, tmp_path):
        """Kaydetten sonra input_file_hash dolu olmalı."""
        fpath = tmp_path / "test_project.json"
        saved = save_project_json(sample_project, fpath)

        assert saved.input_file_hash is not None
        assert len(saved.input_file_hash) == 64

    def test_roundtrip_hash_persists(self, sample_project, tmp_path):
        """Yüklenen projede input_file_hash korunmalı."""
        fpath = tmp_path / "test_project.json"
        saved = save_project_json(sample_project, fpath)
        loaded = load_project_json(fpath)

        assert loaded.input_file_hash == saved.input_file_hash

    def test_roundtrip_double_save_same_hash(self, sample_project, tmp_path):
        """İki kez kaydet → aynı hash."""
        fpath = tmp_path / "test_project.json"
        save_project_json(sample_project, fpath)
        h1 = (tmp_path / "test_project.json").read_text()

        save_project_json(sample_project, fpath)
        h2 = (tmp_path / "test_project.json").read_text()

        # Dosya içerikleri aynı olmalı (deterministic)
        data1 = json.loads(h1)
        data2 = json.loads(h2)
        assert data1["input_file_hash"] == data2["input_file_hash"]

    def test_roundtrip_json_valid(self, sample_project, tmp_path):
        """Kaydedilen dosya geçerli JSON olmalı."""
        fpath = tmp_path / "test_project.json"
        save_project_json(sample_project, fpath)

        raw = fpath.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert "project_number" in data
        assert "input_file_hash" in data

    def test_load_nonexistent_raises(self, tmp_path):
        """Olmayan dosya → FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_project_json(tmp_path / "nonexistent.json")

    def test_load_invalid_json_raises(self, tmp_path):
        """Geçersiz JSON → ValueError."""
        fpath = tmp_path / "bad.json"
        fpath.write_text("not json {{{", encoding="utf-8")
        with pytest.raises(ValueError, match="Geçersiz JSON"):
            load_project_json(fpath)

    def test_hash_tamper_detection(self, sample_project, tmp_path):
        """Dosya değiştirilmişse hash doğrulama başarısız olmalı."""
        fpath = tmp_path / "test_project.json"
        save_project_json(sample_project, fpath)

        # Dosyayı elle değiştir
        raw = fpath.read_text(encoding="utf-8")
        data = json.loads(raw)
        data["project_name"] = "TAMPERED"
        fpath.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Yükleme hash doğrulaması yapmalı (uyarı veya hata)
        # Mevcut implementasyon ValueError fırlatıyor
        with pytest.raises(ValueError, match="Hash doğrulama başarısız"):
            load_project_json(fpath)

    def test_save_creates_parent_dirs(self, sample_project, tmp_path):
        """Üst klasörler yoksa otomatik oluşturulmalı."""
        fpath = tmp_path / "deep" / "nested" / "project.json"
        save_project_json(sample_project, fpath)
        assert fpath.exists()

    def test_roundtrip_model_dump_match(self, sample_project, tmp_path):
        """Yüklenen model_dump() ile kaydedilen dict eşleşmeli (hash hariç)."""
        fpath = tmp_path / "test_project.json"
        saved = save_project_json(sample_project, fpath)
        loaded = load_project_json(fpath)

        saved_dict = saved.model_dump(mode="json")
        loaded_dict = loaded.model_dump(mode="json")

        # Hash'ler zaten eşit, onun dışındaki alanları kontrol et
        assert saved_dict == loaded_dict
