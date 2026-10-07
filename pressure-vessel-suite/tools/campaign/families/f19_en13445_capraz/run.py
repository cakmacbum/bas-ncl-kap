from pathlib import Path
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f19_en13445_capraz.variants import variants
from tools.campaign.families.f19_en13445_capraz.oracle import en_shell
from tools.campaign.harness import run_case, find_results, value_of
FAMILY = "F19-en13445_capraz"
def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project); payload = outcome.get("payload") or {}; code = project["calculation_code"]
        matches = find_results(payload, component_id="SHELL-01")
        result = next((r for r in matches if r.get("calculation_type") == "thickness"), matches[0] if matches else None)
        suite = value_of(result, "e_required") if result else None
        dc=project["design_conditions"]; mat=project["materials"][0]; z=project["welds"][0]["joint_efficiency"]
        oracle,f=(en_shell(dc["design_pressure"],project["shell_sections"][0]["inside_diameter"] + 2*dc.get("corrosion_allowance_internal",0),mat["allowable_stress"],mat["allowable_stress"]*2.4,z) if mat.get("yield_strength") and mat.get("tensile_strength") else (None,None))
        status=result.get("status") if result else ("BLOCKED MISSING INPUT" if not outcome.get("ok") else None)
        diff,verdict=judge(suite,oracle,suite_status=status,formulation_note="EN/ASME form differs" if code.startswith("ASME") else None)
        rows.append(CaseResult(case_id,FAMILY,{"code":code,"P_MPa":dc.get("design_pressure"),"z":z,"Di_mm":project["shell_sections"][0]["inside_diameter"],"f_EN_MPa":f},"shell_required_thickness","mm",suite,oracle,"oracle: EN 13445-3 7.4.2",diff,verdict,note=str(outcome.get("error") or ""),suite_status=status))
    write_results(Path(__file__).parent,FAMILY,rows,{"standard":"EN 13445-3 / ASME VIII-1","oracle":"independent equations in oracle.py","case_count":len(rows)})
if __name__ == "__main__": run()


