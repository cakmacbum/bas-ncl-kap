"""Independent UG-32(d) equations, written from the stated code formula."""


def required_thickness(pressure_mpa, inside_diameter_mm, allowable_mpa, efficiency,
                       corrosion_mm=0.0):
    """UG-32(d), K=1: pressure thickness plus the explicit corrosion allowance."""
    p = pressure_mpa
    t_pressure = p * inside_diameter_mm / (2 * allowable_mpa * efficiency - 0.2 * p)
    return t_pressure + corrosion_mm


def mawp(inside_diameter_mm, net_thickness_mm, allowable_mpa, efficiency):
    """Inverse UG-32(d), using net available thickness."""
    return 2 * allowable_mpa * efficiency * net_thickness_mm / (inside_diameter_mm + 0.2 * net_thickness_mm)


def flat_flange_ug27(pressure_mpa, inside_radius_mm, allowable_mpa, efficiency):
    """UG-27(c)(1), used only as a separate cylindrical reference."""
    return pressure_mpa * inside_radius_mm / (allowable_mpa * efficiency - 0.6 * pressure_mpa)
