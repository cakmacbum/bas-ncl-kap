"""Yayınlanmış hesap setleriyle karşılaştırma testleri (bağımsız doğrulama).

`test_asme_golden.py`'den farkı: oradaki beklenen değerler suite'i yazan kişi tarafından
el hesabıyla üretildi. Buradaki beklenen değerler **dışarıdan** gelir — iki ayrı ticari
yazılımın yayımlanmış çıktısından. Bu yüzden her testin docstring'i el hesabı değil
**kaynak künyesi** taşır.

Kaynaklar (ayrıntı: docs/validation/asme-worked-examples.md):
  PVE-FT   Pressure Vessel Engineering Ltd., "Firetube" hesap seti, PV Elite 2017,
           ASME VIII-1 2015. pveng.com/.../11110c-1_code_calculations.pdf (2026-07-26)
  PVE-S13  Pressure Vessel Engineering Ltd., "Sample 13", Advanced Pressure Vessel 10.1.5,
           ASME VIII-1 2007 Ed. + 2008 Add., ASME Code Stamped.
           pveng.com/.../Sample13_Spreadsheet.pdf (2026-07-26)

K6: Kaynak PDF'leri depoya alınmaz; yalnızca künye + girdi + sayısal sonuç saklanır.

Tolerans %1 — yayınlanan değerler 3-4 anlamlı haneye yuvarlanmıştır.
"""

import pytest

from units import relative_tolerance
from code_asme_viii_1 import formulas as F

# Tam birim dönüşümleri
IN = 25.4                       # mm / inch
PSI = 0.006894757293168361      # MPa / psi

TOL = 0.01  # %1 — yayınlanmış değerlerin yuvarlama hassasiyeti


# ── UG-27: Silindirik gövde ───────────────────────────────────────────────────

def test_v01_ug27_circumferential_pve_firetube():
    """V-01 · UG-27(c)(1) çevresel — PVE-FT s.6 (nozul boynu).

    Kaynak girdisi: P = 125 psi, R = 16.0000 in, S = 20000 psi, E = 1.00, CA = 0
    Kaynak sonucu : t = 0.1004 in
    Kaynak da UG-27(c)(1) iç yarıçap formunu kullanmıştır — birebir aynı formül.
    """
    t_circ, _, _ = F.shell_thickness_internal_pressure(
        P=125 * PSI, R=16.0 * IN, S=20000 * PSI, E=1.00
    )
    assert relative_tolerance(t_circ, 0.1004 * IN, TOL), f"t={t_circ / IN:.6f} in"


def test_v02_ug27_longitudinal_pve_sample13_shell1():
    """V-02 · UG-27(c)(2) boyuna — PVE-S13 s.4 (Shell 1).

    Kaynak girdisi: P = 284.00 psi (250 tasarım + 34 statik kafa), R = 42.1250 in,
                    S = 19700 psi, E = 0.85
    Kaynak sonucu : t = 0.3560 in (korozyon payı eklenmeden önce)
    """
    _, t_long, _ = F.shell_thickness_internal_pressure(
        P=284.0 * PSI, R=42.1250 * IN, S=19700 * PSI, E=0.85
    )
    assert relative_tolerance(t_long, 0.3560 * IN, TOL), f"t={t_long / IN:.6f} in"


def test_v03_ug27_longitudinal_pve_sample13_shell2():
    """V-03 · UG-27(c)(2) boyuna, ikinci sayısal vaka — PVE-S13 s.6 (Shell 2).

    Kaynak girdisi: P = 267.00 psi, R = 60.1250 in, S = 19700 psi, E = 0.85
    Kaynak sonucu : t = 0.4778 in

    V-02 ile birlikte iki ayrı vaka → kaynak politikasının kabul kuralı sağlanır.
    """
    _, t_long, _ = F.shell_thickness_internal_pressure(
        P=267.0 * PSI, R=60.1250 * IN, S=19700 * PSI, E=0.85
    )
    assert relative_tolerance(t_long, 0.4778 * IN, TOL), f"t={t_long / IN:.6f} in"


# ── UG-32(d) vs Appendix 1-4(c): formülasyon farkı ────────────────────────────
#
# Her iki ticari yazılım da eliptik bombede Appendix 1-4(c) DIŞ çap formunu kullanıyor;
# suite UG-32(d) İÇ çap formunu kullanıyor. İkisi de Kod'a uygun, cebirsel olarak
# eşdeğer değil. Testler farkın **beklenen küçük aralıkta kaldığını** doğrular —
# eşitlik iddia etmez. Fark büyürse formüllerden biri bozulmuş demektir.

