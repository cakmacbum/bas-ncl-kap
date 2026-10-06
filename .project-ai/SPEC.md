---
proje: basincli-kap
surum: V2
guncellendi: 2026-10-06
kapsam: M1 — STEP içe aktarma + STL görüntüleme
---

# PROJE SPEC — STEP içe aktarma (M1)

## 1. Proje Hedefi
Kullanıcı kendi CAD modelini (STEP) yükleyince dönel kap geometrisi tanınır ve sihirbaz
formuna **öneri** olarak gelir. Kullanıcı her değeri onaylar, hesabı mevcut ve doğrulanmış
parametrik hat yapar. STL yalnızca görüntülenir.
CAD hiçbir zaman hesabın kaynağı olmaz (K2): dosyadan gelen her değer kullanıcı onayından geçer.

## 2. Kullanıcı Problemi
Mühendis kabı zaten SolidWorks/Inventor'da çizmiş durumda. Ölçüleri forma elle yeniden
girmek hem zaman kaybı hem de hata kaynağı.

## 3. Hedef Kullanıcı
Basınçlı kap tasarımcısı / imalatçı mühendis (mevcut sihirbaz kullanıcısı).

## 4. Başarı Kriterleri (PASS)
- S1: Kullanıcı Geometri adımında "Modelden içe aktar"a basar, suite'in kendi ürettiği
  STEP'i (1000 ID, t 12, L 2000, 2:1 eliptik) seçer → çekmecede ID 1000, t 12, L 2000,
  bombe tipi eliptik %0.1 içinde önerilir → onaylanır → form güncellenir → Hesapla →
  sonuçlar gelir.
- S2: Gerçek küre+torus torisferik STEP → tip torisferik, Rc ve rk %0.5 içinde.
- S3: Kutu / iki ayrı katı / kalınlıksız kabuk / koni → status REJECTED veya PARTIAL ve
  okunur bir sebep gösterilir. Form **değişmez**.
- S4: 25 MB dosya → 413; STEP olmayan içerik → 415; ikisinde de sunucu çökmez.
- S5: `.stl` seçilir → "Yüklenen model (yalnız görüntü — hesaba girmez)" sekmesinde
  görünür. Hiçbir form alanı değişmez.
- S6: Malzeme, P, T, E ve korozyon alanları çekmecede "dosyada yok — girin" rozetiyle gösterilir
  ve hiçbirine değer önerilmez.

## 5. Fonksiyonel Gereksinimler
- MUST: STEP tanıyıcı (gövde + 2 bombe: hemi / tori / 2:1 eliptik / düz), ret sebepleri,
  API ucu, onay çekmecesi, STL görüntüleme.
- SHOULD: radyal gövde nozulları (OD / ID / t / eksenel konum / θ).
- COULD: güven seviyesi rozetleri (high/medium/low).
- NOT NOW → FUTURE.md: bombe nozulu, eğik nozul, koni, çoklu gövde, destek, STL'den
  geometri çıkarma, STL ile model üst üste karşılaştırma, IGES.

## 6. Fonksiyonel Olmayan
Dosya ≤20 MB. İşlem tipik modelde <10 s. Geçici dosya her durumda silinir. Yeni bağımlılık
yok. Arayüz Türkçe.

## 7. Kısıtlar
CadQuery 2.8 / OCP 7.9, FastAPI, React+TS. `python-multipart` kurulu değil (bkz. DEC-002).

## 8. Varsayımlar
- STEP birimi dosyadan okunur. Okunamazsa mm kabul edilir ve uyarı yazılır.
- θ, dosyanın kendi çerçevesinde ölçülür (eksen ≈ Z ise +X'ten, `nozzles/position.py` ile
  aynı kural). Eksen Z değilse θ'nın güveni düşük olur ve uyarı yazılır.
- "Sol bombe", eksen yönünde küçük koordinattaki bombedir.
- Tolerans: elips h/D için 0.25 ± 0.005 → 2:1. Diğer uzunluklar 0.01 mm hassasiyetle verilir.

## 9. Açık Sorular
Yok (BLOCKING yok).

## 10. Riskler → RISKS.md
## 11. Mimari
`cad_engine.step_import.recognize_step()` → `services.import_step_bytes()` →
`POST /api/import/step` (ham gövde) → `api.importStep()` → `StepImportDrawer` → store
güncelleyicileri. Sözleşme: `ORKESTRA.md > Sözleşmeler`.

## 12. Milestone
M1: STEP'ten tanınan dönel kap, kullanıcı onayıyla forma geçer. STL görüntülenir.

## 13. Görevler → TASKS.md
## 14. Doğrulama
pytest (`tests/cad-validation/test_step_import.py`, `tests/api/test_step_import_api.py`,
`tests/wiring`), `npm run build`, Browser pane uçtan uca (S1, S3, S5).

## 15. DoD (M1)
S1–S6 kanıtlandı · tüm eski testler yeşil · limitations.md B kaydı · kasa + log güncel.
