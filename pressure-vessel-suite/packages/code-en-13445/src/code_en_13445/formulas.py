"""EN 13445-3 formülleri — saf matematik.

Bu modül EN 13445-3:2021+A1:2023'teki temel formülleri uygular.
K1 kuralı: Formüller yalnızca hesap eklentilerinde.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: EN 13445-3:2021+A1:2023
"""

from __future__ import annotations

import math
from typing import Tuple


# ── EN 13445-3, 5.4.2: Silindirik gövde, iç basınç ──────────────────────────

def shell_thickness_internal_pressure(
    P: float,
    R: float,
    f: float,
    z: float,
) -> Tuple[float, float, float]:
    """EN 13445-3, 5.4.2 — Silindirik gövde iç basınç et kalınlığı.

    Çevresel gerilme (uzunlamasına dikişler — daha kritik):
        e_circ = P × R / (f × z - P/2)

    Boyuna gerilme (çevresel dikişler):
        e_long = P × R / (2 × f × z + P)

    Burada:
    f = tasarım gerilmesi (izin verilen gerilme, MPa)
    z = birimleştirme katsayısı (joint coefficient, 0.7–1.0)

    Args:
        P: Tasarım basıncı (MPa).
        R: İç yarıçap (mm).
        f: Tasarım gerilmesi / izin verilen gerilme (MPa).
        z: Birimleştirme katsayısı (joint coefficient).
        e: Mevcut et kalınlığı (mm) — kontrol için.
        C: Korozyon payı (mm).

    Returns:
        (e_circ, e_long, e_required) — çevresel, boyuna ve kritik kalınlık (mm).

    Referans: EN 13445-3, 5.4.2, Eq. (5.4.2-1) ve (5.4.2-2)
    """
    # Çevresel gerilme (uzunlamasına dikiş) — Eq. (5.4.2-1)
    denominator_circ = f * z - P / 2.0
    if denominator_circ <= 0:
        raise ValueError(
            f"EN 13445-3, 5.4.2: f×z - P/2 = {denominator_circ:.4f} ≤ 0. "
            "Basınç çok yüksek veya tasarım gerilmesi çok düşük."
        )
    e_circ = P * R / denominator_circ

    # Boyuna gerilme (çevresel dikiş) — Eq. (5.4.2-2)
    denominator_long = 2 * f * z + P
    e_long = P * R / denominator_long

    # Kritik kalınlık (büyük olan)
    e_required = max(e_circ, e_long)

    return e_circ, e_long, e_required


def shell_required_nominal_thickness(
    e_required: float,
    C: float,
    mill_tolerance_factor: float = 0.90,
    forming_thinning: float = 0.0,
) -> float:
    """Gerekli nominal et kalınlığı (EN 13445).

    e_nominal = (e_required + C + forming_thinning) / mill_tolerance_factor

    EN 13445'de tipik mill toleransı %10 → factor = 0.90.

    Mill (sac) negatif toleransı **sipariş edilen nominal kalınlığın tamamına**
    uygulanır: sac en kötü durumda `factor × e_nominal` kalınlığında teslim
    edilebilir. Ömür sonunda basınca dayanması gereken kalınlık, teslim edilen
    kalınlıktan korozyon payı ve şekillendirme incelmesi düşüldükten sonra
    kalandır:

        factor × e_nominal - C - forming_thinning >= e_required

    Bu nedenle C ve forming_thinning bölmenin **içinde** kalmalıdır. Payı bölme
    dışında toplamak (e_required/factor + C) ömür sonunda eksik kalınlık verir.

    Args:
        e_required: Korozyonsuz gerekli kalınlık (mm).
        C: Korozyon payı (mm).
        mill_tolerance_factor: Sac tolerans faktörü (0.90 = %10 negatif).
        forming_thinning: Şekillendirme incelmesi (mm).

    Returns:
        Gerekli nominal kalınlık (mm).
    """
    if mill_tolerance_factor <= 0 or mill_tolerance_factor > 1.0:
        raise ValueError(f"mill_tolerance_factor 0-1 aralığında olmalı: {mill_tolerance_factor}")
    return (e_required + C + forming_thinning) / mill_tolerance_factor


