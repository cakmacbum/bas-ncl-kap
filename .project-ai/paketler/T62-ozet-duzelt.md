# PAKET T62 — T61 özetini düzelt (tek toplam YOK, tür bazlı tablo)

> Proje: BASINCLI-KAP · M2 Tur 5 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir.

## Bağlam
T61 özeti (`docs/validation/campaign-2026-10/tur5/T61-ozet.md`) kabul edilmedi. Sorunlar:
1. Tek "geçerli 2319 / geçersiz 381" toplamı anlamsız: vaka, satır, sayısal inceleme ve kapsam dışı farklı
   türde sayılar, tek sayıya indirgenemez.
2. T02 için "durum" (PASS/FAIL) ile "sonuc" alanı karıştırılmış; hangisinin karar alanı olduğu kanıtlanmamış.
3. Eski ve v2 sonuç dosyaları aynı kaynak için çift sayılmış olabilir (T04 eski/v2, T11 eski/v2, T01 eski/v2).
4. Kaydetme/son kontrol başarısız oldu.

## Görev
1. Her kaynak için TEK bir satır yaz; kaynak = tek karar dosyası (eski sürüm değil):
   - tools/campaign/tur2/t01_metamorfik/results_v2.json (`cases`)
   - tools/campaign/tur2/t02_birim_tutarlilik/results.json (karar alanı: önce `durum`'a bak; hangi alanın
     karar olduğunu iki vaka ile göster)
   - tools/campaign/tur2/t04_fuzz/results_v2.json (`vakalar[].sonuc`)
   - tools/campaign/tur2/t11_yatay_tank_tarama/results_v2.json (`durum_v2`)
   - tools/campaign/tur3/mega_destek|mega_govde|mega_nozul|mega_yuk/results_v2.json (`durum_v2`)
   - tools/campaign/tur5/bombe_tarama/results.json (`durum`)
   - tools/campaign/tur5/mass_govde_20261017.csv (`verdict`)
   Satır formatı: `kaynak | birim (vaka|satır) | GEÇERLİ_OLUMLU | GEÇERLİ_BULGU | İNCELEME | KAPSAM_DIŞI`
   (GEÇERLİ_OLUMLU = GEÇTİ/UYUŞUR/PASS; GEÇERLİ_BULGU = BULGU/UYUŞMUYOR/FAIL-yetersiz; İNCELEME = SAYISAL_INCELEME;
   KAPSAM_DIŞI = KAPSAM_DIŞI/BLOCKED/VERİ_YOK).
2. TOPLAM SATIRI YAZMA. Birimler karışık; tek sayı üretme.
3. Çelişki bölümü: yalnız kanıtlanabilen çelişkileri yaz (aynı vaka kümesinde iki karar dosyasının farklı
   sonuç vermesi). Eski ve v2 karşılaştırmasını çelişki sayma; v2'nin kaynak olduğunu açıkça yaz.
4. Rapor: `docs/validation/campaign-2026-10/tur5/T62-ozet.md` (T61'i değiştirme). Son satır:
   `SONUÇ: kaynak=N · çelişki_kanıtlı=M`.

## Kapsam
Yalnız `docs/validation/campaign-2026-10/tur5/T62-ozet.md`. Başka dosya değiştirme.

## Kabul
Tablo var; toplam satırı yok; her kaynak için satır var; çelişki bölümü var; SONUÇ satırı var.
