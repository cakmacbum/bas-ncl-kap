"""Execute F02 cases via the public API harness and write results.json."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f02_bombe_eliptik.oracle import mawp, required_thickness
from tools.campaign.families.f02_bombe_eliptik.variants import invalid_variant, variants

FAMILY = "F02-bombe_eliptik"
OUT = Path(__file__).parent


def run():
    rows = []
    for case_id, project in list(variants()) + [("INVALID-MATERIAL", invalid_variant())]:
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        head_t = next((r for r in find_results(payload, component_id="HEAD-L", calculation_type="thickness")
                       if str(r.get("clause_reference", "")).startswith("UG-32")), None)
        head_m = next((r for r in find_results(payload, component_id="HEAD-L", calculation_type="mawp")
                       if str(r.get("clause_reference", "")).startswith("UG-32")), None)
        head = head_t or head_m
        status = (head or {}).get("status")
        suite_t = value_of(head_t, "t_required") if head_t else None
        suite_m = value_of(head_m, "MAWP") if head_m else None
        inp = project["heads"][0]
        material = next(m for m in project["materials"] if m["material_id"] == "M1")
        p = project["design_conditions"]["design_pressure"]
        ref_t = required_thickness(p, inp["inside_diameter"], material["allowable_stress"],
                                   next(w["joint_efficiency"] for w in project["welds"]))
        available = inp["nominal_thickness"] * (1 - inp["mill_tolerance"] / 100) - inp["forming_thinning"] - inp["internal_corrosion_allowance"]
        ref_m = mawp(inp["inside_diameter"], max(available, 0), material["allowable_stress"],
                     next(w["joint_efficiency"] for w in project["welds"])) if available > 0 else None
        for quantity, suite, ref, unit in (("required_thickness", suite_t, ref_t, "mm"),
                                           ("mawp", suite_m, ref_m, "MPa")):
            diff, verdict = judge(suite, ref, suite_status=status)
            source = "K1-19 (PVE-3247 p.3; sources-K1.md)" if case_id == "K1-19" and quantity == "required_thickness" else "independent UG-32(d) equation"
            note = ("Compared pressure thickness before CA: source reports 0.115 in including 0.010 in CA; "
                    "source MAWP 341.3 psi recalculates to 342.3 psi.") if case_id == "K1-19" and quantity == "required_thickness" else ""
            rows.append(CaseResult(case_id, FAMILY,
                {"P_MPa": p, "D_i_mm": inp["inside_diameter"], "CA_mm": inp["internal_corrosion_allowance"],
                 "mill_tolerance_pct": inp["mill_tolerance"], "forming_thinning_mm": inp["forming_thinning"],
                 "straight_flange_mm": inp["straight_flange_length"], "E": next(w["joint_efficiency"] for w in project["welds"])},
                quantity, unit, suite, ref, source, diff, verdict, note, status))
    write_results(OUT, FAMILY, rows, {"code": "ASME VIII-1", "basis": "UG-32(d), K=1"})
    return rows


if __name__ == "__main__":
    run()
