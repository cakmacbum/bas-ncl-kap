"""Deterministic leg-to-pad weld variants using the catalog example project."""
from __future__ import annotations

from tools.campaign.examples import example_leg_weld_check


def variants():
    # Vary the rectangular pad perimeter and its weld throat. The API example
    # supplies all required vessel, leg, material, and load fields.
    cases = [
        (70, 120, 6), (50, 100, 4), (100, 200, 4), (150, 250, 4),
        (200, 300, 4), (100, 100, 4), (25, 200, 4), (300, 50, 4),
        (75, 225, 4), (250, 125, 4), (400, 400, 4), (10, 10, 4),
        (500, 100, 4), (600, 400, 4), (400, 250, 4), (250, 180, 4),
        (120, 80, 5), (180, 90, 5), (220, 140, 5), (320, 180, 5),
        (90, 260, 5), (260, 90, 5), (350, 225, 5), (500, 300, 5),
    ]
    for i, (b, d, weld_leg) in enumerate(cases, 1):
        project = example_leg_weld_check()
        support = project["supports"][0]
        support.update(leg_pad_length_mm=b, leg_pad_width_mm=d,
                       pad_to_shell_weld_leg_mm=weld_leg)
        yield f"PAD-WELD-{i:02d}", project, {
            "shape": "rectangle", "b_mm": b, "d_mm": d,
            "weld_leg_mm": weld_leg, "joint": "pad_to_shell",
        }
