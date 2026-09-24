"""Köşe kaynağı dayanımı — welds/strength.py."""

import pytest

from welds.strength import (
    WeldGroup,
    check_fillet_weld_group,
    fillet_allowable_shear,
    fillet_effective_length,
    fillet_throat,
    weld_group_rectangle,
    weld_group_two_lines,
    weld_line_forces,
)


def line_group_modulus(segments, d, n=4000):
    """Kaynak çizgilerini noktalara bölüp I_w = Σ y²·dl hesaplar, S_w = I_w/(d/2).
    segments: [(y0, y1, count)] — eğilme doğrultusunda y0→y1 uzanan çizgiler;
    y0 == y1 ise o yükseklikte yatay çizgi, count = boy."""
    I = 0.0
    for y0, y1, length in segments:
        if y0 == y1:
            I += y0**2 * length
        else:
            dl = (y1 - y0) / n
            I += sum((y0 + (k + 0.5) * dl) ** 2 * dl for k in range(n)) * length
    return I / (d / 2)


class TestFilletBasics:
    def test_throat_is_0_707_leg(self):
        assert fillet_throat(10) == pytest.approx(7.071, rel=1e-4)

    def test_allowable_is_30_percent_fexx(self):
        assert fillet_allowable_shear(480) == pytest.approx(144.0)

    def test_effective_length_deducts_two_legs(self):
        assert fillet_effective_length(100, 6) == pytest.approx(88.0)

    def test_effective_length_rejects_too_short(self):
        with pytest.raises(ValueError, match="krater"):
            fillet_effective_length(10, 6)

    @pytest.mark.parametrize("fn,arg", [(fillet_throat, 0), (fillet_allowable_shear, -1)])
    def test_non_positive_rejected(self, fn, arg):
        with pytest.raises(ValueError):
            fn(arg)


class TestWeldGroups:
    def test_rectangle_modulus_matches_line_integration(self):
        b, d = 100.0, 200.0
        g = weld_group_rectangle(b, d)
        # iki düşey çizgi (−d/2 → d/2) + iki yatay çizgi (±d/2, boy b)
        S = line_group_modulus(
            [(-d / 2, d / 2, 1), (-d / 2, d / 2, 1), (d / 2, d / 2, b), (-d / 2, -d / 2, b)], d
        )
        assert g.L_w == pytest.approx(600.0)
        assert g.S_w == pytest.approx(S, rel=1e-5)

    def test_two_lines_modulus_matches_line_integration(self):
        d = 150.0
        g = weld_group_two_lines(d, 50.0)
        S = line_group_modulus([(-d / 2, d / 2, 1), (-d / 2, d / 2, 1)], d)
        assert g.L_w == pytest.approx(300.0)
        assert g.S_w == pytest.approx(S, rel=1e-5)

    def test_line_forces_combine_vectorially(self):
        # f_v = 6000/600 = 10, f_n = 7500/1000 = 7,5 → f_r = 12,5 (3-4-5 üçgeni)
        g = WeldGroup(L_w=600.0, S_w=1000.0)
        f_r = weld_line_forces(g.L_w, g.S_w, shear=6000.0, moment=7500.0)
        assert f_r == pytest.approx(12.5)


class TestFilletGroupCheck:
    def test_hand_calc(self):
        # b=100, d=200 → L_w=600, S_w=33 333; V=10 kN, M=1 kN·m
        # f_v=16,667, f_n=30 → f_r=34,319 N/mm; a=4,243 → τ=8,089 MPa; izin 144 MPa
        r = check_fillet_weld_group(
            6.0, weld_group_rectangle(100, 200), 480, shear=10_000, moment=1_000_000
        )
        assert r.line_force_N_per_mm == pytest.approx(34.319, rel=1e-4)
        assert r.stress_MPa == pytest.approx(8.089, rel=1e-3)
        assert r.utilization == pytest.approx(8.089 / 144, rel=1e-3)
        assert r.min_leg_ok is None  # asgari bacak girdisi yok → kontrol yapılmadı

    def test_required_leg_gives_exact_unity(self):
        g = weld_group_two_lines(120, 50)
        loads = dict(shear=40_000, normal=5_000, moment=2_500_000)
        r = check_fillet_weld_group(6.0, g, 480, **loads)
        at_required = check_fillet_weld_group(r.required_leg_mm, g, 480, **loads)
        assert at_required.utilization == pytest.approx(1.0)

    def test_min_leg_check(self):
        g = weld_group_rectangle(100, 200)
        assert check_fillet_weld_group(6, g, 480, shear=1000, min_leg_mm=8).min_leg_ok is False
        assert check_fillet_weld_group(8, g, 480, shear=1000, min_leg_mm=8).min_leg_ok is True

    def test_overloaded_weld_exceeds_unity(self):
        r = check_fillet_weld_group(3, weld_group_two_lines(50, 30), 480, shear=200_000)
        assert r.utilization > 1.0
        assert r.required_leg_mm > 3
