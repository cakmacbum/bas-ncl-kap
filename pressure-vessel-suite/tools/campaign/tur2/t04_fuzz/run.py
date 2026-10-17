"""Execute seeded projects and record independent checks for each result."""
import json
import math
from pathlib import Path
from tools.campaign.harness import run_case
from .cases import COUNT, SEED, cases

HERE = Path(__file__).resolve().parent


def numeric_issues(value, path="$", issues=None):
    issues = issues if issues is not None else []
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(float(value)):
            issues.append(f"non-finite at {path}")
    elif isinstance(value, dict):
        for key, item in value.items():
            numeric_issues(item, f"{path}.{key}", issues)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            numeric_issues(item, f"{path}[{index}]", issues)
    return issues


def _values(row):
    found = {}
    for item in row.get("intermediate_values", []) or []:
        if isinstance(item, dict) and item.get("value") is not None:
            found[str(item.get("name", "")).lower()] = item["value"]
    final = row.get("final_result")
    if isinstance(final, dict):
        found.update({str(k).lower(): v for k, v in final.items()})
    return found


def _find(values, *terms):
    for key, value in values.items():
        if all(term in key for term in terms) and isinstance(value, (int, float)):
            return float(value)
    return None


def _check(name, observed, passed=None, scope=False):
    state = "KAPSAM_DIŞI" if scope else ("GEÇTİ" if passed else "BULGU")
    return {"ad": name, "durum": state, "gozlenen": observed}


def inspect(outcome, project):
    payload = outcome.get("payload") or {}
    result_rows = payload.get("results") or []
    finite = not numeric_issues(payload)
    checks = [_check("sonlu_sayi", "sonuç sayısal alanlarında NaN/inf yok" if finite else "NaN/inf bulundu", finite)]
    if not result_rows:
        checks.append(_check("sonuc_kapsami", "API sonuç satırı yok", scope=True))
    else:
        checks.append(_check("sonuc_kapsami", f"{len(result_rows)} sonuç satırı karşılaştırıldı", True))
    usage_rows = 0
    for row in result_rows:
        vals = _values(row)
        status = str(row.get("status", "")).upper()
        comp = str(row.get("component_type", "") or row.get("calculation_type", "") or row.get("component_id", "")).lower()
        reinforcement = "reinforcement" in comp or "reinforcement" in str(row.get("clause_reference", "")).lower()
        util = row.get("utilization_ratio") if isinstance(row.get("utilization_ratio"), (int, float)) else _find(vals, "utilization")
        if reinforcement:
            available = _find(vals, "available")
            required = _find(vals, "required")
            ratio = available / required if available is not None and required not in (None, 0) else None
            if ratio is not None and status in ("PASS", "FAIL"):
                usage_rows += 1
                checks.append(_check(f"kullanim:{row.get('component_id', comp)}", {"available_required": ratio, "status": status}, (ratio >= 1 if status == "PASS" else ratio < 1)))
        elif status in ("PASS", "FAIL"):
            usage_rows += 1
            checks.append(_check(f"kullanim:{row.get('component_id', comp)}", {"utilization": util, "status": status}, ((util >= 1 if status == "PASS" else util < 1) if "nozzle" in str(row.get("calculation_type", "")) or str(row.get("component_type", "")) == "nozzle" else (util <= 1 if status == "PASS" else util > 1)) if util is not None else None, scope=util is None))
        # Independent UG-27(c)(1) check for shell/body rows only.
        if ("shell" in comp or "cylindrical" in comp or str(row.get("component_id", "")).startswith("S")) and str(row.get("clause_reference", "")).startswith("UG-27(c)(1)"):
            shell = next((s for s in project.get("shell_sections", []) if s.get("section_id") == row.get("component_id")), None)
            api_t = _find(vals, "t_required") or _find(vals, "required_thickness")
            snap = row.get("input_snapshot", {})
            pressure = snap.get("P_MPa") or project.get("design_conditions", {}).get("design_pressure")
            rc = snap.get("R_corroded_mm")
            di = (shell or {}).get("inside_diameter")
            material_id = next((m.get("material_id") for m in project.get("materials", []) if m.get("material_id")), None)
            s_value = snap.get("S_MPa") or _find(vals, "allowable", "stress") or _find(vals, "allowable_stress")
            e_value = snap.get("E") or _find(vals, "efficiency")
            ca = snap.get("C_mm", (shell or {}).get("corrosion_allowance", 0))
            independent = None
            if rc is not None and all(isinstance(x, (int, float)) for x in (pressure, s_value, e_value)):
                radius = rc
            elif all(isinstance(x, (int, float)) for x in (pressure, di, s_value, e_value, ca)):
                radius = di / 2 + ca
            else:
                radius = None
            if radius is not None:
                denom = s_value * e_value - .6 * pressure
                if denom > 0:
                    independent = pressure * radius / denom
            if api_t is not None and independent is not None:
                delta = abs(api_t - independent) / abs(independent) if independent else math.inf
                checks.append(_check(f"gövde_bağımsız:{row.get('component_id')}", {"api_t_required": api_t, "ug27_t_required": independent, "relative_error": delta, "material_id": material_id}, delta <= .01))
            else:
                checks.append(_check(f"gövde_bağımsız:{row.get('component_id')}", {"api_t_required": api_t, "ug27_t_required": independent, "malzeme_verisi": s_value}, scope=True))
    return checks, usage_rows