def test_v04_elliptical_head_formulation_gap_pve_firetube():
    """V-04 · Eliptik bombe, UG-32(d) ↔ App 1-4(c) farkı — PVE-FT s.3.

    Kaynak girdisi: P = 125 psi, Do = 72.000 in, t = 0.3900 in, S = 20000 psi, E = 1.00
    Kaynak sonucu : t = 0.2237 in  (Appendix 1-4(c), dış çap)
    Suite         : UG-32(d), iç çap Di = Do − 2t = 71.220 in

    Beklenen: suite biraz daha ince (%0-1). Fark %1'i aşarsa formülasyon farkıyla
    açıklanamaz — o zaman gerçek hata aranır.
    """
    Di = (72.0 - 2 * 0.3900) * IN
    t, K = F.head_elliptical_thickness(P=125 * PSI, D=Di, S=20000 * PSI, E=1.00)
    published = 0.2237 * IN
    assert K == 1.0
    gap = (published - t) / published
    assert 0.0 <= gap <= TOL, f"formülasyon farkı %{gap * 100:.3f} — beklenen aralık dışı"


def test_v05_elliptical_head_formulation_gap_pve_sample13():
    """V-05 · Eliptik bombe, ikinci vaka — PVE-S13 s.28 (Head 1).

    Kaynak girdisi: P = 284.00 psi, Do = 86.000 in, t = 1.0000 in, S = 19700 psi, E = 1.00
    Kaynak sonucu : t = 0.6120 in  (Appendix 1-4(c))
    """
    Di = (86.0 - 2 * 1.0) * IN
    t, _ = F.head_elliptical_thickness(P=284.0 * PSI, D=Di, S=19700 * PSI, E=1.00)
    published = 0.6120 * IN
    gap = (published - t) / published
    assert 0.0 <= gap <= TOL, f"formülasyon farkı %{gap * 100:.3f} — beklenen aralık dışı"


def test_v06_circumferential_formulation_gap_pve_sample13():
    """V-06 · Çevresel gerilme, UG-27(c)(1) ↔ App 1-1(a)(1) farkı — PVE-S13 s.4.

    Kaynak girdisi: P = 284.00 psi, Ro = 43.0000 in (Ri = 42.1250 in), S = 19700 psi, E = 0.85
    Kaynak sonucu : t = 0.7244 in  (Appendix 1-1(a)(1), dış yarıçap)
    """
    t_circ, _, _ = F.shell_thickness_internal_pressure(
        P=284.0 * PSI, R=42.1250 * IN, S=19700 * PSI, E=0.85
    )
    published = 0.7244 * IN
    gap = (published - t_circ) / published
    assert 0.0 <= gap <= TOL, f"formülasyon farkı %{gap * 100:.3f} — beklenen aralık dışı"


# ── UG-99(b) / UG-100: test basınçları — REGRESYON ────────────────────────────
#
# Bu vaka gerçek bir hata ortaya çıkardı: taban MAWP yerine tasarım basıncıydı
# (−42.9%, emniyetsiz yönde). Düzeltme 2026-07-26. Aşağıdaki testler o hatanın
# geri gelmesini engeller. Ayrıntı: docs/validation/asme-worked-examples.md V-07.

def test_v07_hydrotest_basis_is_mawp_pve_firetube():
    """V-07 · UG-99(b) — PVE-FT s.4. Taban MAWP olmalı, tasarım basıncı DEĞİL.

    Kaynak girdisi: MAWP = 218.80 psig, Sa/S = 1.00
    Kaynak sonucu : 1.3 × MAWP × Sa/S = 284.44 psig
    """
    S = 20000 * PSI
    p_test = F.hydrotest_pressure_asme(218.80 * PSI, S, S)
    assert relative_tolerance(p_test, 284.44 * PSI, TOL), f"P={p_test / PSI:.2f} psig"


def test_v07_pneumatic_basis_is_mawp_pve_firetube():
    """V-07 · UG-100 — PVE-FT s.4.

    Kaynak sonucu: 1.1 × MAWP × Sa/S = 240.68 psig
    """
    S = 20000 * PSI
    p_test = F.pneumatic_test_pressure(218.80 * PSI, S, S)
    assert relative_tolerance(p_test, 240.68 * PSI, TOL), f"P={p_test / PSI:.2f} psig"


