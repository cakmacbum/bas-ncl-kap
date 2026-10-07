"""Clean-room pressure-thickness equations, independently transcribed."""


def value(intermediates, key):
    return next((float(x["value"]) for x in intermediates if x.get("name") == key), None)


def required_thickness(row, project=None):
    iv = row.get("intermediate_values") or []
    p, stress, efficiency = value(iv, "P"), value(iv, "S"), value(iv, "E")
    if p is None or stress is None or efficiency is None:
        return None
    if row.get("component_type") == "shell":
        radius = value(iv, "R")
        if radius is None:
            return None
        # Cylindrical shell, circumferential membrane stress.
        return p * radius / (stress * efficiency - 0.6 * p)
    diameter = value(iv, "D")
    if diameter is None and project:
        head_id = row.get("component_id")
        head = next((h for h in project.get("heads", []) if h.get("head_id") == head_id), None)
        if head:
            diameter = float(head["inside_diameter"])
    k = value(iv, "K_factor") or 1.0
    if diameter is None:
        return None
    # Ellipsoidal-head form, with the catalog API's disclosed geometry factor.
    return p * diameter * k / (2 * stress * efficiency - 0.2 * p)
