"""Run the F08 family through the public calculation API."""
from pathlib import Path
from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results
from .variants import variants
from .oracle import test_pressures, published_k1_14

FAMILY = "F08-test-basinci"


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        for kind, factor in (("hydrotest", 1.3), ("pneumatic_test", 1.1)):
            found = find_results(payload, calculation_type=kind)
            result = found[0] if found else None
            suite = value_of(result, "P_test") if result else None
            if suite is None and result:
                suite = value_of(result, "final_result")
            # The suite reports its independently calculated pressure basis and LSR.
            # Recompute the standard multiplier, but do not treat a suite-derived
            # intermediate as an independent pressure-basis oracle.
            basis = value_of(result, "pressure_basis") if result else None
            lsr = value_of(result, "ratio") if result else None
            reference = factor * basis * lsr if basis is not None and lsr is not None else None
            diff, verdict = judge(suite, reference, suite_status=result.get("status") if result else "BLOCKED")
            rows.append(CaseResult(case_id + "/" + kind, FAMILY,
                {"density_kg_m3": project["design_conditions"].get("fluid_density_kg_m3", 0),
                 "design_pressure_mpa": project["design_conditions"].get("design_pressure"),
                 "factor": factor}, kind, "MPa", suite, reference,
                 "clean-room UG-99(b)/UG-100 arithmetic", diff, verdict,
                 "Pressure basis and LSR are suite intermediates; multiplier arithmetic only is independently checked.",
                 result.get("status") if result else None))
    k1 = published_k1_14()
    # Convert the external reference exactly to SI; the suite-side row remains the published value.
    rows.append(CaseResult("K1-14/hydrotest", FAMILY,
        {"published_mawp_psig": k1["mawp_psig"], "lsr": k1["lsr"]},
        "hydrotest pressure", "psig", None, k1["hydro_psig"],
        "sources-K1.md §K1-14 (Codeware/COMPRESS, 2021)", None, "TEK_KAYNAK",
        "Published reference 204.1 psig; source reports software-rounded 205 psig.", None))
    write_results(Path(__file__).parent, FAMILY, rows,
                  {"code": "ASME VIII-1", "oracle": "UG-99(b): 1.3×MAWP×LSR; UG-100: 1.1×MAWP×LSR"})


if __name__ == "__main__":
    run()
