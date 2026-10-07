"""Reproduce F07 global MAWP and static-head comparisons."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case
from tools.campaign.families.f07_mawp_statik_kafa.oracle import oracle
from tools.campaign.families.f07_mawp_statik_kafa.variants import variants

FAMILY = "F07-mawp_statik_kafa"


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        suite = payload.get("global_mawp_mpa")
        mawp_rows = find_results(payload, calculation_type="mawp")
        governing = min(mawp_rows, key=lambda r: float(r.get("final_result") or float("inf")), default=None)
        status = (governing or {}).get("status")
        reference, oracle_governing, source = oracle(project, case_id)
        diff, verdict = judge(suite, reference, suite_status=status or ("BLOCKED MISSING INPUT" if not outcome["ok"] else None))
        note = f"suite_governing={(governing or {}).get('component_id')}; oracle_governing={oracle_governing}; "
        if case_id.startswith("PUB-"):
            verdict = "TEK_KAYNAK" if suite is not None else verdict
            note += "K1-01 yayınlanmış silindir MAWP; statik kafa bileşen hesabı ayrı doğrulama gerektirir. "
        note += source
        rows.append(CaseResult(case_id, FAMILY,
            {"orientation": project.get("orientation"), "density_kg_m3": project["design_conditions"].get("fluid_density_kg_m3"),
             "design_pressure_mpa": project["design_conditions"].get("design_pressure")},
            "global_mawp", "MPa", suite, reference, source, diff, verdict, note, status))
    return write_results(Path(__file__).parent, FAMILY, rows,
                         {"code": "ASME VIII-1", "oracle": "UG-27(c)(1), UG-32(d), hydrostatic rho*g*h; clean-room"})


if __name__ == "__main__":
    print(run())