def run():
    rows = []
    counters = {"sonlu_sayi": {"GEÇTİ": 0, "BULGU": 0, "KAPSAM_DIŞI": 0}, "kullanim": {"GEÇTİ": 0, "BULGU": 0, "KAPSAM_DIŞI": 0}, "gövde_bağımsız": {"uyuşan": 0, "uyuşmayan": 0, "KAPSAM_DIŞI": 0}}
    for case in cases():
        out = run_case(case["project"])
        checks, _ = inspect(out, case["project"])
        for check in checks:
            name, state = check["ad"], check["durum"]
            if name == "sonlu_sayi": counters["sonlu_sayi"][state] += 1
            elif name.startswith("kullanim:"): counters["kullanim"][state] += 1
            elif name.startswith("gövde_bağımsız:"):
                key = "uyuşan" if state == "GEÇTİ" else ("uyuşmayan" if state == "BULGU" else state)
                counters["gövde_bağımsız"][key] += 1
        status_list = [c["durum"] for c in checks]
        status = "BULGU" if "BULGU" in status_list else ("GEÇTİ" if status_list and all(s == "GEÇTİ" for s in status_list) else "KAPSAM_DIŞI")
        rows.append({"vaka": case["case_id"], "temel": case["base"], "girdi": case["project"], "http_status": out.get("http_status"), "sonuc": status, "kontroller": checks,
                     "gozlenen": {"ok": out.get("ok"), "error": out.get("error"), "payload": out.get("payload")}})
    summary = {key: sum(r["sonuc"] == key for r in rows) for key in ("GEÇTİ", "BULGU", "KAPSAM_DIŞI")}
    (HERE / "results_v2.json").write_text(json.dumps({"seed": SEED, "vaka_sayisi": len(rows), "ozet": summary, "kontrol_sayilari": counters, "vakalar": rows}, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    shell = counters["gövde_bağımsız"]
    print(f"SONUÇ: T04 vaka={len(rows)} · GEÇTİ={summary['GEÇTİ']} · BULGU={summary['BULGU']} · KAPSAM_DIŞI={summary['KAPSAM_DIŞI']} · kontrol_gövde_bağımsız={shell['uyuşan']} (uyuşan) / {shell['uyuşmayan']} (uyuşmayan)")
    print(json.dumps(counters, ensure_ascii=False))
    return rows


if __name__ == "__main__":
    run()
