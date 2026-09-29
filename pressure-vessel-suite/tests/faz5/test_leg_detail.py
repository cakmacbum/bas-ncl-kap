"""Ayak (leg) alt kontrolleri — kesit, kaynak, taban plakası, WRC lokal gerilme.

Sayısal beklentiler formülden bağımsız EL HESABIDIR (her testin docstring'inde türetilmiştir;
modül fonksiyonları beklenti üretmek için ÇAĞRILMAZ).

Ortak senaryo (doğrudan yük): 4 ayak, W = 80 000 N, moment yok → N_max = 20 000 N;
e = 90 mm; U profil h=200, b=75, s=6, t=9; ped 200×100×10; Fy = 260 MPa (E malzemede yok →
200 000 MPa varsayımı). Gövde Ø1000×12 (Rm = 506, T = 12), S = 138 MPa, P = 1,2 MPa.
"""

import math

import pytest
from pydantic import ValidationError

from code_asme_viii_1.design_code import ASMEVIII1DesignCode
from domain import (
    CalculationCode,
    ComponentReference,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    Support,
    VesselProject,
    WrcCoefficientEntry,
)
from supports import SupportCalculator, wrc
from supports import leg_detail


# ── Ortak yardımcılar ─────────────────────────────────────────────────────────

def _mat():
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4",
    )


def _dc():
    return DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=20.0, design_temperature=20.0, minimum_design_temperature=-10.0,
    )


def _shell(D=1000.0, t=12.0):
    return ShellSection(section_id="S1", inside_diameter=D, tangent_length=2000.0,
                        nominal_thickness=t, material_id="MAT-01")


CHANNEL = dict(
    leg_section_type="channel", leg_profile_height_mm=200.0, leg_profile_width_mm=75.0,
    leg_web_thickness_mm=6.0, leg_flange_thickness_mm=9.0,
)
FULL = dict(
    **CHANNEL, leg_eccentricity_mm=90.0, leg_pad_length_mm=200.0, leg_pad_width_mm=100.0,
    leg_pad_thickness_mm=10.0, base_plate_length_mm=250.0, base_plate_width_mm=150.0,
    base_plate_thickness_mm=16.0, base_plate_yield_MPa=250.0, foundation_bearing_allowable_MPa=8.0,
    pad_to_shell_weld_leg_mm=6.0, leg_to_pad_weld_leg_mm=6.0, leg_to_base_plate_weld_leg_mm=6.0,
    weld_electrode_strength_MPa=480.0,
)


def _payload(sup_fields, W=80000.0, M=0.0, shell=None, host_type="shell", n=4, lateral=0.0):
    support = {
        "tag": "LG", "type": "leg", "n_legs": n, "height_mm": 800.0, "support_radius_mm": 520.0,
        "lateral_load_N": lateral,
    }
    support.update(sup_fields)
    return {
        "support": support, "shell": shell or _shell(), "total_weight_N": W,
        "overturning_moment_Nmm": M, "materials": [_mat()], "skirt_material_id": "MAT-01",
        "design_conditions": _dc(), "host_component_type": host_type,
    }


def _details(payload):
    out = SupportCalculator().check_leg_detail(payload)
    return {r.calculation_type: r for r in out}


def _iv(result, name):
    return next(v["value"] for v in result.intermediate_values if v["name"] == name)


def _uniform_coeffs(values_by_load):
    """Tüm A/B/C/D noktalarına aynı (Nx, Ny, Mx, My) katsayılarını yükler."""
    return {
        pt: {ld: WrcCoefficientEntry(Nx=v[0], Ny=v[1], Mx=v[2], My=v[3])
             for ld, v in values_by_load.items()}
        for pt in "ABCD"
    }


# ── (f) WRC kayma normalizasyonu, katsayı kapısı ve uygulanabilirlik ───────────

