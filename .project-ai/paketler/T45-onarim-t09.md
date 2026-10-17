# PAKET T45-onarim-t09 — T09 torisferik: 60 kapsam dışı yeniden kur

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

## Bağlam
T09 raporu yok; 60 karşılaştırmanın tamamı KAPSAM_DIŞI. Knuckle yarıçapı eksik vaka (BAD-MISSING-R) PASS dönüyor (F03 ile aynı bulgu).

## Görev
0. ÖN ADIM (zorunlu): harness sahip tavanı düzeltildi. Mevcut results.json dosyalarındaki 'Project limit reached' satırları hesap değil, eski harness artefaktıdır. Bu paketin ilk işi: ilgili run.py'yi YENİDEN koştur, ardından aşağıdaki adımlara geç.
1. Neden KAPSAM_DIŞI: `results.json`'daki ilk 5 satırın `sonuc` ve `beklenen` alanlarını karşılaştır.
2. Karşılaştırma anahtarı (t_required, M, MAWP) suite çıktısında doğru adlarla alınıyor mu? Yanlışsa düzelt.
3. BAD-MISSING-R vakasının sonucunu raporla (PASS mı BLOCKED mı).
4. Raporu `tur2/T09-torisferik-uc.md` olarak yaz.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T45-onarim-t09.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T45-onarim-t09` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
Raporda sayısal karşılaştırmaların çoğu KAPSAM_DIŞI değil; BAD-MISSING-R sonucu açık yazılmış.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
