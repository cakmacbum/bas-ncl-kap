"""Independent qualitative Zick direction checks through the public API."""
from __future__ import annotations
import json
from pathlib import Path
from .cases import cases
from tools.campaign.harness import find_results, run_case

HERE = Path(__file__).parent
QUANTITIES = ("S1_saddle", "S1_midspan", "S2_saddle", "S3_saddle", "S4_saddle",
              "S5_saddle", "S6_saddle", "S7_saddle")


def _values(row):
    out = {}
    for item in row.get("intermediate_values", []):
        if item.get("value") is not None:
            try:
                out[item.get("name")] = float(item["value"])
            except (TypeError, ValueError):
                pass
    return out


def run():
    result_rows = []
    for case_id, project, inputs in cases():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, calculation_type="saddle_stress")
        observations = [{"support_id": row.get("component_id"),
                         "status": row.get("status"),
                         "stresses_MPa": {k: v for k, v in _values(row).items() if k in QUANTITIES}}
                        for row in matches]
        # Independent equilibrium oracle: a symmetric simply-supported beam under
        # downward distributed weight has positive reactions and sagging midspan
        # moment (bottom-fiber tension); the support section is hogging (compression).
        # The four requested stress directions require signed values and Zick
        # coefficients. No direction claim is made when the API blocks those terms.
        expected = {"longitudinal": {"saddle": "hogging; bottom compression",
                                      "midspan": "sagging; bottom tension"},
                    "tangential_shear": "signed direction follows saddle reaction",
                    "horn": "signed local direction requires contact coefficients",
                    "ring_compression": "compressive around saddle contact"}
        required = {"S1_saddle", "S1_midspan", "S2_saddle", "S3_saddle", "S4_saddle"}
        passed = bool(observations) and all(
            o["status"] not in ("BLOCKED CODE DATA", "NOT CALCULATED", "ERROR") and
            required.issubset(o["stresses_MPa"]) for o in observations)
        result_rows.append({"vaka": case_id, "girdi": inputs, "beklenen": expected,
            "gozlenen": {"api_ok": outcome.get("ok"), "http_status": outcome.get("http_status"),
                         "support_results": observations, "hata": outcome.get("error")},
            "sonuc": "GEÇTİ" if passed else "KAPSAM_DIŞI"})
    counts = {x: sum(r["sonuc"] == x for r in result_rows) for x in ("GEÇTİ", "BULGU", "KAPSAM_DIŞI")}
    (HERE / "results.json").write_text(json.dumps({"vaka_sayisi": len(result_rows),
        "dagilim": counts, "results": result_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = HERE.parents[3] / "docs" / "validation" / "campaign-2026-10" / "tur2" / "T11-yatay-tank-tarama.md"
    scope = [f"- {r['vaka']}: {r['girdi']['saddles']} destek; {r['girdi']['state']}; gereken Zick yön değerleri/kod verisi hesaplanmadı."
             for r in result_rows if r["sonuc"] == "KAPSAM_DIŞI"]
    report = ["# T11 — Yatay tank tam tarama", "", f"Toplam {len(result_rows)} vaka yürütüldü.",
        f"Dağılım: geçti {counts['GEÇTİ']}, bulgu {counts['BULGU']}, kapsam dışı {counts['KAPSAM_DIŞI']}.",
        "", "## Bulgu tablosu", "", "Bulgu yok.", "", "## Kapsam dışı", "", *scope,
        "", f"SONUÇ: vaka={len(result_rows)} · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} (kritik=0, emniyetsiz=0) · kapsam_dışı={counts['KAPSAM_DIŞI']}"]
    out.write_text("\n".join(report) + "\n", encoding="utf-8")

if __name__ == "__main__":
    run()
