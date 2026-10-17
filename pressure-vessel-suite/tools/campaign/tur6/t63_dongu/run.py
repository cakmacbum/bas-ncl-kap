"""Run the T63 end-to-end campaign and write raw results plus independent counts."""
from __future__ import annotations

import json
import math
from pathlib import Path

from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.tur6.t63_dongu.cases import cases


OUT = Path(__file__).resolve().parent


def _utilization(row):
    for name in ("utilization_ratio", "utilization", "utilisation"):
        v = row.get(name)
        if isinstance(v, (int, float)):
            return float(v)
    for name in ("utilization_ratio", "utilization", "utilisation", "U"):
        v = value_of(row, name)
        if v is not None:
            return v
    return None


def run():
    records = []
    counts = {c: {"vaka": 0, "UYUŞUR": 0, "UYUŞMUYOR": 0, "VERİ_YOK": 0,
                  "nedenler": {}} for c in ("A", "B")}
    for case in cases():
        outcome = run_case(case["project"])
        payload = outcome.get("payload") or {}
        expected_kind = "nozzle_reinforcement" if case["kind"] == "nozzle" else "thickness"
        rows = find_results(payload, component_id="N1" if case["kind"] == "nozzle" else "HEAD-L",
                            calculation_type=expected_kind)
        if case["kind"] == "head":
            rows = [r for r in rows if str(r.get("clause_reference", "")).startswith("UG-32")]
        row = rows[0] if rows else None
        api_status = (row or {}).get("status")
        api_value = None
        independent = None
        rc = None
        reason = None
        if row is None:
            verdict, reason = "VERİ_YOK", "API bileşen sonucu yok"
        elif case["kind"] == "nozzle":
            api_value = _utilization(row)
            if api_value is None or not math.isfinite(api_value):
                verdict, reason = "VERİ_YOK", "utilization_ratio yok veya sonlu değil"
            else:
                state = str(api_status or "").upper().replace("_", " ").split()[0]
                # Contract: API PASS precisely when current/required utilization >= 1.
                verdict = "UYUŞUR" if ((state == "PASS") == (api_value >= 1.0)) else "UYUŞMUYOR"
                if verdict == "UYUŞMUYOR":
                    reason = "API PASS/FAIL durumu utilization_ratio ≥ 1 eşiğiyle çelişiyor"
        else:
            api_value = value_of(row, "t_required")
            x = case["inputs"]
            rc = x["D_i_mm"] / 2 + x["CA_i_mm"]
            dc = x["D_i_mm"] + 2 * x["CA_i_mm"]
            independent = x["P_MPa"] * dc / (2 * x["S_MPa"] * x["E"] - 0.2 * x["P_MPa"])
            if api_value is None or not math.isfinite(api_value):
                verdict, reason = "VERİ_YOK", "API t_required yok veya sonlu değil"
            else:
                relative_error = abs(api_value - independent) / abs(independent)
                verdict = "UYUŞUR" if relative_error <= 0.01 else "UYUŞMUYOR"
                if verdict == "UYUŞMUYOR":
                    reason = "API t_required bağımsız UG-32(d) sonucundan %1'den fazla farklı"
        bucket = counts[case["component"]]
        bucket["vaka"] += 1
        bucket[verdict] += 1
        if reason:
            bucket["nedenler"][reason] = bucket["nedenler"].get(reason, 0) + 1
        records.append({"id": case["id"], "component": case["component"], "kind": case["kind"],
                        "girdi": case["inputs"], "http_status": outcome.get("http_status"),
                        "api_ok": outcome.get("ok"), "api_error": outcome.get("error"),
                        "api_status": api_status, "api_value": api_value,
                        "independent_value": independent, "R_c_mm": rc if case["kind"] == "head" else None,
                        "relative_error": (abs(api_value - independent) / abs(independent)
                                           if case["kind"] == "head" and api_value is not None else None),
                        "kontrol": verdict, "neden": reason, "api_payload": payload})
    (OUT / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2,
                                                   allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "kontrol.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2,
                                                  allow_nan=False) + "\n", encoding="utf-8")
    print("vaka=240 " + " ".join(f"{c}: uyuşur={counts[c]['UYUŞUR']} uyuşmaz={counts[c]['UYUŞMUYOR']} veri_yok={counts[c]['VERİ_YOK']}" for c in ("A", "B")))
    return records


if __name__ == "__main__":
    run()
