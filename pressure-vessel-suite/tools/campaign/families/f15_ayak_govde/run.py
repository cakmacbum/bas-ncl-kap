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
        payload = out.get("payload") or {}
        found = find_results(payload, component_id="LEGS")
        result = found[0] if found else None
        weight = params.get("weight_N", 100000.0)
        shape = params.get("shape", "pipe")
        d, t = params.get("od_mm", 114.3), params.get("t_mm", 8.0)
        length, k = params.get("length_mm", 600.0), params.get("K", 1.0)
        count = params.get("count", 4)
        ref = calculate(shape, d, t, length, k, weight, count)
        suite = value_of(result, "axial_load_N") if result else None
        status = result.get("status") if result else ("BLOCKED MISSING INPUT" if not out.get("ok") else "NOT CALCULATED")
        # Only the published axial load has a directly comparable documented value.
        reference = weight/count if params.get("published") else ref["axial_N"]
        diff, verdict = judge(suite, reference, suite_status=status)
        if params.get("published") and suite is not None:
            verdict = "TEK_KAYNAK" if abs(diff or 100) <= 1 else "SAPMA"
        rows.append(CaseResult(cid, FAMILY, {**params, "suite_ok": out.get("ok"), "status": status},
                               "axial_load_N", "N", suite, reference,
                               "K3-13" if cid.startswith("K3-13") else ("K3-14" if cid.startswith("K3-14") else "oracle"), diff, verdict,
                               note="Bağımsız oracle ayrıca kesit A, r, KL/r ve AISC E3 Fcr hesaplar; API bu alanı üretmiyorsa kayıt KAPSAM_DIŞI.", suite_status=status))
    return write_results(Path(__file__).parent, FAMILY, rows, {"oracle": "thin-wall section + AISC 360-16 E3", "case_count": len(rows)})


if __name__ == "__main__":
    run()
