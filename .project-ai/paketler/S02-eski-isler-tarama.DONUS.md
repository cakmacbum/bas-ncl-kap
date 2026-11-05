# S02 DÖNÜŞ — Eski açık işlerin bugünkü durumu (salt okur tarama, 2026-11-06)
Yollar `pressure-vessel-suite/` köküne göre.

## 1. liquid_level_mm / component_sequence uyarısı — DURUM: VAR (T-2.7 kapanmış)
Kanıt:
- Domain: `packages/domain/src/domain/conditions.py:88` (Optional, ge=0).
- Hesap: `packages/calc-core/src/calc_core/orchestrator.py:412-500` `_apply_static_head_correction` (`liquid_level_mm` satır 435; `component_bottom_elevations` ile kot; ρ=0 ve kot/seviye yoksa K4 varsayımı yazılır, sessiz atlama yok). `calc_core/hydrostatics.py:71` yatayda gövde+bombe datum=0, dikeyde `component_sequence` kümülatif, sıra yoksa boş (kot uydurulmaz).
- UI: `apps/web-ui/src/pages.tsx:451-456` giriş alanı (WrcCell, <0 → 0); `pages.tsx:461-467` uyarı (dikey + seviye dolu + `component_sequence` boş). `store.ts:191`, `types.ts:16`. Commit 234def3.
- Test: `tests/regression/test_static_head_real.py`, `test_girdi_sinirlari_g03.py`.
Küçük boşluk (isteğe bağlı): UI uyarısı yalnız "dikey+seviye girildi+zincir boş" durumunda; koni içeren yatay kapta koni için kot yok (hydrostatics.py:71 docstring), bunun UI uyarısı yok.
Yapılacak iş: yok (T-2.7 TASKS'ta KAPANDI işaretlenmeli). Opsiyonel: vitest ile uyarı bileşeni testi.

## 2. Hidrotest UG-99 statik kafa — DURUM: YOK (T-2.8 açık)
Kanıt:
- `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:885-975` `calculate_hydrotest_pressure`: `P_test = formulas.hydrotest_pressure_asme(MAWP, S_test, S_design)` = 1.3·MAWP·LSR; ρ·g·h yok, `static_head` ara değeri yok. Orkestratörde (satır 273-286) hidrotest girdisinde seviye/kot yok. Yalnız MAWP statik kafayla düşüyor (orchestrator.py:465-480; MAWP notu "Hidrotest statik kafası bu sürümde uygulanmaz").
- Kapsam sınırı belgelenmiş: `docs/limitations.md` son bölüm (2026-10-18). Orada "uyarı eklemek tüm hidrotest sonuçlarını REVIEW_REQUIRED yapar, kasıtlı yapılmadı; karar Yusuf'ta" notu var.
- Yama `.project-ai/arsiv/worktree-yamalari/agent-a03eb4b0cead35772.patch` (142 satır): HESAP YAPMIYOR. `orchestrator.py`'ye `_flag_hydrotest_static_head_not_applied` ekler: hidrotest sonucuna ASSUMPTION ("ρ_su=1000, kap tepesine kadar dolu") + WARNING ("statik kafa uygulanmadı, kot uydurulmaz DEC-009") yazar ve PASS'i REVIEW_REQUIRED'a düşürür; ayrıca `tests/regression/test_static_head_hydrotest.py` (4 test: P_test=1.3·MAWP değişmez, uyarı var, PASS olamaz, ρ P_test'i değiştirmez). Yama ESKİ varsayıma dayanır ("kot modelde yok"); bugün `component_bottom_elevations` var → yama olduğu gibi uygulanmamalı, yalnız test iskeleti/uyarı metni referans alınabilir. Bu yüzden "yarım kalmış".
Yapılacak iş (öneri): (a) hidrotest hesabına `liquid_level`'den bağımsız test seviyesi gir (varsayılan: kap tepesine kadar su, ρ=1000, `dc.hydrotest_*` alanı ya da sabit varsayım+etiket); (b) bileşen bazında `P_test_bileşen = P_test + ρ_su·g·h_bileşen` (kot `component_bottom_elevations`), UG-99(b)/UG-99(c) test gerilme kontrolü (≤ 0.9·Sy vb.) bileşen bazlı; kot yoksa eski davranış + açık uyarı (karar: REVIEW_REQUIRED mi sadece uyarı mı — Yusuf).
Dosyalar: `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` (885-975), `.../formulas.py`, `packages/calc-core/src/calc_core/orchestrator.py` (273-286), `calc_core/hydrostatics.py`, `packages/code-en-13445/.../design_code.py:532` (aynı iş, ikinci kod), `docs/limitations.md`, yeni test `tests/regression/test_static_head_hydrotest.py`.

