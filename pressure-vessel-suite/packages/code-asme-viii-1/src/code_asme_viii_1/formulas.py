"""ASME VIII-1 formülleri — saf matematik.

Bu modül ASME Section VIII Division 1'deki temel formülleri uygular.
K1 kuralı: Formüller yalnızca hesap eklentilerinde.
K6 kuralı: Standart telifli metni gömülmez; yalnızca madde referansı saklanır.

Referans: ASME BPVC Section VIII Division 1 (2025 Edition)
"""

from __future__ import annotations

import math
from typing import Tuple


# ── UG-16(b): Mutlak minimum kalınlık ────────────────────────────────────────
# Korozyon payı hariç, herhangi bir malzeme için 1.5 mm (1/16 in). Basınçtan
# gelen gerekli kalınlık bunun altında çıksa bile seçilen (nominal) kalınlık
# bu tabanın altına düşemez.
UG16B_MINIMUM_THICKNESS_MM = 1.5


# ── UG-27: Silindirik gövde, iç basınç ───────────────────────────────────────

def shell_thickness_internal_pressure(
    P: float,
    R: float,
    S: float,
    E: float,
) -> Tuple[float, float, float]:
    """UG-27(c)(1) — Silindirik gövde iç basınç et kalınlığı.

    Çevresel gerilme (uzunlamasına dikişler — daha kritik):
        t = P × R / (S × E - 0.6 × P)

    Boyuna gerilme (çevresel dikişler):
        t = P × R / (2 × S × E + 0.4 × P)

    Args:
        P: Tasarım basıncı (MPa).
        R: **Korozyonlu** iç yarıçap (mm) — UG-27'nin istediği budur.
           İç korozyon iç yüzeyden metal yediği için R_korozyonlu = R_yeni + C
           (iç yarıçap BÜYÜR). Çağıran taraf bu dönüşümü yapar.
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi (joint efficiency).

    Returns:
        (t_circ, t_long, t_required) — çevresel, boyuna ve kritik (max) kalınlık (mm).

    Referans: UG-27(c)(1), Eq. (1) ve (2)
    Doğrulandı: ASME BPVC VIII-1 (2025), UG-27(c)(1) Eq. (1) ve (2)
    Bağımsız gözden geçiren: Formül matematiği web aramasıyla teyit edildi (2026-07-23)
    """
    # Çevresel gerilme (uzunlamasına dikiş) — Eq. (1)
    denominator_circ = S * E - 0.6 * P
    if denominator_circ <= 0:
        raise ValueError(
            f"UG-27: S×E - 0.6×P = {denominator_circ:.4f} ≤ 0. "
            "Basınç çok yüksek veya izin verilen gerilme çok düşük."
        )
    t_circ = P * R / denominator_circ

    # Boyuna gerilme (çevresel dikiş) — Eq. (2)
    denominator_long = 2 * S * E + 0.4 * P
    t_long = P * R / denominator_long

    # Kritik kalınlık (büyük olan)
    t_required = max(t_circ, t_long)

    return t_circ, t_long, t_required


def shell_required_nominal_thickness(
    t_required: float,
    C: float,
    mill_tolerance_factor: float = 0.875,
    forming_thinning: float = 0.0,
) -> float:
    """Gerekli nominal et kalınlığı.

    t_nominal = t_required / mill_tolerance_factor + C + forming_thinning

    ASME'de tipik mill toleransı %12.5 → factor = 0.875 (1 - 0.125).

    Args:
        t_required: Korozyonsuz gerekli kalınlık (mm).
        C: Korozyon payı (mm).
        mill_tolerance_factor: Sac tolerans faktörü (0.875 = %12.5 negatif).
        forming_thinning: Şekillendirme incelmesi (mm).

    Returns:
        Gerekli nominal kalınlık (mm).
    """
    if mill_tolerance_factor <= 0 or mill_tolerance_factor > 1.0:
        raise ValueError(f"mill_tolerance_factor 0-1 aralığında olmalı: {mill_tolerance_factor}")
    return t_required / mill_tolerance_factor + C + forming_thinning


# ── UG-32: Elipsoidal bombe ──────────────────────────────────────────────────

