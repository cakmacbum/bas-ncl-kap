# ORKESTRA — STEP içe aktarma (M1)

Tur başı: 2026-10-06 · checkpoint `a0d5619` · Codex: açık (codex-cli 0.157.0, ChatGPT girişi)

## Pano
| Paket | Yürütücü | Dalga | Dosyalar (sahip) | Durum |
|---|---|---|---|---|
| P01 tanıyıcı | Claude Opus (worktree) | 1 | `packages/cad-engine/src/cad_engine/step_import.py`, `tests/cad-validation/test_step_import.py` | DAĞITILDI |
| P02 API | Claude Sonnet backend-builder (worktree) | 1 | `apps/api/main.py`, `apps/api/services.py`, `tests/api/test_step_import_api.py` | ENTEGRE (ab4d28c, tests/api 22 geçti) — BLOCKED de 503 döner |
| P03 UI | Codex gpt-6-luna·medium (`ork/P03`) | 1 | `apps/web-ui/src/StepImportDrawer.tsx` (yeni), `types.ts`, `api.ts`, `pages.tsx`, `workspace.css` | DAĞITILDI |

Yollar `pressure-vessel-suite/` köküne göre verilmiştir.

## Sözleşmeler

### S-1 Python (P01 sağlar, P02 kullanır)
```python
# packages/cad-engine/src/cad_engine/step_import.py
def recognize_step(path: str | Path, filename: str | None = None) -> StepRecognition: ...
class StepRecognition:            # dataclass
    def to_dict(self) -> dict: ...   # aşağıdaki JSON şemasının birebir karşılığı
```
CadQuery yoksa `status="BLOCKED"` döner, exception fırlatmaz. Bozuk/okunamayan dosyada
`status="REJECTED"` döner, exception fırlatmaz.

### S-2 HTTP (P02 sağlar, P03 kullanır)
`POST /api/import/step`
- İstek: ham dosya baytları, `Content-Type: application/octet-stream`, isteğe bağlı başlık
  `X-Filename: <ad>`. (multipart değil — DEC-002)
- 200 → StepRecognition JSON (REJECTED/PARTIAL da 200, sebep gövdede).
- 413 → >20 MB (`{"detail": "..."}`) · 415 → ilk 4 KB'ta `ISO-10303-21` yok · 503 → CAD motoru yok.
- Proje deposuna dokunmaz. Geçici dosya `finally` içinde silinir.

### S-3 JSON şeması (StepRecognition)
```jsonc
{
  "status": "RECOGNIZED" | "PARTIAL" | "REJECTED" | "BLOCKED",
  "source": { "filename": "x.step", "unit": "mm", "unit_scale": 1.0, "solid_count": 1 },
  "shell": null | {
    "inside_diameter": Field, "nominal_thickness": Field, "tangent_length": Field
  },
  "heads": [   // 0 veya 2 eleman; side "left" = eksende küçük koordinat
    { "side": "left" | "right",
      "type": Field,               // value: "elliptical"|"torispherical"|"hemispherical"|"flat"
      "inside_diameter": Field, "nominal_thickness": Field,
      "straight_flange_length": Field,
      "crown_radius": Field | null, "knuckle_radius": Field | null }
  ],
  "nozzles": [
    { "tag": "N1", "outside_diameter": Field, "inside_diameter": Field,
      "neck_thickness": Field, "axial_position": Field,   // sol tanjant hattından, mm
      "circumferential_angle": Field,                     // derece, +X'ten (nozzles/position.py)
      "outside_projection": Field }
  ],
  "unrecognized": [ { "feature": "cone", "reason": "Türkçe açıklama" } ],
  "warnings": [ "Türkçe uyarı" ],
  "not_in_file": ["material", "design_pressure", "design_temperature",
                  "joint_efficiency", "corrosion_allowance"]
}
// Field = { "value": number | string, "confidence": "high" | "medium" | "low", "note": string | null }
```
Uzunluklar mm, açılar derece. Durumlar:
- RECOGNIZED: gövde ve iki bombe tanındı, `unrecognized` boş.
- PARTIAL: gövde tanındı ama bazı öğeler tanınmadı.
- REJECTED: gövde tanınamadı ya da dosya geçersiz.
