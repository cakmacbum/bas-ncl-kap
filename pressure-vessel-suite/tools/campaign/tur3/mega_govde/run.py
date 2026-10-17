"""Run 110 seeded shell thickness checks through the public API."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import find_results, run_case, value_of

HERE = Path(__file__).resolve().parent
REPORT = HERE.parents[3] / "docs" / "validation" / "campaign-2026-10" / "tur3" / "T30-mega-govde.md"


def _cases():
    rng = random.Random(1001)
    for pair in range(55):
        diameter = rng.uniform(300, 4000)
        pressure = rng.uniform(.2, 8.0)
        stress = rng.choice((100.0, 120.0, 138.0, 150.0, 175.0, 200.0))
        efficiency = rng.choice((.7, .85, 1.0))
        cai, cao = rng.choice((0.0, 1.0, 2.0, 4.0)), rng.choice((0.0, 1.0, 2.0))
        mill = rng.choice((0.0, 6.0, 12.5))
        for step, multiplier in enumerate((1.0, 1.2)):
            project = vertical_leg_tank()
            project["project_number"] = f"T30-MEGA-{pair + 1:02d}-{step}"
            shell = project["shell_sections"][0]
            shell.update(inside_diameter=round(diameter, 3), outside_diameter=None,
                         nominal_thickness=20.0, internal_corrosion_allowance=cai,
                         external_corrosion_allowance=cao, mill_tolerance=mill)
            actual_pressure = pressure * multiplier
            project["design_conditions"].update(design_pressure=actual_pressure,
                operating_pressure=actual_pressure, maximum_allowable_pressure_ps=actual_pressure)
            project["materials"][0]["allowable_stress"] = stress
            project["welds"][0]["joint_efficiency"] = efficiency
            yield f"mega-{pair + 1:02d}-{step}", f"govde-p-{step}", project


def _finite(value):
    if isinstance(value, (float, int)):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def run():
    rows, prior = [], {}
    for case_id, family, project in _cases():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        results = find_results(payload, component_id="SHELL-01", clause_prefix="UG-27")
        thickness = next((r for r in results if r.get("calculation_type") == "thickness"), None)
        t_actual = value_of(thickness, "t_required") if thickness else None
        shell = project["shell_sections"][0]
        mat = next(m for m in project["materials"] if m["material_id"] == shell["material_id"])
        weld = next((w for w in project["welds"] if w["joint_id"] == shell.get("weld_joint_id")), None)
        p = project["design_conditions"]["design_pressure"]
        radius = shell["inside_diameter"] / 2 + shell["internal_corrosion_allowance"]
        denominator = mat["allowable_stress"] * (weld["joint_efficiency"] if weld else 1.0) - .6 * p
        expected = p * radius / denominator if denominator > 0 else None
        controls, findings = {}, []
        if outcome.get("http_status") == 500:
            controls["robustness"] = "HTTP 500"
            findings.append("robustness")
        elif not _finite(payload):
            controls["robustness"] = "NaN/inf"
            findings.append("robustness")
        else:
            controls["robustness"] = "OK"
        if thickness:
            utilization = thickness.get("utilization_ratio")
            if utilization is None:
                utilization = value_of(thickness, "utilization")
            if utilization is None and t_actual is not None:
                mill_factor = 1.0 - float(shell.get("mill_tolerance", 0.0)) / 100.0
                nominal_required = (t_actual + float(shell.get("internal_corrosion_allowance", 0.0)) +
                                    float(shell.get("external_corrosion_allowance", 0.0)) +
                                    float(shell.get("forming_thinning", 0.0))) / mill_factor
                utilization = nominal_required / float(shell["nominal_thickness"])
            status = str(thickness.get("status", "")).upper()
            if utilization is None:
                controls["consistency"] = "BLOCKED: utilization ratio missing"
            elif ((status.startswith("PASS") and utilization > 1.0) or
                  (status.startswith("FAIL") and utilization <= 1.0)):
                controls["consistency"] = {"status": status, "utilization": utilization}
                findings.append("consistency")
            else:
                controls["consistency"] = {"status": status, "utilization": utilization}
        else:
            controls["consistency"] = "BLOCKED: UG-27 thickness result missing"
        if expected is not None and t_actual is not None:
            delta = abs(t_actual - expected) / abs(expected) if expected else 0.0
            controls["independent_ug27"] = {"expected": expected, "actual": t_actual, "relative_error": delta}
            if delta > .01:
                controls["independent_ug27"]["hint"] = "pressure-vessel-suite/apps/api calculation implementation"
                findings.append("independent_ug27")
        else:
            controls["independent_ug27"] = "BLOCKED: expected or actual thickness unavailable"
        pair = case_id.rsplit("-", 1)[0]
        step = int(case_id.rsplit("-", 1)[1])
        if step == 1:
            old = prior.get(pair)
            if old is not None and t_actual is not None and old["t"] is not None and t_actual < old["t"]:
                controls["monotonicity"] = {"previous": old["t"], "increased_pressure": t_actual}
                findings.append("monotonicity")
                old["controls"]["monotonicity"] = controls["monotonicity"]
                old["durum"] = "BULGU"
            else:
                controls["monotonicity"] = "OK" if old and t_actual is not None else "BLOCKED: paired result unavailable"
        else:
            controls["monotonicity"] = "pending paired pressure case"
        summary = {"http_status": outcome.get("http_status"), "component_status": thickness.get("status") if thickness else None,
                   "t_required": t_actual, "error": outcome.get("error")}
        row = {"id": case_id, "family": family, "girdi": {"project": project["project_number"],
               "D_i": shell["inside_diameter"], "P": p, "S": mat["allowable_stress"],
               "E": weld["joint_efficiency"], "CAi": shell["internal_corrosion_allowance"],
               "CAo": shell["external_corrosion_allowance"], "mill_tolerance": shell["mill_tolerance"],
               "nominal_thickness": shell["nominal_thickness"]},
               "sonuc": summary, "kontrol": controls,
               "durum": "BULGU" if findings else ("BLOCKED_BEKLENEN" if not outcome.get("ok") or not thickness or controls["consistency"] == "BLOCKED: utilization ratio missing" else "GEÇTİ")}
        rows.append(row)
        if step == 0:
            prior[pair] = {"t": t_actual, "controls": controls, "durum": row["durum"]}

    counts = {state: sum(r["durum"] == state for r in rows) for state in ("GEÇTİ", "BULGU", "BLOCKED_BEKLENEN")}
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    findings = [r for r in rows if r["durum"] == "BULGU"]
    lines = ["# T30 mega gövde kampanyası", "", "Seed: 1001 · Vaka: 110", "",
             "| Durum | Sayı |", "|---|---:|"]
    lines.extend(f"| {name} | {counts[name]} |" for name in counts)
    lines.extend(["", "## Bulgular", ""])
    if findings:
        for row in findings:
            lines.append(f"- `{row['id']}` · girdi: D_i={row['girdi']['D_i']}, P={row['girdi']['P']}, S={row['girdi']['S']}, E={row['girdi']['E']}, CAi={row['girdi']['CAi']} · kontrol: {', '.join(k for k,v in row['kontrol'].items() if isinstance(v, dict) and k in ('robustness','consistency','monotonicity','independent_ug27')) or 'kontrol incelemesi'}")
    else:
        lines.append("Bulgu yok.")
    lines.extend(["", f"SONUÇ: vaka=110 · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} · blocked={counts['BLOCKED_BEKLENEN']}"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"vaka=110 · GEÇTİ={counts['GEÇTİ']} · BULGU={counts['BULGU']} · BLOCKED_BEKLENEN={counts['BLOCKED_BEKLENEN']}")
    print("İlk 10 BULGU: " + (", ".join(r["id"] for r in findings[:10]) or "yok"))


if __name__ == "__main__":
    run()
