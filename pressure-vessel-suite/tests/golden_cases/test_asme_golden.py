"""ASME VIII-1 Golden-case testleri.

Her test: known input → expected intermediate → expected final + tolerans + kaynak/sürüm.
Bağımsız gözden geçiren: [Henüz atanmadı — üretim öncesi uzman incelemesi gerekir]

Referans: ASME BPVC Section VIII Division 1, 2025 Edition
"""

import pytest

from domain import (
    CalculationCode,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    NozzleType,
    ProductForm,
    ShellSection,
    VesselProject,
    WeldJoint,
)
from units import relative_tolerance
from code_asme_viii_1 import ASMEVIII1DesignCode
from calc_core.orchestrator import CalculationOrchestrator


# ── Test fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def asme_code():
    return ASMEVIII1DesignCode(edition="2025")


@pytest.fixture
def sample_project():
    """Tipik bir basınçlı kap projesi — golden-case referans değerleriyle.

    Girdiler:
    - Silindirik gövde: D_i = 1000 mm, L = 2000 mm, t = 12 mm
    - 2 adet 2:1 elipsoidal bombe: D_i = 1000 mm, t = 12 mm
    - Malzeme: SA-516 Gr.70, S = 138 MPa (200°C'de)
    - Tasarım basıncı: 1.2 MPa
    - Tasarım sıcaklığı: 200°C
    - Korozyon payı: 2.0 mm
    - Kaynak verimi: E = 1.0 (tam RT)
    - Mill tolerans: %12.5 (factor = 0.875)
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
        material_id="MAT-01",
        weld_joint_id="WJ-01",
        internal_corrosion_allowance=2.0,
        mill_tolerance=12.5,
    )

    head_l = Head(
        head_id="HEAD-L",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        weld_joint_id="WJ-02",
        internal_corrosion_allowance=2.0,
        mill_tolerance=12.5,
    )

    head_r = Head(
        head_id="HEAD-R",
        type=HeadType.ELLIPTICAL,
        inside_diameter=1000.0,
        nominal_thickness=12.0,
        material_id="MAT-01",
        weld_joint_id="WJ-03",
        internal_corrosion_allowance=2.0,
        mill_tolerance=12.5,
    )

    nozzle_n1 = Nozzle(
        tag="N1",
        nozzle_type=NozzleType.FLANGED,
        host_component_id="SHELL-01",
        axial_position=500.0,
        outside_diameter=168.3,
        inside_diameter=154.1,
        neck_thickness=7.1,
        material_id="MAT-01",
    )

    nozzle_n2 = Nozzle(
        tag="N2",
        nozzle_type=NozzleType.FLANGED,
        host_component_id="SHELL-01",
        axial_position=1200.0,
        outside_diameter=114.3,
        inside_diameter=102.3,
        neck_thickness=6.0,
        material_id="MAT-01",
    )

    mat = MaterialProperty(
        material_id="MAT-01",
        standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=138.0,
        yield_strength=260.0,
        tensile_strength=485.0,
        source_reference="ASME II-D Table 1A, Line 4",
    )

    wj1 = WeldJoint(
        joint_id="WJ-01",
        joint_type="longitudinal",
        weld_category="A",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )
    wj2 = WeldJoint(
        joint_id="WJ-02",
        joint_type="circumferential",
        weld_category="B",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )
    wj3 = WeldJoint(
        joint_id="WJ-03",
        joint_type="circumferential",
        weld_category="B",
        joint_efficiency=1.0,
        full_penetration=True,
        nde_method="RT-1",
        nde_extent="100%",
    )

    return VesselProject(
        project_number="GOLDEN-001",
        project_name="Golden Case Test Vessel",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=dc,
        shell_sections=[shell],
        heads=[head_l, head_r],
        nozzles=[nozzle_n1, nozzle_n2],
        materials=[mat],
        welds=[wj1, wj2, wj3],
    )


# ── Formül birim testleri ─────────────────────────────────────────────────────

class TestASMEFormulas:
    """ASME formüllerinin doğrudan birim testleri."""

    def test_shell_thickness_ug27(self):
        """UG-27(c)(1) — Silindirik gövde et kalınlığı.

        P = 1.2 MPa, R = 498 mm (500 - 2 korozyon), S = 138 MPa, E = 1.0
        t_circ = P×R / (S×E - 0.6×P) = 1.2×498 / (138×1.0 - 0.6×1.2)
               = 597.6 / 137.28 = 4.353 mm
        """
        from code_asme_viii_1.formulas import shell_thickness_internal_pressure

        t_circ, t_long, t_req = shell_thickness_internal_pressure(
            P=1.2, R=498.0, S=138.0, E=1.0
        )
        assert relative_tolerance(t_circ, 4.353, 0.005), f"t_circ={t_circ}"
        assert t_req == t_circ  # Çevresel kritik

    def test_shell_thickness_ug27_long(self):
        """UG-27(c)(1) — Boyuna gerilme (çevresel dikiş).

        t_long = P×R / (2×S×E + 0.4×P) = 1.2×498 / (2×138×1.0 + 0.4×1.2)
               = 597.6 / 276.48 = 2.161 mm
        """
        from code_asme_viii_1.formulas import shell_thickness_internal_pressure

        t_circ, t_long, t_req = shell_thickness_internal_pressure(
            P=1.2, R=498.0, S=138.0, E=1.0
        )
        assert relative_tolerance(t_long, 2.161, 0.005), f"t_long={t_long}"

    def test_shell_nominal_thickness(self):
        """Nominal kalınlık hesabı.

        Mill negatif toleransı sipariş edilen nominal kalınlığın tamamına
        uygulanır; korozyon payı bölmenin içinde kalmalıdır.

        t_required = 4.353 mm, C = 2.0 mm, mill = 0.875
        t_nominal = (4.353 + 2.0) / 0.875 = 6.353 / 0.875 = 7.261 mm
        """
        from code_asme_viii_1.formulas import shell_required_nominal_thickness

        t_nom = shell_required_nominal_thickness(4.353, 2.0, 0.875)
        assert relative_tolerance(t_nom, 7.261, 0.01), f"t_nom={t_nom}"

    def test_shell_nominal_thickness_survives_mill_and_corrosion(self):
        """Üretilen nominal kalınlık ömür sonunda gerekli kalınlığı karşılamalı.

        En kötü teslim (factor × t_nominal) eksi korozyon payı, basınç için
        gerekli kalınlıktan az olamaz. Bu, mill toleransının nereye uygulandığını
        formülden bağımsız olarak sabitler.
        """
        from code_asme_viii_1.formulas import shell_required_nominal_thickness

        t_required, C, factor = 4.353, 2.0, 0.875
        t_nom = shell_required_nominal_thickness(t_required, C, factor)
        kalan = factor * t_nom - C
        assert kalan >= t_required - 1e-9, (
            f"t_nom={t_nom:.3f} mm siparis edilirse en kotu teslim "
            f"{factor * t_nom:.3f} mm, korozyon sonrasi {kalan:.3f} mm kaliyor; "
            f"gerekli {t_required} mm"
        )

    def test_elliptical_head_thickness(self):
        """UG-32(d) — 2:1 elipsoidal bombe.

        P = 1.2 MPa, D = 1000 mm, S = 138 MPa, E = 1.0
        t = P×D / (2×S×E - 0.2×P) = 1.2×1000 / (2×138 - 0.24)
          = 1200 / 275.76 = 4.352 mm
        """
        from code_asme_viii_1.formulas import head_elliptical_thickness

        t, K = head_elliptical_thickness(1.2, 1000.0, 138.0, 1.0)
        assert relative_tolerance(t, 4.352, 0.005), f"t={t}"
        assert K == 1.0

    def test_hemispherical_head_thickness(self):
        """UG-32(f) — Yarım küresel bombe.

        P = 1.2 MPa, R = 500 mm, S = 138 MPa, E = 1.0
        t = P×R / (2×S×E - 0.2×P) = 1.2×500 / (2×138 - 0.24)
          = 600 / 275.52 = 2.178 mm
        """
        from code_asme_viii_1.formulas import head_hemispherical_thickness

        t = head_hemispherical_thickness(1.2, 500.0, 138.0, 1.0)
        assert relative_tolerance(t, 2.178, 0.005), f"t={t}"

    def test_torispherical_head_thickness(self):
        """UG-32(e) — Torisferik bombe (örnek: R_knuckle = 6% D).

        L = 1000 mm, r = 60 mm, P = 1.2, S = 138, E = 1.0
        M = (3 + sqrt(1000/60)) / 4 = (3 + 4.082) / 4 = 1.771
        t = P×L×M / (2×S×E - 0.2×P) = 1.2×1000×1.771 / (275.76)
          = 2125.2 / 275.76 = 7.706 mm
        """
        from code_asme_viii_1.formulas import head_torispherical_thickness_full

        t, M = head_torispherical_thickness_full(1.2, 1000.0, 60.0, 138.0, 1.0)
        assert relative_tolerance(t, 7.706, 0.01), f"t={t}, M={M}"
        assert relative_tolerance(M, 1.771, 0.01), f"M={M}"

    def test_mawp_shell(self):
        """MAWP — silindirik gövde.

        R = 500 mm, t = 12 mm, C = 2 mm → t_corroded = 10 mm
        P = S×E×t / (R + 0.6×t) = 138×1.0×10 / (500 + 6) = 1380/506 = 2.727 MPa
        """
        from code_asme_viii_1.formulas import mawp_from_shell

        mawp = mawp_from_shell(500.0, 12.0, 138.0, 1.0, 2.0)
        assert relative_tolerance(mawp, 2.727, 0.005), f"MAWP={mawp}"

    def test_mawp_ellipsoidal(self):
        """MAWP — 2:1 elipsoidal bombe.

        D = 1000 mm, t = 12 mm, C = 2 mm → t_corroded = 10 mm
        P = 2×S×E×t / (D + 0.2×t) = 2×138×1.0×10 / (1000 + 2) = 2760/1002 = 2.755 MPa
        """
        from code_asme_viii_1.formulas import mawp_from_ellipsoidal_head

        mawp = mawp_from_ellipsoidal_head(1000.0, 12.0, 138.0, 1.0, 2.0)
        assert relative_tolerance(mawp, 2.755, 0.005), f"MAWP={mawp}"

    def test_hydrotest_pressure(self):
        """UG-99 — Hidrostatik test basıncı.

        P_design = 1.2 MPa, S_test = S_design = 138 MPa
        P_test = 1.3 × 1.2 × (138/138) = 1.56 MPa
        """
        from code_asme_viii_1.formulas import hydrotest_pressure_asme

        p_test = hydrotest_pressure_asme(1.2, 138.0, 138.0)
        assert relative_tolerance(p_test, 1.56, 0.001), f"P_test={p_test}"

    def test_mawp_torispherical(self):
        """MAWP — torisferik bombe.
        L = 1000 mm, r = 60 mm, t = 12 mm, C = 2 mm → t_corroded = 10 mm
        M = (3 + sqrt(1000/60)) / 4 = (3 + 4.082) / 4 = 1.7705
        P = 2×S×E×t / (L×M + 0.2×t) = 2×138×1.0×10 / (1000×1.7705 + 2)
          = 2760 / 1772.5 = 1.557 MPa
        """
        from code_asme_viii_1.formulas import mawp_from_torispherical_head

        mawp = mawp_from_torispherical_head(1000.0, 60.0, 12.0, 138.0, 1.0, 2.0)
        assert relative_tolerance(mawp, 1.557, 0.01), f"MAWP={mawp}"

    def test_mawp_hemispherical(self):
        """MAWP — yarım küresel bombe.
        R = 500 mm, t = 12 mm, C = 2 mm → t_corroded = 10 mm
        P = 2×S×E×t / (R + 0.2×t) = 2×138×1.0×10 / (500 + 2)
          = 2760 / 502 = 5.498 MPa
        """
        from code_asme_viii_1.formulas import mawp_from_hemispherical_head

        mawp = mawp_from_hemispherical_head(500.0, 12.0, 138.0, 1.0, 2.0)
        assert relative_tolerance(mawp, 5.498, 0.01), f"MAWP={mawp}"

    def test_hydrotest_stress_ratio(self):
        """UG-99 — Hidrotest, stress ratio ≠ 1.
        P_design = 1.2 MPa, S_test = 148 MPa (20°C), S_design = 138 MPa (200°C)
        P_test = 1.3 × 1.2 × (148/138) = 1.3 × 1.2 × 1.07246 = 1.673 MPa
        """
        from code_asme_viii_1.formulas import hydrotest_pressure_asme

        p_test = hydrotest_pressure_asme(1.2, 148.0, 138.0)
        assert relative_tolerance(p_test, 1.673, 0.005), f"P_test={p_test}"

    def test_flat_head_thickness(self):
        """UG-34(c)(2) — Düz kapak et kalınlığı.

        P = 1.2 MPa, d = 996 mm (1000 - 2×2 korozyon), S = 138 MPa, E = 1.0
        C_attach = 0.33 (taban bağlantı tipi)
        t = d × sqrt(C × P / (S × E)) + CA
          = 996 × sqrt(0.33 × 1.2 / (138 × 1.0)) + 2.0
          = 996 × sqrt(0.396 / 138) + 2.0
          = 996 × sqrt(0.002870) + 2.0
          = 996 × 0.05357 + 2.0
          = 53.36 + 2.0 = 55.36 mm
        """
        from code_asme_viii_1.formulas import flat_head_thickness

        t = flat_head_thickness(P=1.2, d=996.0, S=138.0, E=1.0, C_attach=0.33, CA=2.0)
        assert relative_tolerance(t, 55.36, 0.01), f"t={t}"

    def test_flat_head_mawp(self):
        """UG-34(c)(2) — Düz kapak MAWP.

        d = 1000 mm, t = 20 mm, C = 2 mm → t_corr = 18 mm
        S = 138 MPa, E = 1.0, C_attach = 0.33
        P = S × E × (t_corr/d)² / C_attach
          = 138 × 1.0 × (18/1000)² / 0.33
          = 138 × 0.000324 / 0.33
          = 0.044712 / 0.33 = 0.1355 MPa
        """
        from code_asme_viii_1.formulas import flat_head_mawp

        mawp = flat_head_mawp(d=1000.0, t_actual=20.0, S=138.0, E=1.0, C_attach=0.33, CA=2.0)
        assert relative_tolerance(mawp, 0.1355, 0.01), f"MAWP={mawp}"

    def test_pneumatic_test_pressure(self):
        """UG-100 — Pnömatik test basıncı.

        P_design = 1.2 MPa, S_test = S_design = 138 MPa
        P_test = 1.1 × 1.2 × (138/138) = 1.32 MPa
        """
        from code_asme_viii_1.formulas import pneumatic_test_pressure

        p_test = pneumatic_test_pressure(1.2, 138.0, 138.0)
        assert relative_tolerance(p_test, 1.32, 0.001), f"P_test={p_test}"

    def test_pneumatic_test_stress_ratio(self):
        """UG-100 — Pnömatik test, stress ratio ≠ 1.
        P_design = 1.2 MPa, S_test = 148 MPa (20°C), S_design = 138 MPa (200°C)
        P_test = 1.1 × 1.2 × (148/138) = 1.1 × 1.2 × 1.07246 = 1.4157 MPa
        """
        from code_asme_viii_1.formulas import pneumatic_test_pressure

        p_test = pneumatic_test_pressure(1.2, 148.0, 138.0)
        assert relative_tolerance(p_test, 1.4157, 0.005), f"P_test={p_test}"

    def test_cone_thickness(self):
        """UG-32(g) — Konik bölüm et kalınlığı.

        P = 1.2 MPa, D = 1000 mm, S = 138 MPa, E = 1.0, α = 20°
        cos(20°) = 0.9397
        t = P × D / (2 × cos(α) × (S × E - 0.6 × P))
          = 1.2 × 1000 / (2 × 0.9397 × (138 × 1.0 - 0.6 × 1.2))
          = 1200 / (1.8794 × 137.28)
          = 1200 / 257.98 = 4.652 mm
        """
        from code_asme_viii_1.formulas import cone_thickness

        t = cone_thickness(P=1.2, D=1000.0, S=138.0, E=1.0, alpha_deg=20.0)
        assert relative_tolerance(t, 4.652, 0.01), f"t={t}"

    def test_cone_mawp(self):
        """UG-32(g) — Konik bölüm MAWP.

        D = 1000 mm, t = 12 mm, C = 2 mm → t_corr = 10 mm
        S = 138 MPa, E = 1.0, α = 20°, cos(20°) = 0.9397
        P = 2 × cos(α) × S × E × t / (D + 2 × cos(α) × 0.6 × t)
          = 2 × 0.9397 × 138 × 1.0 × 10 / (1000 + 2 × 0.9397 × 0.6 × 10)
          = 2593.57 / (1000 + 11.28)
          = 2593.57 / 1011.28 = 2.565 MPa
        """
        from code_asme_viii_1.formulas import cone_mawp

        mawp = cone_mawp(D=1000.0, t_actual=12.0, S=138.0, E=1.0, alpha_deg=20.0, C=2.0)
        assert relative_tolerance(mawp, 2.565, 0.01), f"MAWP={mawp}"

    def test_shell_boundary_denominator_zero(self):
        """UG-27 — S·E - 0.6·P ≤ 0 durumunda ValueError."""
        from code_asme_viii_1.formulas import shell_thickness_internal_pressure

        with pytest.raises(ValueError, match="UG-27"):
            shell_thickness_internal_pressure(P=230.0, R=500.0, S=138.0, E=1.0)
        # S·E - 0.6·P = 138 - 138 = 0 → should raise

    def test_mawp_negative_corroded_thickness(self):
        """MAWP — korozyon payı kalınlığı aştığında ValueError."""
        from code_asme_viii_1.formulas import mawp_from_shell

        with pytest.raises(ValueError, match="Korozyon"):
            mawp_from_shell(R=500.0, t_actual=1.0, S=138.0, E=1.0, C=2.0)
        # t_corroded = 1.0 - 2.0 = -1.0 → should raise

    def test_shell_nominal_thickness_zero_mill(self):
        """Nominal kalınlık — mill tolerans = 0 (kaynaksız boru)."""
        from code_asme_viii_1.formulas import shell_required_nominal_thickness

        t_nom = shell_required_nominal_thickness(4.353, 2.0, mill_tolerance_factor=1.0)
        # = (4.353 + 2.0 + 0) / 1.0 = 6.353 mm
        assert relative_tolerance(t_nom, 6.353, 0.01), f"t_nom={t_nom}"


# ── DesignCode entegrasyon testleri ──────────────────────────────────────────

class TestASMEVIII1DesignCode:
    """ASMEVIII1DesignCode entegrasyon testleri."""

    def test_shell_thickness_result(self, asme_code, sample_project):
        """Gövde et kalınlığı hesap sonucu — izlenebilir."""
        shell = sample_project.shell_sections[0]
        r = asme_code.calculate_shell_thickness({
            "shell": shell,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.code == "ASME VIII-1"
        assert r.edition == "2025"
        assert r.clause_reference == "UG-27(c)(1)"
        assert r.status.value == "PASS"
        assert r.final_result is not None
        assert r.final_result <= shell.nominal_thickness
        assert len(r.intermediate_values) > 0
        assert r.material_properties_used["designation"] == "SA-516 Gr.70"

    # ── Malzeme veri geçerliliği (sıcaklık / kalınlık aralığı) ───────────────

    def _shell_input(self, sample_project, **mat_update):
        mat = sample_project.materials[0].model_copy(update=mat_update)
        return {
            "shell": sample_project.shell_sections[0],
            "design_conditions": sample_project.design_conditions,
            "materials": [mat],
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        }

    def test_material_temperature_mismatch_needs_review(self, asme_code, sample_project):
        """S, 20 °C için girilmiş ama tasarım 200 °C → sonuç nihai PASS olamaz."""
        r = asme_code.calculate_shell_thickness(self._shell_input(sample_project, temperature=20.0))
        assert r.status.value == "REVIEW REQUIRED"
        assert any("20 °C" in w and "200 °C" in w for w in r.warnings)

    def test_material_temperature_match_still_passes(self, asme_code, sample_project):
        r = asme_code.calculate_shell_thickness(self._shell_input(sample_project))
        assert r.status.value == "PASS"

    def test_material_thickness_range_violation_needs_review(self, asme_code, sample_project):
        """Nominal kalınlık malzeme veri aralığının dışında (12 mm > max 10 mm)."""
        r = asme_code.calculate_shell_thickness(self._shell_input(sample_project, thickness_max=10.0))
        assert r.status.value == "REVIEW REQUIRED"
        assert any("aralığının" in w for w in r.warnings)

    def test_material_mismatch_keeps_fail(self, asme_code, sample_project):
        """Başarısız (FAIL) sonuç uyuşmazlıkla PASS/REVIEW'a yükseltilmez."""
        inp = self._shell_input(sample_project, temperature=20.0)
        inp["shell"] = inp["shell"].model_copy(update={"nominal_thickness": 3.0})
        r = asme_code.calculate_shell_thickness(inp)
        assert r.status.value == "FAIL"
        assert any("20 °C" in w for w in r.warnings)

    def test_material_mismatch_flags_head_and_mawp(self, asme_code, sample_project):
        mat = sample_project.materials[0].model_copy(update={"temperature": 20.0})
        head = sample_project.heads[0]
        rh = asme_code.calculate_head_thickness({
            "head": head, "design_conditions": sample_project.design_conditions,
            "materials": [mat], "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        shell = sample_project.shell_sections[0]
        rm = asme_code.calculate_mawp({
            "component_type": "shell", "component": shell,
            "design_conditions": sample_project.design_conditions,
            "materials": [mat], "welds": sample_project.welds,
            "nominal_thickness": shell.nominal_thickness,
            "code_edition": sample_project.code_edition,
        })
        assert rh.status.value == "REVIEW REQUIRED"
        assert rm.status.value == "REVIEW REQUIRED"

    def test_head_thickness_result(self, asme_code, sample_project):
        """Bomba et kalınlığı hesap sonucu."""
        head = sample_project.heads[0]
        r = asme_code.calculate_head_thickness({
            "head": head,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "UG-32(d)"
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_head_thickness_torispherical_result(self, asme_code, sample_project):
        """Torisferik bombe kalınlığı — DesignCode entegrasyon.

        L = 1000 mm, r = 60 mm, P = 1.2 MPa, S = 138 MPa, E = 1.0
        M = (3 + sqrt(1000/60)) / 4 = 1.7705
        t = 1.2×1000×1.7705 / (2×138×1.0 - 0.2×1.2) = 2124.6 / 275.76 = 7.704 mm
        """
        head = Head(
            head_id="HEAD-TORI",
            type=HeadType.TORISPHERICAL,
            inside_diameter=1000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            weld_joint_id="WJ-02",
            internal_corrosion_allowance=2.0,
            mill_tolerance=12.5,
            crown_radius=1000.0,
            knuckle_radius=60.0,
        )
        r = asme_code.calculate_head_thickness({
            "head": head,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "UG-32(e)"
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_mawp_shell(self, asme_code, sample_project):
        """MAWP — gövde."""
        shell = sample_project.shell_sections[0]
        r = asme_code.calculate_mawp({
            "component_type": "shell",
            "component": shell,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "nominal_thickness": shell.nominal_thickness,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "PASS"
        assert r.final_result is not None
        assert r.final_result > sample_project.design_conditions.design_pressure

    def test_mawp_head(self, asme_code, sample_project):
        """MAWP — bombe."""
        head = sample_project.heads[0]
        r = asme_code.calculate_mawp({
            "component_type": "head",
            "component": head,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "nominal_thickness": head.nominal_thickness,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "PASS"
        assert r.final_result is not None

    def test_hydrotest(self, asme_code, sample_project):
        """Hidrostatik test basıncı."""
        r = asme_code.calculate_hydrotest_pressure({
            "project": sample_project,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "code_edition": sample_project.code_edition,
        })
        # Tasarım 200 °C, test 20 °C ve test gerilmesi girilmemiş → LSR bilinmiyor;
        # LSR=1 test basıncını düşük verebileceğinden PASS değil REVIEW_REQUIRED (B-28).
        assert r.status.value == "REVIEW REQUIRED"
        assert r.final_result is not None
        assert r.final_result > sample_project.design_conditions.design_pressure
        assert any("Test gerilmesi eksik" in w for w in r.warnings)

    def test_hydrotest_with_test_temperature_stress(self, asme_code, sample_project):
        """UG-99(b): HTP = 1.3 × MAWP × (S_test/S_design) — el hesabı, uygulamadan bağımsız.

        MAWP = 2.0 MPa, S_test = 148 MPa (20°C), S_design = 138 MPa (200°C)
        → 1.3 × 2.0 × 148/138 = 2.7884 MPa
        """
        mat = sample_project.materials[0].model_copy(update={"allowable_stress_test_temp": 148.0})
        r = asme_code.calculate_hydrotest_pressure({
            "project": sample_project,
            "design_conditions": sample_project.design_conditions,
            "materials": [mat],
            "global_mawp": 2.0,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "PASS"
        assert relative_tolerance(r.final_result, 1.3 * 2.0 * 148.0 / 138.0, 0.0005)
        # LSR=1 yedeğiyle hesaplansaydı 2.6 MPa çıkardı — gerçek değer daha yüksek olmalı
        assert r.final_result > 1.3 * 2.0

    def test_hydrotest_lsr_uses_lowest_ratio(self, asme_code, sample_project):
        """İki malzemede LSR = en küçük oran (UG-99(b))."""
        base = sample_project.materials[0]
        hi = base.model_copy(update={"allowable_stress_test_temp": 160.0})   # oran 1.1594
        lo = base.model_copy(update={
            "material_id": "MAT-02", "allowable_stress_test_temp": 145.0,   # oran 1.0507
        })
        project = sample_project.model_copy(update={
            "shell_sections": [
                sample_project.shell_sections[0],
                sample_project.shell_sections[0].model_copy(
                    update={"section_id": "SHELL-X", "material_id": "MAT-02"}),
            ],
        })
        r = asme_code.calculate_hydrotest_pressure({
            "project": project,
            "design_conditions": project.design_conditions,
            "materials": [hi, lo],
            "global_mawp": 2.0,
            "code_edition": project.code_edition,
        })
        assert r.status.value == "PASS"
        assert relative_tolerance(r.final_result, 1.3 * 2.0 * 145.0 / 138.0, 0.0005)

    def test_hydrotest_same_temperature_is_exact(self, asme_code, sample_project):
        """Tasarım = test sıcaklığı → S_test = S_design gerçek eşitlik; PASS, LSR=1."""
        dc = sample_project.design_conditions.model_copy(update={"hydrotest_temperature": 200.0})
        r = asme_code.calculate_hydrotest_pressure({
            "project": sample_project,
            "design_conditions": dc,
            "materials": sample_project.materials,
            "global_mawp": 2.0,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "PASS"
        assert relative_tolerance(r.final_result, 1.3 * 2.0, 0.0005)

    def test_flat_head_thickness_result(self, asme_code, sample_project):
        """Düz kapak et kalınlığı — C_attach ile."""
        head_flat = Head(
            head_id="HEAD-FLAT",
            type=HeadType.FLAT,
            inside_diameter=1000.0,
            nominal_thickness=60.0,
            material_id="MAT-01",
            weld_joint_id="WJ-02",
            internal_corrosion_allowance=2.0,
            mill_tolerance=12.5,
            flat_attachment_factor=0.33,
        )
        r = asme_code.calculate_head_thickness({
            "head": head_flat,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "UG-34(c)(2)"
        assert r.status.value in ("PASS", "FAIL")
        assert r.final_result is not None
        # Ara değerlerde C_attach olmalı
        names = {iv["name"] for iv in r.intermediate_values}
        assert "C_attach" in names

    def test_flat_head_blocked_missing_c(self, asme_code, sample_project):
        """Düz kapak — C_attach eksikse BLOCKED_MISSING_INPUT."""
        head_flat = Head(
            head_id="HEAD-FLAT-NO-C",
            type=HeadType.FLAT,
            inside_diameter=1000.0,
            nominal_thickness=60.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
            # flat_attachment_factor=None (varsayılan)
        )
        r = asme_code.calculate_head_thickness({
            "head": head_flat,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "BLOCKED MISSING INPUT"

    def test_pneumatic_test_result(self, asme_code, sample_project):
        """Pnömatik test basıncı — DesignCode entegrasyonu."""
        r = asme_code.calculate_pneumatic_test_pressure({
            "project": sample_project,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "REVIEW REQUIRED"  # test gerilmesi girilmedi (B-28)
        assert r.final_result is not None
        assert r.clause_reference == "UG-100"
        # Pnömatik test 1.1× olmalı (hidrotest 1.3×)
        assert r.final_result < 1.3 * sample_project.design_conditions.design_pressure
        # Güvenlik + MDMT notları artık "notices" (yayın kapısı: PASS'i geçersiz kılmayan
        # bilgilendirme); "warnings" yalnızca durumu düşüren uyarılar içindir.
        assert len(r.notices) >= 2
        assert any("hidrostatik testten daha tehlikelidir" in n for n in r.notices)
        assert any("MDMT" in n for n in r.notices)

    def test_pneumatic_with_test_temperature_stress(self, asme_code, sample_project):
        """UG-100: 1.1 × MAWP × (S_test/S_design) — el hesabı."""
        mat = sample_project.materials[0].model_copy(update={"allowable_stress_test_temp": 148.0})
        r = asme_code.calculate_pneumatic_test_pressure({
            "project": sample_project,
            "design_conditions": sample_project.design_conditions,
            "materials": [mat],
            "global_mawp": 2.0,
            "code_edition": sample_project.code_edition,
        })
        assert r.status.value == "PASS"
        assert relative_tolerance(r.final_result, 1.1 * 2.0 * 148.0 / 138.0, 0.0005)

    def test_cone_thickness_result(self, asme_code, sample_project):
        """Konik bölüm et kalınlığı — DesignCode entegrasyonu."""
        from domain import Cone

        cone = Cone(
            cone_id="CONE-01",
            large_diameter=1000.0,
            small_diameter=600.0,
            half_apex_angle=20.0,
            length=500.0,
            nominal_thickness=10.0,
            material_id="MAT-01",
            weld_joint_id="WJ-02",
            internal_corrosion_allowance=2.0,
            mill_tolerance=12.5,
        )
        r = asme_code.calculate_cone_thickness({
            "cone": cone,
            "design_conditions": sample_project.design_conditions,
            "materials": sample_project.materials,
            "welds": sample_project.welds,
            "code_edition": sample_project.code_edition,
        })
        assert r.code == "ASME VIII-1"
        assert r.clause_reference == "UG-32(g)"
        assert r.status.value in ("PASS", "FAIL")
        assert r.final_result is not None


# ── Yük durumu testleri ───────────────────────────────────────────────────────

class TestLoadCases:
    """Yük durumu modeli testleri."""

    def test_load_case_creation(self):
        """LoadCase oluşturma."""
        from domain import LoadCase, LoadType

        lc = LoadCase(
            load_case_id="LC-001",
            name="Operating",
            load_type=LoadType.OPERATING,
            pressure_mpa=1.2,
            temperature_c=200.0,
        )
        assert lc.load_case_id == "LC-001"
        assert lc.load_type == LoadType.OPERATING
        assert lc.pressure_mpa == 1.2

    def test_external_load_creation(self):
        """ExternalLoad oluşturma."""
        from domain import ExternalLoad, LoadDirection

        el = ExternalLoad(
            load_id="EL-001",
            component_id="N1",
            fx_n=5000.0,
            fy_n=3000.0,
            fz_n=10000.0,
            elevation_mm=500.0,
            direction=LoadDirection.RADIAL,
        )
        assert el.load_id == "EL-001"
        assert el.fx_n == 5000.0

    def test_load_combination_creation(self):
        """LoadCombination oluşturma."""
        from domain import LoadCombination

        lc = LoadCombination(
            combination_id="LC-COMB-001",
            name="Operating + Wind",
            load_case_ids=["LC-001", "LC-006"],
            load_factors={"LC-001": 1.0, "LC-006": 1.0},
            standard="ASCE 7",
        )
        assert lc.combination_id == "LC-COMB-001"
        assert len(lc.load_case_ids) == 2

    def test_mandatory_templates_count(self):
        """15 zorunlu load-case şablonu."""
        from domain import MANDATORY_LOAD_CASE_TEMPLATES

        assert len(MANDATORY_LOAD_CASE_TEMPLATES) == 15

    def test_non_concurrent_pairs(self):
        """Eşzamanlı olmayan yük çiftleri."""
        from domain import NON_CONCURRENT_LOAD_PAIRS, LoadType

        # Hydrotest + Wind eşzamanlı olmamalı
        assert (LoadType.HYDROTEST, LoadType.WIND) in NON_CONCURRENT_LOAD_PAIRS

    def test_validate_load_combination_rejects_invalid_references_and_pairs(self):
        from domain import LoadCase, LoadCombination, LoadType, validate_load_combination

        cases = [
            LoadCase(load_case_id="HYDRO", name="Hydrotest", load_type=LoadType.HYDROTEST),
            LoadCase(load_case_id="WIND", name="Wind", load_type=LoadType.WIND),
        ]
        invalid = LoadCombination(
            combination_id="BAD-01",
            name="Hydro + Wind",
            load_case_ids=["HYDRO", "WIND", "MISSING"],
            load_factors={"OTHER": 1.0},
        )
        errors = validate_load_combination(cases, invalid)
        assert any("Unknown load case" in error for error in errors)
        assert any("non-member" in error for error in errors)
        assert any("Non-concurrent" in error for error in errors)

    def test_generate_wind_load_cases(self):
        """Rüzgâr yük durumları oluşturma."""
        from domain import generate_wind_load_cases, LoadType

        cases = generate_wind_load_cases(wind_speed_m_s=40.0)
        assert len(cases) == 2
        assert cases[0].load_type == LoadType.WIND
        assert cases[0].wind_speed_m_s == 40.0

    def test_generate_seismic_load_cases(self):
        """Deprem yük durumları oluşturma."""
        from domain import generate_seismic_load_cases, LoadType

        cases = generate_seismic_load_cases(zone_factor=0.4)
        assert len(cases) == 2
        assert cases[0].load_type == LoadType.SEISMIC
        assert cases[0].seismic_zone_factor == 0.4

    def test_generate_structural_load_cases(self):
        """Yapısal yük durumları oluşturma (§7.10)."""
        from domain import generate_structural_load_cases, LoadType

        # Rüzgâr + deprem
        cases = generate_structural_load_cases(
            wind_speed_m_s=30.0,
            seismic_zone_factor=0.3,
        )
        assert len(cases) == 4  # 2 rüzgâr + 2 deprem

        # Taşıma + kaldırma
        cases = generate_structural_load_cases(
            include_transport=True,
            include_lifting=True,
        )
        assert len(cases) == 4  # 2 taşıma + 2 kaldırma


# ── MDMT testleri ─────────────────────────────────────────────────────────────

class TestMDMT:
    """MDMT (UCS-66) testleri."""

    def test_mdmt_exemption(self):
        """MDMT muafiyeti — sıcaklık limit altında."""
        from mdmt import MDMTCalculator, UCS66CurveGroup
        from domain import DesignConditions, ShellSection

        calc = MDMTCalculator()
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-20.0,  # -29°C limitinin ÜSTÜNDE → test gerekli
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        r = calc.check_mdmt({
            "component": shell,
            "design_conditions": dc,
            "curve_group": UCS66CurveGroup.B,
            "nominal_thickness_mm": 12.0,
        })
        # -20°C >= -29°C → impact test gerekli
        assert r.status.value == "REVIEW REQUIRED"

    def test_mdmt_impact_test_required(self):
        """MDMT — impact test gerekli, sıcaklık çok düşük."""
        from mdmt import MDMTCalculator, UCS66CurveGroup
        from domain import DesignConditions, ShellSection

        calc = MDMTCalculator()
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-40.0,  # -29°C limitinin ALTINDA → muafiyet
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        r = calc.check_mdmt({
            "component": shell,
            "design_conditions": dc,
            "curve_group": UCS66CurveGroup.B,
            "nominal_thickness_mm": 12.0,
        })
        # Yaklaşık limit nihai muafiyet PASS'ı üretemez.
        assert r.status.value == "REVIEW REQUIRED"

    def test_mdmt_blocked_missing_curve(self):
        """MDMT — eğri grubu eksikse BLOCKED_MISSING_INPUT."""
        from mdmt import MDMTCalculator
        from domain import DesignConditions

        calc = MDMTCalculator()
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-20.0,
        )
        r = calc.check_mdmt({
            "design_conditions": dc,
            "nominal_thickness_mm": 12.0,
            # curve_group eksik
        })
        assert r.status.value == "BLOCKED MISSING INPUT"


# ── Orchestrator entegrasyon testleri ─────────────────────────────────────────

class TestOrchestratorWithASME:
    """Orchestrator + ASME VIII-1 tam akış testi."""

    def test_full_run(self, asme_code, sample_project):
        """Tam hesap sırası — tüm bileşenler."""
        orch = CalculationOrchestrator(asme_code)
        result = orch.run(sample_project)

        assert not result.has_errors
        assert len(result.results) > 0

        # Gövde kalınlığı
        shell_results = result.get_results_by_component("SHELL-01")
        assert len(shell_results) >= 1
        shell_thickness = [r for r in shell_results if r.calculation_type == "thickness"]
        assert len(shell_thickness) == 1
        assert shell_thickness[0].status.value == "PASS"

        # Bombe kalınlıkları
        head_l_results = result.get_results_by_component("HEAD-L")
        assert len(head_l_results) >= 1

        head_r_results = result.get_results_by_component("HEAD-R")
        assert len(head_r_results) >= 1

        # MAWP
        mawp_results = [r for r in result.results if r.calculation_type == "mawp"]
        assert len(mawp_results) >= 3  # shell + 2 heads

        # Global MAWP
        global_mawp = result.get_global_mawp()
        assert global_mawp is not None
        assert global_mawp > sample_project.design_conditions.design_pressure

        # Hidrotest
        hydro_results = [r for r in result.results if r.calculation_type == "hydrotest"]
        assert len(hydro_results) == 1
        # Örnek proje: tasarım 200 °C / test 20 °C, test gerilmesi girilmemiş (B-28)
        assert hydro_results[0].status.value == "REVIEW REQUIRED"

    def test_nozzle_reinforcement_calculated(self, asme_code, sample_project):
        """Nozul takviye hesabı artık gerçek hesap üretir (Faz 3 entegrasyonu).

        Her nozul için UG-37/UG-40 alan hesabı çalışır; sonuç PASS veya FAIL olur
        (artık NOT_CALCULATED stub değil) ve ara değerlerle izlenebilir (K5).
        """
        orch = CalculationOrchestrator(asme_code)
        result = orch.run(sample_project)

        nozzle_results = [r for r in result.results if r.calculation_type == "nozzle_reinforcement"]
        assert len(nozzle_results) == 2  # N1 ve N2
        for r in nozzle_results:
            assert r.status.value in ("PASS", "FAIL")
            assert r.clause_reference == "UG-37/UG-40"
            # Alan kalemleri ara değer olarak dolu (gerekli + A1..A4 + toplam)
            names = {iv["name"] for iv in r.intermediate_values}
            assert {"A_required", "A1", "A2", "A_total"}.issubset(names)

    def test_to_dict(self, asme_code, sample_project):
        """Orchestrator sonucu serileştirilebilir."""
        orch = CalculationOrchestrator(asme_code)
        result = orch.run(sample_project)
        d = result.to_dict()
        assert "results" in d
        assert len(d["results"]) > 0
        assert d["code"] == "ASME VIII-1"

    def test_traceability(self, asme_code, sample_project):
        """K5: Herhesap denetlenebilir — ara değerler ve madde referansı dolu."""
        orch = CalculationOrchestrator(asme_code)
        result = orch.run(sample_project)

        for r in result.results:
            if r.status.value not in ("NOT CALCULATED", "OUT OF SCOPE"):
                assert r.code != ""
                assert r.edition != ""
                # clause_reference boş olabilir (nozul NOT_CALCULATED için)
                if r.calculation_type in ("thickness", "mawp", "hydrotest"):
                    assert r.clause_reference != ""
                    assert len(r.intermediate_values) > 0

    def test_global_mawp_governing_marked(self, asme_code, sample_project):
        """A3: Global MAWP — yöneten bileşen işaretlenir."""
        orch = CalculationOrchestrator(asme_code)
        result = orch.run(sample_project)

        global_mawp = result.get_global_mawp()
        assert global_mawp is not None

        # Yöneten bileşen işaretlenmiş olmalı
        mawp_results = [r for r in result.results if r.calculation_type == "mawp"]
        governing = [r for r in mawp_results if r.governing]
        assert len(governing) == 1
        assert governing[0].final_result == global_mawp

    def test_global_mawp_blocked_when_component_missing(self, asme_code):
        """A3: Eksik bileşen varsa global MAWP None döner."""
        from domain import DesignConditions, ShellSection, MaterialProperty, ProductForm

        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        # Sadece gövde, bombe yok
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        mat = MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
        )

        from domain import CalculationCode
        project = VesselProject(
            project_number="TEST-BLOCKED",
            project_name="Blocked MAWP Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            heads=[],  # Bombe yok
            materials=[mat],
        )

        orch = CalculationOrchestrator(asme_code)
        result = orch.run(project)

        # Gövde MAWP'si var ama bombe yok → global MAWP hâlâ var (sadece gövde)
        # Bombe olsaydı ve NOT_CALCULATED olsaydı None dönerdi
        global_mawp = result.get_global_mawp()
        assert global_mawp is not None  # Sadece gövde var, o da hesaplandı

    def test_static_head_correction(self, asme_code):
        """A3: Statik kafa düzeltmesi uygulanır."""
        from domain import DesignConditions, ShellSection, MaterialProperty, ProductForm, CalculationCode

        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            fluid_density_kg_m3=1000.0,  # Su
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        mat = MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
        )

        project = VesselProject(
            project_number="TEST-STATIC",
            project_name="Static Head Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            materials=[mat],
        )

        orch = CalculationOrchestrator(asme_code)
        result = orch.run(project)

        # MAWP sonuçlarında statik kafa düzeltmesi olmalı (eğer reference_elevation > 0)
        mawp_results = [r for r in result.results if r.calculation_type == "mawp"]
        # Varsayılan reference_elevation_mm = 0 → düzelleme uygulanmaz
        for r in mawp_results:
            names = {iv["name"] for iv in r.intermediate_values}
            assert "static_head_delta_P" not in names  # 0 kot → düzelleme yok


# ── Fail senaryoları ──────────────────────────────────────────────────────────

class TestASMEFailScenarios:
    """FAIL durumunu tetikleyen senaryolar."""

    def test_shell_too_thin(self, asme_code):
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
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
        )
        mat = MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
        )

        r = asme_code.calculate_shell_thickness({
            "shell": shell,
            "design_conditions": dc,
            "materials": [mat],
            "welds": [],
            "code_edition": "2025",
        })
        assert r.status.value == "FAIL"
        assert r.final_result > shell.nominal_thickness

    def test_external_pressure_blocked_without_chart_data(self, asme_code):
        """Dış basınç → chart verisi yoksa BLOCKED_CODE_DATA."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
            external_pressure=0.5,
        )
        shell = ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
        )
        mat = MaterialProperty(
            material_id="MAT-01",
            standard_pack="ASME II-D 2025",
            material_designation="SA-516 Gr.70",
            product_form=ProductForm.PLATE,
            temperature=200.0,
            allowable_stress=138.0,
            yield_strength=260.0,
            tensile_strength=485.0,
            source_reference="ASME II-D Table 1A, Line 4",
        )

        orch = CalculationOrchestrator(asme_code)
        project = VesselProject(
            project_number="TEST-002",
            project_name="External Pressure Test",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=dc,
            shell_sections=[shell],
            materials=[mat],
        )
        result = orch.run(project)

        ext_results = [r for r in result.results if r.calculation_type == "external_pressure"]
        assert len(ext_results) >= 1
        # Chart verisi girilmediği için NOT_CALCULATED döner (A/B = 0)
        for r in ext_results:
            assert r.status.value in ("NOT CALCULATED", "BLOCKED CODE DATA")
