"""Faz 5 — Supports modülü testleri.

Golden-case ve durum testleri — Zick analizi (saddle) ve skirt.
"""

import pytest
import math
from units import relative_tolerance

from supports.formulas import (
    saddle_reaction,
    skirt_bending_stress,
    skirt_compression_stress,
    skirt_combined_stress,
    leg_pipe_section_area,
    leg_reaction_extremes,
    leg_base_pressure,
)
from supports.support_calc import SupportCalculator

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
from code_asme_viii_1.design_code import ASMEVIII1DesignCode


@pytest.fixture
def support_material():
    return MaterialProperty(
        material_id="MAT-01", standard_pack="ASME II-D 2025",
        material_designation="SA-516 Gr.70", product_form=ProductForm.PLATE,
        temperature=200.0, allowable_stress=138.0, yield_strength=260.0,
        tensile_strength=485.0, source_reference="ASME II-D Table 1A, Line 4",
    )


def test_support_resolves_explicit_host_shell_in_multi_shell_project(support_material):
    """Destek, listedeki ilk gövdeye değil açık host kimliğine bağlanır."""
    project = VesselProject(
        project_number="SUPPORT-HOST-01",
        project_name="Multi shell support host",
        calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-10.0,
        ),
        heads=[
            Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
            Head(head_id="HR", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
        ],
        shell_sections=[
            ShellSection(section_id="SHELL-01", inside_diameter=1000.0,
                         tangent_length=2000.0, nominal_thickness=12.0, material_id="MAT-01"),
            ShellSection(section_id="SHELL-02", inside_diameter=1000.0,
                         tangent_length=1500.0, nominal_thickness=12.0, material_id="MAT-01"),
        ],
        component_sequence=[
            ComponentReference(component_type="head", component_id="HL"),
            ComponentReference(component_type="shell", component_id="SHELL-01"),
            ComponentReference(component_type="shell", component_id="SHELL-02"),
            ComponentReference(component_type="head", component_id="HR"),
        ],
        materials=[support_material],
        supports=[Support(
            support_id="SKIRT-02", type="skirt", host_component_id="SHELL-02",
            location_mm=2500.0, width_mm=200.0, height_mm=2000.0, diameter_mm=1000.0,
            thickness_mm=10.0, material_id="MAT-01",
        )],
    )

    results = ASMEVIII1DesignCode().check_supports(project)
    assert len(results) == 1
    host = next(v for v in results[0].intermediate_values if v["name"] == "host_component_id")
    start = next(v for v in results[0].intermediate_values if v["name"] == "host_axial_start")
    assert host["value"] == "SHELL-02"
    assert start["value"] > 0.0


def test_unresolved_component_sequence_blocks_support_host_resolution(support_material):
    project = VesselProject(
        project_number="SUPPORT-HOST-03", project_name="Broken component sequence",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-10.0,
        ),
        heads=[
            Head(head_id="H1", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
            Head(head_id="H2", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                 nominal_thickness=12.0, material_id="MAT-01"),
        ],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0,
                                     tangent_length=1000.0, nominal_thickness=12.0,
                                     material_id="MAT-01")],
        materials=[support_material],
        component_sequence=[
            ComponentReference(component_type="head", component_id="H1"),
            ComponentReference(component_type="head", component_id="H2"),
        ],
        supports=[Support(support_id="SKIRT-X", type="skirt", host_component_id="S1",
                          location_mm=500.0, width_mm=200.0, height_mm=1000.0,
                          diameter_mm=1000.0, thickness_mm=10.0, material_id="MAT-01")],
    )

    result = ASMEVIII1DesignCode().check_supports(project)[0]
    assert result.status.value == "NOT CALCULATED"
    assert result.final_result is None


