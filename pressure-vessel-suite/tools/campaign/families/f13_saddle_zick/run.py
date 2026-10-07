"""Run the F13 saddle campaign through the public calculation API."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f13_saddle_zick.variants import variants

FAMILY = "F13-saddle_zick"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        match = next(iter(find_results(payload, component_id="SHELL-01",
                                      calculation_type="saddle_stress")), None)
        for quantity in ("S1_saddle", "S1_midspan", "S3_shell", "S4"):
            suite = value_of(match, quantity) if match else None
            # No K-table lookup is embedded. For non-published cases the oracle
            # cannot claim an independent reaction without a source load set.
            ref = None
            status = (match or {}).get("status")
            diff, verdict = judge(suite, ref, suite_status=status)
            rows.append(CaseResult(case_id, FAMILY, params, quantity, "MPa", suite,
                                   ref, "K3-01: PVE-4293 (published subset only)",
                                   diff, verdict, note="Independent reaction/load not published for this variant.",
                                   suite_status=status))
    write_results(HERE, FAMILY, rows, {"code":"Zick 1951 / ASME VIII-2 4.15 mapping",
        "oracle":"F13-local equations; external K values not tabulated",
        "api_ok_cases":sum(1 for _ in variants())})


if __name__ == "__main__":
    run()
