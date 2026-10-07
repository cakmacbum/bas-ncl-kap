# ORKESTRA — M2 Tank doğrulama kampanyası

Tur başı: 2026-10-07 · checkpoint `e9c289b` · Codex: açık · Yusuf: 20 Codex aynı anda (DEC-005)
M1 panosu: `arsiv/ORKESTRA-M1.md`

## Pano
| Paket | Yürütücü | Dalga | Sahip olduğu yol | Durum |
|---|---|---|---|---|
| P00 harness | Codex luna·medium (pilot) | 0 | `pressure-vessel-suite/tools/campaign/*.py`, `tests/campaign/` | DAĞITILDI |
| K1–K4 kaynak avı | Claude Sonnet ×4 (WebSearch) | 0 | `docs/validation/campaign-2026-10/sources-K<n>.md` | DAĞITILDI |
| F01–F20 aileler | Codex luna·medium ×20 | 1 | `tools/campaign/families/fNN_*/`, `docs/validation/campaign-2026-10/FNN-*.md` | BEKLİYOR |

## Sözleşmeler

### C-1 Harness API (P00 sağlar, F01–F20 kullanır) — `pressure-vessel-suite/tools/campaign/`
```python
# harness.py
def run_case(project: dict) -> dict
    # FastAPI TestClient(apps.api.main.app): POST /api/projects → POST /api/projects/{id}/calculate
    # dönüş: {"ok": bool, "http_status": int, "payload": <calculation_payload dict | None>, "error": str | None}
def find_results(payload: dict, *, component_id: str | None = None,
                 calculation_type: str | None = None, clause_prefix: str | None = None) -> list[dict]
def value_of(result: dict, name: str) -> float | None     # intermediate_values[name] veya final_result alanı
# bases.py — geçerli VesselProject dict'leri (VesselProject.model_validate'ten geçer)
def vertical_leg_tank(**overrides) -> dict      # dikey, 2:1 eliptik, 4 boru ayak (taban plakası + ankraj dolu)
def horizontal_saddle_tank(**overrides) -> dict # yatay, 2 saddle
def skirt_column(**overrides) -> dict           # dikey, etek
def with_code(project: dict, code: str) -> dict # "ASME VIII-1" | "EN 13445"
# compare.py
@dataclass
class CaseResult:
    case_id: str; family: str; params: dict; quantity: str; unit: str
    suite: float | None; reference: float | None; ref_source: str   # "oracle" | "<kaynak atfı>"
    diff_pct: float | None; verdict: str; note: str = ""; suite_status: str | None = None
VERDICTS = ("DOĞRULANDI","FORMÜLASYON_FARKI","SAPMA","TEK_KAYNAK","KAYNAK_BEKLİYOR","KAPSAM_DIŞI")
def judge(suite, reference, *, rel_tol=0.01, suite_status=None, formulation_note=None) -> tuple[float|None, str]
    # suite_status REVIEW/BLOCKED/NOT_CALCULATED → KAPSAM_DIŞI; reference None → KAYNAK_BEKLİYOR
def write_results(family_dir: Path, family: str, results: list[CaseResult], meta: dict) -> Path  # results.json
# aggregate.py — python -m tools.campaign.aggregate → docs/validation/campaign-2026-10/OZET.md + ozet.csv
```
Birimler: mm, MPa, °C, N, N·mm. `tools/campaign/README.md`: payload sonuç satırı örneği + kullanım.

### C-2 Aile paketi çıktısı
`tools/campaign/families/fNN_<ad>/{__init__.py, variants.py, oracle.py, run.py, results.json}` +
`docs/validation/campaign-2026-10/FNN-<ad>.md`. `python -m tools.campaign.families.fNN_<ad>.run`
tek komutla yeniden üretilebilir. Suite koduna (`packages/`, `apps/`) yazılmaz.
