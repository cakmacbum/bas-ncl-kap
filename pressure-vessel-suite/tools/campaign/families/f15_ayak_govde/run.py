from pathlib import Path

from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results
from .variants import variants
from .oracle import calculate

FAMILY = "F15-ayak-govde"


def run():
    rows = []
    for cid, project, params in variants():
        out = run_case(project)
        found = find_results(out.get("payload") or {}, component_id="LEGS",
                             calculation_type="leg_stress")
        result = found[0] if found else None
        status = result.get("status") if result else (
            "BLOCKED MISSING INPUT" if not out.get("ok") else "NOT CALCULATED")
        values = {key: value_of(result, key) for key in ("W_total", "N_max", "A_leg", "P_base")} if result else {}
        if result and all(values[k] is not None for k in values):
            ref = calculate(params["diameter_mm"], params["thickness_mm"], params["count"], values["W_total"])
            for quantity, key in (("N_max", "N_max"), ("P_base", "P_base"), ("A_leg", "A_leg")):
                diff, verdict = judge(values[key], ref[key], suite_status=status)
                if params.get("published") and quantity == "P_base":
                    verdict = "TEK_KAYNAK" if abs(diff or 0.0) <= 1.0 else "SAPMA"
                rows.append(CaseResult(f"{cid}-{quantity}", FAMILY, {**params, "suite_ok": out.get("ok"), "status": status},
                                       quantity, "N" if quantity == "N_max" else ("mm2" if quantity == "A_leg" else "MPa"),
                                       values[key], ref[key], params.get("published", "oracle"), diff, verdict,
                                       note="leg_stress ara degerleri ile annulus ve W_total/n bagimsiz kontrolu.", suite_status=status))
        else:
            rows.append(CaseResult(cid, FAMILY, {**params, "suite_ok": out.get("ok"), "status": status},
                                   "N_max", "N", values.get("N_max"), None, "oracle", None,
                                   "KAPSAM_DIŞI", note="Katalog girdisi veya leg_stress ara degeri eksik.", suite_status=status))
    return write_results(Path(__file__).parent, FAMILY, rows,
                         {"oracle": "annular area + W_total/count axial reaction and stress", "case_count": len(variants())})


if __name__ == "__main__":
    run()