# ── EN 13445-3, 5.5.2: Elipsoidal bombe ──────────────────────────────────────

def head_elliptical_thickness(
    P: float,
    D: float,
    f: float,
    z: float,
) -> Tuple[float, float]:
    """EN 13445-3, 5.5.2 — Elipsoidal bombe et kalınlığı.

    Standart 2:1 elipsoidal:
        e = P × D / (4 × f × z - P)

    Args:
        P: Tasarım basıncı (MPa).
        D: İç çap (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        C: Korozyon payı (mm).

    Returns:
        (e_required, shape_factor)

    Referans: EN 13445-3, 5.5.2, Eq. (5.5.2-1)
    """
    denominator = 4 * f * z - P
    if denominator <= 0:
        raise ValueError(
            f"EN 13445-3, 5.5.2: 4×f×z - P = {denominator:.4f} ≤ 0. "
            "Basınç çok yüksek."
        )
    e = P * D / denominator
    return e, 1.0  # shape_factor = 1.0 for 2:1 elliptical


# ── E03: EN 13445-3, 7.5.3 — Torisferik bombe (tam prosedür) ───────────────
# verified=False: lisanslı EN 13445-3 metniyle satır satır doğrulanmadı; denklem
# biçimleri ve 7.5.3.5 β polinom katsayıları bellekten yazıldı (K6: metin gömülmez,
# yalnız madde atfı). Eski "basitleştirilmiş W faktörü" yaklaşımı kaldırıldı (S01).
# Semboller: Di iç çap, De dış çap, R taç iç yarıçapı, r büküm iç yarıçapı,
# e gerekli kalınlık, ea analiz kalınlığı, fb burkulma tasarım gerilmesi.

def torispherical_applicability(
    Di: float, De: float, R: float, r: float, e: float, ea: float | None = None,
) -> list[tuple[str, bool, float, float]]:
    """EN 13445-3, 7.5.3.1 — uygulanabilirlik koşulları.

    r ≤ 0,2·Di ; r ≥ 0,06·Di ; r ≥ 2·e ; e ≤ 0,08·De ; ea ≥ 0,001·De ; R ≤ De.
    Dönüş: (ad, geçti_mi, sınır, gerçek) listesi.
    """
    checks = [
        ("7.5.3.1 r <= 0.2·Di", r <= 0.2 * Di, 0.2 * Di, r),
        ("7.5.3.1 r >= 0.06·Di", r >= 0.06 * Di, 0.06 * Di, r),
        ("7.5.3.1 r >= 2·e", r >= 2.0 * e, 2.0 * e, r),
        ("7.5.3.1 e <= 0.08·De", e <= 0.08 * De, 0.08 * De, e),
        ("7.5.3.1 R <= De", R <= De, De, R),
    ]
    if ea is not None:
        checks.insert(4, ("7.5.3.1 ea >= 0.001·De", ea >= 0.001 * De, 0.001 * De, ea))
    return checks


def torispherical_fb(rp02_t: float, cold_spun_austenitic: bool = False) -> float:
    """EN 13445-3, 7.5.3.2 — burkulma kontrolü tasarım gerilmesi fb.

    fb = Rp0,2/T / 1,5 ; soğuk sıvanmış dikişsiz östenitik bombe: fb = 1,6·Rp0,2/T / 1,5.
    """
    if rp02_t <= 0:
        raise ValueError("EN 13445-3, 7.5.3.2: Rp0,2/T pozitif olmalı")
    fb = rp02_t / 1.5
    return 1.6 * fb if cold_spun_austenitic else fb


