"""T12 cases based only on project-supplied material records."""
from tools.campaign.examples import example_mdmt_check


def cases():
    project = example_mdmt_check()
    out = []
    for mat in project["materials"]:
        mid = mat["material_id"]
        points = mat.get("allowable_stress_temperature_points", [])
        if not points:
            for behavior in ("monotonic", "outside-low", "outside-high", "linear", "boundary", "range", "midpoint", "endpoint-low", "endpoint-high"):
                out.append({"id": f"{mid}-temperature-{behavior}", "material": mid,
                            "kind": "temperature", "behavior": behavior})
        else:
            points = sorted((float(t), float(v)) for t, v in points)
            for i in range(1, len(points)):
                out.append({"id": f"{mid}-mono-{i}", "material": mid,
                            "kind": "monotonic", "points": points})
            for i, (t, v) in enumerate(points):
                out.append({"id": f"{mid}-boundary-{i}", "material": mid,
                            "kind": "boundary", "points": points, "temperature": t, "expected": v})
                if i + 1 < len(points):
                    t2, v2 = points[i+1]
                    out.append({"id": f"{mid}-linear-{i}", "material": mid,
                                "kind": "linear", "points": points, "temperature": (t+t2)/2,
                                "expected": (v+v2)/2})
            for t in (points[0][0]-1, points[-1][0]+1):
                out.append({"id": f"{mid}-outside-{t}", "material": mid,
                            "kind": "outside", "points": points, "temperature": t})
        out.append({"id": f"{mid}-thickness-limits", "material": mid, "kind": "thickness",
                    "minimum": mat.get("thickness_min", 0), "maximum": mat.get("thickness_max", 999)})
    return out
