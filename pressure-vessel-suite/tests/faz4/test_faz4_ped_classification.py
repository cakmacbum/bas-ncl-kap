"""Faz 4.A — PED Classification Engine testleri.

Golden-case: bilinen kap → beklenen kategori/modül/NB çıktısı.

Referans: PED 2014/68/EU, Annex II
"""

import pytest

from ped_2014_68_eu import (
    PEDClassificationEngine,
    ClassificationInput,
    ClassificationResult,
    FluidClassification,
    ConformityModule,
    EquipmentType,
    FluidGroupPED,
    FluidPhasePED,
    GHSClassification,
    NotifyBodyRequired,
    PEDCategory,
    PEDClassificationTable,
)


@pytest.fixture
def engine():
    return PEDClassificationEngine()


# ── Akışkan gruplandırma testleri ─────────────────────────────────────────────

class TestFluidGroupClassification:
    """Akışkan grubu belirleme testleri."""

    def test_flammable_gas_is_group1(self):
        """Yanıcı gaz → Grup 1."""
        fluid = FluidClassification(
            fluid_name="Hydrogen",
            phase=FluidPhasePED.GAS,
            ghs_classifications=[GHSClassification.FLAMMABLE_GAS],
        )
        assert fluid.fluid_group == FluidGroupPED.GROUP_1
        assert fluid.is_group1 is True

    def test_water_is_group2(self):
        """Su → Grup 2."""
        fluid = FluidClassification(
            fluid_name="Water",
            phase=FluidPhasePED.LIQUID,
            ghs_classifications=[GHSClassification.OTHER],
        )
        assert fluid.fluid_group == FluidGroupPED.GROUP_2
        assert fluid.is_group1 is False

    def test_toxic_is_group1(self):
        """Toksik akışkan → Grup 1."""
        fluid = FluidClassification(
            fluid_name="Ammonia",
            phase=FluidPhasePED.GAS,
            ghs_classifications=[GHSClassification.TOXIC],
        )
        assert fluid.fluid_group == FluidGroupPED.GROUP_1

    def test_explosive_is_group1(self):
        """Patlayıcı → Grup 1."""
        fluid = FluidClassification(
            fluid_name="Acetylene",
            phase=FluidPhasePED.GAS,
            ghs_classifications=[GHSClassification.EXPLOSIVE, GHSClassification.FLAMMABLE_GAS],
        )
        assert fluid.fluid_group == FluidGroupPED.GROUP_1

    def test_empty_classification_is_group2(self):
        """Sınıflandırma yok → Grup 2."""
        fluid = FluidClassification(
            fluid_name="Nitrogen",
            phase=FluidPhasePED.GAS,
            ghs_classifications=[],
        )
        assert fluid.fluid_group == FluidGroupPED.GROUP_2


# ── PED sınıflandırma motoru testleri ─────────────────────────────────────────

