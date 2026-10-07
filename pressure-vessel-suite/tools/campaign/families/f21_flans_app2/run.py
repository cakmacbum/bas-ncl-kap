"""Execute the F21 cases through the campaign's public API harness."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f21_flans_app2 import FAMILY
from tools.campaign.families.f21_flans_app2.oracle import values
from tools.campaign.families.f21_flans_app2.variants import variants


def run():
    rows = []
    for case_id, project in variants():
        flange = project["flanges"][0]
        params = dict(flange)
        outcome = run_case(project)
        matches = find_results(outcome.get("payload") or {}, component_id="F1",
                               calculation_type="flange_stress")
        row = matches[0] if matches else None
        refs = values(params)
        for quantity in ("W", "M"):
            suite = value_of(row, quantity) if row else None
            ref = refs[quantity]
            diff, verdict = judge(suite, ref, suite_status=(row or {}).get("status"),
                                  formulation_note="Appendix 2 loads/stresses")
            note = "No flange_stress result row" if row is None else "Catalog intermediate echoed against explicit independent input"
            if not outcome.get("ok") and verdict == "KAPSAM_DIŞI":
                note = f"API error/status: {outcome.get('error')}"
            rows.append(CaseResult(case_id, FAMILY, params, quantity, "N or N·mm (API units)",
                                   suite, ref, "clean-room equations; see report", diff, verdict,
                                   note, (row or {}).get("status")))
    # Published cases retain source values pending complete machine-readable
    # source geometry; the campaign cases above use the public API fixture.
    for case_id, source, refs in (
        ("K2-12", "sources-K2.md §K2-12 (Paget APV 9.1.1, pp. 22–26)",
         {"Wm1": 362291, "Wm2": 182053, "Am": 14.4916, "W": 635645,
          "Mo": 782355, "SH": 14545, "SR": 80, "ST": 10958}),
        ("K2-13", "sources-K2.md §K2-13 (PVE-4293, pp. 11–15)",
         {"Wm1": 53966, "Wm2": 50647, "Am": 2.159, "W": 67383,
          "Mo": 97547, "SH": 19821, "SR": 1180, "ST": 8884}),
    ):
        for quantity, reference in refs.items():
            rows.append(CaseResult(case_id, FAMILY, {"published_example": case_id}, quantity,
                "lb, in·lb, in² or psi (published source units)", None, reference, source, None,
                "KAYNAK_BEKLİYOR", "Source value transcribed; project schema lacks complete matching inputs/API row."))
    write_results(Path(__file__).parent, FAMILY, rows, {"code": "ASME VIII-1", "case_count": 30,
        "method": "Catalog flange_stress example; W and M intermediate_values compared with explicit input oracle"})


if __name__ == "__main__":
    run()
