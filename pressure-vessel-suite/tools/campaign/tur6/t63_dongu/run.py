"""Run T63/T45 cases with independent references persisted before API calls."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.tur6.t63_dongu.cases import cases

OUT = Path(__file__).resolve().parent


def _reference(case):
    x = case["inputs"]
    if case["kind"] == "nozzle":
        tr = x["P_MPa"] * x["R_mm"] / (x["S_MPa"] - 0.6 * x["P_MPa"])
        return x["nozzle_d_mm"] * tr + 2 * x["neck_t_mm"] * tr * (1 - x["fr1"]), tr
    if case["kind"] == "head":
        dc = x["D_i_mm"] + 2 * x["CA_i_mm"]
        return x["P_MPa"] * dc / (2 * x["S_MPa"] * x["E"] - 0.2 * x["P_MPa"]), None
    m = 0.25 * (3 + math.sqrt(x["L_mm"] / x["r_mm"]))
    return x["P_MPa"] * x["L_mm"] * m / (2 * x["S_MPa"] * x["E"] - 0.2 * x["P_MPa"]), None


def run():
    all_cases = list(cases())
    refs = []
    for case in all_cases:
        x = case["inputs"]
        if case["kind"] == "nozzle":
            x.update(R_mm=x["D_i_mm"] / 2, fr1=1.0)
        ref, tr = _reference(case)
        case["reference"] = ref
        refs.append({"id": case["id"], "kind": case["kind"],
                     "required_area_or_thickness": ref, "t_r_mm": tr if tr is not None else ""})
    with (OUT / "ref.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=refs[0].keys())
        writer.writeheader()
        writer.writerows(refs)

    labels = ("UYUŞUR", "UYUŞMUYOR", "VERİ_YOK")
    counts = {c: {"vaka": 0, **{label: 0 for label in labels}, "nedenler": {}} for c in ("A", "B", "C")}
    records = []
    for case in all_cases:
        outcome = run_case(case["project"])
        payload = outcome.get("payload") or {}
        kind = case["kind"]
        rows = find_results(payload, component_id="N1" if kind == "nozzle" else "HEAD-L",
                            calculation_type="nozzle_reinforcement" if kind == "nozzle" else "thickness")
        clause = "UG-32(e)" if kind == "torispherical" else "UG-32(d)"
        if kind != "nozzle":
            rows = [r for r in rows if str(r.get("clause_reference", "")).startswith(clause)]
        row = rows[0] if rows else None
        api_val = None
        utilization = None
        if row:
            if kind == "nozzle":
                api_val = next((float(row[n]) for n in ("required_area", "area_required", "A_required")
                                if isinstance(row.get(n), (int, float))), value_of(row, "A_required"))
                u = row.get("utilization_ratio")
                utilization = float(u) if isinstance(u, (int, float)) else value_of(row, "utilization_ratio")
            else:
                api_val = value_of(row, "t_required")
        ref = case["reference"]
        reason = None
        if api_val is None or not math.isfinite(api_val):
            verdict, reason = "VERİ_YOK", "API karşılaştırma değeri yok"
        else:
            err = abs(api_val - ref) / abs(ref)
            if kind == "nozzle":
                passed = err <= 0.01 and utilization is not None and utilization >= 1
                reason = None if passed else "required_area farkı >%1 veya utilization_ratio <1/yok"
            else:
                passed = err <= 0.01
                reason = None if passed else "t_required bağımsız referanstan %1'den fazla farklı"
            verdict = "UYUŞUR" if passed else "UYUŞMUYOR"
        bucket = counts[case["component"]]
        bucket["vaka"] += 1
        bucket[verdict] += 1
        if reason:
            bucket["nedenler"][reason] = bucket["nedenler"].get(reason, 0) + 1
        records.append({"id": case["id"], "component": case["component"], "kind": kind,
                        "girdi": case["inputs"], "http_status": outcome.get("http_status"),
                        "api_error": outcome.get("error"), "api_status": (row or {}).get("status"),
                        "api_value": api_val, "utilization_ratio": utilization, "independent_value": ref,
                        "relative_error": abs(api_val-ref)/abs(ref) if api_val is not None else None,
                        "kontrol": verdict, "neden": reason, "api_payload": payload})
    (OUT / "results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (OUT / "kontrol.json").write_text(json.dumps(counts, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print("vaka=300 " + " ".join(f"{c}: uyuşur={counts[c]['UYUŞUR']} uyuşmaz={counts[c]['UYUŞMUYOR']} veri_yok={counts[c]['VERİ_YOK']}" for c in counts))
    return records


if __name__ == "__main__":
    run()