class TestWrcShearAndGate:
    def test_shear_is_force_type_normalization(self):
        """VL=1000 N, Rm=500 mm, K: Nx=0.5 Ny=0.2 Mx=0.1 My=0.05 → N=K·V/Rm, M=K·V.

        Nx = 0.5·1000/500 = 1.0 N/mm; Ny = 0.4; Mx = 0.1·1000 = 100 N·mm/mm; My = 50.
        VC aynı kuralla ayrı toplanır: VC=500 → Nx += 0.5·500/500 (K aynı olsaydı).
        """
        c = wrc.coefficients_from_mapping({"A": {"VL": {"Nx": 0.5, "Ny": 0.2, "Mx": 0.1, "My": 0.05}}})
        assert wrc.point_stress_resultants("A", c, 500.0, VL=1000.0) == pytest.approx((1.0, 0.4, 100.0, 50.0))
        c2 = wrc.coefficients_from_mapping({"A": {"VC": {"Nx": 0.5, "Ny": 0.2, "Mx": 0.1, "My": 0.05}}})
        assert wrc.point_stress_resultants("A", c2, 500.0, VC=500.0) == pytest.approx((0.5, 0.2, 50.0, 25.0))

    def test_active_shear_requires_all_four_components(self):
        c = wrc.coefficients_from_mapping({"A": {"VL": {"Nx": 0.5, "Ny": None, "Mx": 0.1, "My": 0.05}}})
        with pytest.raises(ValueError, match="katsayısı eksik"):
            wrc.point_stress_resultants("A", c, 500.0, VL=1000.0)
        gaps = wrc.missing_coefficients(c, {"VL": 1000.0})
        assert gaps[0] == "A/VL: Ny"
        assert len(gaps) == 4  # A (kısmi) + B, C, D (hiç girilmedi)
        assert wrc.missing_coefficients(c, {"VL": 0.0}) == []  # sıfır yük katsayı istemez

    def test_pydantic_entries_and_none_mapping(self):
        assert wrc.coefficients_from_mapping(None).table == {}
        c = wrc.coefficients_from_mapping({"B": {"P": WrcCoefficientEntry(Nx=1, Ny=2, Mx=3, My=4)}})
        assert c.get("B", "P").My == 4

    def test_pressure_membrane_hand_calc(self):
        """P=1.2, Rm=506, T=12 → σc = 1.2·506/12 = 50.6; σL = 25.3 MPa."""
        sl, sc = wrc.pressure_membrane_stresses(1.2, 506.0, 12.0)
        assert (sl, sc) == pytest.approx((25.3, 50.6))

    @pytest.mark.parametrize("t,expect_out", [(20.0, True), (12.0, False)])
    def test_dt_gate_out_of_scope(self, t, expect_out):
        """Ø100×20: Rm = 60, D/T = 120/20 = 6 < 7 → OUT_OF_SCOPE; Ø1000×12 → D/T = 84 kapı içinde."""
        shell = _shell(D=100.0, t=20.0) if expect_out else _shell()
        r = _details(_payload(FULL, shell=shell))["wrc_local_stress"]
        if expect_out:
            assert r.status.value == "OUT OF SCOPE"
            assert "extrapolasyon" in r.warnings[0]
        else:
            assert r.status.value == "BLOCKED CODE DATA"  # kapıyı geçti, katsayı yok


# ── (a) kesit ─────────────────────────────────────────────────────────────────