def test_v07_orchestrator_uses_mawp_not_design_pressure():
    """V-07 regresyon — orkestratör test basıncını MAWP'den türetmeli.

    Bu, formül seviyesinde değil **boru hattı** seviyesinde bir testtir: hatanın
    kendisi orkestratörün tabana tasarım basıncını geçirmesiydi, formülde değildi.
    Bu yüzden 483 testin hiçbiri hatayı yakalayamamıştı.
    """
    from domain import (
        CalculationCode, DesignConditions, Head, HeadType, MaterialProperty,
        ProductForm, ShellSection, VesselProject,
    )
    from code_asme_viii_1 import ASMEVIII1DesignCode
    from calc_core.orchestrator import CalculationOrchestrator

    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0, hydrotest_temperature=20.0,
    )
    shell = ShellSection(
        section_id="S1", inside_diameter=1000, tangent_length=2000, nominal_thickness=12,
        material_id="M1", internal_corrosion_allowance=2.0,
    )
    heads = [
        Head(head_id=f"H{i}", type=HeadType.ELLIPTICAL, inside_diameter=1000,
             nominal_thickness=12, material_id="M1", internal_corrosion_allowance=2.0)
        for i in (1, 2)
    ]
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    project = VesselProject(
        project_number="P", project_name="t", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell], heads=heads,
        materials=[mat],
    )

    res = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025")).run(project)
    mawp = res.get_global_mawp()
    assert mawp is not None and mawp > dc.design_pressure

    by_type = {r.calculation_type: r for r in res.results}

    hydro = by_type["hydrotest"]
    assert hydro.input_snapshot["pressure_basis_type"] == "MAWP"
    assert relative_tolerance(hydro.final_result, 1.3 * mawp, 1e-6)
    # Eski (hatalı) davranışa geri dönmediğinden emin ol
    assert not relative_tolerance(hydro.final_result, 1.3 * dc.design_pressure, 1e-3)

    pneum = by_type["pneumatic_test"]
    assert pneum.input_snapshot["pressure_basis_type"] == "MAWP"
    assert relative_tolerance(pneum.final_result, 1.1 * mawp, 1e-6)


def test_v07_falls_back_to_design_pressure_with_explicit_assumption():
    """MAWP yoksa tasarım basıncına düşülür — ama sessizce değil (K4).

    UG-99(b) endnote'u bu muafiyete izin verir; şart, varsayımın kayda geçmesidir.
    """
    from domain import DesignConditions, MaterialProperty, ProductForm
    from code_asme_viii_1 import ASMEVIII1DesignCode

    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0, hydrotest_temperature=20.0,
    )
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    code = ASMEVIII1DesignCode(edition="2025")
    r = code.calculate_hydrotest_pressure({
        "design_conditions": dc, "materials": [mat], "code_edition": "2025",
        # global_mawp bilerek verilmedi
    })

    assert r.input_snapshot["pressure_basis_type"] == "P_design"
    assert relative_tolerance(r.final_result, 1.3 * dc.design_pressure, 1e-6)
    assert any("UG-99(b) endnote" in a for a in r.assumptions), r.assumptions
    assert any("MAWP" in w for w in r.warnings), r.warnings


# ── MAWP geri hesabı ──────────────────────────────────────────────────────────

def test_v08_mawp_cylindrical_shell_pve_firetube():
    """V-08 · MAWP, silindirik gövde — PVE-FT s.24 (Firetube).

    Kaynak girdisi: Do = 14.000 in, t = 0.3281 in (→ Ri = 6.6719 in), S = 17100 psi, E = 1.00
    Kaynak sonucu : MAWP = 816.88 psig
    """
    Ri = (14.0 / 2 - 0.3281) * IN
    mawp = F.mawp_from_shell(R=Ri, t_actual=0.3281 * IN, S=17100 * PSI, E=1.00)
    assert relative_tolerance(mawp, 816.88 * PSI, TOL), f"MAWP={mawp / PSI:.2f} psig"


def test_v09_mawp_elliptical_head_pve_firetube():
    """V-09 · MAWP, 2:1 eliptik bombe — PVE-FT s.3.

    Kaynak girdisi: Do = 72.000 in, t = 0.3900 in (→ Di = 71.220 in), S = 20000 psi, E = 1.00
    Kaynak sonucu : MAWP = 218.80 psig
    """
    Di = (72.0 - 2 * 0.3900) * IN
    mawp = F.mawp_from_ellipsoidal_head(D=Di, t_actual=0.3900 * IN, S=20000 * PSI, E=1.00)
    assert relative_tolerance(mawp, 218.80 * PSI, TOL), f"MAWP={mawp / PSI:.2f} psig"


# ── Tur 2: torisferik + yarım küre ────────────────────────────────────────────
#
# Ek kaynaklar (ayrıntı: docs/validation/asme-worked-examples.md):
#   PVE-FD   Pressure Vessel Engineering Ltd., "F&D Heads 2.02" anma tablosu,
#            S = 16000 psi. pveng.com/.../FDHeads202_16ksi.pdf (2026-07-26)
#   PVE-CMP  Pressure Vessel Engineering Ltd., "Comparison Between Head Types:
#            Hemi, SE, F&D and Flat". pveng.com/home/asme-code-design/... (2026-07-26)

# PVE-FD tablosu: L = anma çapı, r = 0.06 L, S = 16000 psi.
# Tablodaki kalınlıklar yuvarlanmış kesirlerdir (0.063 = 1/16, 0.313 = 5/16 …);
# karşılaştırma kesirin kendisiyle yapılır, yoksa yuvarlama %0.8 hataya çıkar.
_PVE_FD_TABLE = [
    # (çap in, E, t in, tablo psi)
    (12, 1.00, 1 / 4, 375.8), (12, 1.00, 1 / 2, 749.8), (12, 1.00, 1.0, 1492.5),
    (12, 1.00, 2.0, 2957.5), (12, 1.00, 1 / 16, 94.1), (12, 1.00, 5 / 16, 469.4),
    (12, 0.85, 1 / 2, 637.3), (12, 0.85, 2.0, 2513.9),
    (18, 1.00, 1 / 2, 500.6), (18, 1.00, 1.0, 998.1),
    (24, 1.00, 1 / 4, 188.1), (24, 1.00, 1.0, 749.8),
    (30, 1.00, 1 / 2, 300.8), (30, 1.00, 2.0, 1196.3),
]


