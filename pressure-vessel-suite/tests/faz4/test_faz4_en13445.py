"""Faz 4.D — EN 13445 DesignCode testleri.

Golden-case: bilinen kap → EN 13445-3 hesap sonuçları + tolerans + madde ref.

Referans: EN 13445-3:2021+A1:2023
"""

import pytest

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    ProductForm,
    ShellSection,
    WeldJoint,
)
from units import relative_tolerance
from code_en_13445 import EN13445DesignCode
from code_en_13445 import formulas


@pytest.fixture
def en_code():
    return EN13445DesignCode(edition="2021+A1:2023")


@pytest.fixture
def sample_en_project_components():
    """EN 13445 golden-case proje bileşenleri.

    Silindirik gövde: D_i = 1000 mm, L = 2000 mm, t = 12 mm
    Malzeme: P355NH, f = 163 MPa (200°C'de)
    Tasarım basıncı: 1.2 MPa
    Tasarım sıcaklığı: 200°C
    Korozyon payı: 2.0 mm
    Birimleştirme katsayısı: z = 1.0 (tam RT)
    """
    dc = DesignConditions(
        operating_pressure=1.0,
        design_pressure=1.2,
        maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0,
        design_temperature=200.0,
        minimum_design_temperature=-10.0,
        corrosion_allowance_internal=2.0,
        hydrotest_temperature=20.0,
    )

    shell = ShellSection(
        section_id="SHELL-01",
        inside_diameter=1000.0,
        tangent_length=2000.0,
        nominal_thickness=12.0,
        material_id="MAT-EN-01",
        weld_joint_id="WJ-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,  # EN'de tipik %10
    )

    head_l = Head(
        head_id="HEAD-L",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-EN-01",
        weld_joint_id="WJ-02",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,
    )

    head_r = Head(
        head_id="HEAD-R",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-EN-01",
        weld_joint_id="WJ-03",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,
    )

    mat = MaterialProperty(
        material_id="MAT-EN-01",
        standard_pack="EN 10028-3:2017",
        material_designation="P355NH",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=163.0,  # EN 13445-3 Tablo 6-1
        yield_strength=295.0,    # 200°C'de
        tensile_strength=490.0,
        source_reference="EN 10028-3:2017, P355NH",
    )

    wj1 = WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        weld_category="A",
        joint_efficiency=1.0,
        joint_coefficient=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )
    wj2 = WeldJoint(
        joint_id="WJ-02",
        joint_type="circumferential",
        weld_category="B",
        joint_efficiency=1.0,
        joint_coefficient=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )
    wj3 = WeldJoint(
        joint_id="WJ-03",
        joint_type="circumferential",
        weld_category="B",
        joint_efficiency=1.0,
        joint_coefficient=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )

    return {
        "dc": dc,
        "shell": shell,
        "head_l": head_l,
        "head_r": head_r,
        "mat": mat,
        "welds": [wj1, wj2, wj3],
    }


# ── Formül birim testleri ─────────────────────────────────────────────────────

