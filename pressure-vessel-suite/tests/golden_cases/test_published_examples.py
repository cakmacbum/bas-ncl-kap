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


# ── Kapatılamayan kapsam ──────────────────────────────────────────────────────

@pytest.mark.skip(reason="KAYNAK_BEKLİYOR — torisferik bombeli yayınlanmış hesap seti yok")
def test_ug32e_torispherical_published():
    """UG-32(e) `M` faktörü henüz bağımsız teyit almadı.

    İki kaynakta da torisferik bombe yok. Bulunana kadar `M = (3+√(L/r))/4`
    yalnızca sembolik olarak doğrulanmıştır.
    """


@pytest.mark.skip(reason="KAYNAK_BEKLİYOR — yarım küre bombeli yayınlanmış hesap seti yok")
def test_ug32f_hemispherical_published():
    """UG-32(f) henüz bağımsız teyit almadı."""
