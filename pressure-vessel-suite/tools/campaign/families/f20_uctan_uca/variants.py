"""API-ready pressure sweep based on the catalog's verified thickness example."""
from tools.campaign.examples import example_thickness


def variants():
    # Three vessel bases and ten pressures give 30 distinct API projects.
    # Each project yields shell and head thickness rows; this avoids calling
    # unrelated blocked calculations a comparison.
    from tools.campaign.bases import horizontal_saddle_tank, skirt_column
    bases = (example_thickness, horizontal_saddle_tank, skirt_column)
    for bi, base_fn in enumerate(bases):
        for pressure in (0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2):
            p = base_fn()
            p["design_conditions"]["design_pressure"] = pressure
            p["project_number"] = f"F20b-{bi}-{pressure:.1f}"
            yield f"base-{bi}-pressure-{pressure:.1f}", p
