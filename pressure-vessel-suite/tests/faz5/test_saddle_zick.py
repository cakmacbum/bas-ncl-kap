"""Eyer (saddle) Zick analizi — yapı, katsayı politikası (K6) ve kapsam kapıları.

Kaynak yapı: L.P. Zick (1951), Moss PVDM Prosedür 3-10, Megyesy. Sayısal beklentiler
formülden BAĞIMSIZ el hesabıdır (adımlar docstring'lerde). K1/K2/K3/K6/K7 değerleri
burada yalnızca GİRDİ olarak verilen, tablodan okunmamış örnek sayılardır (program K
tablosu içermez); yayımlanmış çözümlü örnek sayıları bu ortamdan alınamadığı için
testler Zick statik yapısının sınır durumlarıyla ve el hesabıyla doğrulanır.
"""

import math

import pytest

from calc_core.result import CalculationStatus
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
)
from supports import formulas as F
from supports.support_calc import SupportCalculator

# Ortak örnek: R = 1000, t = 10, L = 6000, A = 1200, H = 500, b = 300, Q = 250 kN
Q, L, R, T, A, H, B = 250000.0, 6000.0, 1000.0, 10.0, 1200.0, 500.0, 300.0


def _mat(S=138.0, Sy=260.0):
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=S, yield_strength=Sy,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4",
    )


def _shell():
    # Di = 1990, t = 10, CA = 0 → R_m = 995 + 5 = 1000
    return ShellSection(
        section_id="S1", inside_diameter=1990.0, tangent_length=L,
        nominal_thickness=T, material_id="MAT-01",
    )


def _dc(P=1.0):
    return DesignConditions(
        operating_pressure=P, design_pressure=P, maximum_allowable_pressure_ps=P * 1.25,
        operating_temperature=200.0, design_temperature=200.0, minimum_design_temperature=-10.0,
    )


def _payload(x_self=2200.0, positions=(2200.0, 5800.0), W=500000.0, sup=None, **over):
    support = {
        "tag": "SAD-1", "location_mm": x_self, "width_mm": B, "contact_angle_deg": 120.0,
        "saddle_stiffened": False, "zick_K1": 0.1, "zick_K2": 1.2, "zick_K6": 0.02, "zick_K7": 0.7,
    }
    support.update(sup or {})
    data = {
        "support": support, "shell": _shell(), "vessel_length": L, "tangent_start_mm": 1000.0,
        "saddle_positions_mm": list(positions), "head_depth_mm": H, "head_thickness_mm": 10.0,
        "joint_efficiency": 1.0, "total_weight_N": W, "weight_case": "test",
        "materials": [_mat()], "design_conditions": _dc(),
    }
    data.update(over)
    return data


def _iv(result, name):
    return next(v["value"] for v in result.intermediate_values if v["name"] == name)


# ── Formül yapısı (el hesabı) ────────────────────────────────────────────────

