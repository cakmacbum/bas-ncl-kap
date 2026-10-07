"""Independent UG-32(f) pressure/thickness relationships; dimensions in mm, MPa."""


def required_thickness(pressure, diameter, allowable_stress, efficiency, ca=0.0):
    radius = diameter / 2.0 + ca
    p = pressure
    denominator = 2.0 * allowable_stress * efficiency - 0.2 * p
    if denominator <= 0:
        return None
    return p * radius / denominator + ca


def mawp(diameter, nominal_thickness, allowable_stress, efficiency, ca=0.0):
    radius = diameter / 2.0 + ca
    net = nominal_thickness - ca
    if net <= 0:
        return None
    return 2.0 * allowable_stress * efficiency * net / (radius + 0.2 * net)


def values(project):
    head = project["heads"][0]
    material = next(m for m in project["materials"] if m["material_id"] == head["material_id"])
    weld = next((w for w in project["welds"] if w.get("weld_joint_id") == head.get("weld_joint_id")
                 or w.get("joint_id") == head.get("weld_joint_id")), {})
    efficiency = weld.get("joint_efficiency", weld.get("efficiency", 1.0))
    ca = head["internal_corrosion_allowance"]
    return required_thickness(project["design_conditions"]["design_pressure"], head["inside_diameter"],
                              material["allowable_stress"], efficiency, ca), mawp(
        head["inside_diameter"], head["nominal_thickness"], material["allowable_stress"], efficiency, ca)
