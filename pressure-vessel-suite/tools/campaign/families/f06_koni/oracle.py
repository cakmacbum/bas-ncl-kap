"""Bağımsız UG-32(g) iç çap denklemi; basınç MPa, boyut mm."""
from math import cos, radians


def required_thickness(pressure_mpa, inside_diameter_mm, angle_deg, stress_mpa, efficiency):
    return pressure_mpa * inside_diameter_mm / (2*cos(radians(angle_deg))*(stress_mpa*efficiency-0.6*pressure_mpa))


def mawp(thickness_mm, inside_diameter_mm, angle_deg, stress_mpa, efficiency):
    # Denklem t = PD / (2 cos(a) (SE - 0.6P)) cebirsel olarak çözülür.
    k = 2*cos(radians(angle_deg))*stress_mpa*efficiency
    return thickness_mm*k/(inside_diameter_mm+0.6*thickness_mm*cos(radians(angle_deg)))