@pytest.mark.parametrize("D_in,E,t_in,published_psi", _PVE_FD_TABLE)
def test_v11_torispherical_mawp_pve_fd_table(D_in, E, t_in, published_psi):
    """V-11 · UG-32(e) torisferik MAWP — PVE-FD anma tablosu.

    ASME F&D geometrisi: taç yarıçapı L = anma çapı, büküm yarıçapı r = 0.06 L
    → M = (3 + √(1/0.06)) / 4 = 1.770621.

    Tablonun tamamı (90 nokta) tarandı; tipik fark %0.03-0.05, en büyük %0.29.
    Burada çap/kalınlık/E boyunca yayılmış 14 temsilci nokta sabitlenir.
    """
    L = D_in * IN
    mawp = F.mawp_from_torispherical_head(
        L=L, r=0.06 * L, t_actual=t_in * IN, S=16000 * PSI, E=E
    )
    assert relative_tolerance(mawp, published_psi * PSI, TOL), (
        f"D={D_in}\" E={E} t={t_in:.4f} → {mawp / PSI:.1f} psi (tablo {published_psi})"
    )


def test_v10_hemispherical_head_pve_comparison():
    """V-10 · UG-32(f) yarım küre — PVE-CMP.

    Kaynak girdisi: Do = 48 in, Di = 47 in, P = 420 psi, SA-516-70,
                    S = 20000 psi @100°F, E = 1.00
    Kaynak sonucu : t = 0.2474 in
    Kaynak iç yarıçap formunu kullanmış — suite ile birebir aynı form.
    """
    t = F.head_hemispherical_thickness(P=420 * PSI, R=(47.0 / 2) * IN, S=20000 * PSI, E=1.00)
    assert relative_tolerance(t, 0.2474 * IN, TOL), f"t={t / IN:.4f} in"


def test_v13_elliptical_head_inside_diameter_form_pve_comparison():
    """V-13 · UG-32(d) 2:1 eliptik — PVE-CMP, **iç çap** formu.

    V-04/V-05'ten farkı: bu kaynak Appendix 1-4(c) dış çap formunu değil,
    UG-32(d) iç çap formunu kullanmış → doğrudan eşitlik iddia edilebilir.
    Kaynak girdisi: Di = 47 in, P = 420 psi, S = 20000 psi, E = 1.00
    Kaynak sonucu : t = 0.4947 in
    """
    t, K = F.head_elliptical_thickness(P=420 * PSI, D=47.0 * IN, S=20000 * PSI, E=1.00)
    assert K == 1.0
    assert relative_tolerance(t, 0.4947 * IN, TOL), f"t={t / IN:.4f} in"


def test_v14_torispherical_crown_radius_is_outside_diameter_pve_comparison():
    """V-14 · UG-32(e) F&D — taç yarıçapı DIŞ çaptır.

    PVE-CMP aynı kaba F&D bombe için t = 0.8901 in veriyor. L = Do = 48 in
    alındığında %0.5 içinde uyuyor; L = Di = 47 in alındığında fark %1.6'ya
    çıkıyor. Yani ASME F&D bombesinde taç yarıçapı **dış çapa** eşittir.

    Bu, `_torispherical_radii`'nin `L = D` (iç çap) varsayılanının hafif
    muhafazakâr-olmayan tarafta kaldığını gösterir — limitations B-06.
    """
    t_od, M = F.head_torispherical_thickness_full(
        P=420 * PSI, L=48.0 * IN, r=0.06 * 48.0 * IN, S=20000 * PSI, E=1.00
    )
    t_id, _ = F.head_torispherical_thickness_full(
        P=420 * PSI, L=47.0 * IN, r=0.06 * 47.0 * IN, S=20000 * PSI, E=1.00
    )
    published = 0.8901 * IN
    assert relative_tolerance(M, 1.770621, 1e-5)
    assert relative_tolerance(t_od, published, TOL), f"L=Do → {t_od / IN:.4f} in"
    assert abs(t_id - published) / published > TOL, "L=Di beklenenden iyi uyuyor — varsayım gözden geçirilmeli"


# ── Tur 3: UG-37/UG-40 nozul takviyesi ────────────────────────────────────────
#
# Kaynak: PVE-FT s.5-6 (nozul "Neck"). Tam alan dökümü yayınlanmış:
#   Ar = 7.160 · A1 = 5.320 · A2 = 0.779 · A3 = 0.820 · A4 = 0.250 · Atot = 7.170 in²
# Bu vaka suite'in takviye hesabında beş ayrı sapma ortaya çıkardı; ayrıntı ve
# kök nedenler: docs/validation/asme-worked-examples.md V-15.