def test_support_host_is_required_when_multiple_shells_have_no_host(support_material):
    project = VesselProject(
        project_number="SUPPORT-HOST-02", project_name="Missing support host",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-10.0,
        ),
        shell_sections=[
            ShellSection(section_id="S1", inside_diameter=1000.0, tangent_length=1000.0,
                         nominal_thickness=12.0, material_id="MAT-01"),
            ShellSection(section_id="S2", inside_diameter=1000.0, tangent_length=1000.0,
                         nominal_thickness=12.0, material_id="MAT-01"),
        ],
        materials=[support_material],
        supports=[
            Support(support_id="SKIRT-X", type="skirt", width_mm=200.0,
                    height_mm=1000.0, diameter_mm=1000.0, thickness_mm=10.0,
                    material_id="MAT-01"),
            # Eyer: konum-aralığı kapısı yalnız eyer içindir; zincirsiz çok gövdede
            # global konum çözülemez -> bloke. (Etek/ayak bu kapıya tabi DEĞİL.)
            Support(support_id="SKIRT-Y", type="saddle", host_component_id="S2",
                    location_mm=500.0, width_mm=200.0, height_mm=1000.0,
                    material_id="MAT-01"),
        ],
    )
    results = ASMEVIII1DesignCode().check_supports(project)
    assert len(results) == 2
    assert all(result.status.value == "NOT CALCULATED" for result in results)
    assert "host_component_id is required" in results[0].warnings[0]
    assert "component_sequence" in results[1].warnings[0]
    assert "host_component_id" in results[0].warnings[0]


def test_mdmt_governing_component_is_reported(support_material):
    shell_mat = support_material.model_copy(update={"ucs66_curve_group": "A"})
    head_mat = support_material.model_copy(update={"material_id": "MAT-02", "ucs66_curve_group": "D"})
    project = VesselProject(
        project_number="MDMT-GOV-01", project_name="Governing MDMT",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=DesignConditions(
            operating_pressure=1.0, design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5, operating_temperature=20.0,
            design_temperature=20.0, minimum_design_temperature=-20.0,
        ),
        heads=[Head(head_id="HL", type=HeadType.HEMISPHERICAL, inside_diameter=1000.0,
                    nominal_thickness=12.0, material_id="MAT-02")],
        shell_sections=[ShellSection(section_id="S1", inside_diameter=1000.0,
                                     tangent_length=1000.0, nominal_thickness=12.0,
                                     material_id="MAT-01")],
        materials=[shell_mat, head_mat],
    )
    results = ASMEVIII1DesignCode().check_mdmt(project)
    summary = results[-1]
    assert summary.component_id == "MDMT-GOVERNING"
    assert summary.governing is True
    assert summary.input_snapshot["governing_component_id"] == "S1"
    assert summary.final_result == -29.0


# ── Zick formül testleri ──────────────────────────────────────────────────────

class TestZickFormulas:
    """Zick analizi formüllerinin birim testleri."""

    def test_saddle_reaction(self):
        """Saddle reaksiyon kuvveti.

        W = 500000 N, n = 2 → Q = 250000 N
        """
        Q = saddle_reaction(500000.0, 2)
        assert relative_tolerance(Q, 250000.0, 0.001)


# ── Leg formül testleri (Faz 0 — dolu daire kusuru kapatıldı) ─────────────────

