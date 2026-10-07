"""Clean-room Appendix 2 arithmetic from publicly cited equations and examples."""
import math


def values(params):
    """Return only quantities derivable from the case's explicit inputs.

    App. 2-5 needs gasket effective width/diameter and pressure thrust area;
    this project schema does not carry those dimensions, so loads are not guessed.
    """
    return {"Wm1": None, "Wm2": None, "Am": None, "W": None,
            "Mo": None, "SH": None, "SR": None, "ST": None}


def bsc(bsmax, bs):
    """Appendix 2-3 bolt-spacing multiplier, capped at unity from below."""
    return max(1.0, bsmax / bs) if bs > 0 else None
