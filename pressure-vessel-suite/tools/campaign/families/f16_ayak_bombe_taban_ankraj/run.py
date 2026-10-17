from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from .oracle import oracle
from .variants import variants

FAMILY = "F16-ayak-bombe-taban-ankraj"
REACTION_N = 6526.28415126819  # Resolved test/operating leg reaction, baseline API fixture.


def run():
    rows = []
    for case_id, project in variants():
        support = project["supports"][0]
        length = support["base_plate_length_mm"]
        width = support["base_plate_width_mm"]
        fy = support["base_plate_yield_MPa"]
        ref = oracle({"L": length, "W": width, "Fy": fy,
                      "N": REACTION_N, "footprint": 114.3})
        outcome = run_case(project)
        result = next(iter(find_results(
            outcome.get("payload") or {}, component_id="LEGS",
            calculation_type="base_plate_check")), None)
        status = result.get("status") if result else "BLOCKED MISSING INPUT"
        reaction = value_of(result, "N_max") if result else None
        if reaction is not None:
            ref = oracle({"L": length, "W": width, "Fy": fy,
                          "N": reaction, "footprint": 114.3})
        for quantity, unit in (("t_required", "mm"), ("bearing_pressure_q", "MPa")):
            suite = value_of(result, quantity) if result else None
            diff, verdict = judge(suite, ref[quantity], suite_status=status)
            rows.append(CaseResult(
                case_id, FAMILY,
                {"L_mm": length, "W_mm": width,
                 "plate_t_mm": support["base_plate_thickness_mm"],
                 "Fy_MPa": fy, "reaction_N": reaction,
                 "footprint_mm": 114.3},
                quantity, unit, suite, ref[quantity],
                "Independent elastic bearing + cantilever strip calculation",
                diff, verdict,
                note="Moss PVDM 4-12 comparison uses suite's declared strip geometry; no anchor-group result is emitted by this calculation type.",
                suite_status=status))
    write_results(Path(__file__).parent, FAMILY, rows,
                  {"basis": "API base_plate_check vs independent plate equations",
                   "cases": len(variants()), "numeric_comparisons": len(rows)})


if __name__ == "__main__":
    run()
