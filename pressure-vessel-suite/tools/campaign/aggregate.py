"""Aggregate family results into the campaign Markdown and CSV summary."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "docs" / "validation" / "campaign-2026-10"
LABELS = ("DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA", "TEK_KAYNAK", "KAYNAK_BEKLİYOR", "KAPSAM_DIŞI")


def normalize_verdict(value: str) -> str:
    raw = str(value).strip().upper().replace(" ", "_")
    raw = raw.replace("\x9e", "Ş").replace("\x9f", "ş").replace("?", "Ş")
    # Repair common UTF-8-as-Windows-1252/Latin-1 mojibake before matching.
    for _ in range(2):
        try:
            repaired = raw.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if repaired == raw:
            break
        raw = repaired
    key = "".join(c for c in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(c))
    key = key.replace("_", "")
    aliases = {"DOGRULANDI": LABELS[0], "FORMULASYONFARKI": LABELS[1], "SAPMA": LABELS[2],
               "TEKKAYNAK": LABELS[3], "KAYNAKBEKLIYOR": LABELS[4], "KAPSAMDISI": LABELS[5]}
    return aliases.get(key, str(value).strip())


def _report_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    # A few legacy reports contain question marks where Turkish glyphs were lost.
    return (text.replace("DO?RULANDI", "DOĞRULANDI").replace("FORM?LASYON", "FORMÜLASYON")
            .replace("KAPSAM_DI?I", "KAPSAM_DIŞI").replace("KAPSAM DI?I", "KAPSAM DIŞI")
            .replace("HUKUM:", "HÜKÜM:").replace(" ? ", " · "))


def aggregate(results_root: Path | None = None, output_dir: Path | None = None):
    source = Path(results_root) if results_root else ROOT / "tools" / "campaign" / "families"
    target = Path(output_dir) if output_dir else CAMPAIGN
    rows = []
    for path in sorted(source.glob("**/results.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for original in data.get("results", []):
            row = dict(original)
            if "verdict" in row:
                row["verdict"] = normalize_verdict(row["verdict"])
            rows.append(row)
    target.mkdir(parents=True, exist_ok=True)
    fields = ["family", "case_id", "quantity", "unit", "suite", "reference", "diff_pct", "verdict", "ref_source", "note"]
    with (target / "ozet.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    families = sorted({str(r.get("family", "")) for r in rows})
    counts = {fam: {label: 0 for label in LABELS} for fam in families}
    for row in rows:
        if row.get("verdict") in LABELS:
            counts[str(row.get("family", ""))][row["verdict"]] += 1
    lines = ["# Doğrulama kampanyası özeti", "", f"Toplam vaka: {len(rows)}", "",
             "## Aile × etiket matrisi", "", "| Aile | " + " | ".join(LABELS) + " | Toplam |",
             "|---|" + "---:|" * (len(LABELS) + 1)]
    for fam in families:
        vals = [counts[fam][label] for label in LABELS]
        lines.append("| " + fam + " | " + " | ".join(map(str, vals)) + " | " + str(sum(vals)) + " |")
    totals = [sum(counts[f][label] for f in families) for label in LABELS]
    lines += ["| **Toplam** | " + " | ".join(map(str, totals)) + " | " + str(sum(totals)) + " |", "",
              "## SAPMA aileleri", ""]
    lines += [f"- {f}" for f in families if counts[f]["SAPMA"]] or ["- Yok"]

    reports = sorted(CAMPAIGN.glob("F[0-9][0-9]-*.md"))
    lines += ["", "## KAPSAM_DIŞI nedenleri", "", "| Aile | Neden |", "|---|---|"]
    for report in reports:
        text = _report_text(report)
        reasons = []
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
            if "KAPSAM_DIŞI" in sentence or "KAPSAM DIŞI" in sentence:
                sentence = re.sub(r"\s+", " ", sentence).strip().replace("|", "\\|")
                if sentence and sentence not in reasons:
                    reasons.append(sentence)
        lines.append(f"| {report.stem} | {'; '.join(reasons) if reasons else 'Raporda ayrıca gerekçe belirtilmemiş.'} |")

    lines += ["", "## Teyit", "", "| Aile | Hüküm |", "|---|---|"]
    for report in sorted((CAMPAIGN / "teyit").glob("V*.md")):
        text = _report_text(report)
        match = re.search(r"^H[ÜU]K[ÜU]M:\s*(.+)$", text, re.MULTILINE)
        family = re.search(r"V(\d{2})-([^.]*)", report.stem)
        lines.append(f"| {family.group(0) if family else report.stem} | {match.group(1).strip() if match else 'HÜKÜM satırı bulunamadı.'} |")

    lines += ["", "## P00c bağlanmamış hesap yolları", "",
              "P00c raporundaki desteklenmeyen veya normal akışta üretilemeyen yollar:",
              "- flange, load_combination, fatigue: EN hesapları desteklenmiyor.",
              "- external_pressure_check: normal akışta üretilmiyor; vacuum_stability sonucu farklı adla dönüyor.",
              "- material_check: yalnız eksik malzemede NOT CALCULATED.",
              "- MDMT coincident ratio: solver girdisinde yok.", "",
              "## Vaka ayrıntıları", "", "| Aile | Vaka | Nicelik | Suite | Referans | Fark (%) | Karar |",
              "|---|---|---|---:|---:|---:|---|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(k, "")) for k in ("family", "case_id", "quantity", "suite", "reference", "diff_pct", "verdict")) + " |")
    (target / "OZET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target / "OZET.md", target / "ozet.csv"


if __name__ == "__main__":
    aggregate()
