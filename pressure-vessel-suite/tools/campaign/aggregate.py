"""Aggregate family results into the campaign Markdown and CSV summary."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "docs" / "validation" / "campaign-2026-10"

def aggregate(results_root: Path | None = None, output_dir: Path | None = None):
    source = Path(results_root) if results_root else ROOT / "tools" / "campaign" / "families"
    target = Path(output_dir) if output_dir else CAMPAIGN
    rows = []
    for path in sorted(source.glob("**/results.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data.get("results", []))
    target.mkdir(parents=True, exist_ok=True)
    fields = ["family", "case_id", "quantity", "unit", "suite", "reference", "diff_pct", "verdict", "ref_source", "note"]
    with (target / "ozet.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    lines = ["# Doğrulama kampanyası özeti", "", f"Toplam vaka: {len(rows)}", "",
             "| Aile | Vaka | Nicelik | Suite | Referans | Fark (%) | Karar |",
             "|---|---|---|---:|---:|---:|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k, "")) for k in ("family", "case_id", "quantity", "suite", "reference", "diff_pct", "verdict")) + " |")
    (target / "OZET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target / "OZET.md", target / "ozet.csv"

if __name__ == "__main__":
    aggregate()
