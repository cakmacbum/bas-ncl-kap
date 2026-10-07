"""Deterministic UG-27 case matrix built from the public campaign base."""
from __future__ import annotations

from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    # Inputs are deliberately sampled at boundary, midpoint, and interaction points.
    specs = [
        ("grid-01", 300, .1, 100, 1.0, 0, 0, 0, 0),
        ("grid-02", 500, .5, 120, .85, 1, 0, 12.5, 0),
        ("grid-03", 800, 1.0, 138, .7, 2, 0, 0, 0),
        ("grid-04", 1000, 1.2, 138, 1.0, 2, 1, 12.5, 0),
        ("grid-05", 1500, 2.0, 150, .85, 3, 0, 0, 0),
        ("grid-06", 2000, 3.0, 160, .7, 4, 2, 12.5, 0),
        ("grid-07", 2500, 4.0, 175, 1.0, 0, 0, 0, 0),
        ("grid-08", 3000, 5.0, 180, .85, 5, 1, 12.5, 0),
        ("grid-09", 3500, 7.5, 190, .7, 6, 0, 0, 0),
        ("grid-10", 4000, 10.0, 200, 1.0, 6, 2, 12.5, 0),
        ("thin-11", 1200, .385, 150, .85, 0, 0, 0, 0),
        ("thick-12", 300, 10.0, 100, .7, 0, 0, 12.5, 0),
        ("mill-13", 600, 1.5, 120, .85, 2, 0, 12.5, 0),
        ("mill-14", 600, 1.5, 120, .85, 2, 0, 0, 0),
        ("ca-15", 900, 2.5, 138, 1.0, 6, 0, 0, 0),
        ("ca-16", 900, 2.5, 138, 1.0, 0, 6, 0, 0),
        ("eff-17", 1000, 2.0, 200, .7, 1, 0, 0, 0),
        ("eff-18", 1000, 2.0, 200, .85, 1, 0, 0, 0),
        ("eff-19", 1000, 2.0, 200, 1.0, 1, 0, 0, 0),
        ("large-20", 4000, .1, 100, .7, 0, 0, 12.5, 0),
        ("large-21", 4000, 10.0, 200, .7, 6, 2, 12.5, 0),
        ("outside-22", 1000, 2.0, 138, .85, 2, 0, 0, 0),
        ("outside-23", 1600, 3.0, 160, .85, 3, 1, 12.5, 0),
        ("outside-24", 2500, 1.0, 180, 1.0, 0, 0, 0, 0),
        ("medium-25", 1800, 4.0, 150, .85, 4, 2, 12.5, 0),
        ("medium-26", 2200, 6.0, 175, 1.0, 2, 0, 0, 0),
        ("medium-27", 750, .8, 110, .7, 1, 1, 12.5, 0),
        ("medium-28", 1250, 1.8, 130, .85, 3, 0, 0, 0),
        ("invalid-p-29", 1000, 0, 138, .85, 0, 0, 0, 0),
        ("invalid-d-30", 0, 1, 138, .85, 0, 0, 0, 0),
        ("invalid-s-31", 1000, 1, 0, .85, 0, 0, 0, 0),
        ("missing-mat-32", 1000, 1, 138, .85, 0, 0, 0, 0),
    ]
    for idx, (case_id, d, p, s, e, ci, ce, mill, outside) in enumerate(specs):
        project = vertical_leg_tank()
        shell = project["shell_sections"][0]
        shell.update(inside_diameter=None if case_id.startswith("outside-") else d,
                     outside_diameter=(d + 20) if case_id.startswith("outside-") else None,
                     nominal_thickness=20.0, internal_corrosion_allowance=ci,
                     external_corrosion_allowance=ce, mill_tolerance=mill)
        project["design_conditions"].update(design_pressure=p, operating_pressure=max(p, .01),
                                             maximum_allowable_pressure_ps=max(p, .01))
        project["materials"][0]["allowable_stress"] = s
        project["welds"][0]["joint_efficiency"] = e
        if case_id == "missing-mat-32":
            shell["material_id"] = "MISSING"
        yield case_id, project
