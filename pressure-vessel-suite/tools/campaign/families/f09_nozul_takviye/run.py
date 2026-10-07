"""API karşılaştırması ve sonuç üretimi."""
from pathlib import Path
from tools.campaign.families.f09_nozul_takviye.variants import variants
from tools.campaign.families.f09_nozul_takviye.oracle import calculate
from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results

FAMILY = "F09-nozul-takviye"

def run():
    rows=[]
    for case_id, project in variants():
        outcome=run_case(project)
        payload=outcome.get("payload") or {}
        candidates=find_results(payload, calculation_type="nozzle_reinforcement")
        row=candidates[0] if candidates else None
        status=(row or {}).get("status")
        suite=value_of(row or {}, "A_required")
        n=project["nozzles"][0]
        # Oracle uses explicit conservative material value; tr-area comparisons are input-normalized.
        ref=calculate(d=n["inside_diameter"],host_d=project["shell_sections"][0]["inside_diameter"],t=project["shell_sections"][0]["nominal_thickness"],tn=n["neck_thickness"],
                      pressure=project["design_conditions"]["design_pressure"],allowable=138.0,
                      pad_od=n.get("reinforcement_pad_od") or 0,pad_t=n.get("reinforcement_pad_thickness") or 0,
                      projection=n.get("outside_projection",0))
        diff, verdict=judge(suite,ref["A"],suite_status=status)
        rows.append(CaseResult(case_id,FAMILY,{"nozzle":n,"host":"shell"},"A_required","mm2",suite,ref["A"],"UG-37(c) independent",diff,verdict,
                               note=f"independent={ref}; API ok={outcome.get('ok')} error={outcome.get('error')}",suite_status=status))
    write_results(Path(__file__).parent,FAMILY,rows,{"code":"ASME VIII-1","oracle":"UG-37(c), UG-40, UG-45","calculation_type":"nozzle_reinforcement","intermediate_value":"A_required"})

if __name__ == "__main__": run()
