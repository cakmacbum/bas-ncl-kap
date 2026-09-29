"""Flanş Y/f/F/V/T/U üretim yolu: VesselProject → orkestratör → sonuç (K4/K6).

Y, f, F, V, T, U lisanslı Appendix 2 çizelge/eğrilerinden kullanıcı girdisidir; koda gömülmez.
Hub büyük uç kalınlığı g1 (hub_large_thickness) de kullanıcı girdisidir (varsayılan yok).
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from calc_core.orchestrator import CalculationOrchestrator
from code_asme_viii_1 import ASMEVIII1DesignCode
from domain import Flange, VesselProject
from domain.enums import CalculationStatus

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "vessel_project_five_component.json"


def _flange(**over):
    base = dict(flange_id="FL-1", type="integral", inside_diameter=500.0,
                outside_diameter=700.0, thickness=50.0, hub_small_thickness=20.0,
                hub_length=50.0, material_id="M1")
    base.update(over)
    return Flange(**base)


FULL = dict(hub_large_thickness=25.0, flange_factor_Y=9.0, flange_factor_f=1.0,
            flange_factor_F=0.9, flange_factor_V=0.4, flange_factor_T=1.8,
            flange_factor_U=7.0)


def _run(flange):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["flanges"] = [flange.model_dump()]
    project = VesselProject(**data)
    res = CalculationOrchestrator(ASMEVIII1DesignCode()).run(project)
    return [r for r in res.results if r.calculation_type == "flange_stress"], res


def test_domain_factor_defaults_none_and_gt_zero():
    fl = _flange()
    fields = ("flange_factor_Y", "flange_factor_f", "flange_factor_F", "flange_factor_V",
              "flange_factor_T", "flange_factor_U", "hub_large_thickness")
    assert all(getattr(fl, k) is None for k in fields)
    for field in fields:
        with pytest.raises(ValidationError):
            _flange(**{field: 0})
        with pytest.raises(ValidationError):
            _flange(**{field: -1.0})


def test_production_without_y_f_is_blocked():
    rows, res = _run(_flange())
    assert len(rows) == 1 and not res.errors
    assert rows[0].status == CalculationStatus.BLOCKED_MISSING_INPUT


@pytest.mark.parametrize("y,f", [(9.0, None), (None, 1.0)])
def test_production_with_only_one_factor_is_blocked(y, f):
    rows, _ = _run(_flange(flange_factor_Y=y, flange_factor_f=f))
    assert rows[0].status == CalculationStatus.BLOCKED_MISSING_INPUT


@pytest.mark.parametrize("missing", ["flange_factor_Y", "flange_factor_f", "flange_factor_F",
                                     "flange_factor_V", "flange_factor_T", "flange_factor_U",
                                     "hub_large_thickness"])
def test_production_each_missing_factor_blocks_and_names_it(missing):
    """Üretim yolunda her faktör/g1 eksikliği BLOCKED_MISSING_INPUT; mesaj eksik olanı adıyla söyler."""
    kw = dict(FULL, bolt_load_W_N=3e5, moment_M_Nmm=5e6)
    kw.pop(missing)
    rows, _ = _run(_flange(**kw))
    assert rows[0].status == CalculationStatus.BLOCKED_MISSING_INPUT
    label = "g1" if missing == "hub_large_thickness" else missing.split("_")[-1]
    assert any(label in w for w in rows[0].warnings)


def test_production_loose_flange_is_out_of_scope():
    rows, res = _run(_flange(type="loose", bolt_load_W_N=3e5, moment_M_Nmm=5e6, **FULL))
    assert not res.errors
    assert rows[0].status == CalculationStatus.OUT_OF_SCOPE


def test_production_with_y_f_never_silently_passes_without_moment():
    """Y/f girilse bile M/W yoksa M=0 ile sahte PASS üretilmez."""
    rows, _ = _run(_flange(**FULL))
    assert rows[0].status != CalculationStatus.PASS
    assert rows[0].status == CalculationStatus.BLOCKED_MISSING_INPUT


def test_domain_w_m_default_none_and_gt_zero():
    fl = _flange()
    assert fl.bolt_load_W_N is None and fl.moment_M_Nmm is None
    for field in ("bolt_load_W_N", "moment_M_Nmm"):
        for bad in (0, -1.0):
            with pytest.raises(ValidationError):
                _flange(**{field: bad})


@pytest.mark.parametrize("w,m", [(3e5, None), (None, 5e6)])
def test_production_with_only_one_of_w_m_is_blocked(w, m):
    rows, _ = _run(_flange(bolt_load_W_N=w, moment_M_Nmm=m, **FULL))
    assert rows[0].status == CalculationStatus.BLOCKED_MISSING_INPUT


def test_production_with_y_f_w_m_runs_and_is_review_required_not_pass():
    rows, res = _run(_flange(bolt_load_W_N=3e5, moment_M_Nmm=5e5, **FULL))
    assert len(rows) == 1 and not res.errors
    r = rows[0]
    assert r.status == CalculationStatus.REVIEW_REQUIRED
    assert r.input_snapshot["moment_M_Nmm"] == 5e5
    assert r.input_snapshot["bolt_load_W_N"] == 3e5
    assert any("W ve M kullanıcı girdisidir" in w for w in r.warnings)
    names = {i["name"] for i in r.intermediate_values}
    assert {"S_H", "S_R", "S_T", "(S_H+S_R)/2", "(S_H+S_T)/2", "Z", "L"} <= names


def test_production_high_moment_still_fails():
    rows, _ = _run(_flange(bolt_load_W_N=5e5, moment_M_Nmm=1e9, **FULL))
    assert rows[0].status == CalculationStatus.FAIL


def test_design_code_passes_y_f_from_domain_and_computes_with_explicit_moment():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    project = VesselProject(**data)
    fl = _flange(**FULL)
    r = ASMEVIII1DesignCode().calculate_flange({
        "flange": fl, "design_conditions": project.design_conditions,
        "materials": project.materials,
        "flange_factor_Y": fl.flange_factor_Y, "flange_factor_f": fl.flange_factor_f,
        "bolt_load_W": 300000.0, "moment_M": 5_000_000.0,
    })
    assert r.status in (CalculationStatus.REVIEW_REQUIRED, CalculationStatus.FAIL)
    assert r.input_snapshot["Y_factor"] == 9.0
    assert r.input_snapshot["F_factor"] == 0.9 and r.input_snapshot["g1_mm"] == 25.0


def test_production_full_path_matches_hand_calc():
    """VesselProject → orkestratör: B=500, A=700, t=50, g0=20, g1=25, M=5e6, Y=9, f=1,
    F=0.9, V=0.4, T=1.8, U=7 (bkz. test_faz5_flanges el hesabı yöntemi).
      Z=3.083333 ; h0=100 ; e=0.009 ; d=700000 ; L=(50·0.009+1)/1.8 + 125000/700000
        = 0.805556 + 0.178571 = 0.984127
      S_H = 1·5e6/(0.984127·625·500) = 16.2581
      S_R = (1.33·50·0.009+1)·5e6/(0.984127·2500·500) = 1.5985·5e6/1230158.7 = 6.49685
      S_T = 9·5e6/(2500·500) − 3.083333·6.49685 = 36 − 20.0320 = 15.9680
    """
    rows, _ = _run(_flange(bolt_load_W_N=3e5, moment_M_Nmm=5e6, **FULL))
    r = rows[0]
    iv = {i["name"]: i["value"] for i in r.intermediate_values}
    assert iv["L"] == pytest.approx(0.984127, rel=1e-5)
    assert iv["S_H"] == pytest.approx(16.2581, rel=1e-4)
    assert iv["S_R"] == pytest.approx(6.49685, rel=1e-4)
    assert iv["S_T"] == pytest.approx(15.9680, rel=1e-4)
    assert r.status == CalculationStatus.REVIEW_REQUIRED


# ---- Formülden bağımsız el hesabı (Appendix 2-7 standart form) --------------------
# Eskiden strict xfail'di (kod S_H/S_T'yi standart formdan farklı hesaplıyordu);
# formüller standart forma getirildi, testler artık geçer.
# Girdi: M=5e6, B=500, t=50, g1=25, Y=9, f=1, K=A/B=1.4, L=1 (el hesabı sadeleştirmesi).

M_, B_, T_, G1_, Y_, F_ = 5e6, 500.0, 50.0, 25.0, 9.0, 1.0


def test_hand_calc_y_term_of_tangential_stress_matches():
    """Y·M/(t²·B) = 9·5e6/(2500·500) = 36.0 MPa (el hesabı)."""
    assert 9.0 * 5e6 / (2500.0 * 500.0) == pytest.approx(36.0)


def test_hand_calc_hub_longitudinal_stress():
    from flanges import formulas
    hand = F_ * M_ / (1.0 * G1_ ** 2 * B_)          # = 16.0 MPa (L=1)
    assert hand == pytest.approx(16.0)
    assert formulas.hub_longitudinal_stress(M_, F_, 1.0, G1_, B_) == pytest.approx(hand, rel=1e-6)


def test_hand_calc_tangential_stress_with_z_term():
    from flanges import formulas
    z = (1.4 ** 2 + 1) / (1.4 ** 2 - 1)             # 3.0833
    s_r = 16.0                                       # S_R girdi olarak (el hesabı)
    hand = 36.0 - z * s_r                            # = -13.33 MPa
    assert formulas.tangential_flange_stress(M_, Y_, T_, B_, z, s_r) == pytest.approx(hand, rel=1e-6)
