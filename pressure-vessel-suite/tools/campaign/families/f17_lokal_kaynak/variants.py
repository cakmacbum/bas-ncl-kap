"""Small, deterministic geometry grid for line-weld and WRC scaling probes."""
from __future__ import annotations

from tools.campaign.bases import vertical_leg_tank


def variants():
    # Rectangle b,d corners, interior points, and equal-side case.
    dimensions = [(50, 100), (70, 120), (100, 200), (150, 250), (200, 300),
                  (100, 100), (25, 200), (300, 50), (75, 225), (250, 125),
                  (400, 400), (10, 10), (500, 100)]
    for index, (b, d) in enumerate(dimensions, 1):
        yield f"RECT-{index:02d}", vertical_leg_tank(), {
            "shape": "rectangle", "b_mm": b, "d_mm": d, "wrc_factor": 1.0,
            "support_pad_length_mm": 250, "support_pad_width_mm": 180,
        }
    for index, diameter in enumerate((50, 100, 200, 500, 1000), 1):
        yield f"CIRCLE-{index:02d}", vertical_leg_tank(), {
            "shape": "circle", "b_mm": diameter, "d_mm": diameter, "diameter_mm": diameter, "wrc_factor": 1.0,
            "support_pad_length_mm": 250, "support_pad_width_mm": 180,
        }
    for index, factor in enumerate((0.25, 0.5, 1.0, 2.0, 4.0), 1):
        yield f"WRC-SCALE-{index:02d}", vertical_leg_tank(), {
            "shape": "rectangle", "b_mm": 100, "d_mm": 200,
            "wrc_factor": factor, "support_pad_length_mm": 250,
            "support_pad_width_mm": 180,
        }
    for index, (length, width) in enumerate(((100, 100), (250, 180), (400, 250), (600, 400)), 1):
        project = vertical_leg_tank()
        project["supports"][0]["leg_pad_length_mm"] = length
        project["supports"][0]["leg_pad_width_mm"] = width
        yield f"PAD-{index:02d}", project, {"shape": "rectangle", "b_mm": length, "d_mm": width, "wrc_factor": 1.0,
             "support_pad_length_mm": length, "support_pad_width_mm": width}
    for case_id, dims in (("INVALID-ZERO", (0, 200)), ("INVALID-NEGATIVE", (100, -1)),
                          ("INVALID-MISSING", (None, 200))):
        project = vertical_leg_tank()
        project["design_conditions"]["design_pressure"] = -1.0
        yield case_id, project, {"shape": "rectangle", "b_mm": dims[0],
              "d_mm": dims[1], "wrc_factor": 1.0, "invalid": True}
