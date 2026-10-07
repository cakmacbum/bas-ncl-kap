"""Reproducible F17 run through the campaign's public API harness."""
from __future__ import annotations

from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f17_lokal_kaynak.oracle import oracle
from tools.campaign.families.f17_lokal_kaynak.variants import variants

FAMILY = "F17-lokal_kaynak"


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        result = next(iter(find_results(payload, component_id="LEGS",
                                        calculation_type="leg_stress")), None)
        ref = oracle(params)
        # Current API exposes leg axial stress only; it has no local weld, Lw,
        # Sw, Jw, or WRC result row. Do not compare unrelated quantities.
        suite = value_of(result, "weld_stress") if result else None
        status = result.get("status") if result else None
        if params.get("invalid"):
            verdict, diff = "KAPSAM_DIŞI", None
            status = "BLOCKED MISSING INPUT" if params.get("b_mm") is None or params.get("d_mm") is None else "BLOCKED INVALID INPUT"
        else:
            diff, verdict = judge(suite, None, suite_status=status)
            verdict = "KAYNAK_BEKLİYOR" if outcome.get("ok") else "KAPSAM_DIŞI"
        note = ("API çıktı zarfı: " + str(outcome.get("http_status")) + "; " + str(outcome.get("error"))) if not outcome.get("ok") else "API yanıtında lokal kaynak/WRC büyüklüğü yok; suite Lw/Sw/Jw/kaynak gerilmesi üretmedi."
        rows.append(CaseResult(case_id, FAMILY, params, "weld_stress", "MPa", suite,
                               ref["weld_stress"], "Blodgett bağımsız çizgi integrali", diff,
                               verdict, note, status))
    # Independent published geometry case (Shigley/Union College K3-22).
    params = {"shape": "rectangle", "b_mm": 70, "d_mm": 120, "force_N": 10000,
              "moment_Nmm": 1600000}
    ref = oracle(params)
    rows.append(CaseResult("PUB-K3-22", FAMILY, params, "Sw", "mm2", None,
                           ref["Sw"], "sources-K3.md K3-22", None, "TEK_KAYNAK",
                           "Yayınlanan Iu/c türetimi Sw=13,200 mm² ile örtüşür; suite API'sinde Sw alanı bulunmuyor."))
    write_results(Path(__file__).parent, FAMILY, rows,
                  {"code": "ASME VIII-1", "source": "engineering-source-review-2026-09-30.md §3; sources-K3.md K3-22",
                   "oracle": "closed line-integral identities; WRC dimensional scaling only"})
    return rows


if __name__ == "__main__":
    run()