def torispherical_beta(e: float, R: float, r: float, Di: float) -> float:
    """EN 13445-3, 7.5.3.5 — β katsayısı (Şekil 7.5-1 grafiğinin denklem biçimi).

    Y = min(e/R ; 0,04) ; Z = log10(1/Y) ; X = r/Di ; N = 1,006 − 1/(6,2 + (90·Y)⁴)
    β0,06 = N·(−0,3635·Z³ + 2,2124·Z² − 3,2937·Z + 1,8873)
    β0,1  = N·(−0,1833·Z³ + 1,0383·Z² − 1,2943·Z + 0,837)
    β0,2  = max(0,95·(0,56 − 1,94·Y − 82,5·Y²) ; 0,5)
    0,06 < X < 0,1 : β = 25·[(0,1 − X)·β0,06 + (X − 0,06)·β0,1]
    0,1  < X < 0,2 : β = 10·[(0,2 − X)·β0,1 + (X − 0,1)·β0,2]
    """
    if e <= 0 or R <= 0 or Di <= 0:
        raise ValueError("EN 13445-3, 7.5.3.5: e, R, Di pozitif olmalı")
    X = r / Di
    if X < 0.06 - 1e-12 or X > 0.2 + 1e-12:
        raise ValueError(f"EN 13445-3, 7.5.3.5: r/Di = {X:.4f} 0,06–0,2 aralığı dışında")
    Y = min(e / R, 0.04)
    Z = math.log10(1.0 / Y)
    N = 1.006 - 1.0 / (6.2 + (90.0 * Y) ** 4)
    b006 = N * (-0.3635 * Z ** 3 + 2.2124 * Z ** 2 - 3.2937 * Z + 1.8873)
    b01 = N * (-0.1833 * Z ** 3 + 1.0383 * Z ** 2 - 1.2943 * Z + 0.837)
    b02 = max(0.95 * (0.56 - 1.94 * Y - 82.5 * Y ** 2), 0.5)
    if X <= 0.1:
        return 25.0 * ((0.1 - X) * b006 + (X - 0.06) * b01)
    return 10.0 * ((0.2 - X) * b01 + (X - 0.1) * b02)


def _knuckle_lever(R: float, Di: float) -> float:
    """0,75·R + 0,2·Di (7.5.3.2 ey/eb denklemlerindeki ortak uzunluk)."""
    return 0.75 * R + 0.2 * Di


def head_torispherical_thickness(
    P: float, Di: float, R: float, r: float, f: float, z: float, fb: float,
) -> dict:
    """EN 13445-3, 7.5.3.2 — torisferik bombe gerekli kalınlığı e = max(es, ey, eb).

    es = P·R / (2·f·z − 0,5·P)                               (taç, 7.5-1)
    ey = β·P·(0,75·R + 0,2·Di) / f                            (büküm akma, 7.5-2)
    eb = (0,75·R + 0,2·Di)·[P/(111·fb)·(Di/r)^0,825]^(1/1,5)  (büküm burkulma, 7.5-3)
    β, e'ye bağlıdır (7.5.3.5) → ey = β(ey)·P·k/f kökü ikiye bölme ile bulunur
    (sol taraf artan, β(e) azalan → tek kök). z yalnız taç denkleminde.
    """
    if P <= 0 or f <= 0 or fb <= 0 or z <= 0:
        raise ValueError("EN 13445-3, 7.5.3: P, f, fb, z pozitif olmalı")
    if r <= 0 or R <= 0 or Di <= 0:
        raise ValueError("EN 13445-3, 7.5.3: R, r, Di pozitif olmalı")
    denom = 2.0 * f * z - 0.5 * P
    if denom <= 0:
        raise ValueError(f"EN 13445-3, 7.5.3: 2·f·z − 0,5·P = {denom:.4f} ≤ 0")
    es = P * R / denom
    k = _knuckle_lever(R, Di)

    def g(e: float) -> float:
        return e - torispherical_beta(e, R, r, Di) * P * k / f

    lo, hi = 1e-9 * R, R
    if g(hi) < 0:
        raise ValueError("EN 13445-3, 7.5.3.2: ey taç yarıçapını aşıyor — geometri/basınç geçersiz")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(mid) < 0:
            lo = mid
        else:
            hi = mid
    ey = hi
    beta = torispherical_beta(ey, R, r, Di)
    eb = k * (P / (111.0 * fb) * (Di / r) ** 0.825) ** (1.0 / 1.5)
    e = max(es, ey, eb)
    governing = "es" if e == es else ("ey" if e == ey else "eb")
    return {"es": es, "ey": ey, "eb": eb, "beta": beta, "e": e, "governing": governing, "k": k}


