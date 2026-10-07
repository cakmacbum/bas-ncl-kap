"""Temiz oda oracle: kesit statikleri and AISC 360-16 E3 column curve."""
from math import pi, sqrt

E_MPA = 200000.0
FY_MPA = 250.0


def section(shape, d, t):
    if shape == "box":
        a = d*d - (d-2*t)**2
        ix = (d**4-(d-2*t)**4)/12
        return a, sqrt(ix/a)
    if shape in ("u", "angle"):
        # thin-wall idealizations: web plus two (U) or one (L) flange
        a = (3 if shape == "u" else 2)*d*t
        return a, d/sqrt(12)
    a = pi/4*(d*d-(d-2*t)**2)
    i = pi/64*(d**4-(d-2*t)**4)
    return a, sqrt(i/a)


def calculate(shape, d, t, length, k, weight_n, count):
    area, radius = section(shape, d, t)
    slender = k*length/radius
    fe = pi*pi*E_MPA/slender**2
    fcr = (0.658**(FY_MPA/fe))*FY_MPA if FY_MPA/fe <= 2.25 else 0.877*fe
    axial = weight_n/count
    return {"area_mm2": area, "radius_mm": radius, "KLr": slender,
            "axial_N": axial, "stress_MPa": axial/area, "Fcr_MPa": fcr}
