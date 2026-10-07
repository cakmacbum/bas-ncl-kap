"""Representative wind and seismic input variants."""
from __future__ import annotations

from tools.campaign.bases import skirt_column


def variants():
    """Yield a compact boundary/interior matrix plus invalid/missing inputs."""
    speeds = (20.0, 35.0, 50.0)
    zones = (0.0, 0.2, 0.4)
    dimensions = ((1000.0, 2000.0), (1500.0, 4000.0))
    idx = 0
    for speed in speeds:
        for zone in zones:
            for diameter, height in dimensions:
                idx += 1
                p = skirt_column()
                p["shell_sections"][0]["inside_diameter"] = diameter
                p["shell_sections"][0]["tangent_length"] = height
                p["load_cases"] = [{"load_case_id": "WIND", "name": "Wind", "load_type": "wind",
                    "wind_speed_m_s": speed, "concurrent_with": ["SEISMIC"]},
                    {"load_case_id": "SEISMIC", "name": "Seismic", "load_type": "seismic",
                     "seismic_zone_factor": zone, "concurrent_with": ["WIND"]}]
                p["load_combinations"] = [{"combination_id": "W+E", "name": "Wind plus seismic",
                    "load_case_ids": ["WIND", "SEISMIC"], "load_factors": {"WIND": 1.0, "SEISMIC": 1.0},
                    "is_concurrent": True}]
                yield f"GRID-{idx:02d}", p, {"wind_speed_m_s": speed, "seismic_zone_factor": zone,
                    "diameter_mm": diameter, "height_mm": height, "contents": "full" if idx % 2 else "empty",
                    "wind_factor": 1.0, "seismic_factor": 1.0, "concurrent": True}

    # Edge/invalid records still use valid project templates so the API decides status.
    for case_id, speed, zone, concurrent in (("EDGE-CALM", 0.0, 0.2, True),
            ("EDGE-50", 50.0, 0.0, True), ("EDGE-NONCONCURRENT", 35.0, 0.4, False),
            ("INVALID-NEGATIVE", -1.0, 0.2, True), ("MISSING-WIND", None, 0.2, True),
            ("INVALID-ZONE", 35.0, -0.1, True)):
        p = skirt_column()
        cases = [{"load_case_id": "SEISMIC", "name": "Seismic", "load_type": "seismic",
                  "seismic_zone_factor": zone}]
        if speed is not None:
            cases.insert(0, {"load_case_id": "WIND", "name": "Wind", "load_type": "wind",
                             "wind_speed_m_s": speed})
        p["load_cases"] = cases
        p["load_combinations"] = [{"combination_id": "EDGE", "name": "Edge combination",
            "load_case_ids": ["WIND", "SEISMIC"], "load_factors": {"WIND": 1.0, "SEISMIC": 1.0},
            "is_concurrent": concurrent}]
        yield case_id, p, {"wind_speed_m_s": speed, "seismic_zone_factor": zone, "concurrent": concurrent}

    for factor in (0.6, 0.75, 1.0, 1.2, 1.4, 1.6):
        p = skirt_column()
        p["load_cases"] = [{"load_case_id": "WIND", "name": "Wind", "load_type": "wind",
            "wind_speed_m_s": 35.0, "concurrent_with": ["SEISMIC"]},
            {"load_case_id": "SEISMIC", "name": "Seismic", "load_type": "seismic",
             "seismic_zone_factor": 0.2, "concurrent_with": ["WIND"]}]
        p["load_combinations"] = [{"combination_id": "W+E", "name": "Factored combination",
            "load_case_ids": ["WIND", "SEISMIC"], "load_factors": {"WIND": factor, "SEISMIC": 1.0},
            "is_concurrent": True}]
        yield f"FACTOR-{factor}", p, {"wind_speed_m_s": 35.0, "seismic_zone_factor": 0.2,
            "wind_factor": factor, "seismic_factor": 1.0, "concurrent": True}