def torispherical_max_pressure(
    Di: float, R: float, r: float, ea: float, f: float, z: float, fb: float,
) -> dict:
    """EN 13445-3, 7.5.3.4 — izin verilen azami basınç (kalınlık prosedürünün tersi).

    Ps = 2·f·z·ea / (R + 0,5·ea)
    Py = f·ea / (β·(0,75·R + 0,2·Di)),  β = β(ea)
    Pb = 111·fb·(ea/(0,75·R + 0,2·Di))^1,5·(r/Di)^0,825
    P_max = min(Ps, Py, Pb). Ayrıca aynı prosedür ikiye bölme ile tersine çözülür
    (head_torispherical_thickness(P).e = ea) ve P_bisect döner — iki yol tutarlı olmalı.
    """
    if ea <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={ea:.2f} mm")
    k = _knuckle_lever(R, Di)
    beta = torispherical_beta(ea, R, r, Di)
    Ps = 2.0 * f * z * ea / (R + 0.5 * ea)
    Py = f * ea / (beta * k)
    Pb = 111.0 * fb * (ea / k) ** 1.5 * (r / Di) ** 0.825
    P_max = min(Ps, Py, Pb)

    lo, hi = 0.0, 4.0 * f * z  # 2·f·z − 0,5·P > 0 için P < 4·f·z
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        try:
            ok = head_torispherical_thickness(mid, Di, R, r, f, z, fb)["e"] <= ea
        except ValueError:
            ok = False
        if ok:
            lo = mid
        else:
            hi = mid
    governing = "Ps" if P_max == Ps else ("Py" if P_max == Py else "Pb")
    return {"Ps": Ps, "Py": Py, "Pb": Pb, "beta": beta, "P_max": P_max,
            "P_bisect": lo, "governing": governing, "k": k}


# ── EN 13445-3, 5.5.4: Yarım küresel bombe ──────────────────────────────────

def head_hemispherical_thickness(
    P: float,
    R: float,
    f: float,
    z: float,
) -> float:
    """EN 13445-3, 5.5.4 — Yarım küresel bombe et kalınlığı.

    e = P × R / (2 × f × z - 0.5 × P)

    Args:
        P: Tasarım basıncı (MPa).
        R: İç yarıçap (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.

    Returns:
        Gerekli kalınlık (mm).

    Referans: EN 13445-3, 5.5.4, Eq. (5.5.4-1)
    """
    denominator = 2 * f * z - 0.5 * P
    if denominator <= 0:
        raise ValueError(f"EN 13445-3, 5.5.4: 2×f×z - 0.5×P = {denominator:.4f} ≤ 0")

    return P * R / denominator


# ── PED test basıncı ──────────────────────────────────────────────────────────

def ped_test_pressure(
    ps_mpa: float,
    operating_pressure_max: float,
    coefficient_ps: float = 1.43,
    coefficient_op: float = 1.25,
) -> Tuple[float, str]:
    """PED test basıncı hesabı.

    PED 2014/68/EU Ek I, Madde 8.1'e uygun:
        P_test = max(coefficient_op × P_operating_max, coefficient_ps × PS)

    Varsayılan katsayılar:
        coefficient_op = 1.25 (çalışma azami yükü için)
        coefficient_ps = 1.43 (PS için)

    Args:
        ps_mpa: Azami izin verilen basınç / PS (MPa).
        operating_pressure_max: Azami çalışma basıncı (MPa).
        coefficient_ps: PS katsayısı (varsayılan 1.43).
        coefficient_op: Çalışma basıncı katsayısı (varsayılan 1.25).

    Returns:
        (P_test, limiter) — test basıncı ve hangi değerin limitleyici olduğu.

    Referans: PED 2014/68/EU, Annex I, 8.1
    """
    p_from_op = coefficient_op * operating_pressure_max
    p_from_ps = coefficient_ps * ps_mpa

    if p_from_op >= p_from_ps:
        return p_from_op, "operating_pressure"
    else:
        return p_from_ps, "PS"


