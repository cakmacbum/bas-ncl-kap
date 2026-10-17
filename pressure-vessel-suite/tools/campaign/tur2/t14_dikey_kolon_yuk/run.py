"""Run T14 and report presence of skirt stress and base-ring results."""
from tools.campaign.harness import find_results, run_case
from .cases import cases


def run():
    rows = []
    for case_id, project, params in cases():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        results = payload.get("results", [])
        skirt = find_results(payload, component_id="SKIRT-01",
                             calculation_type="skirt_stress")
        # The current public result schema has no separate skirt base-ring
        # calculation; accept an explicitly named base-ring result if exposed.
        base_ring = [r for r in results if "base_ring" in str(r.get("calculation_type", "")).lower()
                     or "base_ring" in str(r.get("component_id", "")).lower()]
        row = {"case_id": case_id, **params,
               "skirt_stress_present": bool(skirt),
               "base_ring_present": bool(base_ring),
               "status": "GEÇTİ" if skirt else "BULGU",
               "error": outcome.get("error")}
        rows.append(row)
        print(row)
    passed = sum(r["status"] == "GEÇTİ" for r in rows)
    findings = len(rows) - passed
    print(f"SONUÇ: vaka={len(rows)} · GEÇTİ={passed} · BULGU={findings} · BLOCKED=0 · KAPSAM_DIŞI=0 · geçersiz_test=0")
    return rows


if __name__ == "__main__":
    run()
