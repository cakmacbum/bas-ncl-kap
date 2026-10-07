"""Reproduce the F20b catalog-backed API campaign."""
from collections import Counter
from pathlib import Path
from tools.campaign.harness import run_case
from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f20_uctan_uca.variants import variants
from tools.campaign.families.f20_uctan_uca.oracle import required_thickness, value

FAMILY = "F20-uctan_uca"
HERE = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        out = run_case(project)
        payload = out.get("payload") or {}
        target_rows = [r for r in payload.get("results", [])
                       if r.get("calculation_type") == "thickness"
                       and r.get("component_type") in {"shell", "head"}]
        for result in target_rows:
            suite = value(result.get("intermediate_values") or [], "t_required")
            ref = required_thickness(result, project)
            status = result.get("status")
            diff, verdict = judge(suite, ref, suite_status=status,
                                  formulation_note="corroded radius / head geometry convention")
            component = result.get("component_id", result.get("component_type", "part"))
            rows.append(CaseResult(f"{case_id}-{component}", FAMILY,
                {"project_number": project["project_number"], "code": payload.get("code"),
                 "calculation_type": result["calculation_type"], "component_type": result["component_type"],
                 "suite_status": status}, "required_thickness", "mm", suite, ref,
                "independent ASME membrane relation; row inputs read from API intermediate_values",
                diff, verdict, "Nominal allowance and mill-tolerance adjustments excluded; compare pressure-required thickness.",
                None if out.get("ok") else "BLOCKED MISSING INPUT"))
    counts = Counter(r.verdict for r in rows)
    write_results(HERE, FAMILY, rows, {
        "basis": "catalog thickness rows; cylindrical shell and 2:1 elliptical head independent membrane equations",
        "api_projects": 30, "numeric_comparisons": sum(r.reference is not None and r.suite is not None for r in rows),
        "verdict_counts": dict(counts), "clean_room": "No prohibited calculation implementation read."})
    report = ["# F20b — Katalogla uçtan uca kıyas", "",
              f"API projeleri: 30; sayısal bileşen kıyası: {sum(r.reference is not None and r.suite is not None for r in rows)}.",
              "Etiket dağılımı: " + ", ".join(f"{k} {counts.get(k, 0)}" for k in ("DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA", "TEK_KAYNAK", "KAYNAK_BEKLİYOR", "KAPSAM_DIŞI")),
              "", "## Oracle", "Silindir için t = P·R/(S·E−0.6P); 2:1 elipsoid kafa için t = P·D/(2·S·E−0.2P). API ara değerlerinden yalnız girişler alındı; hesap bağımsız yazıldı.",
              "", "## SAPMA tablosu", "Karşılaştırılan büyüklük required thickness'tir; fark yönü hacim gibi emniyet yorumu taşımaz. Düşük fark API girdisindeki yuvarlamadan gelebilir.",
              "| Vaka | Tür | Suite mm | Oracle mm | Fark % | Yön |", "|---|---|---:|---:|---:|---|"]
    for r in rows:
        if r.verdict == "SAPMA":
            direction = "suite yüksek (kalın taraf)" if (r.diff_pct or 0) > 0 else "suite düşük (ince taraf)"
            report.append(f"| {r.case_id} | {r.params['component_type']} | {r.suite:.5f} | {r.reference:.5f} | {r.diff_pct:.3f} | {direction} |")
    report += ["", "## Yayınlanmış vakalar", "K1–K4 kaynaklarında bu örnek geometriler ve eşleşen ASME girdileri bulunmadığından yayınlanmış vakalar sayısal karşılaştırmaya alınmadı; girdileri eşleşmeyen K4 örneği uydurma eşleşmeyle kullanılmadı.",
               "", "## Kapsam dışı / bloklanan", "Katalogda listelenen diğer hesap türleri için doğrulanmış çalışan örnek yok. Bu koşu katalog `thickness` türünü kullanır; eksik satır varsa sonuç JSON'da sayısal karşılaştırma sayısına dahil edilmez.",
               "", "## Temiz oda", "Katalog ve examples.py ile harness arayüzü okundu. Yasaklı hesap implementasyonları açılmadı; oracle formülleri bağımsız yazıldı."]
    (HERE.parents[3] / "docs" / "validation" / "campaign-2026-10" / "F20-uctan_uca.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