# ── MAWP hesaplama ────────────────────────────────────────────────────────────

def mawp_from_shell(
    R: float,
    e_actual: float,
    f: float,
    z: float,
    C: float = 0.0,
) -> float:
    """EN 13445-3, 5.4.2'den MAWP hesabı (silindirik gövde).

    P = f × z × e / (R + e/2)

    Args:
        R: İç yarıçap (mm).
        e_actual: Nominal et kalınlığı (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        C: Korozyon payı (mm).

    Returns:
        MAWP (MPa).
    """
    e = e_actual - C
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")

    mawp = f * z * e / (R + e / 2.0)
    return mawp


def mawp_from_head(
    head_type: str,
    D: float,
    e_actual: float,
    f: float,
    z: float,
    L: float = 0.0,
    r: float = 0.0,
    C: float = 0.0,
) -> float:
    """EN 13445-3'den MAWP hesabı (bombe).

    Args:
        head_type: Bombe tipi ("elliptical", "torispherical", "hemispherical").
        D: İç çap (mm).
        e_actual: Nominal et kalınlığı (mm).
        f: Tasarım gerilmesi (MPa).
        z: Birimleştirme katsayısı.
        L: Taç yarıçapı (mm) — torisferik için.
        r: Büküm yarıçapı (mm) — torisferik için.
        C: Korozyon payı (mm).

    Returns:
        MAWP (MPa).
    """
    e = e_actual - C
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")

    if head_type == "elliptical":
        # P = 4 × f × z × e / (D + e)
        return 4 * f * z * e / (D + e)

    elif head_type == "torispherical":
        raise ValueError(
            "EN 13445-3, 7.5.3: torisferik MAWP için torispherical_max_pressure() kullanılır "
            "(fb ve Di gerekir; eski basitleştirilmiş W formülü kaldırıldı)."
        )

    elif head_type == "hemispherical":
        R = D / 2.0
        # P = 2 × f × z × e / (R + 0.5 × e)
        return 2 * f * z * e / (R + 0.5 * e)

    else:
        raise ValueError(f"Desteklenmeyen bombe tipi: {head_type}")


# ── E02: EN 13445-3, 7.6 — Konik bölümler ve koni/silindir birleşimleri ─────
# verified=False: lisanslı EN 13445-3 metniyle satır satır doğrulanmadı.
# Grafik/tablo katsayısı İÇERMEZ; yalnız kapalı formlu denklemler.

def cone_thickness_internal_pressure(P: float, Di: float, f: float, z: float, alpha_deg: float) -> float:
    """EN 13445-3, 7.6.4 — Konik gövde iç basınç gerekli kalınlığı.

    e_con = P·Di / (2·f·z − P) · 1/cos α

    Di: kalınlığın arandığı noktadaki iç çap (büyük uç iç çapı en elverişsiz/
    muhafazakâr seçimdir). α: yarı tepe açısı.
    """
    if not 0.0 <= alpha_deg < 90.0:
        raise ValueError(f"EN 13445-3, 7.6: yarı tepe açısı 0 ≤ α < 90° olmalı: {alpha_deg}")
    denom = 2.0 * f * z - P
    if denom <= 0:
        raise ValueError(f"EN 13445-3, 7.6.4: 2·f·z − P = {denom:.4f} ≤ 0. Basınç çok yüksek.")
    return P * Di / denom / math.cos(math.radians(alpha_deg))


