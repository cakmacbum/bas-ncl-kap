"""Faz 5 — Flanges modülü testleri.

Golden-case ve durum testleri.
Referans: ASME BPVC Section VIII Division 1, Appendix 2.
"""

import pytest
from units import relative_tolerance

from flanges.formulas import (
    hydrostatic_end_force,
    bolt_load_operating,
    flange_moment,
    flange_shape_parameters,
    hub_longitudinal_stress,
    radial_flange_stress,
    tangential_flange_stress,
    flange_stress_checks,
)
from flanges.flange_calc import FlangeCalculator

from domain import (
    DesignConditions,
    MaterialProperty,
    ProductForm,
)


# Şekil 2-7.1 faktörleri (kullanıcı girdisi; test için sembolik değerler, K6).
FVTU = {"flange_factor_F": 0.9, "flange_factor_V": 0.4,
        "flange_factor_T": 1.8, "flange_factor_U": 7.0}


# ── Formül testleri ────────────────────────────────────────────────────────────

class TestFlangeFormulas:
    """Flanş formüllerinin birim testleri."""

    def test_hydrostatic_end_force(self):
        """Appendix 2-5 — Hidrostatik uç kuvveti.

        P = 1.2 MPa, G = 500 mm
        H = π/4 × 500² × 1.2 = 196349.5 × 1.2 = 235619.4 N
        """
        H = hydrostatic_end_force(1.2, 500.0)
        assert relative_tolerance(H, 235619.4, 0.01), f"H={H}"

    def test_bolt_load_operating(self):
        """Appendix 2-5(a) — İşletme durumu cıvata yükü."""
        W = bolt_load_operating(235619.4, 50000.0)
        assert relative_tolerance(W, 285619.4, 0.01)

    def test_flange_moment(self):
        """Appendix 2-6 — Flanş momenti.

        H_D = 235619 N, h_D = 250 mm
        H_G = 50000 N, h_G = 300 mm
        H_T = 10000 N, h_T = 200 mm
        M = 235619×250 + 50000×300 + 10000×200
          = 58904750 + 15000000 + 2000000 = 75904750 N·mm
        """
        M = flange_moment(235619.0, 250.0, 50000.0, 300.0, 10000.0, 200.0)
        assert relative_tolerance(M, 75904750.0, 0.01), f"M={M}"

    def test_hub_longitudinal_stress(self):
        """Appendix 2-7 — S_H = f·M/(L·g1²·B).

        Eski formül (f·M/(g1²·h0)) standart formdan farklıydı (L ve B yok);
        beklenen değer bu yüzden değişti (formül düzeltmesinin doğal sonucu).
        M = 75904750, f = 1.0, L = 1.0, g1 = 25, B = 500
        S_H = 75904750 / (1·625·500) = 75904750 / 312500 = 242.895 MPa
        """
        S_H = hub_longitudinal_stress(75904750.0, 1.0, 1.0, 25.0, 500.0)
        assert relative_tolerance(S_H, 242.895, 0.001), f"S_H={S_H}"

    def test_radial_flange_stress(self):
        """Appendix 2-7 — S_R = (1.33·t·e + 1)·M/(L·t²·B).

        Eski formül 4M/(t²B) idi; standartta (1.33·t·e+1)/L çarpanı var.
        M = 75904750, t = 50, B = 500, L = 1, e = 0.01 (1.33·50·0.01+1 = 1.665)
        S_R = 1.665·75904750 / (1·2500·500) = 126,384,... / 1,250,000 = 101.10 MPa
        """
        S_R = radial_flange_stress(75904750.0, 1.0, 50.0, 0.01, 500.0)
        assert relative_tolerance(S_R, 1.665 * 75904750.0 / 1250000.0, 1e-9)
        assert relative_tolerance(S_R, 101.104, 0.001), f"S_R={S_R}"

    def test_tangential_flange_stress(self):
        """Appendix 2-7 — S_T = Y·M/(t²·B) − Z·S_R.

        M = 75904750, Y = 9.0, t = 50, B = 500, Z = 3.0, S_R = 100
        Y·M/(t²B) = 683142750 / 1250000 = 546.514 ; S_T = 546.514 − 300 = 246.514
        (eski kod −Z·S_R terimini içermiyordu: 546.5)
        """
        S_T = tangential_flange_stress(75904750.0, 9.0, 50.0, 500.0, 3.0, 100.0)
        assert relative_tolerance(S_T, 246.514, 0.001), f"S_T={S_T}"

    def test_flange_stress_checks_pass(self):
        """Gerilme kontrolü — hepsi sınır altında."""
        rows = flange_stress_checks(100.0, 50.0, 60.0, 138.0)
        assert all(v <= lim for _, v, lim in rows)

    def test_flange_stress_checks_fail_sh(self):
        """S_H > 1.5·S_f ihlali (S_f=100 → limit 150, S_H=200)."""
        rows = flange_stress_checks(200.0, 50.0, 60.0, 100.0)
        bad = [n for n, v, lim in rows if v > lim]
        assert "S_H" in bad


