"""Seeded 300-case pressure-head thickness campaign."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import find_results, run_case, value_of


HERE = Path(__file__).resolve().parent
SEED = 60


def _case(rng: random.Random, number: int, kind: str) -> tuple[dict, dict]:
    project = vertical_leg_tank()
    diameter = round(rng.uniform(500.0, 1800.0), 1)
    nominal = round(rng.uniform(6.0, 30.0), 2)
    ca = round(rng.uniform(0.0, 3.0), 2)
    mill = round(rng.uniform(0.0, 15.0), 2)
    stress = round(rng.uniform(90.0, 180.0), 2)
    efficiency = rng.choice((0.7, 0.85, 0.9, 1.0))
    pressure = round(rng.uniform(0.2, 3.0), 3)
    for head in project["heads"]:
        head["type"] = kind
        head["inside_diameter"] = diameter
        head["nominal_thickness"] = nominal
        head["internal_corrosion_allowance"] = ca
        head["mill_tolerance"] = mill
    for material in project["materials"]:
        material["allowable_stress"] = stress
    for weld in project["welds"]:
        weld["joint_efficiency"] = efficiency
    project["design_conditions"]["design_pressure"] = pressure

    if kind == "torispherical":
        crown = round(diameter * rng.uniform(0.78, 1.0), 2)
        knuckle = round(rng.uniform(max(15.0, 0.06 * diameter), min(0.18 * diameter, crown / 3)), 2)
        for head in project["heads"]:
            head["crown_radius"] = crown
            head["knuckle_radius"] = knuckle
    else:
        crown = diameter / 2 + ca
        knuckle = None

    inputs = {"D_i": diameter, "nominal_thickness": nominal, "CA_i": ca,
              "mill": mill, "S": stress, "E": efficiency, "P": pressure,
              "crown_radius": crown, "knuckle_radius": knuckle}
    return project, inputs


def _independent(kind: str, x: dict) -> float | None:
    p, s, e = x["P"], x["S"], x["E"]
    denominator = 2 * s * e - 0.2 * p
    if denominator <= 0:
        return None
    if kind == "hemispherical":
        return p * (x["D_i"] / 2 + x["CA_i"]) / denominator
    crown, knuckle = x["crown_radius"], x["knuckle_radius"]
    factor = 0.25 * (3 + math.sqrt(crown / knuckle))
    return p * crown * factor / denominator


def _api_thickness(payload: dict) -> float | None:
    rows = find_results(payload, component_id="HEAD-L")
    for row in rows:
        val = value_of(row, "t_required")
        if val is not None:
            return val
    for row in find_results(payload):
        val = value_of(row, "t_required")
        if val is not None:
            return val
    return None


def main() -> None:
    rng = random.Random(SEED)
    results = []
    for i in range(300):
        kind = "hemispherical" if i < 150 else "torispherical"
        project, inputs = _case(rng, i + 1, kind)
        response = run_case(project)
        payload = response.get("payload") or {}
        api_t = _api_thickness(payload)
        calculated = _independent(kind, inputs)
        if api_t is None:
            state = "VERİ_YOK"
        elif calculated is None:
            state = "VERİ_YOK"
        elif abs(api_t - calculated) <= 0.01 * max(abs(api_t), abs(calculated), 1e-12):
            state = "UYUŞUR"
        else:
            state = "UYUŞMUYOR"
        results.append({"id": f"T60-{i + 1:03d}", "tip": kind, "girdi": inputs,
                        "api_t": api_t, "t_hesap": calculated, "durum": state,
                        "api_ok": response.get("ok"), "api_error": response.get("error")})

    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {key: sum(row["durum"] == key for row in results)
              for key in ("UYUŞUR", "UYUŞMUYOR", "VERİ_YOK", "KAPSAM_DIŞI")}
    print(f"vaka={len(results)} · uyuşur={counts['UYUŞUR']} · uyuşmaz={counts['UYUŞMUYOR']} · veri_yok={counts['VERİ_YOK']} · kapsam_dışı={counts['KAPSAM_DIŞI']}")
    report = ("# T60 — Bombe kalınlığı toplu tarama\n\n"
              "Tohum 60 ile 150 yarım küre ve 150 torisferik vaka üretildi. Her API vakası `run_case` ile çalıştırıldı.\n\n"
              "Bağımsız hesaplar UG-32(f) yarım küre ve UG-32(e) torisferik denklemlerini kullandı. Torisferik denetim t_req karşılaştırmasıyla sınırlıdır. Uyuşma ölçütü ±%1'dir.\n\n"
              f"API başarı bayrağı: {sum(row['api_ok'] is True for row in results)}/300. Ayrıntılar `results.json` dosyasındadır.\n\n"
              f"SONUÇ: vaka=300 · uyuşur={counts['UYUŞUR']} · uyuşmaz={counts['UYUŞMUYOR']} · veri_yok={counts['VERİ_YOK']} · kapsam_dışı={counts['KAPSAM_DIŞI']}\n")
    report_path = HERE.parents[4] / "docs" / "validation" / "campaign-2026-10" / "tur5" / "T60-bombe-tarama.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
