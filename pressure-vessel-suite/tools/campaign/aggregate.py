"""Aggregate family results into the campaign Markdown and CSV summary."""
from __future__ import annotations
import csv, json, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "docs" / "validation" / "campaign-2026-10"
LABELS = ("DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA", "TEK_KAYNAK", "KAYNAK_BEKLİYOR", "KAPSAM_DIŞI")

def normalize_verdict(value: str) -> str:
    """Return the canonical Turkish label despite spacing/underscore or mojibake."""
    raw = str(value).strip().upper().replace(" ", "_")
    for bad, good in (("Ã‡", "Ç"), ("Äž", "Ğ"), ("Ä±", "I"), ("Ä°", "İ"),
                      ("Åž", "Ş"), ("ÅŸ", "Ş"), ("Ãœ", "Ü"), ("Ã–", "Ö")):
        raw = raw.replace(bad.upper(), good.upper())
    # Invalid single-byte remnants (e.g. DI\x9eI) and U+FFFD lose the glyph;
    # canonical matching below still recognizes the surviving label letters.
    raw = raw.replace("\ufffd", "")
    key = "".join(c for c in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(c))
    key = key.replace("_", "").replace(" ", "")
    if key.startswith("DO") and key.endswith("RULANDI"):
        return LABELS[0]
    if key.startswith("FORM") and key.endswith("FARKI"):
        return LABELS[1]
    if key.startswith("KAYNAK") and key.endswith("BEKLIYOR"):
        return LABELS[4]
    if key.startswith("KAYNAK") and key.endswith("BEKLYOR"):
        return LABELS[4]
    aliases = {"DOGRULANDI": LABELS[0], "FORMULASYONFARKI": LABELS[1], "SAPMA": LABELS[2],
               "TEKKAYNAK": LABELS[3], "KAYNAKBEKLIYOR": LABELS[4], "KAPSAMDISI": LABELS[5]}
    # A broken Ş may be replaced by an invalid byte, leaving KAPSAM_DI I.
    if key.startswith("KAPSAMDI") and key.endswith("I"):
        return LABELS[5]
    return aliases.get(key, str(value).strip())

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
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
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
    lines += ["", "## KAPSAM_DIŞI nedenleri", "",
              "FNN-*.md raporları bu çalışma ağacında bulunamadı; nedenler aile bazında derlenemedi.", "",
              "## P00c bağlanmamış hesap yolları", "",
              "P00c raporundaki desteklenmeyen veya normal akışta üretilemeyen yollar:",
              "- flange, load_combination, fatigue: EN hesapları desteklenmiyor.",
              "- external_pressure_check: normal akışta üretilmiyor; vacuum_stability sonucu farklı adla dönüyor.",
              "- material_check: yalnız eksik malzemede NOT CALCULATED.",
              "- MDMT coincident ratio: solver girdisinde yok.", "",
              "## Vaka ayrıntıları", "", "| Aile | Vaka | Nicelik | Suite | Referans | Fark (%) | Karar |",
              "|---|---|---|---:|---:|---:|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k, "")) for k in ("family", "case_id", "quantity", "suite", "reference", "diff_pct", "verdict")) + " |")
    (target / "OZET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target / "OZET.md", target / "ozet.csv"

if __name__ == "__main__":
    aggregate()
