"""Reproduce the F20 API campaign from the suite root."""
from pathlib import Path
from tools.campaign.harness import run_case
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f20_uctan_uca.variants import variants
from tools.campaign.families.f20_uctan_uca.oracle import inner_volume_m3

FAMILY = "F20-uctan_uca"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        out = run_case(project)
        payload = out.get("payload") or {}
        ref = inner_volume_m3(project)
        suite = (payload.get("volume_mass") or {}).get("inner_volume_m3")
        status = None
        if not out.get("ok"):
            status = "BLOCKED MISSING INPUT" if out.get("http_status") in (400, 422) else "NOT CALCULATED"
        # Published values are attached only to cases matching documented head/shell equations.
        source = "clean-room geometric integral"
        diff, verdict = judge(suite, ref, suite_status=status,
                              formulation_note="head geometry approximation" if case_id.startswith("head-") else None)
        if case_id.startswith("three-nozzles-") or case_id in {"en-code", "external-pressure", "mdmt", "wind-load"}:
            verdict = "TEK_KAYNAK" if suite is not None else verdict
        rows.append(CaseResult(case_id, FAMILY, {"code": project["calculation_code"], "ok": out.get("ok"),
            "errors": payload.get("errors", out.get("error")), "volume_m3": suite,
            "report_html": None, "step": None}, "inner_volume", "m3", suite, ref, source, diff, verdict,
            "Nozzle and load cases exercise end-to-end API path; volume oracle omits those fittings.", status))
    write_results(HERE, FAMILY, rows, {"basis":"cylindrical shell + analytical head volume", "published_cases":"K1 review pending exact matches"})


if __name__ == "__main__":
    run()
