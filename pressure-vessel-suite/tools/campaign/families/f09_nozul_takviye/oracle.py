"""Temiz oda UG-37(c)/UG-40/UG-45 alan hesabı (mm, MPa)."""

def calculate(*, d, t, tn, pressure, allowable, efficiency=1.0, pad_od=0.0, pad_t=0.0, projection=0.0):
    # UG-37(c): required area; UG-40: limits for available shell/nozzle/pad area.
    tr = pressure * d / (2 * allowable * efficiency + 0.8 * pressure)
    trn = pressure * d / (2 * allowable + 0.8 * pressure)
    A = d * tr
    L = min(max(d, (d/2 + tn + t)), 2.5*t, 2.5*tn)
    A1 = 2 * L * max(0.0, t-tr) * efficiency
    A2 = 2 * min(projection, 2.5*tn) * max(0.0, tn-trn)
    A3 = 0.0
    A4 = min(max(0.0, pad_od-d), 2*L) * min(pad_t, max(0.0, t-tr))
    A5 = 0.0
    total=A1+A2+A3+A4+A5
    return {"A":A,"A1":A1,"A2":A2,"A3":A3,"A4":A4,"A5":A5,"total":total,
            "adequate":total >= A,"UG45_t_min":max(trn,1.5)}
