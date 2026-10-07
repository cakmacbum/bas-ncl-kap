from math import sqrt


def oracle(params):
    L,W,Fy,fc,P,M,V,n,Dbc = (params[k] for k in ("L","W","Fy","fc","P","M","V","n","Dbc"))
    fp = P/(L*W)
    l = max((L-W)/2, 0.0)
    req = l*sqrt(2*fp/(0.9*Fy)) if Fy else None
    tension = max(M/((n/4)*Dbc)-P/n, 0.0) if n and Dbc else None
    return {"required_thickness":req, "concrete_pressure":fp,
            "anchor_tension":tension, "anchor_shear":V/n if n else None}