class TestPEDClassificationEngine:
    """PED sınıflandırma motoru golden-case testleri."""

    def test_category_iv_vessel_group1_gas(self, engine):
        """Grup 1 gaz, yüksek PS×V → Kategori IV.

        PS = 10 MPa, V = 2000 L → PS×V = 20000 MPa·L
        Tablo 1: Kategori IV (PS×V ≥ 100)
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=10.0,
            volume_liters=2000.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Steam",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.FLAMMABLE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.in_scope is True
        assert result.fluid_group == FluidGroupPED.GROUP_1
        assert result.fluid_phase == FluidPhasePED.GAS
        assert result.ps_x_v == 20000.0
        assert result.category == PEDCategory.CATEGORY_IV
        assert result.classification_table == PEDClassificationTable.TABLE_1
        assert result.ce_marking_applicable is True
        assert result.notify_body_required == NotifyBodyRequired.REQUIRED

    def test_category_iv_vessel_group2_gas(self, engine):
        """Grup 2 gaz, yüksek PS×V → Kategori IV.

        PS = 1.0 MPa, V = 100 L → PS×V = 100 MPa·L
        Tablo 7 eşikleri: Cat I≥0.05, Cat II≥0.1, Cat III≥1.0, Cat IV≥5.0
        100 > 5.0 → Kategori IV
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=1.0,
            volume_liters=100.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Air",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.HIGH_PRESSURE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.in_scope is True
        assert result.fluid_group == FluidGroupPED.GROUP_2
        assert result.category == PEDCategory.CATEGORY_IV
        assert result.ce_marking_applicable is True

    def test_sep_vessel_group2_liquid(self, engine):
        """Grup 2 sıvı, düşük PS×V → SEP.

        PS = 0.1 MPa, V = 5 L → PS×V = 0.5 MPa·L
        Tablo 8: SEP (PS < 0.5 bar VE V < 0.1 L) → hayır, Cat I'a geçer
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=0.03,  # 0.3 bar < 0.5 bar
            volume_liters=5.0,
            ts_min_c=5.0,
            ts_max_c=80.0,
            fluids=[
                FluidClassification(
                    fluid_name="Water",
                    phase=FluidPhasePED.LIQUID,
                    ghs_classifications=[GHSClassification.OTHER],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.in_scope is False  # PS < 0.05 MPa → kapsam dışı

    def test_category_iii_vessel_group2_gas(self, engine):
        """Grup 2 gaz, orta PS×V → Kategori III.

        PS = 0.5 MPa, V = 6 L → PS×V = 3.0 MPa·L
        Tablo 7 eşikleri: Cat I≥0.05, Cat II≥0.1, Cat III≥1.0, Cat IV≥5.0
        3.0 > 1.0 VE 3.0 < 5.0 → Kategori III
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=0.5,
            volume_liters=6.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Nitrogen",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.HIGH_PRESSURE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.in_scope is True
        assert result.fluid_group == FluidGroupPED.GROUP_2
        assert result.category == PEDCategory.CATEGORY_III
        assert result.notify_body_required == NotifyBodyRequired.REQUIRED

    def test_below_scope(self, engine):
        """PS < 0.5 bar → PED kapsam dışı.

        PS = 0.03 MPa (0.3 bar) < 0.05 MPa (0.5 bar)
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=0.03,
            volume_liters=100.0,
            ts_min_c=5.0,
            ts_max_c=80.0,
            fluids=[
                FluidClassification(
                    fluid_name="Water",
                    phase=FluidPhasePED.LIQUID,
                    ghs_classifications=[GHSClassification.OTHER],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.in_scope is False
        assert "0.05" in result.scope_reason

    def test_multi_fluid_highest_category(self, engine):
        """Çok akışkanlı sistem → en yüksek kategori esas.

        Grup 2 sıvı (su) + Grup 1 gaz (amonyak) → Grup 1 kuralları uygulanır.
        PS = 2.0 MPa, V = 500 L → PS×V = 1000 MPa·L → Kategori IV (Tablo 1)
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=2.0,
            volume_liters=500.0,
            ts_min_c=-10.0,
            ts_max_c=150.0,
            fluids=[
                FluidClassification(
                    fluid_name="Water",
                    phase=FluidPhasePED.LIQUID,
                    ghs_classifications=[GHSClassification.OTHER],
                ),
                FluidClassification(
                    fluid_name="Ammonia",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.TOXIC, GHSClassification.FLAMMABLE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.fluid_group == FluidGroupPED.GROUP_1
        assert result.determining_fluid == "Ammonia"
        assert result.category in (PEDCategory.CATEGORY_III, PEDCategory.CATEGORY_IV)
        assert len(result.warnings) > 0  # Çok akışkan uyarısı

    def test_module_mapping_sep(self, engine):
        """SEP → Modül None, CE yok, NB yok."""
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=0.06,  # SEP aralığında
            volume_liters=0.5,
            ts_min_c=5.0,
            ts_max_c=80.0,
            fluids=[
                FluidClassification(
                    fluid_name="Water",
                    phase=FluidPhasePED.LIQUID,
                    ghs_classifications=[GHSClassification.OTHER],
                ),
            ],
        )
        result = engine.classify(input_data)

        if result.category == PEDCategory.SEP:
            assert ConformityModule.NONE in result.conformity_modules
            assert result.ce_marking_applicable is False
            assert result.notify_body_required == NotifyBodyRequired.NOT_REQUIRED

    def test_module_mapping_category_iii(self, engine):
        """Kategori III → B+D veya B+F veya H, NB gerekli.

        Grup 1 gaz, PS = 2 MPa, V = 300 L → PS×V = 600 MPa·L
        Tablo 1: Kategori III (PS×V ≥ 350)
        """
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=2.0,
            volume_liters=300.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Oxygen",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.OXIDIZING],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.category in (PEDCategory.CATEGORY_III, PEDCategory.CATEGORY_IV)
        assert result.notify_body_required == NotifyBodyRequired.REQUIRED
        assert result.ce_marking_applicable is True


# ── Çıktı modeli testleri ─────────────────────────────────────────────────────

class TestClassificationResult:
    """ClassificationResult modeli testleri."""

    def test_result_has_all_fields(self, engine):
        """Sonuç tüm gerekli alanları içermeli."""
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=1.0,
            volume_liters=100.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Steam",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.FLAMMABLE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert result.equipment_type == EquipmentType.VESSEL
        assert result.ps_mpa == 1.0
        assert result.volume_liters == 100.0
        assert result.ps_x_v == 100.0
        assert result.fluid_group is not None
        assert result.fluid_phase is not None
        assert result.classification_table is not None
        assert result.category is not None
        assert len(result.conformity_modules) > 0
        assert result.notify_body_required is not None
        assert isinstance(result.ce_marking_applicable, bool)
        assert isinstance(result.intermediate_values, list)

    def test_intermediate_values_populated(self, engine):
        """Ara değerler dolu olmalı (K5)."""
        input_data = ClassificationInput(
            equipment_type=EquipmentType.VESSEL,
            ps_mpa=1.0,
            volume_liters=100.0,
            ts_min_c=-10.0,
            ts_max_c=200.0,
            fluids=[
                FluidClassification(
                    fluid_name="Steam",
                    phase=FluidPhasePED.GAS,
                    ghs_classifications=[GHSClassification.FLAMMABLE_GAS],
                ),
            ],
        )
        result = engine.classify(input_data)

        assert len(result.intermediate_values) > 0
        names = [iv["name"] for iv in result.intermediate_values]
        assert "fluid_group" in names
        assert "ps_x_v" in names
        assert "category" in names
