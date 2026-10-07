"""Independent thin-wall equations used by F19."""
def en_shell(P, Di, Rp02, Rm, z):
    f = min(Rp02 / 1.5, Rm / 2.4)
    return P * Di / (2 * f * z - P), f

def asme_shell(P, Di, S, E):
    return P * Di / (2 * S * E - 0.2 * P)

def en_elliptical(P, Di, Rp02, Rm, z, beta=1.0):
    f = min(Rp02 / 1.5, Rm / 2.4)
    return P * Di * beta / (2 * f * z - 0.2 * P)

def en_test_pressure(PS, f_test, f_design):
    return 1.25 * PS * min(f_test / f_design, 1.0)

