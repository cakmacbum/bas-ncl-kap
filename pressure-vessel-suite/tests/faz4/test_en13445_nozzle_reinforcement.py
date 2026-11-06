"""EN 13445-3 Madde 9 — Basınç-alan yöntemiyle nozul takviyesi testleri.

Test senaryoları:
1. Saf formül testleri: elle adım adım hesap (yorumda), sol/sağ taraf göreli tolerans <= %0.5
2. Silindirik gövde üzerinde dik nozul yeterli takviye (REVIEW_REQUIRED)
3. Silindirik gövde üzerinde dik nozul yetersiz takviye (FAIL)
4. PASS durumunun asla dönmediğinin doğrulanması (verified=False -> en fazla REVIEW_REQUIRED)
5. Takviye pedli nozul hesabı (Af_p, term_p)
6. İç çıkıntılı nozul hesabı (l'_bi katkısı)
7. Eğik nozul (inclination_angle != 0) -> OUT_OF_SCOPE
8. Madde 9.4 uygulanabilirlik sınırları (d/D ve e/D aşımı) -> OUT_OF_SCOPE
9. Desteklenmeyen bileşenler (koni, düz kapak) -> NOT_CALCULATED
10. Bombe üzerindeki nozul takviyesi (sadeleştirilmiş küre yaklaşımı)
11. Kod ve madde referansı kontrolü (code == 'EN 13445', ASME clause yok)

Referans: EN 13445-3:2021+A1:2023 Madde 9
"""

import pytest

from code_en_13445 import EN13445DesignCode
from code_en_13445 import openings
from domain import (
    Cone,
    DesignConditions,
    Head,
    HeadType,
    MaterialProperty,
    Nozzle,
    NozzleType,
    ProductForm,
    ShellSection,
)
from domain.enums import CalculationStatus
from units import relative_tolerance


@pytest.fixture
def en_code():
    return EN13445DesignCode(edition="2021+A1:2023")


@pytest.fixture
def sample_materials():
    """P355NH malzeme özellikleri."""
    mat_shell = MaterialProperty(
        material_id="MAT-P355NH-SHELL",
        standard_pack="EN 10028-3:2017",
        material_designation="P355NH",
        product_form=ProductForm.PLATE,
        temperature=200.0,
        allowable_stress=163.0,  # EN 13445-3 Tablo 6-1, 200°C f
        yield_strength=295.0,
        tensile_strength=490.0,
        source_reference="EN 10028-3:2017, P355NH",
    )
    mat_nozzle = MaterialProperty(
        material_id="MAT-P355NH-NOZ",
        standard_pack="EN 10028-3:2017",
        material_designation="P355NH",
        product_form=ProductForm.PIPE,
        temperature=200.0,
        allowable_stress=163.0,
        yield_strength=295.0,
        tensile_strength=490.0,
        source_reference="EN 10028-3:2017, P355NH",
    )
    return [mat_shell, mat_nozzle]


@pytest.fixture
def sample_design_conditions():
    return DesignConditions(
        operating_pressure=1.0,
        design_pressure=1.2,
        maximum_allowable_pressure_ps=1.5,
        operating_temperature=150.0,
        design_temperature=200.0,
        minimum_design_temperature=-10.0,
        corrosion_allowance_internal=2.0,
        hydrotest_temperature=20.0,
    )


@pytest.fixture
def sample_shell():
    return ShellSection(
        section_id="SHELL-01",
        inside_diameter=1000.0,
        tangent_length=2000.0,
        nominal_thickness=12.0,
        material_id="MAT-P355NH-SHELL",
        internal_corrosion_allowance=2.0,
        mill_tolerance=10.0,  # EN'de tipik %10
    )


