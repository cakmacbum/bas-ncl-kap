# PAKET P11 — harness X-Client-Id + aggregate rapor yolu

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Dalga 2 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤15 satır rapor

## Sorun 1 — harness tüm vakalarda 400 alıyor
Ana dala W04 commit'i (`869e874`, sahip izolasyonu) girdi. Artık `apps/api/auth.py:107-119`
`require_owner`, anonymous modda geçerli ve kanonik bir UUID içeren `X-Client-Id` başlığı istiyor.
Başlık yoksa 400 "Missing or invalid X-Client-Id" dönüyor. `tools/campaign/harness.py` `run_case`
bu başlığı göndermiyor; `tests/campaign/test_examples.py` bu yüzden kalıyor.

Düzeltme: harness'te sabit bir kampanya UUID'si tanımla (ör. `uuid.uuid5(NAMESPACE_URL, "pv-campaign")`,
kanonik küçük harf). TestClient isteklerinin hepsine `X-Client-Id` başlığını ekle. Supabase modu
kampanya kapsamı dışında; harness auth modunu değiştirmesin, yalnız başlık eklesin.

## Sorun 2 — aggregate FNN raporlarını bulamadı
P10 OZET.md "FNN-*.md raporları bulunamadı" yazdı. Oysa dosyalar
`docs/validation/campaign-2026-10/F01-govde_ug27.md` … `F21-flans_app2.md` yolunda duruyor. Yol veya
glob hatasını düzelt; `pathlib` kullan, dosya adı deseni `F[0-9][0-9]-*.md`. Ayrıca
`docs/validation/campaign-2026-10/teyit/V*.md` dosyalarının `HÜKÜM:` satırlarını okuyup OZET.md'ye bir
"Teyit" tablosu ekle (aile, hüküm satırı). Satır bozuk kodlanmışsa (mojibake) metni kanonikleştir.

## Görev sırası
1. Harness düzeltmesi + `pytest tests/campaign -q --basetemp <sistem TEMP>/pv-p11` yeşil.
2. Aggregate düzeltmesi + `python -m tools.campaign.aggregate` → OZET.md yeniden üret.
3. Tam regresyon: `python -m pytest tests -q --basetemp <sistem TEMP>/pv-p11b`. Sonucu raporla.

## Kapsam
Yalnızca şunlara yaz: `tools/campaign/harness.py`, `tools/campaign/aggregate.py`, `tests/campaign/**`,
`docs/validation/campaign-2026-10/OZET.md`, `docs/validation/campaign-2026-10/ozet.csv`.
`packages/**`, `apps/**`, `families/**` dosyalarına dokunma. Worktree içine `.pytest-tmp` veya
`.pytest_cache` açma (`-p no:cacheprovider`).

## Kabul
`tests/campaign` yeşil. OZET.md'de 21 aile için KAPSAM_DIŞI nedenleri ve Teyit tablosu var. Tam
regresyon sonucu raporda yer alır.