class TestSection:
    def test_channel_hand_calc(self):
        """U h=200 b=75 s=6 t=9, N=20000, e=90, L=800, K=2.1, E=200000, Fy=260.

        A = 2·75·9 + 182·6 = 2442; Ix = 2[75·9³/12 + 675·95.5²] + 6·182³/12 = 15 335 734;
        Sx = 153 357.3; x̄ = 22.07, Iy = 1 354 625, ry = 23.55 (r_min), rx = 79.25.
        KL/r = 2.1·800/23.55 = 71.33; Cc = √(2π²·200000/260) = 123.22;
        Fa = (1−0.3352... )Fy/FS = 116.40 MPa; fa = 8.19; fb = 20000·90/153357 = 11.737;
        fa/Fa = 0.0704 ≤ 0.15 → H1-3: 0.0704 + 11.737/(0.6·260) = 0.14560.
        """
        r = _details(_payload(FULL))["leg_section_check"]
        assert _iv(r, "A") == pytest.approx(2442.0)
        assert _iv(r, "Ix") == pytest.approx(15335734.0)
        assert _iv(r, "KL_over_r") == pytest.approx(71.330, rel=1e-4)
        assert _iv(r, "Fa") == pytest.approx(116.396, rel=1e-4)
        assert _iv(r, "fa") == pytest.approx(8.19001, rel=1e-5)
        assert _iv(r, "fb") == pytest.approx(11.7373, rel=1e-4)
        assert r.utilization_ratio == pytest.approx(0.145602, rel=1e-4)
        assert r.status.value == "PASS"
        joined = " ".join(r.assumptions)
        assert "K = 2.1" in joined and "Fb = 0,6" in joined and "200000" in joined  # varsayımlar dolu
        assert r.material_properties_used["yield_strength"] == 260.0

    def test_pipe_annulus_hand_calc(self):
        """Ø100×8 boru, N=20000, e=90: A = π/4(100²−84²) = 2312.2; I = π/64(100⁴−84⁴) = 2 464 786;
        S = I/50 = 49 295.7; fa = 8.65; fb = 1.8e6/49295.7 = 36.51 MPa; r = 32.65."""
        f = dict(leg_section_type="pipe", leg_diameter_mm=100.0, leg_thickness_mm=8.0, leg_eccentricity_mm=90.0)
        r = _details(_payload(f))["leg_section_check"]
        A = math.pi / 4 * (100**2 - 84**2)
        assert _iv(r, "A") == pytest.approx(A)
        assert _iv(r, "fa") == pytest.approx(20000.0 / A, rel=1e-6)
        S = math.pi / 64 * (100**4 - 84**4) / 50.0
        assert _iv(r, "fb_eccentric") == pytest.approx(20000.0 * 90.0 / S, rel=1e-6)
        assert r.status.value == "PASS"

    def test_lateral_load_bending_added(self):
        """H_toplam=4000 N → 1000 N/ayak; H·L/Sx = 1000·800/153357.3 = 5.217 MPa eklenir."""
        r = _details(_payload(FULL, lateral=4000.0))["leg_section_check"]
        assert _iv(r, "fb_lateral") == pytest.approx(800000.0 / 153357.34, rel=1e-5)
        assert _iv(r, "fb") == pytest.approx(11.7373 + 5.2168, rel=1e-3)

    def test_slenderness_above_200_fails(self):
        """L=2500: KL/r = 2.1·2500/23.55 = 222.9 > 200 → FAIL (AISC E2)."""
        f = dict(FULL, leg_unbraced_length_mm=2500.0)
        r = _details(_payload(f))["leg_section_check"]
        assert r.status.value == "FAIL"
        assert _iv(r, "KL_over_r") > 200.0
        assert any("azami narinlik" in w for w in r.warnings)

    def test_overload_fails_by_interaction(self):
        """W=4e6 N → N=1e6, fa = 409.5 MPa > Fy: oran ≫ 1 ya da kararsız → FAIL."""
        r = _details(_payload(FULL, W=4.0e6))["leg_section_check"]
        assert r.status.value == "FAIL"

    def test_missing_eccentricity_and_dims_are_blocked(self):
        f = {k: v for k, v in FULL.items() if k != "leg_eccentricity_mm"}
        r = _details(_payload(f))["leg_section_check"]
        assert r.status.value == "BLOCKED MISSING INPUT"
        assert "leg_eccentricity_mm" in r.warnings[0]
        f2 = {k: v for k, v in FULL.items() if k != "leg_web_thickness_mm"}
        r2 = _details(_payload(f2))["leg_section_check"]
        assert r2.status.value == "BLOCKED MISSING INPUT"
        assert "leg_web_thickness_mm" in r2.warnings[0]

    def test_explicit_K_and_L_are_recorded_not_assumed(self):
        f = dict(FULL, leg_unbraced_length_mm=600.0, leg_effective_length_factor_K=1.0)
        r = _details(_payload(f))["leg_section_check"]
        assert _iv(r, "KL_over_r") == pytest.approx(1.0 * 600.0 / 23.5525, rel=1e-3)
        assert not any("serbest uçlu konsol varsayımı" in a for a in r.assumptions)


# ── (a) kaynak ────────────────────────────────────────────────────────────────

