"""Ayak kesit özellikleri ve kolon kontrolü — supports/sections.py.

Sabitlenen değerler el hesabıdır; ayrıca kesit özellikleri formülden bağımsız
olarak ızgara integrasyonuyla doğrulanır (uygulamayı değil geometriyi test eder).
"""

import math

import pytest

from supports.sections import (
    MAX_COMPRESSION_SLENDERNESS,
    aisc_interaction_ratio,
    allowable_compressive_stress,
    angle_section,
    box_section,
    channel_section,
    column_critical_slenderness,
    column_slenderness,
    euler_stress_asd,
    leg_axial_stress,
    leg_bending_stress,
    pipe_section,
)


def grid_properties(rects, cell=0.25):
    """Dikdörtgen listesini (x0, y0, x1, y1) küçük hücrelere bölerek A, Ix, Iy,
    Ixy ve asal I_min'i sayısal hesaplar."""
    cells = []
    for x0, y0, x1, y1 in rects:
        nx, ny = round((x1 - x0) / cell), round((y1 - y0) / cell)
        for i in range(nx):
            for j in range(ny):
                cells.append((x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell))
    dA = cell * cell
    A = len(cells) * dA
    xc = sum(c[0] for c in cells) * dA / A
    yc = sum(c[1] for c in cells) * dA / A
    Ix = sum((c[1] - yc) ** 2 for c in cells) * dA + len(cells) * dA * cell**2 / 12
    Iy = sum((c[0] - xc) ** 2 for c in cells) * dA + len(cells) * dA * cell**2 / 12
    Ixy = sum((c[0] - xc) * (c[1] - yc) for c in cells) * dA
    I_min = (Ix + Iy) / 2 - math.sqrt(((Ix - Iy) / 2) ** 2 + Ixy**2)
    return A, Ix, Iy, I_min


class TestSectionProperties:
    def test_channel_hand_calc(self):
        # h=100, b=50, s=6, t=8.5 → A = 2·50·8.5 + 83·6 = 1348 mm²
        # Ix = (50·100³ − 44·83³)/12 = 2 070 114 mm⁴
        c = channel_section(100, 50, 6, 8.5)
        assert c.A == pytest.approx(1348.0)
        assert c.Ix == pytest.approx(2_070_114.33, rel=1e-6)
        assert c.Sx == pytest.approx(c.Ix / 50.0)
        assert c.r_min == pytest.approx(c.ry)

    def test_channel_matches_grid_integration(self):
        h, b, s, t = 100, 50, 6, 8.5
        A, Ix, Iy, _ = grid_properties([
            (0, 0, b, t), (0, h - t, b, h), (0, t, s, h - t),
        ])
        c = channel_section(h, b, s, t)
        assert c.A == pytest.approx(A, rel=1e-6)
        assert c.Ix == pytest.approx(Ix, rel=1e-3)
        assert c.Iy == pytest.approx(Iy, rel=1e-3)

    def test_angle_min_radius_matches_grid_principal_axis(self):
        a, b, t = 50, 50, 5
        A, _, _, I_min = grid_properties([(0, 0, t, a), (t, 0, b, t)])
        L = angle_section(a, b, t)
        assert L.A == pytest.approx(A, rel=1e-6)
        assert L.r_min == pytest.approx(math.sqrt(I_min / A), rel=1e-3)
        # Eşit kollu köşebentte asal eksen 45°'dedir; r_min, rx'ten belirgin küçüktür.
        assert L.r_min < 0.7 * L.rx

    def test_unequal_angle_matches_grid(self):
        a, b, t = 80, 40, 6
        A, Ix, Iy, I_min = grid_properties([(0, 0, t, a), (t, 0, b, t)])
        L = angle_section(a, b, t)
        assert L.Ix == pytest.approx(Ix, rel=1e-3)
        assert L.Iy == pytest.approx(Iy, rel=1e-3)
        assert L.r_min == pytest.approx(math.sqrt(I_min / A), rel=1e-3)

    def test_box_hand_calc(self):
        # 100×60×5: A = 6000 − 90·50 = 1500; Ix = (60·100³ − 50·90³)/12 = 1 962 500
        box = box_section(100, 60, 5)
        assert box.A == pytest.approx(1500.0)
        assert box.Ix == pytest.approx(1_962_500.0)
        assert box.Iy == pytest.approx(862_500.0)

    def test_pipe_is_annulus_not_solid(self):
        p = pipe_section(114.3, 6.0)
        solid = math.pi / 4 * 114.3**2
        assert p.A < solid
        assert p.A == pytest.approx(math.pi / 4 * (114.3**2 - 102.3**2))
        assert p.rx == p.ry == p.r_min

    @pytest.mark.parametrize("fn,args", [
        (channel_section, (16, 50, 6, 8.5)),   # h ≤ 2t
        (channel_section, (100, 5, 6, 8.5)),   # b ≤ s
        (box_section, (10, 60, 5)),            # iç boşluk yok
        (angle_section, (5, 50, 5)),           # a ≤ t
        (pipe_section, (20, 10)),              # Di ≤ 0
        (channel_section, (100, 50, 0, 8.5)),  # sıfır kalınlık
    ])
    def test_invalid_dimensions_rejected(self, fn, args):
        with pytest.raises(ValueError):
            fn(*args)


