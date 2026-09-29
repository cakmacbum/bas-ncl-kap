"""WRC 107/537 lokal gerilme çekirdeği — supports/wrc.py.

Katsayıların kendisi (K6 gereği) hiçbir yerde gömülü değil; bu testler
kullanıcı tarafından girilecek katsayılardan üretilen bindirme, sınıflandırma
ve kapsam matematiğinin doğruluğunu, el hesabı ve dimensiyonel tutarlılıkla
sınar.
"""

import math

import pytest

from supports.wrc import (
    D_T_MAX,
    D_T_MIN,
    WrcCoefficients,
    WrcPointCoefficients,
    applicability_gate,
    beta,
    classify_point,
    evaluate_all_points,
    evaluate_point,
    gamma,
    point_stress_resultants,
)


def full(**kw):
    """Dört bileşen de açıkça girilmiş katsayı; belirtilmeyenler gerçek 0.0."""
    base = dict(Nx=0.0, Ny=0.0, Mx=0.0, My=0.0)
    base.update(kw)
    return WrcPointCoefficients(**base)


class TestGeometryParams:
    def test_gamma_and_beta(self):
        assert gamma(500, 10) == pytest.approx(50.0)
        assert beta(50, 500) == pytest.approx(0.1)

    @pytest.mark.parametrize("fn,args", [(gamma, (0, 10)), (gamma, (500, 0)), (beta, (-1, 500))])
    def test_rejects_non_positive(self, fn, args):
        with pytest.raises(ValueError):
            fn(*args)


class TestApplicabilityGate:
    def test_within_range(self):
        ok, msg = applicability_gate(1000, 10)  # D/T = 100
        assert ok is True
        assert "100" in msg

    def test_boundary_inclusive(self):
        assert applicability_gate(D_T_MIN * 10, 10)[0] is True
        assert applicability_gate(D_T_MAX * 10, 10)[0] is True

    def test_below_and_above_range_rejected(self):
        assert applicability_gate(50, 10)[0] is False       # D/T = 5 < 7
        assert applicability_gate(30000, 10)[0] is False    # D/T = 3000 > 2500


class TestCoefficientBookkeeping:
    def test_missing_zero_load_is_not_flagged(self):
        coeffs = WrcCoefficients()
        assert coeffs.missing_for("A", "P", {"P": 0.0}) == []

    def test_missing_nonzero_load_no_entry_lists_all_components(self):
        coeffs = WrcCoefficients()
        assert coeffs.missing_for("C", "MC", {"MC": 5000.0}) == ["C/MC: Nx, Ny, Mx, My"]

    def test_partial_entry_is_flagged_not_zeroed(self):
        # B-29: kısmi giriş eskiden eksik bileşeni sessizce 0 sayıyordu (gerilme düşük kalıyordu)
        coeffs = WrcCoefficients(table={"A": {"P": WrcPointCoefficients(Nx=0.4, Mx=0.3)}})
        assert coeffs.missing_for("A", "P", {"P": 1000.0}) == ["A/P: Ny, My"]

    def test_partial_entry_blocks_calculation(self):
        coeffs = WrcCoefficients(table={"A": {"P": WrcPointCoefficients(Nx=0.4)}})
        with pytest.raises(ValueError, match="Ny, Mx, My"):
            point_stress_resultants("A", coeffs, 500, P=1000)

    def test_explicit_zero_is_a_real_value(self):
        coeffs = WrcCoefficients(table={"A": {"P": full(Nx=0.4)}})
        assert coeffs.missing_for("A", "P", {"P": 1000.0}) == []
        Nx, Ny, Mx, My = point_stress_resultants("A", coeffs, 500, P=1000)
        assert Ny == Mx == My == 0.0
        assert Nx == pytest.approx(0.4 * 1000 / 500)

    def test_inactive_load_needs_no_coefficients(self):
        # P aktif, ML=0: ML için katsayı girilmemesi hesabı engellemez
        coeffs = WrcCoefficients(table={"A": {"P": full(Nx=0.4)}})
        Nx, _, _, _ = point_stress_resultants("A", coeffs, 500, P=1000, ML=0.0)
        assert Nx == pytest.approx(0.4 * 1000 / 500)