class TestWelds:
    def test_three_joints_hand_calc(self):
        """Fexx=480 → izin 0.30·480 = 144 MPa; z=6 → a = 4.243; N=20000, e=90, H=0.

        1) ped→gövde: b'=100−12=88, d'=200−12=188; Lw=552, Sw=88·188+188²/3=28325.3;
           V=20000, M=1.8e6: f=hypot(36.23, 63.55)=73.15 N/mm → τ=17.24 MPa (0.1197).
        2) ayak→ped (U kontur, ρ=1): b'=63, d'=188; Lw=2·63+188=314, Sw=63·188+188²/6=17734.7;
           e'=90−10=80, M=1.6e6: f=hypot(63.69, 90.22)=110.44 → τ=26.03 (0.1808).
        3) ayak→taban: Lw,Sw aynı; N=20000 normal, M=N·e=1.8e6: f_n=63.69+101.49=165.18 → τ=38.94 (0.2704).
        """
        r = _details(_payload(FULL))["leg_weld_check"]
        assert _iv(r, "pad_to_shell_Lw") == pytest.approx(552.0)
        assert _iv(r, "pad_to_shell_Sw") == pytest.approx(28325.333, rel=1e-6)
        assert _iv(r, "pad_to_shell_stress") == pytest.approx(17.2418, rel=1e-4)
        assert _iv(r, "leg_to_pad_Lw") == pytest.approx(314.0)
        assert _iv(r, "leg_to_pad_Sw") == pytest.approx(17734.667, rel=1e-6)
        assert _iv(r, "leg_to_pad_stress") == pytest.approx(26.0303, rel=1e-4)
        assert _iv(r, "leg_to_base_plate_stress") == pytest.approx(38.9357, rel=1e-4)
        assert _iv(r, "governing_joint") == "leg_to_base_plate"
        assert r.utilization_ratio == pytest.approx(0.270387, rel=1e-4)
        assert r.allowable_limit == pytest.approx(144.0)
        # asgari bacak girilmedi → yapılmadı, PASS DEĞİL
        assert r.status.value == "REVIEW REQUIRED"
        assert any("Asgari köşe kaynağı bacağı" in w and "YAPILMADI" in w for w in r.warnings)

    def test_pass_when_min_leg_given_and_ok(self):
        r = _details(_payload(dict(FULL, weld_min_leg_mm=5.0)))["leg_weld_check"]
        assert r.status.value == "PASS"
        assert not any("YAPILMADI" in w for w in r.warnings)

    def test_min_leg_violation_fails(self):
        r = _details(_payload(dict(FULL, weld_min_leg_mm=8.0)))["leg_weld_check"]
        assert r.status.value == "FAIL"
        assert any("asgari 8 mm" in w for w in r.warnings)

    def test_undersized_weld_fails(self):
        """z=1: τ = 165.19/(0.7071·1)·… ≫ 144 → FAIL (gerekli bacak raporlanır)."""
        f = dict(FULL, leg_to_base_plate_weld_leg_mm=1.0)
        r = _details(_payload(f))["leg_weld_check"]
        assert r.status.value == "FAIL"
        assert _iv(r, "leg_to_base_plate_required_leg") > 1.0
        assert r.utilization_ratio > 1.0

    def test_lateral_load_enters_base_weld(self):
        """H_toplam=4000 → 1000/ayak; M_taban = 20000·90 + 1000·800 = 2.6e6; V=1000.
        f=hypot(1000/314, 20000/314 + 2.6e6/17734.67) = 210.32 → τ = 49.57 MPa (0.3443)."""
        r = _details(_payload(FULL, lateral=4000.0))["leg_weld_check"]
        assert _iv(r, "leg_to_base_plate_stress") == pytest.approx(49.5738, rel=1e-4)

    def test_pipe_leg_uses_circle_group(self):
        """Ø100 daire: Lw = π·100 = 314.16, Sw = π·100²/4 = 7853.98; taban: f = 63.66 + 1.8e6/7853.98
        = 292.85 N/mm → τ = 69.02 (0.4793)."""
        f = dict(FULL, leg_section_type="pipe", leg_diameter_mm=100.0, leg_thickness_mm=8.0)
        for k in ("leg_profile_height_mm", "leg_profile_width_mm", "leg_web_thickness_mm", "leg_flange_thickness_mm"):
            f.pop(k)
        r = _details(_payload(f))["leg_weld_check"]
        assert _iv(r, "leg_to_base_plate_Lw") == pytest.approx(math.pi * 100.0)
        assert _iv(r, "leg_to_base_plate_stress") == pytest.approx(69.0243, rel=1e-4)

    def test_contact_ratio_scales_leg_to_pad_group(self):
        """ρ=0.5: Lw=157, Sw=8867.33 → f=hypot(127.39, 180.44)... τ = 52.06 MPa (0.3615)."""
        r = _details(_payload(dict(FULL, leg_pad_contact_ratio=0.5)))["leg_weld_check"]
        assert _iv(r, "leg_to_pad_Lw") == pytest.approx(157.0)
        assert _iv(r, "leg_to_pad_stress") == pytest.approx(52.0606, rel=1e-4)
        assert any("Temas oranı 0.5" in w for w in r.warnings)

    @pytest.mark.parametrize("drop,needle", [
        ("weld_electrode_strength_MPa", "Fexx"),
        ("leg_to_pad_weld_leg_mm", "leg_to_pad_weld_leg_mm"),
        ("leg_to_base_plate_weld_leg_mm", "leg_to_base_plate_weld_leg_mm"),
        ("pad_to_shell_weld_leg_mm", "pad_to_shell_weld_leg_mm"),
    ])
    def test_missing_inputs_blocked(self, drop, needle):
        f = {k: v for k, v in FULL.items() if k != drop}
        r = _details(_payload(f))["leg_weld_check"]
        assert r.status.value == "BLOCKED MISSING INPUT"
        assert needle in r.warnings[0]

    def test_no_pad_skips_pad_joint_with_notice(self):
        f = {k: v for k, v in FULL.items() if k not in ("leg_pad_length_mm", "leg_pad_width_mm", "pad_to_shell_weld_leg_mm")}
        r = _details(_payload(f))["leg_weld_check"]
        assert r.status.value != "BLOCKED MISSING INPUT"
        assert not any(v["name"].startswith("pad_to_shell") for v in r.intermediate_values)
        assert any("Ped tanımlı değil" in n for n in r.notices)


# ── (a) taban plakası ─────────────────────────────────────────────────────────