class TestStresses:
    def test_axial_and_bending(self):
        assert leg_axial_stress(13_480, 1348) == pytest.approx(10.0)
        # N·e/S = 10 000 · 100 / 41 402 = 24,15 MPa
        assert leg_bending_stress(10_000, 100, 41_402.29) == pytest.approx(24.153, rel=1e-4)

    def test_negative_eccentricity_rejected(self):
        with pytest.raises(ValueError):
            leg_bending_stress(1000, -5, 1000)


class TestColumnBuckling:
    E, Fy = 200_000.0, 250.0

    def test_critical_slenderness(self):
        # Cc = √(2π²·200000/250) = 125,66
        assert column_critical_slenderness(self.E, self.Fy) == pytest.approx(125.664, rel=1e-4)

    def test_zero_slenderness_gives_0_6_Fy(self):
        # KL/r = 0 → FS = 5/3 → Fa = 0,6·Fy
        assert allowable_compressive_stress(0, self.E, self.Fy) == pytest.approx(150.0)

    def test_hand_calc_kl_r_100(self):
        # r = 100/125,664 = 0,7958; FS = 1,6667 + 0,2984 − 0,0630 = 1,9021
        # Fa = (1 − 0,3166)·250 / 1,9021 = 89,82 MPa
        assert allowable_compressive_stress(100, self.E, self.Fy) == pytest.approx(89.82, rel=1e-3)

    def test_continuous_at_Cc(self):
        Cc = column_critical_slenderness(self.E, self.Fy)
        below = allowable_compressive_stress(Cc - 1e-9, self.E, self.Fy)
        above = allowable_compressive_stress(Cc + 1e-9, self.E, self.Fy)
        assert below == pytest.approx(above, rel=1e-6)
        assert below == pytest.approx(6 * self.Fy / 23, rel=1e-6)

    def test_monotonically_decreasing(self):
        values = [allowable_compressive_stress(s, self.E, self.Fy) for s in range(0, 301, 5)]
        assert all(a > b for a, b in zip(values, values[1:]))

    def test_slenderness_and_limit(self):
        assert column_slenderness(2.1, 1500, 15.66) == pytest.approx(201.15, rel=1e-3)
        assert MAX_COMPRESSION_SLENDERNESS == 200.0

    def test_euler_asd(self):
        assert euler_stress_asd(self.E, 150) == pytest.approx(
            12 * math.pi**2 * self.E / (23 * 150**2)
        )


class TestInteraction:
    def test_small_axial_uses_simple_sum(self):
        # fa/Fa = 0,10 ≤ 0,15
        assert aisc_interaction_ratio(10, 100, 30, 150, 250) == pytest.approx(0.30)

    def test_large_axial_amplifies_bending(self):
        ratio = aisc_interaction_ratio(50, 100, 30, 150, 250, Fe_prime=200)
        # H1-1: 0,5 + 0,85·30/((1 − 0,25)·150) = 0,7267 ; H1-2: 50/150 + 0,2 = 0,5333
        assert ratio == pytest.approx(0.72667, rel=1e-4)
        assert ratio > 50 / 100 + 30 / 150

    def test_large_axial_requires_Fe_prime(self):
        with pytest.raises(ValueError, match="Fe_prime"):
            aisc_interaction_ratio(50, 100, 30, 150, 250)

    def test_axial_above_euler_is_unstable(self):
        assert aisc_interaction_ratio(60, 100, 0, 150, 250, Fe_prime=50) == math.inf
