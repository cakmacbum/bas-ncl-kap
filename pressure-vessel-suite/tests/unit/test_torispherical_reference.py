"""V1 referans B (tools/verification/torispherical_shell.py) — yalnız iç tutarlılık."""
import numpy as np
import pytest

from tools.verification.torispherical_shell import solve_torispherical

NU = 0.3


@pytest.fixture(scope="module")
def tori06():
    return solve_torispherical(1000, 10, 1000, 60, l_cyl=1500)


def test_converges(tori06):
    assert tori06.success


def test_cylinder_far_field_membrane(tori06):
    # simetri düzlemi (hamuttan ~1500 mm): σθ = P·Rm/t, σz = P·Rm/2t, eğilme yok
    Rm, t = 505.0, 10.0
    assert tori06.N_t[-1] / t == pytest.approx(Rm / t, rel=1e-4)
    assert tori06.N_s[-1] / t == pytest.approx(Rm / (2 * t), rel=1e-4)
    assert abs(tori06.M_s[-1]) < 1e-3


def test_crown_far_field_membrane():
    # D/t=1000 (sönüm boyu kısa): taç ortası küre membranı P·Lm/2t. (D/t=100'de hamut kuyruğu tacın
    # ortasına kadar %5–10 sapma yapar — gerçek kabuk davranışı, bu yüzden ince örnek.)
    res = solve_torispherical(1000, 1, 1000, 60, phi0_deg=2.0)
    Lm, t = 1000.5, 1.0
    crown = res.segment == 0
    j = int(np.argmin(np.abs(res.r - 150) + (~crown) * 1e9))
    assert res.N_s[j] / t == pytest.approx(Lm / (2 * t), rel=1e-4)
    assert res.N_t[j] / t == pytest.approx(Lm / (2 * t), rel=1e-4)


def test_hemisphere_cylinder_geckeler_shear():
    # L = Di/2 → hamut boyu 0, yarımküre–silindir: Q0 = p/(8β), M0 ≈ 0 (Timoshenko, eşit kalınlık)
    res = solve_torispherical(1000, 10, 500, 60, l_cyl=1500)
    Rm, t = 505.0, 10.0
    beta = (3 * (1 - NU**2) / (Rm * t) ** 2) ** 0.25
    i = np.where(res.segment == 2)[0][0]
    assert abs(res.Q[i]) == pytest.approx(1 / (8 * beta), rel=0.01)
    assert abs(res.M_s[i]) < 0.05 * (1 / (8 * beta)) / beta


def test_boundary_and_tolerance_insensitive(tori06):
    a = solve_torispherical(1000, 10, 1000, 60, l_cyl=3000, phi0_deg=2.0, tol=1e-8).max_vm()
    assert a == pytest.approx(tori06.max_vm(), rel=1e-3)


def test_knuckle_peak_inner_meridional_tension(tori06):
    # tepe hamutta, iç yüzeyde meridyen çekme (hamut düzleşir)
    v = tori06.vm_surface()
    i = int(np.argmax(v))
    assert tori06.segment[i] == 1
    s_in, _, s_out, _ = tori06.surface()
    assert s_in[i] > 0 > s_out[i]


def test_trends_reasonable():
    # rk büyüdükçe tepe azalır; kalınlaştıkça (t/D 0,01→0,02) tepe/membran oranı düşer, hepsi membran teorisinin altında
    peaks = [solve_torispherical(1000, 10, 1000, rk).max_vm(1) for rk in (60, 100, 170)]
    assert peaks[0] > peaks[1] > peaks[2] > 50.5
    thick = solve_torispherical(1000, 20, 1000, 60).max_vm(1)
    assert thick < peaks[0] and thick > 0.5 * 1000 / (2 * 20)
