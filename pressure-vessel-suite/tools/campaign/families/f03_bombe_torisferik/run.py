"""Run the F03 torispherical head campaign through the public API."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import math

from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f03_bombe_torisferik.variants import variants
from tools.campaign.families.f03_bombe_torisferik.oracle import thickness_mawp

FAMILY = "F03-bombe-torisferik"
OUT = Path(__file__).parent


def _case_values(project):
    head = project["heads"][0]
    conditions = project["design_conditions"]
    mat = next(m for m in project["materials"] if m["material_id"] == head["material_id"])
    weld_id = head.get("weld_joint_id")
    weld = next((w for w in project["welds"] if w["joint_id"] == weld_id), None)
    e = weld["joint_efficiency"] if weld else 1.0
    return head, conditions["design_pressure"], mat["allowable_stress"], e


def run():
    rows = []
    for case_id, project in variants():
        head, pressure, stress, efficiency = _case_values(project)
        outcome = run_case(project)
        result_rows = find_results(outcome.get("payload") or {}, component_id="HEAD-L")
        result = next((r for r in result_rows if r.get("calculation_type") == "thickness"), None)
        mawp_result = next((r for r in result_rows if r.get("calculation_type") == "mawp"), None)
        status = result.get("status") if result else ("BLOCKED MISSING INPUT" if not outcome.get("ok") else None)
        suite_map = {
            "required_thickness": value_of(result, "t_required") if result else None,
            "mawp": (value_of(mawp_result, "MAWP") or value_of(mawp_result, "final_result")) if mawp_result else None,
            "M": value_of(result, "M_factor") if result else None,
        }
        # K1-10 uses published output as a separate oracle row; all other rows use equations.
        p = pressure
        ref = None
        if head.get("knuckle_radius"):
            m = 0.25 * (3 + math.sqrt(head["crown_radius"] / head["knuckle_radius"]))
            tref = p * head["crown_radius"] * m / (2*stress*efficiency - 0.2*p)
            mref = m
            t_corr = head["nominal_thickness"] - head["internal_corrosion_allowance"]
            pref = 2*stress*efficiency*t_corr/(head["crown_radius"]*m + 0.2*t_corr)
            ref = {"required_thickness":tref, "mawp":pref, "M":mref}
        if case_id == "PUB-K1-10":
            # Published COMPRESS Four Heads values and source attribution are retained as their own case.
            ref = {"required_thickness":0.8901*25.4, "mawp":420.01*0.006894757293168, "M":1.7623}
        for quantity, unit in (("required_thickness","mm"),("mawp","MPa"),("M","dimensionless")):
            reference = ref.get(quantity) if ref else None
            diff, verdict = judge(suite_map[quantity], reference, suite_status=status,
                                  formulation_note="custom geometry route" if head.get("torispherical_geometry") == "custom" else None)
            note = "API request failed: " + str(outcome.get("error")) if not outcome.get("ok") else ""
            if head.get("knuckle_radius") and head["knuckle_radius"] < 0.06 * head["crown_radius"]:
                note = (note + "; " if note else "") + "r < 0.06L boundary violation probe"
            rows.append(CaseResult(case_id, FAMILY, {"pressure_mpa":pressure, "D_mm":head["inside_diameter"],
                "L_mm":head.get("crown_radius"), "r_mm":head.get("knuckle_radius"),
                "geometry":head.get("torispherical_geometry"), "efficiency":efficiency}, quantity, unit,
                suite_map[quantity], reference, "K1-10 (PVE Four Heads)" if case_id == "PUB-K1-10" else "UG-32(e)/Appendix 1-4(d) independent equation",
                diff, verdict, note, status))
    write_results(OUT, FAMILY, rows, {"code":"ASME VIII-1", "clause":"UG-32(e), Appendix 1-4(d)",
        "oracle":"t=PLM/(2SE-0.2P); M=1/4(3+sqrt(L/r)); MAWP=2SEt/(LM+0.2t)"})
    return rows


if __name__ == "__main__":
    rows = run()
    counts = Counter(r.verdict for r in rows)
    print(f"{len(rows)} comparisons; verdicts={dict(counts)}")
