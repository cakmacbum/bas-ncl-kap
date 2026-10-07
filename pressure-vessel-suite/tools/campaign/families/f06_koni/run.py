from pathlib import Path
from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results
from .variants import variants
from .oracle import required_thickness, mawp

FAMILY = "F06-koni"


def run():
    rows=[]
    for case_id, project in variants():
        outcome=run_case(project)
        payload=outcome.get("payload") or {}
        cone=find_results(payload, component_id="CONE-01")
        angle=project["cones"][0]["half_apex_angle"]
        pressure=project["design_conditions"]["design_pressure"]
        dia=project["cones"][0]["large_diameter"]
        material=next(m for m in project["materials"] if m["material_id"]=="M1")
        stress=material["allowable_stress"]
        thickness=project["cones"][0]["nominal_thickness"]
        ref=required_thickness(pressure,dia,angle,stress,1.0)/0.875
        result=next((r for r in cone if "UG-32" in str(r.get("clause_reference","")) or "1-4" in str(r.get("clause_reference",""))),None)
        suite=value_of(result,"t_nominal_required") if result else None
        if suite is None and result: suite=value_of(result,"final_result")
        status=(result or {}).get("status")
        diff,verdict=judge(suite,ref,suite_status=status,formulation_note="UG-32(g) ic cap")
        rows.append(CaseResult(case_id,FAMILY,{"angle_deg":angle,"pressure_mpa":pressure,"large_diameter_mm":dia,"small_diameter_mm":project["cones"][0]["small_diameter"],"ca_mm":project["cones"][0]["internal_corrosion_allowance"]},"required_thickness","mm",suite,ref,"oracle",diff,verdict,"UG-32(g); koni MAWP oracle: %.6g MPa; App 1-5 Q/area oracle unavailable."%mawp(thickness,dia,angle,stress,1.0),status))
        mawp_row=next((r for r in find_results(payload,component_id="CONE-01",calculation_type="mawp") if "UG-32(g)" in str(r.get("clause_reference",""))),None)
        suite_mawp=value_of(mawp_row,"mawp") if mawp_row else None
        if suite_mawp is None and mawp_row: suite_mawp=value_of(mawp_row,"final_result")
        ref_mawp=mawp(thickness,dia,angle,stress,1.0)
        mdiff,mverdict=judge(suite_mawp,ref_mawp,suite_status=(mawp_row or {}).get("status"),formulation_note="UG-32(g) ic cap")
        rows.append(CaseResult(case_id+"-MAWP",FAMILY,{"angle_deg":angle,"pressure_mpa":pressure,"large_diameter_mm":dia},"mawp","MPa",suite_mawp,ref_mawp,"oracle",mdiff,mverdict,"Nominal thickness based UG-32(g) pressure inversion.",(mawp_row or {}).get("status")))
        # Bağlantı takviyesi API çıktısı ayrı kayıt: bağımsız App 1-5 değer seti bulunmadığından kaynak bekliyor.
        rows.append(CaseResult(case_id+"-APP15",FAMILY,{"angle_deg":angle,"junction":"large"},"reinforcement_area","mm2",None,None,"",None,"KAPSAM_DIŞI","Junction API status BLOCKED MISSING INPUT; K2-18 Bednar gerilmesidir, App. 1-5 alan vakası değildir.","BLOCKED MISSING INPUT"))
    write_results(Path(__file__).parent,FAMILY,rows,{"code":"ASME VIII-1","oracle":"UG-32(g) independent; Appendix 1-5 external published reference missing"})


if __name__ == "__main__": run()
