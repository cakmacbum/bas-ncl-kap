"""Run the MDMT campaign through the public project API."""
from pathlib import Path

from tools.campaign.compare import CaseResult, judge, write_results
from tools.campaign.families.f12_mdmt.oracle import oracle
from tools.campaign.families.f12_mdmt.variants import variants
from tools.campaign.harness import find_results, run_case, value_of

FAMILY = "F12-mdmt"
OUT = Path(__file__).parent


def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        matches = find_results(payload, calculation_type="mdmt_check")
        ref = oracle(case_id)
        if not matches:
            status = "BLOCKED MISSING INPUT" if not outcome.get("ok") else "NOT CALCULATED"
            rows.append(CaseResult(case_id, FAMILY, {"curve_group": project["materials"][0].get("ucs66_curve_group"),
                "thickness_mm": project["shell_sections"][0]["nominal_thickness"]}, "MDMT", "Â°C",
                None, ref["value_c"] if ref else None, ref["source"] if ref else "none",
                None, "KAPSAM_DIÅI" if not ref else "KAPSAM_DIÅI", status, status))
            continue
        for i, result in enumerate(matches):
            suffix = result.get("component_id", str(i))
            suite = value_of(result, "mdmt")
            if suite is None:
                suite = value_of(result, "final_result")
            diff, verdict = judge(suite, ref["value_c"] if ref else None,
                                  suite_status=result.get("status"))
            rows.append(CaseResult(f"{case_id}:{suffix}", FAMILY,
                {"curve_group": project["materials"][0].get("ucs66_curve_group"),
                 "thickness_mm": project["shell_sections"][0]["nominal_thickness"],
                 "impact_test_temperature_C": project["design_conditions"].get("impact_test_temperature_C"),
                 "status": result.get("status")}, "MDMT", "Â°C", suite,
                ref["value_c"] if ref else None, ref["source"] if ref else "none", diff,
                verdict, "Published K4 value is a point reference, not a full independent curve oracle." if ref else "No admissible numeric curve reference.",
                result.get("status")))
    write_results(OUT, FAMILY, rows, {"code": "ASME VIII-1", "oracle": "published K4 point ledger; unsupported UCS-66 curve points withheld"})
    counts = {}
    for row in rows:
        counts[row.verdict] = counts.get(row.verdict, 0) + 1
    report = ["# F12 â€” MDMT UCS-66", "", f"## 1. Ã–zet", "",
              f"Vaka/sonuÃ§ satÄ±rÄ±: {len(rows)}. Etiket daÄŸÄ±lÄ±mÄ±: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())), "",
              "## 2. Oracle formÃ¼lleri", "",
              "UCS-66: gruba ve yÃ¶neten kalÄ±nlÄ±ÄŸa baÄŸlÄ± muafiyet sÄ±caklÄ±ÄŸÄ±; grafik deÄŸerleri K4 yayÄ±n Ã§Ä±ktÄ±larÄ±ndan alÄ±nmÄ±ÅŸtÄ±r. UCS-66.1: coincident ratio = trÂ·E*/(tg_srâˆ’c), sÄ±caklÄ±k azaltÄ±mÄ± Fig. UCS-66.1'den okunur. FigÃ¼r verisi bu kaynaklarda tam olmadÄ±ÄŸÄ± iÃ§in yeni deÄŸer tÃ¼retilmedi.", "",
              "## 3. SAPMA tablosu", "", "| case_id | girdiler | suite | oracle | fark % | yÃ¶n | olasÄ± neden |", "|---|---|---:|---:|---:|---|---|"]
    for row in rows:
        if row.verdict == "SAPMA":
            direction = "suite daha sÄ±caksa emniyetsiz; aksi emniyetli"
            report.append(f"| {row.case_id} | {row.params} | {row.suite} | {row.reference} | {row.diff_pct} | {direction} | Tahmin: kaynak/uygulama farkÄ± araÅŸtÄ±rÄ±lmalÄ± |")
    if not any(r.verdict == "SAPMA" for r in rows):
        report.append("SAPMA yok.")
    report += ["", "## 4. YayÄ±nlanmÄ±ÅŸ vakalar", "",
               "| Kaynak vakasÄ± | YayÄ±n MDMT | KullanÄ±m |", "|---|---:|---|"]
    from tools.campaign.families.f12_mdmt.oracle import PUBLISHED
    for cid, item in PUBLISHED.items():
        report.append(f"| {cid} | {item['value_c']:.3f} Â°C | {item['source']} |")
    report += ["", "## 5. Kapsam dÄ±ÅŸÄ± ve bloklanan vakalar", "",
               "Curve ve impact girdisi eksik vakalar API BLOCKED dÃ¶ndÃ¼rÃ¼rse KAPSAM_DIÅI; sayÄ±sal yayÄ±mlanmÄ±ÅŸ eÅŸleÅŸmesi olmayan varyantlar KAYNAK_BEKLÄ°YOR olarak tutulur. Coincident ratio/PWHT girdilerinin MDMT hesabÄ±nda etkili olduÄŸu API Ã§Ä±ktÄ±sÄ±ndan teyit edilmelidir.", "",
               "## 6. Temiz oda beyanÄ±", "",
               "Oracle baÄŸÄ±msÄ±z kuruldu; yasaklÄ± uygulama paketleri aÃ§Ä±lmadÄ±. UCS-66.1 grafik noktalarÄ± uydurulmadÄ±; API sonucu yalnÄ±zca harness Ã¼zerinden alÄ±ndÄ±."]
    (OUT.parents[3] / "docs/validation/campaign-2026-10/F12-mdmt.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return rows


if __name__ == "__main__":
    run()

