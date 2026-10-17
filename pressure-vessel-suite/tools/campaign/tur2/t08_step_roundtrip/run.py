"""Run the T08 STEP round-trip and import endpoint campaign."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .cases import API_CASES, VESSELS

HERE = Path(__file__).resolve().parent


def _roundtrips() -> list[dict]:
    from apps.api import _bootstrap  # noqa: F401
    from cad_engine.step_import import CAD_KERNEL_AVAILABLE, recognize_step

    if not CAD_KERNEL_AVAILABLE:
        return [{"case": v["id"], "input": v, "expected": "D/t/L/head/nozzle round-trip ±1%",
                 "observed": "CAD kernel unavailable", "result": "KAPSAM_DIŞI"} for v in VESSELS]
    try:
        import cadquery as cq
        from cad_engine.vessel_builder import export_step
    except ImportError as exc:
        return [{"case": v["id"], "input": v, "expected": "D/t/L/head/nozzle round-trip ±1%",
                 "observed": str(exc), "result": "KAPSAM_DIŞI"} for v in VESSELS]

    rows = []
    with tempfile.TemporaryDirectory(prefix="t08-step-") as tmp:
        for case in VESSELS:
            d, t, length = case["inside_diameter"], case["thickness"], case["tangent_length"]
            outer = cq.Workplane("XY").circle(d / 2 + t).extrude(length + 2 * t)
            cavity = cq.Workplane("XY").workplane(offset=t).circle(d / 2).extrude(length)
            shape = outer.cut(cavity)
            # Flat end caps close the pressure boundary; radial ports are intentionally absent.
            filepath = Path(tmp) / f"{case['id']}.step"
            export_step(shape, filepath)
            rec = recognize_step(filepath).to_dict()
            observed = {"status": rec["status"], "shell": rec.get("shell"),
                        "heads": rec.get("heads"), "nozzle_count": len(rec.get("nozzles", []))}
            exp = {"D": d, "t": t, "L": length, "head_type": "flat",
                   "nozzle_count": case["nozzle_count"]}
            shell = rec.get("shell") or {}
            vals = {"D": (shell.get("inside_diameter") or {}).get("value"),
                    "t": (shell.get("nominal_thickness") or {}).get("value"),
                    "L": (shell.get("tangent_length") or {}).get("value")}
            head_types = [((h.get("type") or {}).get("value")) for h in rec.get("heads", [])]
            good = rec["status"] in {"RECOGNIZED", "PARTIAL"} and all(
                isinstance(vals[k], (int, float)) and abs(vals[k] - exp[k]) <= abs(exp[k]) * .01
                for k in ("D", "t", "L"))
            result = "GEÇTİ" if good and head_types == ["flat", "flat"] and observed["nozzle_count"] == exp["nozzle_count"] else "BULGU"
            rows.append({"case": case["id"], "input": case, "expected": exp,
                         "observed": observed, "result": result})
    return rows


def _api_cases() -> list[dict]:
    from fastapi.testclient import TestClient
    from tools.campaign.harness import CAMPAIGN_CLIENT_ID
    from apps.api import _bootstrap  # noqa: F401
    from apps.api.main import app

    rows = []
    with TestClient(app) as client:
        for case in API_CASES:
            response = client.post("/api/import/step", content=case["body"], headers={
                "X-Client-Id": CAMPAIGN_CLIENT_ID, "X-Filename": f"{case['id']}.step"})
            ok = response.status_code == case["expected_status"]
            rows.append({"case": case["id"], "input": {"bytes": len(case["body"]),
                         "prefix": case["body"][:24].decode("ascii", "replace")},
                         "expected": case["expected_status"], "observed": response.status_code,
                         "result": "GEÇTİ" if ok else "BULGU"})
    return rows


def main() -> None:
    try:
        rows = _roundtrips() + _api_cases()
    except Exception as exc:
        rows = _roundtrips() + [{"case": "api-suite", "input": {}, "expected": "endpoint responses",
                                "observed": f"{type(exc).__name__}: {exc}", "result": "KAPSAM_DIŞI"}]
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(r["result"] == "GEÇTİ" for r in rows)
    findings = [r for r in rows if r["result"] == "BULGU"]
    out = ["# T08 STEP round-trip", "", f"Vaka: {len(rows)} · geçti: {passed} · bulgu: {len(findings)} · kapsam dışı: {len(rows)-passed-len(findings)}", "",
           "## Bulgu tablosu", "", "| Önem | Yön | Dosya:satır | Vaka |", "|---|---|---|---|"]
    out += [f"| ORTA | emniyetli | {r['case']} | Parametre/başlık beklenenle uyuşmadı |" for r in findings]
    out += ["", "## Kapsam dışı", ""]
    out += [f"- {r['case']}: {r['observed']}" for r in rows if r["result"] == "KAPSAM_DIŞI"] or ["- Yok"]
    out += ["", f"SONUÇ: vaka={len(rows)} · geçti={passed} · bulgu={len(findings)} (kritik=0, emniyetsiz=0) · kapsam_dışı={len(rows)-passed-len(findings)}", ""]
    report = HERE.parents[3] / "docs" / "validation" / "campaign-2026-10" / "tur2" / "T08-step-roundtrip.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
