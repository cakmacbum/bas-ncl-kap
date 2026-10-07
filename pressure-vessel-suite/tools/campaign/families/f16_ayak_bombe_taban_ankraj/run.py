from pathlib import Path
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from .oracle import oracle
from .variants import variants

FAMILY = "F16-ayak-bombe-taban-ankraj"


def run():
    rows = []
    for case_id, project in variants():
        support = project["supports"][0]
        L = support.get("base_plate_length_mm") or 250
        W = support.get("base_plate_width_mm") or 200
        Fy = support.get("base_plate_yield_MPa") or 250
        fc = support.get("foundation_bearing_allowable_MPa") or 10
        n = support.get("anchor_bolt_count") or 4
        moment = support.get("overturning_moment_Nmm", 0)
        shear = support.get("lateral_load_N", 0)
        # Suite uses total vessel/support reaction; oracle's load basis is explicitly recorded.
        load = 26105.13660507276
        ref = oracle({"L":L,"W":W,"Fy":Fy,"fc":fc,"P":load,"M":moment,"V":shear,"n":n,"Dbc":150})
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, component_id="LEGS")
        for quantity, unit, result_name in (("required_thickness","mm","required_plate_thickness"),
                                             ("concrete_pressure","MPa","concrete_bearing_pressure"),
                                             ("anchor_tension","N","anchor_tension_per_bolt"),
                                             ("anchor_shear","N","anchor_shear_per_bolt")):
            result = next((r for r in matches if r.get("calculation_type")=="base_plate_check"), None)
            suite = value_of(result, result_name) if result else None
            status = result.get("status") if result else "BLOCKED MISSING INPUT"
            diff, verdict = judge(suite, ref[quantity], suite_status=status)
            params = {"L_mm":L,"W_mm":W,"t_mm":support.get("base_plate_thickness_mm"),"Fy_MPa":Fy,
                      "fc_allow_MPa":fc,"anchors":support.get("anchor_bolt_count"),"moment_Nmm":moment,"shear_N":shear}
            source = "K3-15..18 AISC DG1 (cases are external checks; see report)" if case_id in {"GRID-01","GRID-05","GRID-06","GRID-07"} else "independent oracle"
            rows.append(CaseResult(case_id, FAMILY, params, quantity, unit, suite, ref[quantity], source,
                                   diff, verdict, note=outcome.get("error") or "API calculation row unavailable or field not exposed",
                                   suite_status=status))
    write_results(Path(__file__).parent, FAMILY, rows, {"basis":"API output compared to family-local equations", "cases":len(variants())})


if __name__ == "__main__":
    run()
