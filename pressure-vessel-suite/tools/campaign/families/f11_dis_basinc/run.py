from __future__ import annotations

from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f11_dis_basinc.oracle import shell_allowable_pressure
from tools.campaign.families.f11_dis_basinc.variants import variants

FAMILY = "F11-dis_basinc"
K2 = "sources-K2.md §K2-16, PVE Firetube (2017), pp.24–26"


def run():
    rows = []
    for case_id, project in variants():
        shell = project["shell_sections"][0]
        do = shell["outside_diameter"]
        t = shell["nominal_thickness"]
        b = shell["ug28_allowable_stress_b"]
        ref = shell_allowable_pressure(b, do, t)
        out = run_case(project)
        matches = find_results(out.get("payload") or {}, component_id="SHELL-01",
                               calculation_type="external_pressure", clause_prefix="UG-28")
        result = matches[0] if matches else None
        suite = value_of(result, "P_allow") if result else None
        diff, verdict = judge(suite, ref, suite_status=(result or {}).get("status"))
        note = "A kullanıcı girdisi; bağımsız grafik okunmadı." \
            if result else (out.get("error") or "UG-28 API sonucu yok")
        rows.append(CaseResult(case_id, FAMILY, {
            "Do_mm": do, "t_mm": t, "L_over_Do": shell["tangent_length"] / do,
            "Do_over_t": do / t, "A_user": shell["ug28_strain_factor_a"],
            "B_MPa": b, "external_pressure_MPa": project["design_conditions"]["external_pressure"]},
            "Pa", "MPa", suite, ref, "UG-28(c)(1) bağımsız denklem", diff, verdict,
            note, (result or {}).get("status")))
    write_results(Path(__file__).parent, FAMILY, rows, {"code": "ASME VIII-1", "oracle": "UG-28(c)(1)"})
    return rows


if __name__ == "__main__":
    run()