class TestBasePlate:
    def test_hand_calc_pass(self):
        """N=20000, L=250, W=150, U h=200 b=75, Fy=250, t=16, q_izin=8.

        q = 20000/(250·150) = 0.5333 MPa; m = (250−0.95·200)/2 = 30; n = (150−0.8·75)/2 = 45; c=45;
        t_gerekli = 45·√(3·0.5333/(0.75·250)) = 4.157 mm → oran 4.157/16 = 0.2598; yataklık 0.0667.
        """
        r = _details(_payload(FULL))["base_plate_check"]
        assert _iv(r, "bearing_pressure_q") == pytest.approx(20000.0 / 37500.0)
        assert _iv(r, "cantilever_m") == pytest.approx(30.0)
        assert _iv(r, "cantilever_n") == pytest.approx(45.0)
        assert _iv(r, "t_required") == pytest.approx(4.157, rel=1e-3)
        assert r.utilization_ratio == pytest.approx(4.1569 / 16.0, rel=1e-3)
        assert r.status.value == "PASS"
        assert any("leg_stress" in a and "TEKRARLANMADI" in a for a in r.assumptions)  # ankraj tek yerde

    def test_pipe_uses_080_factors(self):
        """Ø100 boru: m = (250−0.8·100)/2 = 85, n = (150−80)/2 = 35 → c = 85."""
        f = dict(FULL, leg_section_type="pipe", leg_diameter_mm=100.0, leg_thickness_mm=8.0)
        r = _details(_payload(f))["base_plate_check"]
        assert _iv(r, "cantilever_m") == pytest.approx(85.0)
        assert _iv(r, "cantilever_c") == pytest.approx(85.0)

    def test_foundation_allowable_missing_is_review_not_pass(self):
        f = {k: v for k, v in FULL.items() if k != "foundation_bearing_allowable_MPa"}
        r = _details(_payload(f))["base_plate_check"]
        assert r.status.value == "REVIEW REQUIRED"
        assert any("KONTROL EDİLMEDİ" in w for w in r.warnings)

    def test_thin_plate_fails(self):
        r = _details(_payload(dict(FULL, base_plate_thickness_mm=4.0)))["base_plate_check"]
        assert r.status.value == "FAIL"  # 4.157 > 4.0
        assert r.utilization_ratio == pytest.approx(4.1569 / 4.0, rel=1e-3)

    def test_bearing_over_allowable_fails(self):
        r = _details(_payload(dict(FULL, foundation_bearing_allowable_MPa=0.4)))["base_plate_check"]
        assert r.status.value == "FAIL"  # 0.5333 > 0.4
        assert any("yataklık" in w for w in r.warnings)

    def test_missing_dims_and_thickness(self):
        f = {k: v for k, v in FULL.items() if k not in ("base_plate_length_mm",)}
        r = _details(_payload(dict(f, base_plate_area_mm2=37500.0)))["base_plate_check"]
        assert r.status.value == "BLOCKED MISSING INPUT" and "yeterli değil" in r.warnings[0]
        f2 = {k: v for k, v in FULL.items() if k not in ("base_plate_yield_MPa", "base_plate_thickness_mm")}
        r2 = _details(_payload(f2))["base_plate_check"]
        assert r2.status.value == "BLOCKED MISSING INPUT"
        assert "base_plate_yield_MPa" in r2.warnings[0] and "base_plate_thickness_mm" in r2.warnings[0]

    def test_profile_larger_than_plate_not_calculated(self):
        r = _details(_payload(dict(FULL, base_plate_length_mm=150.0)))["base_plate_check"]
        assert r.status.value == "NOT CALCULATED"


# ── (a) WRC lokal gerilme ─────────────────────────────────────────────────────

WRC_VL = (0.1, 0.2, 0.05, 0.03)
WRC_ML = (0.4, 0.3, 0.06, 0.02)