def cone_mawp(Di: float, e: float, f: float, z: float, alpha_deg: float) -> float:
    """7.6.4 denkleminin P için çözümü: P = 2·f·z·e·cos α / (Di + e·cos α).

    e: korozyonlu (analiz) kalınlığı.
    """
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")
    c = math.cos(math.radians(alpha_deg))
    return 2.0 * f * z * e * c / (Di + e * c)


def cone_large_end_beta(Dc: float, e: float, alpha_deg: float) -> float:
    """EN 13445-3, 7.6.6 — büküm (knuckle) olmayan büyük uç birleşimi β katsayısı.

    β = (1/3)·√(Dc/e)·tan α / (1 + 1/√cos α) − 0.15
    """
    a = math.radians(alpha_deg)
    return (1.0 / 3.0) * math.sqrt(Dc / e) * math.tan(a) / (1.0 + 1.0 / math.sqrt(math.cos(a))) - 0.15


def cone_large_end_required_thickness(P: float, Dc: float, f: float, alpha_deg: float) -> Tuple[float, float]:
    """EN 13445-3, 7.6.6 — büyük uç birleşim kalınlığı e_j (sabit nokta çözümü).

    e_j = P·Dc·β(e_j) / (2·f). β, e_j'ye bağlı olduğundan e = P·Dc·β(e)/(2f)
    denkleminin kökü ikiye bölme ile bulunur (sol taraf artan, sağ taraf azalan
    → tek kök). Dönüş: (e_j, β(e_j)). β ≤ 0 ise birleşim bu denklemle sınırlanmaz;
    e_j = 0 döner (gövde/koni membran kalınlığı ayrıca kontrol edilir).
    """
    if P <= 0 or f <= 0 or Dc <= 0:
        raise ValueError("EN 13445-3, 7.6.6: P, f, Dc pozitif olmalı")

    def g(e: float) -> float:
        return e - P * Dc * cone_large_end_beta(Dc, e, alpha_deg) / (2.0 * f)

    lo, hi = 1e-9 * Dc, Dc
    if g(hi) < 0:
        raise ValueError("EN 13445-3, 7.6.6: birleşim kalınlığı Dc'yi aşıyor — geometri geçersiz")
    if g(lo) >= 0:
        return 0.0, cone_large_end_beta(Dc, lo, alpha_deg)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(mid) < 0:
            lo = mid
        else:
            hi = mid
    e_j = hi
    beta = cone_large_end_beta(Dc, e_j, alpha_deg)
    if beta <= 0:
        return 0.0, beta
    return e_j, beta


def cone_small_end_beta_h(Dc: float, e1: float, e2: float, alpha_deg: float) -> Tuple[float, float, float]:
    """EN 13445-3, 7.6.8 — küçük uç birleşimi β_H katsayısı.

    s = e2/e1
    s < 1 : τ = s·√(s/cos α) + √((1 + s²)/2)
    s ≥ 1 : τ = 1 + √(s·(1 + s²)/(2·cos α))
    β_H = 0.4·√(Dc/e1)·tan α / τ + 0.5
    Dönüş: (s, τ, β_H). e1: silindir, e2: koni analiz kalınlığı.
    """
    if e1 <= 0 or e2 <= 0:
        raise ValueError("EN 13445-3, 7.6.8: e1 ve e2 pozitif olmalı")
    a = math.radians(alpha_deg)
    c = math.cos(a)
    s = e2 / e1
    if s < 1.0:
        tau = s * math.sqrt(s / c) + math.sqrt((1.0 + s * s) / 2.0)
    else:
        tau = 1.0 + math.sqrt(s * (1.0 + s * s) / (2.0 * c))
    beta_h = 0.4 * math.sqrt(Dc / e1) * math.tan(a) / tau + 0.5
    return s, tau, beta_h


