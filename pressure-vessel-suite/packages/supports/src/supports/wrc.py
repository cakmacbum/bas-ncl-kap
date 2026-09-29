"""WRC 107 / WRC 537 — silindirik kabukta lokal ped/ayak yükünden gerilme.

K6 kuralı: WRC 107/537 bültenlerinin boyutsuz eğrileri (β, γ'ye bağlı Kn/Kb
katsayıları) teliflidir ve repoya **gömülmez**. Bu modül yalnız:

1. Geometri parametrelerini (γ, β1, β2) hesaplar,
2. Kullanıcının lisanslı bültenden okuduğu katsayılardan gerilme bileşke
   değerlerini (Nx, Ny, Mx, My) üretir (bindirme/toplama matematiği),
3. 8 noktada (A/B/C/D × iç/dış yüzey) membran+eğilme gerilmesini basınç
   gerilmesiyle birleştirir,
4. ASME VIII-2 Bölüm 5 stil sınıflandırmayla (PL ≤ 1.5S, PL+Pb ≤ 1.5S) kıyaslar.

Katsayı okuma ve eğri-uydurma adımı kullanıcının/mühendisin işidir — bu K6'nın
UG-28 A/B faktörü ile aynı desenidir (bkz. `design_code.py` dış basınç kontrolü).

## Normalizasyon kuralı

Kuvvet tipi yükler (radyal `P`, kesmeler `VL`/`VC`) için bültenler eğriyi
`N·Rm/Load` ve `M/Load` biçiminde sunar (N: kuvvet/uzunluk boyutlu bileşke,
M: kuvvet boyutlu bileşke moment/uzunluk):

    N_katkı = K_N · Load / Rm         M_katkı = K_M · Load

Kayma yükleri (boyuna `VL`, çevresel `VC`) de KUVVET tipidir: bülten eğrisi
`N·Rm/V` ve `M/V` verir → N_katkı = K_N·V/Rm, M_katkı = K_M·V.

Moment tipi yükler (`ML`, `MC`) için bülten `N·Rm²/Moment` ve `M·Rm/Moment`
sunar:

    N_katkı = K_N · Moment / Rm²      M_katkı = K_M · Moment / Rm

Bu, WRC 107/537'nin standart pratikte kullanılan (kuvvet→N∝1/Rm, M∝1;
moment→N∝1/Rm², M∝1/Rm) boyut analizidir; kullanıcı boyutsuz `K` değerini
kendi bültenden okur, kod yalnız ölçekleme ve toplamı yapar.

Referanslar:
- WRC Bulletin 107 (1979 revizyonu), WRC Bulletin 537 (2010) — yöntem adı ve
  D/T=7–2500, d/D=0–0.7, t/T=0.1–10 kapsam aralığı (madde referansı olarak).
- ASME BPVC VIII-2, Part 5 — gerilme sınıflandırması PL ≤ 1.5S, PL+Pb ≤ 1.5S.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

# WRC 107/537 kapsam sınırı: kabuk çap/kalınlık oranı.
D_T_MIN, D_T_MAX = 7.0, 2500.0

POINTS = ("A", "B", "C", "D")
SURFACES = ("outside", "inside")

# Her nokta için (Nx katsayı alanı, Ny katsayı alanı) — hangi katsayının
# hangi bileşke için gerekli olduğunu belirtir; kullanıcı yalnız gerçekten
# ihtiyaç duyulanları girer.
_COMPONENTS = ("Nx", "Ny", "Mx", "My")
_LOADS = ("P", "ML", "MC", "VL", "VC")


def gamma(Rm: float, T: float) -> float:
    """γ = Rm / T — kabuk inceliği parametresi."""
    if Rm <= 0 or T <= 0:
        raise ValueError(f"Rm ve T pozitif olmalı: {Rm}, {T}")
    return Rm / T


def beta(C: float, Rm: float) -> float:
    """β = C / Rm — ped/ayak yarı-boyutunun kabuk yarıçapına oranı."""
    if C <= 0 or Rm <= 0:
        raise ValueError(f"C ve Rm pozitif olmalı: {C}, {Rm}")
    return C / Rm


def applicability_gate(D: float, T: float) -> Tuple[bool, str]:
    """WRC 107/537 kapsam kontrolü: D/T ∈ [7, 2500].

    Returns:
        (kapsam_içinde, mesaj)
    """
    if D <= 0 or T <= 0:
        raise ValueError(f"D ve T pozitif olmalı: {D}, {T}")
    ratio = D / T
    if D_T_MIN <= ratio <= D_T_MAX:
        return True, f"D/T={ratio:.1f} WRC 107/537 kapsamında [{D_T_MIN:g}, {D_T_MAX:g}]"
    return False, (
        f"D/T={ratio:.1f} WRC 107/537 kapsamı [{D_T_MIN:g}, {D_T_MAX:g}] dışında — "
        "extrapolasyon yapılmaz."
    )


@dataclass(frozen=True)
class WrcPointCoefficients:
    """Bir nokta (A/B/C/D) için, bir yük (P/ML/MC) altında dört boyutsuz
    katsayı: eksenel membran/eğilme (Nx, Mx), çevresel membran/eğilme (Ny, My).

    Aktif (sıfır olmayan) bir yük için dört bileşenin **hepsi** girilmelidir.
    Bültende değeri gerçekten sıfır olan bileşen açıkça `0.0` girilir; `None`
    "okunmadı" demektir ve hesap bloklanır — sessizce sıfır sayılmaz (K4/K6).
    """

    Nx: Optional[float] = None
    Ny: Optional[float] = None
    Mx: Optional[float] = None
    My: Optional[float] = None


@dataclass(frozen=True)
class WrcCoefficients:
    """Tüm noktalar × tüm yükler için kullanıcı tarafından girilen katsayı
    tablosu. Yapı: `table[point][load] = WrcPointCoefficients`.

    Katsayılar yalnız aktif (sıfır olmayan) yükler için gerekir; o yükün
    kullanılan her noktasında dört bileşen (Nx, Ny, Mx, My) tam girilmelidir.
    Eksikleri `missing_for` listeler; hesap eksik katsayıyla çalışmaz.
    """

    table: Dict[str, Dict[str, WrcPointCoefficients]] = field(default_factory=dict)

    def get(self, point: str, load: str) -> WrcPointCoefficients:
        return self.table.get(point, {}).get(load, WrcPointCoefficients())

    def missing_for(self, point: str, load: str, active_loads: Dict[str, float]) -> list:
        """Aktif (sıfır olmayan) `load` için bu noktada girilmemiş bileşenleri döner.

        Örn. `["A/P: Ny, My"]`. Yük sıfırsa katsayı gerekmez. Eksik bileşen
        sıfır sayılmaz — çağıran taraf `BLOCKED_CODE_DATA` verir.
        """
        if active_loads.get(load, 0.0) == 0.0:
            return []
        coeffs = self.get(point, load)
        names = [c for c in _COMPONENTS if getattr(coeffs, c) is None]
        return [f"{point}/{load}: {', '.join(names)}"] if names else []


@dataclass(frozen=True)
class PointStressResult:
    point: str
    surface: str
    membrane_axial: float
    membrane_circ: float
    bending_axial: float
    bending_circ: float
    shear: float
    total_axial: float
    total_circ: float
    stress_intensity: float


def _force_contribution(K: Optional[float], load: float, Rm: float, is_membrane: bool) -> float:
    if K is None or load == 0.0:
        return 0.0
    return K * load / Rm if is_membrane else K * load


def _moment_contribution(K: Optional[float], load: float, Rm: float, is_membrane: bool) -> float:
    if K is None or load == 0.0:
        return 0.0
    return K * load / (Rm * Rm) if is_membrane else K * load / Rm


def point_stress_resultants(
    point: str,
    coeffs: WrcCoefficients,
    Rm: float,
    P: float = 0.0,
    ML: float = 0.0,
    MC: float = 0.0,
    VL: float = 0.0,
    VC: float = 0.0,
) -> Tuple[float, float, float, float]:
    """Bir noktadaki toplam Nx, Ny, Mx, My bileşke değerleri (bindirme).

    P, VL, VC kuvvet tipi (N∝1/Rm, M∝1); ML/MC moment tipi (N∝1/Rm², M∝1/Rm).
    """
    if point not in POINTS:
        raise ValueError(f"Geçersiz nokta: {point}")
    Nx = Ny = Mx = My = 0.0
    for load_name, load_value, contrib_n, contrib_m in (
        ("P", P, _force_contribution, _force_contribution),
        ("ML", ML, _moment_contribution, _moment_contribution),
        ("MC", MC, _moment_contribution, _moment_contribution),
        ("VL", VL, _force_contribution, _force_contribution),
        ("VC", VC, _force_contribution, _force_contribution),
    ):
        c = coeffs.get(point, load_name)
        if load_value != 0.0:
            gaps = coeffs.missing_for(point, load_name, {load_name: load_value})
            if gaps:
                raise ValueError(
                    f"WRC katsayısı eksik — {gaps[0]}. Bültende gerçekten sıfırsa 0.0 girin; "
                    "eksik katsayı sıfır sayılmaz."
                )
        Nx += contrib_n(c.Nx, load_value, Rm, True)
        Ny += contrib_n(c.Ny, load_value, Rm, True)
        Mx += contrib_m(c.Mx, load_value, Rm, False)
        My += contrib_m(c.My, load_value, Rm, False)
    return Nx, Ny, Mx, My


def evaluate_point(
    point: str,
    surface: str,
    coeffs: WrcCoefficients,
    Rm: float,
    T_eff: float,
    P: float = 0.0,
    ML: float = 0.0,
    MC: float = 0.0,
    shear_stress: float = 0.0,
    pressure_axial_stress: float = 0.0,
    pressure_circ_stress: float = 0.0,
    VL: float = 0.0,
    VC: float = 0.0,
) -> PointStressResult:
    """Tek bir nokta/yüzey için lokal + basınç gerilmesini birleştirir.

    Eğilme işareti: dış yüzeyde membran + eğilme, iç yüzeyde membran − eğilme
    (dışbükey tarafta çekme veren pozitif moment kabulü — WRC 107 worksheet
    kuralıyla tutarlı; ped/ayak yük yönü tersse kullanıcı işaretleri ters
    girer).

    Basınç gerilmesi (`pressure_axial_stress`, `pressure_circ_stress`) genel
    primer membran gerilmesidir — lokal PL ile toplanarak sınıflandırılır; bu
    "basıncın buna göre tespit edilmesi" adımıdır.
    """
    if surface not in SURFACES:
        raise ValueError(f"Geçersiz yüzey: {surface}")
    if T_eff <= 0:
        raise ValueError(f"T_eff pozitif olmalı: {T_eff}")

    Nx, Ny, Mx, My = point_stress_resultants(point, coeffs, Rm, P, ML, MC, VL, VC)
    sign = 1.0 if surface == "outside" else -1.0

    sigma_m_x = Nx / T_eff
    sigma_m_y = Ny / T_eff
    sigma_b_x = sign * 6.0 * Mx / T_eff**2
    sigma_b_y = sign * 6.0 * My / T_eff**2

    total_x = sigma_m_x + sigma_b_x + pressure_axial_stress
    total_y = sigma_m_y + sigma_b_y + pressure_circ_stress

    # Düzlem gerilme von Mises eşdeğeri (Tresca yerine; ASME VIII-2 Bölüm 5
    # uygulamasında yaygın basitleştirme — açıkça belgelenir).
    si = math.sqrt(total_x**2 - total_x * total_y + total_y**2 + 3.0 * shear_stress**2)

    return PointStressResult(
        point=point, surface=surface,
        membrane_axial=sigma_m_x, membrane_circ=sigma_m_y,
        bending_axial=sigma_b_x, bending_circ=sigma_b_y,
        shear=shear_stress,
        total_axial=total_x, total_circ=total_y,
        stress_intensity=si,
    )


def evaluate_all_points(
    coeffs: WrcCoefficients,
    Rm: float,
    T_eff: float,
    P: float = 0.0,
    ML: float = 0.0,
    MC: float = 0.0,
    shear_stress: float = 0.0,
    pressure_axial_stress: float = 0.0,
    pressure_circ_stress: float = 0.0,
    VL: float = 0.0,
    VC: float = 0.0,
) -> Dict[Tuple[str, str], PointStressResult]:
    """8 nokta (A/B/C/D × dış/iç) için `evaluate_point`'i toplu çalıştırır."""
    results = {}
    for point in POINTS:
        for surface in SURFACES:
            results[(point, surface)] = evaluate_point(
                point, surface, coeffs, Rm, T_eff, P, ML, MC,
                shear_stress, pressure_axial_stress, pressure_circ_stress, VL, VC,
            )
    return results


