"""G01 — UI bloklayıcı geometri kurallarının Python karşılığı (hesap öncesi kapı)."""
from calc_core.orchestrator import CalculationOrchestrator
from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import VesselProject
from domain.geometry_checks import geometry_blockers
from tools.campaign.bases import vertical_leg_tank


def _codes(d):
    return {i.code for i in geometry_blockers(VesselProject.model_validate(d))}


def test_gecerli_taban_temiz():
    assert _codes(vertical_leg_tank()) == set()


def test_bombe_govde_cap_uyusmazligi():
    p = vertical_leg_tank()
    p["heads"][1]["inside_diameter"] = 800
    assert "DIAMETER_MISMATCH" in _codes(p)
    p["heads"][1]["inside_diameter"] = 1000.9  # tolerans: |dr| <= 0.5 mm
    assert "DIAMETER_MISMATCH" not in _codes(p)


def test_ayak_cok_kisa():
    p = vertical_leg_tank()
    p["supports"][0]["height_mm"] = 600
    assert "LEG_TOO_SHORT" in _codes(p)


def test_gecersiz_geometri_hesaba_girmez():
    p = vertical_leg_tank()
    p["heads"][1]["inside_diameter"] = 800
    res = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025")).run(VesselProject.model_validate(p))
    assert not res.results
    assert any("GEOMETRY_INVALID" in e and "DIAMETER_MISMATCH" in e for e in res.errors)
