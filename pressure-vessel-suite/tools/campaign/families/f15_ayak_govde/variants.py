from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    """Temsilci boru ayakları, K3 yayın vakaları ve geçersiz sınırlar."""
    cases = []
    for shape, od, t in (("pipe", 114.3, 8.0), ("pipe", 88.9, 5.4865),
                         ("box", 100.0, 6.0), ("box", 120.0, 8.0),
                         ("angle", 75.0, 6.0), ("angle", 90.0, 8.0), ("u", 90.0, 5.0)):
        for n in (3, 4, 6, 8):
            p = vertical_leg_tank()
            leg = p["supports"][0]
            leg.update(leg_count=n, leg_diameter_mm=od, leg_thickness_mm=t)
            cases.append((f"{shape}-n{n}-od{od:g}", p, {"shape": shape, "count": n, "od_mm": od, "t_mm": t, "length_mm": leg["height_mm"], "K": 1.0}))
    # K3-13 PVE-Sample 8: A=4.61 in2, r=1.2 in, L=26.5 in, W=12,300 lb.
    # K3-14 IJERT: A=14.377 cm2, r=29.555 mm, L=700 mm, W=1574.2 kgf.
    for cid, count, diameter, thick, length, weight in (
        ("K3-13-PVE-Sample8", 4, 101.6, 15.875, 673.1, 12300 * 4.4482216153),
        ("K3-14-IJERT-2013", 3, 88.9, 5.4865, 700.0, 1574.2 * 9.80665),
    ):
        p = vertical_leg_tank()
        p["supports"][0].update(leg_count=count, leg_diameter_mm=diameter, leg_thickness_mm=thick, height_mm=length)
        p["design_conditions"]["design_pressure"] = 0.0
        cases.append((cid, p, {"published": cid, "count": count, "diameter_mm": diameter, "thickness_mm": thick, "length_mm": length, "weight_N": weight}))
    # Invalid/missing support geometry should not be treated as a numeric comparison.
    p = vertical_leg_tank(); p["supports"][0]["leg_count"] = 0
    cases.append(("invalid-zero-count", p, {"invalid": "leg_count=0"}))
    p = vertical_leg_tank(); p["supports"][0].pop("leg_count")
    cases.append(("missing-count", p, {"invalid": "leg_count absent"}))
    return cases