def cone_small_end_max_pressure(Dc: float, e1: float, f: float, beta_h: float) -> float:
    """EN 13445-3, 7.6.8 — küçük uç izin verilen basınç: P_max = 2·f·e1 / (Dc·β_H)."""
    return 2.0 * f * e1 / (Dc * beta_h)


# ── E02: EN 13445-3, 10 — Desteksiz dairesel düz kapak (iç basınç) ──────────

def flat_end_thickness(P: float, D: float, f: float, C: float) -> float:
    """EN 13445-3, 10.4 (kaynaklı) biçimi: e = C·D·√(P/f).

    C (C1/C2) katsayısı lisanslı grafikten (EN 13445-3 Şekil 10.4-x) KULLANICI
    tarafından okunur; burada üretilmez/interpolasyon yapılmaz (K6).
    """
    if C <= 0 or f <= 0 or D <= 0 or P < 0:
        raise ValueError("EN 13445-3, 10: C, f, D pozitif; P ≥ 0 olmalı")
    return C * D * math.sqrt(P / f)


def flat_end_mawp(D: float, e: float, f: float, C: float) -> float:
    """flat_end_thickness'ın P için çözümü: P = f·(e/(C·D))²."""
    if e <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: e={e:.2f} mm")
    return f * (e / (C * D)) ** 2


# ── E04: EN 13445-3 Madde 6 — nominal tasarım gerilmesi; 5.6 z; EN 13445-5 test basınçları ──
# verified=False: bölenler ve denklem biçimleri bellekten yazıldı, lisanslı metinle
# satır satır doğrulanmadı (K6: metin gömülmez). Alt madde numaraları doğrulanmadı;
# çağıran taraf sonucu en fazla REVIEW_REQUIRED yapar.

# Malzeme grubu -> (tasarım için gerekli özellikler, test için gerekli özellikler)
EN_STRESS_REQUIRED_PROPERTIES = {
    "ferritic": (("rp02_t", "rm_20"), ("rp02_test",)),
    "austenitic_a30": (("rp10_t",), ("rp10_test",)),
    "austenitic_a35": (("rp10_t", "rm_t"), ("rp10_test", "rm_test")),
    "cast": (("rp02_t", "rm_20"), ("rp02_test",)),
}

# Östenitik alt grupların kopma uzaması alt sınırı (%)
EN_AUSTENITIC_MIN_ELONGATION = {"austenitic_a30": 30.0, "austenitic_a35": 35.0}


def nominal_design_stress(group: str, p: dict) -> Tuple[float, str]:
    """EN 13445-3 Madde 6 — normal çalışma için azami nominal tasarım gerilmesi f_d.

    ferritic        : f = min(Rp0,2/T / 1,5 ; Rm/20 / 2,4)
    austenitic_a30  : f = Rp1,0/T / 1,5
    austenitic_a35  : f = max(Rp1,0/T / 1,5 ; min(Rp1,0/T / 1,2 ; Rm/T / 3,0))
    cast            : f = min(Rp0,2/T / 1,9 ; Rm/20 / 3,0)

    Returns: (f_d, formül metni)
    """
    if group == "ferritic":
        return min(p["rp02_t"] / 1.5, p["rm_20"] / 2.4), "min(Rp0.2/T/1.5 ; Rm/20/2.4)"
    if group == "austenitic_a30":
        return p["rp10_t"] / 1.5, "Rp1.0/T/1.5"
    if group == "austenitic_a35":
        f = max(p["rp10_t"] / 1.5, min(p["rp10_t"] / 1.2, p["rm_t"] / 3.0))
        return f, "max(Rp1.0/T/1.5 ; min(Rp1.0/T/1.2 ; Rm/T/3.0))"
    if group == "cast":
        return min(p["rp02_t"] / 1.9, p["rm_20"] / 3.0), "min(Rp0.2/T/1.9 ; Rm/20/3.0)"
    raise ValueError(f"Bilinmeyen EN malzeme grubu: {group}")