class TestEN13445Formulas:
    """EN 13445-3 formüllerinin doğrudan birim testleri."""

    def test_shell_thickness_en_5_4_2(self):
        """EN 13445-3, 5.4.2 — Silindirik gövde et kalınlığı.

        P = 1.2 MPa, R = 498 mm (500 - 2 korozyon), f = 163 MPa, z = 1.0
        e_circ = P×R / (f×z - P/2) = 1.2×498 / (163×1.0 - 0.6)
               = 597.6 / 162.4 = 3.679 mm
        """
        e_circ, e_long, e_req = formulas.shell_thickness_internal_pressure(
            P=1.2, R=498.0, f=163.0, z=1.0
        )
        assert relative_tolerance(e_circ, 3.679, 0.005), f"e_circ={e_circ}"
        assert e_req == e_circ  # Çevresel kritik

    def test_shell_thickness_en_5_4_2_long(self):
        """EN 13445-3, 5.4.2 — Boyuna gerilme.

        e_long = P×R / (2×f×z + P) = 1.2×498 / (2×163 + 1.2)
               = 597.6 / 327.2 = 1.826 mm
        """
        e_circ, e_long, e_req = formulas.shell_thickness_internal_pressure(
            P=1.2, R=498.0, f=163.0, z=1.0
        )
        assert relative_tolerance(e_long, 1.826, 0.005), f"e_long={e_long}"

    def test_shell_nominal_thickness_en(self):
        """EN 13445 nominal kalınlık hesabı.

        Mill negatif toleransı sipariş edilen nominal kalınlığın tamamına
        uygulanır; korozyon payı bölmenin içinde kalmalıdır.

        e_required = 3.679 mm, C = 2.0 mm, mill = 0.90 (%10)
        e_nominal = (3.679 + 2.0) / 0.90 = 5.679 / 0.90 = 6.310 mm
        """
        e_nom = formulas.shell_required_nominal_thickness(3.679, 2.0, 0.90)
        assert relative_tolerance(e_nom, 6.310, 0.01), f"e_nom={e_nom}"

    def test_elliptical_head_thickness_en(self):
        """E06: EN 13445-3, 7.5.4 — 2:1 elipsoidal → eşdeğer torisferik + 7.5.3.

        K = 2 → R = Di·(0,44·2 + 0,02) = 900 mm, r = Di·(0,5/2 − 0,08) = 170 mm
        P = 1.2, Di = 1000, f = 163, z = 1, fb = 295/1.5 = 196.67, k = 0.75R + 0.2Di = 875
        es = 1.2·900/(326 − 0.6) = 3.3190 mm
        ey: X = 0.17; Y = ey/R = 0.004682, Z = 2.3296, N = 0.84552
            β0.1 = 0.9632, β0.2 = 0.52165 → β = 10·(0.03·0.9632 + 0.07·0.52165) = 0.6541
            ey = 0.6541·1.2·875/163 = 4.2138 mm (yöneten)
        eb = 875·[1.2/(111·196.67)·(1000/170)^0.825]^(2/3) = 3.3523 mm
        Eski küre denklemi 1.2·1000/(652 − 1.2) = 1.844 mm idi (~%44 → emniyetsiz).
        """
        R, r = formulas.ellipsoidal_equivalent_radii(1000.0, 2.0)
        assert relative_tolerance(R, 900.0, 1e-9) and relative_tolerance(r, 170.0, 1e-9)
        d = formulas.head_torispherical_thickness(1.2, 1000.0, R, r, 163.0, 1.0, 295.0 / 1.5)
        assert relative_tolerance(d["es"], 3.3190, 0.001), d
        assert relative_tolerance(d["beta"], 0.6541, 0.001), d
        assert relative_tolerance(d["ey"], 4.2138, 0.001), d
        assert relative_tolerance(d["eb"], 3.3523, 0.001), d
        assert d["governing"] == "ey"
        assert d["e"] > 2.2 * 1.844  # eski küre değerinin 2 katından fazla

    def test_ellipsoidal_shape_factor_and_scope(self):
        """7.5.4: K = Di/(2hi); uygulanabilirlik 1,7 < K < 2,2 (bellekten)."""
        assert formulas.ellipsoidal_shape_factor(1000.0, 250.0) == 2.0
        assert formulas.ellipsoidal_in_scope(2.0)
        assert not formulas.ellipsoidal_in_scope(1.7)
        assert not formulas.ellipsoidal_in_scope(2.2)
        assert not formulas.ellipsoidal_in_scope(2.5)

    def test_hemispherical_head_thickness_en(self):
        """EN 13445-3, 5.5.4 — Yarım küresel bombe.

        P = 1.2 MPa, R = 500 mm, f = 163 MPa, z = 1.0
        e = P×R / (2×f×z - 0.5×P) = 1.2×500 / (2×163 - 0.6)
          = 600 / 325.4 = 1.844 mm
        """
        e = formulas.head_hemispherical_thickness(1.2, 500.0, 163.0, 1.0)
        assert relative_tolerance(e, 1.844, 0.005), f"e={e}"

    def test_torispherical_head_thickness_en(self):
        """EN 13445-3, 7.5.3 — Torisferik bombe tam prosedürü (E03; eski W yaklaşımı kaldırıldı).

        P = 1.2, Di = R = 1000, r = 60 (X = 0.06), f = 163, z = 1.0, fb = 275/1.5
        es = 1.2×1000/(326 − 0.6) = 3.6878 mm
        ey = β0.06(ey)×1.2×950/163 → ey = 8.0602 mm, β = 1.1525 (yöneten)
        eb = 950×[1.2/(111×183.33)×(1000/60)^0.825]^(2/3) = 6.7632 mm
        Ayrıntılı el hesabı: test_faz4_en13445_torispherical.py
        """
        d = formulas.head_torispherical_thickness(1.2, 1000.0, 1000.0, 60.0, 163.0, 1.0, 275.0 / 1.5)
        assert relative_tolerance(d["es"], 3.6878, 0.001), d
        assert relative_tolerance(d["ey"], 8.0602, 0.001), d
        assert relative_tolerance(d["eb"], 6.7632, 0.001), d
        assert d["governing"] == "ey"

    def test_mawp_shell_en(self):
        """MAWP — silindirik gövde (EN 13445).

        R = 500 mm, e = 12 mm, C = 2 mm → e_corroded = 10 mm
        P = f×z×e / (R + e/2) = 163×1.0×10 / (500 + 5) = 1630/505 = 3.228 MPa
        """
        mawp = formulas.mawp_from_shell(500.0, 12.0, 163.0, 1.0, 2.0)
        assert relative_tolerance(mawp, 3.228, 0.005), f"MAWP={mawp}"

    def test_mawp_ellipsoidal_en(self):
        """E06: MAWP — 2:1 elipsoidal, eşdeğer torisferik (7.5.3.4 ters).

        Di = 1000, R = 900, r = 170, ea = 10, f = 163, z = 1, fb = 196.67
        Ps = 2·163·10/(900 + 5) = 3.6022 ; β(ea) = 0.5867
        Py = 163·10/(0.5867·875) = 3.1752 (yöneten) ; Pb = 6.1825
        Eski küre denklemi 4·163·10/1010 = 6.455 MPa idi (~2 kat fazla).
        """
        R, r = formulas.ellipsoidal_equivalent_radii(1000.0, 2.0)
        m = formulas.torispherical_max_pressure(1000.0, R, r, 10.0, 163.0, 1.0, 295.0 / 1.5)
        assert relative_tolerance(m["Ps"], 3.6022, 0.001), m
        assert relative_tolerance(m["Py"], 3.1752, 0.001), m
        assert relative_tolerance(m["Pb"], 6.1825, 0.001), m
        assert m["governing"] == "Py"
        assert relative_tolerance(m["P_bisect"], m["P_max"], 0.001), m
        with pytest.raises(ValueError, match="7.5.4"):
            formulas.mawp_from_head("elliptical", 1000.0, 12.0, 163.0, 1.0, C=2.0)

    def test_ped_test_pressure(self):
        """PED test basıncı.

        PS = 1.5 MPa, P_operating_max = 1.0 MPa
        P_test = max(1.25×1.0, 1.43×1.5) = max(1.25, 2.145) = 2.145 MPa
        Limiter: PS
        """
        p_test, limiter = formulas.ped_test_pressure(1.5, 1.0)
        assert relative_tolerance(p_test, 2.145, 0.001), f"P_test={p_test}"
        assert limiter == "PS"

    def test_ped_test_pressure_op_limiter(self):
        """PED test basıncı — çalışma basıncı limitleyici.

        PS = 0.5 MPa, P_operating_max = 2.0 MPa
        P_test = max(1.25×2.0, 1.43×0.5) = max(2.5, 0.715) = 2.5 MPa
        Limiter: operating_pressure
        """
        p_test, limiter = formulas.ped_test_pressure(0.5, 2.0)
        assert relative_tolerance(p_test, 2.5, 0.001), f"P_test={p_test}"
        assert limiter == "operating_pressure"


