"""Nozul dış yükü — WRC 537 (WRC 107 eğrileri) ve WRC 297 lokal gerilme (P07).

Kapsam: silindirik gövdeye radyal (α = 0) dairesel nozul. Bombe/koni host'u ve
eğik nozul OUT_OF_SCOPE (WRC 537 küresel kabuk yolu bu sürümde yok).

## WRC 537 (silindir, dairesel bağlantı) — programın yaptığı
1. Geometri: Rm = Ri(korozyonlu) + T/2, γ = Rm/T, β = 0.875·r0/Rm
   (r0 = bağlantı dış yarıçapı; WRC 107 §3 dairesel bağlantının eşdeğer kare
   bağlantıya dönüşümü). Takviye pedi varsa iki konum değerlendirilir:
   ped kenarı (r0 = ped DÇ/2, T = gövde) ve nozul boynu (r0 = nozul DÇ/2,
   T = gövde + ped).
2. Boyutsuz eğri değeri → bileşke (WRC 107 normalizasyonu):
       P  : N = K·P/Rm,           M = K·P
       Mc : N = K·Mc/(Rm²·β),     M = K·Mc/(Rm·β)
       ML : N = K·ML/(Rm²·β),     M = K·ML/(Rm·β)
   σ_m = Kn·N/T, σ_b = Kb·6M/T².
3. İşaret düzeni (simetriden): P tüm noktalarda aynı işaret; ML yalnız A(+)/B(−)
   (boyuna eksen), Mc yalnız C(+)/D(−) (çevresel eksen); eğilme dış yüzeyde +,
   iç yüzeyde −. Eğilme işaret kabulünün bültenle ters olması yalnız iç/dış
   ETİKETİNİ değiştirir; her iki yüzey değerlendirildiğinden zarf değişmez.
4. Kesme (WRC 107 dairesel bağlantı): τ_Mt = Mt/(2π r0² T), τ_Vc = Vc/(π r0 T)
   (A, B noktaları), τ_VL = VL/(π r0 T) (C, D noktaları). Burulma ile kesmenin
   işaret etkileşimi bülten tablosuyla doğrulanmadığından |τ_Mt| + |τ_V|
   (muhafazakâr üst sınır) alınır.
5. Basınç genel membranı: σφ = P·Rm/T, σx = P·Rm/(2T) (korozyonlu gövde T'si;
   ped konumunda da gövde T'si — muhafazakâr).
6. Sınıflandırma (ASME VIII-2 Part 5 stili, VIII-1 S ile):
       Pm (yalnız basınç)              ≤ S
       PL (basınç + lokal membran)     ≤ 1.5·S
       PL + Pb + Q (toplam)            ≤ SPS = 3·S
   VIII-2 5.5.6.1 belirli koşullarda SPS = max(3S, 2Sy) izin verir; Sy/Su ve
   zamana bağlı özellik koşulu doğrulanmadığından 3S (muhafazakâr) kullanılır.
   Eşdeğer gerilme: Tresca gerilme şiddeti (WRC 107) veya von Mises (seçimli).

## Programın YAPMADIĞI (K6)
Eğri değerleri (`wrc_curves.WRC537_CURVES`) BOŞTUR — bellekten yazılmadı.
Kullanıcı lisanslı bültenden okuduğu değerleri girer (öncelik: kullanıcı > tablo);
eksik değer sıfır sayılmaz → BLOCKED_CODE_DATA.

## WRC 297
Geometri parametreleri ve sınır kapısı kurulur; eğri tablosu boş ve
normalizasyon biçimleri (N·T/P, M/P, moment için √(R·T) çarpanları) bağımsız
doğrulanamadığından sonuç her zaman BLOCKED_CODE_DATA — kullanıcı okuması da bu
sürümde hesaba alınmaz (yanlış normalizasyonla sayı üretmemek için).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from calc_core.result import CalculationResult

from .wrc_curves import WRC297_CURVES, WRC537_CURVES, WrcCurveError, resolve

POINTS = ("A", "B", "C", "D")
SURFACES = ("outside", "inside")
_COMPONENTS = ("Nphi", "Nx", "Mphi", "Mx")
_GROUP = {"A": "AB", "B": "AB", "C": "CD", "D": "CD"}
_SIGN = {
    "P": {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0},
    "ML": {"A": 1.0, "B": -1.0, "C": 0.0, "D": 0.0},
    "MC": {"A": 0.0, "B": 0.0, "C": 1.0, "D": -1.0},
}

# Geometri kapıları — bülten metniyle doğrulanmadı (verified False), kaynak notlu.
WRC537_D_OVER_D_MAX = 0.33   # P07 brief'i / yaygın yazılım pratiği: üstünde WRC 297 veya FEA
WRC297_D_OVER_D_MAX = 0.5    # yaygın pratik; bülten metniyle doğrulanmadı
GATE_SOURCE = "Sınır P07 brief'i / yaygın yazılım pratiğinden; WRC bülten metniyle doğrulanmadı (verified: false)."

WRC297_KEYS = tuple(f"{side}.{ld}.{c}" for side in ("shell", "nozzle")
                    for ld in ("P", "MC", "ML") for c in _COMPONENTS)


@dataclass(frozen=True)
class NozzleLoads:
    P: float = 0.0
    Vc: float = 0.0
    VL: float = 0.0
    Mc: float = 0.0
    ML: float = 0.0
    Mt: float = 0.0

    def active(self) -> Dict[str, float]:
        return {k: v for k, v in (("P", self.P), ("MC", self.Mc), ("ML", self.ML)) if v != 0.0}

    def any(self) -> bool:
        return any(v != 0.0 for v in (self.P, self.Vc, self.VL, self.Mc, self.ML, self.Mt))


@dataclass(frozen=True)
class PointStress:
    location: str
    point: str
    surface: str
    sigma_phi: float      # toplam çevresel
    sigma_x: float        # toplam boyuna
    tau: float
    membrane_phi: float   # basınç + lokal membran
    membrane_x: float
    PL: float
    total: float


def equivalent_stress(s1: float, s2: float, tau: float, criterion: str = "tresca") -> float:
    """Düzlem gerilme (σr ≈ 0) eşdeğer gerilme.

    tresca: max(|σa|, |σb|, |σa − σb|), σa,b = (s1+s2)/2 ± √(((s1−s2)/2)² + τ²)
    von_mises: √(s1² − s1·s2 + s2² + 3τ²)
    """
    if criterion == "von_mises":
        return math.sqrt(s1 * s1 - s1 * s2 + s2 * s2 + 3.0 * tau * tau)
    if criterion != "tresca":
        raise ValueError(f"Bilinmeyen eşdeğer gerilme ölçütü: {criterion}")
    c = 0.5 * (s1 + s2)
    r = math.sqrt((0.5 * (s1 - s2)) ** 2 + tau * tau)
    a, b = c + r, c - r
    return max(abs(a), abs(b), abs(a - b))


def wrc537_geometry(Rm: float, T: float, r0: float) -> Dict[str, float]:
    """γ = Rm/T, β = 0.875·r0/Rm, d/D = r0/Rm."""
    if Rm <= 0 or T <= 0 or r0 <= 0:
        raise ValueError(f"Rm, T, r0 pozitif olmalı: {Rm}, {T}, {r0}")
    return {"gamma": Rm / T, "beta": 0.875 * r0 / Rm, "d_over_D": r0 / Rm}


def wrc297_geometry(Rm: float, T: float, d_o: float, t_n: float) -> Dict[str, float]:
    """WRC 297 parametreleri: λ = (dm/Dm)·√(Dm/T), T/t, d/D (dm = d_o − t_n).

    Not: λ tanımı bellekten; bülten metniyle doğrulanmadı (verified False).
    """
    if Rm <= 0 or T <= 0 or d_o <= 0 or t_n <= 0 or t_n >= d_o / 2:
        raise ValueError(f"Geçersiz WRC 297 geometrisi: Rm={Rm}, T={T}, d={d_o}, t={t_n}")
    Dm, dm = 2.0 * Rm, d_o - t_n
    return {"lambda": (dm / Dm) * math.sqrt(Dm / T), "T_over_t": T / t_n, "d_over_D": d_o / Dm}


def required_keys_537(loads: NozzleLoads) -> List[str]:
    keys = []
    for ld in loads.active():
        groups = ("AB", "CD") if ld == "P" else (("AB",) if ld == "ML" else ("CD",))
        keys += [f"{ld}.{c}.{g}" for g in groups for c in _COMPONENTS]
    return keys


def resolve_coefficients_537(loads: NozzleLoads, user: Optional[Dict[str, Optional[float]]],
                             gamma: float, beta: float,
                             tables: Optional[Dict[str, dict]] = None) -> Tuple[Dict[str, dict], List[str]]:
    """Gerekli eğri değerlerini çözer. Dönüş: (çözülen {anahtar: {...}}, eksik/hata listesi)."""
    tables = WRC537_CURVES if tables is None else tables
    found, missing = {}, []
    for key in required_keys_537(loads):
        try:
            found[key] = resolve(key, user, gamma, beta, tables)
        except WrcCurveError as exc:
            missing.append(f"{key} ({exc})")
    return found, missing


def evaluate_wrc537(loads: NozzleLoads, K: Dict[str, float], Rm: float, T: float, r0: float,
                    sigma_p_phi: float = 0.0, sigma_p_x: float = 0.0, Kn: float = 1.0,
                    Kb: float = 1.0, criterion: str = "tresca", location: str = "nozzle_neck") -> List[PointStress]:
    """8 nokta (A/B/C/D × dış/iç) gerilmesi. `K`: {anahtar: boyutsuz eğri değeri}.

    Eksik anahtar (aktif yük için) KeyError verir — sıfır sayılmaz.
    """
    geo = wrc537_geometry(Rm, T, r0)
    beta = geo["beta"]
    norm = {
        "P": (loads.P / Rm, loads.P),
        "MC": (loads.Mc / (Rm * Rm * beta), loads.Mc / (Rm * beta)),
        "ML": (loads.ML / (Rm * Rm * beta), loads.ML / (Rm * beta)),
    }
    tau_t = abs(loads.Mt) / (2.0 * math.pi * r0 * r0 * T)
    tau = {
        "A": tau_t + abs(loads.Vc) / (math.pi * r0 * T),
        "B": tau_t + abs(loads.Vc) / (math.pi * r0 * T),
        "C": tau_t + abs(loads.VL) / (math.pi * r0 * T),
        "D": tau_t + abs(loads.VL) / (math.pi * r0 * T),
    }
    out = []
    for pt in POINTS:
        g = _GROUP[pt]
        res = dict.fromkeys(_COMPONENTS, 0.0)
        for ld, (nN, nM) in norm.items():
            s = _SIGN[ld][pt]
            if s == 0.0 or (nN == 0.0 and nM == 0.0):
                continue
            for c in _COMPONENTS:
                k = K[f"{ld}.{c}.{g}"]
                res[c] += s * k * (nN if c.startswith("N") else nM)
        m_phi = sigma_p_phi + Kn * res["Nphi"] / T
        m_x = sigma_p_x + Kn * res["Nx"] / T
        b_phi = Kb * 6.0 * res["Mphi"] / (T * T)
        b_x = Kb * 6.0 * res["Mx"] / (T * T)
        PL = equivalent_stress(m_phi, m_x, tau[pt], criterion)
        for surf in SURFACES:
            sgn = 1.0 if surf == "outside" else -1.0
            s_phi, s_x = m_phi + sgn * b_phi, m_x + sgn * b_x
            out.append(PointStress(
                location=location, point=pt, surface=surf, sigma_phi=s_phi, sigma_x=s_x,
                tau=tau[pt], membrane_phi=m_phi, membrane_x=m_x, PL=PL,
                total=equivalent_stress(s_phi, s_x, tau[pt], criterion),
            ))
    return out


# ── Proje → sonuç ─────────────────────────────────────────────────────────────

def _new_result(tag: str, method: str, code: str, edition: str) -> CalculationResult:
    if method == "WRC297":
        return CalculationResult(
            component_id=tag, component_type="nozzle", calculation_type="nozzle_load_wrc297",
            code=code, edition=edition,
            clause_reference="WRC Bulletin 297 (silindir-silindir, kabuk + nozul); ASME VIII-2 Part 5",
            formula_reference="λ = (dm/Dm)·√(Dm/T), T/t — eğri normalizasyonu doğrulanmadı",
        )
    return CalculationResult(
        component_id=tag, component_type="nozzle", calculation_type="nozzle_load_wrc537",
        code=code, edition=edition,
        clause_reference="WRC Bulletin 537 / 107 (silindir, dairesel bağlantı); ASME VIII-2 Part 5 "
                         "(Pm ≤ S, PL ≤ 1,5S, PL+Pb+Q ≤ 3S)",
        formula_reference="γ=Rm/T, β=0,875·r0/Rm; N=K·P/Rm, M=K·P; N=K·M/(Rm²β), M=K·M/(Rmβ); "
                          "σ=Kn·N/T ± Kb·6M/T²; τ=Mt/(2πr0²T)+V/(πr0T)",
    )


def _shell_geometry(shell) -> Tuple[float, float, float]:
    """(T korozyonlu, Ri korozyonlu, Rm) — gövde."""
    t_nom = shell.nominal_thickness
    ci, co = shell.internal_corrosion_allowance, shell.external_corrosion_allowance
    T = t_nom - ci - co
    D_i = shell.inside_diameter if shell.inside_diameter else shell.outside_diameter - 2.0 * t_nom
    Ri = D_i / 2.0 + ci
    return T, Ri, Ri + T / 2.0


def _material(materials, material_id):
    return next((m for m in materials or [] if m.material_id == material_id), None)


def _loads_of(entry) -> NozzleLoads:
    return NozzleLoads(P=entry.Fr_N, Vc=entry.Vc_N, VL=entry.VL_N,
                       Mc=entry.Mc_Nmm, ML=entry.ML_Nmm, Mt=entry.Mt_Nmm)


def _locations(nozzle, T: float) -> List[Tuple[str, float, float]]:
    """(konum, r0, T_eff). Ped varsa ped kenarı + nozul boynu."""
    locs = []
    pad_t, pad_od = nozzle.reinforcement_pad_thickness, nozzle.reinforcement_pad_od
    has_pad = bool(nozzle.reinforcement_pad and pad_t and pad_od and pad_od > nozzle.outside_diameter)
    if has_pad:
        locs.append(("pad_edge", pad_od / 2.0, T))
        locs.append(("nozzle_neck", nozzle.outside_diameter / 2.0, T + pad_t))
    else:
        locs.append(("nozzle_neck", nozzle.outside_diameter / 2.0, T))
    return locs


def _evaluate_entry(entry, project, criterion: str, code: str, edition: str) -> CalculationResult:
    res = _new_result(entry.nozzle_tag, entry.method, code, edition)
    nozzle = next((n for n in project.nozzles if n.tag == entry.nozzle_tag), None)
    if nozzle is None:
        res.set_not_calculated(f"Yük takımındaki nozul '{entry.nozzle_tag}' projede yok.")
        return res
    loads = _loads_of(entry)
    res.input_snapshot = {"nozzle": nozzle.tag, "method": entry.method, "loads": loads.__dict__,
                          "criterion": criterion, "Kn": entry.Kn, "Kb": entry.Kb}
    if not loads.any():
        res.set_not_calculated("Nozul dış yükü girilmedi (Fr, Vc, VL, Mc, ML, Mt hepsi 0).")
        return res
    shell = next((s for s in project.shell_sections if s.section_id == nozzle.host_component_id), None)
    if shell is None:
        res.set_out_of_scope(
            f"Host '{nozzle.host_component_id}' silindirik gövde değil — WRC 537 küresel kabuk / koni yolu "
            "bu sürümde yok; ayrıntılı analiz/FEA gerekir.")
        return res
    if nozzle.inclination_angle != 0.0:
        res.set_out_of_scope(f"Eğik nozul (α = {nozzle.inclination_angle:g}°): WRC 537/297 radyal nozul içindir.")
        return res
    mat = _material(project.materials, shell.material_id)
    if mat is None or not getattr(mat, "allowable_stress", None):
        res.set_not_calculated(f"Gövde malzemesi '{shell.material_id}' veya izin verilen gerilmesi bulunamadı.")
        return res
    T, Ri, Rm = _shell_geometry(shell)
    if T <= 0:
        res.set_not_calculated("Korozyonlu gövde kalınlığı sıfır veya negatif.")
        return res
    S = mat.allowable_stress
    P_des = project.design_conditions.design_pressure if entry.include_pressure else 0.0
    sp_phi, sp_x = P_des * Rm / T, P_des * Rm / (2.0 * T)
    res.material_properties_used = {"material_id": shell.material_id, "S_MPa": S}
    for name, val, unit, desc in (
        ("T_shell", T, "mm", "Korozyonlu gövde kalınlığı"), ("Rm", Rm, "mm", "Ortalama yarıçap (korozyonlu)"),
        ("S_allowable", S, "MPa", "Gövde S (VIII-1, tasarım sıcaklığı)"),
        ("pressure_sigma_phi", sp_phi, "MPa", "P·Rm/T"), ("pressure_sigma_x", sp_x, "MPa", "P·Rm/(2T)"),
    ):
        res.add_intermediate(name, val, unit, desc)
    for k, v in loads.__dict__.items():
        res.add_intermediate(f"load_{k}", v, "N" if k in ("P", "Vc", "VL") else "N·mm", f"Nozul yükü {k}")

    if entry.method == "WRC297":
        return _finish_297(res, nozzle, Rm, T)
    return _finish_537(res, entry, nozzle, loads, Rm, T, S, sp_phi, sp_x, criterion)


def _finish_297(res: CalculationResult, nozzle, Rm: float, T: float) -> CalculationResult:
    t_n = nozzle.neck_thickness - nozzle.corrosion_allowance
    try:
        g = wrc297_geometry(Rm, T, nozzle.outside_diameter, t_n)
    except ValueError as exc:
        res.set_not_calculated(str(exc))
        return res
    res.add_intermediate("lambda", g["lambda"], "-", "λ = (dm/Dm)·√(Dm/T) (doğrulanmadı)")
    res.add_intermediate("T_over_t", g["T_over_t"], "-", "Gövde/nozul kalınlık oranı")
    res.add_intermediate("d_over_D", g["d_over_D"], "-", "Nozul DÇ / gövde ortalama çap")
    ok = g["d_over_D"] <= WRC297_D_OVER_D_MAX
    res.add_validity_check("WRC 297 d/D ≤ 0,5", ok, WRC297_D_OVER_D_MAX, g["d_over_D"])
    res.add_assumption(GATE_SOURCE)
    if not ok:
        res.set_out_of_scope(f"d/D = {g['d_over_D']:.3f} > {WRC297_D_OVER_D_MAX} — WRC 297 kapsamı dışı; FEA gerekir.")
        return res
    res.set_blocked_code_data(
        "WRC 297 eğri tablosu programda yok (K6) ve eğri normalizasyon biçimleri bağımsız doğrulanmadı; "
        "kabuk ve nozul tarafı gerilmesi hesaplanmadı. Kullanıcı okumaları bu sürümde hesaba alınmaz. "
        f"Parametreler: λ = {g['lambda']:.3f}, T/t = {g['T_over_t']:.3f}, d/D = {g['d_over_D']:.3f}. "
        f"Gerekli eğri anahtarları: {', '.join(WRC297_KEYS[:4])} … ({len(WRC297_KEYS)} adet).")
    return res


def _finish_537(res, entry, nozzle, loads, Rm, T, S, sp_phi, sp_x, criterion) -> CalculationResult:
    blocked, out_of_scope, all_points, sources_verified = [], [], [], True
    for loc, r0, T_eff in _locations(nozzle, T):
        g = wrc537_geometry(Rm, T_eff, r0)
        res.add_intermediate(f"{loc}_r0", r0, "mm", f"{loc}: bağlantı dış yarıçapı r0")
        res.add_intermediate(f"{loc}_T", T_eff, "mm", f"{loc}: değerlendirme kalınlığı")
        res.add_intermediate(f"{loc}_gamma", g["gamma"], "-", "γ = Rm/T")
        res.add_intermediate(f"{loc}_beta", g["beta"], "-", "β = 0,875·r0/Rm")
        ok = g["d_over_D"] <= WRC537_D_OVER_D_MAX
        res.add_validity_check(f"{loc}: WRC 537 d/D ≤ 0,33", ok, WRC537_D_OVER_D_MAX, g["d_over_D"])
        if not ok:
            out_of_scope.append(f"{loc}: d/D = {g['d_over_D']:.3f}")
            continue
        found, missing = resolve_coefficients_537(loads, entry.coefficients, g["gamma"], g["beta"])
        if missing:
            blocked.append(f"{loc} (γ = {g['gamma']:.2f}, β = {g['beta']:.4f}): " + "; ".join(missing[:6])
                           + (f" … (+{len(missing) - 6})" if len(missing) > 6 else ""))
            continue
        sources_verified &= all(v["verified"] for v in found.values())
        K = {k: v["value"] for k, v in found.items()}
        all_points += evaluate_wrc537(loads, K, Rm, T_eff, r0, sp_phi, sp_x, entry.Kn, entry.Kb, criterion, loc)

    res.add_assumption(GATE_SOURCE)
    res.add_assumption(
        "K4: Kesme ile burulma kesmesi |τMt| + |τV| toplandı (işaret etkileşimi doğrulanmadı — muhafazakâr).")
    res.add_assumption(
        "K4: SPS = 3S (VIII-2 5.5.6.1 max(3S, 2Sy) seçeneği uygulanmadı — muhafazakâr); "
        "S = VIII-1 izin verilen gerilme.")
    res.add_assumption("K4: Basınç membranı ped konumunda da yalnız gövde kalınlığıyla hesaplandı (muhafazakâr).")
    if out_of_scope:
        res.set_out_of_scope("WRC 537 kapsamı dışı (d/D > 0,33): " + "; ".join(out_of_scope)
                             + ". WRC 297 veya FEA kullanın.")
        return res
    if blocked:
        res.set_blocked_code_data(
            "WRC 537 eğri değeri eksik — programda doğrulanmış eğri tablosu yok (K6); lisanslı bültenden "
            "okunan değerler 'coefficients' alanına girilmelidir, eksik değer sıfır sayılmaz. "
            + " | ".join(blocked))
        return res

    Pm = equivalent_stress(sp_phi, sp_x, 0.0, criterion)
    lim_pm, lim_pl, lim_sps = S, 1.5 * S, 3.0 * S
    for ps in all_points:
        key = f"{ps.location}_{ps.point}_{ps.surface}"
        res.add_intermediate(f"{key}_sigma_phi", ps.sigma_phi, "MPa", f"{key}: toplam çevresel")
        res.add_intermediate(f"{key}_sigma_x", ps.sigma_x, "MPa", f"{key}: toplam boyuna")
        res.add_intermediate(f"{key}_tau", ps.tau, "MPa", f"{key}: kesme")
        res.add_intermediate(f"{key}_PL", ps.PL, "MPa", f"{key}: PL (basınç + lokal membran)")
        res.add_intermediate(f"{key}_PL_Pb_Q", ps.total, "MPa", f"{key}: PL+Pb+Q")
    gov_pl = max(all_points, key=lambda p: p.PL)
    gov_t = max(all_points, key=lambda p: p.total)
    ratios = {"Pm": Pm / lim_pm, "PL": gov_pl.PL / lim_pl, "PL+Pb+Q": gov_t.total / lim_sps}
    res.add_intermediate("Pm", Pm, "MPa", f"Genel primer membran (yalnız basınç) ≤ S = {lim_pm:.1f}")
    res.add_intermediate("PL_max", gov_pl.PL, "MPa", f"{gov_pl.location}/{gov_pl.point} ≤ 1,5S = {lim_pl:.1f}")
    res.add_intermediate("PL_Pb_Q_max", gov_t.total, "MPa",
                         f"{gov_t.location}/{gov_t.point}/{gov_t.surface} ≤ 3S = {lim_sps:.1f}")
    governing = max(ratios, key=ratios.get)
    res.add_intermediate("governing_check", governing, "-", "En yüksek kullanım oranlı sınır")
    res.final_result, res.final_result_unit = gov_t.total, "MPa"
    res.allowable_limit, res.allowable_limit_unit = lim_sps, "MPa"
    util = max(ratios.values())
    if util > 1.0:
        res.set_fail(util)
        res.add_warning(f"WRC 537 sınırı aşıldı: {governing} oranı {ratios[governing]:.3f}.")
    else:
        # Kapı sınırı ve işaret düzeni bültenle doğrulanmadığından bu sürümde PASS verilmez.
        res.utilization_ratio = util
        why = ("eğri değerleri doğrulanmış tablodan" if sources_verified
               else "eğri değerleri kullanıcı okuması / doğrulanmamış tablo")
        res.set_review_required(
            f"Sınırlar sağlandı; {why}, d/D kapısı ve işaret düzeni bülten çalışma sayfasıyla "
            "doğrulanmadı — bağımsız mühendislik incelemesi gerekir.")
    return res


def build_nozzle_load_results(project, code: str, edition: str) -> List[CalculationResult]:
    """`project.nozzle_loads` her girdisi için bir sonuç. Analiz tanımsızsa boş liste."""
    nl = getattr(project, "nozzle_loads", None)
    if nl is None or not nl.entries:
        return []
    out = []
    for entry in nl.entries:
        try:
            out.append(_evaluate_entry(entry, project, nl.stress_criterion, code, edition))
        except (ValueError, KeyError, ZeroDivisionError) as exc:
            r = _new_result(entry.nozzle_tag, entry.method, code, edition)
            r.set_not_calculated(f"Nozul yükü hesabı tamamlanamadı: {exc}")
            out.append(r)
    return out


__all__ = [
    "NozzleLoads", "PointStress", "equivalent_stress", "wrc537_geometry", "wrc297_geometry",
    "required_keys_537", "resolve_coefficients_537", "evaluate_wrc537", "build_nozzle_load_results",
    "WRC297_KEYS", "WRC537_D_OVER_D_MAX", "WRC297_D_OVER_D_MAX",
]
