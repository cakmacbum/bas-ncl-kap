"""Deterministic nozzle placement variants."""
from __future__ import annotations
from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    base = vertical_leg_tank()
    n1 = base["nozzles"][0]
    specs = [(f"SHELL-{i:02d}", 100 + i * 100, a, d, False) for i, (a, d) in enumerate(
        [(0,60.3),(45,60.3),(90,60.3),(135,60.3),(180,60.3),(225,60.3),(270,60.3),(315,60.3),
         (359.9,60.3),(0,100),(90,100),(180,100),(270,100),(0,200),(90,200),(180,200),
         (270,200),(0,400),(90,400),(180,400),(270,400),(0,900),(90,900),(180,900),(270,900),
         (0,1100),(90,1100),(180,1100),(270,1100),(360,60.3)], 1)]
    for case, z, angle, diameter, invalid in specs:
        p = deepcopy(base)
        p["project_number"] = f"F10-{case}"
        n = dict(n1, tag="N1", axial_position=z, circumferential_angle=angle, outside_diameter=diameter,
                 inside_diameter=min(52.5, diameter - 1))
        if invalid:
            n["circumferential_angle"] = 360
        p["nozzles"] = [n]
        yield case, p