class TestWrcLocal:
    def test_missing_coefficients_blocked_with_counts(self):
        r = _details(_payload(FULL))["wrc_local_stress"]
        assert r.status.value == "BLOCKED CODE DATA"
        # aktif yükler VL ve ML: 4 nokta × 2 yük × 4 bileşen = 32 değer
        assert "32 bileşen" in r.warnings[0] and "VL, ML" in r.warnings[0]
        assert "K6" in r.warnings[0] or "İÇERMEZ" in r.warnings[0]

    def test_partial_coefficients_still_blocked(self):
        coeffs = _uniform_coeffs({"VL": WRC_VL, "ML": WRC_ML})
        coeffs["C"]["ML"] = WrcCoefficientEntry(Nx=0.4, Ny=None, Mx=0.06, My=0.02)
        f = dict(FULL, wrc_coefficients=coeffs)
        r = _details(_payload(f))["wrc_local_stress"]
        assert r.status.value == "BLOCKED CODE DATA"
        assert "1 bileşen" in r.warnings[0] and "C/ML: Ny" in r.warnings[0]

    def test_hand_calc_all_points(self):
        """VL = N = 20000, ML = N·e = 1.8e6; Rm=506, T=12; tüm noktalarda aynı katsayılar:
        VL(Nx .1, Ny .2, Mx .05, My .03), ML(Nx .4, Ny .3, Mx .06, My .02).

        Nx = .1·20000/506 + .4·1.8e6/506² = 6.7647; Ny = 10.0142;
        Mx = .05·20000 + .06·1.8e6/506 = 1213.44; My = 671.15 N·mm/mm.
        Basınç: σL = 1.2·506/24 = 25.3; σc = 50.6. Dış yüzey: σx = 6.7647/12 + 6·1213.44/144 + 25.3
        = 76.424; σy = 79.399 → SI = √(σx²−σxσy+σy²) = 77.954. İç yüzey: σx=−24.696, σy=23.470 → 41.718.
        PL (yalnız membran+basın): σx=25.864, σy=51.435 → 44.544. Sınır 1.5·138 = 207 MPa.
        """
        f = dict(FULL, wrc_coefficients=_uniform_coeffs({"VL": WRC_VL, "ML": WRC_ML}))
        r = _details(_payload(f))["wrc_local_stress"]
        assert r.status.value == "REVIEW REQUIRED"
        assert _iv(r, "A_outside_membrane_axial") == pytest.approx(6.76467 / 12.0, rel=1e-4)
        assert _iv(r, "A_outside_bending_axial") == pytest.approx(6 * 1213.4387 / 144.0, rel=1e-4)
        assert _iv(r, "A_outside_PL_Pb") == pytest.approx(77.9539, rel=1e-4)
        assert _iv(r, "A_inside_PL_Pb") == pytest.approx(41.7178, rel=1e-4)
        assert _iv(r, "A_outside_PL") == pytest.approx(44.5438, rel=1e-4)
        assert r.final_result == pytest.approx(77.9539, rel=1e-4)
        assert r.allowable_limit == pytest.approx(207.0)
        assert r.utilization_ratio == pytest.approx(77.9539 / 207.0, rel=1e-4)
        assert _iv(r, "gamma") == pytest.approx(506.0 / 12.0)
        assert _iv(r, "beta_longitudinal") == pytest.approx(100.0 / 506.0)   # C = pad boyu/2 = 100
        assert _iv(r, "beta_circumferential") == pytest.approx(50.0 / 506.0)  # C = pad eni/2 = 50
        assert any("Ped gövde kalınlığına EKLENMEDİ" in a for a in r.assumptions)

    def test_exceeding_limit_fails(self):
        big = _uniform_coeffs({"VL": (50.0, 50.0, 50.0, 50.0), "ML": (50.0, 50.0, 50.0, 50.0)})
        r = _details(_payload(dict(FULL, wrc_coefficients=big)))["wrc_local_stress"]
        assert r.status.value == "FAIL"
        assert r.utilization_ratio > 1.0

    def test_lateral_load_activates_radial_and_circumferential_loads(self):
        """H=4000/4 = 1000 → P=1000, VC=1000, MC=90000: coeffs eksikse P, VC, MC de istenir."""
        f = dict(FULL, wrc_coefficients=_uniform_coeffs({"VL": WRC_VL, "ML": WRC_ML}))
        r = _details(_payload(f, lateral=4000.0))["wrc_local_stress"]
        assert r.status.value == "BLOCKED CODE DATA"
        assert "VL, ML, P, VC, MC" in r.warnings[0] or all(k in r.warnings[0] for k in ("P", "VC", "MC"))
        assert _iv(r, "load_MC") == pytest.approx(1000.0 * 90.0)

    @pytest.mark.parametrize("fields,host", [({"leg_attachment": "bottom_head"}, "shell"), ({}, "head")])
    def test_bottom_head_or_head_host_out_of_scope(self, fields, host):
        r = _details(_payload(dict(FULL, **fields), host_type=host))["wrc_local_stress"]
        assert r.status.value == "OUT OF SCOPE"

    def test_missing_pad_blocked(self):
        f = {k: v for k, v in FULL.items() if k not in ("leg_pad_length_mm", "leg_pad_width_mm")}
        r = _details(_payload(f))["wrc_local_stress"]
        assert r.status.value == "BLOCKED MISSING INPUT" and "leg_pad" in r.warnings[0]


# ── ön koşullar ve özet ───────────────────────────────────────────────────────

