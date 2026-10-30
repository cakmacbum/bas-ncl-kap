"""Kaldırma kulağı (lifting lug) kontrolleri — P06.

Kaynak yaklaşımı (formüller telifli metin gömmez; yalnız referans):
- Plaka çekme / kesme (tear-out) / yatak (pim): AISC 360 §D5 (pim bağlantılı elemanlar) ve
  Moss "Pressure Vessel Design Manual" lifting-lug prosedürü; ASD izinleri: çekme 0,6·Fy,
  kesme 0,4·Fy, yatak 0,9·Fy (AISC J7: 1,8·Fy·Apb / 2,0).
- Köşe kaynak: boğaz 0,707·ayak; AISC J2.4 ASD izin gerilmesi 0,6·FEXX/2,0 = 0,3·FEXX.
  Yatay bileşen momenti için taban kaynağı iki paralel çizgi kaynak (Zu = b²/3, Shigley).
- Gövde yerel (zımbalama/kesme-through) kontrolü KENDİ TUTUCU yaklaşımımızdır
  (WRC-107/537 değildir): Fv / (Lw · t_kabuk) <= 0,4·S. Yerel eğilme gerilmesi hesaplanmaz.
  BTH-1 tasarım kategorisi/Nd faktörleri uygulanmaz; darbe katsayısı kullanıcı tarafından seçilir.
Bu nedenle tüm kontroller `verified=False` işaretlidir (mühendis doğrulaması ister).

Birimler: N, mm, MPa.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

GRAVITY_M_S2 = 9.80665
DEFAULT_FEXX_MPA = 482.0  # E70 (varsayım sonuca yazılır)


@dataclass
class LugCheck:
    name: str
    stress_MPa: float
    allowable_MPa: float
    clause: str
    formula: str
    verified: bool = False
    intermediates: dict = field(default_factory=dict)

    @property
    def utilization(self) -> float:
        return self.stress_MPa / self.allowable_MPa


@dataclass
class LugResult:
    checks: List[LugCheck]
    load_per_lug_N: float
    vertical_per_lug_N: float
    horizontal_per_lug_N: float
    effective_lugs: int
    total_mass_kg: float
    assumptions: List[str]
    local_shell_bending_computed: bool = False


def effective_lug_count(lug_count: int) -> int:
    """3+ kulakta yük paylaşımı belirsiz (statik belirsiz); en fazla 2 kulak taşır varsayılır."""
    return min(lug_count, 2)


def evaluate_lifting_lug(
    spec,
    total_mass_kg: float,
    shell_thickness_mm: float,
    shell_allowable_MPa: float,
) -> LugResult:
    """Kulak başına yükü hesaplayıp tüm kontrolleri döndür.

    `spec`: domain.lifting_lug.LiftingLugSpec. Girdi doğrulaması model katmanında yapılır.
    """
    n_eff = effective_lug_count(spec.lug_count)
    W = (total_mass_kg + spec.extra_mass_kg) * GRAVITY_M_S2
    Pv = W * spec.impact_factor / n_eff
    th = math.radians(spec.lift_angle_deg)
    Ph = Pv * math.tan(th)
    F = Pv / math.cos(th)  # sapan (pim) kuvveti bileşkesi

    t = spec.plate_thickness_mm
    b = spec.plate_width_mm
    d = spec.hole_diameter_mm
    dp = spec.pin_diameter_mm or d
    e = spec.edge_distance_mm
    Fy = spec.yield_strength_MPa
    fexx = spec.weld_electrode_Fu_MPa or DEFAULT_FEXX_MPA

    assumptions = [
        f"Kulak başına yük: kap boş metal kütlesi + ek kütle, darbe katsayısı {spec.impact_factor:g}; "
        f"{spec.lug_count} kulaktan yalnız {n_eff} tanesi yük taşır (statik belirsizlik, tutucu).",
        "Sapan kulak düzleminde kabul edildi; düzlem dışı yük hesaba katılmadı.",
        "Kaldırma yeni/korozyonsuz durumda; nominal kalınlıklar kullanıldı.",
        "İzinler: çekme 0,6Fy, kesme 0,4Fy, yatak 0,9Fy, kaynak 0,3·FEXX (ASD).",
    ]
    if spec.pin_diameter_mm is None:
        assumptions.append("Pim çapı girilmedi; yatak kontrolünde delik çapı kullanıldı.")
    if spec.weld_electrode_Fu_MPa is None:
        assumptions.append(f"FEXX girilmedi; {DEFAULT_FEXX_MPA:g} MPa (E70) varsayıldı.")

    checks: List[LugCheck] = []

    # 1) Net kesit çekme (pim deliği hizası)
    A_net = (b - d) * t
    checks.append(LugCheck(
        "lug_tension", F / A_net, 0.6 * Fy,
        "AISC 360 §D5 / Moss PVDM lifting lug", "sigma_t = F / ((b - d_h)·t)",
        intermediates={"A_net_mm2": A_net, "F_N": F},
    ))
    # 2) Kesme (tear-out): iki düzlem, uzunluk = delik merkezi-kenar mesafesi e
    A_sh = 2.0 * e * t
    checks.append(LugCheck(
        "lug_shear", F / A_sh, 0.4 * Fy,
        "AISC 360 §D5 / Moss PVDM lifting lug", "tau = F / (2·e·t)",
        intermediates={"A_shear_mm2": A_sh},
    ))
    # 3) Yatak (pim)
    A_br = dp * t
    checks.append(LugCheck(
        "lug_bearing", F / A_br, 0.9 * Fy,
        "AISC 360 §J7 / Moss PVDM lifting lug", "sigma_br = F / (d_pin·t)",
        intermediates={"A_bearing_mm2": A_br},
    ))
    # 4) Taban köşe kaynağı: doğrudan kesme + yatay bileşen momenti
    throat = 0.707 * spec.weld_leg_mm
    Aw = throat * spec.weld_length_mm
    tau_v = Pv / Aw
    tau_h = Ph / Aw
    M = Ph * spec.hole_height_mm
    Sw = throat * spec.base_width_mm ** 2 / 3.0
    tau_b = M / Sw
    tau_w = math.sqrt((tau_v + tau_b) ** 2 + tau_h ** 2)
    checks.append(LugCheck(
        "lug_weld", tau_w, 0.3 * fexx,
        "AISC 360 §J2.4 / Shigley line-weld", "tau = sqrt((Pv/Aw + M/Sw)^2 + (Ph/Aw)^2)",
        intermediates={"throat_mm": throat, "Aw_mm2": Aw, "M_Nmm": M, "Sw_mm3": Sw},
    ))
    # 5) Gövde yerel kesme (tutucu, WRC değil)
    tau_s = Pv / (spec.weld_length_mm * shell_thickness_mm)
    checks.append(LugCheck(
        "lug_shell_local_shear", tau_s, 0.4 * shell_allowable_MPa,
        "Kendi tutucu yaklaşım (WRC-107/537 değil)", "tau = Pv / (Lw·t_shell)",
        intermediates={"t_shell_mm": shell_thickness_mm},
    ))

    return LugResult(
        checks=checks, load_per_lug_N=F, vertical_per_lug_N=Pv, horizontal_per_lug_N=Ph,
        effective_lugs=n_eff, total_mass_kg=total_mass_kg + spec.extra_mass_kg,
        assumptions=assumptions,
    )


__all__ = ["LugCheck", "LugResult", "evaluate_lifting_lug", "effective_lug_count", "GRAVITY_M_S2"]
