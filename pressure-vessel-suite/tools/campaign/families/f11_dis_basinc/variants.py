from __future__ import annotations

from copy import deepcopy

from tools.campaign.bases import vertical_leg_tank, with_code


def variants():
    # Geometry grid is deliberately sampled rather than expanded as a full product.
    grid = [
        (0.5, 10), (0.5, 50), (0.5, 600), (1, 20), (1, 100), (1, 400),
        (2, 10), (2, 75), (2, 300), (4, 25), (4, 150), (4, 600),
        (6, 40), (6, 200), (6, 500), (8.5714, 42.6667), (10, 30),
        (10, 120), (10, 600), (15, 20), (15, 250), (15, 500),
        (20, 10), (20, 80), (20, 350), (0.25, 40), (25, 100),
        (5, 8), (3, 700), (50, 42.6667),
    ]
    for i, (ld, dt) in enumerate(grid, 1):
        do = 1000.0
        t = do / dt
        length = ld * do
        b = 56.25 if (ld, dt) == (8.5714, 42.6667) else 60.0 + (i % 7) * 10.0
        p = vertical_leg_tank(
            design_conditions={"external_pressure": 0.1, "vacuum_condition": True},
            shell_sections=[{
                "section_id": "SHELL-01", "outside_diameter": do,
                "tangent_length": length, "nominal_thickness": t,
                "material_id": "M1", "ug28_strain_factor_a": 0.0006042 if i == 16 else 0.0005,
                "ug28_allowable_stress_b": b * 0.006894757293168361,
            }],
        )
        yield f"GRID-{i:02d}", with_code(p, "ASME VIII-1")

    # Published K2-16 input and two output checks; B is the source's numeric input.
    for case_id, thickness, a, b in (
        ("K2-16-EMA-WP", 8.33374, 0.0006042, 56.2497),
        ("K2-16-THICKNESS", 6.51284, 0.0003790, 35.2284),
    ):
        p = vertical_leg_tank(
            design_conditions={"external_pressure": 0.861843, "vacuum_condition": True},
            shell_sections=[{
                "section_id": "SHELL-01", "outside_diameter": 355.6,
                "tangent_length": 3048.0, "nominal_thickness": thickness,
                "material_id": "M1", "ug28_strain_factor_a": a,
                "ug28_allowable_stress_b": b * 0.006894757293168361,
            }],
        )
        yield case_id, with_code(p, "ASME VIII-1")
