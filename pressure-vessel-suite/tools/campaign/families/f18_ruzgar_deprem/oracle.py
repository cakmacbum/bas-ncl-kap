"""Independent direct equilibrium oracle for explicit external load components."""
from __future__ import annotations


def load_case_oracle(params: dict, quantity: str) -> float:
    """One horizontal force and one overturning moment are supplied per case."""
    if quantity == "resultant_shear":
        return abs(float(params["applied_fx_n"]))
    if quantity == "overturning_moment":
        return abs(float(params["applied_my_nmm"]))
    raise KeyError(quantity)
