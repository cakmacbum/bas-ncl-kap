"""CAD nozul entegrasyonu testleri (Faz 3 → cad-engine bağlanması).

Nozul adımları (5-10): boru + delik + takviye pedi.
K2: nozul konumu hesap verisinden (nozzles.position) gelir; CAD yalnızca üretir.
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
from cad_engine.vessel_builder import CADQUERY_AVAILABLE, build_vessel, export_step

pytestmark = pytest.mark.skipif(not CADQUERY_AVAILABLE, reason="CadQuery kurulu değil")


def _base_kwargs(nozzles):
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0,
    )
    shell = ShellSection(
        section_id="SHELL-01", inside_diameter=1000, tangent_length=2000,
        nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0,
    )
    hl = Head(head_id="HL", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    hr = Head(head_id="HR", type=HeadType.ELLIPTICAL, inside_diameter=1000,
              nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    return VesselProject(
        project_number="P", project_name="t", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell],
        heads=[hl, hr], nozzles=nozzles, materials=[mat],
    )


@pytest.fixture
def nozzle():
    return Nozzle(
        tag="N1", host_component_id="SHELL-01", axial_position=800,
        circumferential_angle=90, outside_diameter=168.3, inside_diameter=154.1,
        neck_thickness=7.1, material_id="M1", outside_projection=150,
        reinforcement_pad=True, reinforcement_pad_od=300, reinforcement_pad_thickness=10,
    )


def test_nozzle_added_to_model(nozzle):
    """Nozul modele eklenmeli, tek solid kalmalı, hata olmamalı."""
    r = build_vessel(_base_kwargs([nozzle]))
    assert r.success
    assert r.error is None
    assert r.nozzle_count == 1
    assert not r.warnings  # CAD hatası olmamalı
    # Tek solid (nozul gövdeyle birleşik)
    solid_check = next(c for c in r.validation.results if "Solid" in c.message)
    assert solid_check.passed


def test_nozzle_increases_metal_volume(nozzle):
    """Nozul + ped metal hacmini artırır (boru/ped > açılan delik)."""
    r_with = build_vessel(_base_kwargs([nozzle]))
    r_without = build_vessel(_base_kwargs([]))
    assert r_with.outer_volume_mm3 > r_without.outer_volume_mm3


def test_nozzle_bore_actually_cut(nozzle):
    """Delik gerçekten kesilmeli — nozul borusu içi boş (bore hacmi çıkarılmış).

    Delikli nozulun metal katkısı, aynı dış çaplı dolu silindirden belirgin az olmalı.
    """
    r = build_vessel(_base_kwargs([nozzle]))
    r0 = build_vessel(_base_kwargs([]))
    added = r.outer_volume_mm3 - r0.outer_volume_mm3
    # Nozul dış silindiri tümüyle dolu olsaydı hacim çok daha büyük olurdu;
    # bore kesildiği için eklenen hacim makul aralıkta kalır (> 0, çok büyük değil).
    assert added > 0
    # Kaba üst sınır: aynı boyda tam dolu boru hacminden az olmalı
    import math
    od_r = nozzle.outside_diameter / 2.0
    full_pipe = math.pi * od_r ** 2 * (nozzle.outside_projection + 12 + 150)
    assert added < full_pipe


def test_nozzle_step_export(nozzle, tmp_path):
    """Nozullu model STEP'e aktarılabilmeli."""
    r = build_vessel(_base_kwargs([nozzle]))
    out = export_step(r.shape, str(tmp_path / "vessel_nozzle.step"))
    p = tmp_path / "vessel_nozzle.step"
    assert p.exists()
    assert p.stat().st_size > 1000


def test_head_nozzle_is_modeled():
    """Bombe üzerindeki nozul artık CAD'de modellenir (eskiden atlanıyordu)."""
    noz = Nozzle(
        tag="N-HEAD", host_component_id="HL", axial_position=0,
        outside_diameter=100, inside_diameter=90, neck_thickness=5, material_id="M1",
        outside_projection=120,
    )
    r = build_vessel(_base_kwargs([noz]))
    assert r.success
    assert r.nozzle_count == 1
    assert not any("modellenmedi" in w for w in r.warnings)


def test_unknown_host_nozzle_warned():
    """Host'u gövde/bombe listesinde olmayan nozul modellenmez, uyarı verir."""
    noz = Nozzle(
        tag="N-X", host_component_id="YOK-123", axial_position=0,
        outside_diameter=100, inside_diameter=90, neck_thickness=5, material_id="M1",
    )
    r = build_vessel(_base_kwargs([noz]))
    assert r.success
    assert r.nozzle_count == 0
    assert any("YOK-123" in w for w in r.warnings)


def test_head_nozzle_protrudes_beyond_head():
    """Sol bombeye takılan nozul −Z yönünde bombeyi aşmalı (gerçekten dışarı çıkar)."""
    noz = Nozzle(
        tag="N-HEAD", host_component_id="HL", axial_position=0,
        circumferential_angle=0, outside_diameter=100, inside_diameter=90,
        neck_thickness=5, material_id="M1", outside_projection=150,
    )
    r_with = build_vessel(_base_kwargs([noz]))
    r_without = build_vessel(_base_kwargs([]))

    def zmin(res):
        bb = res.shape.val().BoundingBox()
        return bb.zmin

    # Nozul sol bombenin tepesinden (−Z) daha dışarı uzanmalı
    assert zmin(r_with) < zmin(r_without) - 50


