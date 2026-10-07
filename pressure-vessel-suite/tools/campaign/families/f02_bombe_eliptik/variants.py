"""Deterministic head variants for the F02 campaign."""
from __future__ import annotations

from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    # Valid cases cover scale, pressure, E, CA, mill tolerance, forming loss,
    # flange length and mixed boundary values. Geometry is kept 2:1 (h=D/4).
    specs = [
        ("BASE", 1000, .8, 0, 0, 0, 0, 25, 12, .85),
        ("D300", 300, .8, 0, 0, 0, 0, 0, 8, 1.0),
        ("D4000", 4000, .8, 0, 0, 0, 0, 100, 20, .85),
        ("P01", 1000, .1, 0, 0, 0, 0, 25, 10, 1.0),
        ("P6", 1000, 6, 0, 0, 0, 0, 25, 30, .85),
        ("CA1", 1000, .8, 1, 0, 0, 0, 25, 12, .85),
        ("CA3", 1000, .8, 3, 0, 0, 0, 25, 14, 1.0),
        ("MILL125", 1000, .8, 0, 12.5, 0, 0, 25, 12, .85),
        ("MILL3", 1000, .8, 0, 3, 0, 0, 25, 12, 1.0),
        ("FORM1", 1000, .8, 0, 0, 1, 0, 25, 12, .85),
        ("FORM3", 1000, .8, 0, 0, 3, 0, 25, 15, .85),
        ("FLANGE0", 1000, .8, 0, 0, 0, 0, 0, 12, .85),
        ("FLANGE100", 1000, .8, 0, 0, 0, 0, 100, 12, .85),
        ("E70", 1000, .8, 0, 0, 0, 0, 25, 12, .70),
        ("E100", 1000, .8, 0, 0, 0, 0, 25, 12, 1.0),
        ("SMALL_LOW", 300, .1, 0, 0, 0, 0, 0, 5, .70),
        ("SMALL_HIGH", 300, 6, 1, 3, 2, 0, 50, 25, .85),
        ("LARGE_LOW", 4000, .1, 3, 12.5, 3, 0, 100, 15, 1.0),
        ("LARGE_HIGH", 4000, 6, 0, 0, 0, 0, 25, 40, .70),
        ("MID1", 1800, 1.5, .5, 5, .5, 0, 10, 18, .9),
        ("MID2", 2500, 3, 2, 10, 1.5, 0, 75, 25, .85),
        ("MID3", 750, 2.2, .2, 7.5, .25, 0, 35, 12, 1.0),
        ("MID4", 3200, .6, 1.5, 2, 2.5, 0, 60, 20, .9),
        ("MID5", 1250, 4.5, 0, 8, .75, 0, 15, 30, .85),
        ("MID6", 2200, .25, 2.5, 0, 1, 0, 90, 12, 1.0),
        ("MID7", 900, 5, 1, 12.5, 0, 0, 5, 35, .70),
        ("MID8", 3500, 2, .75, 4, 2, 0, 45, 22, .85),
        ("MID9", 1600, 1, 3, 6, 0, 0, 100, 15, 1.0),
        ("MID10", 2800, 3.5, .25, 1, 1, 0, 0, 28, .9),
        # Published K1-19, converted exactly from inch/psi to mm/MPa.
        ("K1-19", 448.31, 1.3886, .254, 0, 0, 0, 0, 4.7752, .85),
    ]
    for case_id, d, p, ca, mill, form, _unused, flange, nominal, eff in specs:
        project = vertical_leg_tank(
            design_conditions={"design_pressure": p, "operating_pressure": p,
                               "maximum_allowable_pressure_ps": p,
                               "corrosion_allowance_internal": 0},
            heads=[{"head_id": "HEAD-L", "type": "elliptical", "inside_diameter": d,
                    "outside_diameter": d + 2 * nominal, "crown_depth": d / 4,
                    "straight_flange_length": flange, "nominal_thickness": nominal,
                    "material_id": "M1", "weld_joint_id": "WJ-01",
                    "internal_corrosion_allowance": ca, "mill_tolerance": mill,
                    "forming_thinning": form},
                   {"head_id": "HEAD-R", "type": "elliptical", "inside_diameter": d,
                    "outside_diameter": d + 2 * nominal, "crown_depth": d / 4,
                    "straight_flange_length": flange, "nominal_thickness": nominal,
                    "material_id": "M1", "weld_joint_id": "WJ-01",
                    "internal_corrosion_allowance": ca, "mill_tolerance": mill,
                    "forming_thinning": form}],
            materials=[{"material_id": "M1", "standard_pack": "campaign manual",
                        "material_designation": "campaign plate", "product_form": "plate",
                        "temperature": 200, "allowable_stress": 138,
                        "allowable_stress_test_temp": 138, "yield_strength": 260,
                        "tensile_strength": 485, "source_reference": "campaign input"}],
            welds=[{"joint_id": "WJ-01", "joint_type": "longitudinal",
                    "weld_category": "A", "joint_efficiency": eff,
                    "nde_method": "RT-1", "nde_extent": "100%"}],
            diameter_relation="independent",
        )
        yield case_id, project


def invalid_variant():
    """A missing material-data case intended to be blocked by the API."""
    project = next(project for case_id, project in variants() if case_id == "BASE")
    project = deepcopy(project)
    project["heads"][0]["material_id"] = "MISSING"
    return project
