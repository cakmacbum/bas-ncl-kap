from tools.campaign.examples import example_base_plate_check


def variants():
    # Complete, API-supported leg setup from the campaign example; vary plate
    # dimensions, thickness, yield strength, and foundation bearing allowance.
    grid = [
        (250, 200, 8, 250, 10), (250, 200, 12, 250, 10),
        (250, 200, 16, 250, 10), (250, 200, 20, 250, 10),
        (200, 200, 12, 250, 8), (200, 200, 16, 250, 8),
        (200, 200, 20, 250, 8), (300, 200, 12, 250, 10),
        (300, 200, 16, 250, 10), (300, 200, 20, 250, 10),
        (300, 250, 12, 345, 15), (300, 250, 16, 345, 15),
        (300, 250, 20, 345, 15), (300, 250, 25, 345, 15),
        (350, 250, 16, 345, 12), (350, 250, 20, 345, 12),
        (350, 250, 25, 345, 12), (400, 300, 20, 345, 20),
        (400, 300, 25, 345, 20), (400, 300, 30, 345, 20),
        (225, 175, 10, 250, 6), (225, 175, 14, 250, 6),
        (275, 225, 14, 250, 10), (275, 225, 18, 250, 10),
        (325, 275, 18, 345, 16), (325, 275, 24, 345, 16),
        (375, 300, 20, 345, 18), (375, 300, 28, 345, 18),
        (450, 350, 25, 345, 20), (450, 350, 32, 345, 20),
    ]
    rows = []
    for i, (length, width, thickness, fy, allowable) in enumerate(grid, 1):
        project = example_base_plate_check()
        project["supports"][0].update(
            base_plate_length_mm=length,
            base_plate_width_mm=width,
            base_plate_thickness_mm=thickness,
            base_plate_yield_MPa=fy,
            foundation_bearing_allowable_MPa=allowable,
        )
        rows.append((f"PLATE-{i:02d}", project))
    return rows