def head_elliptical_thickness(
    P: float,
    D: float,
    S: float,
    E: float,
) -> Tuple[float, float]:
    """UG-32(d) — 2:1 Elipsoidal bombe et kalınlığı.

    Standart 2:1 elipsoidal (D/6 geometrisi):
        K = 1/6 + (D/(2h))² / 6  (2:1 için K=1.0, genel formül)
        t = P × D / (2 × S × E - 0.2 × P)

    2:1 elipsoidal için:
        t = P × D / (2 × S × E - 0.2 × P)

    Args:
        P: Tasarım basıncı (MPa).
        D: **Korozyonlu** iç çap (mm) — D_korozyonlu = D_yeni + 2C (iç çap BÜYÜR).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        (t_required, K_factor) — gerekli kalınlık ve K faktörü.

    Referans: UG-32(d)
    Doğrulandı: ASME BPVC VIII-1 (2025), UG-32(d)
    Bağımsız gözden geçiren: Formül matematiği web aramasıyla teyit edildi (2026-07-23)
    """
    # 2:1 elipsoidal için K = 1.0
    K = 1.0

    denominator = 2 * S * E - 0.2 * P
    if denominator <= 0:
        raise ValueError(
            f"UG-32: 2×S×E - 0.2×P = {denominator:.4f} ≤ 0. "
            "Basınç çok yüksek."
        )
    t = P * D / denominator * K

    return t, K


# ── UG-32: Torisferik bombe ──────────────────────────────────────────────────

def head_torispherical_thickness(
    P: float,
    D: float,
    L: float,
    S: float,
    E: float,
    C: float = 0.0,
) -> Tuple[float, float]:
    """UG-32(e) — Torisferik bombe et kalınlığı.

    M = (3 + sqrt(L/r)) / 4
    t = P × L × M / (2 × S × E - 0.2 × P)

    Burada:
    L = taç yarıçapı (crown radius)
    r = büküm yarıçapı (knuckle radius)
    D = iç çap

    Args:
        P: Tasarım basıncı (MPa).
        D: İç çap (mm).
        L: Taç yarıçapı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        (t_required, M_factor)

    Referans: UG-32(e)
    """
    # Torisferik için r (knuckle radius) genellikle D/10 veya L/6
    # Bu fonksiyon L ve r'yi ayrı alır; r çağırıcıdan gelmeli
    # Burada L/r oranını doğrudan hesaplıyoruz
    raise NotImplementedError(
        "Torispherical head thickness requires knuckle_radius parameter. "
        "Use head_torispherical_thickness_full() instead."
    )


def head_torispherical_thickness_full(
    P: float,
    L: float,
    r: float,
    S: float,
    E: float,
) -> Tuple[float, float]:
    """UG-32(e) — Torisferik bombe et kalınlığı (tam parametreli).

    M = (3 + sqrt(L/r)) / 4
    t = P × L × M / (2 × S × E - 0.2 × P)

    Args:
        P: Tasarım basıncı (MPa).
        L: Taç yarıçapı (mm).
        r: Büküm yarıçapı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        (t_required, M_factor)

    Referans: UG-32(e)
    Doğrulandı: ASME BPVC VIII-1 (2025), UG-32(e)
    Bağımsız gözden geçiren: Formül matematiği web aramasıyla teyit edildi (2026-07-23)
    """
    if r <= 0:
        raise ValueError("Büküm yarıçapı (r) sıfırdan büyük olmalı")
    if L <= 0:
        raise ValueError("Taç yarıçapı (L) sıfırdan büyük olmalı")

    M = (3.0 + math.sqrt(L / r)) / 4.0

    denominator = 2 * S * E - 0.2 * P
    if denominator <= 0:
        raise ValueError(f"UG-32: 2×S×E - 0.2×P = {denominator:.4f} ≤ 0")

    t = P * L * M / denominator

    return t, M


# ── UG-32: Yarım küresel bombe ───────────────────────────────────────────────

