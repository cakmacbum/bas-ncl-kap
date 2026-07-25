"""Materials — birim testleri."""

import pytest

from domain import MaterialProperty, ProductForm
from materials import MaterialProvider, linear_interpolate, interpolate_material_property


# ── Interpolasyon ─────────────────────────────────────────────────────────────

class TestLinearInterpolate:
    """Lineer interpolasyon testleri."""

    def test_exact_match(self):
        assert linear_interpolate(100.0, [0, 100, 200], [10, 20, 30]) == 20.0

    def test_between_points(self):
        result = linear_interpolate(50.0, [0, 100, 200], [10, 20, 30])
        assert abs(result - 15.0) < 1e-10

    def test_extrapolation_below_clamped(self):
        """Ekstrapolasyon yoksa en düşük değer kullanılır."""
        result = linear_interpolate(-50.0, [0, 100, 200], [10, 20, 30])
        assert result == 10.0

    def test_extrapolation_above_clamped(self):
        """Ekstrapolasyon yoksa en yüksek değer kullanılır."""
        result = linear_interpolate(300.0, [0, 100, 200], [10, 20, 30])
        assert result == 30.0

    def test_extrapolation_allowed(self):
        result = linear_interpolate(300.0, [0, 100, 200], [10, 20, 30], allow_extrapolation=True)
        assert abs(result - 40.0) < 1e-10

    def test_empty_data(self):
        with pytest.raises(ValueError):
            linear_interpolate(50.0, [], [])

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError):
            linear_interpolate(50.0, [0, 100], [10])


class TestInterpolateMaterialProperty:
    """Malzeme özelliği interpolasyon testleri."""

    def test_typical_carbon_steel(self):
        """SA-516 Gr.70 tipik sıcaklık-serisi verisi."""
        data = [
            (20.0, 138.0),
            (100.0, 138.0),
            (150.0, 138.0),
            (200.0, 138.0),
            (250.0, 135.0),
            (300.0, 130.0),
        ]
        result = interpolate_material_property(175.0, data)
        assert abs(result - 138.0) < 1.0

    def test_empty_data_raises(self):
        with pytest.raises(ValueError):
            interpolate_material_property(100.0, [])


# ── MaterialProvider ──────────────────────────────────────────────────────────

class TestMaterialProvider:
    """MaterialProvider testleri."""

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

    def test_add_and_get(self):
        provider = MaterialProvider()
        mat = self._make_material()
        provider.add_material(mat)
        assert provider.get("MAT-01") is not None
        assert provider.get("MAT-01").allowable_stress == 138.0

    def test_get_not_found(self):
        provider = MaterialProvider()
        assert provider.get("NONEXISTENT") is None

    def test_get_required_not_found(self):
        provider = MaterialProvider()
        with pytest.raises(ValueError):
            provider.get_required("NONEXISTENT")

    def test_list_materials(self):
        provider = MaterialProvider()
        provider.add_material(self._make_material(material_id="MAT-01"))
        provider.add_material(self._make_material(material_id="MAT-02"))
        assert len(provider.list_materials()) == 2

    def test_remove(self):
        provider = MaterialProvider()
        provider.add_material(self._make_material())
        assert provider.remove("MAT-01") is True
        assert provider.get("MAT-01") is None

    def test_remove_not_found(self):
        provider = MaterialProvider()
        assert provider.remove("NONEXISTENT") is False

    def test_count(self):
        provider = MaterialProvider()
        assert provider.count == 0
        provider.add_material(self._make_material())
        assert provider.count == 1

    def test_clear(self):
        provider = MaterialProvider()
        provider.add_material(self._make_material())
        provider.clear()
        assert provider.count == 0

    def test_overwrite_material(self):
        """Aynı ID ile eklenen malzeme güncellenir."""
        provider = MaterialProvider()
        provider.add_material(self._make_material(allowable_stress=138.0))
        provider.add_material(self._make_material(allowable_stress=150.0))
        assert provider.get("MAT-01").allowable_stress == 150.0

    def test_validate_against_project(self):
        provider = MaterialProvider()
        provider.add_material(self._make_material(material_id="MAT-01"))
        project_mats = [
            self._make_material(material_id="MAT-01"),
            self._make_material(material_id="MAT-02"),
        ]
        missing = provider.validate_against_project(project_mats)
        assert "MAT-02" in missing
        assert "MAT-01" not in missing