# ── DesignCode entegrasyon testleri ──────────────────────────────────────────

class TestEN13445DesignCode:
    """EN13445DesignCode entegrasyon testleri."""

    def test_code_name(self, en_code):
        """Standart adı doğru olmalı."""
        assert en_code.code_name == "EN 13445"
        assert en_code.code_edition == "2021+A1:2023"

    def test_shell_thickness_result(self, en_code, sample_en_project_components):
        """Gövde et kalınlığı hesap sonucu — izlenebilir."""
        comp = sample_en_project_components
        r = en_code.calculate_shell_thickness({
            "shell": comp["shell"],
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "welds": comp["welds"],
            "code_edition": "2021+A1:2023",
        })
        assert r.code == "EN 13445"
        assert r.edition == "2021+A1:2023"
        assert r.clause_reference == "EN 13445-3, 7.4.2"  # E04: Madde 7 (eski 5.4.2 yanlıştı)
        assert r.status.value == "PASS"
        assert r.final_result is not None
        assert r.final_result <= comp["shell"].nominal_thickness
        assert len(r.intermediate_values) > 0
        assert r.material_properties_used["designation"] == "P355NH"

    def test_material_temperature_and_thickness_range_require_review(self, en_code, sample_en_project_components):
        comp = sample_en_project_components
        mat = comp["mat"].model_copy(update={"temperature": 20.0, "thickness_min": 20.0})
        r = en_code.calculate_shell_thickness({
            "shell": comp["shell"], "design_conditions": comp["dc"],
            "materials": [mat], "welds": comp["welds"],
        })
        assert r.status.value == "REVIEW REQUIRED"
        assert any("design stress is declared at 20 C" in w for w in r.warnings)
        assert any("outside material" in w for w in r.warnings)

        mawp = en_code.calculate_mawp({
            "component_type": "shell", "component": comp["shell"],
            "design_conditions": comp["dc"], "materials": [mat],
            "welds": comp["welds"], "nominal_thickness": comp["shell"].nominal_thickness,
        })
        assert mawp.status.value == "REVIEW REQUIRED"

    def test_head_thickness_result(self, en_code, sample_en_project_components):
        """Bomba et kalınlığı hesap sonucu."""
        comp = sample_en_project_components
        r = en_code.calculate_head_thickness({
            "head": comp["head_l"],
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "welds": comp["welds"],
            "code_edition": "2021+A1:2023",
        })
        assert r.code == "EN 13445"
        assert r.clause_reference == "EN 13445-3, 7.5.4"
        # E06: 7.5.4 eşdeğer torisferik (K = 2 varsayımı) → verified=False → PASS yok
        assert r.status.value == "REVIEW REQUIRED"
        assert any("7.5.4" in w and "verified=False" in w for w in r.warnings)
        iv = {i["name"]: i["value"] for i in r.intermediate_values}
        assert iv["K"] == 2.0
        # Dc = 1004 → R = 903.6, r = 170.68 → ey = 4.2306 mm (yöneten)
        assert relative_tolerance(iv["R"], 903.6, 1e-6) and relative_tolerance(iv["r"], 170.68, 1e-6)
        assert relative_tolerance(iv["e_required"], 4.2306, 0.001), iv
        assert iv["governing"] == "ey"
        # e_nom = (4.2306 + 2)/0.90 = 6.9229 mm
        assert relative_tolerance(r.final_result, 6.9229, 0.001), r.final_result
        assert any("K4" in a and "2:1" in a for a in r.assumptions)

    def test_mawp_shell(self, en_code, sample_en_project_components):
        """MAWP — gövde."""
        comp = sample_en_project_components
        r = en_code.calculate_mawp({
            "component_type": "shell",
            "component": comp["shell"],
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "welds": comp["welds"],
            "nominal_thickness": comp["shell"].nominal_thickness,
            "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "PASS"
        assert r.final_result is not None
        assert r.final_result > comp["dc"].design_pressure

    def test_mawp_head(self, en_code, sample_en_project_components):
        """MAWP — bombe."""
        comp = sample_en_project_components
        r = en_code.calculate_mawp({
            "component_type": "head",
            "component": comp["head_l"],
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "welds": comp["welds"],
            "nominal_thickness": comp["head_l"].nominal_thickness,
            "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "REVIEW REQUIRED"  # E06: 7.5.4 eşdeğer torisferik, verified=False
        assert r.clause_reference == "EN 13445-3, 7.5.4"
        # Dc = 1004, R = 903.6, r = 170.68, ea = 10 → Py = 3.1608 MPa (yöneten; eski küre 6.430)
        assert relative_tolerance(r.final_result, 3.1608, 0.001), r.final_result

    def test_elliptical_head_k_out_of_scope(self, en_code, sample_en_project_components):
        """E06: K = Di/(2hi) = 1000/(2·200) = 2,5 → 7.5.4 dışı → OUT_OF_SCOPE (sessiz hesap yok)."""
        comp = sample_en_project_components
        head = comp["head_l"].model_copy(update={"crown_depth": 200.0})
        for r in (
            en_code.calculate_head_thickness({
                "head": head, "design_conditions": comp["dc"], "materials": [comp["mat"]],
                "welds": comp["welds"]}),
            en_code.calculate_mawp({
                "component_type": "head", "component": head, "design_conditions": comp["dc"],
                "materials": [comp["mat"]], "welds": comp["welds"],
                "nominal_thickness": head.nominal_thickness}),
        ):
            assert r.status.value == "OUT OF SCOPE", r.status
            assert r.final_result is None
            assert any("K = Di/(2hi) = 2.500" in w for w in r.warnings), r.warnings

    def test_ped_hydrotest(self, en_code, sample_en_project_components):
        """PED test basıncı."""
        comp = sample_en_project_components
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "code_edition": "2021+A1:2023",
        })
        # Tasarım 200 °C / test 20 °C, test gerilmesi girilmemiş → fa/ft bilinmiyor (B-28)
        assert r.status.value == "REVIEW REQUIRED"
        assert r.final_result is not None
        # PED test basıncı = max(1.25×1.0, 1.43×1.5) = 2.145 MPa
        assert relative_tolerance(r.final_result, 2.145, 0.001), f"P_test={r.final_result}"
        assert any("fa/ft" in w for w in r.warnings)

    def test_ped_hydrotest_ratio_below_threshold_passes(self, en_code, sample_en_project_components):
        """fa/ft ≤ 1.43/1.25 = 1.144 → 1.43·Ps her iki seçim yönünde belirleyici → PASS."""
        comp = sample_en_project_components
        mat = comp["mat"].model_copy(update={
            "allowable_stress_test_temp": comp["mat"].allowable_stress * 1.07,
        })
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": comp["dc"], "materials": [mat], "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "PASS"
        assert relative_tolerance(r.final_result, 2.145, 0.001)

    def test_ped_hydrotest_ratio_term_governs_needs_review(self, en_code, sample_en_project_components):
        """E04 el hesabı: fa/fT = 1,5 → 1,25·1,2·1,5 = 2,25 > 1,43·1,5 = 2,145 → Pt = 2,25, inceleme."""
        comp = sample_en_project_components
        mat = comp["mat"].model_copy(update={
            "allowable_stress_test_temp": comp["mat"].allowable_stress * 1.5,
        })
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": comp["dc"], "materials": [mat], "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "REVIEW REQUIRED"
        assert r.final_result == pytest.approx(2.25, rel=1e-9)
        assert r.clause_reference == "EN 13445-5, 10.2.3.3.1"
        assert any("fa/fT = 1.500" in w for w in r.warnings)

    def test_ped_hydrotest_ratio_applied_ps_still_governs(self, en_code, sample_en_project_components):
        """E04 el hesabı: fa/fT = 1,40 → 1,25·1,2·1,40 = 2,10 < 2,145 → 1,43·PS belirleyici (PASS)."""
        comp = sample_en_project_components
        mat = comp["mat"].model_copy(update={
            "allowable_stress_test_temp": comp["mat"].allowable_stress * 1.40,
        })
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": comp["dc"], "materials": [mat], "code_edition": "2021+A1:2023",
        })
        iv = {v["name"]: v["value"] for v in r.intermediate_values}
        assert iv["P_from_pd"] == pytest.approx(2.10, rel=1e-9)
        assert r.final_result == pytest.approx(2.145, rel=1e-9)
        assert r.status.value == "PASS"

    def test_hydrotest_uses_design_pressure_not_operating(self, en_code, sample_en_project_components):
        """E04: 1,25 terimi Pd ile: Pd = 3,0, PS = 1,5, aynı sıcaklık → Pt = 3,75 (eskisi 1,25·Pop)."""
        comp = sample_en_project_components
        dc = comp["dc"].model_copy(update={
            "design_pressure": 3.0, "hydrotest_temperature": comp["dc"].design_temperature})
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": dc, "materials": [comp["mat"]], "code_edition": "2021+A1:2023",
        })
        assert r.final_result == pytest.approx(3.75, rel=1e-9)
        assert r.input_snapshot["limiter"] == "design_pressure"
        assert r.status.value == "PASS"  # fa/fT = 1: sonuç PED 1,25/1,43 ile aynı

    def test_ped_hydrotest_same_temperature_passes(self, en_code, sample_en_project_components):
        """Tasarım = test sıcaklığı → fa = ft → PASS (ek veri gerekmez)."""
        comp = sample_en_project_components
        dc = comp["dc"].model_copy(update={"hydrotest_temperature": comp["dc"].design_temperature})
        r = en_code.calculate_hydrotest_pressure({
            "design_conditions": dc, "materials": [comp["mat"]], "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "PASS"

    def test_nozzle_not_calculated(self, en_code, sample_en_project_components):
        """Nozul hesapları NOT_CALCULATED."""
        from domain import Nozzle, NozzleType
        nozzle = Nozzle(
            tag="N1",
            nozzle_type=NozzleType.FLANGED,
            host_component_id="SHELL-01",
            axial_position=500.0,
            outside_diameter=168.3,
            inside_diameter=154.1,
            neck_thickness=7.1,
            material_id="MAT-EN-01",
        )
        r = en_code.calculate_nozzle({
            "nozzle": nozzle,
            "design_conditions": sample_en_project_components["dc"],
            "materials": [sample_en_project_components["mat"]],
        })
        assert r.status.value == "NOT CALCULATED"

    def test_traceability(self, en_code, sample_en_project_components):
        """K5: Herhesap denetlenebilir — ara değerler ve madde referansı dolu."""
        comp = sample_en_project_components
        r = en_code.calculate_shell_thickness({
            "shell": comp["shell"],
            "design_conditions": comp["dc"],
            "materials": [comp["mat"]],
            "welds": comp["welds"],
            "code_edition": "2021+A1:2023",
        })
        assert r.clause_reference != ""
        assert r.formula_reference != ""
        assert len(r.intermediate_values) > 0
        # Ara değerlerde f, z, P, R olmalı
        names = [iv["name"] for iv in r.intermediate_values]
        assert "f" in names
        assert "z" in names
        assert "P" in names
        assert "R" in names


# ── Fail senaryoları ──────────────────────────────────────────────────────────

class TestEN13445FailScenarios:
    """FAIL durumunu tetikleyen senaryolar."""

    def test_shell_too_thin_en(self, en_code):
        """Çok ince gövde → FAIL."""
        dc = DesignConditions(
            operating_pressure=5.0,
            design_pressure=5.0,
            maximum_allowable_pressure_ps=5.0,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            corrosion_allowance_internal=2.0,
        )
        shell = ShellSection(
            section_id="SHELL-THIN",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=5.0,  # Çok ince
            material_id="MAT-EN-01",
            internal_corrosion_allowance=2.0,
        )
        mat = MaterialProperty(
            material_id="MAT-EN-01",
            standard_pack="EN 10028-3:2017",
            material_designation="P355NH",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=163.0,
            yield_strength=295.0,
            tensile_strength=490.0,
            source_reference="EN 10028-3:2017",
        )

        r = en_code.calculate_shell_thickness({
            "shell": shell,
            "design_conditions": dc,
            "materials": [mat],
            "welds": [],
            "code_edition": "2021+A1:2023",
        })
        assert r.status.value == "FAIL"
        assert r.final_result > shell.nominal_thickness


# ── StandardPack testleri ─────────────────────────────────────────────────────

class TestStandardPack:
    """StandardPack testleri."""

    def test_load_asme_pack(self):
        """ASME standart paketi yüklenebilmeli."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "standards" / "manifests"))
        from standards_manifests import StandardPack, ASME_VIII_1_2025
        assert ASME_VIII_1_2025.pack_id == "asme-viii-1-2025"
        assert ASME_VIII_1_2025.code_family == "ASME VIII-1"
        assert ASME_VIII_1_2025.full_edition == "2025"

    def test_load_en_pack(self):
        """EN standart paketi yüklenebilmeli."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "standards" / "manifests"))
        from standards_manifests import EN_13445_2021
        assert EN_13445_2021.pack_id == "en-13445-2021"
        assert EN_13445_2021.code_family == "EN 13445"
        assert "A1:2023" in EN_13445_2021.amendments
        assert EN_13445_2021.full_edition == "2021+A1:2023"

    def test_clause_mapping(self):
        """Madde eşleştirmesi bulunabilmeli."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "standards" / "clause-mappings"))
        from clause_mappings import get_clause_mapping
        mapping = get_clause_mapping("UG-27-CIRC")
        assert mapping is not None
        assert mapping.clause_reference == "UG-27(c)(1)"
        assert mapping.code == "ASME VIII-1"

    def test_en_clause_mapping(self):
        """EN madde eşleştirmesi bulunabilmeli."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "standards" / "clause-mappings"))
        from clause_mappings import get_clause_mapping
        mapping = get_clause_mapping("EN-5.4.2-CIRC", "EN 13445")  # eski kimlik = takma ad
        assert mapping is not None
        assert mapping.clause_reference == "EN 13445-3, 7.4.2"
        assert get_clause_mapping("EN-5.5.4-HEMI", "EN 13445").clause_reference == "EN 13445-3, 7.5.2"
        assert get_clause_mapping("EN-5.5.2-ELLIP", "EN 13445").clause_reference == "EN 13445-3, 7.5.4"
        assert get_clause_mapping("EN-5.5.3-TORI", "EN 13445").clause_reference == "EN 13445-3, 7.5.3"
        assert get_clause_mapping("EN-10.2-HYDRO", "EN 13445").clause_reference == "EN 13445-5, 10.2.3.3.1"


# Path import for StandardPack tests
from pathlib import Path
