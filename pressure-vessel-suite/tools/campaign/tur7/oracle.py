"""Saf referans fonksiyonlar (ASME VIII-1 formulleri). API/paket kodu import edilmez."""


def shell_ug27c1(P, S, E, D_i, CA_i):
    """UG-27(c)(1): t = P*R_c/(S*E - 0.6*P), R_c = D_i/2 + CA_i."""
    r_c = D_i / 2.0 + CA_i
    return P * r_c / (S * E - 0.6 * P)


def head_ug32d(P, S, E, D_i, CA_i, crown_depth=None):
    """UG-32(d): t = P*D_c*K/(2SE - 0.2P); K=(2+(D_c/2h)^2)/6.
    crown_depth None -> standart 2:1 (K=1)."""
    d_c = D_i + 2.0 * CA_i
    if crown_depth is None:
        k = 1.0
    else:
        k = (2.0 + (d_c / (2.0 * crown_depth)) ** 2) / 6.0
    return P * d_c * k / (2.0 * S * E - 0.2 * P)


def nozzle_A_required(P, S, E_host, D_i, CA_i, d, F=1.0, use_E=True):
    """UG-37(c): A = d*t_r*F. V1: t_r kabuk verimi E_host ile; V2 (use_E=False): E=1."""
    e = E_host if use_E else 1.0
    t_r = P * (D_i / 2.0 + CA_i) / (S * e - 0.6 * P)
    return d * t_r * F
