"""Destek formülleri — Zick analizi (saddle) ve skirt temeli.

K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referanslar:
- Zick, L.P., "Stresses in Large Horizontal Cylindrical Pressure Vessels on Two Saddle Supports"
- Moss, Pressure Vessel Design Manual (PVDM), Proc. 4-1 / ASME VIII-1 UG-23(b) (etek; madde metni gömülmez)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


# ── Saddle (Zick analizi) ─────────────────────────────────────────────────────
#
# Yapı Zick (1951) / Moss PVDM Prosedür 3-10 / Megyesy'e göredir. K1…K7 katsayı
# tabloları lisanslı olabileceğinden BURADA YOKTUR (K6): kullanıcı tablodan
# okuyup girer. Adlandırma Moss/Megyesy'dir; Zick 1951 orijinalinde numaralama
# farklıdır (orada K3 çevresel moment sabitidir):
#   K1  boyuna eğilme, eyer kesiti (çekme tarafı); halkalı / başlık-destekli π
#   K2  kabuk teğetsel kesme (halkalı: 1/π = 0,319 sabit)
#   K3  başlık kesmesi (yalnız A ≤ R/2)
#   K6  eyer boynuzunda çevresel eğilme momenti sabiti
#   K7  eyer altı kabuk çevresel basma sabiti
# Semboller: Q eyer reaksiyonu (N), R ortalama yarıçap, t korozyonlu et, L
# teğet-teğet kap boyu, A eyerin en yakın teğet çizgisine uzaklığı, H BAŞLIK
# DERİNLİĞİ, b eyer genişliği. Birimler mm / N / MPa.

_ZICK_EFF_WIDTH_C = 1.56  # kabuğun eyerle birlikte çalışan etkin genişliği: b + 1,56·√(R·t)


def saddle_reaction(W_total: float, n_saddles: int = 2) -> float:
    """Simetrik durumda eyer reaksiyonu Q = W_total / n_saddles (N)."""
    if n_saddles <= 0:
        raise ValueError("Saddle sayısı pozitif olmalı")
    return W_total / n_saddles


def saddle_reactions_two(
    W_total: float, x_left: float, x_right: float, x_cg: float
) -> Tuple[float, float]:
    """İki eyerin reaksiyonları — moment dengesinden (asimetride W/2 değil).

    Q_sol = W·(x_sağ − x_cg)/(x_sağ − x_sol),  Q_sağ = W − Q_sol
    """
    if x_right <= x_left:
        raise ValueError("Eyer konumları x_sağ > x_sol olmalı")
    q_left = W_total * (x_right - x_cg) / (x_right - x_left)
    return q_left, W_total - q_left


def zick_head_depth(head) -> float:
    """Başlık derinliği H (mm) — teğet çizgisinden başlık ucuna (düz flanş HARİÇ).

    Eliptik: crown_depth verilmişse o, yoksa D/4 (2:1). Yarıküresel: D/2.
    Torisferik: crown_depth verilmişse o; yoksa Rc, rk yarıçaplarından
    h = Rc − √((Rc − rk)² − (D/2 − rk)²) (standart ASME F&D: Rc = D, rk = 0,06 D).
    Düz: 0.
    """
    D = head.inside_diameter
    kind = getattr(head.type, "value", head.type)
    if kind == "flat":
        return 0.0
    if kind == "hemispherical":
        return D / 2.0
    if getattr(head, "crown_depth", None):
        return float(head.crown_depth)
    if kind == "elliptical":
        return D / 4.0
    Rc = head.crown_radius
    rk = head.knuckle_radius
    if kind == "torispherical" and getattr(head, "torispherical_geometry", "") == "standard_asme_fd":
        Rc, rk = D, 0.06 * D
    if not Rc or not rk:
        raise ValueError("Torisferik başlık derinliği için crown_depth veya Rc/rk gerekli")
    return Rc - math.sqrt((Rc - rk) ** 2 - (D / 2.0 - rk) ** 2)


def zick_moment_saddle(Q: float, L: float, R: float, A: float, H: float) -> float:
    """Zick M1 — eyer kesitindeki boyuna eğilme momenti (N·mm; + = eyerde üst lif çekme).

    M1 = Q·A·[1 − (1 − A/L + (R² − H²)/(2·A·L)) / (1 + 4H/(3L))]

    Kontrol (H = 0, R → 0): M1 = Q·A²/L (iki ucu A taşan basit kiriş, w·A²/2).
    """
    if L <= 0 or A <= 0 or R <= 0:
        raise ValueError("L, A, R pozitif olmalı")
    return Q * A * (
        1.0 - (1.0 - A / L + (R * R - H * H) / (2.0 * A * L)) / (1.0 + 4.0 * H / (3.0 * L))
    )


def zick_moment_midspan(Q: float, L: float, R: float, A: float, H: float) -> float:
    """Zick M2 — orta açıklık boyuna eğilme momenti (N·mm; + = alt lif çekme).

    M2 = (Q·L/4)·[(1 + 2(R² − H²)/L²)/(1 + 4H/(3L)) − 4A/L]

    Kontrol (H = 0, R → 0): M2 = Q·L/4 − Q·A (iki eşit yüklü basit kiriş).
    """
    if L <= 0 or R <= 0:
        raise ValueError("L, R pozitif olmalı")
    return (Q * L / 4.0) * (
        (1.0 + 2.0 * (R * R - H * H) / (L * L)) / (1.0 + 4.0 * H / (3.0 * L)) - 4.0 * A / L
    )


def zick_longitudinal_stress_saddle(M1: float, K1: float, R: float, t: float) -> float:
    """S1 (eyer kesiti) = |M1| / (K1·R²·t)  [MPa]. K1: halkalı/başlık-destekli π."""
    if K1 <= 0 or R <= 0 or t <= 0:
        raise ValueError("K1, R, t pozitif olmalı")
    return abs(M1) / (K1 * R * R * t)


def zick_longitudinal_stress_midspan(M2: float, R: float, t: float) -> float:
    """S1 (orta açıklık) = |M2| / (π·R²·t)  [MPa]."""
    if R <= 0 or t <= 0:
        raise ValueError("R, t pozitif olmalı")
    return abs(M2) / (math.pi * R * R * t)


def zick_pressure_longitudinal(P: float, R: float, t: float) -> float:
    """Boyuna basınç gerilmesi P·R/(2t) — yalnız çekme tarafına eklenir."""
    if t <= 0:
        raise ValueError("t pozitif olmalı")
    return P * R / (2.0 * t)


def zick_effective_width(b: float, R: float, t: float) -> float:
    """Etkin genişlik b + 1,56·√(R·t) (Zick düzeltmesi; eski 10·t yerine)."""
    if b <= 0 or R <= 0 or t <= 0:
        raise ValueError("b, R, t pozitif olmalı")
    return b + _ZICK_EFF_WIDTH_C * math.sqrt(R * t)


def zick_shear_shell(
    Q: float, R: float, t: float, L: float, A: float, H: float, K2: float,
    head_stiffened: bool = False,
) -> float:
    """Kabuk teğetsel kesme gerilmesi (MPa).

    Eyer başlıktan uzak (A > R/2) veya halkalı: S2 = K2·Q/(R·t)·(L − 2A)/(L + 4H/3)
    Eyer başlığa yakın (A ≤ R/2, halkasız): S2 = K2·Q/(R·t)
    """
    if K2 <= 0 or R <= 0 or t <= 0 or L <= 0:
        raise ValueError("K2, R, t, L pozitif olmalı")
    base = K2 * Q / (R * t)
    if head_stiffened:
        return base
    return base * (L - 2.0 * A) / (L + 4.0 * H / 3.0)


def zick_shear_head(Q: float, R: float, t_head: float, K3: float) -> float:
    """Başlıkta ek kesme gerilmesi S3 = K3·Q/(R·t_h) (yalnız A ≤ R/2)."""
    if K3 <= 0 or R <= 0 or t_head <= 0:
        raise ValueError("K3, R, t_h pozitif olmalı")
    return K3 * Q / (R * t_head)


def zick_circumferential_membrane(Q: float, R: float, t: float, b: float) -> float:
    """Boynuz doğrudan (membran) terimi Q/(4·t·(b + 1,56√(R·t))) — MPa, basma."""
    return Q / (4.0 * t * zick_effective_width(b, R, t))


def zick_circumferential_horn(
    Q: float, R: float, t: float, b: float, L: float, K6: float
) -> float:
    """Eyer boynuzunda toplam çevresel gerilme büyüklüğü (MPa, basma).

    L ≥ 8R:  S4 = Q/(4t(b+1,56√(Rt))) + 12·K6·Q·R/(L·t²)
    L < 8R:  S4 = Q/(4t(b+1,56√(Rt))) + 3·K6·Q/(2·t²)
    (her iki terim basma; büyüklük döner.)
    """
    if K6 <= 0 or L <= 0:
        raise ValueError("K6, L pozitif olmalı")
    membrane = zick_circumferential_membrane(Q, R, t, b)
    if L >= 8.0 * R:
        bending = 12.0 * K6 * Q * R / (L * t * t)
    else:
        bending = 3.0 * K6 * Q / (2.0 * t * t)
    return membrane + bending


def zick_circumferential_bottom(Q: float, R: float, t: float, b: float, K7: float) -> float:
    """Kabuk tabanı (eyer altı) çevresel basma S5 = K7·Q/(t·(b + 1,56√(R·t))) (MPa)."""
    if K7 <= 0:
        raise ValueError("K7 pozitif olmalı")
    return K7 * Q / (t * zick_effective_width(b, R, t))


def saddle_stress_limits(S_allow: float, S_yield: float, E: float = 1.0) -> dict:
    """Zick sınırları (ayrı ayrı; tek bir 0,67·S DEĞİL).

    S1 çekme        ≤ S·E
    S1 basma        ≤ 0,5·Sy   (burkulma B sınırı UG-23(b) ayrıca kontrol edilir)
    S2 kabuk kesme  ≤ 0,8·S
    S3 başlık kesme ≤ 1,25·S
    S4 boynuz çevresel ≤ 1,5·S
    S5 taban/aşınma plakası basma ≤ 0,5·Sy
    """
    return {
        "S1_tension": S_allow * E,
        "S1_compression": 0.5 * S_yield,
        "S2": 0.8 * S_allow,
        "S3": 1.25 * S_allow,
        "S4": 1.5 * S_allow,
        "S5": 0.5 * S_yield,
    }


# ── Skirt (etek destek) ───────────────────────────────────────────────────────

def skirt_bending_stress(
    M_overturning: float,
    D_skirt: float,
    t_skirt: float,
) -> float:
    """Skirt eğilme gerilmesi.

    S_bending = 4×M / (π × D_skirt² × t_skirt)

    Args:
        M_overturning: Devirme momenti (N·mm).
        D_skirt: Etek ORTALAMA çapı (mm) — dış çap değil.
        t_skirt: Skirt et kalınlığı (mm).

    Returns:
        Eğilme gerilmesi (MPa).
    """
    if D_skirt <= 0 or t_skirt <= 0:
        raise ValueError("D_skirt, t_skirt pozitif olmalı")

    return 4.0 * M_overturning / (math.pi * D_skirt * D_skirt * t_skirt)


def skirt_compression_stress(
    W_total: float,
    D_skirt: float,
    t_skirt: float,
) -> float:
    """Skirt basma gerilmesi.

    S_compression = W / (π × D_skirt × t_skirt)

    Args:
        W_total: Toplam ağırlık (N).
        D_skirt: Etek ORTALAMA çapı (mm) — dış çap değil.
        t_skirt: Skirt et kalınlığı (mm).

    Returns:
        Basma gerilmesi (MPa).
    """
    if D_skirt <= 0 or t_skirt <= 0:
        raise ValueError("D_skirt, t_skirt pozitif olmalı")

    return W_total / (math.pi * D_skirt * t_skirt)


def skirt_combined_stress(
    S_bending: float,
    S_compression: float,
) -> float:
    """Skirt birleşik gerilme (eğilme + basma).

    S_combined = S_bending + S_compression

    Args:
        S_bending: Eğilme gerilmesi (MPa).
        S_compression: Basma gerilmesi (MPa).

    Returns:
        Birleşik gerilme (MPa).
    """
    return S_bending + S_compression


def skirt_tensile_stress(
    M_overturning: float,
    W_min: float,
    D_skirt: float,
    t_skirt: float,
) -> float:
    """Etek çekme tarafı gerilmesi (kaldırma eğilimi).

    S_t = M / Z − W_min / A,  A = π·D_m·t,  Z = π·D_m²·t/4

    Pozitif değer, rüzgâr tarafında çekme (ankraj/kaldırma) demektir. W_min,
    en küçük eşzamanlı ağırlıktır (boş kap); işletme/test ağırlığı DEĞİL.

    Returns:
        Çekme gerilmesi (MPa); negatifse çekme oluşmaz (tüm kesit basma).
    """
    if D_skirt <= 0 or t_skirt <= 0:
        raise ValueError("D_skirt, t_skirt pozitif olmalı")
    return (
        skirt_bending_stress(M_overturning, D_skirt, t_skirt)
        - skirt_compression_stress(W_min, D_skirt, t_skirt)
    )


def skirt_geometric_factor_A(D_skirt: float, t_skirt: float) -> float:
    """Silindirik etek için geometrik faktör A = 0,125 / (R/t), R = D_m/2.

    Yalnız bilgi amaçlıdır: UG-23(b) B çizelgesinde okuma için A üretir. B
    değeri eğri okumasıdır ve bu pakette YOKTUR (K6).
    """
    if D_skirt <= 0 or t_skirt <= 0:
        raise ValueError("D_skirt, t_skirt pozitif olmalı")
    return 0.125 / ((D_skirt / 2.0) / t_skirt)


# ── Leg (ayak destek) ─────────────────────────────────────────────────────────

def leg_pipe_section_area(D_outside: float, t_leg: float) -> float:
    """Boru kesitli ayağın taşıyıcı alanı (halka kesit).

    A = π/4 × (D_outside² - D_inside²),  D_inside = D_outside - 2×t_leg

    Ayak DOLU DAİRE değil, et kalınlığı `t_leg` olan bir borudur; kesit alanı
    dış çaptan türetilen dolu daireden küçüktür. Dolu daire varsayımı gerçek
    gerilmeyi olduğundan düşük gösterir (emniyetsiz).

    Args:
        D_outside: Ayak dış çapı (mm).
        t_leg: Ayak et kalınlığı (mm).

    Returns:
        Halka kesit alanı (mm²).
    """
    if D_outside <= 0 or t_leg <= 0:
        raise ValueError("D_outside, t_leg pozitif olmalı")
    D_inside = D_outside - 2.0 * t_leg
    if D_inside <= 0:
        raise ValueError(
            f"t_leg={t_leg} çok büyük: D_inside={D_inside} <= 0 (D_outside={D_outside})"
        )
    return math.pi / 4.0 * (D_outside * D_outside - D_inside * D_inside)


def leg_reaction_extremes(
    W_total: float,
    n_legs: int,
    M_overturning: float = 0.0,
    support_radius: float = 0.0,
) -> Tuple[float, float]:
    """Ayak takımında en kritik (maks/min) reaksiyon kuvveti.

    Simetrik dağılım varsayımı — takım tek bir birim olarak modellenir. Eşit
    aralıklı n ayak r yarıçaplı çember üzerindeyken devirme momenti eğilme
    eksenine uzaklıkla orantılı kuvvet doğurur (F_i = M·y_i / Σy²):

    n ≥ 3:  Σy² = n·r²/2  →  en yüklü ayak (moment ekseni bir ayağın
            üstündeyken):  ΔN = 2M/(n×r)          (= 4M/(n×D), D = 2r)
    n = 2:  iki ayak moment düzleminde karşılıklı → ΔN = M/(n×r)

    N_max = W/n + ΔN,  N_min = W/n − ΔN.

    Eski `M/(n×r)` n ≥ 3 için gerçek en kötü ayak yükünün YARISIYDI
    (emniyetsiz). Bağımsız kaynak: Moss, *Pressure Vessel Design Manual*
    (ankraj/ayak yükü `P = W/N ± 4M/(N·D)`). n = 2'de moment eksenine dik
    yönde ayaklar momenti taşıyamaz — bu yön kapsanmaz, yerleşim doğrulanmalı.

    r, ayakların kap ekseninden dağılım yarıçapıdır (moment kolu); ayak
    çapından türetilemez, ayrı girdidir.

    Args:
        W_total: Toplam ağırlık (N).
        n_legs: Ayak sayısı.
        M_overturning: Devirme momenti (N·mm). Varsayılan 0.
        support_radius: Dağılım yarıçapı (mm). Moment sıfırsa gerekmez.

    Returns:
        (N_max, N_min) — sırasıyla en yüklü ve en az yüklü (veya negatifse
        kaldırma talebindeki) ayak reaksiyonu (N).
    """
    if n_legs < 1:
        raise ValueError("n_legs en az 1 olmalı")
    if M_overturning > 0 and support_radius <= 0:
        raise ValueError("M_overturning > 0 ise support_radius pozitif olmalı")

    base = W_total / n_legs
    if support_radius > 0 and M_overturning > 0:
        if n_legs == 1:
            raise ValueError("Tek ayak devirme momentini taşıyamaz (n_legs ≥ 2 gerekir)")
        factor = 1.0 if n_legs == 2 else 2.0
        moment_term = factor * M_overturning / (n_legs * support_radius)
    else:
        moment_term = 0.0
    return base + moment_term, base - moment_term


def leg_base_pressure(N_max: float, A_leg: float) -> float:
    """Ayak kesitindeki eksenel yataklık gerilmesi.

    P = N_max / A_leg

    Args:
        N_max: En kritik ayak reaksiyonu (N).
        A_leg: Ayak taşıyıcı kesit alanı (mm²) — bkz. `leg_pipe_section_area`
            veya taban plakası alanı (`base_plate_area_mm2` verilmişse).

    Returns:
        Yataklık gerilmesi (MPa).
    """
    if A_leg <= 0:
        raise ValueError("A_leg pozitif olmalı")
    return N_max / A_leg


# ── Taban plakası ─────────────────────────────────────────────────────────────
# Yöntem: Moss, *Pressure Vessel Design Manual*, Procedure 4-12 (ayak taban
# plakası) — AISC ASD kolon tabanı konsol şerit yaklaşımıyla aynıdır.

def base_plate_bearing_pressure(N: float, length: float, width: float) -> float:
    """Temel yataklık basıncı q = N / (L × W) (MPa)."""
    if length <= 0 or width <= 0:
        raise ValueError(f"Plaka ölçüleri pozitif olmalı: {length}, {width}")
    return N / (length * width)


def base_plate_cantilevers(
    length: float,
    width: float,
    profile_depth: float,
    profile_width: float,
    depth_factor: float = 0.95,
    width_factor: float = 0.80,
) -> Tuple[float, float]:
    """Profil kenarından plaka kenarına konsol çıkıntıları (m, n).

        m = (L − depth_factor × h) / 2,   n = (W − width_factor × b)/2

    0,95/0,80 katsayıları I/U profil için kritik kesitin profil dış
    yüzünün biraz içinde oluştuğunu hesaba katar; boru için ikisi de 0,80
    alınır. Profil plakadan taşarsa ValueError.
    """
    if min(length, width, profile_depth, profile_width) <= 0:
        raise ValueError("Plaka ve profil ölçüleri pozitif olmalı")
    if profile_depth > length or profile_width > width:
        raise ValueError(
            f"Profil ({profile_depth}×{profile_width}) taban plakasından "
            f"({length}×{width}) büyük olamaz"
        )
    m = (length - depth_factor * profile_depth) / 2.0
    n = (width - width_factor * profile_width) / 2.0
    return m, n


def base_plate_required_thickness(q: float, cantilever: float, Fy: float) -> float:
    """Konsol şerit eğilmesinden gerekli plaka kalınlığı.

        t = c × √(3q / Fb),  Fb = 0,75·Fy   ⇔   t = 2c·√(q / Fy)

    Args:
        q: Yataklık basıncı (MPa).
        cantilever: En büyük konsol çıkıntısı c = max(m, n) (mm).
        Fy: Plaka akma dayanımı (MPa).
    """
    if q < 0:
        raise ValueError(f"q negatif olamaz: {q}")
    if cantilever < 0 or Fy <= 0:
        raise ValueError(f"cantilever ≥ 0 ve Fy > 0 olmalı: {cantilever}, {Fy}")
    return cantilever * math.sqrt(3.0 * q / (0.75 * Fy))


# ── Ayak yük dağılımı yardımcıları ────────────────────────────────────────────

def leg_lateral_load_per_leg(H_total: float, n_legs: int) -> float:
    """Toplam yatay taban yükünün ayak başına düşen payı H = H_toplam / n (N).

    Eşit paylaşım varsayımı (yönden bağımsız, simetrik takım).
    """
    if n_legs < 1:
        raise ValueError("n_legs en az 1 olmalı")
    if H_total < 0:
        raise ValueError(f"H_total negatif olamaz: {H_total}")
    return H_total / n_legs


def leg_eccentric_moment(N: float, eccentricity: float) -> float:
    """Ayak yükünün gövde yüzeyine göre eksantrik momenti M = N·e (N·mm)."""
    if eccentricity < 0:
        raise ValueError(f"eccentricity negatif olamaz: {eccentricity}")
    return abs(N) * eccentricity


def leg_base_moment(N: float, eccentricity: float, H_per_leg: float, leg_length: float) -> float:
    """Ayak tabanında kaynak/plakaya aktarılan moment (N·mm), muhafazakâr:

        M_taban = N·e + H·L

    N·e: eksantrik eksenel yükün ayak boyunca sabit kalan momenti (ankastre taban
    varsayımı); H·L: yatay yükün serbest uçlu konsol (K = 2,1) kolu.
    """
    if leg_length <= 0:
        raise ValueError(f"leg_length pozitif olmalı: {leg_length}")
    return leg_eccentric_moment(N, eccentricity) + abs(H_per_leg) * leg_length


__all__ = [
    "SaddleResult",
    "saddle_reaction",
    "zick_longitudinal_bending",
    "zick_circumferential_saddle",
    "zick_circumferential_crown",
    "zick_shear_stress",
    "saddle_stress_limits",
    "skirt_tensile_stress",
    "skirt_geometric_factor_A",
    "skirt_bending_stress",
    "skirt_compression_stress",
    "skirt_combined_stress",
    "leg_pipe_section_area",
    "leg_reaction_extremes",
    "leg_base_pressure",
    "base_plate_bearing_pressure",
    "base_plate_cantilevers",
    "base_plate_required_thickness",
    "leg_lateral_load_per_leg",
    "leg_eccentric_moment",
    "leg_base_moment",
]