class TestPreconditionsAndSummary:
    def test_empty_when_section_type_blank(self):
        assert SupportCalculator().check_leg_detail(_payload({"leg_diameter_mm": 100.0})) == []

    def test_single_leg_not_calculated_everywhere(self):
        out = SupportCalculator().check_leg_detail(_payload(FULL, n=1))
        assert [r.calculation_type for r in out] == list(leg_detail.LEG_DETAIL_TYPES)
        assert all(r.status.value == "NOT CALCULATED" for r in out)
        assert "tek ayak" in out[0].warnings[0]

    def test_summary_never_final_pass_and_lists_subchecks(self):
        calc = SupportCalculator()
        payload = _payload(dict(FULL, weld_min_leg_mm=5.0, leg_diameter_mm=None))
        leg = calc.check_leg_support(payload)
        details = calc.check_leg_detail(payload)
        calc.summarize_leg(leg, details)
        assert leg.status.value == "REVIEW REQUIRED"
        assert "leg_section_check=PASS" in _iv(leg, "leg_subchecks")
        assert "wrc_local_stress=BLOCKED CODE DATA" in _iv(leg, "leg_subchecks")
        assert any("nihai PASS verilmez" in a for a in leg.assumptions)

    def test_summary_propagates_fail(self):
        calc = SupportCalculator()
        payload = _payload(dict(FULL, base_plate_thickness_mm=4.0))
        leg = calc.check_leg_support(payload)
        calc.summarize_leg(leg, calc.check_leg_detail(payload))
        assert leg.status.value == "FAIL"
        assert any("base_plate_check" in w for w in leg.warnings)

    def test_leg_stress_uses_channel_area_not_pipe(self):
        """Kanal ayakta leg_stress D/t istemez ve A = 2442 mm² kullanır: P_base = 20000/2442 = 8.19 MPa."""
        leg = SupportCalculator().check_leg_support(_payload(FULL))
        assert leg.status.value != "NOT CALCULATED", leg.warnings
        assert _iv(leg, "A_leg") == pytest.approx(2442.0)
        assert _iv(leg, "P_base") == pytest.approx(20000.0 / 2442.0, rel=1e-6)

    def test_anchor_bolt_diameter_unused_warning(self):
        leg = SupportCalculator().check_leg_support(
            _payload(dict(FULL, anchor_bolt_diameter_mm=24.0)))
        assert any("KULLANILMADI" in w for w in leg.warnings)
        leg2 = SupportCalculator().check_leg_support(_payload(FULL))
        assert not any("KULLANILMADI" in w for w in leg2.warnings)

    def test_single_leg_message_mentions_scope(self):
        leg = SupportCalculator().check_leg_support(_payload(FULL, n=1))
        assert leg.status.value == "NOT CALCULATED"
        assert "At least 2 legs" in leg.warnings[0] and "kapsam dışı" in leg.warnings[0]


# ── (d) üretim yolu: VesselProject → orkestratör → sonuç ──────────────────────

def _project(supports):
    return VesselProject(
        project_number="LEG-DET", project_name="Leg detail", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=_dc(),
        heads=[Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0, nominal_thickness=12.0, material_id="MAT-01"),
               Head(head_id="HR", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0, nominal_thickness=12.0, material_id="MAT-01")],
        shell_sections=[_shell()], materials=[_mat()], supports=supports,
        component_sequence=[ComponentReference(component_type="head", component_id="HL"),
                            ComponentReference(component_type="shell", component_id="S1"),
                            ComponentReference(component_type="head", component_id="HR")],
    )


def _leg_support(**kw):
    base = dict(support_id="LG", type="leg", host_component_id="S1", location_mm=0.0, width_mm=200.0,
                height_mm=800.0, material_id="MAT-01", leg_count=4, support_radius_mm=520.0)
    base.update(kw)
    return Support(**base)


class TestProductionPath:
    def test_u_profile_four_legs_yields_five_results(self):
        sup = _leg_support(**FULL)
        res = ASMEVIII1DesignCode().check_supports(_project([sup]))
        assert [r.calculation_type for r in res] == ["leg_stress", *leg_detail.LEG_DETAIL_TYPES]
        by = {r.calculation_type: r for r in res}
        assert by["leg_section_check"].status.value == "PASS"
        assert by["leg_weld_check"].status.value == "REVIEW REQUIRED"      # asgari bacak girilmedi
        assert by["base_plate_check"].status.value == "PASS"
        assert by["wrc_local_stress"].status.value == "BLOCKED CODE DATA"   # katsayı yok
        assert by["leg_stress"].status.value == "REVIEW REQUIRED"
        assert "leg_section_check=PASS" in _iv(by["leg_stress"], "leg_subchecks")
        # yük zinciri: leg_stress ve alt kontroller AYNI N_max'ı görür
        assert _iv(by["leg_section_check"], "N_max") == pytest.approx(_iv(by["leg_stress"], "N_max"))
        assert _iv(by["leg_stress"], "host_component_id") == "S1"

    def test_u_profile_with_wrc_coefficients_gives_real_result(self):
        f = dict(FULL, weld_min_leg_mm=5.0, wrc_coefficients=_uniform_coeffs({"VL": WRC_VL, "ML": WRC_ML}))
        res = ASMEVIII1DesignCode().check_supports(_project([_leg_support(**f)]))
        by = {r.calculation_type: r for r in res}
        assert by["wrc_local_stress"].status.value == "REVIEW REQUIRED"
        assert by["wrc_local_stress"].final_result is not None
        assert by["leg_weld_check"].status.value == "PASS"
        assert by["leg_stress"].status.value == "REVIEW REQUIRED"   # dördü de geçse bile nihai PASS yok
        # JSON'a serileştirilebilir (inf/NaN yok)
        import json
        json.dumps([r.to_dict() for r in res])

    def test_pipe_example_via_section_type(self):
        f = dict(FULL, leg_section_type="pipe", leg_diameter_mm=100.0, leg_thickness_mm=8.0)
        for k in ("leg_profile_height_mm", "leg_profile_width_mm", "leg_web_thickness_mm", "leg_flange_thickness_mm"):
            f.pop(k)
        res = ASMEVIII1DesignCode().check_supports(_project([_leg_support(**f)]))
        assert len(res) == 5
        assert res[1].status.value == "PASS"

    def test_backward_compat_no_section_type_only_leg_stress(self):
        sup = _leg_support(leg_diameter_mm=100.0, leg_thickness_mm=8.0)
        res = ASMEVIII1DesignCode().check_supports(_project([sup]))
        assert [r.calculation_type for r in res] == ["leg_stress"]
        assert res[0].status.value == "REVIEW REQUIRED"
        assert not any("ÇALIŞTIRILMADI" in w for w in res[0].warnings)

    def test_new_fields_without_section_type_warn(self):
        sup = _leg_support(leg_diameter_mm=100.0, leg_thickness_mm=8.0, weld_electrode_strength_MPa=480.0)
        res = ASMEVIII1DesignCode().check_supports(_project([sup]))
        assert len(res) == 1
        assert any("ÇALIŞTIRILMADI" in w for w in res[0].warnings)

    def test_legacy_pad_fields_alone_do_not_warn(self):
        sup = _leg_support(leg_diameter_mm=100.0, leg_thickness_mm=8.0, leg_pad_length_mm=200.0)
        res = ASMEVIII1DesignCode().check_supports(_project([sup]))
        assert not any("ÇALIŞTIRILMADI" in w for w in res[0].warnings)