class TestOpeningsPureFormulas:
    """EN 13445-3 Madde 9 saf fonksiyon birim testleri ve elle adım adım hesap kontrolü."""

    def test_step_by_step_manual_calculation(self):
        """Elle adım adım hesap doğrulaması:
        Girdiler:
        - Silindir: D_i = 1000 mm, t_nom = 12 mm, mt = %10, C = 2 mm
          e_c = 12 * 0.90 - 2.0 = 8.8 mm
          R_is = 500 + 2 = 502 mm
          f_s = 163.0 MPa
        - Nozul: d_eb = 168.3 mm, t_b_nom = 10 mm, C_b = 2 mm
          e_b = 10.0 - 2.0 = 8.0 mm
          d_ib = 168.3 - 2 * 8.0 = 152.3 mm
          a = 152.3 / 2 = 76.15 mm
          h_bo = 150 mm, c_i = 0 mm
          f_b = 163.0 MPa
        - Basınç: P = 1.2 MPa

        Adım adım sonuçlar:
        1. l_so = sqrt((2 * 502 + 8.8) * 8.8) = sqrt(1012.8 * 8.8) = sqrt(8912.64) = 94.4068 mm
        2. l_bo = sqrt((168.3 - 8.0) * 8.0) = sqrt(160.3 * 8.0) = sqrt(1282.4) = 35.8106 mm
        3. l'_bo = min(150.0, 35.8106) = 35.8106 mm
        4. l'_bi = min(0.0, 0.5 * 35.8106) = 0.0 mm
        5. Af_s = 94.4068 * 8.8 = 830.7797 mm²
        6. Af_b = 8.0 * (35.8106 + 0.0 + 8.8) = 8.0 * 44.6106 = 356.8849 mm²
        7. Ap_s = 502 * (94.4068 + 76.15) = 502 * 170.5568 = 85619.5033 mm²
        8. Ap_b = 0.5 * 152.3 * (35.8106 + 8.8) = 76.15 * 44.6106 = 3397.1004 mm²
        9. f_ob = min(163, 163) = 163 MPa
        10. Sol taraf (Phi - Kapasite):
            Phi = (830.7797 + 0) * (163 - 0.6) + 356.8849 * (163 - 0.6)
                = (830.7797 + 356.8849) * 162.4 = 1187.6646 * 162.4 = 192876.72 N
        11. Sağ taraf (Psi - Yük):
            Psi = 1.2 * (85619.5033 + 3397.1004) = 1.2 * 89016.6037 = 106819.92 N
        12. Kullanım:
            u = 106819.92 / 192876.72 = 0.553825 <= 1.0 (Yeterli)
        """
        R_is = 502.0
        e_c = 8.8
        d_eb = 168.3
        e_b = 8.0
        d_ib = 152.3
        a = 76.15
        h_bo = 150.0
        c_i = 0.0
        P = 1.2
        f_s = 163.0
        f_b = 163.0

        # 1. Etkin boylar
        l_so = openings.effective_shell_length(R_is, e_c)
        assert relative_tolerance(l_so, 94.4068, 0.005), f"l_so={l_so}"

        l_bo = openings.effective_nozzle_length(d_eb, e_b)
        assert relative_tolerance(l_bo, 35.8106, 0.005), f"l_bo={l_bo}"

        l_bo_eff = min(h_bo, l_bo)
        assert relative_tolerance(l_bo_eff, 35.8106, 0.005)

        l_bi_eff = openings.effective_inside_projection(c_i, l_bo)
        assert l_bi_eff == 0.0

        # 2. Alanlar
        Af_s = openings.shell_reinforcement_area(l_so, e_c)
        assert relative_tolerance(Af_s, 830.7797, 0.005), f"Af_s={Af_s}"

        Af_b = openings.nozzle_reinforcement_area(e_b, l_bo_eff, l_bi_eff, e_c)
        assert relative_tolerance(Af_b, 356.8849, 0.005), f"Af_b={Af_b}"

        Ap_s = openings.shell_pressure_area_cylinder(R_is, l_so, a)
        assert relative_tolerance(Ap_s, 85619.5033, 0.005), f"Ap_s={Ap_s}"

        Ap_b = openings.nozzle_pressure_area(d_ib, l_bo_eff, e_c)
        assert relative_tolerance(Ap_b, 3397.1004, 0.005), f"Ap_b={Ap_b}"

        # 3. Basınç-alan kontrolü
        res = openings.check_pressure_area_reinforcement(
            P=P,
            f_s=f_s,
            f_b=f_b,
            Af_s=Af_s,
            Af_b=Af_b,
            Ap_s=Ap_s,
            Ap_b=Ap_b,
        )

        assert relative_tolerance(res["capacity_phi"], 192876.72, 0.005), f"Phi={res['capacity_phi']}"
        assert relative_tolerance(res["load_psi"], 106819.92, 0.005), f"Psi={res['load_psi']}"
        assert relative_tolerance(res["utilization"], 0.553825, 0.005), f"u={res['utilization']}"
        assert res["is_reinforced"] is True

    def test_applicability_limits_check(self):
        """Madde 9.4 d_ib/D_is <= 1.0 ve e_c/D_is <= 0.1 sınırları."""
        # Uygun durum
        checks_ok = openings.check_applicability_limits(d_ib=150.0, D_is=1000.0, e_c=10.0)
        assert all(c[1] for c in checks_ok)

        # d_ib > D_is durumu (uygun değil)
        checks_fail_d = openings.check_applicability_limits(d_ib=1200.0, D_is=1000.0, e_c=10.0)
        assert not checks_fail_d[0][1]

        # e_c / D_is > 0.1 durumu (uygun değil)
        checks_fail_e = openings.check_applicability_limits(d_ib=150.0, D_is=1000.0, e_c=150.0)
        assert not checks_fail_e[1][1]


