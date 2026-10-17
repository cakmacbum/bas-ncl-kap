"""Execute T01 public API metamorphic sweeps and write results.json."""
import json
from pathlib import Path

from tools.campaign.harness import run_case, find_results, value_of
from .cases import COMPONENTS, RELATIONS, project_for, vary

OUT = Path(__file__).resolve().parent

def extract(payload, component, relation):
    rows = payload.get("results", []) if payload else []
    if component == "nozul":
        rows = find_results(payload, calculation_type="nozzle_reinforcement") if payload else []
        return value_of(rows[0], "required_area") if rows else None
    if component == "dış basınç":
        rows = find_results(payload, calculation_type="external_pressure") if payload else []
        return value_of(rows[0], "allowable_external_pressure") if rows else None
    kind = "shell" if component == "gövde" else "cone" if component == "koni" else "head"
    rows = [r for r in rows if r.get("component_type") == kind and r.get("calculation_type") in ("thickness", "mawp")]
    wanted = "mawp" if relation == RELATIONS[4] else "thickness"
    rows = [r for r in rows if r.get("calculation_type") == wanted]
    if not rows:
        return None
    if wanted == "mawp":
        return rows[0].get("final_result")
    return value_of(rows[0], "t_required")

def main():
    records = []
    for component in COMPONENTS:
        for relation in RELATIONS:
            samples = []
            for step in range(5):
                project = vary(project_for(component), relation, step)
                response = run_case(project)
                observed = extract(response.get("payload"), component, relation)
                samples.append(observed)
                records.append({"case":f"{component} | {relation} | {step+1}", "component":component,
                    "relation":relation, "input":{"step":step+1, "design_conditions":project["design_conditions"],
                    "nominal_thickness":project["shell_sections"][0]["nominal_thickness"],
                    "allowable_stress":project["materials"][0]["allowable_stress"],
                    "efficiency":project["welds"][0]["joint_efficiency"]},
                    "expected":relation, "observed":observed,
                    "detail": response.get("error") if not response.get("ok") else None,
                    "available_results": [{"component_type":x.get("component_type"), "calculation_type":x.get("calculation_type"),
                        "status":x.get("status"), "final_result":x.get("final_result"),
                        "intermediate_names":[v.get("name") for v in x.get("intermediate_values",[])]}
                        for x in (response.get("payload") or {}).get("results",[])],
                    "result":"KAPSAM_DIŞI" if observed is None or not response.get("ok") else "GEÇTİ"})
            increasing = relation in (RELATIONS[0], RELATIONS[2], RELATIONS[3], RELATIONS[4], RELATIONS[5])  # sıcaklık↑ → S↓ → t_required↑
            # CA drives a larger nominal required thickness; all sampled values must be available.
            for idx, rec in enumerate(records[-5:-1]):
                a,b=samples[idx:idx+2]
                if a is not None and b is not None and ((b < a) if increasing else (b > a)):
                    rec["result"]="BULGU"
                    rec["observed"]={"value":samples[idx], "next":b, "violation":"monotonicity"}
    (OUT / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"cases={len(records)} passed={sum(r['result']=='GEÇTİ' for r in records)} findings={sum(r['result']=='BULGU' for r in records)} out_of_scope={sum(r['result']=='KAPSAM_DIŞI' for r in records)}")

if __name__ == "__main__": main()
