"""Run the F05 UG-34 campaign through the service API."""
from __future__ import annotations

from pathlib import Path
from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results
from .variants import variants, invalid_variants
from .oracle import required_thickness, reference_cases

FAMILY = "F05-duz_kapak_ug34"
OUT = Path(__file__).parent


def _project(case_id, d, p, c, ca, stress=137.895):
    return vertical_leg_tank(
        project_number=case_id, project_name=case_id,
        design_conditions={"operating_pressure": max(.001, p*.8), "design_pressure":p,
                           "maximum_allowable_pressure_ps":max(p,.01)},
        heads=[{"head_id":"FLAT-01", "type":"flat", "inside_diameter":d,
                "nominal_thickness":25, "material_id":"M1", "internal_corrosion_allowance":ca,
                "flat_attachment_factor":c}],
        materials=[{"material_id":"M1", "standard_pack":"ASME II-D 2025",
                    "material_designation":"SA-516 Gr.70", "product_form":"plate",
                    "temperature":200, "allowable_stress":stress, "yield_strength":260,
                    "tensile_strength":485, "source_reference":"ASME II-D Table 1A",
                    "source_revision":"2025", "density":7850}],
    )


def run():
    rows = []
    for case_id, project in list(variants()) + list(invalid_variants()):
        head = project["heads"][0]
        dc = project["design_conditions"]
        material = next(m for m in project["materials"] if m["material_id"] == head["material_id"])
        p = dc["design_pressure"]
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, component_id=head["head_id"], clause_prefix="UG-34")
        result = matches[0] if matches else None
        suite = value_of(result, "t_required") if result else None
        status = result.get("status") if result else ("BLOCKED INVALID INPUT" if case_id == "INVALID-NEGATIVE-P" else None)
        c_factor = head.get("flat_attachment_factor")
        ref = (required_thickness(head["inside_diameter"], p, material["allowable_stress"],
                                  1.0, c_factor,
                                  head.get("internal_corrosion_allowance", 0))
               if p > 0 and c_factor is not None else None)
        diff, verdict = judge(suite, ref, suite_status=status)
        note = "" if result else f"API/result missing: {outcome.get('error') or 'UG-34 row not returned'}"
        rows.append(CaseResult(case_id, FAMILY, {"d_mm":head.get("inside_diameter"),
            "P_MPa":p, "C":head.get("flat_attachment_factor"), "CA_mm":head.get("internal_corrosion_allowance",0),
            "S_MPa":material["allowable_stress"]}, "required_thickness", "mm", suite, ref,
            "oracle", diff, verdict, note, status))

    pub = reference_cases()["PUBLISHED-K1-05"]
    project = _project("PUBLISHED-K1-05", pub["d_mm"], pub["pressure_mpa"], .2, 0,
                       pub["allowable_mpa"])
    outcome = run_case(project)
    result_rows = find_results(outcome.get("payload") or {}, component_id="FLAT-01", clause_prefix="UG-34")
    result = result_rows[0] if result_rows else None
    suite = value_of(result, "t_required") if result else None
    diff, verdict = judge(suite, pub["published_mm"], suite_status=(result or {}).get("status"))
    rows.append(CaseResult("PUBLISHED-K1-05", FAMILY, pub, "required_thickness", "mm", suite,
        pub["published_mm"], pub["source"], diff, verdict,
        "Published output has C=.2 and zero corrosion allowance.", (result or {}).get("status")))
    write_results(OUT, FAMILY, rows, {"code":"ASME VIII-1", "clause":"UG-34(c)(2)",
        "oracle":"t=d*sqrt(CP/SE + 1.9WhG/(SEd^3))+CA", "cases":len(rows)})
    return rows


if __name__ == "__main__":
    run()
