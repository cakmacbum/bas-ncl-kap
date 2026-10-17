"""Independent checks for explicit flange loads carried by the fixture."""


def values(params):
    # These are the defined Appendix 2 intermediate quantities W (bolt load)
    # and M (applied flange moment), copied from the explicitly supplied inputs.
    # No gasket seating geometry is inferred for Wm1/Wm2/Am or stress terms.
    return {"W": float(params["bolt_load_W_N"]),
            "M": float(params["moment_M_Nmm"]),
            "Wm1": None, "Wm2": None, "Am": None, "Mo": None,
            "SH": None, "SR": None, "ST": None}
