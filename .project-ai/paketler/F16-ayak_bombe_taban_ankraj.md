# PAKET F16 — Bombeye bağlı ayak + taban plakası + ankraj

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1 · Yürütücü: codex:yaz
> Mod: yaz → worktree'de yazarsın, dönüş = ≤15 satır rapor
> Codex yoksa: bu paket Claude Sonnet'e brief'lenir.
> Oluşturan: Orkestra şefi (Opus) · Tarih: 2026-10-07

## Sen kimsin, ne yapıyorsun
20 paralel ajandan birisin. Bir basınçlı kap tasarım sitesinin **Bombeye bağlı ayak + taban plakası + ankraj** hesabını çok sayıda
varyantla koşturuyorsun. Sonuçları **bağımsız** bir kontrol hesabıyla ve yayınlanmış örneklerle
kıyaslıyorsun. Amaç hata bulmak, suite'i haklı çıkarmak değil. Sayı uydurma. Emin olmadığın şeyi
rapora "Açık soru" olarak yaz.

## Amaç
`tools/campaign/families/f16_ayak_bombe_taban_ankraj/`: varyant üret → site API'sinden hesaplat → temiz-oda oracle ile
kıyasla → yayınlanmış vakaları ekle → `results.json` + rapor.

## Bağlam
- Harness (hazır, oku): `pressure-vessel-suite/tools/campaign/`. İçinde `README.md`, `harness.py`
  (`run_case`, `find_results`, `value_of`), `bases.py` (temel tanklar, `with_code`) ve `compare.py`
  (`CaseResult`, `judge`, `write_results`) var. Sözleşme: `.project-ai/ORKESTRA.md` C-1/C-2.
- Domain modelleri (oku): `packages/domain/src/domain/` (project.py, geometry.py, conditions.py,
  load_cases.py, materials.py). Varyantları bu alanlarla kur.
- Etiket politikası: `docs/validation/README.md`. Önceki dersler: `docs/validation/asme-worked-examples.md`
  (yalnız "ders" ve "yayınlanmış değer" kısımları).
- Yayınlanmış örnekler: `docs/validation/campaign-2026-10/sources-K1.md` … `sources-K4.md`. Bu
  aile için öncelikli küme: **K3**. Konuna uyan vakaları ayrı `case_id` ile ekle ve
  `ref_source` olarak kaynak atfını yaz.

## TEMİZ ODA KURALI (zorunlu)
Oracle'ı Kod veya standart formülünden **sıfırdan** yaz. Şu implementasyonları **açma ve okuma**:
`packages/code-asme-viii-1`, `packages/code-en-13445`, `packages/nozzles`, `packages/supports`,
`packages/external-pressure`, `packages/mdmt`, `packages/flanges`, `packages/calc-core` (yalnız
`verification.py` serbest). Suite sonucunu yalnızca API çıktısından al. Raporun sonunda bu kurala
uyduğunu beyan et. Okumak zorunda kaldıysan hangi dosyayı neden okuduğunu açıkça yaz.

## Bu ailenin içeriği
- Varyant ekseni: leg_attachment=bottom_head, taban plakası L/W/t/Fy, beton taşıma izinli değeri, ankraj sayısı/çapı, çekme/kesme izinlileri, devrilme momenti
- Oracle dayanağı: taban plakası AISC DG1 (m, n; t_req=l·√(2fp/(0.9Fy))) — farklı yöntem çıkarsa FORMÜLASYON_FARKI; beton fp=P/(L·W); ankraj çekme T=M/(n/4·D_bc) − W/n; kesme V/n
- Kıyaslanacak büyüklükler: taban plakası gerekli t, beton basıncı, ankraj çekme/kesme
- **En az 30 vaka.** Eksenlerin tam ızgarasını kurma, akıllı örnekle: sınırlar, orta değerler,
  köşe durumları ve geçersiz girdiler. Geçersiz/eksik girdide suite BLOCKED dönmeli → KAPSAM_DIŞI
  (K4 uyarısını kontrol et). **REVIEW REQUIRED sonuçlar sayı üretir ve NORMAL kıyaslanır**
  (`judge(..., suite_status=...)` bunu zaten yapar); destek ailelerinde çoğu sonuç REVIEW'dur.
- Temel tanklar `bases.py`'de: dikey ayaklı tankta TEK destek kaydı = tüm ayak takımı (`leg_count`);
  her ayak için ayrı destek kaydı açma. Saddle'da Zick K katsayıları girilmezse BLOCKED döner.

## Kapsam
- Yazacağın yerler: `pressure-vessel-suite/tools/campaign/families/f16_ayak_bombe_taban_ankraj/` (`__init__.py`,
  `variants.py`, `oracle.py`, `run.py`, `results.json`) ve
  `pressure-vessel-suite/docs/validation/campaign-2026-10/F16-ayak_bombe_taban_ankraj.md`.
- **Dokunma:** `packages/**`, `apps/**`, `tools/campaign/*.py` (harness), mevcut `tests/**`,
  diğer ailelerin klasörleri. Harness'te hata bulursan düzeltme; etrafından dolaş ve rapora yaz.
- `run.py` tek komutla yeniden üretilebilir olmalı: `python -m tools.campaign.families.f16_ayak_bombe_taban_ankraj.run`
  (`pressure-vessel-suite/` kökünden). Koştur ve `results.json`'u üret.

## Rapor dosyası (`F16-ayak_bombe_taban_ankraj.md`) yapısı
1. Özet: vaka sayısı ve etiket dağılımı (DOĞRULANDI / FORMÜLASYON_FARKI / SAPMA / TEK_KAYNAK /
   KAYNAK_BEKLİYOR / KAPSAM_DIŞI).
2. Oracle formülleri (madde numarasıyla, kısa).
3. SAPMA tablosu: case_id · girdiler · suite · oracle · fark % · **yön (emniyetsiz/emniyetli)** ·
   olası neden (tahminse "tahmin" diye yaz).
4. Yayınlanmış vakalar tablosu.
5. Kapsam dışı ve bloklanan vakalar, nedenleriyle.
6. Temiz oda beyanı.

## Kabul kriterleri
1. `python -m tools.campaign.families.f16_ayak_bombe_taban_ankraj.run` hatasız biter ve `results.json` ≥30 vaka içerir.
2. Rapor dosyası yukarıdaki 6 bölümü içerir.
3. `git diff --stat` yalnızca kendi iki yolunu gösterir.
