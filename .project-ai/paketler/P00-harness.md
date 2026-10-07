# PAKET P00 — Doğrulama kampanyası harness'i

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 0 · Yürütücü: codex:yaz (pilot)
> Mod: yaz → worktree'de yazarsın, dönüş = ≤15 satır rapor
> Codex yoksa: bu paket Claude Sonnet'e brief'lenir.
> Oluşturan: Orkestra şefi (Opus) · Tarih: 2026-10-07

## Sen kimsin, ne yapıyorsun
Büyük bir doğrulama kampanyasının **altyapısını** yazıyorsun. Bundan sonra 20 ayrı ajan senin
API'nle yüzlerce tank varyantını koşturacak, sonuçları bağımsız hesapla kıyaslayacak. Bu yüzden
API sade, kararlı ve iyi belgelenmiş olmalı. Sözleşmeye birebir uy. Emin olmadığın şeyi uydurma,
rapora "Açık soru" olarak yaz.

## Amaç
`tools/campaign/` paketi: bir VesselProject dict'ini **sitenin API yolundan** hesaplatır,
sonuçlardan değer çeker, kıyas sonucunu standart biçimde yazar ve tüm aileleri tek bir özet
tabloda toplar.

## Bağlam
- Suite: ASME VIII-1 + EN 13445 basınçlı kap hesabı. Python 3.14, FastAPI, Pydantic v2, uv monorepo.
- `sys.path` kurulumu: `import apps.api._bootstrap` (bkz. `apps/api/_bootstrap.py`) veya
  `tests/conftest.py`. WeasyPrint uyarısı stderr'e basılır, zararsızdır.
- API: `apps/api/main.py`. `POST /api/projects` (gövde = VesselProject JSON) → `{id, ...}`.
  Ardından `POST /api/projects/{id}/calculate` → `services.calculation_payload` çıktısı.
  Anahtarlar: `project_number, project_name, code, edition, global_mawp_mpa, results, errors,
  volume_mass, verification`. Her `results[]` satırında şu alanlar var: `component_id,
  component_type, calculation_type, clause_reference, input_snapshot, intermediate_values[{name,
  value, unit}], final_result..., status`. Gerçek yapıyı kendin bir koşuyla gör ve README'de belgele.
- Geçerli proje örnekleri: `output/demo-project.json`, `tests/fixtures/*.json`,
  `apps/web-ui/src/store.ts` `defaultProject`. Domain: `packages/domain/src/domain/` (project.py,
  geometry.py — `Support` saddle/skirt/leg alanları, conditions.py, load_cases.py, materials.py).
- Kodu seçme: proje dict'indeki hesap kodu alanı (bkz. `services._build_design_code`).
- Yeniden kullan: `packages/calc-core/src/calc_core/verification.py` (`TolerancePolicy`).
- Etiket politikası: `docs/validation/README.md`.

## Arayüz sözleşmesi (değiştirme)
Tam metin: `.project-ai/ORKESTRA.md` → **C-1** ve **C-2**. Fonksiyon adları, imzalar ve dönüş
anahtarları birebir olmalı.

`bases.py` notları:
- Her temel tank `VesselProject.model_validate`'ten geçmeli **ve** `run_case` ile `ok=True` dönmeli.
- `vertical_leg_tank` mümkün olduğunca çok özelliği doldurur: 4 boru ayak, taban plakası, ankraj,
  kaynak bacakları, MDMT için `ucs66_curve_group`, en az 1 gövde nozulu.
- `horizontal_saddle_tank` 2 saddle içerir. `skirt_column` etek içerir.
- `**overrides` derin birleştirme (deep merge) yapar. Listeler tümüyle değiştirilir.

## Kapsam
- Yazacağın dosyalar (`pressure-vessel-suite/` altında): `tools/__init__.py`,
  `tools/campaign/__init__.py`, `harness.py`, `bases.py`, `compare.py`, `aggregate.py`,
  `README.md`, `tools/campaign/families/__init__.py` (boş), `tests/campaign/__init__.py`,
  `tests/campaign/test_harness.py`.
- **Dokunma:** `packages/**`, `apps/**`, mevcut `tests/**`, `docs/**` (aggregate yalnız çalışınca
  `docs/validation/campaign-2026-10/` altına yazar; şimdi koşturma).
- Yapılmayacaklar: aile paketleri (F01–F20), oracle formülleri.

## Kabul kriterleri
1. `python -m pytest tests/campaign -q` yeşil. En az şunları sınar:
   - Üç temel tank `ok=True` döner.
   - `find_results` ve `value_of` gövde UG-27 gerekli kalınlığını bulur.
   - Bilinen vaka: `tests/golden_cases/test_published_examples.py` içindeki V-01 (UG-27) girdileri
     proje olarak kurulup harness'ten geçirilince oradaki beklenen değerle ±%1 içinde eşleşir.
   - `judge` etiket mantığı.
   - `aggregate` sahte iki `results.json`'dan tablo üretir (tmp_path).
2. Mevcut testler bozulmaz: `python -m pytest tests -q -x` (uzun sürerse en az `tests/api tests/unit`).
3. README'de: tek bir aile paketinin nasıl yazılacağı (20–30 satır örnek) ve gerçek bir payload
   sonuç satırının kısaltılmış örneği.
