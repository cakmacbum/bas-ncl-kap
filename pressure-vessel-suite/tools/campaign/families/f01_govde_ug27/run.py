"""Run F01 against the public calculation API and write family results."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f01_govde_ug27.oracle import calculate
from tools.campaign.families.f01_govde_ug27.variants import variants

FAMILY = "F01-govde-ug27"
OUT = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, component_id="SHELL-01", clause_prefix="UG-27")
        thickness_result = next((r for r in matches if r.get("calculation_type") == "thickness"), None)
        mawp_result = next((r for r in matches if r.get("calculation_type") == "mawp"), None)
        expected = calculate(project)
        # API failures or missing material are recorded as blocked/out of scope.
        if not outcome.get("ok") or thickness_result is None:
            suite_status = "BLOCKED MISSING INPUT"
        else:
            suite_status = thickness_result.get("status")
        mapping = (("required_thickness", "required_thickness", "mm"),
                   ("mawp", "mawp", "MPa"), ("used_radius", "used_radius", "mm"))
        for quantity, oracle_key, unit in mapping:
            reference = expected.get(oracle_key)
            suite = None
            if thickness_result and quantity == "required_thickness":
                suite = value_of(thickness_result, "t_required")
            elif mawp_result and quantity == "mawp":
                suite = value_of(mawp_result, "MAWP")
            elif thickness_result and quantity == "used_radius":
                suite = value_of(thickness_result, "R_corroded") or value_of(thickness_result, "R")
            diff, verdict = judge(suite, reference, suite_status=suite_status)
            rows.append(CaseResult(f"{case_id}:{quantity}", FAMILY,
                                   {"project": project["project_number"], "pressure_mpa": project["design_conditions"]["design_pressure"]},
                                   quantity, unit, suite, reference, "oracle", diff, verdict,
                                   "API result missing or case intentionally invalid" if verdict == "KAPSAM_DIŞI" else "",
                                   suite_status))
    # Published K1 cylinder values are retained as distinct sourced records.
    # Input/output pairs are in the publication's original units; these are audit
    # anchors and are not silently converted into synthetic API test cases.
    published = [
        ("K1-16", "PVEng PVE-6847, pp.15-16; App.1-1(a)(1) outer-radius alternate; 0.2437 in", "required_thickness", .2437, "in"),
        ("K1-18", "PVEng PVE-3247, p.2; UG-27(c)(1), CA case; 0.127 in", "required_thickness", .127, "in"),
    ]
    for case_id, source, quantity, value, unit in published:
        rows.append(CaseResult(case_id, FAMILY, {"published_anchor": True}, quantity, unit,
                               None, value, source, None, "TEK_KAYNAK",
                               "Published anchor recorded; no matching independently runnable source case."))
    write_results(OUT, FAMILY, rows, {"code": "ASME VIII-1", "oracle": "UG-27(c)(1), clean-room arithmetic"})


if __name__ == "__main__":
    run()
