"""Independent elementary geometry for cylindrical-shell nozzle placement."""
from __future__ import annotations
import math


def shell_location(radius_mm: float, axial_mm: float, angle_deg: float) -> dict:
    """Angle is measured from +X; return shell surface coordinates in mm."""
    theta = math.radians(angle_deg % 360)
    return {"x_mm": radius_mm * math.cos(theta), "y_mm": radius_mm * math.sin(theta), "z_mm": axial_mm}


def ellipse_head_location(radius_mm: float, depth_mm: float, diameter_mm: float, angle_deg: float) -> dict:
    """Point on a 2:1 ellipsoid, depth measured from tangent plane toward crown."""
    rho = diameter_mm / 2
    if abs(rho) > radius_mm:
        raise ValueError("placement diameter outside head")
    z = depth_mm * math.sqrt(max(0.0, 1.0 - (rho / radius_mm) ** 2))
    th = math.radians(angle_deg % 360)
    return {"x_mm": rho * math.cos(th), "y_mm": rho * math.sin(th), "z_mm": z}


def circle_interference(center_distance_mm: float, diameter_a_mm: float, diameter_b_mm: float) -> bool:
    """Projected circular reinforcement bounds overlap or touch."""
    return center_distance_mm <= (diameter_a_mm + diameter_b_mm) / 2