def head_hemispherical_thickness(
    P: float,
    R: float,
    S: float,
    E: float,
) -> float:
    """UG-32(f) — Yarım küresel bombe et kalınlığı.

    t = P × R / (2 × S × E - 0.2 × P)

    Args:
        P: Tasarım basıncı (MPa).
        R: İç yarıçap (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        Gerekli kalınlık (mm).

    Referans: UG-32(f)
    Doğrulandı: ASME BPVC VIII-1 (2025), UG-32(f)
    Bağımsız gözden geçiren: Formül matematiği web aramasıyla teyit edildi (2026-07-23)
    """
    denominator = 2 * S * E - 0.2 * P
    if denominator <= 0:
        raise ValueError(f"UG-32: 2×S×E - 0.2×P = {denominator:.4f} ≤ 0")

    return P * R / denominator


# ── UG-99: Hidrostatik test basıncı ──────────────────────────────────────────

def hydrotest_pressure_asme(
    pressure_basis: float,
    allowable_stress_test: float,
    allowable_stress_design: float,
    temperature_ratio_factor: float = 1.0,
) -> float:
    """UG-99(b) — Hidrostatik test basıncı.

    P_test = 1.3 × MAWP × (S_test / S_design)

    Burada:
    S_test = test sıcaklığındaki izin verilen gerilme
    S_design = tasarım sıcaklığındaki izin verilen gerilme

    **Basınç tabanı MAWP'dir, tasarım basıncı DEĞİL.** UG-99(b) endnote'u tasarım
    basıncının yalnızca **MAWP hesaplanmadığında** yerine konabileceğini söyler.
    Bu suite MAWP'yi hesapladığı için muafiyet geçerli değildir; taban MAWP olmalıdır.
    MAWP ≥ P_tasarım olduğundan, tasarım basıncı kullanmak Kod'un istediğinden
    **düşük** test basıncı üretir (emniyetsiz yönde). Tabanı çağıran seçer;
    `design_code.calculate_hydrotest_pressure` MAWP yoksa geri düşer ve varsayımı
    açıkça kaydeder (K4).

    Args:
        pressure_basis: Test basıncı tabanı (MPa) — MAWP; yoksa tasarım basıncı.
        allowable_stress_test: Test sıcaklığındaki izin verilen gerilme (MPa).
        allowable_stress_design: Tasarım sıcaklığındaki izin verilen gerilme (MPa).
        temperature_ratio_factor: Sıcaklık oranı düzeltme faktörü.

    Returns:
        Hidrostatik test basıncı (MPa).

    Referans: UG-99(b)
    Doğrulandı (sayısal-bağımsız): PV Elite 2017 çıktısı — 1.3 × 218.80 psig MAWP
        × 1.0 = 284.44 psig. Bkz. docs/validation/asme-worked-examples.md V-07.
    """
    if allowable_stress_design <= 0:
        raise ValueError("Tasarım sıcaklığındaki izin verilen gerilme sıfırdan büyük olmalı")

    ratio = allowable_stress_test / allowable_stress_design
    p_test = 1.3 * pressure_basis * ratio

    return p_test


# ── MAWP hesaplama ────────────────────────────────────────────────────────────

def mawp_from_shell(
    R: float,
    t_actual: float,
    S: float,
    E: float,
    C: float = 0.0,
) -> float:
    """UG-27'den MAWP hesabı (silindirik gövde).

    P = S × E × t / (R + 0.6 × t)

    Burada:
    t = nominal kalınlık - korozyon payı (korozyonlu koşul)
    R = iç yarıçap (orijinal, korozyon payı eklenmemiş)

    Args:
        R: İç yarıçap (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        MAWP (MPa).

    Referans: UG-27(c)(1), rearranged
    """
    t = t_actual - C
    if t <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t:.2f} mm")

    mawp = S * E * t / (R + 0.6 * t)
    return mawp


def mawp_from_ellipsoidal_head(
    D: float,
    t_actual: float,
    S: float,
    E: float,
    C: float = 0.0,
) -> float:
    """UG-32(d)'den MAWP hesabı (2:1 elipsoidal bombe).

    P = 2 × S × E × t / (D + 0.2 × t)

    Args:
        D: İç çap (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        MAWP (MPa).

    Referans: UG-32(d), rearranged
    """
    t = t_actual - C
    if t <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t:.2f} mm")

    mawp = 2 * S * E * t / (D + 0.2 * t)
    return mawp


