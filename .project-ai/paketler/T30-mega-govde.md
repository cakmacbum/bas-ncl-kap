# PAKET T30-mega-govde — Gövde + bombe rastgele tarama

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 3 (toplu test) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

## Görev
Tek bir `tools/campaign/tur3/mega_govde/run.py` yaz. Rastgele ama tohumlu (seed=1001) üretici kullan; **110 vaka** üret.
Her vaka bir `/api/projects` + `/calculate` çağrısı (harness.run_case). Kontroller:

- **Sağlamlık:** HTTP 500 veya NaN/inf yok. (BULGU: herhangi biri)
- **Tutarlılık:** PASS olan bileşende utilization ≤ 1.0; FAIL olanda > 1.0. (BULGU: tersi)
- **Monotonluk:** aynı tankta P %20 artınca t_required artar veya eşit kalır. (BULGU: azalma)
- **Bağımsız değer:** sonucun t_required'ı kendi kodunla (UG-27: t=P·R/(S·E−0.6P), R=D_i/2+CAi) ±%1 hesapla. Gövdeler için. (BULGU: fark >%1, dosya:satır ipucu ver)

Her vaka için `results.json` satırı: `{"id","family","girdi","sonuc","kontrol","durum":"GEÇTİ|BULGU|BLOCKED_BEKLENEN"}`.
Çalıştırmanın sonunda konsola: vaka sayısı, GEÇTİ/BULGU/BLOCKED dağılımı, ilk 10 BULGU'nun id'si.

Rapor: `pressure-vessel-suite/docs/validation/campaign-2026-10/tur3/T30-mega-govde.md` — dağılım tablosu, her BULGU için
girdi özeti ve kontrol adı. Son satır: `SONUÇ: vaka=110 · geçti=a · bulgu=b · blocked=c`.

## Kurallar
- Harness: `pressure-vessel-suite/tools/campaign/harness.py` (`run_case`), taban tanklar `bases.py`, örnekler `examples.py`,
  sonuç kataloğu `RESULT_CATALOG.md`. Harness `X-Client-Id` gönderir (P11). Harness'i değiştirme.
- `packages/**` ve `apps/**` DOKUNMA. Hataları yalnız raporla (vaka, girdi, beklenen, gözlenen, dosya:satır tahmini).
- Pytest: `--basetemp <sistem TEMP>/pv-<paket>` ve `-p no:cacheprovider`.
- Gizli bilgi (.env, anahtar) yok.
- Verimlilik: tek bir `run.py` her şeyi koşturup `results.json` yazsın; çıktı tablosunu konsola kısa bas.

## Kapsam
Yalnızca `tools/campaign/tur3/mega_govde/` ve `docs/validation/campaign-2026-10/tur3/T30-mega-govde.md`.

## Kabul
`python -m tools.campaign.tur3.mega_govde.run` hatasız biter; sonuç 110 satır.