class TestZickFormulas:
    def test_M1_hand_calc(self):
        """M1 = Q·A·[1 − (1 − A/L + (R²−H²)/(2AL))/(1 + 4H/3L)]

        A/L = 0,2; R²−H² = 750 000; 2AL = 14,4e6 → 0,0520833
        pay = 1 − 0,2 + 0,0520833 = 0,8520833; payda = 1 + 2000/18000 = 1,1111111
        oran = 0,766875 → 1 − 0,766875 = 0,233125
        M1 = 250 000 · 1200 · 0,233125 = 69 937 500 N·mm
        Kapalı form kontrolü: Q(8AH + 6A² − 3R² + 3H²)/(2(3L+4H)) = 250000·11,19e6/40000.
        """
        assert F.zick_moment_saddle(Q, L, R, A, H) == pytest.approx(69_937_500.0, rel=1e-9)
        closed = Q * (8 * A * H + 6 * A**2 - 3 * R**2 + 3 * H**2) / (2 * (3 * L + 4 * H))
        assert closed == pytest.approx(69_937_500.0, rel=1e-9)

    def test_M2_hand_calc(self):
        """M2 = (QL/4)[(1 + 2(R²−H²)/L²)/(1 + 4H/3L) − 4A/L]

        QL/4 = 3,75e8·... = 250000·6000/4 = 3,75e8 (N·mm)
        (1 + 1,5e6/36e6) = 1,0416667; /1,1111111 = 0,9375; − 0,8 = 0,1375
        M2 = 3,75e8 · 0,1375 = 51 562 500 N·mm
        """
        assert F.zick_moment_midspan(Q, L, R, A, H) == pytest.approx(51_562_500.0, rel=1e-9)

    def test_moments_reduce_to_simple_beam_statics(self):
        """H = 0, R → 0: iki uçtan A taşan basit kiriş, toplam yük 2Q üniform.

        M1 = w·A²/2 = (2Q/L)·A²/2 = Q·A²/L ;  M2 = Q·L/4 − Q·A
        """
        M1 = F.zick_moment_saddle(Q, L, 1e-9, A, 0.0)
        M2 = F.zick_moment_midspan(Q, L, 1e-9, A, 0.0)
        assert M1 == pytest.approx(Q * A**2 / L, rel=1e-9)
        assert M2 == pytest.approx(Q * L / 4 - Q * A, rel=1e-9)

    def test_longitudinal_stresses(self):
        """K1 = 0,1: S1 = 69 937 500/(0,1·1000²·10) = 69,9375 MPa; orta: M2/(π R² t) = 1,6413 MPa;
        P = 1,0 → P·R/2t = 50 MPa."""
        assert F.zick_longitudinal_stress_saddle(69_937_500.0, 0.1, R, T) == pytest.approx(69.9375)
        assert F.zick_longitudinal_stress_midspan(51_562_500.0, R, T) == pytest.approx(
            51_562_500.0 / (math.pi * 1e7)
        )
        assert F.zick_pressure_longitudinal(1.0, R, T) == pytest.approx(50.0)

    def test_circumferential_and_shear(self):
        """eff = 300 + 1,56·√(1000·10) = 456,0 → membran = 250000/(4·10·456) = 13,706 MPa.
        L = 6000 < 8R = 8000 → eğilme = 3·K6·Q/(2t²) = 3·0,02·250000/200 = 75 MPa.
        L ≥ 8R (L = 9000): 12·K6·Q·R/(L t²) = 12·0,02·250000·1000/(9000·100) = 66,667 MPa.
        S5 = K7·Q/(t·eff) = 0,7·250000/4560 = 38,377 MPa.
        S2 = K2·Q/(R t)·(L−2A)/(L+4H/3) = 1,2·25·(3600/6666,667) = 16,2 MPa.
        S2 (A ≤ R/2, halkasız) = K2·Q/(R t) = 30 MPa.  S3 = K3·Q/(R t_h) = 0,4·25 = 10 MPa.
        """
        eff = 300 + 1.56 * math.sqrt(1000 * 10)
        assert F.zick_effective_width(B, R, T) == pytest.approx(eff)
        memb = 250000 / (4 * 10 * eff)
        assert F.zick_circumferential_membrane(Q, R, T, B) == pytest.approx(memb)
        assert F.zick_circumferential_horn(Q, R, T, B, 6000.0, 0.02) == pytest.approx(memb + 75.0)
        assert F.zick_circumferential_horn(Q, R, T, B, 9000.0, 0.02) == pytest.approx(
            memb + 12 * 0.02 * 250000 * 1000 / (9000 * 100)
        )
        assert F.zick_circumferential_bottom(Q, R, T, B, 0.7) == pytest.approx(0.7 * 250000 / (10 * eff))
        assert F.zick_shear_shell(Q, R, T, L, A, H, 1.2) == pytest.approx(16.2)
        assert F.zick_shear_shell(Q, R, T, L, A, H, 1.2, head_stiffened=True) == pytest.approx(30.0)
        assert F.zick_shear_head(Q, R, T, 0.4) == pytest.approx(10.0)

    def test_limits_are_separate_per_check(self):
        """S1 çekme S·E; S1 basma 0,5Sy; kabuk kesme 0,8S; başlık 1,25S; boynuz 1,5S; taban 0,5Sy."""
        lim = F.saddle_stress_limits(138.0, 260.0, 0.85)
        assert lim == pytest.approx({
            "S1_tension": 138.0 * 0.85, "S1_compression": 130.0, "S2": 110.4,
            "S3": 172.5, "S4": 207.0, "S5": 130.0,
        })

    def test_two_saddle_reactions_moment_balance(self):
        """Simetri: W/2. Asimetri: cg=4000, x=(1500, 6800): Q_sol = W·(6800−4000)/5300."""
        assert F.saddle_reactions_two(500000.0, 2200.0, 6800.0, 4500.0) == pytest.approx((250000.0, 250000.0))
        ql, qr = F.saddle_reactions_two(500000.0, 1500.0, 6800.0, 4000.0)
        assert ql == pytest.approx(500000.0 * 2800.0 / 5300.0)
        assert ql + qr == pytest.approx(500000.0)

    def test_head_depth_from_head_type(self):
        def head(kind, **kw):
            return Head(head_id="H", type=kind, inside_diameter=2000.0, nominal_thickness=10.0,
                        material_id="MAT-01", **kw)
        assert F.zick_head_depth(head(HeadType.ELLIPTICAL)) == pytest.approx(500.0)
        assert F.zick_head_depth(head(HeadType.ELLIPTICAL, crown_depth=480.0)) == 480.0
        assert F.zick_head_depth(head(HeadType.HEMISPHERICAL)) == pytest.approx(1000.0)
        assert F.zick_head_depth(head(HeadType.FLAT)) == 0.0
        # Standart F&D: Rc = D = 2000, rk = 120 → h = 2000 − √(1880² − 880²)
        assert F.zick_head_depth(head(HeadType.TORISPHERICAL)) == pytest.approx(
            2000 - math.sqrt(1880**2 - 880**2)
        )