class TestEN13445NozzleReinforcementDesignCode:
    """EN13445DesignCode.calculate_nozzle entegrasyon testleri."""

    def test_cylinder_radial_nozzle_sufficient_review_required(
        self, en_code, sample_design_conditions, sample_materials, sample_shell
    ):
        """Silindir üzerinde dik nozul — yeterli takviye.
        verified=False nedeniyle durum PASS değil REVIEW_REQUIRED olmalıdır.
        """
        nozzle = Nozzle(
            tag="N1",
            host_component_id="SHELL-01",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=0.0,
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [sample_shell],
            "heads": [],
        })

        # Standart ve madde referansı
        assert res.code == "EN 13445"
        assert res.clause_reference == "EN 13445-3, 9.5"
        assert "UG-37" not in str(res.clause_reference)
        assert "ASME" not in str(res.formula_reference)

        # Durum kontrolü: PASS asla dönmez, cap_unverified ile REVIEW_REQUIRED olmalı
        assert res.status == CalculationStatus.REVIEW_REQUIRED
        assert res.status != CalculationStatus.PASS
        assert res.utilization_ratio < 1.0

        # Sol ve sağ taraf ara değerleri
        intermediates = {iv["name"]: iv["value"] for iv in res.intermediate_values}
        assert relative_tolerance(intermediates["capacity_phi"], 192876.72, 0.005)
        assert relative_tolerance(intermediates["load_psi"], 106819.92, 0.005)
        assert relative_tolerance(intermediates["utilization"], 0.553825, 0.005)

    def test_cylinder_radial_nozzle_insufficient_fail(
        self, en_code, sample_design_conditions, sample_materials
    ):
        """Silindir üzerinde dik nozul — yetersiz takviye (ince boyun/gövde ve yüksek basınç).
        Durum FAIL olmalı ve utilization > 1.0 olmalıdır.
        """
        weak_shell = ShellSection(
            section_id="SHELL-WEAK",
            inside_diameter=1000.0,
            tangent_length=2000.0,
            nominal_thickness=5.0,  # Çok ince gövde
            material_id="MAT-P355NH-SHELL",
            internal_corrosion_allowance=2.0,
            mill_tolerance=10.0,
        )
        weak_nozzle = Nozzle(
            tag="N-WEAK",
            host_component_id="SHELL-WEAK",
            outside_diameter=219.1,
            inside_diameter=213.1,
            neck_thickness=3.0,  # Çok ince nozul
            outside_projection=100.0,
            inside_projection=0.0,
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )
        high_pressure_dc = DesignConditions(
            design_pressure=2.5,
            operating_pressure=2.0,
            design_temperature=200.0,
            corrosion_allowance_internal=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": weak_nozzle,
            "design_conditions": high_pressure_dc,
            "materials": sample_materials,
            "shell_sections": [weak_shell],
            "heads": [],
        })

        assert res.code == "EN 13445"
        assert res.clause_reference == "EN 13445-3, 9.5"
        assert res.status == CalculationStatus.FAIL
        assert res.utilization_ratio > 1.0

    def test_nozzle_with_reinforcement_pad(
        self, en_code, sample_design_conditions, sample_materials, sample_shell
    ):
        """Takviye pedli nozul: Af_p ve f_op kapasiteye katkı sağlamalıdır."""
        pad_nozzle = Nozzle(
            tag="N-PAD",
            host_component_id="SHELL-01",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=0.0,
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
            reinforcement_pad=True,
            reinforcement_pad_thickness=8.0,
            reinforcement_pad_od=300.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": pad_nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [sample_shell],
            "heads": [],
        })

        assert res.status == CalculationStatus.REVIEW_REQUIRED
        intermediates = {iv["name"]: iv["value"] for iv in res.intermediate_values}
        assert intermediates["Af_p"] > 0.0
        # Pedli kapasite pedsiz kapasiteden (192876 N) belirgin şekilde yüksek olmalı
        assert intermediates["capacity_phi"] > 192876.72

    def test_nozzle_with_inside_projection(
        self, en_code, sample_design_conditions, sample_materials, sample_shell
    ):
        """İç çıkıntılı nozul: l'_bi ve Af_b katkısı doğrulanır."""
        proj_nozzle = Nozzle(
            tag="N-PROJ",
            host_component_id="SHELL-01",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=25.0,  # 25 mm iç çıkıntı
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": proj_nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [sample_shell],
            "heads": [],
        })

        assert res.status == CalculationStatus.REVIEW_REQUIRED
        intermediates = {iv["name"]: iv["value"] for iv in res.intermediate_values}
        assert intermediates["l_bi_eff"] == min(25.0, 0.5 * intermediates["l_bo"])
        # İç çıkıntı nozul kesit alanını artırmalı
        assert intermediates["Af_b"] > 356.8849

    def test_oblique_nozzle_out_of_scope(
        self, en_code, sample_design_conditions, sample_materials, sample_shell
    ):
        """Eğik nozul (inclination_angle != 0) -> OUT_OF_SCOPE dönmelidir."""
        oblique_nozzle = Nozzle(
            tag="N-OBLIQUE",
            host_component_id="SHELL-01",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=0.0,
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=30.0,  # Eğik
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": oblique_nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [sample_shell],
            "heads": [],
        })

        assert res.code == "EN 13445"
        assert res.status == CalculationStatus.OUT_OF_SCOPE
        assert "kapsam dışı" in res.error_message or "out of scope" in res.error_message.lower()

    def test_applicability_limits_exceeded_out_of_scope(
        self, en_code, sample_design_conditions, sample_materials, sample_shell
    ):
        """EN 13445-3 Madde 9.4 d_ib/D_is > 1.0 sınırı aşıldığında OUT_OF_SCOPE dönmelidir."""
        giant_nozzle = Nozzle(
            tag="N-GIANT",
            host_component_id="SHELL-01",
            outside_diameter=1200.0,  # Gövdeden (1000 mm) büyük nozul
            inside_diameter=1180.0,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=0.0,
            axial_position=1000.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": giant_nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [sample_shell],
            "heads": [],
        })

        assert res.code == "EN 13445"
        assert res.status == CalculationStatus.OUT_OF_SCOPE
        assert "9.4" in res.error_message

    def test_unsupported_hosts_not_calculated(
        self, en_code, sample_design_conditions, sample_materials
    ):
        """Koni ve düz kapak üzerindeki nozullar -> NOT_CALCULATED dönmelidir."""
        flat_head = Head(
            head_id="HEAD-FLAT",
            type=HeadType.FLAT,
            inside_diameter=1000.0,
            nominal_thickness=25.0,
            material_id="MAT-P355NH-SHELL",
            internal_corrosion_allowance=2.0,
        )
        cone = Cone(
            cone_id="CONE-01",
            large_diameter=1000.0,
            small_diameter=500.0,
            half_apex_angle=30.0,
            length=800.0,
            nominal_thickness=12.0,
        )
        nozzle_flat = Nozzle(
            tag="N-FLAT",
            host_component_id="HEAD-FLAT",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            axial_position=0.0,
            material_id="MAT-P355NH-NOZ",
        )
        nozzle_cone = Nozzle(
            tag="N-CONE",
            host_component_id="CONE-01",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            axial_position=0.0,
            material_id="MAT-P355NH-NOZ",
        )

        # Düz kapak
        res_flat = en_code.calculate_nozzle({
            "nozzle": nozzle_flat,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [],
            "heads": [flat_head],
        })
        assert res_flat.status == CalculationStatus.NOT_CALCULATED
        assert "Düz kapak" in res_flat.error_message or "flat head" in res_flat.error_message.lower()

        # Koni
        res_cone = en_code.calculate_nozzle({
            "nozzle": nozzle_cone,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [],
            "heads": [],
            "cones": [cone],
        })
        assert res_cone.status == CalculationStatus.NOT_CALCULATED
        assert "Koni" in res_cone.error_message or "cone" in res_cone.error_message.lower()

    def test_dished_head_nozzle_reinforcement(
        self, en_code, sample_design_conditions, sample_materials
    ):
        """Torisferik ve elipsoidal bombe üzerindeki nozul takviyesi (sadeleştirilmiş küre)."""
        head_tori = Head(
            head_id="HEAD-TORI",
            type=HeadType.TORISPHERICAL,
            inside_diameter=1000.0,
            crown_radius=1000.0,
            knuckle_radius=100.0,
            nominal_thickness=14.0,
            material_id="MAT-P355NH-SHELL",
            internal_corrosion_allowance=2.0,
            mill_tolerance=10.0,
        )
        nozzle = Nozzle(
            tag="N-TORI",
            host_component_id="HEAD-TORI",
            outside_diameter=168.3,
            inside_diameter=148.3,
            neck_thickness=10.0,
            outside_projection=150.0,
            inside_projection=0.0,
            axial_position=0.0,
            circumferential_angle=0.0,
            inclination_angle=0.0,
            material_id="MAT-P355NH-NOZ",
            corrosion_allowance=2.0,
        )

        res = en_code.calculate_nozzle({
            "nozzle": nozzle,
            "design_conditions": sample_design_conditions,
            "materials": sample_materials,
            "shell_sections": [],
            "heads": [head_tori],
        })

        assert res.code == "EN 13445"
        assert res.clause_reference == "EN 13445-3, 9.5"
        assert res.status == CalculationStatus.REVIEW_REQUIRED
        intermediates = {iv["name"]: iv["value"] for iv in res.intermediate_values}
        # Bombede Ap_s küre formülü (0.5 * R_is * (l_so + a)) olmalıdır
        assert intermediates["Ap_s"] > 0.0