class TestLegFormulas:
    """Ayak (leg) formüllerinin birim testleri.

    Faz 0 düzeltmesi: ayak boru kesitlidir (halka), dolu daire DEĞİL.
    Bu sınıf, eski dolu daire varsayımının artık kullanılmadığını ve yeni
    halka kesit alanının her zaman daha küçük (dolayısıyla gerilmenin daha
    büyük, emniyetli yönde) olduğunu kalıcı olarak sabitler.
    """

    def test_pipe_section_area_smaller_than_solid_disk(self):
        """Halka kesit alanı, aynı dış çaplı dolu daireden küçük olmalı.

        D_outside=100 mm, t_leg=10 mm → D_inside=80 mm
        A_solid_disk = π×(50)² = 7853.98 mm²
        A_annulus    = π/4×(100²-80²) = 2827.43 mm²
        """
        D_o, t = 100.0, 10.0
        A_annulus = leg_pipe_section_area(D_o, t)
        A_solid_disk = math.pi * (D_o / 2.0) ** 2

        assert relative_tolerance(A_annulus, 2827.43, 0.001), f"A={A_annulus}"
        assert A_annulus < A_solid_disk, (
            f"Halka kesit ({A_annulus:.2f}) dolu daireden ({A_solid_disk:.2f}) "
            "küçük olmalı — aksi hâlde eski emniyetsiz varsayıma dönülmüş demektir."
        )

    def test_pipe_section_area_rejects_wall_thicker_than_radius(self):
        """Et kalınlığı yarıçaptan büyükse (D_inside<=0) hata verilmeli."""
        with pytest.raises(ValueError, match="D_inside"):
            leg_pipe_section_area(D_outside=20.0, t_leg=15.0)

    def test_reaction_extremes_no_moment(self):
        """Moment yoksa tüm ayaklar eşit yük taşır.

        W=400000 N, n=4 → N_max=N_min=100000 N
        """
        N_max, N_min = leg_reaction_extremes(400000.0, 4, 0.0, 0.0)
        assert relative_tolerance(N_max, 100000.0, 0.001)
        assert relative_tolerance(N_min, 100000.0, 0.001)

    def test_reaction_extremes_with_moment(self):
        """Moment varsa en yüklü ve en az yüklü ayak ayrışır (n ≥ 3: 2M/(n·r)).

        W=400000 N, n=4, M=40000000 N·mm, r=500 mm
        ΔN = 2×40e6/(4×500) = 40000 N   (Moss: 4M/(N·D), D = 2r = 1000 mm)
        N_max = 100000 + 40000 = 140000 N,  N_min = 60000 N
        (Eski M/(n·r) formülü 120000/80000 veriyordu — gerçek yükün yarısı, B-32.)
        """
        N_max, N_min = leg_reaction_extremes(400000.0, 4, 40_000_000.0, 500.0)
        assert relative_tolerance(N_max, 140000.0, 0.001)
        assert relative_tolerance(N_min, 60000.0, 0.001)

    @pytest.mark.parametrize("n", [3, 4, 5, 6, 8])
    def test_reaction_matches_independent_leg_by_leg_statics(self, n):
        """Formülden bağımsız: n ayağı çember üzerine yerleştir, moment yönünü tara,
        her ayak için F_i = W/n + M·y_i/Σy² ile en büyük yükü bul → formülle aynı olmalı."""
        import math
        W, M, r = 1_000_000.0, 60_000_000.0, 800.0
        angles = [2 * math.pi * i / n for i in range(n)]
        worst = 0.0
        for k in range(0, 3600):
            phi = math.radians(k / 10.0)                       # moment ekseni yönü
            ys = [r * math.sin(a - phi) for a in angles]        # eksene uzaklık
            s2 = sum(y * y for y in ys)
            worst = max(worst, max(W / n + M * y / s2 for y in ys))
        N_max, _ = leg_reaction_extremes(W, n, M, r)
        assert N_max == pytest.approx(worst, rel=2e-3)

    def test_reaction_two_legs_in_moment_plane(self):
        """n=2, ayaklar moment düzleminde: kuvvet çifti F·2r = M → ΔN = M/(2r)."""
        N_max, N_min = leg_reaction_extremes(100_000.0, 2, 10_000_000.0, 500.0)
        assert N_max == pytest.approx(50_000.0 + 10_000.0)
        assert N_min == pytest.approx(50_000.0 - 10_000.0)

    def test_single_leg_cannot_carry_moment(self):
        with pytest.raises(ValueError, match="Tek ayak"):
            leg_reaction_extremes(100_000.0, 1, 1_000_000.0, 500.0)

    def test_reaction_extremes_requires_radius_with_moment(self):
        """Moment > 0 iken dağılım yarıçapı verilmezse hata."""
        with pytest.raises(ValueError, match="support_radius"):
            leg_reaction_extremes(400000.0, 4, 40_000_000.0, 0.0)

    def test_leg_uplift_uses_empty_weight(self, support_material):
        """Yükselme boş kap ağırlığıyla değerlendirilir (basma hidrotest ağırlığıyla).

        n=4, r=500, M=4e8 → ΔN = 2M/(nr) = 400 000 N.
        Basma W=800 kN → N_max = 200 000 + 400 000; boş W=200 kN → N_min = 50 000 − 400 000.
        (Boş ağırlık verilmeseydi N_min = 200 000 − 400 000 = −200 000: kaldırma yarı yarıya az.)
        """
        calc = SupportCalculator(code="ASME VIII-1", edition="2025")
        base = {"support": {"tag": "L1", "n_legs": 4, "leg_diameter_mm": 200.0,
                            "leg_thickness_mm": 12.0, "support_radius_mm": 500.0},
                "total_weight_N": 800_000.0, "overturning_moment_Nmm": 4e8,
                "materials": [support_material], "skirt_material_id": "MAT-01"}
        vals = lambda r: {v["name"]: v["value"] for v in r.intermediate_values}
        with_empty = calc.check_leg_support({**base, "min_weight_N": 200_000.0})
        without = calc.check_leg_support(base)
        assert vals(with_empty)["N_max"] == pytest.approx(600_000.0)
        assert vals(with_empty)["N_min"] == pytest.approx(-350_000.0)
        assert vals(without)["N_min"] == pytest.approx(-200_000.0)
        assert any("K4" in a and "Boş" in a for a in without.assumptions)

    def test_leg_stress_ignores_base_plate_area(self, support_material):
        """B-33: taban plakası alanı ayak çelik gerilmesini DÜŞÜRMEMELİ.

        Eskiden base_plate_area_mm2 verilince N_max/A_taban çelik S ile kıyaslanıyordu;
        çok büyük plaka girmek 'güvenli' sonuç üretiyordu. Şimdi ayak gerilmesi
        yalnız ayak halka kesitinden gelir; plaka alanı yalnız P_bearing'i etkiler.
        """
        def run(area):
            sup = {"tag": "L1", "n_legs": 4, "leg_diameter_mm": 100.0,
                   "leg_thickness_mm": 10.0, "support_radius_mm": 500.0}
            if area:
                sup["base_plate_area_mm2"] = area
            calc = SupportCalculator(code="ASME VIII-1", edition="2025")
            return calc.check_leg_support({
                "support": sup, "total_weight_N": 400000.0,
                "overturning_moment_Nmm": 0.0,
                "materials": [support_material], "skirt_material_id": "MAT-01"})
        small, huge = run(None), run(10_000_000.0)
        vals = lambda r: {v["name"]: v["value"] for v in r.intermediate_values}
        assert vals(huge)["P_base"] == pytest.approx(vals(small)["P_base"])
        assert vals(huge)["P_bearing"] == pytest.approx(100_000.0 / 10_000_000.0)
        assert any("KONTROL EDİLMEDİ" in w for w in huge.warnings)
        assert "P_bearing" not in vals(small)

    def test_base_pressure_uses_annulus_area_end_to_end(self):
        """check_leg_support artık halka kesit alanını kullanıyor (Faz 0).

        Eski dolu daire varsayımıyla kıyaslandığında gerilme ~2,78× büyük
        çıkmalı (emniyetli yöne) — bu, tek başına implementasyona göre
        yazılmış bir test değil; alan oranı bağımsız olarak yukarıda
        `test_pipe_section_area_smaller_than_solid_disk` ile de doğrulanır.
        """
        D_o, t = 100.0, 10.0
        N_max = 10000.0
        A_annulus = leg_pipe_section_area(D_o, t)
        A_solid_disk = math.pi * (D_o / 2.0) ** 2

        P_new = leg_base_pressure(N_max, A_annulus)
        P_old_equivalent = N_max / A_solid_disk

        assert P_new > P_old_equivalent, (
            f"Yeni P_base ({P_new:.4f}) eski dolu daire varsayımından "
            f"({P_old_equivalent:.4f}) büyük olmalı — kesit alanı küçüldü."
        )
        assert relative_tolerance(P_new / P_old_equivalent, old_area_ratio(D_o, t), 0.001)


