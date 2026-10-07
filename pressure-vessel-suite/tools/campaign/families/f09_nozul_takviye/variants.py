"""F09 nozul takviyesi varyantları."""
from tools.campaign.bases import vertical_leg_tank
from tools.campaign.examples import example_nozzle_reinforcement


def variants():
    cases = []
    for ratio in (0.05, 0.1, 0.2, 0.35, 0.5):
        for pad in (False, True):
            p = example_nozzle_reinforcement()
            nz = p["nozzles"][0]
            d = 500.0 * ratio
            nz.update(outside_diameter=d + 2 * 8.0, inside_diameter=d, neck_thickness=8.0,
                      outside_projection=30.0, reinforcement_pad=pad,
                      reinforcement_pad_thickness=8.0 if pad else None,
                      reinforcement_pad_od=d + 100.0 if pad else None)
            cases.append((f"ratio-{ratio:g}-pad-{int(pad)}", p))
    for i, typ in enumerate(("flanged", "slip_on", "socket_weld", "threaded", "manway")):
        p = example_nozzle_reinforcement(); p["nozzles"][0]["nozzle_type"] = typ
        p["nozzles"][0]["outside_projection"] = 10.0 * i
        cases.append((f"type-{typ}", p))
    for e in (0.7, 0.85, 1.0):
        p = example_nozzle_reinforcement()
        for m in p["materials"]:
            if m["material_id"] == "M1": m["weld_joint_efficiency"] = e
        cases.append((f"eff-{e}", p))
    for t in (4.0, 8.0, 15.0):
        p = example_nozzle_reinforcement(); p["nozzles"][0]["neck_thickness"] = t
        p["nozzles"][0]["inside_diameter"] = p["nozzles"][0]["outside_diameter"] - 2*t
        cases.append((f"neck-{t:g}", p))
    for od in (100.0, 250.0, 600.0):
        p = example_nozzle_reinforcement(); n=p["nozzles"][0]; n.update(reinforcement_pad=True, reinforcement_pad_thickness=8.0, reinforcement_pad_od=od)
        cases.append((f"pad-od-{od:g}",p))
    # Published checks: inputs are SI equivalents; tr values are retained as reported inputs where noted.
    p=example_nozzle_reinforcement(); p["shell_sections"][0].update(inside_diameter=314.198, nominal_thickness=4.775)
    p["nozzles"][0].update(outside_diameter=55.677, inside_diameter=47.498, neck_thickness=4.089, outside_projection=38.1)
    cases.append(("PUB-K2-02-PVE-S5",p))
    p=example_nozzle_reinforcement(); p["nozzles"][0].update(outside_diameter=457.2,inside_diameter=428.65,neck_thickness=14.275,
            reinforcement_pad=True,reinforcement_pad_thickness=6,reinforcement_pad_od=600)
    cases.append(("PUB-K2-17-IJERT",p))
    for name, projection in (("proj-0",0),("proj-10",10),("proj-100",100),("proj-250",250),("proj-500",500),("proj-1000",1000)):
        p=example_nozzle_reinforcement(); p["nozzles"][0]["outside_projection"]=projection
        cases.append((name,p))
    return cases