IN2 = IN * IN  # mm² / in²


@pytest.fixture
def pve_ft_nozzle_case():
    """PVE-FT s.5 girdileri — 32" ID nozul, 72" OD 2:1 eliptik bombede, pedsiz."""
    from nozzles.reinforcement import NozzleReinforcementInput

    return NozzleReinforcementInput(
        nozzle_tag="Neck",
        nozzle_inside_diameter=32.000 * IN,
        nozzle_outside_diameter=(32.000 + 2 * 0.5) * IN,
        nozzle_neck_thickness=0.5000 * IN,
        nozzle_corrosion_allowance=0.0,
        nozzle_projection_outside=2.881 * IN,
        nozzle_projection_inside=0.8200 * IN,
        nozzle_allowable_stress=20000 * PSI,
        component_type="head",
        component_inside_diameter=(72.000 - 2 * 0.39) * IN,
        component_nominal_thickness=0.3900 * IN,
        component_corrosion_allowance=0.0,
        component_required_thickness=0.2237 * IN,
        component_allowable_stress=20000 * PSI,
        weld_leg_size_nozzle_to_shell=0.5000 * IN,
        design_pressure=125 * PSI,
    )


@pytest.mark.parametrize("area,published_in2", [
    ("A1", 5.320),   # gövde/bombe fazlası — UG-40 sınırı 2·max(d, Rn+tn+t) = 64"
    ("A2", 0.779),   # nozul boynu dışa — 2 × min(2.5t, 2.5tn) × (tn − trn)
    ("A3", 0.820),   # nozul boynu içe — 2 × min(h, 2.5t, 2.5tn) × tn (TAM kalınlık)
    ("A4", 0.250),   # kaynak — wo² (kesitin iki yanında birer köşe kaynağı)
])
def test_v15_nozzle_reinforcement_areas_pve_firetube(pve_ft_nozzle_case, area, published_in2):
    """V-15 · UG-37(c) takviye alanları — PVE-FT s.6.

    Düzeltme öncesi bu alanların dördü de yanlıştı (A1 −%96, A2 −%8, A3 −%100,
    A4 −%50) ve toplam −%85 sapıyordu; karar bile ters çıkıyordu (YETERSİZ,
    oysa lisanslı yazılım YETERLİ diyor).
    """
    from nozzles.reinforcement import calculate_reinforcement

    res = calculate_reinforcement(pve_ft_nozzle_case)
    got = {a.name: a.area_mm2 for a in res.available_areas}
    assert relative_tolerance(got[area], published_in2 * IN2, TOL), (
        f"{area} = {got[area] / IN2:.4f} in² (yayın {published_in2})"
    )


def test_v15_nozzle_reinforcement_required_area_and_verdict(pve_ft_nozzle_case):
    """V-15 · Gerekli alan, toplam ve karar — PVE-FT s.6.

    Kaynak: Ar = 7.160 in², Atot = 7.170 in² → "pedsiz mevcut alan yeterli".
    """
    from calc_core.result import CalculationStatus
    from nozzles.reinforcement import calculate_reinforcement

    res = calculate_reinforcement(pve_ft_nozzle_case)
    assert relative_tolerance(res.required_area, 7.160 * IN2, TOL)
    assert relative_tolerance(res.total_available_area, 7.170 * IN2, TOL)
    assert res.status == CalculationStatus.PASS, "lisanslı yazılım 'yeterli' diyor"


def test_v15_ug40_reinforcement_limits(pve_ft_nozzle_case):
    """V-15 · UG-40 sınırları — PVE-FT s.6 doğrudan yayımlamış.

    DL   (etkin malzeme çap sınırı)      = 64.000 in
    TLNP (pedsiz dik yönde kalınlık sınırı) = 0.975 in
    """
    from nozzles.reinforcement import calculate_reinforcement

    res = calculate_reinforcement(pve_ft_nozzle_case)
    lim = res.dimension_limits
    assert relative_tolerance(lim["limit_parallel_total_width"], 64.000 * IN, TOL)
    assert relative_tolerance(lim["limit_normal"], 0.975 * IN, TOL)


