"""Destek formülleri — Zick analizi (saddle) ve skirt temeli.

K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referanslar:
- Zick, L.P., "Stresses in Large Horizontal Cylindrical Pressure Vessels on Two Saddle Supports"
- ASME VIII-1, Appendix G (skirt)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


# ── Saddle (Zick analizi) ─────────────────────────────────────────────────────

@dataclass
class SaddleResult:
    """Saddle hesap sonuçları."""
    Q: float = 0.0          # Saddle reaksiyon kuvveti (N)
    S1: float = 0.0         # Longitudinal bending stress at saddle (MPa)
    S2: float = 0.0         # Circumferential stress at saddle (MPa)
    S3: float = 0.0         # Circumferential stress at crown (MPa)
    S4: float = 0.0         # Shear stress (MPa)
    K: float = 0.0          # Saddle width factor
    C4: float = 0.0         # Saddle location factor


def saddle_reaction(
    W_total: float,
    n_saddles: int = 2,
) -> float:
    """Saddle reaksiyon kuvveti.

    Q = W_total / n_saddles

    Args:
        W_total: Toplam ağırlık (N) — kap + içerik + donanım.
        n_saddles: Saddle sayısı (tipik: 2).

    Returns:
        Saddle reaksiyon kuvveti (N).
    """
    if n_saddles <= 0:
        raise ValueError("Saddle sayısı pozitif olmalı")
    return W_total / n_saddles


def zick_longitudinal_bending(
    Q: float,
    L: float,
    R_m: float,
    t: float,
    A: float,
    h: float,
) -> float:
    """Zick — Saddle'da boyuna eğilme gerilmesi.

    S1 = Q × L / (4 × π × R_m² × t) × [1 - (2×A/L) / (1 + 4×h/(3×L))]

    Args:
        Q: Saddle reaksiyonu (N).
        L: Kap uzunluğu (saddle arası, mm).
        R_m: Ortalama yarıçap (mm).
        t: Gövde et kalınlığı (mm).
        A: Saddle'dan kap ucuna mesafe (mm).
        h: Saddle yüksekliği (mm).

    Returns:
        Boyuna eğilme gerilmesi (MPa).

    Referans: Zick analizi, S1
    """
    if R_m <= 0 or t <= 0 or L <= 0:
        raise ValueError("R_m, t, L pozitif olmalı")

    K1 = 1.0 - (2.0 * A / L) / (1.0 + 4.0 * h / (3.0 * L))
    S1 = Q * L / (4.0 * math.pi * R_m * R_m * t) * K1

    return S1


def zick_circumferential_saddle(
    Q: float,
    R_m: float,
    t: float,
    b: float,
) -> float:
    """Zick — Saddle'da çevresel gerilme.

    S2 = Q / (4 × t × (b + 1.56×sqrt(R_m×t)))

    Args:
        Q: Saddle reaksiyonu (N).
        R_m: Ortalama yarıçap (mm).
        t: Gövde et kalınlığı (mm).
        b: Saddle genişliği (mm).

    Returns:
        Çevresel gerilme (MPa).

    Referans: Zick analizi, S2
    """
    if R_m <= 0 or t <= 0 or b <= 0:
        raise ValueError("R_m, t, b pozitif olmalı")

    effective_width = b + 1.56 * math.sqrt(R_m * t)
    S2 = Q / (4.0 * t * effective_width)

    return S2


def zick_circumferential_crown(
    Q: float,
    R_m: float,
    t: float,
    b: float,
    L: float,
) -> float:
    """Zick — Taç noktasında çevresel gerilme.

    S3 = Q / (4 × t × (b + 1.56×sqrt(R_m×t))) × K2

    K2 = L/(4×R_m) faktörü.

    Args:
        Q: Saddle reaksiyonu (N).
        R_m: Ortalama yarıçap (mm).
        t: Gövde et kalınlığı (mm).
        b: Saddle genişliği (mm).
        L: Kap uzunluğu (mm).

    Returns:
        Taç noktasında çevresel gerilme (MPa).

    Referans: Zick analizi, S3
    """
    if R_m <= 0 or t <= 0 or b <= 0 or L <= 0:
        raise ValueError("R_m, t, b, L pozitif olmalı")

    K2 = L / (4.0 * R_m)
    effective_width = b + 1.56 * math.sqrt(R_m * t)
    S3 = Q / (4.0 * t * effective_width) * K2

    return S3


def zick_shear_stress(
    Q: float,
    R_m: float,
    t: float,
    A: float,
    L: float,
) -> float:
    """Zick — Kesme gerilmesi.

    S4 = Q / (π × R_m × t) × (L - 2×A) / (L + 4×h/3)

    Args:
        Q: Saddle reaksiyonu (N).
        R_m: Ortalama yarıçap (mm).
        t: Gövde et kalınlığı (mm).
        A: Saddle'dan kap ucuna mesafe (mm).
        L: Kap uzunluğu (mm).

    Returns:
        Kesme gerilmesi (MPa).

    Referans: Zick analizi, S4
    """
    if R_m <= 0 or t <= 0 or L <= 0:
        raise ValueError("R_m, t, L pozitif olmalı")

    S4 = Q / (math.pi * R_m * t) * (L - 2.0 * A) / L

    return S4


def saddle_stress_limits(
    S_allow: float,
) -> Tuple[float, float, float, float]:
    """Saddle gerilme limitleri.

    Zick limitleri:
    - S1 ≤ 0.67 × S_allow (çelik)
    - S2 ≤ 0.67 × S_allow (çelik)
    - S3 ≤ 0.67 × S_allow (çelik)
    - S4 ≤ 0.67 × S_allow (çelik)

    Args:
        S_allow: İzin verilen gerilme (MPa).

    Returns:
        (S1_limit, S2_limit, S3_limit, S4_limit)
    """
    limit = 0.67 * S_allow
    return limit, limit, limit, limit


# ── Skirt (etek destek) ───────────────────────────────────────────────────────

@dataclass
class SkirtResult:
    """Skirt hesap sonuçları."""
    P_base: float = 0.0         # Temel basıncı (MPa)
    S_bending: float = 0.0      # Eğilme gerilmesi (MPa)
    S_compression: float = 0.0  # Basınç gerilmesi (MPa)
    S_combined: float = 0.0     # Birleşik gerilme (MPa)


def skirt_base_pressure(
    W_total: float,
    M_overturning: float,
    D_skirt: float,
    t_skirt: float,
) -> float:
    """Skirt temel basıncı.

    P_base = W / (π × D_skirt × t_skirt) + 4×M / (π × D_skirt² × t_skirt)

    Args:
        W_total: Toplam ağırlık (N).
        M_overturning: Devirme momenti (N·mm).
        D_skirt: Skirt çapı (mm).
        t_skirt: Skirt et kalınlığı (mm).

    Returns:
        Temel basıncı (MPa).
    """
    if D_skirt <= 0 or t_skirt <= 0:
        raise ValueError("D_skirt, t_skirt pozitif olmalı")

    A_skirt = math.pi * D_skirt * t_skirt
    S_skirt = math.pi * D_skirt * D_skirt * t_skirt / 4.0

    P_axial = W_total / A_skirt
    P_bending = M_overturning / S_skirt

    return P_axial + P_bending


def skirt_bending_stress(
    M_overturning: float,
    D_skirt: float,
    t_skirt: float,
) -> float:
    """Skirt eğilme gerilmesi.

    S_bending = 4×M / (π × D_skirt² × t_skirt)

    Args:
        M_overturning: Devirme momenti (N·mm).
        D_skirt: Skirt çapı (mm).
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
        D_skirt: Skirt çapı (mm).
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

    Simetrik dağılım varsayımı — takım tek bir birim olarak modellenir:

    N_max = W/n + M/(n×r)
    N_min = W/n - M/(n×r)

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
        moment_term = M_overturning / (n_legs * support_radius)
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


__all__ = [
    "SaddleResult",
    "SkirtResult",
    "saddle_reaction",
    "zick_longitudinal_bending",
    "zick_circumferential_saddle",
    "zick_circumferential_crown",
    "zick_shear_stress",
    "saddle_stress_limits",
    "skirt_base_pressure",
    "skirt_bending_stress",
    "skirt_compression_stress",
    "skirt_combined_stress",
    "leg_pipe_section_area",
    "leg_reaction_extremes",
    "leg_base_pressure",
    "base_plate_bearing_pressure",
    "base_plate_cantilevers",
    "base_plate_required_thickness",
]