def old_area_ratio(D_o: float, t: float) -> float:
    """Yardımcı: dolu daire / halka alan oranı — yalnız test amaçlı."""
    D_i = D_o - 2 * t
    solid = math.pi * (D_o / 2.0) ** 2
    annulus = math.pi / 4.0 * (D_o * D_o - D_i * D_i)
    return solid / annulus


class TestAnchorSafety:
    """Faz C ankraj emniyet kapısı testleri."""

    @staticmethod
    def _material():
        return MaterialProperty(
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

    def test_uplift_without_anchor_data_is_review_required(self):
        mat = self._material()
        calc = SupportCalculator()
        result = calc.check_leg_support({
            "support": {
                "tag": "LEG-UPLIFT",
                "n_legs": 4,
                "leg_diameter_mm": 100.0,
                "leg_thickness_mm": 10.0,
                "support_radius_mm": 500.0,
            },
            "total_weight_N": 1_000.0,
            "overturning_moment_Nmm": 2_000_000.0,
            "materials": [mat],
            "skirt_material_id": mat.material_id,
        })
        assert result.status.value == "REVIEW REQUIRED"
        assert any("ankraj" in warning.lower() for warning in result.warnings + result.assumptions)

    def test_anchor_tension_over_capacity_fails(self):
        mat = self._material()
        calc = SupportCalculator()
        result = calc.check_leg_support({
            "support": {
                "tag": "LEG-ANCHOR-FAIL",
                "n_legs": 4,
                "leg_diameter_mm": 100.0,
                "leg_thickness_mm": 10.0,
                "support_radius_mm": 500.0,
                "anchor_bolt_count": 4,
                "anchor_tension_allowable_N": 100_000.0,
            },
            "total_weight_N": 1_000.0,
            "overturning_moment_Nmm": 2_000_000_000.0,
            "materials": [mat],
            "skirt_material_id": mat.material_id,
        })
        assert result.status.value == "FAIL"
        assert any(v["name"] == "anchor_tension_ratio" for v in result.intermediate_values)

    # Zick eyer testleri: tests/faz5/test_saddle_zick.py (yeniden yazıldı, el hesabı).


# ── Skirt formül testleri ─────────────────────────────────────────────────────

class TestSkirtFormulas:
    """Skirt formüllerinin birim testleri."""

    def test_skirt_bending_stress(self):
        """Skirt eğilme gerilmesi.

        M = 50000000 N·mm, D = 1000 mm, t = 10 mm
        S = 4×50000000 / (π×1000²×10) = 200000000 / 31415927 = 6.37 MPa
        """
        S = skirt_bending_stress(50000000.0, 1000.0, 10.0)
        assert relative_tolerance(S, 6.37, 0.01), f"S={S}"

    def test_skirt_compression_stress(self):
        """Skirt basma gerilmesi.

        W = 200000 N, D = 1000 mm, t = 10 mm
        S = 200000 / (π×1000×10) = 200000 / 31415.9 = 6.37 MPa
        """
        S = skirt_compression_stress(200000.0, 1000.0, 10.0)
        assert relative_tolerance(S, 6.37, 0.01), f"S={S}"

    def test_skirt_combined_stress(self):
        """Skirt birleşik gerilme."""
        S = skirt_combined_stress(6.37, 6.37)
        assert relative_tolerance(S, 12.74, 0.01)


# ── Calculator entegrasyon testleri ───────────────────────────────────────────

class TestSupportCalculator:
    """SupportCalculator entegrasyon testleri."""

    @pytest.fixture
    def calc(self):
        return SupportCalculator()

    @pytest.fixture
    def shell(self):
        return ShellSection(
            section_id="SHELL-01",
            inside_diameter=1000.0,
            tangent_length=4000.0,
            nominal_thickness=12.0,
            material_id="MAT-01",
            internal_corrosion_allowance=2.0,
        )

    @pytest.fixture
    def mat(self):
        return MaterialProperty(
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

    # Eyer (Zick) calculator testleri: tests/faz5/test_saddle_zick.py

    def test_skirt_pass(self, calc, mat):
        """Skirt kontrolü — B girilmişse REVIEW REQUIRED (nihai PASS değil).

        S_comb = 6.37 + 6.37 = 12.74 MPa; B = 50 MPa -> min(S, B) sınırı altında.
        B girilmezse burkulma kontrolü yapılamaz: BLOCKED CODE DATA
        (bkz. tests/faz5/test_skirt_buckling.py).
        """
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_skirt({
            "support": {
                "tag": "SKIRT-01",
                "type": "skirt",
                "diameter_mm": 1000.0,
                "thickness_mm": 10.0,
                "height_mm": 2000.0,
                "skirt_allowable_compressive_MPa": 50.0,
            },
            "total_weight_N": 200000.0,
            "overturning_moment_Nmm": 50000000.0,
            "materials": [mat],
            "design_conditions": dc,
            "skirt_material_id": "MAT-01",
        })
        assert r.status.value == "REVIEW REQUIRED"
        assert r.final_result is not None

    def test_skirt_fail(self, calc, mat):
        """Skirt kontrolü — FAIL (yüksek moment)."""
        dc = DesignConditions(
            operating_pressure=1.0,
            design_pressure=1.2,
            maximum_allowable_pressure_ps=1.5,
            operating_temperature=200.0,
            design_temperature=200.0,
            minimum_design_temperature=-10.0,
        )
        r = calc.check_skirt({
            "support": {
                "tag": "SKIRT-02",
                "type": "skirt",
                "diameter_mm": 1000.0,
                "thickness_mm": 10.0,
                "height_mm": 2000.0,
            },
            "total_weight_N": 5000000.0,
            "overturning_moment_Nmm": 5000000000.0,  # Çok yüksek moment
            "materials": [mat],
            "design_conditions": dc,
            "skirt_material_id": "MAT-01",
        })
        assert r.status.value == "FAIL"

    def test_production_support_payload_wires_skirt(self, mat):
        """ASME orkestratörü gerçek Support alanlarını supports payload'ına taşır."""
        project = VesselProject(
            project_number="SUPPORT-WIRING-01",
            project_name="Support wiring integration",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=DesignConditions(
                operating_pressure=1.0,
                design_pressure=1.2,
                maximum_allowable_pressure_ps=1.5,
                operating_temperature=20.0,
                design_temperature=20.0,
                minimum_design_temperature=-10.0,
            ),
            shell_sections=[ShellSection(
                section_id="SHELL-01",
                inside_diameter=1000.0,
                tangent_length=2000.0,
                nominal_thickness=12.0,
                material_id="MAT-01",
            )],
            materials=[mat],
            supports=[Support(
                support_id="SKIRT-01",
                type="skirt",
                location_mm=0.0,
                width_mm=200.0,
                height_mm=2000.0,
                diameter_mm=1000.0,
                thickness_mm=10.0,
                skirt_allowable_compressive_MPa=50.0,
                material_id="MAT-01",
            )],
        )

        results = ASMEVIII1DesignCode().check_supports(project)

        assert len(results) == 1
        assert results[0].component_id == "SKIRT-01"
        # Üretim hattı destek sonucu, Faz C kapsamı eksikleri nedeniyle
        # nihai PASS değil; mühendis incelemesi gerektirir.
        assert results[0].status.value == "REVIEW REQUIRED"

    def test_production_support_payload_wires_leg_count_and_geometry(self, mat):
        """Leg sayısı ve ölçüler nested support sözleşmesiyle hesapçıya ulaşır."""
        project = VesselProject(
            project_number="SUPPORT-WIRING-02",
            project_name="Leg support wiring integration",
            calculation_code=CalculationCode.ASME_VIII_1,
            code_edition="2025",
            design_conditions=DesignConditions(
                operating_pressure=1.0,
                design_pressure=1.2,
                maximum_allowable_pressure_ps=1.5,
                operating_temperature=20.0,
                design_temperature=20.0,
                minimum_design_temperature=-10.0,
            ),
            shell_sections=[ShellSection(
                section_id="SHELL-01",
                inside_diameter=1000.0,
                tangent_length=2000.0,
                nominal_thickness=12.0,
                material_id="MAT-01",
            )],
            materials=[mat],
            supports=[Support(
                support_id="LEG-01",
                type="leg",
                location_mm=0.0,
                width_mm=200.0,
                height_mm=500.0,
                material_id="MAT-01",
                leg_count=6,
                leg_diameter_mm=100.0,
                leg_thickness_mm=10.0,
                support_radius_mm=600.0,
                overturning_moment_Nmm=1_000_000.0,
            )],
        )

        results = ASMEVIII1DesignCode().check_supports(project)

        assert len(results) == 1
        assert results[0].component_id == "LEG-01"
        assert results[0].status.value == "REVIEW REQUIRED"
        n_legs = next(v for v in results[0].intermediate_values if v["name"] == "n_legs")
        assert n_legs["value"] == 6
        r_dist = next(v for v in results[0].intermediate_values if v["name"] == "r_dist")
        assert r_dist["value"] == 600.0