def test_v15_pad_outside_ug40_limit_is_not_counted():
    """V-15 · UG-40 sınırı dışındaki ped takviye sayılmamalı (K4: uyarı verir).

    Eski kod pedin tamamını `(pad_OD − d) × te` ile sayıyordu; sınır kontrolü yoktu.
    Bu, sınırı aşan geniş pedlerde **emniyetsiz** taraftaydı — diğer dört sapmanın
    aksine bu yön tehlikeliydi.
    """
    from nozzles.reinforcement import NozzleReinforcementInput, calculate_reinforcement

    base = dict(
        nozzle_tag="N-PAD", nozzle_inside_diameter=100.0, nozzle_outside_diameter=120.0,
        nozzle_neck_thickness=10.0, nozzle_projection_outside=150.0,
        nozzle_projection_inside=0.0, nozzle_allowable_stress=138.0,
        component_type="shell", component_inside_diameter=1000.0,
        component_nominal_thickness=12.0, component_corrosion_allowance=0.0,
        component_required_thickness=5.0, component_allowable_stress=138.0,
        weld_leg_size_nozzle_to_shell=8.0, design_pressure=1.2,
        has_reinforcement_pad=True, reinforcement_pad_thickness=10.0,
        reinforcement_pad_allowable_stress=138.0,
    )
    res = calculate_reinforcement(NozzleReinforcementInput(
        **base, reinforcement_pad_od=2000.0,  # UG-40 sınırının çok ötesinde
    ))
    limit = res.dimension_limits["limit_parallel_total_width"]
    assert 2000.0 > limit, "test kurgusu: ped sınırı aşmalı"
    a5 = next(a.area_mm2 for a in res.available_areas if a.name == "A5")
    # Sınıra kırpılmış genişlik üzerinden hesaplanmalı
    expected = (limit - 100.0 - 2 * 10.0) * 10.0
    assert relative_tolerance(a5, expected, 1e-6)
    assert res.limits["ug40_pad_within_limit"] is False
    assert any("UG-40 sınırını" in w for w in res.warnings), res.warnings


# ── Tur 4: korozyonlu iç ölçü — UÇTAN UCA REGRESYON ───────────────────────────
#
# V-01..V-15 formülleri DOĞRUDAN çağırıyordu, yani `design_code`'un formüle hangi
# yarıçapı geçtiğini hiç sınamıyordu. Bu testler o boşluğu kapatır: girdi
# `ShellSection`/`Head`, çıktı `CalculationResult` — arada design_code var.

def _sample13_shell_project():
    """PVE-S13 Shell 1 — Do = 86.000 in, t = 1.0000 in, CA = 0.1250 in.

    PV Elite hesapta R = 42.1250 in kullanıyor ve bunu çıktısında açıkça yazıyor.
    Korozyonsuz iç yarıçap 42.0000 in → aradaki fark tam olarak +C.
    """
    from domain import (
        CalculationCode, DesignConditions, MaterialProperty, ProductForm,
        ShellSection, VesselProject, WeldJoint,
    )

    Do, t_nom, CA = 86.0, 1.0000, 0.1250
    Di_new = Do - 2 * t_nom  # 84.000 in

    dc = DesignConditions(
        operating_pressure=200 * PSI,
        design_pressure=284.0 * PSI,          # 250 tasarım + 34 statik kafa (kaynakta böyle)
        maximum_allowable_pressure_ps=300 * PSI,
        operating_temperature=250, design_temperature=288,   # 550°F
        minimum_design_temperature=-29,
        corrosion_allowance_internal=CA * IN,
    )
    shell = ShellSection(
        section_id="S1", inside_diameter=Di_new * IN, tangent_length=98.0 * IN,
        nominal_thickness=t_nom * IN, material_id="M1", weld_joint_id="WJ1",
        internal_corrosion_allowance=CA * IN,
    )
    weld = WeldJoint(joint_id="WJ1", joint_type="longitudinal",
                     weld_category="A", joint_efficiency=0.85)
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516 Gr.70",
        product_form=ProductForm.PLATE, temperature=288, allowable_stress=19700 * PSI,
        yield_strength=31000 * PSI, tensile_strength=70000 * PSI,
        source_reference="x", density=7850,
    )
    return VesselProject(
        project_number="PVE-3602", project_name="Sample 13",
        calculation_code=CalculationCode.ASME_VIII_1, code_edition="2025",
        design_conditions=dc, shell_sections=[shell], heads=[], materials=[mat],
        welds=[weld],
    )


def test_v16_corroded_inside_radius_grows_not_shrinks():
    """V-16 · Korozyonlu iç yarıçap R + C olmalı, R − C değil — PVE-S13 s.4.

    İç korozyon metali **iç yüzeyden** yer → iç yarıçap BÜYÜR. UG-27'nin R'si
    "korozyonlu durumdaki iç yarıçap"tır.

    Eski kod `R − C` yapıyordu; bu, gerekli kalınlığı olduğundan DÜŞÜK gösteriyordu
    (emniyetsiz). Bu vakada yayınlanan yarıçap 42.1250 in, korozyonsuz 42.0000 in.
    """
    from code_asme_viii_1 import ASMEVIII1DesignCode

    project = _sample13_shell_project()
    code = ASMEVIII1DesignCode(edition="2025")
    r = code.calculate_shell_thickness({
        "shell": project.shell_sections[0],
        "design_conditions": project.design_conditions,
        "materials": project.materials,
        "welds": project.welds,
    })
    inter = {i["name"]: i["value"] for i in r.intermediate_values}

    # Yayınlanan yarıçap birebir
    assert relative_tolerance(inter["R_corroded"], 42.1250 * IN, 1e-6), (
        f"R_corroded = {inter['R_corroded'] / IN:.4f} in (yayın 42.1250)"
    )
    # Eski (yanlış) davranışa dönülmediğinden emin ol
    assert not relative_tolerance(inter["R_corroded"], 41.8750 * IN, 1e-3)

    # Boyuna gerilme kalınlığı yayınla uyuşmalı
    assert relative_tolerance(inter["t_long"], 0.3560 * IN, TOL), (
        f"t_long = {inter['t_long'] / IN:.5f} in (yayın 0.3560)"
    )