def mawp_from_hemispherical_head(
    R: float,
    t_actual: float,
    S: float,
    E: float,
    C: float = 0.0,
) -> float:
    """UG-32(f)'den MAWP hesabı (yarım küresel bombe).

    P = 2 × S × E × t / (R + 0.2 × t)

    Args:
        R: İç yarıçap (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        MAWP (MPa).

    Referans: UG-32(f), rearranged
    """
    t = t_actual - C
    if t <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t:.2f} mm")

    mawp = 2 * S * E * t / (R + 0.2 * t)
    return mawp


def mawp_from_torispherical_head(
    L: float,
    r: float,
    t_actual: float,
    S: float,
    E: float,
    C: float = 0.0,
) -> float:
    """UG-32(e)'den MAWP hesabı (torisferik bombe).

    M = (3 + sqrt(L/r)) / 4
    P = 2 × S × E × t / (L × M + 0.2 × t)

    Args:
        L: Taç yarıçapı (mm).
        r: Büküm yarıçapı (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.

    Returns:
        MAWP (MPa).
    """
    t = t_actual - C
    if t <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t:.2f} mm")

    M = (3.0 + math.sqrt(L / r)) / 4.0
    mawp = 2 * S * E * t / (L * M + 0.2 * t)
    return mawp


# ── UG-34: Düz kapak ─────────────────────────────────────────────────────────

def flat_head_thickness(
    P: float,
    d: float,
    S: float,
    E: float,
    C_attach: float,
    CA: float = 0.0,
) -> float:
    """UG-34(c)(2) — Düz kapak et kalınlığı.

    t = d × sqrt(C × P / (S × E)) + CA

    Burada:
    d = kapak çapı (korozyona uğramış, mm)
    C_attach = bağlantı katsayısı (Şekil UG-34, kullanıcı girer)
    P = tasarım basıncı (MPa)
    S = izin verilen gerilme (MPa)
    E = kaynak verimi
    CA = korozyon payı (mm)

    Args:
        P: Tasarım basıncı (MPa).
        d: Kapak çapı (korozyona uğramış) (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.
        C_attach: UG-34 bağlantı katsayısı.
        CA: Korozyon payı (mm).

    Returns:
        Gerekli kalınlık (mm).

    Referans: UG-34(c)(2), Şekil UG-34
    """
    if S <= 0:
        raise ValueError("S (izin verilen gerilme) sıfırdan büyük olmalı")
    if E <= 0:
        raise ValueError("E (kaynak verimi) sıfırdan büyük olmalı")
    if C_attach <= 0:
        raise ValueError("C_attach (bağlantı katsayısı) sıfırdan büyük olmalı")

    t = d * math.sqrt(C_attach * P / (S * E)) + CA
    return t


def flat_head_mawp(
    d: float,
    t_actual: float,
    S: float,
    E: float,
    C_attach: float,
    CA: float = 0.0,
) -> float:
    """UG-34(c)(2)'den MAWP hesabı (düz kapak).

    P = S × E × (t_corr / d)² / C_attach

    Burada:
    t_corr = nominal kalınlık - korozyon payı
    d = kapak çapı (mm)
    C_attach = bağlantı katsayısı

    Args:
        d: Kapak çapı (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.
        C_attach: UG-34 bağlantı katsayısı.
        CA: Korozyon payı (mm).

    Returns:
        MAWP (MPa).

    Referans: UG-34(c)(2), rearranged
    """
    t_corr = t_actual - CA
    if t_corr <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t_corr:.2f} mm")
    if d <= 0:
        raise ValueError("Kapak çapı sıfırdan büyük olmalı")
    if C_attach <= 0:
        raise ValueError("C_attach sıfırdan büyük olmalı")

    mawp = S * E * (t_corr / d) ** 2 / C_attach
    return mawp


# ── UG-100: Pnömatik test basıncı ────────────────────────────────────────────

