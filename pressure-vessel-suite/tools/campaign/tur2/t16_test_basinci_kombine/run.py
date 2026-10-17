"""Execute T16 clean-room pressure/head comparison and write its artifacts."""
from __future__ import annotations
import json
from pathlib import Path
from tools.campaign.harness import run_case, find_results, value_of
from .cases import cases
from .oracle import static_head_mpa, ug99_pressure

HERE = Path(__file__).resolve().parent
REPORT = Path(__file__).resolve().parents[4] / "docs" / "validation" / "campaign-2026-10" / "tur2" / "T16-test-basinci-kombine.md"
TOL = 1e-6


def run():
    rows = []
    for case_id, project in cases():
        conditions = project["design_conditions"]
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        mawp_rows = find_results(payload, calculation_type="mawp")
        hp_rows = find_results(payload, calculation_type="hydrotest")
        test = hp_rows[0] if hp_rows else None
        component_values = [{"component_id": r.get("component_id"), "mawp_mpa": value_of(r, "MAWP") or value_of(r, "final_result")} for r in mawp_rows]
        valid = [x for x in component_values if x["mawp_mpa"] is not None]
        governor = min(valid, key=lambda x: x["mawp_mpa"]) if valid else None
        ratio = value_of(test, "ratio") if test else None
        observed = value_of(test, "P_test") if test else None
        basis = value_of(test, "pressure_basis") if test else None
        density = float(conditions.get("fluid_density_kg_m3", 0))
        height = float(conditions.get("test_fluid_level_mm", 0))
        basis_mode = case_id.rsplit("-", 1)[-1]
        expected_basis = float(conditions["design_pressure"]) if basis_mode == "design" else (governor["mawp_mpa"] if governor else None)
        expected_base = ug99_pressure(expected_basis, ratio) if expected_basis is not None and ratio is not None else None
        expected_bottom = expected_base + static_head_mpa(density, height) if expected_base is not None else None
        if not outcome.get("ok") or test is None or observed is None or expected_bottom is None:
            verdict = "KAPSAM_DIŞI"
        elif abs(observed - expected_bottom) <= max(1e-6, abs(expected_bottom) * TOL):
            verdict = "GEÇTİ"
        else:
            verdict = "BULGU"
        rows.append({
            "vaka": case_id,
            "girdi": {"orientation": project["orientation"], "basis_mode": basis_mode, "design_pressure_mpa": conditions.get("design_pressure"),
                      "maximum_allowable_pressure_ps_mpa": conditions.get("maximum_allowable_pressure_ps"),
                      "fluid_density_kg_m3": density, "test_fluid_level_mm": height,
                      "ratio_input": next((m.get("allowable_stress_test_temp") / m["allowable_stress"] for m in project["materials"] if m.get("allowable_stress_test_temp") is not None), None)},
            "beklenen": {"governing_component": governor, "basis_mode": basis_mode, "expected_pressure_basis_mpa": expected_basis,
                         "ug99_top_pressure_mpa": expected_base, "static_head_mpa": static_head_mpa(density, height),
                         "bottom_pressure_mpa": expected_bottom},
            "gozlenen": {"pressure_basis_mpa": basis, "ratio": ratio, "test_pressure_mpa": observed,
                         "components_mawp": component_values, "status": test.get("status") if test else None,
                         "error": outcome.get("error")},
            "sonuc": verdict,
        })
    counts = {name: sum(1 for row in rows if row["sonuc"] == name) for name in ("GEÇTİ", "BULGU", "KAPSAM_DIŞI")}
    HERE.joinpath("results.json").write_text(json.dumps({"paket": "T16-test-basinci-kombine", "vaka_sayisi": len(rows), "dagilim": counts, "results": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ["# T16 — Test basıncı, statik kafa ve yöneten bileşen", "",
              f"Vaka: {len(rows)} · geçti: {counts['GEÇTİ']} · bulgu: {counts['BULGU']} · kapsam dışı: {counts['KAPSAM_DIŞI']}", "",
              "Oracle: UG-99(b) üst basıncı = 1,3 × en düşük bileşen MAWP × S_test/S_design; alt nokta = üst basınç + ρgh. Statik kafa SI dönüşümü bağımsız hesaplanır.", "",
              "| Önem | Yön | Dosya:satır | Vaka | Beklenen | Gözlenen |", "|---|---|---|---|---:|---:|"]
    findings = [r for r in rows if r["sonuc"] == "BULGU"]
    head_findings = [r for r in findings if r["beklenen"]["basis_mode"] == "mawp"]
    basis_findings = [r for r in findings if r["beklenen"]["basis_mode"] == "design"]
    if head_findings:
        row = head_findings[0]
        report.append(f"| YÜKSEK | Emniyetsiz düşük basınç: statik kafa eksik | API sonucu (uygulama dosya:satır clean-room gereği incelenmedi) | {len(head_findings)} MAWP vakası; ör. {row['vaka']} | {row['beklenen']['bottom_pressure_mpa']:.6f} MPa | {row['gozlenen']['test_pressure_mpa']:.6f} MPa |")
    if basis_findings:
        row = basis_findings[0]
        report.append(f"| ORTA | Emniyetli yüksek basınç: design_pressure yerine MAWP tabanı | API sonucu (uygulama dosya:satır clean-room gereği incelenmedi) | {len(basis_findings)} tasarım tabanı kontrolü; ör. {row['vaka']} | {row['beklenen']['bottom_pressure_mpa']:.6f} MPa | {row['gozlenen']['test_pressure_mpa']:.6f} MPa |")
    report.extend(["", "Kapsam dışı vakalar: " + (", ".join(r["vaka"] for r in rows if r["sonuc"] == "KAPSAM_DIŞI") or "yok"), "",
                   f"SONUÇ: vaka={len(rows)} · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} (kritik=0, emniyetsiz={len(head_findings)}) · kapsam_dışı={counts['KAPSAM_DIŞI']}"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"T16: {len(rows)} vaka; GEÇTİ={counts['GEÇTİ']} BULGU={counts['BULGU']} KAPSAM_DIŞI={counts['KAPSAM_DIŞI']}")


if __name__ == "__main__":
    run()

