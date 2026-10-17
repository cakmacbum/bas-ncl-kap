"""Seeded pressure, wind, seismic, and mixed-load API campaign."""
from __future__ import annotations

import json
import math
import random
from copy import deepcopy
from pathlib import Path

from tools.campaign.bases import horizontal_saddle_tank, skirt_column, vertical_leg_tank
from tools.campaign.harness import find_results, run_case

OUT = Path(__file__).with_name("results.json")
COUNT = 110


def _finite_tree(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite_tree(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite_tree(v) for v in value)
    return True


def _project(rng: random.Random, index: int) -> tuple[dict, str]:
    # Even/odd pairs share geometry and loads; the second has 20% higher allowable stress S.
    pair = index // 2
    family = ("vertical", "horizontal", "skirt")[pair % 3]
    project = {"vertical": vertical_leg_tank, "horizontal": horizontal_saddle_tank,
               "skirt": skirt_column}[family]()
    project = deepcopy(project)
    project["project_number"] = f"T33-{index + 1:03d}"
    conditions = project["design_conditions"]
    base_pressure = rng.uniform(0.25, 1.25)
    conditions["design_pressure"] = base_pressure
    conditions["operating_pressure"] = conditions["design_pressure"] * rng.uniform(.65, .95)
    if index % 2:
        for material in project.get("materials", []):
            if isinstance(material.get("allowable_stress"), (int, float)):
                material["allowable_stress"] *= 1.2
    load_kind = ("wind", "seismic", "mixed")[pair % 3]
    cases = []
    if load_kind in ("wind", "mixed"):
        cases.append({"load_case_id": f"W-{index}", "name": "Seeded wind", "load_type": "wind",
                      "wind_speed_m_s": rng.uniform(15, 55),
                      "external_loads": [{"load_id": f"WF-{index}", "component_id": "SHELL-01",
                          "fx_n": rng.uniform(100, 12000), "my_nmm": rng.uniform(1e4, 2e6)}]})
    if load_kind in ("seismic", "mixed"):
        cases.append({"load_case_id": f"E-{index}", "name": "Seeded seismic", "load_type": "seismic",
                      "seismic_zone_factor": rng.uniform(.05, .6),
                      "external_loads": [{"load_id": f"EF-{index}", "component_id": "SHELL-01",
                          "fx_n": rng.uniform(100, 12000), "my_nmm": rng.uniform(1e4, 2e6)}]})
    project["load_cases"] = cases
    return project, f"{family}_{load_kind}"


def _check(result: dict) -> tuple[list[str], dict]:
    controls = []
    payload = result.get("payload") or {}
    if result.get("http_status") == 500:
        controls.append("HTTP_500")
    if not _finite_tree(payload):
        controls.append("NaN_INF")
    rows = payload.get("results", [])
    for row in rows:
        status = str(row.get("status", "")).upper()
        utilization = row.get("utilization_ratio")
        if utilization is None:
            utilization = next((v.get("value") for v in row.get("intermediate_values", [])
                                if v.get("name") in ("utilization", "utilization_ratio")), None)
        if isinstance(utilization, (int, float)):
            if status == "PASS" and utilization > 1.0:
                controls.append(f"TUTARLILIK_{row.get('component_id')}:PASS>{utilization:.6g}")
            elif status == "FAIL" and utilization <= 1.0:
                controls.append(f"TUTARLILIK_{row.get('component_id')}:FAIL<={utilization:.6g}")
    blocked = (not result.get("ok") or any(str(r.get("status", "")).upper() in
               {"BLOCKED MISSING INPUT", "BLOCKED CODE DATA", "NOT CALCULATED"} for r in rows))
    summary = {"http_status": result.get("http_status"), "ok": result.get("ok"),
               "row_count": len(rows), "rows": [{"component_id": r.get("component_id"),
                   "calculation_type": r.get("calculation_type"), "status": r.get("status"),
                   "utilization_ratio": r.get("utilization_ratio"),
                   "t_required": next((v.get("value") for v in r.get("intermediate_values", [])
                                       if v.get("name") == "t_required"), None)} for r in rows]}
    return controls, {"summary": summary, "blocked": blocked}


def main() -> None:
    records = []
    monotonic_by_pair: dict[int, list[tuple[str, float | None]]] = {}
    for index in range(COUNT):
        project, family = _project(random.Random(1004 + index // 2), index)
        response = run_case(project)
        controls, check = _check(response)
        pair = index // 2
        t_values = [row.get("t_required") for row in check["summary"]["rows"]
                    if row.get("calculation_type") == "thickness" and row.get("t_required") is not None]
        monotonic_by_pair.setdefault(pair, []).append((f"T33-{index + 1:03d}", max(t_values) if t_values else None))
        records.append({"id": f"T33-{index + 1:03d}", "family": family,
                        "girdi": {"design_pressure": project["design_conditions"].get("design_pressure"),
                                  "loads": project.get("load_cases", [])},
                        "sonuc": check["summary"], "kontrol": controls or ["SAĞLAMLIK", "TUTARLILIK"],
                        "durum": "BULGU" if controls else ("BLOCKED_BEKLENEN" if check["blocked"] else "GEÇTİ")})
    for pair, values in monotonic_by_pair.items():
        if len(values) == 2 and all(v is not None for _, v in values) and values[1][1] > values[0][1] + 1e-9:
            target = records[pair * 2 + 1]
            target["kontrol"].append(f"MONOTONLUK {values[0][0]}→{values[1][0]}: t_required arttı")
            target["durum"] = "BULGU"
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    counts = {status: sum(r["durum"] == status for r in records)
              for status in ("GEÇTİ", "BULGU", "BLOCKED_BEKLENEN")}
    findings = [r for r in records if r["durum"] == "BULGU"]
    print(f"vaka={len(records)} geçti={counts['GEÇTİ']} bulgu={counts['BULGU']} blocked={counts['BLOCKED_BEKLENEN']}")
    print("ilk_10_bulgu=" + ",".join(r["id"] for r in findings[:10]))
    report = Path(__file__).resolve().parents[4] / "docs" / "validation" / "campaign-2026-10" / "tur3" / "T33-mega-yuk.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# T33 Mega yük — basınç, rüzgâr ve deprem taraması", "",
             "Tohum: `1004`; vaka sayısı: `110`. Her vaka `harness.run_case` ile `/api/projects` ve `/calculate` üzerinden çalıştırıldı.", "",
             "| Durum | Sayı |", "|---|---:|",
             f"| GEÇTİ | {counts['GEÇTİ']} |", f"| BULGU | {counts['BULGU']} |",
             f"| BLOCKED_BEKLENEN | {counts['BLOCKED_BEKLENEN']} |", "", "## Bulgular", ""]
    for item in findings:
        lines.append(f"- **{item['id']}** ({item['family']}): kontrol `{', '.join(item['kontrol'])}`; "
                     f"girdi: tasarım basıncı {item['girdi']['design_pressure']:.6g} MPa, "
                     f"yükler {', '.join(c['load_type'] for c in item['girdi']['loads']) or 'yok'}; "
                     f"sonuç HTTP {item['sonuc']['http_status']}, {item['sonuc']['row_count']} satır.")
    lines += ["", f"SONUÇ: vaka={len(records)} · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} · blocked={counts['BLOCKED_BEKLENEN']}", ""]
    report.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