def test_v16_head_corroded_inside_diameter_grows():
    """V-16 · Bombede de korozyonlu iç çap D + 2C olmalı.

    Eski kod bombede korozyon düzeltmesi HİÇ yapmıyordu (ham iç çap) — gövdedeki
    `R − C` ile de tutarsızdı. Aynı fiziksel kural her ikisine de uygulanır.
    """
    from domain import (
        DesignConditions, Head, HeadType, MaterialProperty, ProductForm,
    )
    from code_asme_viii_1 import ASMEVIII1DesignCode

    C_mm = 3.0
    D_new = 1000.0
    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=C_mm,
    )
    head = Head(
        head_id="H1", type=HeadType.ELLIPTICAL, inside_diameter=D_new,
        nominal_thickness=14, material_id="M1", internal_corrosion_allowance=C_mm,
    )
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    r = ASMEVIII1DesignCode(edition="2025").calculate_head_thickness({
        "head": head, "design_conditions": dc, "materials": [mat], "welds": [],
    })
    assert relative_tolerance(r.input_snapshot["D_corroded_mm"], D_new + 2 * C_mm, 1e-9)
    assert r.input_snapshot["D_new_mm"] == D_new


def test_v16_self_consistency_thickness_vs_mawp():
    """V-16 · İç tutarlılık: üretilen kalınlık kendi MAWP'sini karşılamalı.

    Suite'in verdiği nominal kalınlığı, yine suite'in (yayınla doğrulanmış) MAWP
    fonksiyonuna geri veriyoruz. "Bu kalınlık P_tasarım'ı taşır" diyen hesap ile
    "bu kalınlık şu kadar taşır" diyen hesap çelişmemeli.

    Eski `R − C` davranışında küçük çaplı / yüksek korozyon paylı kaplarda MAWP,
    tasarım basıncının ALTINDA kalıyordu — yani kap kendi tasarım basıncını
    taşımıyordu.
    """
    from domain import (
        DesignConditions, MaterialProperty, ProductForm, ShellSection, WeldJoint,
    )
    from code_asme_viii_1 import ASMEVIII1DesignCode

    # Hatanın en görünür olduğu bölge: küçük yarıçap + yüksek korozyon payı
    for R_mm, C_mm, P_MPa in ((25.0, 6.0, 10.0), (40.0, 6.0, 8.0), (500.0, 3.0, 2.0)):
        dc = DesignConditions(
            operating_pressure=P_MPa * 0.8, design_pressure=P_MPa,
            maximum_allowable_pressure_ps=P_MPa * 1.2,
            operating_temperature=150, design_temperature=200,
            minimum_design_temperature=-10, corrosion_allowance_internal=C_mm,
        )
        mat = MaterialProperty(
            material_id="M1", standard_pack="x", material_designation="SA-516",
            product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
            yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
        )
        code = ASMEVIII1DesignCode(edition="2025")
        shell = ShellSection(
            section_id="S1", inside_diameter=2 * R_mm, tangent_length=1000,
            nominal_thickness=10, material_id="M1", weld_joint_id="WJ1",
            internal_corrosion_allowance=C_mm, mill_tolerance=0.0,
        )
        weld = WeldJoint(joint_id="WJ1", joint_type="longitudinal",
                         weld_category="A", joint_efficiency=1.0)

        r_t = code.calculate_shell_thickness({
            "shell": shell, "design_conditions": dc, "materials": [mat], "welds": [weld],
        })
        t_nom = next(
            i["value"] for i in r_t.intermediate_values if i["name"] == "t_nominal_required"
        )

        # Bu kalınlıkla kabı yeniden kur ve MAWP'sini sor
        shell_built = shell.model_copy(update={"nominal_thickness": t_nom})
        r_m = code.calculate_mawp({
            "component_type": "shell", "component": shell_built,
            "design_conditions": dc, "materials": [mat], "welds": [weld],
            "nominal_thickness": t_nom, "code_edition": "2025",
        })
        assert r_m.final_result >= P_MPa * 0.999, (
            f"R={R_mm} C={C_mm} P={P_MPa}: üretilen t={t_nom:.3f} mm için "
            f"MAWP={r_m.final_result:.3f} MPa < P_tasarım={P_MPa} MPa — iç çelişki"
        )