def missing_coefficients(
    coeffs: WrcCoefficients,
    active_loads: Dict[str, float],
    points: Tuple[str, ...] = POINTS,
) -> list:
    """Aktif (sıfır olmayan) her yük × her nokta için girilmemiş katsayıları listeler.

    Örn. `["A/VL: Ny, My", "B/VL: Nx, Ny, Mx, My"]`. Eksik bileşen sıfır sayılmaz.
    """
    missing = []
    for point in points:
        for load in _LOADS:
            missing.extend(coeffs.missing_for(point, load, active_loads))
    return missing


def _entry_value(entry, name: str) -> Optional[float]:
    if entry is None:
        return None
    if isinstance(entry, dict):
        return entry.get(name)
    return getattr(entry, name, None)


def coefficients_from_mapping(mapping) -> WrcCoefficients:
    """Kullanıcı girdisi `{nokta: {yük: {Nx,Ny,Mx,My}}}` (dict veya Pydantic
    `WrcCoefficientEntry`) yapısını `WrcCoefficients`'e çevirir. None/boş → boş tablo."""
    table: Dict[str, Dict[str, WrcPointCoefficients]] = {}
    for point, loads in (mapping or {}).items():
        for load, entry in (loads or {}).items():
            table.setdefault(point, {})[load] = WrcPointCoefficients(
                Nx=_entry_value(entry, "Nx"), Ny=_entry_value(entry, "Ny"),
                Mx=_entry_value(entry, "Mx"), My=_entry_value(entry, "My"),
            )
    return WrcCoefficients(table=table)


