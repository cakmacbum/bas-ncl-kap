"""Execute T03 boundary cases and write a machine-readable result table."""
from __future__ import annotations

import json
import math
from pathlib import Path

from tools.campaign.harness import run_case
from tools.campaign.tur2.t03_sinir_girdi.cases import build_cases

OUT = Path(__file__).resolve().parent / "results.json"


def _safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    return value


def _status(result: dict) -> tuple[str, list[str]]:
    http = result.get("http_status")
    if http == 422:
        return "GEÇTİ", ["422"]
    if http == 500 or http is None:
        return "BULGU", ["HTTP 500/yanıtsız"]
    if result.get("payload") is None:
        return "BULGU", [f"beklenmeyen HTTP {http}"]
    rows = result["payload"].get("results", [])
    statuses = [str(row.get("status", "")) for row in rows]
    upper = [s.upper() for s in statuses]
    safe = bool(upper) and all("BLOCKED" in s or "NOT CALCULATED" in s or "NOT_CALCULATED" in s for s in upper)
    if safe:
        return "GEÇTİ", statuses
    if not rows:
        return "GEÇTİ", ["NOT CALCULATED (sonuç satırı yok)"]
    if any("PASS" in s for s in upper):
        return "BULGU", statuses
    return "BULGU", statuses or ["durum yok"]


def main() -> int:
    results = []
    for case in build_cases():
        observed = run_case(case["project"])
        outcome, statuses = _status(observed)
        results.append({
            "vaka": case["id"], "girdi": case["input"],
            "beklenen": "422 veya BLOCKED/NOT CALCULATED",
            "gozlenen": {"http": observed.get("http_status"), "status": statuses,
                         "error": observed.get("error")},
            "sonuc": outcome,
        })
        print(f"{case['id']}: HTTP {observed.get('http_status')} | {', '.join(statuses)} | {outcome}")
    OUT.write_text(json.dumps(_safe(results), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    passed = sum(r["sonuc"] == "GEÇTİ" for r in results)
    findings = len(results) - passed
    print(f"TOPLAM vaka={len(results)} geçti={passed} bulgu={findings} sonuç={OUT}")
    # Findings are campaign data, not harness execution failures.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
