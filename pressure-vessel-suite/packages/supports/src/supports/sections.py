"""Ayak kesit özellikleri ve kolon kontrolü formülleri.

K1 kuralı: Formüller yalnızca bu pakette.
K6 kuralı: Profil kataloğu gömülmez — ölçüler kullanıcıdan serbest girilir.
Kesitler keskin köşeli dikdörtgen parçaların birleşimi olarak modellenir;
haddelenmiş profillerin köşe yuvarlatmaları ve eğimli flanşları yok sayılır
(katalog değerinden birkaç % sapma beklenir).

Referanslar:
- AISC, *Specification for Structural Steel Buildings — Allowable Stress
  Design* (1989), Chapter E (kolon burkulması) ve Chapter H (birleşik gerilme).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

# AISC ASD: basma elemanları için önerilen azami narinlik.
MAX_COMPRESSION_SLENDERNESS = 200.0


@dataclass(frozen=True)
class SectionProperties:
    """Kesit özellikleri. x ekseni güçlü eksen (profil yüksekliği boyunca eğilme)."""

    A: float      # mm²
    Ix: float     # mm⁴
    Iy: float     # mm⁴
    Sx: float     # mm³ (en küçük elastik kesit modülü)
    Sy: float     # mm³ (en küçük elastik kesit modülü)
    rx: float     # mm
    ry: float     # mm
    r_min: float  # mm — asal eksenlere göre en küçük atalet yarıçapı


def _positive(**dims: float) -> None:
    for name, value in dims.items():
        if value is None or value <= 0:
            raise ValueError(f"{name} pozitif olmalı: {value}")


def pipe_section(D_outside: float, t_wall: float) -> SectionProperties:
    """Boru (halka) kesit.

    A = π/4 (D² − Di²),  I = π/64 (D⁴ − Di⁴),  S = I/(D/2),  Di = D − 2t
    """
    _positive(D_outside=D_outside, t_wall=t_wall)
    D_inside = D_outside - 2.0 * t_wall
    if D_inside <= 0:
        raise ValueError(f"t_wall={t_wall} çok büyük: D_inside={D_inside} <= 0")
    A = math.pi / 4.0 * (D_outside**2 - D_inside**2)
    I = math.pi / 64.0 * (D_outside**4 - D_inside**4)
    S = I / (D_outside / 2.0)
    r = math.sqrt(I / A)
    return SectionProperties(A=A, Ix=I, Iy=I, Sx=S, Sy=S, rx=r, ry=r, r_min=r)


def channel_section(h: float, b: float, s: float, t: float) -> SectionProperties:
    """U profil (channel): yükseklik h, flanş genişliği b, gövde kalınlığı s,
    flanş kalınlığı t.

    Güçlü eksen (x, simetri ekseni):  Ix = [b·h³ − (b − s)(h − 2t)³] / 12
    Zayıf eksen (y): ağırlık merkezi gövde sırtından x̄ uzaklıkta; U kesit
    simetri eksenine sahip olduğu için x/y asal eksenlerdir.
    """
    _positive(h=h, b=b, s=s, t=t)
    if h <= 2.0 * t:
        raise ValueError(f"h={h} flanş kalınlıklarının toplamından (2t={2 * t}) büyük olmalı")
    if b <= s:
        raise ValueError(f"b={b} gövde kalınlığından (s={s}) büyük olmalı")

    h_web = h - 2.0 * t
    A_flanges = 2.0 * b * t
    A_web = h_web * s
    A = A_flanges + A_web

    Ix = (b * h**3 - (b - s) * h_web**3) / 12.0
    Sx = Ix / (h / 2.0)

    x_bar = (A_flanges * (b / 2.0) + A_web * (s / 2.0)) / A
    Iy_back = 2.0 * t * b**3 / 3.0 + h_web * s**3 / 3.0
    Iy = Iy_back - A * x_bar**2
    Sy = Iy / max(x_bar, b - x_bar)

    rx = math.sqrt(Ix / A)
    ry = math.sqrt(Iy / A)
    return SectionProperties(A=A, Ix=Ix, Iy=Iy, Sx=Sx, Sy=Sy, rx=rx, ry=ry, r_min=min(rx, ry))


def box_section(H: float, B: float, t: float) -> SectionProperties:
    """Dikdörtgen kutu profil: dış yükseklik H, dış genişlik B, et kalınlığı t."""
    _positive(H=H, B=B, t=t)
    if H <= 2.0 * t or B <= 2.0 * t:
        raise ValueError(f"t={t} çok büyük: iç boşluk kalmıyor (H={H}, B={B})")
    Hi, Bi = H - 2.0 * t, B - 2.0 * t
    A = B * H - Bi * Hi
    Ix = (B * H**3 - Bi * Hi**3) / 12.0
    Iy = (H * B**3 - Hi * Bi**3) / 12.0
    rx, ry = math.sqrt(Ix / A), math.sqrt(Iy / A)
    return SectionProperties(
        A=A, Ix=Ix, Iy=Iy, Sx=Ix / (H / 2.0), Sy=Iy / (B / 2.0),
        rx=rx, ry=ry, r_min=min(rx, ry),
    )


def angle_section(a: float, b: float, t: float) -> SectionProperties:
    """Köşebent (L): düşey kol a, yatay kol b, kalınlık t.

    Köşebentte x/y eksenleri asal değildir; burkulmayı belirleyen `r_min`
    asal eksen ataletinden hesaplanır:
        I_min = (Ix + Iy)/2 − √[((Ix − Iy)/2)² + Ixy²]
    """
    _positive(a=a, b=b, t=t)
    if a <= t or b <= t:
        raise ValueError(f"t={t} kol uzunluklarından (a={a}, b={b}) küçük olmalı")

    # Parça 1: düşey kol (0..t) × (0..a); parça 2: yatay kol (t..b) × (0..t)
    parts = [
        (t * a, t / 2.0, a / 2.0, t, a),
        ((b - t) * t, t + (b - t) / 2.0, t / 2.0, b - t, t),
    ]
    A = sum(p[0] for p in parts)
    x_bar = sum(p[0] * p[1] for p in parts) / A
    y_bar = sum(p[0] * p[2] for p in parts) / A

    Ix = Iy = Ixy = 0.0
    for area, cx, cy, width, height in parts:
        Ix += width * height**3 / 12.0 + area * (cy - y_bar) ** 2
        Iy += height * width**3 / 12.0 + area * (cx - x_bar) ** 2
        Ixy += area * (cx - x_bar) * (cy - y_bar)

    I_min = (Ix + Iy) / 2.0 - math.sqrt(((Ix - Iy) / 2.0) ** 2 + Ixy**2)
    Sx = Ix / max(y_bar, a - y_bar)
    Sy = Iy / max(x_bar, b - x_bar)
    return SectionProperties(
        A=A, Ix=Ix, Iy=Iy, Sx=Sx, Sy=Sy,
        rx=math.sqrt(Ix / A), ry=math.sqrt(Iy / A), r_min=math.sqrt(I_min / A),
    )


# ── Gerilmeler ────────────────────────────────────────────────────────────────

def leg_axial_stress(N: float, A: float) -> float:
    """fa = N / A (MPa)."""
    _positive(A=A)
    return N / A


def leg_bending_stress(N: float, eccentricity: float, S: float) -> float:
    """Eksantrik yükten eğilme: fb = N·e / S (MPa)."""
    _positive(S=S)
    if eccentricity < 0:
        raise ValueError(f"eccentricity negatif olamaz: {eccentricity}")
    return N * eccentricity / S


# ── Kolon burkulması (AISC ASD Chapter E) ─────────────────────────────────────

def column_slenderness(K: float, L: float, r: float) -> float:
    """Narinlik KL/r."""
    _positive(K=K, L=L, r=r)
    return K * L / r


def column_critical_slenderness(E: float, Fy: float) -> float:
    """Cc = √(2π²E / Fy) — elastik/inelastik burkulma sınırı."""
    _positive(E=E, Fy=Fy)
    return math.sqrt(2.0 * math.pi**2 * E / Fy)


def euler_stress_asd(E: float, slenderness: float) -> float:
    """Güvenlik katsayılı Euler gerilmesi F'e = 12π²E / [23 (KL/r)²]."""
    _positive(E=E, slenderness=slenderness)
    return 12.0 * math.pi**2 * E / (23.0 * slenderness**2)