def pressure_membrane_stresses(P_design: float, Rm: float, T: float) -> Tuple[float, float]:
    """İnce cidar silindir basınç membran gerilmeleri (MPa).

        σ_çevresel = P·Rm/T,   σ_boyuna = P·Rm/(2T)

    Rm ortalama yarıçap, T korozyonlu kalınlık. Lokal gerilmeyle birleştirilen
    genel primer membrandır ("basıncın buna göre tespit edilmesi").
    """
    if Rm <= 0 or T <= 0:
        raise ValueError(f"Rm ve T pozitif olmalı: {Rm}, {T}")
    if P_design < 0:
        raise ValueError(f"P_design negatif olamaz: {P_design}")
    return P_design * Rm / (2.0 * T), P_design * Rm / T


@dataclass(frozen=True)
class WrcClassification:
    point: str
    surface: str
    PL: float          # lokal primer membran gerilme şiddeti (basınç dahil)
    PL_plus_Pb: float   # + eğilme
    allowable_PL: float
    allowable_PL_Pb: float
    pl_ok: bool
    pl_pb_ok: bool


def classify_point(result: PointStressResult, S: float) -> WrcClassification:
    """PL ≤ 1.5S, PL+Pb ≤ 1.5S sınıflandırması (ASME VIII-2 Part 5 stili).

    PL burada yalnız membran (basınç + lokal) bileşke şiddeti; PL+Pb eğilme
    dahil toplam şiddettir — `stress_intensity` zaten eğilmeyi içerdiğinden
    PL için ayrı, membran-only bir von Mises değeri hesaplanır.
    """
    if S <= 0:
        raise ValueError(f"S (izin verilen gerilme) pozitif olmalı: {S}")
    # PL: yalnız membran + basınç (eğilme hariç)
    m_axial = result.total_axial - result.bending_axial
    m_circ = result.total_circ - result.bending_circ
    PL = math.sqrt(m_axial**2 - m_axial * m_circ + m_circ**2 + 3.0 * result.shear**2)
    PL_Pb = result.stress_intensity
    allowable_PL = 1.5 * S
    allowable_PL_Pb = 1.5 * S
    return WrcClassification(
        point=result.point, surface=result.surface,
        PL=PL, PL_plus_Pb=PL_Pb,
        allowable_PL=allowable_PL, allowable_PL_Pb=allowable_PL_Pb,
        pl_ok=PL <= allowable_PL, pl_pb_ok=PL_Pb <= allowable_PL_Pb,
    )


__all__ = [
    "D_T_MIN",
    "D_T_MAX",
    "POINTS",
    "SURFACES",
    "gamma",
    "beta",
    "applicability_gate",
    "WrcPointCoefficients",
    "WrcCoefficients",
    "PointStressResult",
    "point_stress_resultants",
    "missing_coefficients",
    "coefficients_from_mapping",
    "pressure_membrane_stresses",
    "evaluate_point",
    "evaluate_all_points",
    "WrcClassification",
    "classify_point",
]
