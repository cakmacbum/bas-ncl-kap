"""Hacim ve ağırlık hesaplama — geometrik formüller (kaynak §2.B).

K2 kuralı: Bu hesap CAD'den bağımsızdır — yalnızca project data'dan çalışır.
CAD hacmi, doğrulama amaçlı ayrı karşılaştırılır (cad_engine.validation).

Hacim formülleri:
  - Silindirik gövde: V = π × r² × L
  - 2:1 Elipsoidal bombe: V = (2/3) × π × a² × b  (a = D/2, b = D/4)
  - Torisferik bombe: Yaklaşık formül
  - Yarım küresel bombe: V = (2/3) × π × r³
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from domain.enums import HeadType
from domain.geometry import Head, ShellSection
from domain.materials import MaterialProperty
from domain.project import VesselProject


@dataclass
class VolumeResult:
    """Hacim hesaplama sonucu."""

    component_id: str
    component_type: str  # "shell", "head"
    inner_volume_mm3: float  # İç hacim (akışkan hacmi, korozyon payı düşülmüş)
    metal_volume_mm3: float  # Metal hacmi
    outer_volume_mm3: float  # Dış hacim (metal + iç hacim)

    @property
    def inner_volume_liters(self) -> float:
        return self.inner_volume_mm3 / 1e6

    @property
    def inner_volume_m3(self) -> float:
        return self.inner_volume_mm3 / 1e9

    @property
    def metal_volume_m3(self) -> float:
        return self.metal_volume_mm3 / 1e9


@dataclass
class MassResult:
    """Ağırlık hesaplama sonucu."""

    component_id: str
    component_type: str
    metal_mass_kg: float
    density_kg_m3: float
    metal_volume_mm3: float


@dataclass
class VesselVolumeMassReport:
    """Kap hacim ve ağırlık raporu."""

    volume_results: List[VolumeResult]
    mass_results: List[MassResult]

    @property
    def total_inner_volume_mm3(self) -> float:
        """Toplam iç hacim (mm³)."""
        return sum(v.inner_volume_mm3 for v in self.volume_results)

    @property
    def total_inner_volume_liters(self) -> float:
        """Toplam iç hacim (litre)."""
        return self.total_inner_volume_mm3 / 1e6

    @property
    def total_inner_volume_m3(self) -> float:
        """Toplam iç hacim (m³)."""
        return self.total_inner_volume_mm3 / 1e9

    @property
    def total_metal_volume_mm3(self) -> float:
        """Toplam metal hacmi (mm³)."""
        return sum(v.metal_volume_mm3 for v in self.volume_results)

    @property
    def total_metal_mass_kg(self) -> float:
        """Toplam metal ağırlığı (kg)."""
        return sum(m.metal_mass_kg for m in self.mass_results)

    def to_dict(self) -> dict:
        return {
            "total_inner_volume_mm3": self.total_inner_volume_mm3,
            "total_inner_volume_liters": self.total_inner_volume_liters,
            "total_inner_volume_m3": self.total_inner_volume_m3,
            "total_metal_volume_mm3": self.total_metal_volume_mm3,
            "total_metal_mass_kg": self.total_metal_mass_kg,
            "components": [
                {
                    "id": v.component_id,
                    "type": v.component_type,
                    "inner_volume_mm3": v.inner_volume_mm3,
                    "metal_volume_mm3": v.metal_volume_mm3,
                }
                for v in self.volume_results
            ],
        }


def shell_volume(shell: ShellSection) -> VolumeResult:
    """Silindirik gövde hacim hesabı.

    İç hacim: π × r_corroded² × L
    Metal hacmi: π × (r_outer² - r_inner²) × L

    Args:
        shell: Gövde kesit tanımı.

    Returns:
        VolumeResult.
    """
    t = shell.nominal_thickness or 0.0
    if shell.inside_diameter:
        r_inner = shell.inside_diameter / 2.0
        r_outer = r_inner + t
    elif shell.outside_diameter:
        r_outer = shell.outside_diameter / 2.0
        r_inner = r_outer - t
    else:
        r_inner = r_outer = 0.0

    L = shell.tangent_length or 0.0
    ca = shell.internal_corrosion_allowance or 0.0
    r_corroded = max(r_inner - ca, 0.0)

    # İç hacim (korozyon paylı)
    inner_vol = math.pi * r_corroded**2 * L

    # Dış hacim
    outer_vol = math.pi * r_outer**2 * L

    # Metal hacmi
    metal_vol = outer_vol - inner_vol

    return VolumeResult(
        component_id=shell.section_id,
        component_type="shell",
        inner_volume_mm3=inner_vol,
        metal_volume_mm3=metal_vol,
        outer_volume_mm3=outer_vol,
    )


def head_volume(head: Head) -> VolumeResult:
    """Bombe hacim hesabı.

    2:1 Elipsoidal: V_inner = (2/3) × π × a² × b  (a = D/2, b = D/4)
    Yarım küresel: V_inner = (2/3) × π × r³
    Torisferik: Yaklaşık (dönüş simetrisi integrali)

    Args:
        head: Bombe tanımı.

    Returns:
        VolumeResult.
    """
    D = head.inside_diameter or 0.0
    R = D / 2.0
    t = head.nominal_thickness or 0.0
    ca = head.internal_corrosion_allowance or 0.0
    r_corroded = max(R - ca, 0.0)

    if head.type == HeadType.ELLIPTICAL:
        # 2:1 elipsoidal: a = r, b = r/2
        # İç hacim
        a_in = r_corroded
        b_in = r_corroded / 2.0
        inner_vol = (2.0 / 3.0) * math.pi * a_in**2 * b_in

        # Dış hacim
        a_out = R + t
        b_out = (R + t) / 2.0
        outer_vol = (2.0 / 3.0) * math.pi * a_out**2 * b_out

    elif head.type == HeadType.HEMISPHERICAL:
        # Yarım küre: V = (2/3) × π × r³
        inner_vol = (2.0 / 3.0) * math.pi * r_corroded**3
        outer_vol = (2.0 / 3.0) * math.pi * (R + t) ** 3

    elif head.type == HeadType.TORISPHERICAL:
        # Torisferik: yaklaşık hesap
        # Taç bölgesi + knuckle bölgesi
        L = head.crown_radius if head.crown_radius else D
        r = head.knuckle_radius if head.knuckle_radius else D / 10.0

        # Yaklaşık: elipsoid gibi düşün
        # Daha hassas hesap için Pappus teoremi kullanılabilir
        inner_vol = (2.0 / 3.0) * math.pi * r_corroded**2 * (r_corroded / 2.0)
        outer_vol = (2.0 / 3.0) * math.pi * (R + t) ** 2 * ((R + t) / 2.0)

    else:
        # Flat veya bilinmeyen → sıfır
        return VolumeResult(
            component_id=head.head_id,
            component_type="head",
            inner_volume_mm3=0.0,
            metal_volume_mm3=0.0,
            outer_volume_mm3=0.0,
        )

    # Düz flanş ekle
    sf = head.straight_flange_length
    if sf > 0:
        sf_inner = math.pi * r_corroded**2 * sf
        sf_outer = math.pi * (R + t) ** 2 * sf
        inner_vol += sf_inner
        outer_vol += sf_outer

    metal_vol = outer_vol - inner_vol

    return VolumeResult(
        component_id=head.head_id,
        component_type="head",
        inner_volume_mm3=inner_vol,
        metal_volume_mm3=metal_vol,
        outer_volume_mm3=outer_vol,
    )


def calculate_mass(volume_mm3: float, density_kg_m3: float) -> float:
    """Metal ağırlığı hesabı.

    Args:
        volume_mm3: Metal hacmi (mm³).
        density_kg_m3: Yoğunluk (kg/m³).

    Returns:
        Ağırlık (kg).
    """
    volume_m3 = volume_mm3 / 1e9
    return volume_m3 * density_kg_m3


def calculate_vessel_volume_mass(project: VesselProject) -> VesselVolumeMassReport:
    """Kap için toplam hacim ve ağırlık hesapla.

    Args:
        project: VesselProject.

    Returns:
        VesselVolumeMassReport.
    """
    volume_results: List[VolumeResult] = []
    mass_results: List[MassResult] = []

    # Gövde(ler)
    for shell in project.shell_sections:
        vr = shell_volume(shell)
        volume_results.append(vr)

        mat = project.get_material(shell.material_id)
        density = mat.density if mat else 7850.0
        mass = calculate_mass(vr.metal_volume_mm3, density)
        mass_results.append(MassResult(
            component_id=shell.section_id,
            component_type="shell",
            metal_mass_kg=mass,
            density_kg_m3=density,
            metal_volume_mm3=vr.metal_volume_mm3,
        ))

    # Bombeler
    for head in project.heads:
        vr = head_volume(head)
        volume_results.append(vr)

        mat = project.get_material(head.material_id)
        density = mat.density if mat else 7850.0
        mass = calculate_mass(vr.metal_volume_mm3, density)
        mass_results.append(MassResult(
            component_id=head.head_id,
            component_type="head",
            metal_mass_kg=mass,
            density_kg_m3=density,
            metal_volume_mm3=vr.metal_volume_mm3,
        ))

    return VesselVolumeMassReport(
        volume_results=volume_results,
        mass_results=mass_results,
    )


__all__ = [
    "VolumeResult",
    "MassResult",
    "VesselVolumeMassReport",
    "shell_volume",
    "head_volume",
    "calculate_mass",
    "calculate_vessel_volume_mass",
]
