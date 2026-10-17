# PAKET T43-onarim-t04 — T04 fuzz kapsam dışı nedenleri

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir. Örn. `tools/campaign/...` = `pressure-vessel-suite/tools/campaign/...`. Depo kökünde `tools/` yoktur.

## Bağlam
T04 (300 vaka) 250'si KAPSAM_DIŞI. Sebep çoğunlukla girdi üretici tarafında olabilir (geçersiz kombinasyon).

## Görev
0. ÖN ADIM (zorunlu): harness sahip tavanı düzeltildi. Mevcut results.json dosyalarındaki 'Project limit reached' satırları hesap değil, eski harness artefaktıdır. Bu paketin ilk işi: ilgili run.py'yi YENİDEN koştur, ardından aşağıdaki adımlara geç.
1. Kapsam dışı satırların `sonuc` mesajlarını grupla (ilk 80 karakter).
2. Üreticinin fiziksel olarak geçersiz kombinasyon üretip üretmediğini kontrol et (ör. nozul çapı > gövde çapı, eksik malzeme).
3. Üretici düzeltilmeli: geçerli girdi üret, geçersiz girdi üretiyorsa BLOCKED beklentisi ile ayrı say.
4. 300 vakayı yeniden koştur; kapsam dışı oranını raporla.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T43-onarim-t04.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T43-onarim-t04` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
Kapsam dışı < %10; nedenler ve yeni dağılım raporda.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
