"""Execute seeded projects and check numeric/status invariants."""
import json
import math
from pathlib import Path
from tools.campaign.harness import run_case
from .cases import COUNT, SEED, cases
HERE = Path(__file__).resolve().parent

def numeric_issues(value, path="$", issues=None):
    issues = issues if issues is not None else []
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(float(value)): issues.append(f"non-finite at {path}")
    elif isinstance(value, dict):
        for k, v in value.items(): numeric_issues(v, f"{path}.{k}", issues)
    elif isinstance(value, list):
        for i, v in enumerate(value): numeric_issues(v, f"{path}[{i}]", issues)
    return issues

def inspect(outcome):
    issues = []
    if outcome.get("http_status") == 500: issues.append("HTTP 500")
    payload = outcome.get("payload") or {}
    numeric_issues(payload, issues=issues)
    for row in payload.get("results", []):
        status = str(row.get("status", "")).upper()
        vals = row.get("intermediate_values", [])
        util = next((v.get("value") for v in vals if "utilization" in str(v.get("name", "")).lower()), None)
        final = row.get("final_result")
        if util is None and isinstance(final, dict):
            util = next((v for k, v in final.items() if "utilization" in str(k).lower()), None)
        if isinstance(util, (int, float)):
            if status == "PASS" and util > 1+1e-9: issues.append(f"PASS utilization={util}")
            if status == "FAIL" and util <= 1: issues.append(f"FAIL utilization={util}")
    return issues

def run():
    rows = []
    for case in cases():
        out = run_case(case["project"])
        issues = inspect(out)
        status = "BULGU" if issues or out.get("http_status") == 500 else "GEÇTİ"
        if out.get("http_status") not in (200, 201, 500): status = "KAPSAM_DIŞI"
        rows.append({"vaka": case["case_id"], "temel": case["base"], "girdi": case["project"],
            "beklenen": {"http_500": False, "finite": True, "checks": ["PASS utilization <= 1", "FAIL utilization > 1"]},
            "gozlenen": {"http_status": out.get("http_status"), "ok": out.get("ok"),
                          "error": out.get("error"), "payload": out.get("payload")},
            "sonuc": status, "bulgular": issues})
    (HERE / "results.json").write_text(json.dumps({"seed": SEED, "vaka_sayisi": len(rows), "vakalar": rows},
        ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return rows

if __name__ == "__main__": run()


