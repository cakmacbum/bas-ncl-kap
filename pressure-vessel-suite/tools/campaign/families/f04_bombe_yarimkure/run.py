from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f04_bombe_yarimkure.oracle import values
from tools.campaign.families.f04_bombe_yarimkure.variants import variants

FAMILY = "F04-bombe-yarimkure"
OUT = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        source = ("K1-12 PVEcalc-4225-0-1, sphere segment" if case_id.startswith("K1-12") else
                  "K1-13 PVEcalc-4225-0-1, sphere segment" if case_id.startswith("K1-13") else
                  "UG-32(f) independent oracle")
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        thickness_rows = find_results(payload, component_id="HEAD-L", calculation_type="thickness",
                                      clause_prefix="UG-32")
        mawp_rows = find_results(payload, component_id="HEAD-L", calculation_type="mawp",
                                  clause_prefix="UG-32")
        result = thickness_rows[0] if thickness_rows else None
        ref_t, ref_p = values(project)
        if result is None:
            # Invalid input is expected to be rejected before calculation.
            blocked = "BLOCKED MISSING INPUT" if not outcome.get("ok") else "NOT CALCULATED"
            for quantity, reference, unit in (("required_thickness", ref_t, "mm"), ("mawp", ref_p, "MPa")):
                diff, verdict = judge(None, reference, suite_status=blocked)
                rows.append(CaseResult(case_id, FAMILY, {"design_pressure": project["design_conditions"]["design_pressure"]},
                                       quantity, unit, None, reference, source, diff, verdict,
                                       note=outcome.get("error") or "No UG-32 head result", suite_status=blocked))
            continue
        suite_t = value_of(result, "final_result")
        pressure_result = mawp_rows[0] if mawp_rows else None
        suite_p = value_of(pressure_result, "final_result") if pressure_result else None
        status = result.get("status")
        for quantity, suite, reference, unit in (("required_thickness", suite_t, ref_t, "mm"),
                                                  ("mawp", suite_p, ref_p, "MPa")):
            diff, verdict = judge(suite, reference, suite_status=status)
            rows.append(CaseResult(case_id, FAMILY, {"diameter": project["heads"][0]["inside_diameter"],
                                   "pressure": project["design_conditions"]["design_pressure"],
                                   "ca": project["heads"][0]["internal_corrosion_allowance"]},
                                   quantity, unit, suite, reference, source, diff, verdict,
                                   suite_status=status))
    write_results(OUT, FAMILY, rows, {"code": "ASME VIII-1", "clause": "UG-32(f)"})


if __name__ == "__main__":
    run()
