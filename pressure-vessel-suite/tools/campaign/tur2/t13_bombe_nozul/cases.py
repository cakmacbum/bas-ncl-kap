"""Deterministic head-nozzle cases and independent spherical-part reference."""
from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank

FAMILY = "T13-bombe-nozul"


def spherical_required_thickness(pressure_mpa: float, radius_mm: float,
                                allowable_mpa: float, efficiency: float) -> float:
    """UG-37 head reference: pressure thickness of a sphere, P R/(2 S E-0.2P)."""
    return pressure_mpa * radius_mm / (2 * allowable_mpa * efficiency - 0.2 * pressure_mpa)


def cases():
    out = []
    for shape, radius_factor in (("elliptical", 0.5), ("torispherical", 1.0), ("hemispherical", 0.5)):
        for offset in (0, 100, 300, 399, 400, 401, 450, 500, 600, 800, 801):
            p = vertical_leg_tank()
            head = deepcopy(p["heads"][0])
            head.update(head_id="HEAD-T13", type=shape, inside_diameter=1000,
                        nominal_thickness=16, straight_flange_length=40,
                        crown_radius=1000, knuckle_radius=60)
            p["heads"][0] = head
            p["nozzles"] = [{"tag": "T13-N1", "host_component_id": "HEAD-T13",
                "axial_position": offset, "circumferential_angle": 0,
                "outside_diameter": 114.3, "inside_diameter": 100.0,
                "neck_thickness": 7.1, "material_id": "M1", "reinforcement_pad": False}]
            p["calculation_code"] = "ASME VIII-1"
            p["code_edition"] = "2025"
            d = 100.0
            p80 = 0.8 * 1000
            zone = "center" if offset == 0 else ("inside_80_percent" if offset < p80 else
                   ("on_80_percent" if offset == p80 else "outside_80_percent"))
            case_id = f"{shape}-{offset:03d}"
            oracle_r = radius_factor * 1000
            tr = spherical_required_thickness(p["design_conditions"]["design_pressure"], oracle_r, 138.0, 1.0)
            out.append({"case_id": case_id, "family": FAMILY, "project": p,
                "expected": {"shape": shape, "offset_mm": offset, "zone": zone,
                    "head_spherical_radius_mm": oracle_r,
                    "t_r_mm": tr, "placement_rule": "boundary is 0.8D; outside requires review/block"}})
    return out

