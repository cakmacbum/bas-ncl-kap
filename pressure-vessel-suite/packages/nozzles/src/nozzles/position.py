"""Nozul pozisyon yardımcısı — üç koordinat (z, θ, α) (kaynak §6).

K7 kuralı: Domain modelinden bağımsız; geometri hesapları burada.
K2 kuralı: CAD'e dokunulmaz; saf matematikle yapılır.

Nozul konumu üç koordinatla tanımlanır:
  - z: Eksenel mesafe (gövde başlangıcından itibaren, mm)
  - θ: Çevresel açı (derece, 0 = üst, 90 = yan)
  - α: Eğim açısı (derece, 0 = radyal/dik)

Referans: Kaynak §6 — Nozzle positioning
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from domain.enums import HeadType, NozzleType
from domain.geometry import Head, Nozzle, ShellSection


@dataclass
class NozzlePosition:
    """Nozul 3D pozisyon bilgisi."""

    tag: str

    # Silindirik koordinatlar (gövde referans)
    axial_z_mm: float = 0.0  # Eksenel konum
    circumferential_theta_deg: float = 0.0  # Çevresel açı
    inclination_alpha_deg: float = 0.0  # Eğim açısı

    # Kartezyen koordinatlar (hesaplanmış)
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0

    # Yüzey normali (radyal nozul için)
    normal_x: float = 0.0
    normal_y: float = 0.0
    normal_z: float = 0.0

    # Host bilgisi
    host_component_id: str = ""
    host_type: str = "shell"  # "shell" veya "head"

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "axial_z_mm": round(self.axial_z_mm, 2),
            "circumferential_theta_deg": round(self.circumferential_theta_deg, 2),
            "inclination_alpha_deg": round(self.inclination_alpha_deg, 2),
            "x_mm": round(self.x_mm, 2),
            "y_mm": round(self.y_mm, 2),
            "z_mm": round(self.z_mm, 2),
            "normal_x": round(self.normal_x, 4),
            "normal_y": round(self.normal_y, 4),
            "normal_z": round(self.normal_z, 4),
            "host_component_id": self.host_component_id,
            "host_type": self.host_type,
        }


def calculate_nozzle_position_on_shell(
    nozzle: Nozzle,
    shell: ShellSection,
) -> NozzlePosition:
    """Gövde üzerindeki nozul pozisyonunu hesapla.

    Gövde silindirik kabul edilir:
    - x = R × cos(θ)
    - y = R × sin(θ)
    - z = axial_position

    Yüzey normali (radyal nozul için):
    - n = (cos(θ), sin(θ), 0)

    Args:
        nozzle: Nozul tanımı.
        shell: Gövde tanımı.

    Returns:
        NozzlePosition.
    """
    R = shell.inside_diameter / 2.0 if shell.inside_diameter else (
        shell.outside_diameter / 2.0 - shell.nominal_thickness
    )

    theta_rad = math.radians(nozzle.circumferential_angle)
    alpha_rad = math.radians(nozzle.inclination_angle)

    # Kartezyen koordinatlar
    x = R * math.cos(theta_rad)
    y = R * math.sin(theta_rad)
    z = nozzle.axial_position

    # Yüzey normali (silindir üzerinde radyal yön)
    # Eğim açısı α=0 → tam radyal, α>0 → eğik
    nx = math.cos(theta_rad) * math.cos(alpha_rad)
    ny = math.sin(theta_rad) * math.cos(alpha_rad)
    nz = math.sin(alpha_rad)

    return NozzlePosition(
        tag=nozzle.tag,
        axial_z_mm=nozzle.axial_position,
        circumferential_theta_deg=nozzle.circumferential_angle,
        inclination_alpha_deg=nozzle.inclination_angle,
        x_mm=x,
        y_mm=y,
        z_mm=z,
        normal_x=nx,
        normal_y=ny,
        normal_z=nz,
        host_component_id=nozzle.host_component_id,
        host_type="shell",
    )


def calculate_nozzle_position_on_head(
    nozzle: Nozzle,
    head: Head,
) -> NozzlePosition:
    """Bombe üzerindeki nozul pozisyonunu hesapla.

    Bombe 2:1 elipsoid kabul edilir:
    - x = a × sin(φ) × cos(θ)
    - y = a × sin(φ) × sin(θ)
    - z = b × cos(φ)

    Burada a = R (yarıçap), b = R/2 (2:1 için), φ = merkez açısı.

    Konum iki şekilde verilebilir:
      - `head_position_diameter` (tercih edilen): bombe merkez ekseninden ölçülen
        yerleşim çapı d → r = d/2, φ = asin(r/a). İmalat çiziminden okunan ölçü.
      - `axial_position`: bombe tepesinden ölçülen mesafe (geriye dönük uyum).

    Args:
        nozzle: Nozul tanımı.
        head: Bombe tanımı.

    Returns:
        NozzlePosition.

    Raises:
        ValueError: Yerleşim çapı bombe çapını aşarsa (K4 — sessizce kırpılmaz).
    """
    R = head.inside_diameter / 2.0

    # Bombe tipine göre yarı eksenler
    if head.type == HeadType.ELLIPTICAL:
        a = R  # Yatay yarı eksen
        b = R / 2.0  # Dikey yarı eksen (2:1)
    elif head.type == HeadType.HEMISPHERICAL:
        a = R
        b = R
    elif head.type == HeadType.TORISPHERICAL:
        a = R
        b = R * 0.25  # Yaklaşık
    else:
        a = R
        b = R / 2.0

    # Merkez açısı φ
    d_pos = getattr(nozzle, "head_position_diameter", None)
    if d_pos:
        # Yerleşim çapından: r = d/2, r = a·sin(φ)
        r = d_pos / 2.0
        if r > a:
            raise ValueError(
                f"Nozul {nozzle.tag}: yerleşim çapı {d_pos:.1f} mm, bombe iç çapı "
                f"{head.inside_diameter:.1f} mm'yi aşıyor — nozul bombe yüzeyine "
                f"oturmaz."
            )
        phi = math.asin(max(-1.0, min(1.0, r / a))) if a > 0 else 0.0
    else:
        # axial_position bombe tepesinden mesafe: φ = acos(1 - z/b)
        head_height = b
        if head_height > 0 and nozzle.axial_position <= head_height:
            phi = math.acos(
                max(-1.0, min(1.0, 1.0 - nozzle.axial_position / head_height))
            )
        else:
            phi = 0.0

    theta_rad = math.radians(nozzle.circumferential_angle)
    alpha_rad = math.radians(nozzle.inclination_angle)

    # Kartezyen koordinatlar (bombe tepesi origin)
    x = a * math.sin(phi) * math.cos(theta_rad)
    y = a * math.sin(phi) * math.sin(theta_rad)
    z = b * math.cos(phi)

    # Yüzey normali (elipsoid normali)
    # n = (x/a², y/a², z/b²) normalize
    nx_raw = x / (a * a) if a > 0 else 0
    ny_raw = y / (a * a) if a > 0 else 0
    nz_raw = z / (b * b) if b > 0 else 0
    n_mag = math.sqrt(nx_raw**2 + ny_raw**2 + nz_raw**2)

    if n_mag > 0:
        nx = nx_raw / n_mag * math.cos(alpha_rad)
        ny = ny_raw / n_mag * math.cos(alpha_rad)
        nz = nz_raw / n_mag * math.cos(alpha_rad) + math.sin(alpha_rad)
    else:
        nx, ny, nz = 0, 0, 1

    return NozzlePosition(
        tag=nozzle.tag,
        axial_z_mm=nozzle.axial_position,
        circumferential_theta_deg=nozzle.circumferential_angle,
        inclination_alpha_deg=nozzle.inclination_angle,
        x_mm=x,
        y_mm=y,
        z_mm=z,
        normal_x=nx,
        normal_y=ny,
        normal_z=nz,
        host_component_id=nozzle.host_component_id,
        host_type="head",
    )


def calculate_nozzle_position(
    nozzle: Nozzle,
    shell: Optional[ShellSection] = None,
    head: Optional[Head] = None,
) -> NozzlePosition:
    """Nozul pozisyonunu hesapla (otomatik host algılama).

    Args:
        nozzle: Nozul tanımı.
        shell: Gövde tanımı (host gövde ise).
        head: Bombe tanımı (host bombe ise).

    Returns:
        NozzlePosition.

    Raises:
        ValueError: Host bileşen belirlenemezse.
    """
    if shell and nozzle.host_component_id == shell.section_id:
        return calculate_nozzle_position_on_shell(nozzle, shell)
    elif head and nozzle.host_component_id == head.head_id:
        return calculate_nozzle_position_on_head(nozzle, head)
    else:
        raise ValueError(
            f"Nozul {nozzle.tag} için host bileşen '{nozzle.host_component_id}' "
            f"verilen shell/head ile eşleşmiyor."
        )


__all__ = [
    "NozzlePosition",
    "calculate_nozzle_position",
    "calculate_nozzle_position_on_shell",
    "calculate_nozzle_position_on_head",
]
