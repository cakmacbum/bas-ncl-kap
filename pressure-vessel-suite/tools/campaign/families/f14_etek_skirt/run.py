"""Execute the F14 skirt campaign through the public calculation API."""
from __future__ import annotations

from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f14_etek_skirt.oracle import axial_stress, weld_stress
from tools.campaign.families.f14_etek_skirt.variants import variants
from tools.campaign.harness import find_results, run_case, value_of

FAMILY = "F14-etek_skirt"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project, params in variants():
        outcome = run_case(project)
        result = None
        if outcome.get("payload"):
            matches = find_results(outcome["payload"], component_id="SKIRT-01",
                                   calculation_type="skirt_stress")
            result = matches[0] if matches else None
        blocked = case_id in {"MISSING-B", "INVALID-THICKNESS"} or result is None
        if blocked:
            status = "BLOCKED MISSING INPUT" if case_id != "INVALID-THICKNESS" else "BLOCKED INVALID INPUT"
            for quantity in ("axial_stress", "weld_stress"):
                rows.append(CaseResult(case_id, FAMILY, params, quantity, "MPa", None, None,
                    "independent thin-wall oracle", None, "KAPSAM_DIŞI", outcome.get("error") or status, status))
            continue
        get = lambda name: value_of(result, name)
        diameter, thickness = get("D_skirt_mean"), get("t_skirt")
        weight, moment = get("W_total"), get("M_overturning")
        efficiency = get("E_weld")
        references = {
            "axial_stress": axial_stress(weight, moment, diameter, thickness),
            "weld_stress": weld_stress(weight, moment, diameter, thickness, efficiency),
        }
        # Suite axial comparator is S_combined; weld comparator is the tension-side stress.
        suite_values = {"axial_stress": get("S_combined"), "weld_stress": abs(get("S_tension"))}
        for quantity, reference in references.items():
            suite = suite_values[quantity]
            diff, verdict = judge(suite, reference, suite_status=result.get("status"),
                formulation_note="E weld efficiency differs: reference applies E to tensile-side stress only"
                if quantity == "weld_stress" else None)
            # compare.py's source file is decoded with replacement characters in this checkout.
            verdict = {"DO�RULANDI": "DOĞRULANDI", "FORM�LASYON_FARKI": "FORMÜLASYON_FARKI",
                       "KAPSAM_DI�I": "KAPSAM_DIŞI", "KAYNAK_BEKL�YOR": "KAYNAK_BEKLİYOR"}.get(verdict, verdict)
            rows.append(CaseResult(case_id, FAMILY, params, quantity, "MPa", suite, reference,
                "K3-08 CRC Press (geometry/moment reference; API-derived W)" if case_id == "K3-08" else "independent W/A ± M/Z thin-wall calculation",
                diff, verdict, "; status=" + str(result.get("status")), result.get("status")))
    write_results(HERE, FAMILY, rows, {"code": "ASME VIII-1", "oracle": "W/(πDt) ± 4M/(πD²t); tensile weld side considers E",
        "suite_source": "FastAPI /api/projects/{id}/calculate", "case_count": len(list(variants()))})
    return rows


if __name__ == "__main__":
    run()
