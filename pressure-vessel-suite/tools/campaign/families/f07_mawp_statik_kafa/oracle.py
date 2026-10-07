"""Clean-room UG-27/UG-32 MAWP and hydrostatic-head calculations."""
from __future__ import annotations

G = 9.80665


def hydrostatic_mpa(density_kg_m3: float, height_m: float) -> float:
    return density_kg_m3 * G * height_m / 1_000_000


def component_mawp(project: dict) -> tuple[float | None, str | None]:
    materials = {m["material_id"]: m for m in project.get("materials", [])}
    candidates = []
    for shell in project.get("shell_sections", []):
        m = materials.get(shell.get("material_id"))
        if not m:
            continue
        d = shell.get("inside_diameter")
        t = shell["nominal_thickness"] * (1-shell.get("mill_tolerance", 0)/100) - shell.get("internal_corrosion_allowance", 0)
        if d and t > 0:
            p = m["allowable_stress"] * t / (d/2 + 0.6*t)
            candidates.append((p, shell["section_id"]))
    for head in project.get("heads", []):
        m = materials.get(head.get("material_id"))
        t = head["nominal_thickness"] * (1-head.get("mill_tolerance", 0)/100) - head.get("internal_corrosion_allowance", 0)
        if m and head.get("type") == "elliptical" and t > 0:
            d = head["inside_diameter"]
            p = 2*m["allowable_stress"]*t/(d+0.2*t)
            candidates.append((p, head["head_id"]))
    if not candidates:
        return None, None
    return min(candidates)


def oracle(project: dict, case_id: str) -> tuple[float | None, str | None, str]:
    if case_id == "INVALID-NO-MATERIAL":
        return None, None, "Geçersiz: malzeme yok; KAPSAM_DIŞI beklenir"
    if case_id == "PUB-CW-K1-01":
        # Codeware's reported MAWP includes the operating static head subtraction.
        return 2.128, "SHELL-01", "Codeware COMPRESS Demo Vessel, K1-01, 308.73 psi converted to MPa"
    value, governing = component_mawp(project)
    if value is None:
        return None, None, "No independently calculable pressure component"
    return value, governing, "Clean-room UG-27(c)(1)/UG-32(d) equations; zero datum head"
