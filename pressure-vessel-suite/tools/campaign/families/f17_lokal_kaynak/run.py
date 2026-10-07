"""Reproducible F17 comparisons through the public campaign API."""
from __future__ import annotations

from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case
from tools.campaign.families.f17_lokal_kaynak.oracle import oracle
from tools.campaign.families.f17_lokal_kaynak.variants import variants

FAMILY = "F17-lokal_kaynak"


def _values(result):
    return {item["name"]: item.get("value")
            for item in result.get("intermediate_values", [])}


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        result = next(iter(find_results(outcome.get("payload") or {},
                                        component_id="LEGS",
                                        calculation_type="leg_weld_check")), None)
        if not outcome.get("ok") or result is None:
            rows.append(CaseResult(case_id, FAMILY, params, "pad_to_shell_stress",
                "MPa", None, None, "RESULT_CATALOG.md leg_weld_check", None,
                "KAPSAM_DIŞI", str(outcome.get("error") or "leg_weld_check satırı yok"),
                "BLOCKED CODE DATA"))
            continue
        vals = _values(result)
        ref = oracle(params,
            shear_N=float(vals["pad_to_shell_shear"]),
            normal_N=float(vals["pad_to_shell_normal"]),
            moment_Nmm=float(vals["pad_to_shell_moment"]),
            effective_Lw_mm=float(vals["pad_to_shell_Lw"]),
            effective_Sw_mm=float(vals["pad_to_shell_Sw"]))
        suite = float(vals["pad_to_shell_stress"])
        diff, verdict = judge(suite, ref["weld_stress"], suite_status=result.get("status"))
        rows.append(CaseResult(case_id, FAMILY, params, "pad_to_shell_stress",
            "MPa", suite, ref["weld_stress"],
            "Independent weld-group stress equation; geometry intermediates from API", diff, verdict,
            f"Effective Lw={ref['Lw']:.6g} mm; Sw={ref['Sw']:.6g} mm²; "
            f"raw closed-line Lw={ref['raw_Lw']:.6g}, Sw={ref['raw_Sw']:.6g}; "
            "loads and corrected geometry use API intermediates.", result.get("status")))

    # Published geometry reference, retained as a single-source check.
    pub = {"shape": "rectangle", "b_mm": 70, "d_mm": 120}
    pub_oracle = 70 * 120 + 120**2 / 3
    rows.append(CaseResult("PUB-K3-22", FAMILY, pub, "Sw", "mm2", None,
        pub_oracle, "sources-K3.md K3-22", None, "TEK_KAYNAK",
        "Shigley/Union College yayın geometrisi; Sw=13,200 mm².", None))

    write_results(Path(__file__).parent, FAMILY, rows,
        {"code": "ASME VIII-1", "source": "RESULT_CATALOG.md leg_weld_check; "
         "Blodgett §7.4; sources-K3.md K3-22",
         "oracle": "independently derived weld-group line-force and throat-stress "
         "equation; API effective Lw/Sw accepted as inputs; raw Blodgett geometry "
         "reported separately"})
    return rows


if __name__ == "__main__":
    run()
