from tools.campaign.examples import example_leg_stress


def variants():
    """Working leg-stress examples with useful geometry/count variations."""
    cases = []
    for diameter, thickness in ((114.3, 8.0), (88.9, 5.4865), (101.6, 6.35), (139.7, 9.525)):
        for count in (3, 4, 5, 6, 8, 10, 12):
            project = example_leg_stress()
            leg = project["supports"][0]
            leg.update(leg_count=count, leg_diameter_mm=diameter, leg_thickness_mm=thickness)
            cases.append((f"pipe-n{count}-od{diameter:g}", project,
                          {"count": count, "diameter_mm": diameter, "thickness_mm": thickness}))
    for cid, count, diameter, thickness, length, weight in (
        ("K3-13-PVE-Sample8", 4, 101.6, 15.875, 673.1, 12300 * 4.4482216153),
        ("K3-14-IJERT-2013", 3, 88.9, 5.4865, 700.0, 1574.2 * 9.80665),
    ):
        project = example_leg_stress()
        project["supports"][0].update(leg_count=count, leg_diameter_mm=diameter,
                                      leg_thickness_mm=thickness, height_mm=length)
        project["design_conditions"]["design_pressure"] = 0.0
        cases.append((cid, project, {"published": cid, "count": count,
                                     "diameter_mm": diameter, "thickness_mm": thickness,
                                     "weight_N": weight}))
    return cases
