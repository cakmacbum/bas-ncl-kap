"""Run F10 through the calculation API and compare available geometry outputs."""
from __future__ import annotations
from pathlib import Path
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import run_case, find_results
from tools.campaign.families.f10_nozul_yerlesim.variants import variants
from tools.campaign.families.f10_nozul_yerlesim.oracle import shell_location

FAMILY = "F10-nozul_yerlesim"


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        nozzle = project["nozzles"][0]
        shell = project["shell_sections"][0]
        radius = float(shell["inside_diameter"]) / 2
        location = shell_location(radius, float(nozzle["axial_position"]), float(nozzle["circumferential_angle"]))
        matches = find_results(payload, component_id=nozzle["tag"], calculation_type="clash_check")
        result = matches[0] if matches else None
        status = (result or {}).get("status")
        # The catalog's clash contract exposes a text PASS/REVIEW/FAIL marker for
        # single-nozzle cases, not a numeric placement coordinate or distance.
        marker = next((v.get("value") for v in (result or {}).get("intermediate_values", [])
                       if v.get("name") == "nozzle_nozzle_clash"), None)
        suite = None
        oracle = None
        diff, verdict = judge(suite, oracle, suite_status="NOT CALCULATED")
        rows.append(CaseResult(case_id, FAMILY, {"host": nozzle["host_component_id"],
            "z_mm": nozzle["axial_position"], "theta_deg": nozzle["circumferential_angle"],
            "outside_diameter_mm": nozzle["outside_diameter"], "oracle_location": location,
            "api_ok": outcome["ok"], "api_http_status": outcome["http_status"],
            "api_errors": outcome.get("error"), "clash_marker": marker}, "clash_check", "mm", suite,
            oracle, "catalog clash_check", diff, verdict,
            "Catalog row emitted, but placement/distance is absent; categorical marker is not numeric comparison.", status))
    write_results(Path(__file__).parent, FAMILY, rows, {"code": "API calculation route",
        "oracle": "x=R cos(theta), y=R sin(theta), z=axial position; single-nozzle clash oracle PASS"})


if __name__ == "__main__":
    run()
