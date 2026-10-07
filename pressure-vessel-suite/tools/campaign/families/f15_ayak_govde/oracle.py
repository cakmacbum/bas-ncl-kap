from math import pi


def calculate(diameter_mm, thickness_mm, count, total_weight_N):
    """Independent annular-section reaction and axial-stress check."""
    inner = diameter_mm - 2.0 * thickness_mm
    area = pi / 4.0 * (diameter_mm**2 - inner**2)
    reaction = total_weight_N / count
    return {"N_max": reaction, "A_leg": area, "P_base": reaction / area}
