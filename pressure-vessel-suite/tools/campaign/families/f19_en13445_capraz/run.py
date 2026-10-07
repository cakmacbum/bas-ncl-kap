from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f19_en13445_capraz.variants import variants
from tools.campaign.families.f19_en13445_capraz.oracle import en_shell, asme_shell
from tools.campaign.harness import run_case, find_results, value_of

FAMILY = "F19-en13445_capraz"


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        code = project["calculation_code"]
        result = next(iter(find_results(payload, component_id="SHELL-01",
                                        calculation_type="thickness")), None)
        mat = project["materials"][0]
        dc = project["design_conditions"]
        shell = project["shell_sections"][0]
        weld = next((w for w in project["welds"] if w.get("component_id") == "SHELL-01" or
                     w.get("joint_id") == "W-SHELL-01"), project["welds"][0])
        p = dc.get("design_pressure")
        radius = shell["inside_diameter"] / 2
        is_en = code == "EN 13445"
        suite_name = "e_required" if is_en else "t_required"
        suite = value_of(result, suite_name) if result else None
        # Use the API's reported governing inputs (the project's first weld can
        # belong to another component, so it is not necessarily this shell's E).
        allowable = value_of(result, "f" if is_en else "S") if result else mat.get("allowable_stress")
        efficiency = value_of(result, "z" if is_en else "E") if result else weld["joint_efficiency"]
        reference = (en_shell(p, radius, allowable, efficiency) if is_en else
                     asme_shell(p, radius, allowable, efficiency)) if p and allowable else None
        status = result.get("status") if result else (
            "BLOCKED MISSING INPUT" if not outcome.get("ok") else None)
        diff, verdict = judge(suite, reference, suite_status=status)
        rows.append(CaseResult(
            case_id, FAMILY,
            {"code": code, "P_MPa": p, "z_or_E": efficiency,
             "inside_radius_mm": radius, "allowable_MPa": allowable},
            "shell_required_thickness", "mm", suite, reference,
            "oracle: EN 13445-3 7.4.2" if is_en else "oracle: ASME VIII-1 UG-27(c)(1)",
            diff, verdict, note=str(outcome.get("error") or ""), suite_status=status))
    write_results(Path(__file__).parent, FAMILY, rows,
                  {"standard": "EN 13445-3 / ASME VIII-1",
                   "oracle": "independent equations in oracle.py",
                   "case_count": len(rows)})


if __name__ == "__main__":
    run()
