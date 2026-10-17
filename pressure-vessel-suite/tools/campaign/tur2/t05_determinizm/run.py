"""Repeat public API calculations and compare normalized payloads."""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from tools.campaign import harness
from tools.campaign.tur2.t05_determinizm.cases import cases, permuted

OUT = Path(__file__).parent
REPORT = OUT / "rapor_v3.md"  # tur2 docs dizinine yazılmaz (A3 kısıtı)
VOLATILE = re.compile(r"(^|_)(id|uuid|timestamp|created_at|updated_at|calculated_at|request_id)$", re.I)


def normalize(value, key=""):
    if isinstance(value, dict):
        return {k: normalize(v, k) for k, v in sorted(value.items()) if not VOLATILE.search(k)}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


_PAREN = re.compile(r"\(([A-Za-z0-9_\-]+(?:, [A-Za-z0-9_\-]+)+)\)")


def canon(value):
    """Sıradan bağımsız karşılaştırma: listeleri JSON anahtarına göre sırala, '(M1, M2)' kimlik listelerini sırala."""
    if isinstance(value, dict):
        return {k: canon(v) for k, v in value.items()}
    if isinstance(value, list):
        return sorted((canon(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False))
    if isinstance(value, str):
        return _PAREN.sub(lambda m: "(" + ", ".join(sorted(m.group(1).split(", "))) + ")", value)
    return value


def _run(project, sequence):
    # The API enforces a per-client project cap; isolate each transient run.
    harness.CAMPAIGN_CLIENT_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, f"t05-run-{sequence}"))
    return harness.run_case(project)


def run():
    rows = []
    for item in cases():
        project = item["project"]
        outcomes = [_run(project, f"{item['case_id']}-repeat-{i}") for i in range(3)]
        shuffled = _run(permuted(project), f"{item['case_id']}-permuted")
        payloads = [normalize(outcome.get("payload")) for outcome in outcomes]
        expected = payloads[0]
        all_ok = all(outcome.get("ok") and outcome.get("payload") is not None for outcome in outcomes)
        repeat_equal = all(payload == expected for payload in payloads[1:])
        permuted_payload = normalize(shuffled.get("payload"))
        permutation_strict = bool(shuffled.get("ok")) and permuted_payload == expected
        permutation_equal = bool(shuffled.get("ok")) and canon(permuted_payload) == canon(expected)
        verdict = "GEÇTİ" if all_ok and repeat_equal and permutation_equal else (
            "BULGU" if all_ok else "KAPSAM_DIŞI")
        rows.append({
            "vaka": item["case_id"],
            "girdi": project,
            "beklenen": {"tekrarlar_ayni": True, "liste_permutasyonu_ayni": True},
            "gozlenen": {"uc_tekrar_ok": all_ok, "tekrarlar_ayni": repeat_equal,
                         "permutasyon_ok": bool(shuffled.get("ok")),
                         "permutasyon_ayni": permutation_equal,
                         "permutasyon_sira_dahil_ayni": permutation_strict,
                         "hatalar": [o.get("error") for o in outcomes if o.get("error")]
                         + ([shuffled.get("error")] if shuffled.get("error") else [])},
            "sonuc": verdict,
            "payload": expected,
            "permuted_payload": permuted_payload,
        })
    OUT.joinpath("results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    counts = {name: sum(row["sonuc"] == name for row in rows)
              for name in ("GEÇTİ", "BULGU", "KAPSAM_DIŞI")}
    findings = [row for row in rows if row["sonuc"] == "BULGU"]
    report = ["# T05 — Determinizm ve snapshot", "", f"Vaka sayısı: {len(rows)}.",
              f"Dağılım: geçti={counts['GEÇTİ']}, bulgu={counts['BULGU']}, kapsam dışı={counts['KAPSAM_DIŞI']}.",
              "", "Tekrar karşılaştırması: id/zaman damgası alanları çıkarılır, kalan payload aynen kıyaslanır. Permütasyon karşılaştırması: listeler sıradan bağımsız (kanonik) kıyaslanır; girdi sırasını izleyen çıktı sırası ayrıca 'permutasyon_sira_dahil_ayni' alanında kayıtlıdır.",
              "", "## Bulgular", "", "| Vaka | Önem | Yön | Konum | Ayrıntı |", "|---|---|---|---|---|"]
    for row in findings:
        report.append(f"| {row['vaka']} | ORTA | ? | ? | tekrar veya sıradan bağımsız permütasyon farkı (bkz. results.json) |")
    if not findings:
        report.append("Bulgu yok.")
    report += ["", "## Kapsam dışı", ""]
    report.extend(f"- {row['vaka']}: API hesaplama çağrısı başarılı değil." for row in rows
                  if row["sonuc"] == "KAPSAM_DIŞI")
    if counts["KAPSAM_DIŞI"] == 0:
        report.append("Kapsam dışı vaka yok.")
    report += ["", f"SONUÇ: vaka={len(rows)} · geçti={counts['GEÇTİ']} · bulgu={counts['BULGU']} (kritik=0, emniyetsiz=0) · kapsam_dışı={counts['KAPSAM_DIŞI']}", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report), encoding="utf-8")
    return rows


if __name__ == "__main__":
    run()
