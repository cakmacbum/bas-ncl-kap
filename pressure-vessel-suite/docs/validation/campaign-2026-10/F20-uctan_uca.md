# F20b — Katalogla uçtan uca kıyas

API projeleri: 30; sayısal bileşen kıyası: 90.
Etiket dağılımı: DOĞRULANDI 90, FORMÜLASYON_FARKI 0, SAPMA 0, TEK_KAYNAK 0, KAYNAK_BEKLİYOR 0, KAPSAM_DIŞI 0

## Oracle
Silindir için t = P·R/(S·E−0.6P); 2:1 elipsoid kafa için t = P·D/(2·S·E−0.2P). API ara değerlerinden yalnız girişler alındı; hesap bağımsız yazıldı.

## SAPMA tablosu
Karşılaştırılan büyüklük required thickness'tir; fark yönü hacim gibi emniyet yorumu taşımaz. Düşük fark API girdisindeki yuvarlamadan gelebilir.
| Vaka | Tür | Suite mm | Oracle mm | Fark % | Yön |
|---|---|---:|---:|---:|---|

## Yayınlanmış vakalar
K1–K4 kaynaklarında bu örnek geometriler ve eşleşen ASME girdileri bulunmadığından yayınlanmış vakalar sayısal karşılaştırmaya alınmadı; girdileri eşleşmeyen K4 örneği uydurma eşleşmeyle kullanılmadı.

## Kapsam dışı / bloklanan
Katalogda listelenen diğer hesap türleri için doğrulanmış çalışan örnek yok. Bu koşu katalog `thickness` türünü kullanır; eksik satır varsa sonuç JSON'da sayısal karşılaştırma sayısına dahil edilmez.

## Temiz oda
Katalog ve examples.py ile harness arayüzü okundu. Yasaklı hesap implementasyonları açılmadı; oracle formülleri bağımsız yazıldı.
