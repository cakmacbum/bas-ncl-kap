"""Deterministic skirt support cases, including limits and missing-input cases."""
from __future__ import annotations

from tools.campaign.bases import skirt_column


def variants():
    # Cover both ends and representative interior points without a Cartesian grid.
    settings = [
        (d, t, h, e, m)
        for d, t, h, e, w, m in [
            (850, 6, 1000, .55, 30000, 0), (1000, 8, 1200, .6, 50000, 1e6),
            (1500, 12, 2000, .7, 100000, 5e6), (2000, 20, 4000, .85, 250000, 2e7),
            (3000, 30, 6000, 1.0, 500000, 1e8), (1200, 10, 3000, .8, 0, 2e7),
            (2400, 16, 5000, .9, 750000, 4e7), (1800, 25, 1500, .65, 200000, 8e7),
            (900, 15, 6000, .75, 60000, 6e6), (2800, 6, 2500, .95, 900000, 9e7),
            (1300, 30, 4500, .55, 400000, 3e7), (2200, 18, 1000, 1.0, 125000, 7e7),
            (1600, 9, 3500, .62, 350000, 1e7), (2600, 22, 5500, .78, 650000, 5e7),
            (1100, 7, 1800, .88, 80000, 2e6), (2900, 28, 3200, .68, 300000, 9e7),
            (1900, 13, 5200, .92, 550000, 1.5e7), (1400, 24, 2200, .58, 150000, 6e7),
            (2500, 11, 4200, .82, 850000, 3.5e7), (1000, 19, 5800, .72, 450000, 8.5e7),
            (1700, 6, 1300, .98, 100000, 4e6), (2100, 27, 2800, .63, 700000, 7.5e7),
            (2700, 14, 4800, .87, 225000, 2.5e7), (950, 21, 3600, .57, 625000, 5.5e7),
            (2300, 29, 1600, .77, 175000, 1.2e7), (1250, 17, 6000, .93, 575000, 6.5e7),
            (2850, 23, 2300, .66, 325000, 4.5e7), (1550, 28, 3900, .83, 975000, 8e7),
            (1950, 7, 4900, .59, 275000, 3.2e7), (2650, 26, 1100, .97, 725000, 9.5e7),
        ]
    ]
    for i, (diameter, thickness, height, efficiency, moment_nmm) in enumerate(settings, 1):
        p = skirt_column()
        support = p["supports"][0]
        support.update(diameter_mm=diameter, thickness_mm=thickness, height_mm=height,
                       skirt_weld_efficiency=efficiency, skirt_allowable_compressive_MPa=120,
                       overturning_moment_Nmm=moment_nmm)
        p["project_number"] = f"F14-{i:02d}"
        yield f"GRID-{i:02d}", p, {"D_mm": diameter, "t_mm": thickness, "height_mm": height,
            "E": efficiency, "M_Nmm": moment_nmm,
            "weight_case": "suite-derived W_total; template weight is not an exposed variant input"}
    # Published CRC arithmetic case, modelled with matching mean diameter and t.
    p = skirt_column()
    p["supports"][0].update(diameter_mm=4250, thickness_mm=10, height_mm=1200,
        skirt_weld_efficiency=1.0, skirt_allowable_compressive_MPa=120,
        overturning_moment_Nmm=2050e6)
    p["project_number"] = "F14-K3-08"
    yield "K3-08", p, {"D_mm":4250,"t_mm":10,"E":1.0,"M_Nmm":2050e6,
        "published_W_N":720000,"weight_case":"suite-derived W_total; published weight not applied"}
    # Expected blocking conditions: no B value, or physically invalid skirt wall.
    p = skirt_column(); p["supports"][0]["skirt_allowable_compressive_MPa"] = None
    yield "MISSING-B", p, {"D_mm":1000,"t_mm":8}
    p = skirt_column(); p["supports"][0]["thickness_mm"] = 0
    yield "INVALID-THICKNESS", p, {"D_mm":1000,"t_mm":0}
