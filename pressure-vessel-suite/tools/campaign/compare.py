"""Standard case comparison and JSON output."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from pathlib import Path

VERDICTS = ("DOĞRULANDI", "FORMÜLASYON_FARKI", "SAPMA", "TEK_KAYNAK", "KAYNAK_BEKLİYOR", "KAPSAM_DIŞI")

@dataclass
class CaseResult:
    case_id: str
    family: str
    params: dict
    quantity: str
    unit: str
    suite: float | None
    reference: float | None
    ref_source: str
    diff_pct: float | None
    verdict: str
    note: str = ""
    suite_status: str | None = None

def judge(suite, reference, *, rel_tol=0.01, suite_status=None, formulation_note=None):
    # Gerçek durumlar: "REVIEW REQUIRED", "BLOCKED CODE DATA", "BLOCKED MISSING INPUT",
    # "NOT CALCULATED", "OUT OF SCOPE" (domain.enums.CalculationStatus).
    # REVIEW REQUIRED sayı üretir (yalnız mühendis onayı ister) → normal kıyaslanır.
    st = str(suite_status or "").upper().replace("_", " ")
    if st.startswith(("BLOCKED", "NOT CALCULATED", "OUT OF SCOPE")):
        return None, "KAPSAM_DIŞI"
    if reference is None:
        return None, "KAYNAK_BEKLİYOR"
    if suite is None:
        return None, "KAPSAM_DIŞI"
    diff = (float(suite) - float(reference)) / abs(float(reference)) if reference else (0.0 if suite == 0 else float("inf"))
    if formulation_note and abs(diff) > rel_tol:
        verdict = "FORMÜLASYON_FARKI"
    elif abs(diff) <= rel_tol:
        verdict = "DOĞRULANDI"
    else:
        verdict = "SAPMA"
    return diff * 100, verdict

def write_results(family_dir: Path, family: str, results: list[CaseResult], meta: dict) -> Path:
    path = Path(family_dir) / "results.json"
    path.write_text(json.dumps({"family": family, "meta": meta,
                                "results": [asdict(r) for r in results]}, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path