def test_inclined_nozzle_differs_from_radial(nozzle):
    """Eğim açısı (α) modele yansımalı — eğik nozul radyalden farklı geometri üretir."""
    radial = build_vessel(_base_kwargs([nozzle]))

    inclined = nozzle.model_copy(update={"inclination_angle": 30.0})
    tilted = build_vessel(_base_kwargs([inclined]))

    assert radial.success and tilted.success
    bb_r = radial.shape.val().BoundingBox()
    bb_t = tilted.shape.val().BoundingBox()
    # θ=90° → nozul +Y yönünde uzanır ve ymax'ı belirler. α=30° ekseni Z'ye
    # eğer: boru ucu Y'de geri çekilir ama flanş diski eğildiği için Y'ye taşar.
    # Yön tek başına anlamlı değil; kritik olan geometrinin gerçekten değişmesi.
    assert abs(bb_t.ymax - bb_r.ymax) > 10.0


def test_manway_and_flanged_differ():
    """Manway ve flanşlı nozul farklı 3D görünüm üretmeli (aynı boru ölçüsünde)."""
    from domain.enums import NozzleType

    base = dict(
        host_component_id="SHELL-01", axial_position=800, circumferential_angle=90,
        outside_diameter=168.3, inside_diameter=154.1, neck_thickness=7.1,
        material_id="M1", outside_projection=150,
    )
    flanged = Nozzle(tag="NF", nozzle_type=NozzleType.FLANGED, **base)
    manway = Nozzle(tag="NM", nozzle_type=NozzleType.MANWAY, **base)

    r_f = build_vessel(_base_kwargs([flanged]))
    r_m = build_vessel(_base_kwargs([manway]))
    assert r_f.success and r_m.success
    # Manway kör kapaklı ve daha büyük flanşlı → metal hacmi belirgin fazla
    assert r_m.outer_volume_mm3 > r_f.outer_volume_mm3
    # Görsel temsil notu üretilmeli (K6 — ölçü B16.5'ten gelmiyor)
    assert any("görsel temsil" in n for n in r_m.notes)


def test_coupling_differs_from_socket_welded():
    """Manşon (coupling) 3D'de soket kaynaklı boss'tan ayırt edilebilir olmalı."""
    from domain.enums import NozzleType

    base = dict(
        host_component_id="SHELL-01", axial_position=800, circumferential_angle=90,
        outside_diameter=48.3, inside_diameter=40.9, neck_thickness=3.7,
        material_id="M1", outside_projection=80,
    )
    socket = Nozzle(tag="NS", nozzle_type=NozzleType.SOCKET_WELDED, **base)
    coupling = Nozzle(tag="NC", nozzle_type=NozzleType.COUPLING, **base)

    r_s = build_vessel(_base_kwargs([socket]))
    r_c = build_vessel(_base_kwargs([coupling]))
    assert r_s.success and r_c.success
    assert r_s.nozzle_count == 1 and r_c.nozzle_count == 1
    # Manşon daha uzun/kalın bilezik → metal hacmi belirgin fazla
    assert r_c.outer_volume_mm3 > r_s.outer_volume_mm3


def test_head_nozzle_positioned_by_diameter():
    """Bombe nozulu 'yerleşim çapı' ile konumlanır — merkezden o yarıçapta durur."""
    noz = Nozzle(
        tag="N-HD", host_component_id="HL", axial_position=0,
        circumferential_angle=0, head_position_diameter=600.0,
        outside_diameter=100, inside_diameter=90, neck_thickness=5,
        material_id="M1", outside_projection=150,
    )
    r = build_vessel(_base_kwargs([noz]))
    assert r.success
    assert r.nozzle_count == 1

    # Aynı nozul çapsız (tepeye oturur) → farklı yerde durmalı.
    apex = noz.model_copy(update={"head_position_diameter": None})
    r_apex = build_vessel(_base_kwargs([apex]))
    bb, bb_apex = r.shape.val().BoundingBox(), r_apex.shape.val().BoundingBox()
    # Tepedeki nozul −Z'ye daha çok taşar; 300 mm yarıçaptaki nozul yana kayar.
    # (Kesin konum `tests/faz3` içindeki position testinde doğrulanır — K2: burada
    #  mesh'ten ölçüp hesaba beslemiyoruz, yalnızca geometrinin farkını kanıtlıyoruz.)
    assert bb.zmin > bb_apex.zmin + 20


def test_head_nozzle_diameter_out_of_bounds_warns():
    """Bombe sınırını aşan yerleşim çapı sessizce kırpılmaz, uyarı verir (K4)."""
    noz = Nozzle(
        tag="N-OOB", host_component_id="HL", axial_position=0,
        head_position_diameter=9000.0,
        outside_diameter=100, inside_diameter=90, neck_thickness=5,
        material_id="M1", outside_projection=150,
    )
    r = build_vessel(_base_kwargs([noz]))
    assert r.success
    assert r.nozzle_count == 0
    assert any("yerleşim çapı" in w for w in r.warnings)
