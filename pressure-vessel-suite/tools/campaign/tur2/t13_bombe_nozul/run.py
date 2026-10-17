"""Run T13 head nozzle geometry cases through the public calculation API."""
from __future__ import annotations

import json
from pathlib import Path

from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.tur2.t13_bombe_nozul.cases import cases


def run():
    rows = []
    for case in cases():
        outcome = run_case(case["project"])
        payload = outcome.get("payload") or {}
        matches = find_results(payload, calculation_type="nozzle_reinforcement")
        row = next((r for r in matches if r.get("component_id") == "HEAD-T13"),
                   matches[0] if matches else None)
        expected = case["expected"]
        status = (row or {}).get("status")
        zone = expected["zone"]
        if row is None:
            result = "BULGU" if outcome.get("ok") else "KAPSAM_DIŞI"
        elif zone == "outside_80_percent" and status not in {"BLOCKED", "REVIEW REQUIRED", "OUT OF SCOPE"}:
            result = "BULGU"
        else:
            result = "GEÇTİ"
        rows.append({"vaka": case["case_id"], "girdi": {
                "shape": expected["shape"], "offset_mm": expected["offset_mm"],
                "nozzle": case["project"]["nozzles"][0]},
            "beklenen": expected, "gozlenen": {"api_ok": outcome.get("ok"),
                "error": outcome.get("error"), "status": status,
                "component_id": (row or {}).get("component_id"),
                "A_required_mm2": value_of(row or {}, "A_required"),
                "result_row": row}, "sonuc": result})
    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


if __name__ == "__main__":
    run()
