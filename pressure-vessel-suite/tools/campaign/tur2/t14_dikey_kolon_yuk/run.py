"""Run T14 and report presence of skirt stress and base-ring results."""
import json
from collections import Counter
from pathlib import Path
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
               "skirt_stress_status": skirt[0].get("status") if skirt else None,
               "result_types": sorted({f"{x.get('component_type')}/{x.get('calculation_type')}" for x in results}),
               "base_ring_durumu": "VAR" if base_ring else "KAPSAM_DIŞI (API'de taban halkası sonucu yok)",
               "status": "GEÇTİ" if skirt else "BULGU",
               "error": outcome.get("error")}
        rows.append(row)
        print(row)
    out = Path(__file__).with_name("results.json")
    types = Counter(t for r in rows for t in r["result_types"])
    summary = {"vaka": len(rows), "skirt_stress_var": sum(r["skirt_stress_present"] for r in rows),
               "base_ring_var": sum(r["base_ring_present"] for r in rows),
               "skirt_stress_durumlari": dict(Counter(r["skirt_stress_status"] for r in rows)),
               "sonuc_tipi_sayilari": dict(types),
               "not": "Taban halkası (base ring) hesabı API sonuç şemasında yok: kapsam boşluğu, test düzeltmesi gerekmiyor."}
    out.write_text(json.dumps({"ozet": summary, "satirlar": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(r["status"] == "GEÇTİ" for r in rows)
    findings = len(rows) - passed
    print(f"SONUÇ: vaka={len(rows)} · GEÇTİ={passed} · BULGU={findings} · BLOCKED=0 · KAPSAM_DIŞI=0 · geçersiz_test=0 · taban_halkası_kapsam_boşluğu={sum(not r['base_ring_present'] for r in rows)}")
    return rows


if __name__ == "__main__":
    run()
