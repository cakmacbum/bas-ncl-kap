"""El hesabı çapraz doğrulaması — ASME VIII-1 UG-27(c)(1) ve UG-32 (2:1 eliptik).

İki vaka elle (adım adım aritmetik) çözülmüş, sonra projenin mevcut
fonksiyonlarıyla kıyaslanmıştır. Tolerans: mutlak 0.001 mm.

Vaka 1 — Silindirik gövde, UG-27(c)(1) Eq. (1), çevresel gerilme:
    ID = 1800 mm → R = 900 mm, P = 2.5 MPa, S = 138 MPa, E = 1.0, C = 0
    pay     = P·R           = 2.5 × 900       = 2250
    payda   = S·E − 0.6·P   = 138 − 1.5       = 136.5
    t       = 2250 / 136.5
            = 16 + 66/136.5 (136.5 × 16 = 2184; kalan 66)
            = 16 + 0.483516 = 16.4835 mm  → 16.484 mm
    Boyuna (Eq. 2): 2250 / (2·138 + 0.4·2.5) = 2250 / 277 = 8.123 mm < 16.484
    → çevresel kritik.

Vaka 2 — 2:1 eliptik başlık, UG-32 (K = 1):
    ID = D = 2000 mm, P = 2.0 MPa, S = 138 MPa, E = 1.0, C = 0
    pay     = P·D             = 2.0 × 2000    = 4000
    payda   = 2·S·E − 0.2·P   = 276 − 0.4     = 275.6
    t       = 4000 / 275.6
            = 14 + 141.6/275.6 (275.6 × 14 = 3858.4; kalan 141.6)
            = 14 + 0.513788 = 14.5138 mm  → 14.514 mm

Uçtan uca testlerde korozyon 0 alınır ve `t_required` ara değeri okunur;
`final_result` mill toleransı + korozyon payı içerdiği için kıyaslanmaz.
"""

import pytest

from domain import (
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    WeldJoint,
)
from code_asme_viii_1 import ASMEVIII1DesignCode
from code_asme_viii_1.formulas import (
    head_elliptical_thickness,
    shell_thickness_internal_pressure,
)

ABS_TOL_MM = 1e-3

T_SHELL_HAND = 16.484  # 2250 / 136.5
T_HEAD_HAND = 14.514   # 4000 / 275.6


def _intermediate(result, name):
    """CalculationResult.intermediate_values içinden ada göre değer oku."""
    for iv in result.intermediate_values:
        if iv.get("name") == name:
            return iv["value"]
    raise AssertionError(
        f"'{name}' ara değeri yok; status={getattr(result, 'status', None)}, "
        f"mevcut={[iv.get('name') for iv in result.intermediate_values]}"
    )


def _design_conditions(pressure):
    return DesignConditions(
        operating_pressure=pressure * 0.8,
        design_pressure=pressure,
        maximum_allowable_pressure_ps=pressure,
        operating_temperature=150.0,
        design_temperature=200.0,
        minimum_design_temperature=-10.0,
        corrosion_allowance_internal=0.0,
        hydrotest_temperature=20.0,
    )


@pytest.fixture
def asme_code():
    return ASMEVIII1DesignCode(edition="2025")


@pytest.fixture
def material():
    return MaterialProperty(
        material_id="MAT-HC",
        standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=138.0,
        yield_strength=260.0,
        tensile_strength=485.0,
        source_reference="El hesabı vakası — S elle girildi",
    )


@pytest.fixture
def weld():
    return WeldJoint(
        joint_id="WJ-HC",
        joint_type="longitudinal",
        weld_category="A",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )


# ── (a) Formül katmanı ────────────────────────────────────────────────────────

class TestHandCalcFormulas:
    def test_hand_calc_ug27_shell_formula(self):
        """UG-27(c)(1): t = 2.5×900 / (138×1.0 − 0.6×2.5) = 2250/136.5 = 16.484 mm."""
        t_circ, t_long, t_required = shell_thickness_internal_pressure(
            P=2.5, R=900.0, S=138.0, E=1.0
        )
        assert t_circ == pytest.approx(T_SHELL_HAND, abs=ABS_TOL_MM)
        assert t_required == pytest.approx(T_SHELL_HAND, abs=ABS_TOL_MM)
        # Boyuna: 2250 / 277 = 8.123 mm — kritik değil
        assert t_long == pytest.approx(8.123, abs=ABS_TOL_MM)
        assert t_required == t_circ

    def test_hand_calc_ug32_elliptical_head_formula(self):
        """UG-32 2:1 eliptik: t = 2.0×2000 / (2×138×1.0 − 0.2×2.0) = 4000/275.6 = 14.514 mm."""
        t, K = head_elliptical_thickness(P=2.0, D=2000.0, S=138.0, E=1.0)
        assert t == pytest.approx(T_HEAD_HAND, abs=ABS_TOL_MM)
        assert K == 1.0


# ── (b) Uçtan uca: design_code üzerinden ──────────────────────────────────────

class TestHandCalcDesignCode:
    def test_hand_calc_ug27_shell_design_code(self, asme_code, material, weld):
        """calculate_shell_thickness → t_required ara değeri = 16.484 mm (C = 0)."""
        shell = ShellSection(
            section_id="SHELL-HC",
            inside_diameter=1800.0,
            tangent_length=3000.0,
            nominal_thickness=20.0,
            material_id="MAT-HC",
            weld_joint_id="WJ-HC",
            internal_corrosion_allowance=0.0,
            mill_tolerance=12.5,
        )
        result = asme_code.calculate_shell_thickness({
            "shell": shell,
            "design_conditions": _design_conditions(2.5),
            "materials": [material],
            "welds": [weld],
            "code_edition": "2025",
        })
        assert _intermediate(result, "R_corroded") == pytest.approx(900.0)
        assert _intermediate(result, "t_required") == pytest.approx(
            T_SHELL_HAND, abs=ABS_TOL_MM
        )

    def test_hand_calc_ug32_elliptical_head_design_code(self, asme_code, material, weld):
        """calculate_head_thickness (2:1 eliptik) → t_required = 14.514 mm (C = 0)."""
        head = Head(
            head_id="HEAD-HC",
            type=HeadType.ELLIPTICAL,
            inside_diameter=2000.0,
            nominal_thickness=18.0,
            material_id="MAT-HC",
            weld_joint_id="WJ-HC",
            internal_corrosion_allowance=0.0,
            mill_tolerance=12.5,
        )
        result = asme_code.calculate_head_thickness({
            "head": head,
            "design_conditions": _design_conditions(2.0),
            "materials": [material],
            "welds": [weld],
            "code_edition": "2025",
        })
        assert _intermediate(result, "K_factor") == pytest.approx(1.0)
        assert _intermediate(result, "t_required") == pytest.approx(
            T_HEAD_HAND, abs=ABS_TOL_MM
        )
