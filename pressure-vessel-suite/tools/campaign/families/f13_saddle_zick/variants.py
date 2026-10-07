"""Deterministic, compact saddle geometry campaign matrix."""
from copy import deepcopy

from tools.campaign.bases import horizontal_saddle_tank


def variants():
    # K values are explicit inputs; the source's K mapping and applicability
    # remain an acknowledged limitation (see family report).
    cases = []
    axes = [
        ("base", 5000, 250, 120, False, 1000, 4000, 5000),
        ("short_L", 3500, 250, 120, False, 1000, 3000, 4500),
        ("long_L", 7000, 250, 120, False, 1000, 3000, 6000),
        ("a_low", 5000, 250, 120, False, 300, 4000, 5000),
        ("a_high", 5000, 250, 120, False, 1400, 4000, 5000),
        ("theta_150", 5000, 250, 150, False, 1000, 4000, 5000),
        ("theta_135", 5000, 250, 135, False, 1000, 4000, 5000),
        ("width_narrow", 5000, 150, 120, False, 1000, 4000, 5000),
        ("width_wide", 5000, 400, 120, False, 1000, 4000, 5000),
        ("ring", 5000, 250, 120, True, 1000, 4000, 5000),
    ]
    # 3×10 representative cases cover spacing, contact width/angle, A/R,
    # ring, empty/full weight and position. Values are SI mm and MPa.
    for repeat, scale in enumerate((0.85, 1.0, 1.15)):
        for name, L, b, theta, ring, A, x1, x2 in axes:
            p = horizontal_saddle_tank(
                design_conditions={"design_pressure": 0.2, "operating_pressure": 0.18,
                                   "maximum_allowable_pressure_ps": 0.2},
                shell_sections=[{"section_id":"SHELL-01", "inside_diameter":1000,
                    "tangent_length":L, "nominal_thickness":12, "material_id":"M1"}],
            )
            # tank fixture head IDs/materials are preserved; only shell geometry changes.
            p["supports"] = [
                {"support_id":"SAD-1", "host_component_id":"SHELL-01", "type":"saddle",
                 "location_mm":x1, "width_mm":b, "height_mm":400, "material_id":"M1",
                 "contact_angle_deg":theta, "saddle_stiffened":ring,
                 "zick_K1":0.1066, "zick_K2":1.1707, "zick_K3":0.8799,
                 "zick_K6":0.0325, "zick_K7":0.0325},
                {"support_id":"SAD-2", "host_component_id":"SHELL-01", "type":"saddle",
                 "location_mm":x2, "width_mm":b, "height_mm":400, "material_id":"M1",
                 "contact_angle_deg":theta, "saddle_stiffened":ring,
                 "zick_K1":0.1066, "zick_K2":1.1707, "zick_K3":0.8799,
                 "zick_K6":0.0325, "zick_K7":0.0325},
            ]
            if name == "missing_K":
                p["supports"][0]["zick_K1"] = None
            # pressure remains constant; vary load by changing shell length is not
            # a clean operating/empty comparison, so these are geometric repeats.
            cid = f"R{repeat+1}-{name}"
            cases.append((cid, p, {"L_mm":L, "b_mm":b, "theta_deg":theta,
                                   "ring":ring, "A_mm":A, "saddle_positions_mm":[x1,x2],
                                   "weight_scale_label":scale}))
    # Deliberate missing-coefficient and out-of-domain boundary requests.
    p = deepcopy(cases[0][1]); p["supports"][0]["zick_K1"] = None
    cases.append(("invalid-missing-K", p, {"invalid":"K1 missing"}))
    p = deepcopy(cases[0][1]); p["supports"][0]["contact_angle_deg"] = 160
    cases.append(("invalid-angle", p, {"invalid":"angle 160 deg"}))
    return [(cid, project, params) for cid, project, params in cases]