def test_v19_cone_mawp_participates_in_global_mawp():
    """V-19 · Koni MAWP'i global MAWP'e katılmalı.

    `cone_mawp()` yazılmıştı ama **hiçbir yerden çağrılmıyordu**. Global MAWP
    `min(tüm MAWP sonuçları)` olduğu için, sınırlayıcı bir konik geçiş sessizce
    görünmüyordu — hem MAWP hem de ona dayanan UG-99(b) test basıncı olduğundan
    yüksek raporlanıyordu.

    Bu testte koni bilerek gövde/bombeden **ince** seçildi: global MAWP'i koni
    yönetmeli.
    """
    from domain import (
        CalculationCode, Cone, DesignConditions, Head, HeadType, MaterialProperty,
        ProductForm, ShellSection, VesselProject,
    )
    from code_asme_viii_1 import ASMEVIII1DesignCode
    from calc_core.orchestrator import CalculationOrchestrator

    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=2.0, hydrotest_temperature=20.0,
    )
    shell = ShellSection(
        section_id="S1", inside_diameter=1000, tangent_length=2000, nominal_thickness=20,
        material_id="M1", internal_corrosion_allowance=2.0,
    )
    heads = [
        Head(head_id=f"H{i}", type=HeadType.ELLIPTICAL, inside_diameter=1000,
             nominal_thickness=20, material_id="M1", internal_corrosion_allowance=2.0)
        for i in (1, 2)
    ]
    cone = Cone(
        cone_id="C1", large_diameter=1000.0, small_diameter=500.0,
        half_apex_angle=25.0, length=536.0, nominal_thickness=8.0,   # kasten ince
        material_id="M1", internal_corrosion_allowance=2.0,
    )
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )
    project = VesselProject(
        project_number="P", project_name="koni", calculation_code=CalculationCode.ASME_VIII_1,
        code_edition="2025", design_conditions=dc, shell_sections=[shell], heads=heads,
        cones=[cone], materials=[mat],
    )

    res = CalculationOrchestrator(ASMEVIII1DesignCode(edition="2025")).run(project)

    mawps = {r.component_id: r for r in res.results if r.calculation_type == "mawp"}
    assert "C1" in mawps, "koni için MAWP sonucu hiç üretilmedi"

    governing = [r for r in mawps.values() if r.governing]
    assert len(governing) == 1
    assert governing[0].component_id == "C1", (
        "ince koni global MAWP'i yönetmeli; yöneten: " + governing[0].component_id
    )
    assert res.get_global_mawp() == mawps["C1"].final_result


# ── Torisferik varsayılan büküm yarıçapı — REGRESYON ──────────────────────────

def test_v12_default_knuckle_radius_is_asme_fd_six_percent():
    """V-12 · Büküm yarıçapı girilmediğinde varsayılan %6 olmalı, D/10 değil.

    Eski varsayılan `r = D/10` idi. Daha büyük büküm yarıçapı → daha küçük M →
    **%13 daha ince** bombe. Fiziksel bombe standart %6 bükümlüyse bu emniyetsiz
    taraftadır. Ayrıca varsayım sessizdi (K4 ihlali).

    Bu test hem değeri hem de varsayımın kayda geçtiğini sabitler.
    """
    from domain import (
        DesignConditions, Head, HeadType, MaterialProperty, ProductForm,
    )
    from code_asme_viii_1 import ASMEVIII1DesignCode

    dc = DesignConditions(
        operating_pressure=1.0, design_pressure=1.2, maximum_allowable_pressure_ps=1.5,
        operating_temperature=150, design_temperature=200, minimum_design_temperature=-10,
        corrosion_allowance_internal=0.0,
    )
    head = Head(
        head_id="H1", type=HeadType.TORISPHERICAL, inside_diameter=1000.0,
        nominal_thickness=20, material_id="M1", internal_corrosion_allowance=0.0,
        # crown_radius / knuckle_radius bilerek verilmedi
    )
    mat = MaterialProperty(
        material_id="M1", standard_pack="x", material_designation="SA-516",
        product_form=ProductForm.PLATE, temperature=200, allowable_stress=138,
        yield_strength=260, tensile_strength=485, source_reference="x", density=7850,
    )

    r = ASMEVIII1DesignCode(edition="2025").calculate_head_thickness({
        "head": head, "design_conditions": dc, "materials": [mat], "welds": [],
    })
    inter = {i["name"]: i["value"] for i in r.intermediate_values}

    # Varsayılan F&D taç/büküm yarıçapları dış çapa göre tanımlanır;
    # 20 mm nominal etle dış çap 1040 mm olur.
    assert relative_tolerance(inter["r"], 0.06 * 1040.0, 1e-9), "varsayılan büküm dış çapın %6'sı olmalı"
    assert relative_tolerance(inter["M_factor"], 1.770621, 1e-5)
    # Eski D/10 varsayılanına dönülmediğinden emin ol (M = 1.5406 verirdi)
    assert not relative_tolerance(inter["M_factor"], 1.540569, 1e-3)
    # K4: varsayım sessiz olmamalı
    assert any("Büküm yarıçapı girilmedi" in a for a in r.assumptions), r.assumptions
    assert any("Büküm yarıçapı" in w for w in r.warnings), r.warnings
