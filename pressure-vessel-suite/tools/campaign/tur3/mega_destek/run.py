"""Seeded 110-case support geometry campaign through the public API."""
from __future__ import annotations

import json
import math
import random
from copy import deepcopy
from pathlib import Path

from tools.campaign.bases import horizontal_saddle_tank, skirt_column, vertical_leg_tank
from tools.campaign.harness import run_case

OUT = Path(__file__).with_name("results.json")


def generate_cases() -> list[tuple[str, dict]]:
    rng = random.Random(1002)
    cases: list[tuple[str, dict]] = []
    for i in range(110):
        family = ("vertical_leg", "horizontal_saddle", "skirt")[i % 3]
        if family == "vertical_leg":
            project = vertical_leg_tank()
            project["supports"][0].update(
                location_mm=rng.randint(350, 750), leg_count=rng.choice((3, 4, 6)),
                leg_diameter_mm=rng.choice((88.9, 101.6, 114.3, 139.7)),
                leg_thickness_mm=rng.choice((6, 8, 10)),
                leg_pad_thickness_mm=rng.choice((8, 10, 12, 16)))
        elif family == "horizontal_saddle":
            project = horizontal_saddle_tank()
            separation = rng.randint(900, 1450)
            project["supports"][0].update(location_mm=rng.randint(250, 500), width_mm=rng.randint(180, 320))
            project["supports"][1].update(location_mm=project["supports"][0]["location_mm"] + separation,
                                          width_mm=rng.randint(180, 320),
                                          contact_angle_deg=rng.choice((100, 120, 140)),
                                          saddle_stiffened=rng.choice((True, False)),
                                          zick_K1=1.0, zick_K2=1.0, zick_K6=1.0, zick_K7=1.0)
        else:
            project = skirt_column()
            project["supports"][0].update(
                diameter_mm=rng.randint(850, 1200), thickness_mm=rng.choice((6, 8, 10, 12)),
                height_mm=rng.randint(900, 1600), skirt_allowable_compressive_MPa=100)
        project["project_number"] = f"T31-{i + 1:03d}"
        project["project_name"] = f"T31 mega support {i + 1:03d}"
        cases.append((family, project))
    return cases


def _walk_numbers(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_numbers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_numbers(child)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield float(value)


def _required(payload: dict) -> float | None:
    vals = [float(item["value"]) for result in payload.get("results", [])
            for item in result.get("intermediate_values", [])
            if item.get("name") == "t_required" and isinstance(item.get("value"), (int, float))]
    return max(vals) if vals else None


def _check(response: dict, probe: dict) -> tuple[list[str], list[str]]:
    findings, controls = [], []
    payload = response.get("payload")
    if response.get("http_status") == 500 or (payload is not None and any(
            not math.isfinite(n) for n in _walk_numbers(payload))):
        findings.append("sağlamlık")
    rows = payload.get("results", []) if payload else []
    checked = 0
    for row in rows:
        status = str(row.get("status", "")).upper()
        util = row.get("utilization_ratio")
        if status in ("PASS", "FAIL") and isinstance(util, (int, float)):
            checked += 1
            if (status == "PASS" and util > 1.0) or (status == "FAIL" and util <= 1.0):
                findings.append("tutarlılık")
                break
    if checked:
        controls.append("tutarlılık")
    base_t, probe_t = _required(payload or {}), _required(probe.get("payload") or {})
    if base_t is not None and probe_t is not None:
        controls.append("monotonluk")
        if probe_t > base_t + 1e-9:
            findings.append("monotonluk")
    if not response.get("ok") and response.get("http_status") not in (500,):
        controls.append("API/hesap")
    return list(dict.fromkeys(findings)), controls


def main() -> None:
    records = []
    for i, (family, project) in enumerate(generate_cases(), 1):
        response = run_case(project)
        probe_project = deepcopy(project)
        for material in probe_project.get("materials", []):
            material["allowable_stress"] *= 1.2
        probe = run_case(probe_project)
        findings, controls = _check(response, probe)
        status = "BULGU" if findings else ("BLOCKED_BEKLENEN" if not controls else "GEÇTİ")
        records.append({"id": f"T31-{i:03d}", "family": family, "girdi": project,
                        "sonuc": response, "kontrol": controls + findings, "durum": status})
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    counts = {s: sum(r["durum"] == s for r in records) for s in ("GEÇTİ", "BULGU", "BLOCKED_BEKLENEN")}
    first = [r["id"] for r in records if r["durum"] == "BULGU"][:10]
    print(f"Vaka={len(records)} GEÇTİ={counts['GEÇTİ']} BULGU={counts['BULGU']} BLOCKED={counts['BLOCKED_BEKLENEN']}")
    print("İlk 10 BULGU: " + (", ".join(first) if first else "yok"))


if __name__ == "__main__":
    main()
