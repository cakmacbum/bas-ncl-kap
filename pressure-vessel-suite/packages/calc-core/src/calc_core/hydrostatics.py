"""Statik kafa hesabı — hidrostatik basınç düzeltmesi (kaynak §19).

K1 kuralı: Formül burada yazılır; orchestrator yalnızca çağırır.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple


def static_head_pressure(
    fluid_density_kg_m3: float,
    height_mm: float,
    gravity_m_s2: float = 9.80665,
) -> float:
    """Statik sıvı basıncı hesabı.

    ΔP = ρ × g × h

    Args:
        fluid_density_kg_m3: Sıvı yoğunluğu (kg/m³).
        height_mm: Sıvı yüksekliği (mm).
        gravity_m_s2: Yerçekimi ivmesi (m/s²). Varsayılan: 9.80665.

    Returns:
        Statik basınç (MPa).

    Referans: Hidrostatik temel formül
    """
    if fluid_density_kg_m3 < 0:
        raise ValueError("Sıvı yoğunluğu negatif olamaz")
    if height_mm < 0:
        raise ValueError("Yükseklik negatif olamaz")

    # mm → m dönüşümü
    height_m = height_mm / 1000.0

    # Pa → MPa dönüşümü
    pressure_pa = fluid_density_kg_m3 * gravity_m_s2 * height_m
    pressure_mpa = pressure_pa / 1e6

    return pressure_mpa


def _head_depth_mm(head: Any) -> Optional[float]:
    """Bombe derinliği (teğet çizgisinden uca, düz flanş hariç); hesaplanamazsa None."""
    d = head.inside_diameter
    kind = getattr(head.type, "value", head.type)
    if kind == "flat":
        return 0.0
    if kind == "hemispherical":
        return d / 2.0
    if getattr(head, "crown_depth", None):
        return float(head.crown_depth)
    if kind == "elliptical":
        return d / 4.0
    if kind != "torispherical":
        return None
    rc, rk = head.crown_radius, head.knuckle_radius
    if getattr(head, "torispherical_geometry", "") == "standard_asme_fd":
        rc, rk = d, 0.06 * d
    if not rc or not rk:
        return None
    inner = (rc - rk) ** 2 - (d / 2.0 - rk) ** 2
    if inner < 0:
        return None
    return rc - math.sqrt(inner)


def component_bottom_elevations(project: Any) -> Dict[Tuple[str, str], float]:
    """Bileşen en alt noktasının kap datumundan (kabın en alt noktası) yüksekliği (mm).

    Yalnız güvenilir hesaplanabilenler döner; diğerleri sözlükte YOKTUR (kot uydurulmaz):
    - YATAY kap: gövde ve bombeler datumda (0). Koni (eksen kayması bilinmez) hariç.
    - DİKEY kap: component_sequence (alttan üste) ile kümülatif; sıra yoksa/çözülemezse boş.
    """
    out: Dict[Tuple[str, str], float] = {}
    orient = getattr(project.orientation, "value", project.orientation)
    if orient == "horizontal":
        for s in project.shell_sections:
            out[("shell", s.section_id)] = 0.0
        for h in project.heads:
            out[("head", h.head_id)] = 0.0
        return out
    if orient != "vertical" or not project.component_sequence:
        return out
    shells = {x.section_id: x for x in project.shell_sections}
    heads = {x.head_id: x for x in project.heads}
    cones = {x.cone_id: x for x in project.cones}
    seq = project.component_sequence
    z = 0.0
    result: Dict[Tuple[str, str], float] = {}
    for i, ref in enumerate(seq):
        key = (ref.component_type, ref.component_id)
        if ref.component_type == "shell":
            length = shells[ref.component_id].tangent_length
            result[key] = z
        elif ref.component_type == "cone":
            length = cones[ref.component_id].length
            result[key] = z
        else:
            head = heads[ref.component_id]
            depth = _head_depth_mm(head)
            if depth is None:
                return {}
            length = depth + head.straight_flange_length
            result[key] = z  # alt bombe: ucu datum; üst bombe: düz flanş başlangıcı
        z += length
    return result


__all__ = ["static_head_pressure", "component_bottom_elevations"]
