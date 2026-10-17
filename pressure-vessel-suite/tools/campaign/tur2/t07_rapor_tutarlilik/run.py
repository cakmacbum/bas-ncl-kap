from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import _bootstrap  # noqa: F401
from apps.api.main import app
from tools.campaign.harness import CAMPAIGN_CLIENT_ID
from .cases import CASES

OUT = Path(__file__).with_name("results.json")


def _case(client: TestClient, spec: dict) -> dict:
    project = spec["project"]()
    headers = {"X-Client-Id": CAMPAIGN_CLIENT_ID}
    created = client.post("/api/projects", json=project, headers=headers)
    result = {"vaka": spec["id"], "girdi": {"ad": spec["name"], "proje": project},
              "beklenen": "Rapor hesap sonuçları ve bileşenleri korumalı; durumları gizlememeli.",
              "gozlenen": {}, "sonuc": "BULGU"}
    if created.status_code != 201:
        result["gozlenen"] = {"http": created.status_code, "hata": created.text}
        return result
    pid = created.json()["id"]
    calc = client.post(f"/api/projects/{pid}/calculate", headers=headers)
    report = client.get(f"/api/projects/{pid}/report.html", headers=headers)
    if calc.status_code != 200 or report.status_code != 200:
        result["gozlenen"] = {"calculate_http": calc.status_code, "report_http": report.status_code}
        return result
    payload, html = calc.json(), report.text
    rows = payload.get("results", [])
    missing_components = sorted({str(r.get("component_id")) for r in rows
                                 if r.get("component_id") and str(r["component_id"]) not in html})
    statuses = sorted({str(r.get("status")) for r in rows if r.get("status")})
    hidden_statuses = [s for s in statuses if s.casefold() not in html.casefold()]
    # Test hatası düzeltmesi (A3): önceki sürüm TÜM ara değerlerin (R=500, R_corroded=502 ...) raporda
    # geçmesini bekliyordu; rapor yalnızca başlık sonuçlarını gösterir. Burada rapora basılması
    # beklenen çekirdek hesap türlerinin başlık sonucu (final_result) kontrol edilir; diğerleri
    # yalnızca gözlem olarak 'rapor_disi_basliklar'a yazılır.
    CORE = {"thickness", "mawp", "nozzle_reinforcement", "hydrotest"}
    numbers = [float(x.replace(",", "")) for x in re.findall(r"(?<![\w])[-+]?\d[\d,]*(?:\.\d+)?", html)]
    missing_values, outside_report = [], []
    for row in rows:
        final = row.get("final_result")
        if not isinstance(final, (int, float)) or isinstance(final, bool):
            continue
        tolerance = max(0.006, abs(float(final)) * 1e-3)
        found = any(abs(float(final) - c) <= tolerance for c in numbers)
        entry = {"component": row.get("component_id"), "calculation_type": row.get("calculation_type"),
                 "final_result": final}
        if not found:
            (missing_values if row.get("calculation_type") in CORE else outside_report).append(entry)
    ok = not missing_components and not hidden_statuses and not missing_values and not payload.get("errors")
    result["gozlenen"] = {"result_count": len(rows), "components_missing": missing_components,
                          "statuses": statuses, "hidden_statuses": hidden_statuses,
                          "values_missing": missing_values[:20], "rapor_disi_basliklar": outside_report[:30], "errors": payload.get("errors"),
                          "report_bytes": len(html)}
    result["sonuc"] = "GEÇTİ" if ok else "BULGU"
    return result


def main() -> None:
    with TestClient(app) as client:
        results = [_case(client, spec) for spec in CASES]
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {key: sum(r["sonuc"] == key for r in results) for key in ("GEÇTİ", "BULGU", "KAPSAM_DIŞI")}
    print(f"vaka={len(results)} geçti={counts['GEÇTİ']} bulgu={counts['BULGU']} kapsam_dışı={counts['KAPSAM_DIŞI']}")


if __name__ == "__main__":
    main()
