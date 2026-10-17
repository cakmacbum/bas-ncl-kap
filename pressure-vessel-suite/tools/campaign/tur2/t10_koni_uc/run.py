"""Run T10 cases through the public campaign harness and save observations."""
from __future__ import annotations

import json
from pathlib import Path

from tools.campaign.harness import find_results, run_case
from tools.campaign.tur2.t10_koni_uc.cases import all_cases


HERE = Path(__file__).resolve().parent


def main() -> int:
    rows = []
    for case in all_cases():
        response = run_case(case["project"])
        found = find_results(response.get("payload") or {}, component_id="J1",
                             calculation_type="junction_check")
        result = found[0] if found else None
        observed = result.get("status") if result else ("HTTP_ERROR" if not response.get("ok") else "NO_RESULT")
        observed_key = str(observed).upper().replace(" ", "_")
        expected_key = case["expected"]
        status = "GEÇTİ" if (observed_key.startswith("BLOCKED") if expected_key == "BLOCKED"
                              else observed_key == expected_key) else "BULGU"
        if observed in ("NO_RESULT", "HTTP_ERROR"):
            status = "BULGU"
        rows.append({"vaka": case["id"], "girdi": {k: case[k] for k in
                     ("angle_deg", "knuckle_present", "end", "mismatch")},
                     "beklenen": case["expected"], "gözlenen": observed,
                     "sonuç": status, "durum": (result or {}).get("status"),
                     "uyarılar": (result or {}).get("warnings", []),
                     "hata": response.get("error"), "oracle_notu": case["basis"]})
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {key: sum(row["sonuç"] == key for row in rows) for key in ("GEÇTİ", "BULGU")}
    print(f"vaka={len(rows)} geçti={counts['GEÇTİ']} bulgu={counts['BULGU']}")
    return 1 if counts["BULGU"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
