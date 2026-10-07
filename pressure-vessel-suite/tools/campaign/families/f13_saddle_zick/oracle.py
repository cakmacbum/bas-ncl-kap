"""Independent Zick equation evaluator (SI); coefficients are explicit inputs."""
from math import pi, sqrt


def calculate(*, Q_N, L_mm, R_mm, t_mm, A_mm, b_mm, K1, K2, K6, K7):
    """Return absolute stress magnitudes in MPa from elementary beam/shell forms.

    Q_N is one saddle reaction. Midspan moment is the simply-supported uniform
    load expression; saddle moment follows the common Zick saddle moment form.
    This compact oracle deliberately does not infer/tabulate K coefficients.
    """
    R, t, L, A, b = R_mm, t_mm, L_mm, A_mm, b_mm
    if min(Q_N, L, R, t, b, K1, K2, K6, K7) <= 0:
        raise ValueError("positive inputs required")
    # Uniform line-load equivalent from the two support reactions.
    W = 2.0 * Q_N
    M2 = W * L / 8.0
    M1 = Q_N * A * (L - 2.0 * A) / (2.0 * L)
    s1 = abs(M1) / (K1 * R * R * t)
    s2 = abs(M2) / (pi * R * R * t)
    s3 = K2 * Q_N / (2.0 * t * (b + 1.56 * sqrt(R * t)))
    s4 = Q_N / (4.0 * t * (b + 1.56 * sqrt(R * t))) + 3.0 * K6 * Q_N / (2.0 * t * t)
    return {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": K7 * Q_N / (R*t)}


def published_k3_01():
    """Published independent result subset; psi converted to MPa."""
    psi_to_mpa = 0.006894757293
    return {"S1": 9074.51 * psi_to_mpa, "S2": 9236.72 * psi_to_mpa,
            "S3": 277.72 * psi_to_mpa, "S4": 253.77 * psi_to_mpa}
