"""Ayak (leg) destek alt kontrolleri — kesit, kaynak, taban plakası, WRC lokal gerilme.

Bu modül YALNIZ orkestre eder (K1): formüller `sections.py`, `wrc.py`,
`formulas.py` ve `welds.strength` modüllerindedir. Dört ayrı `CalculationResult`
üretir (her biri ayrı `calculation_type`, K5 izlenebilir ara değerlerle):

    leg_section_check   ayak profili: eksenel + eksantrik eğilme + kolon burkulması
    leg_weld_check      üç köşe kaynağı: ped->gövde, ayak->ped, ayak->taban plakası
    base_plate_check    taban plakası: yataklık basıncı + gerekli kalınlık
    wrc_local_stress    gövde lokal gerilmesi (WRC 107/537 bindirme; katsayı kullanıcı girdisi)

Tetikleme kuralı: `leg_section_type` boşsa hiçbiri üretilmez (eski boru-ayak davranışı,
yalnız `leg_stress`). Dolu ise dördü birden üretilir; eksik girdi ilgili sonuçta
`BLOCKED_MISSING_INPUT`/`BLOCKED_CODE_DATA` olarak söylenir.

K4: her idealizasyon sonuca `assumptions`/`warnings` olarak yazılır.
K6: WRC katsayıları, AWS D1.1 asgari bacak tablosu ve profil katalogları burada YOKTUR.

Referanslar (madde adı): AISC ASD (1989) E2/H1; Blodgett, *Design of Welded
Structures* §7.4; AWS D1.1 (0,30·Fexx); Moss, *PVDM* Prosedür 4-12; WRC 107/537.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from calc_core.result import CalculationResult
from domain.enums import CalculationStatus
from supports import formulas, sections, wrc
from welds import strength

# AISC ASD E1: azami narinlik; serbest uçlu konsol için AISC C-C2.1 (teorik 2,0, önerilen 2,1).
DEFAULT_K_CANTILEVER = 2.1
# Çelik elastisite modülü (AISC 29 000 ksi = 200 GPa). Malzemede yoksa VARSAYIM (yalnız karbon/düşük alaşım).
DEFAULT_E_STEEL_MPA = 200000.0

_WRC_TAU_WARNING = (
    "WRC 107/537'nin kayma yüklerinden doğrudan kayma gerilmesi (τ) hesaplanmadı (0 alındı); β/γ "
    "geçerlilik aralığı, kullandığınız bülten eğrisine göre kullanıcı tarafından doğrulanmalıdır."
)

LEG_DETAIL_TYPES = ("leg_section_check", "leg_weld_check", "base_plate_check", "wrc_local_stress")


# ── Yardımcılar ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LegGeometry:
    """Ayak profilinin hesaba giren ölçüleri."""

    kind: str                       # pipe | channel | box | angle
    section: sections.SectionProperties
    depth: float                    # eğilme düzlemindeki boyut (h veya D) (mm)
    width: float                    # diğer plan boyutu (b veya D) (mm)
    description: str


def _num(support: dict, key: str) -> Optional[float]:
    v = support.get(key)
    return None if v is None else float(v)


def build_leg_geometry(support: dict) -> Tuple[Optional[LegGeometry], List[str], Optional[str]]:
    """Girdilerden ayak geometrisi. Döner: (geometri | None, eksik_alanlar, hata_mesajı)."""
    kind = support.get("leg_section_type") or "pipe"
    missing: List[str] = []

    def need(*keys):
        vals = [_num(support, k) for k in keys]
        for k, v in zip(keys, vals):
            if v is None or v <= 0:
                missing.append(k)
        return vals

    try:
        if kind == "pipe":
            D, t = need("leg_diameter_mm", "leg_thickness_mm")
            if missing:
                return None, missing, None
            sec = sections.pipe_section(D, t)
            return LegGeometry(kind, sec, D, D, f"boru Ø{D:g}x{t:g}"), [], None
        if kind == "channel":
            h, b, s, t = need("leg_profile_height_mm", "leg_profile_width_mm",
                              "leg_web_thickness_mm", "leg_flange_thickness_mm")
            if missing:
                return None, missing, None
            sec = sections.channel_section(h, b, s, t)
            return LegGeometry(kind, sec, h, b, f"U profil h={h:g} b={b:g} s={s:g} t={t:g}"), [], None
        if kind == "box":
            H, B, t = need("leg_profile_height_mm", "leg_profile_width_mm", "leg_web_thickness_mm")
            if missing:
                return None, missing, None
            sec = sections.box_section(H, B, t)
            return LegGeometry(kind, sec, H, B, f"kutu {H:g}x{B:g}x{t:g}"), [], None
        if kind == "angle":
            a, b, t = need("leg_profile_height_mm", "leg_profile_width_mm", "leg_web_thickness_mm")
            if missing:
                return None, missing, None
            sec = sections.angle_section(a, b, t)
            return LegGeometry(kind, sec, a, b, f"köşebent {a:g}x{b:g}x{t:g}"), [], None
    except ValueError as exc:
        return None, [], f"Ayak kesit ölçüleri geçersiz: {exc}"
    return None, [], f"Bilinmeyen leg_section_type: {kind!r}"


def _find_material(materials, material_id):
    for m in materials or []:
        if m.material_id == material_id:
            return m
    return None


def _finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


# ── Sonuç fabrikaları (calculation_type literal: wiring testi bunları tarar) ──

def _new_section(tag, code, edition) -> CalculationResult:
    return CalculationResult(
        component_id=tag, component_type="support", calculation_type="leg_section_check",
        code=code, edition=edition,
        clause_reference="AISC ASD E2 / H1 (kolon + birleşik gerilme)",
        formula_reference="fa/Fa + Cm·fb/((1-fa/F'e)·Fb) <= 1; Fa: E2-1/E2-2",
    )


def _new_weld(tag, code, edition) -> CalculationResult:
    return CalculationResult(
        component_id=tag, component_type="support", calculation_type="leg_weld_check",
        code=code, edition=edition,
        clause_reference="AWS D1.1 (0,30·Fexx boğaz kayması); Blodgett §7.4 kaynak grubu",
        formula_reference="f_r = sqrt((V/Lw)^2 + (N/Lw + M/Sw)^2); tau = f_r/(0,707 z) <= 0,30 Fexx",
    )


def _new_base_plate(tag, code, edition) -> CalculationResult:
    return CalculationResult(
        component_id=tag, component_type="support", calculation_type="base_plate_check",
        code=code, edition=edition,
        clause_reference="Moss PVDM Prosedür 4-12 (taban plakası)",
        formula_reference="q = N/(L·W); t = c·sqrt(3q/(0,75 Fy)), c = max(m, n)",
    )


def _new_wrc(tag, code, edition) -> CalculationResult:
    return CalculationResult(
        component_id=tag, component_type="support", calculation_type="wrc_local_stress",
        code=code, edition=edition,
        clause_reference="WRC 107/537; ASME VIII-2 Part 5 (PL <= 1,5S, PL+Pb <= 1,5S)",
        formula_reference="N=K·V/Rm, M=K·V (kuvvet); N=K·M/Rm^2, M=K·M/Rm (moment) — K kullanıcı okuması",
    )


_FACTORIES = (_new_section, _new_weld, _new_base_plate, _new_wrc)


# ── Ortak bağlam ──────────────────────────────────────────────────────────────

@dataclass
class _Ctx:
    support: dict
    tag: str
    n_legs: int
    N_max: float
    N_min: float
    W_total: float
    M_overturn: float
    r_dist: float
    H_total: float
    H_leg: float
    e: Optional[float]
    L_leg: float
    L_assumed: bool
    K: float
    K_assumed: bool
    leg_mat: Any
    geometry: Optional[LegGeometry]
    geom_missing: List[str]
    geom_error: Optional[str]


def _load_notes(res: CalculationResult, ctx: _Ctx) -> None:
    res.add_intermediate("n_legs", ctx.n_legs, "-", "Ayak sayısı")
    res.add_intermediate("N_max", ctx.N_max, "N", "En yüklü ayak reaksiyonu (basma/hidrotest ağırlığı + devirme)")
    res.add_intermediate("N_min", ctx.N_min, "N", "En az yüklü ayak reaksiyonu (basma ağırlığıyla; yükselme leg_stress'te)")
    res.add_intermediate("H_per_leg", ctx.H_leg, "N", "Ayak başına yatay yük = lateral_load_N / n")
    if ctx.e is not None:
        res.add_intermediate("eccentricity_e", ctx.e, "mm", "Gövde dış yüzü -> ayak ağırlık merkezi")
    res.add_assumption(
        "K4: N_max, leg_stress ile AYNI yük durumundan alındı (hidrotest ağırlığı + devirme momenti "
        "eşdeğer ayak yükü); rüzgâr/deprem/basınç eşzamanlılığı ayrıca doğrulanmalıdır."
    )


def _build_ctx(payload: dict) -> Tuple[Optional[_Ctx], Optional[str]]:
    support = payload["support"]
    tag = support.get("tag", "LEG-01")
    materials = payload.get("materials", [])
    leg_mat = _find_material(materials, payload.get("skirt_material_id", ""))
    if leg_mat is None:
        return None, f"Ayak malzemesi '{payload.get('skirt_material_id', '')}' bulunamadı."
    W_total = payload.get("total_weight_N", 0.0) or 0.0
    if W_total <= 0:
        return None, "Toplam ağırlık belirtilmedi."
    n_legs = support.get("n_legs") or 0
    if n_legs < 2:
        return None, "En az 2 ayak gerekli (tek ayak devrilme analizi kapsam dışı)."
    M = payload.get("overturning_moment_Nmm", 0.0) or 0.0
    r = support.get("support_radius_mm") or 0.0
    if M > 0 and r <= 0:
        return None, "Devirme momenti için ayak dağılım yarıçapı (support_radius_mm) gerekli."
    try:
        N_max, N_min = formulas.leg_reaction_extremes(W_total, n_legs, M, r)
        H_total = support.get("lateral_load_N") or 0.0
        H_leg = formulas.leg_lateral_load_per_leg(H_total, n_legs)
    except ValueError as exc:
        return None, str(exc)

    L_in = _num(support, "leg_unbraced_length_mm")
    L_leg = L_in if L_in else float(support.get("height_mm") or 0.0)
    K_in = _num(support, "leg_effective_length_factor_K")
    geometry, gmiss, gerr = build_leg_geometry(support)
    return _Ctx(
        support=support, tag=tag, n_legs=n_legs, N_max=N_max, N_min=N_min, W_total=W_total,
        M_overturn=M, r_dist=r, H_total=H_total, H_leg=H_leg, e=_num(support, "leg_eccentricity_mm"),
        L_leg=L_leg, L_assumed=not L_in, K=K_in if K_in else DEFAULT_K_CANTILEVER,
        K_assumed=not K_in, leg_mat=leg_mat, geometry=geometry, geom_missing=gmiss, geom_error=gerr,
    ), None


def _geometry_block(res: CalculationResult, ctx: _Ctx) -> bool:
    """Geometri eksik/geçersizse sonucu bloke eder; True → bloke edildi."""
    if ctx.geom_error:
        res.set_not_calculated(ctx.geom_error)
        return True
    if ctx.geom_missing:
        res.set_blocked_missing_input(
            f"Ayak kesit girdisi eksik ({ctx.support.get('leg_section_type') or 'pipe'}): "
            + ", ".join(ctx.geom_missing) + "."
        )
        return True
    return False


# ── 1) Ayak profili ───────────────────────────────────────────────────────────

def leg_section_check(ctx: _Ctx, code: str, edition: str) -> CalculationResult:
    res = _new_section(ctx.tag, code, edition)
    if _geometry_block(res, ctx):
        return res
    if ctx.e is None:
        res.set_blocked_missing_input(
            "Eksantriklik e (leg_eccentricity_mm) girilmedi: eğilme momenti N·e hesaplanamaz. "
            "Eksenel ayak için 0 girin (bilinçli)."
        )
        return res
    if ctx.L_leg <= 0:
        res.set_blocked_missing_input("Burkulma boyu için leg_unbraced_length_mm veya height_mm gerekli.")
        return res

    g, sec = ctx.geometry, ctx.geometry.section
    Fy = ctx.leg_mat.yield_strength
    E = ctx.leg_mat.elastic_modulus
    E_assumed = not E
    if E_assumed:
        E = DEFAULT_E_STEEL_MPA
    H_leg = ctx.H_leg

    try:
        lam = sections.column_slenderness(ctx.K, ctx.L_leg, sec.r_min)
        lam_x = sections.column_slenderness(ctx.K, ctx.L_leg, sec.rx)
        Cc = sections.column_critical_slenderness(E, Fy)
        Fa = sections.allowable_compressive_stress(lam, E, Fy)
        Fe_prime = sections.euler_stress_asd(E, lam_x)
        fa = sections.leg_axial_stress(ctx.N_max, sec.A)
        fb_ecc = sections.leg_bending_stress(ctx.N_max, ctx.e, sec.Sx)
        M_lat = H_leg * ctx.L_leg
        fb_lat = sections.leg_bending_stress(H_leg, ctx.L_leg, sec.Sx) if H_leg > 0 else 0.0
        fb = fb_ecc + fb_lat
        Fb = 0.6 * Fy
        ratio = sections.aisc_interaction_ratio(fa, Fa, fb, Fb, Fy, Fe_prime)
    except ValueError as exc:
        res.set_not_calculated(str(exc))
        return res

    res.input_snapshot = {
        "tag": ctx.tag, "section": g.description, "N_max_N": ctx.N_max, "e_mm": ctx.e,
        "L_mm": ctx.L_leg, "K": ctx.K, "Fy_MPa": Fy, "E_MPa": E, "H_per_leg_N": H_leg,
    }
    _load_notes(res, ctx)
    res.add_intermediate("A", sec.A, "mm²", "Kesit alanı")
    res.add_intermediate("Ix", sec.Ix, "mm⁴", "Güçlü eksen atalet momenti")
    res.add_intermediate("Iy", sec.Iy, "mm⁴", "Zayıf eksen atalet momenti")
    res.add_intermediate("Sx", sec.Sx, "mm³", "Güçlü eksen kesit modülü")
    res.add_intermediate("rx", sec.rx, "mm", "Güçlü eksen atalet yarıçapı")
    res.add_intermediate("r_min", sec.r_min, "mm", "En küçük atalet yarıçapı (burkulmayı belirler)")
    res.add_intermediate("L_unbraced", ctx.L_leg, "mm", "Burkulma boyu")
    res.add_intermediate("K", ctx.K, "-", "Etkin boy katsayısı")
    res.add_intermediate("KL_over_r", lam, "-", "Narinlik K·L/r_min")
    res.add_intermediate("Cc", Cc, "-", "sqrt(2π²E/Fy) elastik/inelastik sınır")
    res.add_intermediate("Fa", Fa, "MPa", "İzin verilen eksenel basma (AISC E2-1/E2-2)")
    res.add_intermediate("fa", fa, "MPa", "Eksenel gerilme N_max/A")
    res.add_intermediate("fb_eccentric", fb_ecc, "MPa", "Eksantrik eğilme N_max·e/Sx")
    if H_leg > 0:
        res.add_intermediate("fb_lateral", fb_lat, "MPa", "Yatay yük eğilmesi H·L/Sx (konsol)")
    res.add_intermediate("fb", fb, "MPa", "Toplam eğilme gerilmesi")
    res.add_intermediate("Fb", Fb, "MPa", "İzin verilen eğilme 0,6·Fy (varsayım)")
    res.add_intermediate("Fe_prime", Fe_prime, "MPa", "F'e = 12π²E/(23 (KL/rx)²)")
    res.add_intermediate("fa_over_Fa", fa / Fa, "-", "fa/Fa")
    if _finite(ratio):
        res.add_intermediate("interaction_ratio", ratio, "-", "AISC H1 birleşik oran (<= 1,0)")
    res.add_validity_check("KL/r <= 200 (AISC E2)", lam <= sections.MAX_COMPRESSION_SLENDERNESS,
                           sections.MAX_COMPRESSION_SLENDERNESS, lam)

    res.add_assumption(
        f"K4: K = {ctx.K:g} " + ("(girilmedi; serbest uçlu konsol varsayımı, AISC)" if ctx.K_assumed
                                 else "(kullanıcı girdisi)") + "; ayak üstten gövdeye kaynaklı, altta taban plakası — yanal tutulu değil."
    )
    if ctx.L_assumed:
        res.add_assumption("K4: leg_unbraced_length_mm girilmedi; destek yüksekliği (height_mm) burkulma boyu alındı.")
    if E_assumed:
        res.add_assumption(
            f"K4: Malzemede elastik modül yok; E = {DEFAULT_E_STEEL_MPA:g} MPa (AISC çelik) varsayıldı — yalnız "
            "karbon/düşük alaşımlı çelik için geçerli; diğer malzemede material.elastic_modulus girin."
        )
    res.add_assumption("K4: Fb = 0,6·Fy (yanal-burulmalı burkulma ve kompaktlık kontrolü yapılmadı).")
    res.add_assumption(
        "K4: Eksantriklik e, güçlü eksen (Sx, h yönü) düzlemindedir; eğilme yalnız o düzlemde ve "
        "Cm = 0,85 (yanal ötelenmesi serbest) alındı. F'e için K·L/rx kullanıldı; burkulma için r_min."
    )
    res.add_assumption(
        "K4: Boy boyunca moment sabit (N·e) — üst uçtaki en büyük moment tüm boya uygulandı (muhafazakâr)."
        + (" Yatay yük eğilmesi H·L eksantrik eğilmeye aynı düzlemde eklendi." if H_leg > 0 else "")
    )
    res.add_warning(
        "Yerel burkulma (boru D/t, U/kutu/köşebent kol narinliği) ve profil köşe yuvarlatmaları bu "
        "kontrolde YOK; kesit keskin köşeli dikdörtgen parçalardan hesaplandı (katalogdan birkaç % sapabilir)."
    )
    if g.kind == "angle":
        res.add_warning("Köşebent: eğilme Ix üzerinden (asal eksen değil) alındı; burkulma asal r_min ile.")

    res.final_result = ratio if _finite(ratio) else None
    res.final_result_unit = "-"
    res.allowable_limit = 1.0
    res.allowable_limit_unit = "-"
    res.utilization_ratio = ratio if _finite(ratio) else None
    res.material_properties_used = {
        "designation": ctx.leg_mat.material_designation, "yield_strength": Fy, "elastic_modulus_used": E,
        "source_reference": ctx.leg_mat.source_reference,
    }

    if lam > sections.MAX_COMPRESSION_SLENDERNESS:
        res.set_fail(res.utilization_ratio)
        res.add_warning(f"KL/r = {lam:.1f} > {sections.MAX_COMPRESSION_SLENDERNESS:g}: azami narinlik aşıldı (AISC E2).")
    elif not _finite(ratio):
        res.set_fail(None)
        res.add_warning(f"fa = {fa:.2f} MPa >= F'e = {Fe_prime:.2f} MPa: eleman kararsız (eğilme etkisi sonsuz).")
    elif ratio > 1.0:
        res.set_fail(ratio)
        res.add_warning(f"Birleşik gerilme oranı {ratio:.3f} > 1,0.")
    else:
        res.set_pass(ratio)
    return res


# ── 2) Üç kaynak birleşimi ────────────────────────────────────────────────────

def _profile_group(kind: str, depth: float, width: float, leg: float):
    """Profil konturu çizgi-kaynak grubu; doğru kenarlara krater düzeltmesi (L-2z) uygulanır."""
    if kind == "pipe":
        return strength.weld_group_circle(depth), "daire kontur (Lw=πD, Sw=πD²/4)"
    d = strength.fillet_effective_length(depth, leg)
    b = strength.fillet_effective_length(width, leg)
    if kind == "channel":
        return strength.weld_group_channel(b, d), "C kontur: iki flanş + gövde (Lw=2b+d, Sw=bd+d²/6)"
    if kind == "box":
        return strength.weld_group_rectangle(b, d), "dikdörtgen kontur (Lw=2(b+d), Sw=bd+d²/3)"
    return strength.weld_group_two_lines(d, b), "iki paralel kenar (Lw=2d, Sw=d²/3) — köşebent idealizasyonu"


def leg_weld_check(ctx: _Ctx, code: str, edition: str) -> CalculationResult:
    res = _new_weld(ctx.tag, code, edition)
    sup = ctx.support
    if _geometry_block(res, ctx):
        return res
    Fexx = _num(sup, "weld_electrode_strength_MPa")
    z1 = _num(sup, "pad_to_shell_weld_leg_mm")
    z2 = _num(sup, "leg_to_pad_weld_leg_mm")
    z3 = _num(sup, "leg_to_base_plate_weld_leg_mm")
    pad_L, pad_W = _num(sup, "leg_pad_length_mm"), _num(sup, "leg_pad_width_mm")
    t_pad = _num(sup, "leg_pad_thickness_mm")
    has_pad = bool(pad_L and pad_W)

    missing = []
    if not Fexx:
        missing.append("weld_electrode_strength_MPa (Fexx)")
    if ctx.e is None:
        missing.append("leg_eccentricity_mm")
    if has_pad and not z1:
        missing.append("pad_to_shell_weld_leg_mm")
    if not z2:
        missing.append("leg_to_pad_weld_leg_mm")
    if not z3:
        missing.append("leg_to_base_plate_weld_leg_mm")
    if ctx.L_leg <= 0:
        missing.append("leg_unbraced_length_mm / height_mm")
    if missing:
        res.set_blocked_missing_input("Kaynak kontrolü için eksik girdi: " + "; ".join(missing) + ".")
        return res

    e = ctx.e
    N, H = ctx.N_max, ctx.H_leg
    rho = _num(sup, "leg_pad_contact_ratio")
    rho_assumed = rho is None
    rho = 1.0 if rho is None else rho
    min_leg = _num(sup, "weld_min_leg_mm")
    g = ctx.geometry
    V_pad = math.hypot(N, H)
    M_ecc = formulas.leg_eccentric_moment(N, e)
    e_lp = max(e - (t_pad or 0.0), 0.0)
    M_lp = formulas.leg_eccentric_moment(N, e_lp)
    M_base = formulas.leg_base_moment(N, e, H, ctx.L_leg)

    joints = []  # (ad, bacak, grup, açıklama, shear, normal, moment)
    try:
        if has_pad:
            grp = strength.weld_group_rectangle(
                strength.fillet_effective_length(pad_W, z1), strength.fillet_effective_length(pad_L, z1))
            joints.append(("pad_to_shell", z1, grp, "ped çevresi dikdörtgen (b=ped eni, d=ped boyu)", V_pad, 0.0, M_ecc))
        grp2, why2 = _profile_group(g.kind, g.depth, g.width, z2)
        grp2 = strength.scale_weld_group(grp2, rho)
        joints.append(("leg_to_pad", z2, grp2, why2 + f", temas oranı {rho:g} ile ölçekli", V_pad, 0.0, M_lp))
        grp3, why3 = _profile_group(g.kind, g.depth, g.width, z3)
        joints.append(("leg_to_base_plate", z3, grp3, why3, H, N, M_base))
        checks = []
        for name, leg, grp_, why, shear, normal, moment in joints:
            checks.append((name, why, grp_, shear, normal, moment,
                           strength.check_fillet_weld_group(leg, grp_, Fexx, shear, normal, moment, min_leg)))
    except ValueError as exc:
        res.set_not_calculated(f"Kaynak grubu hesaplanamadı: {exc}")
        return res

    res.input_snapshot = {
        "tag": ctx.tag, "Fexx_MPa": Fexx, "N_max_N": N, "H_per_leg_N": H, "e_mm": e,
        "weld_legs_mm": {"pad_to_shell": z1, "leg_to_pad": z2, "leg_to_base_plate": z3},
        "weld_min_leg_mm": min_leg, "leg_pad_contact_ratio": rho,
    }
    _load_notes(res, ctx)
    res.add_intermediate("Fexx", Fexx, "MPa", "Elektrot dayanımı")
    res.add_intermediate("weld_allowable", strength.fillet_allowable_shear(Fexx), "MPa", "0,30·Fexx (AWS D1.1)")
    worst, fail_msgs, min_fail = 0.0, [], []
    for name, why, grp_, shear, normal, moment, c in checks:
        res.add_intermediate(f"{name}_Lw", grp_.L_w, "mm", f"{name}: kaynak grubu boyu — {why}")
        res.add_intermediate(f"{name}_Sw", grp_.S_w, "mm²", f"{name}: kaynak grubu kesit modülü")
        res.add_intermediate(f"{name}_shear", shear, "N", f"{name}: kaynağa paralel kesme")
        res.add_intermediate(f"{name}_normal", normal, "N", f"{name}: kaynağa dik kuvvet")
        res.add_intermediate(f"{name}_moment", moment, "N·mm", f"{name}: moment")
        res.add_intermediate(f"{name}_throat", c.throat_mm, "mm", f"{name}: boğaz 0,707·z")
        res.add_intermediate(f"{name}_line_force", c.line_force_N_per_mm, "N/mm", f"{name}: birim boy bileşke kuvvet")
        res.add_intermediate(f"{name}_stress", c.stress_MPa, "MPa", f"{name}: boğaz gerilmesi")
        res.add_intermediate(f"{name}_utilization", c.utilization, "-", f"{name}: kullanım oranı")
        res.add_intermediate(f"{name}_required_leg", c.required_leg_mm, "mm", f"{name}: gerekli bacak")
        worst = max(worst, c.utilization)
        if c.utilization > 1.0:
            fail_msgs.append(f"{name}: τ={c.stress_MPa:.1f} > {c.allowable_MPa:.1f} MPa (z gerekli {c.required_leg_mm:.1f} mm)")
        if c.min_leg_ok is False:
            min_fail.append(f"{name}: z={c.leg_mm:g} < asgari {c.min_leg_mm:g} mm")
    gov = max(checks, key=lambda t: t[6].utilization)
    res.add_intermediate("governing_joint", gov[0], "-", "En yüksek kullanım oranlı birleşim")
    res.final_result = gov[6].stress_MPa
    res.final_result_unit = "MPa"
    res.allowable_limit = gov[6].allowable_MPa
    res.allowable_limit_unit = "MPa"
    res.utilization_ratio = worst

    res.add_assumption(
        "K4: Kaynaklar 'çizgi kaynak' (Blodgett §7.4) olarak gruplandı; kesme ve moment birim boy kuvvetlerine "
        "çevrilip bileşke alındı. Doğru kenar boylarından krater düzeltmesi L−2z düşüldü (kapalı çevre için muhafazakâr)."
    )
    if has_pad:
        res.add_assumption(
            f"K4: ped->gövde: ped çevresi (eni × boyu) grubu; kesme = sqrt(N_max² + H²) = {V_pad:.0f} N, "
            f"moment N_max·e = {M_ecc:.0f} N·mm (e gövde dış yüzünden ayak eksenine)."
        )
    else:
        res.add_notice("Ped tanımlı değil (leg_pad_length/width_mm): ped->gövde birleşimi hesaplanmadı; ayak->'ped' birleşimi ayağın doğrudan gövdeye kaynağı olarak okunmalıdır.")
    res.add_assumption(
        f"K4: ayak->ped: profil konturu ({g.description}), eğilme derinliği d={g.depth:g} mm; eksantriklik ped "
        f"kalınlığı düşülerek e' = {e_lp:.1f} mm alındı."
    )
    res.add_assumption(
        "K4: ayak->taban plakası: N_max kaynak tarafından taşınır (yataklık teması yok sayıldı, muhafazakâr); "
        f"kesme = H = {H:.0f} N; moment = N_max·e + H·L = {M_base:.0f} N·mm (ankastre taban)."
    )
    if rho_assumed:
        res.add_assumption("K4: leg_pad_contact_ratio girilmedi; ayak->ped için tam kontur (1,0) alındı.")
    elif rho < 1.0:
        res.add_warning(
            f"Temas oranı {rho:g} 'kaynaklı kontur boyu / profil kontur boyu' olarak yorumlandı; Lw ve Sw eşit "
            "oranda kısaltıldı (yaklaşık). Oranı 'profil ayak izi / ped alanı' olarak girdiyseniz kaynak boyu "
            "olduğundan kısa (emniyetli yönde) hesaplanır."
        )
    if min_leg is None:
        res.add_warning(
            "Asgari köşe kaynağı bacağı (AWS D1.1 tablosu) kontrolü YAPILMADI: weld_min_leg_mm girilmedi "
            "(tablo K6 gereği programda yok)."
        )
    res.add_warning("Bacak boyunun bağlanan parça kalınlığına göre azami sınırı ve yorulma kontrol edilmedi.")

    if fail_msgs or min_fail:
        res.set_fail(worst)
        for m in fail_msgs + min_fail:
            res.add_warning("Kaynak yetersiz — " + m)
    elif min_leg is None:
        res.set_review_required("Kaynak dayanımı geçti fakat asgari bacak kontrolü yapılamadı.")
    else:
        res.set_pass(worst)
    return res


# ── 3) Taban plakası ──────────────────────────────────────────────────────────

def base_plate_check(ctx: _Ctx, code: str, edition: str) -> CalculationResult:
    res = _new_base_plate(ctx.tag, code, edition)
    sup = ctx.support
    if _geometry_block(res, ctx):
        return res
    L, W = _num(sup, "base_plate_length_mm"), _num(sup, "base_plate_width_mm")
    if not L or not W:
        area = sup.get("base_plate_area_mm2")
        res.set_blocked_missing_input(
            "Taban plakası ölçüleri (base_plate_length_mm, base_plate_width_mm) girilmedi"
            + (f"; yalnız alan ({area:g} mm²) yeterli değil (m, n konsolları için L ve W gerekir)." if area else ".")
        )
        return res
    t_plate, Fy_p = _num(sup, "base_plate_thickness_mm"), _num(sup, "base_plate_yield_MPa")
    q_allow = _num(sup, "foundation_bearing_allowable_MPa")
    g = ctx.geometry
    depth_f, width_f = (0.80, 0.80) if g.kind == "pipe" else (0.95, 0.80)
    try:
        q = formulas.base_plate_bearing_pressure(ctx.N_max, L, W)
        m, n = formulas.base_plate_cantilevers(L, W, g.depth, g.width, depth_f, width_f)
    except ValueError as exc:
        res.set_not_calculated(str(exc))
        return res
    c = max(m, n)
    t_req = formulas.base_plate_required_thickness(q, c, Fy_p) if Fy_p else None

    res.input_snapshot = {"tag": ctx.tag, "L_mm": L, "W_mm": W, "t_mm": t_plate, "Fy_MPa": Fy_p,
                          "q_allowable_MPa": q_allow, "profile": g.description}
    _load_notes(res, ctx)
    res.add_intermediate("bearing_pressure_q", q, "MPa", "Yataklık basıncı q = N_max/(L·W)")
    res.add_intermediate("cantilever_m", m, "mm", f"m = (L − {depth_f:g}·h)/2")
    res.add_intermediate("cantilever_n", n, "mm", f"n = (W − {width_f:g}·b)/2")
    res.add_intermediate("cantilever_c", c, "mm", "c = max(m, n)")
    if t_req is not None:
        res.add_intermediate("t_required", t_req, "mm", "Gerekli kalınlık c·sqrt(3q/(0,75 Fy))")
    if q_allow:
        res.add_intermediate("q_allowable", q_allow, "MPa", "Temel izin verilen yataklık (kullanıcı)")
        res.add_intermediate("bearing_ratio", q / q_allow, "-", "q / q_izin")

    util_bearing = q / q_allow if q_allow else None
    util_t = t_req / t_plate if (t_req is not None and t_plate) else None
    utils = [u for u in (util_bearing, util_t) if u is not None]
    res.utilization_ratio = max(utils) if utils else None
    if util_t is not None and (util_bearing is None or util_t >= util_bearing):
        res.final_result, res.final_result_unit = t_req, "mm"
        res.allowable_limit, res.allowable_limit_unit = t_plate, "mm"
    else:
        res.final_result, res.final_result_unit = q, "MPa"
        res.allowable_limit, res.allowable_limit_unit = q_allow, "MPa"

    res.add_assumption(
        "K4: Yük tüm plakaya düzgün yayılı (rijit taban, doğrusal olmayan dağılım yok); gerekli kalınlık "
        "konsol şerit yaklaşımıyla (Moss 4-12, Fb = 0,75·Fy). Boru ayakta ikisi de 0,80·D; U/kutu/köşebentte "
        "0,95·h ve 0,80·b."
    )
    res.add_assumption(
        "Ankraj çekme/kesme kontrolü bu sonuçta TEKRARLANMADI: `leg_stress` sonucundadır "
        "(anchor_tension/anchor_shear ara değerleri) — tek yerde raporlanır."
    )

    missing = []
    if not Fy_p:
        missing.append("base_plate_yield_MPa")
    if not t_plate:
        missing.append("base_plate_thickness_mm")
    fails = []
    if util_bearing is not None and util_bearing > 1.0:
        fails.append(f"yataklık q = {q:.2f} > izin {q_allow:.2f} MPa")
    if util_t is not None and util_t > 1.0:
        fails.append(f"gerekli kalınlık {t_req:.1f} > plaka {t_plate:g} mm")
    if fails:
        res.set_fail(res.utilization_ratio)
        res.add_warning("Taban plakası yetersiz — " + "; ".join(fails))
    elif missing:
        res.set_blocked_missing_input(
            "Taban plakası eğilme kontrolü için eksik girdi: " + ", ".join(missing) + "."
        )
    elif not q_allow:
        res.add_warning(
            f"Yataklık basıncı q = {q:.2f} MPa hesaplandı ancak foundation_bearing_allowable_MPa girilmediği "
            "için temel yataklığı KONTROL EDİLMEDİ."
        )
        res.set_review_required("Temel izin verilen yataklık basıncı girilmedi; yataklık kontrolü yapılamadı.")
    else:
        res.set_pass(res.utilization_ratio)
    if sup.get("base_plate_area_mm2"):
        area = float(sup["base_plate_area_mm2"])
        if abs(area - L * W) > 0.01 * L * W:
            res.add_warning(
                f"base_plate_area_mm2 ({area:g}) ile L·W ({L * W:g}) uyuşmuyor; bu kontrol L·W kullanır, "
                "leg_stress yataklık ara değeri base_plate_area_mm2 kullanır."
            )
    if ctx.N_min < 0:
        res.add_warning("Negatif ayak reaksiyonu (kaldırma): ankraj çekmesinden plaka eğilmesi hesaplanmadı.")
    res.add_warning("Plaka altı grout/beton kesme, delme (punching) ve ankraj çekme koni kırılması kontrol edilmedi.")
    return res


# ── 4) WRC lokal kabuk gerilmesi ──────────────────────────────────────────────

def wrc_local_stress(ctx: _Ctx, payload: dict, code: str, edition: str) -> CalculationResult:
    res = _new_wrc(ctx.tag, code, edition)
    sup = ctx.support
    host_type = payload.get("host_component_type")
    if host_type != "shell" or sup.get("leg_attachment") == "bottom_head":
        res.set_out_of_scope(
            "WRC 107/537 lokal gerilme yalnız silindirik GÖVDE üzerindeki ped/ayak için uygulanır "
            f"(host: {host_type}, leg_attachment: {sup.get('leg_attachment') or 'shell'}); "
            "bombe/koni altı bağlantı için ayrıntılı analiz/FEA gerekir."
        )
        return res

    shell = payload["shell"]
    t_nom = shell.nominal_thickness
    T = t_nom - shell.internal_corrosion_allowance - shell.external_corrosion_allowance
    if T <= 0:
        res.set_not_calculated("Korozyonlu gövde kalınlığı sıfır veya negatif.")
        return res
    D_i = shell.inside_diameter if shell.inside_diameter else shell.outside_diameter - 2.0 * t_nom
    Rm = D_i / 2.0 + shell.internal_corrosion_allowance + T / 2.0
    D_mean = 2.0 * Rm
    ok_gate, gate_msg = wrc.applicability_gate(D_mean, T)
    res.input_snapshot = {"tag": ctx.tag, "Rm_mm": Rm, "T_mm": T, "D_over_T": D_mean / T}
    res.add_intermediate("Rm", Rm, "mm", "Ortalama yarıçap (korozyonlu)")
    res.add_intermediate("T", T, "mm", "Korozyonlu gövde kalınlığı (ped kalınlığı EKLENMEDİ)")
    res.add_intermediate("D_over_T", D_mean / T, "-", "D/T uygulanabilirlik oranı")
    res.add_validity_check("WRC 107/537 D/T ∈ [7, 2500]", ok_gate, "7–2500", D_mean / T)
    if not ok_gate:
        res.set_out_of_scope(gate_msg)
        return res

    pad_L, pad_W = _num(sup, "leg_pad_length_mm"), _num(sup, "leg_pad_width_mm")
    missing = []
    if not pad_L or not pad_W:
        missing.append("leg_pad_length_mm / leg_pad_width_mm (WRC yük ayak izi C1, C2)")
    if ctx.e is None:
        missing.append("leg_eccentricity_mm")
    dc = payload.get("design_conditions")
    if dc is None:
        missing.append("design_conditions (basınç)")
    mat = _find_material(payload.get("materials", []), shell.material_id)
    if mat is None:
        res.set_not_calculated(f"Gövde malzemesi '{shell.material_id}' bulunamadı.")
        return res
    if missing:
        res.set_blocked_missing_input("WRC lokal gerilme için eksik girdi: " + "; ".join(missing) + ".")
        return res

    C_L, C_C = pad_L / 2.0, pad_W / 2.0
    gam = wrc.gamma(Rm, T)
    beta_L, beta_C = wrc.beta(C_L, Rm), wrc.beta(C_C, Rm)
    N, e, H = ctx.N_max, ctx.e, ctx.H_leg
    loads = {
        "VL": max(N, 0.0),
        "ML": max(N, 0.0) * e,
        "P": H, "VC": H, "MC": H * e,
    }
    S = mat.allowable_stress
    P_des = dc.design_pressure
    sig_long, sig_circ = wrc.pressure_membrane_stresses(P_des, Rm, T)

    res.add_intermediate("gamma", gam, "-", "γ = Rm/T")
    res.add_intermediate("C_longitudinal", C_L, "mm", "Ped yarı boyu (eksenel) C")
    res.add_intermediate("C_circumferential", C_C, "mm", "Ped yarı eni (çevresel) C")
    res.add_intermediate("beta_longitudinal", beta_L, "-", "β = C_eksenel/Rm")
    res.add_intermediate("beta_circumferential", beta_C, "-", "β = C_çevresel/Rm")
    for k, v in loads.items():
        unit = "N·mm" if k in ("ML", "MC") else "N"
        res.add_intermediate(f"load_{k}", v, unit, f"WRC yükü {k}")
    res.add_intermediate("pressure_P_design", P_des, "MPa", "Tasarım basıncı")
    res.add_intermediate("pressure_stress_longitudinal", sig_long, "MPa", "P·Rm/(2T)")
    res.add_intermediate("pressure_stress_circumferential", sig_circ, "MPa", "P·Rm/T")
    res.add_intermediate("S_allowable", S, "MPa", "Gövde malzemesi izin verilen gerilme S")

    coeffs = wrc.coefficients_from_mapping(sup.get("wrc_coefficients"))
    active = {k: v for k, v in loads.items() if v != 0.0}
    gaps = wrc.missing_coefficients(coeffs, active)
    res.add_assumption(
        "K4: Yükler (bülten eksenleri: L = kap ekseni yönü, C = çevre yönü, pozitif büyüklük): "
        "VL = N_max (ayak düşey yükü gövdeye boyuna kesme); ML = N_max·e; yatay yük H = lateral_load_N/n "
        "yönü bilinmediğinden hem radyal P = H hem çevresel kesme VC = H (MC = H·e) olarak uygulandı "
        "(muhafazakâr üst sınır); çevresel eksantriklik (ayak ekseninin ped eksenine çevresel kayıklığı) yok sayıldı."
    )
    res.add_assumption("K4: İşaretler kullanıcının katsayı okumasında taşınır (yükler pozitif büyüklük girildi).")
    res.add_assumption("K4: Ped gövde kalınlığına EKLENMEDİ (muhafazakâr): T = korozyonlu gövde kalınlığı.")
    res.add_assumption(
        "K4: Basınç genel membranı (σc = P·Rm/T, σL = P·Rm/2T; korozyonlu) lokal gerilmeyle birleştirildi; "
        "basma yükü (hidrotest) ile tasarım basıncı eşzamanlı alındı (muhafazakâr)."
    )
    if gaps:
        n_missing = sum(len(g.split(": ")[1].split(", ")) for g in gaps)
        res.set_blocked_code_data(
            f"WRC katsayısı eksik: {n_missing} bileşen ({len(gaps)} nokta×yük girişi). Aktif yükler: "
            f"{', '.join(active)}. Katsayılar (Nx, Ny, Mx, My — A/B/C/D noktaları) lisanslı WRC 107/537 "
            f"bülteninden okunup girilmelidir; program bunları İÇERMEZ (K6). γ = {gam:.2f}, "
            f"β_L = {beta_L:.3f}, β_C = {beta_C:.3f}. Eksikler: " + "; ".join(gaps[:8])
            + (" ..." if len(gaps) > 8 else "")
        )
        res.add_warning(_WRC_TAU_WARNING)
        return res

    res.add_warning(_WRC_TAU_WARNING)
    try:
        pts = wrc.evaluate_all_points(
            coeffs, Rm, T, P=loads["P"], ML=loads["ML"], MC=loads["MC"], shear_stress=0.0,
            pressure_axial_stress=sig_long, pressure_circ_stress=sig_circ,
            VL=loads["VL"], VC=loads["VC"],
        )
        cls = {k: wrc.classify_point(v, S) for k, v in pts.items()}
    except ValueError as exc:
        res.set_not_calculated(str(exc))
        return res

    worst_pl = worst_plpb = 0.0
    for (pt, surf), pr in pts.items():
        cl = cls[(pt, surf)]
        key = f"{pt}_{surf}"
        res.add_intermediate(f"{key}_membrane_axial", pr.membrane_axial, "MPa", f"{key}: lokal membran eksenel")
        res.add_intermediate(f"{key}_membrane_circ", pr.membrane_circ, "MPa", f"{key}: lokal membran çevresel")
        res.add_intermediate(f"{key}_bending_axial", pr.bending_axial, "MPa", f"{key}: eğilme eksenel")
        res.add_intermediate(f"{key}_bending_circ", pr.bending_circ, "MPa", f"{key}: eğilme çevresel")
        res.add_intermediate(f"{key}_PL", cl.PL, "MPa", f"{key}: PL (membran+basınç, von Mises)")
        res.add_intermediate(f"{key}_PL_Pb", cl.PL_plus_Pb, "MPa", f"{key}: PL+Pb (von Mises)")
        worst_pl = max(worst_pl, cl.PL / cl.allowable_PL)
        worst_plpb = max(worst_plpb, cl.PL_plus_Pb / cl.allowable_PL_Pb)
    gov = max(cls.values(), key=lambda c: c.PL_plus_Pb)
    res.add_intermediate("governing_point", f"{gov.point}/{gov.surface}", "-", "En yüksek PL+Pb noktası")
    res.final_result = gov.PL_plus_Pb
    res.final_result_unit = "MPa"
    res.allowable_limit = gov.allowable_PL_Pb
    res.allowable_limit_unit = "MPa"
    res.utilization_ratio = max(worst_pl, worst_plpb)
    res.add_assumption(
        "K4: Eşdeğer gerilme von Mises (ASME VIII-2 Part 5 gerilme şiddeti Tresca'dır — basitleştirme); "
        "tüm lokal gerilme primer (PL) sınıflandırıldı: PL ≤ 1,5S, PL+Pb ≤ 1,5S; sekonder (Q) ayrımı yapılmadı."
    )
    if worst_pl > 1.0 or worst_plpb > 1.0:
        res.set_fail(res.utilization_ratio)
        res.add_warning("WRC lokal gerilme sınırı aşıldı (PL veya PL+Pb > 1,5S).")
    else:
        res.set_review_required(
            "Sınır kontrolleri geçti; ancak katsayılar kullanıcı okumasıdır ve lokal gerilme sınıflandırması "
            "basitleştirilmiştir — bağımsız mühendislik incelemesi gerekir."
        )
    return res


# ── Dört sonucu birleştirme ve özet ───────────────────────────────────────────

def check_leg_detail(payload: dict, code: str, edition: str) -> List[CalculationResult]:
    """Dört alt kontrolü üretir (yalnız `leg_section_type` doluysa çağrılmalı)."""
    ctx, reason = _build_ctx(payload)
    tag = payload["support"].get("tag", "LEG-01")
    if ctx is None:
        out = []
        for factory in _FACTORIES:
            r = factory(tag, code, edition)
            r.set_not_calculated(reason)
            out.append(r)
        return out
    return [
        leg_section_check(ctx, code, edition),
        leg_weld_check(ctx, code, edition),
        base_plate_check(ctx, code, edition),
        wrc_local_stress(ctx, payload, code, edition),
    ]


def summarize_leg(leg_result: CalculationResult, details: List[CalculationResult]) -> None:
    """`leg_stress` özet sonucuna alt kontrol durumlarını yazar; NİHAİ PASS vermez.

    Herhangi bir alt kontrol FAIL ise özet FAIL; aksi hâlde (leg_stress FAIL değilse)
    REVIEW_REQUIRED — temel yataklık/ankraj/eşzamanlı yük durumu kontrolleri tam değildir.
    """
    lines = [f"{d.calculation_type}={d.status.value}" for d in details]
    leg_result.add_intermediate(
        "leg_subchecks", "; ".join(lines), "-", "Alt kontrol durumları (kesit/kaynak/taban plakası/WRC)"
    )
    failed = [d.calculation_type for d in details if d.status == CalculationStatus.FAIL]
    if failed:
        leg_result.set_fail(leg_result.utilization_ratio)
        leg_result.add_warning("Alt kontrol(ler) FAIL: " + ", ".join(failed) + ".")
    elif leg_result.status != CalculationStatus.FAIL:
        leg_result.set_review_required(
            "Ayak nihai PASS verilmez: alt kontroller — " + "; ".join(lines) + ". Temel yataklık, ankraj "
            "ve eşzamanlı yük durumu kontrolleri tam değildir; bağımsız mühendislik incelemesi gerekir."
        )
