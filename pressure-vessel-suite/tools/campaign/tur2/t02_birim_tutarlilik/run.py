"""Execute T02 scale/unit consistency probes through the shared API harness."""
from __future__ import annotations

import json
from pathlib import Path

from tools.campaign.harness import find_results, run_case, value_of
from tools.campaign.tur2.t02_birim_tutarlilik.cases import variants


HERE = Path(__file__).resolve().parent
TOLERANCE = 0.001  # 0.1 percent


def _shell_value(outcome):
    payload = outcome.get("payload") or {}
    result = next(iter(find_results(payload, component_id="SHELL-01",
                                    calculation_type="internal_pressure")), None)
    if result is None:
        result = next(iter(find_results(payload, component_id="SHELL-01")), None)
    return (value_of(result, "t_required"), result) if result else (None, None)


def run():
    records = []
    baseline = None
    baseline_error = None
    for case_id, project, params in variants():
        outcome = run_case(project)
        observed, result = _shell_value(outcome)
        if case_id == "BASE":
            baseline = observed
            baseline_error = outcome.get("error")
        expected = (baseline * params["scale"] / 25.4
                    if params["unit_system"] == "Imperial" and baseline is not None else
                    baseline * params["scale"] if baseline is not None else None)
        if case_id == "BASE":
            expected = observed
        if expected is None or observed is None:
            verdict = "KAPSAM_DIŞI"
        else:
            relative_error = abs(observed - expected) / abs(expected) if expected else 0.0
            verdict = "GEÇTİ" if relative_error <= TOLERANCE else "BULGU"
        records.append({
            "vaka": case_id,
            "girdi": {**params, "design_pressure_mpa": project["design_conditions"]["design_pressure"],
                      "shell_inside_diameter_mm": project["shell_sections"][0].get("inside_diameter"),
                      "shell_nominal_thickness_mm": project["shell_sections"][0]["nominal_thickness"]},
            "beklenen": expected,
            "gozlenen": observed,
            "sonuc": verdict,
            "birim": "mm t_required (Imperial vakada beklenen inç)",
            "durum": result.get("status") if result else None,
            "hata": outcome.get("error"),
        })
    out = {"paket": "T02-birim-tutarlilik", "metrik": "SHELL-01 required_thickness",
           "tolerans_yuzde": TOLERANCE * 100, "baseline_hata": baseline_error, "vakalar": records}
    (HERE / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    result = run()
    print(f"T02: {len(result['vakalar'])} vakada sonuç yazıldı: {HERE / 'results.json'}")
