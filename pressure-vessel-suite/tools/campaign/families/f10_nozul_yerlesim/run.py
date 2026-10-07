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
        matches = find_results(payload, component_id=nozzle["tag"])
        result = matches[0] if matches else None
        status = (result or {}).get("status")
        # API currently has no placement/interference result row; retain oracle location,
        # and classify unavailable comparison as out of scope.
        suite = None
        diff, verdict = judge(suite, None, suite_status="NOT CALCULATED")
        rows.append(CaseResult(case_id, FAMILY, {"host": nozzle["host_component_id"],
            "z_mm": nozzle["axial_position"], "theta_deg": nozzle["circumferential_angle"],
            "outside_diameter_mm": nozzle["outside_diameter"], "oracle_location": location,
            "api_ok": outcome["ok"], "api_http_status": outcome["http_status"],
            "api_errors": outcome.get("error")}, "position_and_interference", "mixed", suite,
            None, "independent cylindrical geometry", diff, verdict,
            "API output has no nozzle placement/interference quantity; no numeric comparison.", status))
    write_results(Path(__file__).parent, FAMILY, rows, {"code": "API calculation route",
        "oracle": "x=R cos(theta), y=R sin(theta), z=axial position; geometric comparison unavailable"})


if __name__ == "__main__":
    run()