# ── check_saddle: durum ve kapsam kapıları ───────────────────────────────────

class TestCheckSaddle:
    calc = SupportCalculator()

    def test_full_numeric_review_required(self):
        """Simetrik iki eyer, W = 500 kN → Q = 250 kN (moment dengesi). K1=0,1 K2=1,2 K6=0,02 K7=0,7.

        R_m = 995 + 5 = 1000, t = 10, A = 1200 (> R/2 → başlık desteği yok).
        S1 çekme = 69,9375 + 50 = 119,9375 (sınır 138) → oran 0,8691 (kılavuz)
        S2 = 16,2 ; S4 = 13,706 + 75 = 88,706 ; S5 = 38,377 (sınır 130).
        """
        r = self.calc.check_saddle(_payload())
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert _iv(r, "Q") == pytest.approx(250000.0)
        assert _iv(r, "M1") == pytest.approx(69_937_500.0, rel=1e-9)
        assert _iv(r, "M2") == pytest.approx(51_562_500.0, rel=1e-9)
        assert _iv(r, "S1_saddle") == pytest.approx(69.9375)
        assert _iv(r, "S1_tension") == pytest.approx(69.9375 + 50.0)
        assert _iv(r, "S2") == pytest.approx(16.2)
        assert _iv(r, "S4_membrane") == pytest.approx(13.7061, rel=1e-4)
        assert _iv(r, "S4") == pytest.approx(13.7061 + 75.0, rel=1e-4)
        assert _iv(r, "S5") == pytest.approx(38.3772, rel=1e-4)
        # Her kontrol kendi sınırıyla: tek 0,67·S yok
        assert _iv(r, "S4_limit") == pytest.approx(207.0)
        assert _iv(r, "S2_limit") == pytest.approx(110.4)
        assert _iv(r, "S1_tension_ratio") == pytest.approx(119.9375 / 138.0)
        assert r.utilization_ratio == pytest.approx(119.9375 / 138.0)
        assert _iv(r, "governing_check") == "S1_tension"
        assert "Zick" in r.formula_reference

    def test_fail_when_a_check_exceeds_its_own_limit(self):
        r = self.calc.check_saddle(_payload(W=5_000_000.0))
        assert r.status == CalculationStatus.FAIL
        assert r.utilization_ratio > 1.0

    def test_never_pass_even_with_low_load(self):
        r = self.calc.check_saddle(_payload(W=20000.0))
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert r.status != CalculationStatus.PASS

    def test_missing_k_is_blocked_code_data_with_structural_values(self):
        r = self.calc.check_saddle(_payload(sup={"zick_K6": None, "zick_K7": None}))
        assert r.status == CalculationStatus.BLOCKED_CODE_DATA
        msg = " ".join(r.warnings + r.notices)
        assert "zick_K6" in msg and "zick_K7" in msg and "zick_K1" not in msg
        assert "İÇERMEZ" in msg
        # Katsayısız yapısal ara değerler yine de raporlanır
        assert _iv(r, "M1") == pytest.approx(69_937_500.0, rel=1e-9)
        assert _iv(r, "S4_membrane") > 0
        assert r.final_result is None

    @pytest.mark.parametrize("key,value", [
        ("head_depth_mm", None), ("tangent_start_mm", None), ("saddle_positions_mm", None),
    ])
    def test_missing_geometry_is_blocked_missing_input_no_silent_default(self, key, value):
        data = _payload()
        data.pop(key) if value is None else data.update({key: value})
        r = self.calc.check_saddle(data)
        assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT

    def test_ring_choice_must_be_declared(self):
        r = self.calc.check_saddle(_payload(sup={"saddle_stiffened": None}))
        assert r.status == CalculationStatus.BLOCKED_MISSING_INPUT

    def test_three_saddles_out_of_scope(self):
        r = self.calc.check_saddle(_payload(positions=(2200.0, 4000.0, 5800.0)))
        assert r.status == CalculationStatus.OUT_OF_SCOPE

    def test_single_saddle_not_calculated(self):
        r = self.calc.check_saddle(_payload(positions=(2200.0,)))
        assert r.status == CalculationStatus.NOT_CALCULATED

    def test_asymmetric_saddles_use_moment_balance_and_both_A(self):
        """x = 1800 ve 6300 (A_sol = 800, A_sağ = 700), cg = 4000 → Q_sol = W·2300/4500."""
        pos = (1800.0, 6300.0)
        left = self.calc.check_saddle(_payload(x_self=1800.0, positions=pos))
        right = self.calc.check_saddle(_payload(x_self=6300.0, positions=pos))
        assert _iv(left, "A") == pytest.approx(800.0)
        assert _iv(right, "A") == pytest.approx(700.0)
        assert _iv(left, "A_left") == pytest.approx(800.0) == pytest.approx(_iv(right, "A_left"))
        assert _iv(left, "Q") == pytest.approx(500000.0 * 2300.0 / 4500.0)
        assert _iv(left, "Q") + _iv(right, "Q") == pytest.approx(500000.0)
        assert _iv(left, "Q") != pytest.approx(250000.0)
        assert any("Asimetrik" in w for w in left.warnings)

    def test_head_stiffened_uses_pi_for_K1_and_needs_K3(self):
        """A = 400 ≤ R/2 = 500 (halkasız): K1 = π; K3 (başlık kesmesi) zorunlu; S2 L-çarpanı yok."""
        pos = (1400.0, 6600.0)
        data = _payload(x_self=1400.0, positions=pos, sup={"zick_K1": None})
        r = self.calc.check_saddle(data)
        assert r.status == CalculationStatus.BLOCKED_CODE_DATA and "zick_K3" in " ".join(r.warnings)
        data = _payload(x_self=1400.0, positions=pos, sup={"zick_K1": None, "zick_K3": 0.4})
        r = self.calc.check_saddle(data)
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert _iv(r, "K1") == pytest.approx(math.pi)
        assert _iv(r, "S3") == pytest.approx(0.4 * 250000 / (1000 * 10))   # 10 MPa
        assert _iv(r, "S2") == pytest.approx(1.2 * 250000 / (1000 * 10))    # 30 MPa
        assert _iv(r, "S3_limit") == pytest.approx(1.25 * 138.0)

    def test_ring_stiffened_constants_and_no_horn_check(self):
        r = self.calc.check_saddle(_payload(sup={
            "saddle_stiffened": True, "zick_K1": None, "zick_K2": None, "zick_K6": None,
        }))
        assert r.status == CalculationStatus.REVIEW_REQUIRED
        assert _iv(r, "K1") == pytest.approx(math.pi)
        assert _iv(r, "K2") == pytest.approx(1 / math.pi)
        assert not any(v["name"] == "S4" for v in r.intermediate_values)
        assert any("Halkalı" in w for w in r.warnings)

    def test_weight_case_is_reported(self):
        r = self.calc.check_saddle(_payload())
        assert any("test" in a and "500000" in a for a in r.assumptions)


