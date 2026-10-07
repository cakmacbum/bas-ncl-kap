"""Deterministic UG-34 case matrix."""
from __future__ import annotations

from copy import deepcopy
from tools.campaign.bases import vertical_leg_tank


def variants():
    # All lengths are mm, pressure MPa, and allowable stress MPa.
    grid = [
        ("C017-d200-P02", .17, 200, .2, 0), ("C020-d200-P10", .20, 200, 1, 0),
        ("C025-d400-P05", .25, 400, .5, 0), ("C030-d400-P20", .30, 400, 2, 0),
        ("C033-d600-P10", .33, 600, 1, 0), ("C017-d600-P30", .17, 600, 3, 0),
        ("C020-d800-P05", .20, 800, .5, 0), ("C025-d800-P15", .25, 800, 1.5, 0),
        ("C030-d1000-P02", .30, 1000, .2, 0), ("C033-d1000-P10", .33, 1000, 1, 0),
        ("C017-d1200-P05", .17, 1200, .5, 0), ("C020-d1200-P20", .20, 1200, 2, 0),
        ("C025-d1400-P10", .25, 1400, 1, 0), ("C030-d1400-P30", .30, 1400, 3, 0),
        ("C033-d1600-P05", .33, 1600, .5, 0), ("C017-d1600-P15", .17, 1600, 1.5, 0),
        ("C020-d1800-P10", .20, 1800, 1, 0), ("C025-d1800-P30", .25, 1800, 3, 0),
        ("C030-d2000-P05", .30, 2000, .5, 0), ("C033-d2000-P20", .33, 2000, 2, 0),
        ("W-C020", .20, 600, 1, 0), ("W-C025", .25, 1000, 1, 0),
        ("W-C030", .30, 1600, 2, 0), ("W-C033", .33, 2000, 3, 0),
        ("CA-1", .20, 500, 1, 1), ("CA-5", .25, 1000, 1, 5),
        ("CA-20", .30, 1500, 2, 20), ("LOW-P", .20, 1000, .01, 0),
        ("HIGH-P", .33, 1000, 5, 0), ("LOW-S", .20, 1000, 1, 50),
        ("HIGH-S", .20, 1000, 1, 200),
    ]
    for i, (case_id, c, d, p, ca) in enumerate(grid):
        weld = case_id.startswith("W-")
        stress = 137.895 if case_id != "LOW-S" else 50
        project = vertical_leg_tank(
            design_conditions={"operating_pressure": max(.001, p*.8), "design_pressure": p,
                               "maximum_allowable_pressure_ps": max(p, .01)},
            heads=[{
                "head_id": "FLAT-01", "type": "flat", "inside_diameter": d,
                "nominal_thickness": 25, "material_id": "M1",
                "internal_corrosion_allowance": ca,
                "flat_attachment_factor": c, "weld_joint_id": "WJ-01" if weld else None,
            }],
            materials=[{"material_id":"M1", "standard_pack":"ASME II-D 2025",
                        "material_designation":"SA-516 Gr.70", "product_form":"plate",
                        "temperature":200, "allowable_stress":stress, "yield_strength":260,
                        "tensile_strength":485, "source_reference":"ASME II-D Table 1A",
                        "source_revision":"2025", "density":7850}],
            project_number=f"F05-{i:02d}", project_name=case_id,
        )
        # Keep the supplied dimensions/loads explicit for auditability.
        yield case_id, project


def invalid_variants():
    p = vertical_leg_tank(design_conditions={"design_pressure": -1})
    yield "INVALID-NEGATIVE-P", p
    p = vertical_leg_tank(heads=[{"head_id":"FLAT-01", "type":"flat", "inside_diameter":500,
        "nominal_thickness":10, "material_id":"M1"}])
    yield "BLOCKED-MISSING-C", p