## 3. Nozul E1 < 1 — DURUM: KISMİ (T-2.14)
Kanıt:
- Hesap çekirdeği hazır: `packages/nozzles/src/nozzles/reinforcement.py:62` `opening_weld_joint_efficiency: Optional[float]=None`; satır 267-279: None → E1=1.0 + K4 uyarısı; (0,1] dışı → FAIL; E1 satır 310'da `E1·t − F·tr` içinde kullanılıyor. (Commit b9f6e28.)
- AMA hiçbir yerden beslenmiyor: `design_code.py:1151-1173` `NozzleReinforcementInput(...)` çağrısında alan geçilmiyor; domain `Nozzle` (`packages/domain/src/domain/geometry.py:137`) ve UI'da E1/dikiş-geçişi alanı yok. Yani pratikte her zaman E1=1 + uyarı.
- Yama `agent-afcd30bff3cfbf39c.patch` (174 satır): İLGİLİ ama zaten UYGULANMIŞ. İçeriği: reinforcement.py E1 alanı (yukarıdaki), `DesignConditions.coincident_stress_ratio` (conditions.py:102, mevcut), `mdmt_calc.py:153` oranı kayıt+uyarı (mevcut), design_code.py:1334 geçiş (mevcut), `tests/unit/test_k3_e1_coincident.py`. Yama artık yeni iş içermiyor; arşivde kalabilir.
Yapılacak iş: `Nozzle` domain modeline `opening_weld_joint_efficiency: Optional[float]` (0<x≤1) ekle; `design_code.py:1151` çağrısına geçir; (ileri adım) gövde dikişi konumu ile nozul z/θ konumundan otomatik "dikişten geçiyor mu" çıkarımı (ayrı inceleme, Yusuf kararı); UI nozul formuna alan + uyarı metni; test: E1=0.85 ile elle beklenen A1 değeri, API uçtan uca.
Dosyalar: `packages/domain/src/domain/geometry.py`, `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` (1151), `packages/nozzles/src/nozzles/reinforcement.py`, `apps/web-ui/src/types.ts` + `pages.tsx` (nozul bölümü ~satır 520+), `tests/unit/test_k3_e1_coincident.py`.

## 4. Tarayıcı e2e — DURUM: YOK (T-2.12 açık)
Kanıt: `apps/web-ui/package.json` yalnız `vitest ^3.2.7`, script `test: vitest run`; Playwright bağımlılığı yok. Repo genelinde (node_modules/dist hariç) `playwright` geçen dosya yok; `playwright.config*` ve `tests/e2e` yok. (`tests/wiring`, `tests/api` backend/API seviyesinde.)
"3 temel tank" tanımı: `docs/validation/campaign-2026-10/` içinde AYRI bir tanım dosyası YOK (yalnız F14/T13 belgelerinde "temel tank" geçer). Tanım koddadır: `tools/campaign/bases.py` — `vertical_leg_tank` (satır 36), `horizontal_saddle_tank` (52), `skirt_column` (58); `tests/campaign/test_harness.py:12` bu üçünü parametreli test eder. Ham proje JSON'ları buradan türer.
Yapılacak iş: `apps/web-ui` altına `@playwright/test` ekle + `playwright.config.ts` (vite dev server + API); bases.py fabrikalarından 3 proje JSON'u dışa aktar (script) → UI'a import (STEP/JSON içe aktarma varsa `StepImportDrawer`/proje yükleme) ya da form doldurma; her tank için: hesap çalıştır → sonuç sayfası + 3D/çizim ekran görüntüsü (görsel kanıt) kaydet; geçici olarak `tests/e2e/` + `docs/validation/campaign-2026-10/e2e/` ekran görüntüleri.
Dosyalar: `apps/web-ui/package.json`, yeni `apps/web-ui/playwright.config.ts`, yeni `apps/web-ui/e2e/*.spec.ts`, `tools/campaign/bases.py` (okunur), `.project-ai/launch` (`.claude/launch.json` api+web).

## 5. TASKS BACKLOG gerçek durum
- T-2.7: KAPANMIŞ (madde 1) → TASKS'ta üstü çizilmeli.
- T-2.8: AÇIK, yalnız hidrotest kısmı kaldı (koni CA_o zaten kapalı).
- T-2.12: AÇIK (madde 4).
- T-2.14: KISMİ — hesap çekirdeği var, domain/API/UI bağlantısı ve otomatik çıkarım yok (madde 3).
- Ek not: T-2.11'in "MDMT coincident ratio" kısmı da kısmen kapanmış (girdi+kayıt var, azaltma eğrisi telif nedeniyle uygulanmıyor — kasıtlı).
Önerilen sıra: T-2.7 kapat → T-2.14 domain bağlantısı (küçük) → T-2.8 hidrotest (karar gerektirir) → T-2.12 e2e.
