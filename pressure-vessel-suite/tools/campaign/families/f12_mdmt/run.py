"""Run UCS-66 cases through the public campaign API and retain honest references."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.examples import example_mdmt_check
from tools.campaign.families.f12_mdmt.oracle import PUBLISHED, oracle
from tools.campaign.families.f12_mdmt.variants import variants
from tools.campaign.harness import find_results, run_case, value_of

FAMILY = "F12-mdmt"
OUT = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        # All variants originate from the catalogued non-blocked MDMT example.
        assert project["project_number"].startswith("CAMPAIGN-")
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, calculation_type="mdmt_check")
        ref = oracle(case_id)
        if not matches:
            status = "BLOCKED MISSING INPUT" if not outcome.get("ok") else "NOT CALCULATED"
            rows.append(CaseResult(case_id, FAMILY, {"curve_group": project["materials"][0].get("ucs66_curve_group")},
                "MDMT", "°C", None, ref["value_c"] if ref else None,
                ref["source"] if ref else "none", None, "KAPSAM_DIŞ", status, status))
            continue
        for i, result in enumerate(matches):
            suite = value_of(result, "mdmt")
            if suite is None:
                suite = value_of(result, "final_result")
            diff, verdict = judge(suite, ref["value_c"] if ref else None,
                                  suite_status=result.get("status"))
            rows.append(CaseResult(f"{case_id}:{result.get('component_id', i)}", FAMILY,
                {"curve_group": project["materials"][0].get("ucs66_curve_group"),
                 "thickness_mm": project["shell_sections"][0]["nominal_thickness"],
                 "impact_test_temperature_C": project["design_conditions"].get("impact_test_temperature_C"),
                 "status": result.get("status")}, "MDMT", "°C", suite,
                ref["value_c"] if ref else None, ref["source"] if ref else "none", diff,
                verdict, "Published point reference only; inputs are not a reconstructed source case." if ref
                else "Catalog has no independent numeric curve reference for this point.", result.get("status")))
    write_results(OUT, FAMILY, rows, {"code": "ASME VIII-1", "input_example": "tools.campaign.examples.example_mdmt_check",
        "oracle": "published K4 MDMT points only; UCS-66 curve values withheld"})
    counts = {}
    for row in rows:
        counts[row.verdict] = counts.get(row.verdict, 0) + 1
    numeric = sum(r.suite is not None and r.reference is not None and r.verdict in
                  ("DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA") for r in rows)
    report = ["# F12b — MDMT UCS-66", "", "## Özet", "",
        f"Sonuç satırı: {len(rows)}; sayısal kıyaslanan: {numeric}. Etiket dağılımı: " +
        ", ".join(f"{k}={v}" for k, v in sorted(counts.items())), "",
        "## Oracle ve sınır", "",
        "Bağımsız UCS-66 grafik noktaları çıkarılmadı: katalog ve sources-K4 yalnızca seçili yayınlanmış nihai MDMT noktalarını verir; eğri/tablo değerleri ve Fig. UCS-66.1 tam verisi yoktur. Kaynak örneklerinin her birini bu API fixture'ına birebir eşleyen girdi seti de katalogda yok. Bu nedenle varyantların hesaplanan MDMT sayıları kaynaksız kıyaslanmadı; K4 noktaları yalnızca etiketli referans olarak tutuldu. Katalogdaki MDMT örneği API'de çalışır ve sonuçlar `mdmt_check` satırlarından, `mdmt` ara değeri/final sonuç sözleşmesiyle çekilir.", "",
        "## SAPMA tablosu", "", "| case_id | girdiler | suite | oracle | fark % | yön | olası neden |", "|---|---|---:|---:|---:|---|---|"]
    for row in rows:
        if row.verdict == "SAPMA":
            direction = "suite daha sıcak: emniyetsiz; daha soğuk: emniyetli"
            report.append(f"| {row.case_id} | {row.params} | {row.suite} | {row.reference} | {row.diff_pct} | {direction} | Girdi eşleşmesi/kaynak yuvarlaması incelenmeli |")
    if not any(r.verdict == "SAPMA" for r in rows):
        report.append("Sayısal kıyaslanmış SAPMA yok.")
    report += ["", "## Yayınlanmış vakalar", "", "| Kaynak | Yayın MDMT | Durum |", "|---|---:|---|"]
    for cid, item in PUBLISHED.items():
        report.append(f"| {cid} | {item['value_c']:.3f} °C | Katalog girdileriyle birebir eşlenmedi; doğrulama iddiası yok |")
    report += ["", "## Temiz oda", "", "Oracle yalnızca açık yayınlanmış noktalara dayanır; eğri verisi türetilmedi. Yasaklı uygulama paketleri okunmadı. API sonuçları harness üzerinden alındı.", ""]
    (OUT.parents[3] / "docs/validation/campaign-2026-10/F12-mdmt.md").write_text("\n".join(report), encoding="utf-8")
    return rows


if __name__ == "__main__":
    run()
