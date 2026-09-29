"""Etek (skirt) basma/burkulma (UG-23(b) B) ve çekme kontrolü testleri.

El hesabı (formülden bağımsız), ORTALAMA çap D_m = 2000 mm, t = 6 mm:
    A = pi*D_m*t      = pi*2000*6      = 37 699.11 mm^2
    Z = pi*D_m^2*t/4  = pi*2000^2*6/4  = 18 849 556 mm^3
    R/t = 1000/6 = 166.7  ->  A_geom = 0.125/(R/t) = 7.5e-4
    (elastik bölgede B ~ A*E/2 ~ 75-76 MPa; B çizelge okumasıdır, kodda YOK)
Yük seçimi: W = 50 MPa * A = 1 884 956 N ; M = 50 MPa * Z = 9.42478e8 N.mm
    => S_comb = W/A + M/Z = 100 MPa.
Eski (hatalı) kontrol: 100 / S(138) = 0.72 (geçer). Doğrusu: 100 / min(138, 76) = 1.32 (FAIL).
"""

import math

import pytest

from domain import MaterialProperty, ProductForm
from supports import formulas
from supports.support_calc import SupportCalculator

D, T = 2000.0, 6.0
A_MM2 = math.pi * D * T           # 37 699.11
Z_MM3 = math.pi * D * D * T / 4.0  # 18 849 556
W = 50.0 * A_MM2                   # 50 MPa basma
M = 50.0 * Z_MM3                   # 50 MPa eğilme


@pytest.fixture
def mat():
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4",
    )


def _run(mat, *, B=None, E=None, weight=W, moment=M, w_min=None, d=D, t=T):
    payload = {
        "support": {
            "tag": "SK-1", "type": "skirt", "diameter_mm": d, "thickness_mm": t,
            "height_mm": 3000.0,
            "skirt_allowable_compressive_MPa": B, "skirt_weld_efficiency": E,
        },
        "total_weight_N": weight,
        "overturning_moment_Nmm": moment,
        "materials": [mat],
        "skirt_material_id": "MAT-01",
    }
    if w_min is not None:
        payload["min_weight_N"] = w_min
    return SupportCalculator().check_skirt(payload)


def test_formulas_match_hand_calc():
    assert formulas.skirt_compression_stress(W, D, T) == pytest.approx(50.0, rel=1e-9)
    assert formulas.skirt_bending_stress(M, D, T) == pytest.approx(50.0, rel=1e-9)
    assert formulas.skirt_geometric_factor_A(D, T) == pytest.approx(7.5e-4, rel=1e-3)
    # çekme: 50 - 0.4*50 = 30
    assert formulas.skirt_tensile_stress(M, 0.4 * W, D, T) == pytest.approx(30.0, rel=1e-9)


def test_missing_B_is_blocked_not_pass(mat):
    r = _run(mat)  # S_comb = 100 < S = 138, B yok
    assert r.status.value == "BLOCKED CODE DATA"
    assert any("UG-23(b)" in w for w in r.warnings)
    assert r.utilization_ratio is None


def test_B_below_stress_now_fails_where_old_check_passed(mat):
    r = _run(mat, B=76.0)
    assert r.status.value == "FAIL"
    assert r.utilization_ratio == pytest.approx(100.0 / 76.0, rel=1e-6)  # ~1.316
    assert r.allowable_limit == pytest.approx(76.0)


def test_B_high_enough_gives_review_required_with_util(mat):
    r = _run(mat, B=120.0)
    assert r.status.value == "REVIEW REQUIRED"
    assert r.utilization_ratio == pytest.approx(100.0 / 120.0, rel=1e-6)


def test_B_capped_by_tensile_allowable(mat):
    # B = 500 > S = 138 -> sınır S
    r = _run(mat, B=500.0)
    assert r.allowable_limit == pytest.approx(138.0)


def test_stress_above_S_fails_even_without_B(mat):
    r = _run(mat, weight=W * 2, moment=M * 2)  # S_comb = 200 > S = 138
    assert r.status.value == "FAIL"


def test_tension_side_uses_weld_efficiency_and_default_assumption(mat):
    # W_min = 0 -> S_t = 50 MPa; E=0.6 -> 82.8 MPa: geçer; E=0.3 -> 41.4: FAIL
    ok = _run(mat, B=200.0, w_min=0.0)
    assert ok.status.value == "REVIEW REQUIRED"
    assert any("E = 0,6 VARSAYILDI" in a for a in ok.assumptions)  # K4
    assert any("ankraj" in w.lower() for w in ok.warnings)         # kaldırma uyarısı
    bad = _run(mat, B=200.0, w_min=0.0, E=0.3)
    assert bad.status.value == "FAIL"
    assert bad.utilization_ratio == pytest.approx(50.0 / (138.0 * 0.3), rel=1e-6)


def test_no_tension_when_weight_dominates(mat):
    r = _run(mat, B=200.0, moment=0.2 * M)  # S_t = 10 - 50 < 0
    assert not any("ankraj" in w.lower() for w in r.warnings)


def test_invalid_weld_efficiency_not_calculated(mat):
    assert _run(mat, B=100.0, E=1.5).status.value == "NOT CALCULATED"


def test_clause_reference_and_mean_diameter_wording(mat):
    r = _run(mat, B=120.0)
    assert "Appendix G" not in r.clause_reference
    assert "UG-23(b)" in r.clause_reference
    names = [iv["name"] if isinstance(iv, dict) else getattr(iv, "name", None)
             for iv in r.intermediate_values]
    assert "P_base" not in names
    assert "D_skirt_mean" in names
