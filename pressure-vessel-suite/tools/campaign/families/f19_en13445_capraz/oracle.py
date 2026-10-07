"""Independent thin-wall equations used by F19 (EN 13445-3 / ASME VIII-1)."""


def en_shell(P, radius, f, z):
    """EN 13445-3 7.4.2 inside-radius equation, in mm and MPa."""
    return P * radius / (f * z - 0.5 * P)


def asme_shell(P, radius, S, E):
    """ASME VIII-1 UG-27(c)(1), internal pressure, inside radius basis."""
    return P * radius / (S * E - 0.6 * P)


def en_elliptical(P, Di, f, z, beta=1.0):
    return beta * P * Di / (2 * f * z - 0.2 * P)


def en_test_pressure(PS, f_test, f_design):
    return 1.25 * PS * min(f_test / f_design, 1.0)