# ── Orkestratör: H, L, A iki uç, ≥3 eyer ─────────────────────────────────────

def _project(saddles, n_heads=2):
    mat = _mat()
    return VesselProject(
        project_number="SAD-ORCH", project_name="Saddle orchestration",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=_dc(),
        heads=[
            Head(head_id="HL", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
            Head(head_id="HR", type=HeadType.ELLIPTICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
        ],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0, tangent_length=2000.0,
                                     nominal_thickness=12.0, material_id="MAT-01")],
        component_sequence=[
            ComponentReference(component_type="head", component_id="HL"),
            ComponentReference(component_type="shell", component_id="S1"),
            ComponentReference(component_type="head", component_id="HR"),
        ],
        materials=[mat], supports=saddles,
    )


def _sad(sid, loc, **kw):
    base = dict(support_id=sid, type="saddle", host_component_id="S1", location_mm=loc,
                width_mm=200.0, height_mm=300.0, material_id="MAT-01", contact_angle_deg=120.0,
                saddle_stiffened=False, zick_K1=0.1, zick_K2=1.2, zick_K6=0.02, zick_K7=0.7)
    base.update(kw)
    return Support(**base)


class TestOrchestration:
    def test_H_L_A_derived_from_project(self):
        """Eliptik 2:1 başlık D=1000 → H = 250. Zincir: HL = 250+25 = 275 → tangent_start = 275.
        Eyerler 675 ve 1875 (A = 400 / 1875→ end 2275 − 1875 = 400); L = 2000."""
        p = _project([_sad("A", 675.0), _sad("B", 1875.0)])
        res = ASMEVIII1DesignCode().check_supports(p)
        assert len(res) == 2
        r = res[0]
        assert r.status in (CalculationStatus.REVIEW_REQUIRED, CalculationStatus.FAIL), r.warnings
        assert _iv(r, "H") == pytest.approx(250.0)
        assert _iv(r, "L") == pytest.approx(2000.0)
        assert _iv(r, "A_left") == pytest.approx(400.0)
        assert _iv(r, "A_right") == pytest.approx(400.0)
        assert r.input_snapshot["Q_left_N"] == pytest.approx(r.input_snapshot["Q_right_N"])

    def test_three_saddles_out_of_scope_through_orchestrator(self):
        p = _project([_sad("A", 675.0), _sad("B", 1275.0), _sad("C", 1875.0)])
        assert all(r.status == CalculationStatus.OUT_OF_SCOPE for r in ASMEVIII1DesignCode().check_supports(p))

    def test_missing_K_through_orchestrator_is_blocked(self):
        p = _project([_sad("A", 675.0, zick_K6=None), _sad("B", 1875.0, zick_K6=None)])
        assert all(r.status == CalculationStatus.BLOCKED_CODE_DATA for r in ASMEVIII1DesignCode().check_supports(p))
