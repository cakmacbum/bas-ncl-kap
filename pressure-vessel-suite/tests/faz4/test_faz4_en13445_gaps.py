"""E01 — EN 13445 sessiz boşluklar: ASME'de hesaplanan her kontrol EN raporunda açık satırdır.

Boş liste = "sorun yok" gibi okunabileceği için EN'de hesaplanmayan her kontrol
NOT_CALCULATED / OUT_OF_SCOPE + nedenle görünmelidir (ASME'ye fallback yok).
"""

import pytest

from calc_core.orchestrator import CalculationOrchestrator
from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from code_en_13445 import EN13445DesignCode
from domain import (
    CalculationCode, Cone, DesignConditions, Head, HeadType, MaterialProperty, Nozzle,
    NozzleType, ProductForm, ShellSection, Support, VesselProject, WeldJoint,
)
from domain.enums import CalculationStatus
from domain.geometry import Junction
from domain.lifting_lug import LiftingLugSpec

GAP_STATUSES = {CalculationStatus.NOT_CALCULATED, CalculationStatus.OUT_OF_SCOPE}

LUG = dict(
    lug_count=2, location="shell_top", plate_thickness_mm=20, plate_width_mm=150,
    hole_diameter_mm=50, edge_distance_mm=75, hole_height_mm=100, base_width_mm=150,
    weld_length_mm=400, weld_leg_mm=10, lift_angle_deg=0, impact_factor=2.0,
    yield_strength_MPa=250,
)


def _project(code=CalculationCode.EN_13445, full=True):
    kw = {}
    if full:
        kw = dict(
            cones=[Cone(cone_id="CONE-1", large_diameter=1000.0, small_diameter=500.0,
                        half_apex_angle=30.0, length=400.0, nominal_thickness=12.0,
                        material_id="M")],
            junctions=[Junction(junction_id="J-1", left_component_id="S",
                                right_component_id="CONE-1", junction_type="cone_to_shell",
                                cone_end="large")],
            nozzles=[Nozzle(tag="N1", nozzle_type=NozzleType.FLANGED, host_component_id="S",
                            axial_position=500.0, outside_diameter=168.3, inside_diameter=154.1,
                            neck_thickness=7.1, material_id="M")],
            supports=[Support(support_id="SAD-1", type="saddle", location_mm=500.0,
                              width_mm=200.0, height_mm=300.0, material_id="M")],
            lifting_lugs=LiftingLugSpec(**LUG),
        )
    return VesselProject(
        project_number="E01", project_name="gaps", calculation_code=code, code_edition="2021",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
            operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0),
        heads=[Head(head_id="H", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
        shell_sections=[ShellSection(section_id="S", inside_diameter=1000.0, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="M", weld_joint_id="WJ")],
        welds=[WeldJoint(joint_id="WJ", joint_type="longitudinal", weld_category="A",
                         full_penetration=True)],
        materials=[MaterialProperty(
            material_id="M", standard_pack="EN 10028-3", material_designation="P355NH",
            product_form=ProductForm.PLATE, temperature=20.0, allowable_stress=163.0,
            yield_strength=295.0, tensile_strength=490.0, source_reference="t")],
        **kw,
    )


@pytest.fixture(scope="module")
def en_result():
    return CalculationOrchestrator(EN13445DesignCode(edition="2021")).run(_project())


def _rows(res, calc_type):
    return [r for r in res.results if r.calculation_type == calc_type]


# (calculation_type, beklenen component_id veya None)
EXPECTED = [
    ("mdmt_check", "S"), ("mdmt_check", "H"), ("mdmt_check", "CONE-1"),
    ("saddle_stress", "SAD-1"),
    ("weld_validation", "WJ"),
    ("clash_check", "N1"),
    ("inspection_opening", None),
    ("lug_tension", "LUG"), ("lug_shell_local_shear", "LUG"),
    ("pneumatic_test", None),
]
# E02: koni kalınlığı, koni MAWP ve koni-silindir birleşimi artık gerçek hesap satırıdır
# (verified=False -> olumlu sonuç REVIEW_REQUIRED); ayrıntılı el hesabı test_faz4_en13445_cone_flat.py.


@pytest.mark.parametrize("calc_type,cid", EXPECTED)
def test_gap_is_explicit_row(en_result, calc_type, cid):
    rows = [r for r in _rows(en_result, calc_type) if cid is None or r.component_id == cid]
    assert rows, f"{calc_type}/{cid}: raporda satır yok (sessiz boşluk)"
    for r in rows:
        assert r.status in GAP_STATUSES
        assert "13445" in r.code
        assert r.clause_reference and r.clause_reference.startswith("EN 13445")
        assert "ASME" not in r.clause_reference


def test_lifting_lug_is_out_of_scope(en_result):
    assert all(r.status == CalculationStatus.OUT_OF_SCOPE for r in _rows(en_result, "lug_weld"))


def test_no_orchestrator_errors_for_cone(en_result):
    # Önceden EN'de calculate_cone_thickness yoktu -> hata satırı, sonuç satırı değil.
    assert not [e for e in en_result.errors if "Cone" in e]


def test_asme_headings_covered_by_en():
    """ASME'nin ürettiği her kontrol başlığı (calculation_type) EN'de de satırdır."""
    asme = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025")).run(_project(CalculationCode.ASME_VIII_1))
    en = CalculationOrchestrator(EN13445DesignCode(edition="2021")).run(_project())
    asme_types = {r.calculation_type for r in asme.results}
    en_types = {r.calculation_type for r in en.results}
    missing = {t for t in asme_types - en_types if not t.startswith(("pressure_relief", "global"))}
    assert not missing, f"ASME'de olup EN raporunda olmayan başlıklar: {missing}"


def test_empty_project_collections_produce_no_phantom_rows():
    res = CalculationOrchestrator(EN13445DesignCode(edition="2021")).run(_project(full=False))
    assert not _rows(res, "saddle_stress") and not _rows(res, "lug_weld")
    assert _rows(res, "mdmt_check") and _rows(res, "pneumatic_test")


@pytest.mark.parametrize("calc_type,cid,clause,expected", [
    ("thickness", "CONE-1", "EN 13445-3, 7.6.4", 4.266134994 / 0.90),
    ("mawp", "CONE-1", "EN 13445-3, 7.6.4", 3.353045509),
    ("junction_check", "J-1", "EN 13445-3, 7.6.6", 4.578728842),
])
def test_cone_rows_are_calculated_and_capped(en_result, calc_type, cid, clause, expected):
    rows = [r for r in _rows(en_result, calc_type) if r.component_id == cid]
    assert len(rows) == 1
    r = rows[0]
    assert r.status == CalculationStatus.REVIEW_REQUIRED  # PASS değil: verified=False
    assert r.clause_reference == clause
    assert r.final_result == pytest.approx(expected, rel=1e-6)
    assert not [e for e in en_result.errors if "Cone" in e or "MAWP" in e or "Junction" in e]
