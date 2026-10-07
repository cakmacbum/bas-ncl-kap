"""Execute F18 through the API and compare available result quantities."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f18_ruzgar_deprem.variants import variants
from tools.campaign.harness import run_case, find_results, value_of

FAMILY = "F18-ruzgar-deprem"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        # API rows are the only suite source. Current endpoint may not expose load checks.
        matches = find_results(payload, calculation_type="wind") + find_results(payload, calculation_type="seismic")
        result = matches[0] if matches else None
        suite = value_of(result, "base_shear") if result else None
        reference = None
        diff, verdict = judge(suite, reference, suite_status=(result or {}).get("status"))
        note = "No wind/seismic result row in API payload" if not result else "Oracle inputs need independent weight/drag inputs"
        rows.append(CaseResult(case_id, FAMILY, params, "base_shear", "N", suite, reference,
            "independent elementary equations; no complete matching case", diff, verdict, note,
            (result or {}).get("status")))

    # K3-19 published wind case: retain published total as a separately attributed record.
    rows.append(CaseResult("K3-19-PUBLISHED", FAMILY,
        {"source_case": "ASCE Petrochemical Wind Loads §6.4", "published_simple_base_shear_lb": 82496,
         "published_detailed_base_shear_lb": 58868, "wind_speed_mph": 120},
        "base_shear", "lb", None, 58868.0,
        "K3-19; ASCE Petrochemical Committee (2011), §6.4, pp.140-149", None,
        "TEK_KAYNAK", "Published detailed-method total; API has no matching method/result."))
    write_results(HERE, FAMILY, rows, {"code": "elementary wind/seismic screening", "oracle": "F18 clean-room equations"})


if __name__ == "__main__":
    run()
