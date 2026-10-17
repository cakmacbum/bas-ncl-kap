"""Thirty skirt-column cases spanning H/D and environmental metadata."""
from tools.campaign.bases import skirt_column


def cases():
    for index in range(30):
        ratio = 3.0 + 17.0 * index / 29
        diameter = 1000.0
        wind = (20.0, 35.0, 50.0)[index % 3]
        zone = (0.0, 0.2, 0.4)[(index // 3) % 3]
        project = skirt_column()
        support = project["supports"][0]
        support.update(diameter_mm=diameter, height_mm=diameter * ratio,
                       thickness_mm=10.0, skirt_allowable_compressive_MPa=120.0,
                       skirt_weld_efficiency=0.8,
                       overturning_moment_Nmm=1.0e7 + index * 1.0e6)
        project["project_number"] = f"T14-{index + 1:02d}"
        for load_case in project.get("load_cases", []):
            load_case["wind_speed_m_s"] = wind
            load_case["seismic_zone_factor"] = zone
        yield f"T14-{index + 1:02d}", project, {
            "H_D": round(ratio, 4), "wind_speed_m_s": wind,
            "seismic_zone_factor": zone,
        }
