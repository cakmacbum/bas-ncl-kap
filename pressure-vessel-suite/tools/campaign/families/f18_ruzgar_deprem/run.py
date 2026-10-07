"""Execute catalog-backed wind/seismic load-case comparisons through the API."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f18_ruzgar_deprem.oracle import load_case_oracle
from tools.campaign.families.f18_ruzgar_deprem.variants import variants
from tools.campaign.harness import run_case, find_results, value_of

FAMILY = "F18-ruzgar-deprem"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, calculation_type="global_load_case")
        result = matches[0] if matches else None
        status = (result or {}).get("status")
        for quantity, unit, key in (
            ("resultant_shear", "N", "resultant_shear"),
            ("overturning_moment", "N-mm", "overturning_moment"),
        ):
            reference = load_case_oracle(params, key)
            suite = value_of(result, key) if result else None
            diff, verdict = judge(suite, reference, suite_status=status)
            rows.append(CaseResult(
                f"{case_id}-{quantity.upper()}", FAMILY, params, quantity, unit,
                suite, reference, "F18 clean-room: explicit applied force/moment components",
                diff, verdict,
                "Catalog global_load_case numeric resultant; load intensity itself is not calculated."
                if result else "No global_load_case row in API payload.", status,
            ))

    rows.append(CaseResult("K3-19-PUBLISHED", FAMILY,
        {"source_case": "ASCE Petrochemical Wind Loads §6.4", "published_simple_base_shear_lb": 82496,
         "published_detailed_base_shear_lb": 58868, "wind_speed_mph": 120},
        "base_shear", "lb", None, 58868.0,
        "K3-19; ASCE Petrochemical Committee (2011), §6.4, pp.140-149", None,
        "TEK_KAYNAK", "Published detailed-method total; suite global load case cannot reproduce ASCE method."))
    write_results(HERE, FAMILY, rows, {
        "code": "catalog global_load_case applied load resultant",
        "oracle": "independent direct component sums; no plugin equations",
    })


if __name__ == "__main__":
    run()