def allowable_compressive_stress(slenderness: float, E: float, Fy: float) -> float:
    """İzin verilen eksenel basma gerilmesi Fa (AISC ASD E2-1 / E2-2).

    KL/r ≤ Cc:  Fa = [1 − (KL/r)²/(2Cc²)] Fy / FS,
                FS = 5/3 + 3/8·(KL/r)/Cc − (KL/r)³/(8Cc³)
    KL/r > Cc:  Fa = 12π²E / [23 (KL/r)²]

    Narinliğin `MAX_COMPRESSION_SLENDERNESS` sınırını aşıp aşmadığını çağıran
    taraf ayrıca kontrol eder; bu fonksiyon yalnız gerilmeyi verir.
    """
    if slenderness < 0:
        raise ValueError(f"slenderness negatif olamaz: {slenderness}")
    Cc = column_critical_slenderness(E, Fy)
    if slenderness <= Cc:
        ratio = slenderness / Cc
        FS = 5.0 / 3.0 + 3.0 / 8.0 * ratio - ratio**3 / 8.0
        return (1.0 - ratio**2 / 2.0) * Fy / FS
    return euler_stress_asd(E, slenderness)


def aisc_interaction_ratio(
    fa: float,
    Fa: float,
    fb: float,
    Fb: float,
    Fy: float,
    Fe_prime: Optional[float] = None,
    Cm: float = 0.85,
) -> float:
    """Eksenel basma + eğilme birleşik oranı (AISC ASD H1). ≤ 1,0 olmalı.

    fa/Fa ≤ 0,15:  fa/Fa + fb/Fb                                   (H1-3)
    fa/Fa > 0,15:  max( fa/Fa + Cm·fb / [(1 − fa/F'e)·Fb],          (H1-1)
                        fa/(0,6Fy) + fb/Fb )                        (H1-2)

    Cm = 0,85 yanal ötelenmesi serbest çerçeve üyesi varsayımıdır (ayak alt
    uçtan taban plakasına, üst uçtan kaba bağlı; yanal tutulu değil).
    fa ≥ F'e ise eleman kararsızdır → sonsuz oran döner.
    """
    _positive(Fa=Fa, Fb=Fb, Fy=Fy)
    if fa < 0 or fb < 0:
        raise ValueError("fa ve fb negatif olamaz (basma/eğilme büyüklükleri)")
    axial_ratio = fa / Fa
    if axial_ratio <= 0.15:
        return axial_ratio + fb / Fb
    if Fe_prime is None:
        raise ValueError("fa/Fa > 0,15 için Fe_prime (F'e) gerekli")
    _positive(Fe_prime=Fe_prime)
    if fa >= Fe_prime:
        return math.inf
    h1_1 = axial_ratio + Cm * fb / ((1.0 - fa / Fe_prime) * Fb)
    h1_2 = fa / (0.6 * Fy) + fb / Fb
    return max(h1_1, h1_2)


__all__ = [
    "MAX_COMPRESSION_SLENDERNESS",
    "SectionProperties",
    "pipe_section",
    "channel_section",
    "box_section",
    "angle_section",
    "leg_axial_stress",
    "leg_bending_stress",
    "column_slenderness",
    "column_critical_slenderness",
    "euler_stress_asd",
    "allowable_compressive_stress",
    "aisc_interaction_ratio",
]