# ── Calculator entegrasyon testleri ───────────────────────────────────────────

class TestFlangeCalculator:
    """FlangeCalculator entegrasyon testleri."""

    @pytest.fixture
    def calc(self):
        return FlangeCalculator()

    @pytest.fixture
    def mat(self):
        return MaterialProperty(
            material_id="MAT-FLANGE",
            standard_pack="ASME II-D 2025",
            material_designation="SA-105",
            product_form=ProductForm.FORGING,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=250.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 1",
        )

    def test_flange_stress_pass(self, calc, mat):
        """Flanş gerilme kontrolü — PASS."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-01",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 300000.0,
            "moment_M": 5000000.0,  # Düşük moment → düşük gerilme
            "flange_factor_Y": 9.0,
            "flange_factor_f": 1.0,
            **FVTU,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "Appendix 2"
        # W/M kullanıcı girdisi + basitleştirilmiş formüller → nihai PASS verilmez.
        assert r.status.value == "REVIEW REQUIRED"
        assert any("W ve M kullanıcı girdisidir" in w for w in r.warnings)
        assert r.final_result is not None

    def test_flange_stress_fail(self, calc, mat):
        """Flanş gerilme kontrolü — FAIL (yüksek moment)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-02",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 500000.0,
            "moment_M": 100000000.0,  # Çok yüksek moment
            "flange_factor_Y": 9.0,
            "flange_factor_f": 1.0,
            **FVTU,
        })
        assert r.status.value == "FAIL"

    def test_traceability(self, calc, mat):
        """K5: İzlenebilirlik."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-03",
                "type": "integral",
                "B": 500.0,
                "A": 700.0,
                "t": 50.0,
                "g0": 20.0,
                "g1": 25.0,
                "h": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 300000.0,
            "moment_M": 5000000.0,
            "flange_factor_Y": 9.0,
            "flange_factor_f": 1.0,
            **FVTU,
        })
        assert len(r.intermediate_values) > 0
        assert r.material_properties_used != {}

    def test_y_faktoru_yoksa_bloke_olur(self, calc, mat):
        """K4: Appendix 2 Y faktörü verilmezse hesap yapılmaz, varsayılan atanmaz.

        Eskiden sessizce `Y = 5.0` varsayılıyordu. Y, K = A/B oranına göre
        Şekil 2-7.1'den okunur ve geniş aralıkta değişir; sessiz varsayılan,
        modül hesap hattına bağlandığı gün sessizce yanlış sonuç üretirdi.
        """
        from domain.enums import CalculationStatus

        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_flange_stress({
            "flange": {
                "tag": "FL-NOY", "type": "integral", "B": 500.0, "A": 700.0,
                "t": 50.0, "g0": 20.0, "g1": 25.0, "h": 50.0,
                "material_id": "MAT-FLANGE",
            },
            "design_conditions": dc,
            "materials": [mat],
            "bolt_load_W": 300000.0,
            "moment_M": 5000000.0,
            "flange_factor_f": 1.0,
            **FVTU,
            # flange_factor_Y bilerek verilmedi
        })
        assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
        assert any("Y" in w for w in r.warnings), r.warnings

    def test_moment_calculation(self, calc):
        """Moment hesaplama."""
        result = calc.calculate_moment_from_pressure({
            "P": 1.2,
            "G": 500.0,
            "B": 500.0,
            "h_D": 250.0,
            "h_G": 300.0,
            "h_T": 200.0,
            "H_p": 50000.0,
        })
        assert "H" in result
        assert "M" in result
        assert result["H"] > 0
        assert result["M"] > 0


# ── Standart form: elle hesaplanmış tam örnek + kapsam/eksik girdi/ihlal ──────

def _dc():
    return DesignConditions(
        operating_pressure=1.0, design_pressure=1.2,
        maximum_allowable_pressure_ps=1.5, operating_temperature=200.0,
        design_temperature=200.0, minimum_design_temperature=-10.0,
    )


def _mat(allow=138.0):
    return MaterialProperty(
        material_id="MAT-FLANGE", standard_pack="ASME II-D 2025",
        material_designation="SA-105", product_form=ProductForm.FORGING,
        temperature=200.0, allowable_stress=allow, yield_strength=250.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 1",
    )


def _payload(M=5e6, flange_over=None, **over):
    flange = {"tag": "FL-H", "type": "integral", "B": 500.0, "A": 700.0, "t": 60.0,
              "g0": 20.0, "g1": 25.0, "h": 50.0, "material_id": "MAT-FLANGE"}
    flange.update(flange_over or {})
    d = {"flange": flange, "design_conditions": _dc(), "materials": [_mat(over.pop("allow", 138.0))],
         "bolt_load_W": 3e5, "moment_M": M, "flange_factor_Y": 9.0, "flange_factor_f": 1.2,
         "flange_factor_F": 0.9, "flange_factor_V": 0.4, "flange_factor_T": 1.8,
         "flange_factor_U": 7.0}
    d.update(over)
    return d


def _iv(r, name):
    return next(i["value"] for i in r.intermediate_values if i["name"] == name)


def test_hand_calc_full_example_standard_form():
    """Tam el hesabı (kodla paylaşılan formül çağrısı YOK; sayılar elle türetildi).

    Girdi: B=500, A=700, t=60, g0=20, g1=25, M=5e6 N·mm,
           Y=9.0, f=1.2, F=0.9, V=0.4, T=1.8, U=7.0 (sembolik sayılar).
      K  = 700/500 = 1.4            K² = 1.96
      Z  = (1.96+1)/(1.96-1) = 2.96/0.96 = 3.083333
      h0 = √(500·20) = √10000 = 100
      e  = F/h0 = 0.9/100 = 0.009
      d  = (U/V)·h0·g0² = 17.5·100·400 = 700000
      L  = (t·e+1)/T + t³/d = (0.54+1)/1.8 + 216000/700000 = 0.855556 + 0.308571 = 1.164127
      S_H = f·M/(L·g1²·B) = 6e6 / (1.164127·625·500) = 6e6/363789.68 = 16.4930
      1.33·t·e+1 = 1.33·60·0.009 + 1 = 1.7182
      S_R = 1.7182·5e6 / (1.164127·3600·500) = 8.591e6/2095... = 4.09988
      Y·M/(t²B) = 9·5e6/(3600·500) = 25.0
      S_T = 25.0 − 3.083333·4.09988 = 25.0 − 12.64129 = 12.35871
      (S_H+S_R)/2 = (16.4930+4.09988)/2 = 10.29646
      (S_H+S_T)/2 = (16.4930+12.35871)/2 = 14.42588
    """
    r = FlangeCalculator().check_flange_stress(_payload())
    assert _iv(r, "K") == pytest.approx(1.4)
    assert _iv(r, "Z") == pytest.approx(3.083333, rel=1e-6)
    assert _iv(r, "h0") == pytest.approx(100.0)
    assert _iv(r, "e") == pytest.approx(0.009)
    assert _iv(r, "d") == pytest.approx(700000.0)
    assert _iv(r, "L") == pytest.approx(1.164127, rel=1e-6)
    assert _iv(r, "S_H") == pytest.approx(16.4930, rel=1e-4)
    assert _iv(r, "S_R") == pytest.approx(4.09988, rel=1e-4)
    assert _iv(r, "S_T") == pytest.approx(12.35871, rel=1e-4)
    assert _iv(r, "(S_H+S_R)/2") == pytest.approx(10.29646, rel=1e-4)
    assert _iv(r, "(S_H+S_T)/2") == pytest.approx(14.42588, rel=1e-4)
    assert r.status.value == "REVIEW REQUIRED"
    assert any("2.5·S_n" in w for w in r.warnings)


def test_z_formula_boundary_behaviour():
    """K→1 iken Z→∞ (A→B), K büyüdükçe Z→1; A ≤ B geçersiz (Z tanımsız)."""
    z = lambda A: flange_shape_parameters(A, 500.0, 60.0, 20.0, 0.9, 0.4, 1.8, 7.0)["Z"]
    assert z(500.0 * 1.001) > 1000.0
    assert z(500.0 * 1000.0) == pytest.approx(1.0, abs=1e-5)
    assert z(700.0) == pytest.approx(3.0833333, rel=1e-6)
    with pytest.raises(ValueError):
        flange_shape_parameters(500.0, 500.0, 60.0, 20.0, 0.9, 0.4, 1.8, 7.0)
    with pytest.raises(ValueError):
        flange_shape_parameters(400.0, 500.0, 60.0, 20.0, 0.9, 0.4, 1.8, 7.0)


@pytest.mark.parametrize("missing", ["flange_factor_Y", "flange_factor_f", "flange_factor_F",
                                     "flange_factor_V", "flange_factor_T", "flange_factor_U"])
def test_each_missing_factor_blocks(missing):
    from domain.enums import CalculationStatus
    p = _payload()
    p.pop(missing)
    r = FlangeCalculator().check_flange_stress(p)
    assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
    short = missing.split("_")[-1]
    assert any(f" {short}," in w or f" {short}." in w or w.endswith(short) for w in r.warnings), r.warnings


def test_missing_g1_blocks():
    from domain.enums import CalculationStatus
    r = FlangeCalculator().check_flange_stress(_payload(flange_over={"g1": None}))
    assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT
    assert any("g1" in w for w in r.warnings)


def test_loose_flange_is_out_of_scope():
    from domain.enums import CalculationStatus
    r = FlangeCalculator().check_flange_stress(_payload(flange_over={"type": "loose"}))
    assert r.status == CalculationStatus.OUT_OF_SCOPE
    assert not r.intermediate_values
    assert any("loose" in w.lower() for w in r.warnings)


@pytest.mark.parametrize("allow,which", [
    (10.0, "S_H"),      # 1.5·10 = 15 < S_H = 16.49 (diğerleri ≤ 10 → yalnız S_H ihlali)
    (12.0, "S_T"),      # S_T=12.36 > 12; S_H=16.49 ≤ 18; (S_H+S_T)/2=14.43 > 12 de ihlal
    (14.0, "(S_H+S_T)/2"),  # S_T=12.36 ≤ 14, ortalama 14.43 > 14
])
def test_single_check_violations_fail(allow, which):
    from domain.enums import CalculationStatus
    r = FlangeCalculator().check_flange_stress(_payload(allow=allow))
    assert r.status == CalculationStatus.FAIL
    assert any(which + "=" in w for w in r.warnings), r.warnings
    assert r.utilization_ratio > 1.0


def test_sr_limit_violation_fails():
    """S_R ≤ S_f: S_R = 4.10 > S_f = 4.0 (S_H limit 6 < 16.49 da ihlal ama S_R ayrıca raporlanır)."""
    from domain.enums import CalculationStatus
    r = FlangeCalculator().check_flange_stress(_payload(allow=4.0))
    assert r.status == CalculationStatus.FAIL
    assert any("S_R=" in w for w in r.warnings)


def test_negative_stress_not_reported_as_violation():
    """İşaretli gerilme: S_T negatifse S_f sınırını aşmaz (Appendix 2 işaretli karşılaştırır)."""
    rows = flange_stress_checks(10.0, 5.0, -50.0, 20.0)
    assert all(v <= lim for _, v, lim in rows)