class TestPointStressResultants:
    def test_force_load_scales_as_documented(self):
        # P kuvvet tipi: N ∝ K·P/Rm, M ∝ K·P
        coeffs = WrcCoefficients(table={"A": {"P": full(Nx=0.5, Mx=0.3)}})
        Nx, _, Mx, _ = point_stress_resultants("A", coeffs, Rm=500, P=10_000)
        assert Nx == pytest.approx(0.5 * 10_000 / 500)
        assert Mx == pytest.approx(0.3 * 10_000)

    def test_moment_load_scales_as_documented(self):
        # ML moment tipi: N ∝ K·ML/Rm², M ∝ K·ML/Rm
        coeffs = WrcCoefficients(table={"A": {"ML": full(Nx=0.2, Mx=0.6)}})
        Nx, _, Mx, _ = point_stress_resultants("A", coeffs, Rm=500, ML=2_000_000)
        assert Nx == pytest.approx(0.2 * 2_000_000 / 500**2)
        assert Mx == pytest.approx(0.6 * 2_000_000 / 500)

    def test_contributions_from_multiple_loads_superpose(self):
        coeffs = WrcCoefficients(table={"A": {
            "P": full(Nx=0.5),
            "ML": full(Nx=0.2),
        }})
        Nx_p, _, _, _ = point_stress_resultants("A", coeffs, 500, P=10_000)
        Nx_ml, _, _, _ = point_stress_resultants("A", coeffs, 500, ML=2_000_000)
        Nx_both, _, _, _ = point_stress_resultants("A", coeffs, 500, P=10_000, ML=2_000_000)
        assert Nx_both == pytest.approx(Nx_p + Nx_ml)

    def test_invalid_point_rejected(self):
        with pytest.raises(ValueError):
            point_stress_resultants("Z", WrcCoefficients(), 500, P=1)


class TestEvaluatePoint:
    def test_outside_adds_bending_inside_subtracts(self):
        coeffs = WrcCoefficients(table={"A": {"P": full(Nx=0.1, Mx=0.5)}})
        out = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, P=10_000)
        inn = evaluate_point("A", "inside", coeffs, Rm=500, T_eff=10, P=10_000)
        assert out.bending_axial == pytest.approx(-inn.bending_axial)
        assert out.membrane_axial == pytest.approx(inn.membrane_axial)
        assert out.total_axial != inn.total_axial

    def test_pressure_stress_adds_to_membrane(self):
        coeffs = WrcCoefficients()
        r = evaluate_point(
            "A", "outside", coeffs, Rm=500, T_eff=10,
            pressure_axial_stress=40.0, pressure_circ_stress=80.0,
        )
        assert r.total_axial == pytest.approx(40.0)
        assert r.total_circ == pytest.approx(80.0)

    def test_stress_intensity_hand_calc(self):
        # sx=100, sy=0, tau=0 -> von Mises düzlem gerilme = sx
        coeffs = WrcCoefficients()
        r = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, pressure_axial_stress=100.0)
        assert r.stress_intensity == pytest.approx(100.0)

    def test_stress_intensity_pure_shear(self):
        coeffs = WrcCoefficients()
        r = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, shear_stress=50.0)
        assert r.stress_intensity == pytest.approx(50.0 * math.sqrt(3.0))

    def test_invalid_surface_rejected(self):
        with pytest.raises(ValueError):
            evaluate_point("A", "top", WrcCoefficients(), 500, 10)

    def test_non_positive_thickness_rejected(self):
        with pytest.raises(ValueError):
            evaluate_point("A", "outside", WrcCoefficients(), 500, 0)


class TestEvaluateAllPoints:
    def test_returns_eight_points(self):
        coeffs = WrcCoefficients(table={pt: {"P": full()} for pt in "ABCD"})
        results = evaluate_all_points(coeffs, Rm=500, T_eff=10, P=1000)
        assert len(results) == 8
        assert set(k[0] for k in results) == {"A", "B", "C", "D"}
        assert set(k[1] for k in results) == {"outside", "inside"}


class TestAllPointsRequireCoefficients:
    def test_missing_point_blocks_the_whole_evaluation(self):
        coeffs = WrcCoefficients(table={pt: {"P": full()} for pt in "ABC"})  # D eksik
        with pytest.raises(ValueError, match="D/P"):
            evaluate_all_points(coeffs, Rm=500, T_eff=10, P=1000)


class TestClassification:
    def test_pass_when_within_allowable(self):
        coeffs = WrcCoefficients()
        r = evaluate_point("A", "outside", coeffs, 500, 10, pressure_axial_stress=50)
        cls = classify_point(r, S=150)
        assert cls.pl_ok and cls.pl_pb_ok
        assert cls.allowable_PL == pytest.approx(225.0)

    def test_fail_when_pl_pb_exceeds_allowable(self):
        coeffs = WrcCoefficients(table={"A": {"P": full(Mx=5.0)}})
        r = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, P=100_000)
        cls = classify_point(r, S=150)
        assert cls.pl_pb_ok is False

    def test_pl_excludes_bending_pl_pb_includes_it(self):
        coeffs = WrcCoefficients(table={"A": {"P": full(Mx=2.0)}})
        r = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, P=50_000)
        cls = classify_point(r, S=200)
        assert cls.PL < cls.PL_plus_Pb

    def test_membrane_only_load_gives_equal_pl_and_pl_pb(self):
        coeffs = WrcCoefficients(table={"A": {"P": full(Nx=0.3)}})
        r = evaluate_point("A", "outside", coeffs, Rm=500, T_eff=10, P=20_000)
        cls = classify_point(r, S=150)
        assert cls.PL == pytest.approx(cls.PL_plus_Pb)

    def test_rejects_non_positive_allowable(self):
        r = evaluate_point("A", "outside", WrcCoefficients(), 500, 10)
        with pytest.raises(ValueError):
            classify_point(r, S=0)
