"""Catalog-backed global load cases with explicit, independently checkable loads."""
from __future__ import annotations

from tools.campaign.examples import example_global_load_case


def variants():
    # Wind/seismic intensities remain metadata: the catalog exposes global load
    # resultants, not a wind-pressure or seismic-force calculation.
    index = 0
    for speed in (20.0, 35.0, 50.0):
        for zone in (0.0, 0.2, 0.4):
            for force, moment in ((1000.0, 200000.0), (2500.0, 500000.0)):
                index += 1
                project = example_global_load_case()
                case = project["load_cases"][0]
                case["wind_speed_m_s"] = speed
                case["seismic_zone_factor"] = zone
                case["external_loads"] = [{"load_id": "F18-LOAD", "component_id": "LEGS",
                                            "fx_n": force, "my_nmm": moment}]
                yield f"LOAD-{index:02d}", project, {
                    "wind_speed_m_s": speed, "seismic_zone_factor": zone,
                    "applied_fx_n": force, "applied_my_nmm": moment,
                    "calculation_type": "global_load_case",
                }
