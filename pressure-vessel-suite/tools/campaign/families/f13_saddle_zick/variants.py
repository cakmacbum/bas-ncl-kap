"""Saddle cases based on the catalog's runnable public-API example."""
from copy import deepcopy

from tools.campaign.examples import example_saddle_stress


def variants():
    cases = []
    # A compact sample across saddle spacing, width, contact angle, and stiffening.
    for i in range(30):
        p = example_saddle_stress()
        supports = p["supports"]
        angle = (120, 135, 150)[i % 3]
        width = (150, 250, 400)[(i // 3) % 3]
        stiffened = bool((i // 9) % 2)
        span = (900, 1100, 1200, 1300, 1500)[i % 5]
        for j, support in enumerate(supports):
            support["width_mm"] = width
            support["contact_angle_deg"] = angle
            support["saddle_stiffened"] = stiffened
            support["location_mm"] = 250 if j == 0 else 250 + span
        cases.append((f"catalog-{i+1:02d}", p, {
            "span_mm": span, "width_mm": width, "theta_deg": angle,
            "stiffened": stiffened,
        }))
    # Catalog-defined invalid requests exercise blocked behavior.
    p = deepcopy(cases[0][1])
    p["supports"][0]["zick_K1"] = None
    cases.append(("invalid-missing-K1", p, {"invalid": "missing zick_K1"}))
    p = deepcopy(cases[0][1])
    p["supports"][0]["contact_angle_deg"] = 160
    cases.append(("invalid-angle", p, {"invalid": "160 degrees"}))
    return cases
