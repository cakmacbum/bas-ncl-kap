"""Execute T15 sequential/concurrent runs and persist machine-readable results."""
from __future__ import annotations

import hashlib
import json
import statistics
import time
import tracemalloc
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient
from tools.campaign.tur2.t15_performans.cases import cases

OUT = Path(__file__).parent


def signature(outcome: dict) -> str:
    """Stable output signature used to identify cross-request result mixing."""
    payload = outcome.get("payload") or {}
    canonical = json.dumps({
        "ok": outcome.get("ok"), "http_status": outcome.get("http_status"),
        "errors": payload.get("errors"),
        "results": [{"component_id": row.get("component_id"),
                     "calculation_type": row.get("calculation_type"),
                     "clause_reference": row.get("clause_reference"),
                     "status": row.get("status"), "final_result": row.get("final_result"),
                     "intermediate_values": row.get("intermediate_values")}
                    for row in payload.get("results", [])],
    }, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def isolated_run(project: dict, phase: str) -> dict:
    """Harness-compatible wrapper with an isolated client quota per trial."""
    from apps.api import _bootstrap  # noqa: F401
    from apps.api.main import app
    client_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"t15:{phase}:{project['project_number']}"))
    try:
        with TestClient(app) as client:
            headers = {"X-Client-Id": client_id}
            created = client.post("/api/projects", json=project, headers=headers)
            if created.status_code != 201:
                return {"ok": False, "http_status": created.status_code, "payload": None,
                        "error": created.text}
            project_id = created.json()["id"]
            response = client.post(f"/api/projects/{project_id}/calculate", headers=headers)
            if response.status_code != 200:
                return {"ok": False, "http_status": response.status_code, "payload": None,
                        "error": response.text}
            payload = response.json()
            return {"ok": not bool(payload.get("errors")), "http_status": response.status_code,
                    "payload": payload, "error": None if not payload.get("errors") else str(payload["errors"])}
    except Exception as exc:
        return {"ok": False, "http_status": 500, "payload": None,
                "error": f"{type(exc).__name__}: {exc}"}


def timed_run(project: dict, phase: str) -> tuple[dict, float]:
    start = time.perf_counter()
    outcome = isolated_run(project, phase)
    return outcome, time.perf_counter() - start


def run() -> dict:
    inputs = cases(100)
    tracemalloc.start()
    start_current, start_peak = tracemalloc.get_traced_memory()
    seq_start = time.perf_counter()
    sequential = [timed_run(project, "sequential") for _, project in inputs]
    sequential_total = time.perf_counter() - seq_start
    after_seq_current, after_seq_peak = tracemalloc.get_traced_memory()

    concurrent_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        concurrent = list(pool.map(lambda row: timed_run(row[1], "concurrent"), inputs))
    concurrent_total = time.perf_counter() - concurrent_start
    end_current, end_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    sequential_times = [duration for _, duration in sequential]
    concurrent_times = [duration for _, duration in concurrent]
    mismatches = [i for i, (seq, conc) in enumerate(zip(sequential, concurrent))
                  if signature(seq[0]) != signature(conc[0])]
    successes = sum(bool(result.get("ok")) for result, _ in sequential)
    errors = len(inputs) - successes
    rows = []
    for i, (case_id, project) in enumerate(inputs):
        seq_result, seq_duration = sequential[i]
        conc_result, conc_duration = concurrent[i]
        mixed = i in mismatches
        status = "BULGU" if mixed or not seq_result.get("ok") or not conc_result.get("ok") else "GEÇTİ"
        rows.append({
            "vaka": case_id,
            "girdi": {"project_number": project["project_number"],
                      "design_pressure": project["design_conditions"]["design_pressure"],
                      "is_paralel": True, "worker_count": 8},
            "beklenen": "Seri/paralel yanıt özeti eşit; API çağrısı başarılı",
            "gözlenen": {"seri": {"ok": seq_result.get("ok"), "http_status": seq_result.get("http_status"),
                                    "error": seq_result.get("error"), "payload_signature": signature(seq_result)},
                         "paralel": {"ok": conc_result.get("ok"), "http_status": conc_result.get("http_status"),
                                     "error": conc_result.get("error"), "payload_signature": signature(conc_result)},
                         "seri_saniye": round(seq_duration, 6),
                         "paralel_saniye": round(conc_duration, 6),
                         "yanıt_karışması": mixed},
            "sonuç": status,
        })
    def percentile(values: list[float], pct: float) -> float:
        return round(sorted(values)[max(0, int((len(values) - 1) * pct))], 6)

    summary = {
        "vaka_sayisi": len(rows), "seri_toplam_saniye": round(sequential_total, 6),
        "paralel_toplam_saniye": round(concurrent_total, 6),
        "seri_ortalama_saniye": round(statistics.mean(sequential_times), 6),
        "seri_p95_saniye": percentile(sequential_times, .95),
        "paralel_ortalama_saniye": round(statistics.mean(concurrent_times), 6),
        "paralel_p95_saniye": percentile(concurrent_times, .95),
        "hata_orani": round(errors / len(rows), 6), "seri_basarili": successes,
        "seri_hata": errors, "paralel_hata": sum(not r.get("ok") for r, _ in concurrent),
        "yanit_karismasi_sayisi": len(mismatches),
        "bellek_baslangic_artik_bayt": start_current,
        "bellek_seri_sonrasi_artik_bayt": after_seq_current,
        "bellek_seri_tepe_artis_bayt": after_seq_peak - start_peak,
        "bellek_son_artik_bayt": end_current,
        "bellek_tepe_artis_bayt": end_peak - start_peak,
    }
    document = {"ozet": summary, "vakalar": rows}
    (OUT / "results.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return document


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["ozet"], ensure_ascii=False, indent=2))
