"""Run the saddle campaign through the public calculation API."""
from pathlib import Path
import json

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.families.f13_saddle_zick.oracle import calculate
from tools.campaign.families.f13_saddle_zick.variants import variants

FAMILY = "F13-saddle_zick"
HERE = Path(__file__).parent


def run():
    rows = []
    api_ok = 0
    for case_id, project, params in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        api_ok += int(bool(outcome.get("ok")))
        matches = find_results(payload, calculation_type="saddle_stress")
        for match in matches:
            iv = {item.get("name"): item.get("value")
                  for item in match.get("intermediate_values", [])}
            ref = None
            if all(iv.get(k) is not None for k in ("M1", "M2", "R_m", "t", "K1")):
                ref = calculate(M1_Nmm=float(iv["M1"]), M2_Nmm=float(iv["M2"]),
                                R_m_mm=float(iv["R_m"]), t_corroded_mm=float(iv["t"]),
                                K1=float(iv["K1"]))
            for quantity in ("S1_saddle", "S1_midspan"):
                suite = value_of(match, quantity)
                reference = ref.get(quantity) if ref else None
                diff, verdict = judge(suite, reference, suite_status=match.get("status"))
                rows.append(CaseResult(
                    case_id, FAMILY, {**params, "support_id": match.get("component_id")},
                    quantity, "MPa", suite, reference,
                    "Independent beam/shell equation check; catalog API intermediates",
                    diff, verdict,
                    note="Formula check uses the API-reported moments, radius, thickness, and explicit K1.",
                    suite_status=match.get("status")))
        # Preserve one diagnostic row when the API emitted no saddle result.
        if not matches:
            rows.append(CaseResult(case_id, FAMILY, params, "saddle_stress", "MPa",
                                   None, None, "RESULT_CATALOG.md saddle_stress contract",
                                   None, "KAPSAM_DIŞI",
                                   note=outcome.get("error") or "No saddle_stress result row.",
                                   suite_status=None))
    path = write_results(HERE, FAMILY, rows, {
        "code": "Zick longitudinal saddle/midspan bending forms",
        "oracle": "independent abs(M)/(K1 Rm^2 t) and abs(M2)/(pi Rm^2 t); no K table",
        "api_ok_cases": api_ok,
    })
    # The shared compare module's source encoding corrupts Turkish verdicts;
    # normalize only this campaign output to the contract's canonical labels.
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data["results"]:
        row["verdict"] = row["verdict"].replace("�", "Ş") if "KAPSAM" in row["verdict"] else row["verdict"].replace("�", "Ğ")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
