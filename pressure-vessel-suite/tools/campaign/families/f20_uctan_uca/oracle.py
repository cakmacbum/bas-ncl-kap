"""Clean-room geometric checks; no calculation-package implementation used."""
import math


def inner_volume_m3(project):
    total = 0.0
    for s in project.get("shell_sections", []):
        r = float(s["inside_diameter"]) / 2000
        total += math.pi * r*r * float(s["tangent_length"]) / 1000
    for h in project.get("heads", []):
        r = float(h["inside_diameter"]) / 2000
        typ = h["type"]
        if typ == "hemispherical":
            total += 2 * math.pi * r**3 / 3
        elif typ == "elliptical":
            total += 2 * math.pi * r**3 / 3  # 2:1 ellipsoid, semi-axis r/2
        elif typ == "flat":
            pass
        else:
            return None  # custom torispherical surface needs an explicit integral
    return total


def shell_required_mm(pressure_mpa, radius_mm, allowable_mpa, efficiency=1.0):
    """Independent thin-wall internal pressure relation, for context only."""
    den = allowable_mpa * efficiency - 0.6 * pressure_mpa
    return pressure_mpa * radius_mm / den if den > 0 else None