# ── domain doğrulayıcıları ────────────────────────────────────────────────────

class TestDomain:
    def test_new_fields_default_none_and_backward_compatible(self):
        s = _leg_support(leg_diameter_mm=100.0, leg_thickness_mm=8.0)
        for name in ("leg_attachment", "leg_section_type", "leg_eccentricity_mm", "base_plate_length_mm",
                     "weld_electrode_strength_MPa", "wrc_coefficients", "leg_pad_contact_ratio"):
            assert getattr(s, name) is None

    @pytest.mark.parametrize("kw", [
        {"leg_section_type": "tee"}, {"leg_attachment": "top"}, {"leg_pad_contact_ratio": 1.5},
        {"leg_profile_height_mm": 0.0}, {"base_plate_yield_MPa": -1.0}, {"leg_eccentricity_mm": -5.0},
    ])
    def test_invalid_values_rejected(self, kw):
        with pytest.raises(ValidationError):
            _leg_support(**kw)

    def test_wrc_keys_validated_and_round_trip(self):
        with pytest.raises(ValidationError):
            _leg_support(wrc_coefficients={"E": {"P": WrcCoefficientEntry()}})
        with pytest.raises(ValidationError):
            _leg_support(wrc_coefficients={"A": {"XX": WrcCoefficientEntry()}})
        s = _leg_support(wrc_coefficients={"A": {"VL": {"Nx": 1.0, "Ny": None, "Mx": 2.0, "My": 3.0}}})
        again = Support.model_validate(s.model_dump())
        assert again.wrc_coefficients["A"]["VL"].Nx == 1.0 and again.wrc_coefficients["A"]["VL"].Ny is None


# ── formül modülü yeni eklemeleri ─────────────────────────────────────────────

class TestNewFormulaHelpers:
    def test_weld_group_circle_and_channel(self):
        from welds import strength
        c = strength.weld_group_circle(100.0)
        assert (c.L_w, c.S_w) == pytest.approx((math.pi * 100.0, math.pi * 2500.0))
        # C kontur: b=63, d=188 → Lw = 314, Sw = 63·188 + 188²/6 (Iw = 2b(d/2)² + d³/12 ile bağımsız kontrol)
        g = strength.weld_group_channel(63.0, 188.0)
        Iw = 2 * 63.0 * 94.0**2 + 188.0**3 / 12.0
        assert g.L_w == pytest.approx(314.0)
        assert g.S_w == pytest.approx(Iw / 94.0)
        s = strength.scale_weld_group(g, 0.5)
        assert (s.L_w, s.S_w) == pytest.approx((157.0, g.S_w / 2))
        with pytest.raises(ValueError):
            strength.scale_weld_group(g, 0.0)

    def test_leg_load_helpers(self):
        from supports import formulas
        assert formulas.leg_lateral_load_per_leg(4000.0, 4) == 1000.0
        assert formulas.leg_eccentric_moment(20000.0, 90.0) == 1.8e6
        assert formulas.leg_base_moment(20000.0, 90.0, 1000.0, 800.0) == 2.6e6
        with pytest.raises(ValueError):
            formulas.leg_base_moment(1.0, 1.0, 1.0, 0.0)
