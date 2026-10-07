# PAKET F20 — Her şey dahil uçtan uca tanklar

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1 · Yürütücü: codex:yaz
> Mod: yaz → worktree'de yazarsın, dönüş = ≤15 satır rapor
> Codex yoksa: bu paket Claude Sonnet'e brief'lenir.
> Oluşturan: Orkestra şefi (Opus) · Tarih: 2026-10-07

## Sen kimsin, ne yapıyorsun
20 paralel ajandan birisin. Bir basınçlı kap tasarım sitesinin **Her şey dahil uçtan uca tanklar** hesabını çok sayıda
varyantla koşturuyorsun. Sonuçları **bağımsız** bir kontrol hesabıyla ve yayınlanmış örneklerle
kıyaslıyorsun. Amaç hata bulmak, suite'i haklı çıkarmak değil. Sayı uydurma. Emin olmadığın şeyi
rapora "Açık soru" olarak yaz.

## Amaç
`tools/campaign/families/f20_uctan_uca/`: varyant üret → site API'sinden hesaplat → temiz-oda oracle ile
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
  aile için öncelikli küme: **oracle**. Konuna uyan vakaları ayrı `case_id` ile ekle ve
  `ref_source` olarak kaynak atfını yaz.

## TEMİZ ODA KURALI (zorunlu)
Oracle'ı Kod veya standart formülünden **sıfırdan** yaz. Şu implementasyonları **açma ve okuma**:
`packages/code-asme-viii-1`, `packages/code-en-13445`, `packages/nozzles`, `packages/supports`,
`packages/external-pressure`, `packages/mdmt`, `packages/flanges`, `packages/calc-core` (yalnız
`verification.py` serbest). Suite sonucunu yalnızca API çıktısından al. Raporun sonunda bu kurala
uyduğunu beyan et. Okumak zorunda kaldıysan hangi dosyayı neden okuduğunu açıkça yaz.

## Bu ailenin içeriği
- Varyant ekseni: 3 temel tank (bases.py) × özellik kombinasyonları: tüm bombe tipleri, koni, 3+ nozul, destek tipi, dış basınç, MDMT, yük durumları, EN/ASME
- Oracle dayanağı: iç tutarlılık: suite kalınlığı → suite MAWP ≥ P (Tur 4 tekniği); hacim ve kütle elle (silindir + bombe hacim formülleri, ρ=7850); hata listesi boş mu; rapor HTML üretiliyor mu (services.generate_report_html); 5 tankta STEP üretimi (services.generate_step)
- Kıyaslanacak büyüklükler: hacim, kütle, MAWP tutarlılığı, rapor/STEP üretimi, hata sayısı
- **En az 30 vaka.** Eksenlerin tam ızgarasını kurma, akıllı örnekle: sınırlar, orta değerler,
  köşe durumları ve geçersiz girdiler. Geçersiz girdide suite REVIEW/BLOCKED dönmeli; bunu
  KAPSAM_DIŞI say, ama K4 uyarısının verildiğini kontrol et.

## Kapsam
- Yazacağın yerler: `pressure-vessel-suite/tools/campaign/families/f20_uctan_uca/` (`__init__.py`,
  `variants.py`, `oracle.py`, `run.py`, `results.json`) ve
  `pressure-vessel-suite/docs/validation/campaign-2026-10/F20-uctan_uca.md`.
- **Dokunma:** `packages/**`, `apps/**`, `tools/campaign/*.py` (harness), mevcut `tests/**`,
  diğer ailelerin klasörleri. Harness'te hata bulursan düzeltme; etrafından dolaş ve rapora yaz.
- `run.py` tek komutla yeniden üretilebilir olmalı: `python -m tools.campaign.families.f20_uctan_uca.run`
  (`pressure-vessel-suite/` kökünden). Koştur ve `results.json`'u üret.

## Rapor dosyası (`F20-uctan_uca.md`) yapısı
1. Özet: vaka sayısı ve etiket dağılımı (DOĞRULANDI / FORMÜLASYON_FARKI / SAPMA / TEK_KAYNAK /
   KAYNAK_BEKLİYOR / KAPSAM_DIŞI).
2. Oracle formülleri (madde numarasıyla, kısa).
3. SAPMA tablosu: case_id · girdiler · suite · oracle · fark % · **yön (emniyetsiz/emniyetli)** ·
   olası neden (tahminse "tahmin" diye yaz).
4. Yayınlanmış vakalar tablosu.
5. Kapsam dışı ve bloklanan vakalar, nedenleriyle.
6. Temiz oda beyanı.

## Kabul kriterleri
1. `python -m tools.campaign.families.f20_uctan_uca.run` hatasız biter ve `results.json` ≥30 vaka içerir.
2. Rapor dosyası yukarıdaki 6 bölümü içerir.
3. `git diff --stat` yalnızca kendi iki yolunu gösterir.