def pneumatic_test_pressure(
    pressure_basis: float,
    allowable_stress_test: float,
    allowable_stress_design: float,
) -> float:
    """UG-100 — Pnömatik test basıncı.

    P_test = 1.1 × MAWP × (S_test / S_design)

    UG-99(b) ile aynı kural: taban **MAWP**'dir. Ayrıntı ve gerekçe için
    `hydrotest_pressure_asme` docstring'ine bakınız.

    Args:
        pressure_basis: Test basıncı tabanı (MPa) — MAWP; yoksa tasarım basıncı.
        allowable_stress_test: Test sıcaklığındaki izin verilen gerilme (MPa).
        allowable_stress_design: Tasarım sıcaklığındaki izin verilen gerilme (MPa).

    Returns:
        Pnömatik test basıncı (MPa).

    Referans: UG-100
    Doğrulandı (sayısal-bağımsız): PV Elite 2017 çıktısı — 1.1 × 218.80 psig MAWP
        × 1.0 = 240.68 psig. Bkz. docs/validation/asme-worked-examples.md V-07.
    """
    if allowable_stress_design <= 0:
        raise ValueError("Tasarım sıcaklığındaki izin verilen gerilme sıfırdan büyük olmalı")

    ratio = allowable_stress_test / allowable_stress_design
    p_test = 1.1 * pressure_basis * ratio

    return p_test


# ── UG-32(g): Konik bölüm ────────────────────────────────────────────────────

def cone_thickness(
    P: float,
    D: float,
    S: float,
    E: float,
    alpha_deg: float,
    C: float = 0.0,
) -> float:
    """UG-32(g) — Konik bölüm et kalınlığı.

    t = P × D / (2 × cos(α) × (S × E - 0.6 × P))

    Burada:
    D = büyük çap (mm)
    α = yarı tepe açısı (derece)
    P = tasarım basıncı (MPa)
    S = izin verilen gerilme (MPa)
    E = kaynak verimi

    Args:
        P: Tasarım basıncı (MPa).
        D: Büyük çap (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.
        alpha_deg: Yarı tepe açısı (derece).
        C: Korozyon payı (mm).

    Returns:
        Gerekli kalınlık (mm).

    Referans: UG-32(g)
    """
    if alpha_deg < 0 or alpha_deg > 80:
        raise ValueError(f"Yarı tepe açısı 0-80 derece aralığında olmalı: {alpha_deg}")

    alpha_rad = math.radians(alpha_deg)
    cos_alpha = math.cos(alpha_rad)

    if cos_alpha <= 0:
        raise ValueError("Yarı tepe açısı çok büyük (cos(α) ≤ 0)")

    denominator = 2 * cos_alpha * (S * E - 0.6 * P)
    if denominator <= 0:
        raise ValueError(
            f"UG-32(g): 2×cos(α)×(S×E - 0.6×P) = {denominator:.4f} ≤ 0. "
            "Basınç çok yüksek."
        )

    t = P * D / denominator
    return t


def cone_mawp(
    D: float,
    t_actual: float,
    S: float,
    E: float,
    alpha_deg: float,
    C: float = 0.0,
) -> float:
    """UG-32(g)'den MAWP hesabı (konik bölüm).

    P = 2 × cos(α) × S × E × t / (D + 2 × cos(α) × 0.6 × t)

    Args:
        D: Büyük çap (mm).
        t_actual: Nominal et kalınlığı (mm).
        S: İzin verilen gerilme (MPa).
        E: Kaynak verimi.
        alpha_deg: Yarı tepe açısı (derece).
        C: Korozyon payı (mm).

    Returns:
        MAWP (MPa).

    Referans: UG-32(g), rearranged
    """
    t = t_actual - C
    if t <= 0:
        raise ValueError(f"Korozyon payı düşüldükten sonra kalınlık negatif: t={t:.2f} mm")

    alpha_rad = math.radians(alpha_deg)
    cos_alpha = math.cos(alpha_rad)

    mawp = 2 * cos_alpha * S * E * t / (D + 2 * cos_alpha * 0.6 * t)
    return mawp


__all__ = [
    "shell_thickness_internal_pressure",
    "shell_required_nominal_thickness",
    "head_elliptical_thickness",
    "head_torispherical_thickness_full",
    "head_hemispherical_thickness",
    "hydrotest_pressure_asme",
    "pneumatic_test_pressure",
    "cone_thickness",
    "cone_mawp",
    "mawp_from_shell",
    "mawp_from_ellipsoidal_head",
    "mawp_from_hemispherical_head",
    "mawp_from_torispherical_head",
    "flat_head_thickness",
    "flat_head_mawp",
]
