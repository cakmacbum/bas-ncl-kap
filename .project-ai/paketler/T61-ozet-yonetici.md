# PAKET T61 — Kampanya yöneticisi: tüm sonuçları topla, özetle, çelişkileri listele

> Proje: BASINCLI-KAP · M2 Tur 5 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir.

## Rol
Sen kampanya yöneticisisin. Diğer ajanların sonuçlarını topluyorsun. Kendi testlerini yazmıyorsun; yalnız
okuyup birleştiriyorsun ve çelişkileri işaretliyorsun. Hiçbir kaynak dosyayı DEĞİŞTİRME.

## Görev
1. Şu sonuç dosyalarını oku (varsa), her biri için vaka sayısı ve durum dağılımını çıkar:
   - `tools/campaign/tur2/t02_birim_tutarlilik/results.json` (ve diğer tur2/*/results.json, results_v2.json öncelikli)
   - `tools/campaign/tur2/t04_fuzz/results_v2.json`
   - `tools/campaign/tur2/t01_metamorfik/results_v2.json` (`cases` listesi)
   - `tools/campaign/tur2/t11_yatay_tank_tarama/results_v2.json`
   - `tools/campaign/tur3/mega_*/results_v2.json` ya da `results.json`
   - `tools/campaign/tur5/bombe_tarama/results.json`
   - `tools/campaign/tur5/mass_govde_20261017.csv` (satır sayısı ve verdict dağılımı)
   Durum alanı adları farklı olabilir (durum, sonuc, result, verdict). Her dosyada bulduğun alanı belirt.
2. Her dosya için tek satır: `dosya | vaka | GEÇTİ/UYUŞUR | BULGU/UYUŞMUYOR | KAPSAM_DIŞI/VERİ_YOK | diğer`.
3. Çelişkileri listele: aynı konuda iki dosyanın farklı sonuç verdiği yerler (ör. T11 sınıflandırması,
   T04 ile önceki T04). Her çelişki için hangi dosyanın daha güvenilir olduğunu ve neden olduğunu yaz.
4. Kampanya toplamı: geçerli (GEÇTİ veya UYUŞUR) vaka sayısı, geçersiz (KAPSAM_DIŞI / VERİ_YOK) sayısı.
5. Rapor: `docs/validation/campaign-2026-10/tur5/T61-ozet.md` olarak yaz. Son satır:
   `SONUÇ: dosya=N · geçerli=a · geçersiz=b · çelişki=c`.

## Kapsam
Yalnız `docs/validation/campaign-2026-10/tur5/T61-ozet.md` yaz. Başka hiçbir dosyayı değiştirme.
Betik kullanacaksan `tools/campaign/tur5/ozet/` altına koy (ayrı klasör).

## Kabul
Rapor var; her dosya için satır var; çelişki bölümü var (yoksa "çelişki yok" açıkça yazılı); SONUÇ satırı var.
