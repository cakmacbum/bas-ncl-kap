"""Run 110 seeded nozzle cases against the public calculation API."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from tools.campaign.examples import example_nozzle_reinforcement
from tools.campaign.harness import CAMPAIGN_CLIENT_ID, find_results, run_case, value_of

OUT = Path(__file__).resolve().parent
FAMILY = "T32-mega-nozul"


def cases():
    rng = random.Random(1003)
    result = []
    for i in range(55):
        host = "shell" if i % 2 == 0 else "head"
        p = example_nozzle_reinforcement()
        section = p["shell_sections"][0]
        head = p["heads"][0]
        host_id = "SHELL-01" if host == "shell" else head["head_id"]
        diameter = section["inside_diameter"] if host == "shell" else head["inside_diameter"]
        thickness = section["nominal_thickness"] if host == "shell" else head["nominal_thickness"]
        d = round(rng.uniform(45, min(240, diameter * 0.32)), 2)
        tn = round(rng.uniform(5, 16), 2)
        nz = p["nozzles"][0]
        nz.update(host_component_id=host_id, outside_diameter=d + 2 * tn,
                  inside_diameter=d, neck_thickness=tn,
                  axial_position=round(rng.uniform(150, 1800), 2),
                  outside_projection=round(rng.uniform(0, 180), 2),
                  reinforcement_pad=False)
        # Head nozzles use a centered/near-center axial coordinate; the API
        # model uses this shared positional field for both host types.
        base_pressure = round(rng.uniform(0.35, 1.8), 4)
        p["shell_sections"][0]["nominal_thickness"] = thickness
        for factor, suffix in ((1.0, "low"), (1.2, "high")):
            project = json.loads(json.dumps(p))
            project["project_number"] = f"T32-{i:03d}-{suffix}"
            project["project_name"] = f"T32 mega nozzle {i:03d} {suffix}"
            project["design_conditions"]["design_pressure"] = round(base_pressure * factor, 4)
            result.append((f"T32-{i:03d}-{suffix}", host, project,
                           f"PAIR-{i:03d}", base_pressure * factor))
    return result


def _finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite(v) for v in value)
    return True


def _utilization(row):
    for key in ("utilization_ratio", "utilization", "utilisation"):
        if isinstance(row.get(key), (int, float)):
            return float(row[key])
    for name in ("utilization", "utilisation", "utilization_ratio", "U"):
        value = value_of(row, name)
        if value is not None:
            return value
    final = row.get("final_result")
    if isinstance(final, dict):
        for key in ("utilization", "utilisation", "utilization_ratio", "U"):
            if isinstance(final.get(key), (int, float)):
                return float(final[key])
    return None


def _release_campaign_project():
    """Keep this in-memory API campaign below its per-client 50-project cap."""
    from apps.api.store import store
    with store._lock:
        for project_id, (owner, _) in list(store._items.items()):
            if owner == f"anon:{CAMPAIGN_CLIENT_ID}":
                del store._items[project_id]


def run():
    records = []
    evaluated = {}
    for case_id, host, project, pair, pressure in cases():
        outcome = run_case(project)
        _release_campaign_project()
        payload = outcome.get("payload") or {}
        all_rows = payload.get("results", [])
        nozzle_rows = find_results(payload, component_id="N1")
        checks = []
        findings = []
        if outcome.get("http_status") == 500:
            findings.append({"ad": "HTTP 500", "gozlenen": outcome.get("error")})
        if not _finite(outcome):
            findings.append({"ad": "NaN/inf", "gozlenen": "API sonucu sonlu değil"})
        if not outcome.get("ok"):
            status = "BULGU" if outcome.get("http_status") == 500 else "BLOCKED_BEKLENEN"
            checks.append({"ad": "API", "gozlenen": outcome.get("error") or outcome.get("http_status")})
        else:
            status = "GEÇTİ"
            if not nozzle_rows:
                status = "BLOCKED_BEKLENEN"
                checks.append({"ad": "nozzle_reinforcement", "gozlenen": "N1 sonucu yok"})
            for row in nozzle_rows:
                state = str(row.get("status", "")).upper().replace("_", " ")
                if state not in {"PASS", "FAIL"}:
                    continue
                util = _utilization(row)
                if state.startswith("BLOCKED") or state in {"NOT CALCULATED", "OUT OF SCOPE"} or util is None:
                    status = "BLOCKED_BEKLENEN" if status == "GEÇTİ" else status
                    checks.append({"ad": "utilization", "durum": state, "gozlenen": util})
                elif ((state == "PASS" or state.startswith("PASS ")) and util > 1.0) or ((state == "FAIL" or state.startswith("FAIL ")) and util <= 1.0):
                    status = "BULGU"
                    checks.append({"ad": "PASS/FAIL-utilization", "durum": state, "gozlenen": util})
                else:
                    checks.append({"ad": "PASS/FAIL-utilization", "durum": state, "gozlenen": util})
        evaluated[(pair, "high" if case_id.endswith("high") else "low")] = (case_id, all_rows)
        input_summary = {"host": host, "nozzle": project["nozzles"][0],
                         "P_MPa": pressure, "pair": pair}
        records.append({"id": case_id, "family": FAMILY, "girdi": input_summary,
                        "sonuc": outcome, "kontrol": checks, "durum": status})

    # Compare t_required at each higher-pressure member with its paired baseline.
    by_id = {r["id"]: r for r in records}
    for i in range(55):
        low_id, high_id = f"T32-{i:03d}-low", f"T32-{i:03d}-high"
        low_rows = find_results({"results": evaluated[(f"PAIR-{i:03d}", "low")][1]}, calculation_type="thickness")
        high_rows = find_results({"results": evaluated[(f"PAIR-{i:03d}", "high")][1]}, calculation_type="thickness")
        comp = "SHELL-01" if i % 2 == 0 else "HEAD-L"
        low = next((value_of(r, "t_required") for r in low_rows if r.get("component_id") == comp), None)
        high = next((value_of(r, "t_required") for r in high_rows if r.get("component_id") == comp), None)
        ctrl = {"ad": "monotonluk-t_required", "beklenen": "P +%20 iken t_required artar/eşit",
                "dusuk": low, "yuksek": high}
        if low is None or high is None:
            ctrl["durum"] = "BLOCKED_BEKLENEN"
            for cid in (low_id, high_id):
                by_id[cid]["kontrol"].append(ctrl.copy())
                if by_id[cid]["durum"] == "GEÇTİ":
                    by_id[cid]["durum"] = "BLOCKED_BEKLENEN"
        else:
            ctrl["durum"] = "GEÇTİ" if high >= low else "BULGU"
            for cid in (low_id, high_id):
                by_id[cid]["kontrol"].append(ctrl.copy())
                if high < low:
                    by_id[cid]["durum"] = "BULGU"

    path = OUT / "results.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    counts = {name: sum(r["durum"] == name for r in records)
              for name in ("GEÇTİ", "BULGU", "BLOCKED_BEKLENEN")}
    bugs = [r["id"] for r in records if r["durum"] == "BULGU"]
    print(f"vaka={len(records)} GEÇTİ={counts['GEÇTİ']} BULGU={counts['BULGU']} BLOCKED={counts['BLOCKED_BEKLENEN']}")
    print("İlk 10 BULGU: " + (", ".join(bugs[:10]) if bugs else "yok"))
    _write_report(records, counts)
    return records


def _write_report(records, counts):
    report = OUT.parents[3] / "docs" / "validation" / "campaign-2026-10" / "tur3" / "T32-mega-nozul.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# T32 Mega Nozul — Gövde ve Bombe Rastgele Taraması", "",
             "Seed: `1003`; 55 geometri × düşük/yüksek basınç çifti; toplam 110 API vakası.", "",
             "| Durum | Adet |", "|---|---:|",
             f"| GEÇTİ | {counts['GEÇTİ']} |", f"| BULGU | {counts['BULGU']} |",
             f"| BLOCKED_BEKLENEN | {counts['BLOCKED_BEKLENEN']} |", "", "## BULGU vakaları", ""]
    bugs = [r for r in records if r["durum"] == "BULGU"]
    if bugs:
        for row in bugs:
            for check in row["kontrol"]:
                lines.append(f"- `{row['id']}` — girdi özeti: host={row['girdi']['host']}, P={row['girdi']['P_MPa']} MPa, "
                             f"nozul OD/ID/t={row['girdi']['nozzle'].get('outside_diameter')}/"
                             f"{row['girdi']['nozzle'].get('inside_diameter')}/{row['girdi']['nozzle'].get('neck_thickness')} mm; "
                             f"kontrol: {check.get('ad')}; beklenen={check.get('beklenen', 'tutarlılık şartı')}; "
                             f"gözlenen={check.get('gozlenen', check.get('durum', check))}")
    else:
        lines.append("BULGU yok.")
    lines += ["", f"SONUÇ: vaka=110 · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} · blocked={counts['BLOCKED_BEKLENEN']}", ""]
    report.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()