def nominal_test_stress(group: str, p: dict) -> Tuple[float, str]:
    """EN 13445-3 Madde 6 — test durumu için azami nominal gerilme f_test.

    ferritic        : f_test = Rp0,2/Ttest / 1,05
    austenitic_a30  : f_test = Rp1,0/Ttest / 1,05
    austenitic_a35  : f_test = max(Rp1,0/Ttest / 1,05 ; Rm/Ttest / 2)
    cast            : f_test = Rp0,2/Ttest / 1,33
    """
    if group == "ferritic":
        return p["rp02_test"] / 1.05, "Rp0.2/Ttest/1.05"
    if group == "austenitic_a30":
        return p["rp10_test"] / 1.05, "Rp1.0/Ttest/1.05"
    if group == "austenitic_a35":
        return max(p["rp10_test"] / 1.05, p["rm_test"] / 2.0), "max(Rp1.0/Ttest/1.05 ; Rm/Ttest/2)"
    if group == "cast":
        return p["rp02_test"] / 1.33, "Rp0.2/Ttest/1.33"
    raise ValueError(f"Bilinmeyen EN malzeme grubu: {group}")


# EN 13445-3, 5.6 (Tablo 5.6-1): test grubu -> izin verilen en büyük z
EN_JOINT_COEFFICIENT_BY_TESTING_GROUP = {"1": 1.0, "2": 1.0, "3": 0.85, "4": 0.7}


def joint_coefficient_for_testing_group(testing_group: str) -> float:
    """EN 13445-5 test grubu (1a..4) -> EN 13445-3 5.6 birimleştirme katsayısı z."""
    key = str(testing_group)[:1]
    if key not in EN_JOINT_COEFFICIENT_BY_TESTING_GROUP:
        raise ValueError(f"Bilinmeyen EN 13445-5 test grubu: {testing_group}")
    return EN_JOINT_COEFFICIENT_BY_TESTING_GROUP[key]


def en_hydrotest_pressure(Pd: float, PS: float, stress_ratio: float) -> Tuple[float, str, float, float]:
    """EN 13445-5, 10.2.3.3.1 — Pt = max(1,25·Pd·fa/fT ; 1,43·PS).

    Returns: (Pt, limiter, 1,25·Pd·fa/fT, 1,43·PS)
    """
    if stress_ratio <= 0:
        raise ValueError(f"fa/fT oranı pozitif olmalı: {stress_ratio}")
    p_pd = 1.25 * Pd * stress_ratio
    p_ps = 1.43 * PS
    return (p_pd, "design_pressure", p_pd, p_ps) if p_pd > p_ps else (p_ps, "PS", p_pd, p_ps)


def en_pneumatic_test_pressure(Pd: float, stress_ratio: float, factor: float) -> float:
    """EN 13445-5 pnömatik test — Pt = k·Pd·fa/fT (k kullanıcı girdisi, gömülmez)."""
    if stress_ratio <= 0 or factor <= 0:
        raise ValueError("fa/fT oranı ve pnömatik katsayı pozitif olmalı")
    return factor * Pd * stress_ratio


__all__ = [
    "shell_thickness_internal_pressure",
    "shell_required_nominal_thickness",
    "head_elliptical_thickness",
    "head_torispherical_thickness",
    "torispherical_applicability",
    "torispherical_beta",
    "torispherical_fb",
    "torispherical_max_pressure",
    "head_hemispherical_thickness",
    "ped_test_pressure",
    "mawp_from_shell",
    "mawp_from_head",
    "cone_thickness_internal_pressure",
    "cone_mawp",
    "cone_large_end_beta",
    "cone_large_end_required_thickness",
    "cone_small_end_beta_h",
    "cone_small_end_max_pressure",
    "flat_end_thickness",
    "flat_end_mawp",
    "nominal_design_stress",
    "nominal_test_stress",
    "joint_coefficient_for_testing_group",
    "en_hydrotest_pressure",
    "en_pneumatic_test_pressure",
]
