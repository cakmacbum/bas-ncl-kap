# PAKET P10 — kampanya özeti (aggregate) + regresyon

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Dalga 2 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤15 satır rapor

## Görev
1. `cd pressure-vessel-suite && python -m tools.campaign.aggregate` çalıştır. Çıktı:
   `docs/validation/campaign-2026-10/OZET.md` + `ozet.csv`.
2. Bilinen sorun: bazı `results.json` dosyalarında etiketler bozuk kodlanmış (ör. f06'da
   `KAPSAM_DI\x9eI`, normali `KAPSAM_DIŞI`). `tools/campaign/aggregate.py` içinde etiket
   normalizasyonu ekle: Türkçe karakter mojibake'ini ve `_`/boşluk farkını tek kanonik etikete indir.
   Kanonik etiketler: DOĞRULANDI, FORMÜLASYON_FARKI, SAPMA, TEK_KAYNAK, KAYNAK_BEKLİYOR, KAPSAM_DIŞI.
   `results.json` dosyalarına dokunma.
3. OZET.md şunları içerir: aile × etiket matrisi (21 aile), toplamlar, SAPMA olan ailelerin listesi
   (teyit `teyit/V*.md` dosyalarında yapılacak), KAPSAM_DIŞI nedenlerinin aile başına özeti
   (FNN-*.md raporlarından derlenir, en çok 3 madde) ve P00c'de bulunan bağlanmamış hesap yollarının
   listesi (`.project-ai/paketler/P00c*.RAPOR.md`).
4. Regresyon: `python -m pytest tests -q -x --basetemp <sistem TEMP>/pv-p10` çalıştır. Sonucu
   (geçen/kalan) OZET.md sonuna yaz. Hata varsa düzeltme; yalnız raporla.
5. `tests/campaign/` içine normalizasyon için küçük bir test ekle.

## Kapsam
Yalnızca şunlara yaz: `tools/campaign/aggregate.py`, `tests/campaign/test_aggregate.py`,
`docs/validation/campaign-2026-10/OZET.md`, `docs/validation/campaign-2026-10/ozet.csv`.
`packages/**`, `apps/**` ve `families/**` dosyalarına dokunma.

## Kabul
Aggregate hatasız biter. Matriste bozuk etiket kalmaz. Pytest sonucu raporda yer alır.
