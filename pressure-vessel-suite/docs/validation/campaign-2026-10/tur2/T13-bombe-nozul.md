# T13 — Bombe üzerindeki nozullar

ASME VIII-1 2025 seçili temel tankı ile 33 API vakası çalıştırıldı: eliptik,
torisferik ve yarım küre bombelerde merkezden 801 mm'ye kadar konumlar.
80% D sınırı 800 mm olarak ele alındı; merkez, sınırın içi, tam sınır ve dışı
örneklendi.

Bağımsız küresel bölüm basınç kalınlığı referansı:
`t_r = P R / (2 S E - 0.2 P)`. Eliptik 2:1 bombede tepe küresel yarıçapı
D/2, yarım kürede D/2, torisferik referans küresel tepe yarıçapı D alındı.
Bu değerler tüm sonuç satırlarında `beklenen.t_r_mm` olarak kayıtlıdır;
servis çıktı sözleşmesi t_r ara değerini sunmadığı için eşitlik iddiası yoktur.

## Dağılım

- Vaka: 33
- GEÇTİ: 30
- BULGU: 3
- KAPSAM_DIŞI: 0

| Önem | Yön | Vaka / gözlem | Dosya:satır |
|---|---|---|---|
| YÜKSEK | emniyetsiz | eliptik-801, torisferik-801, hemisferik-801: nozul merkez ofseti 801 mm (>0.8D=800 mm); API sonucu `PASS`, uyarı yok. Beklenen yerleşim dışı için BLOCKED veya uyarı. | `packages/code-asme-viii-1` nozul takviye sonucu; temiz oda kuralı gereği implementasyon okunmadı, satır doğrulanamadı |

## Kapsam dışı

- Yok. `t_r` kıyası oran/çıktı alanı API'de bulunmadığından bağımsız referans
  olarak raporlandı, birebir servis çıktısı karşılaştırması yapılmadı.

SONUÇ: vaka=33 · geçti=30 · bulgu=3 (kritik=0, emniyetsiz=3) · kapsam_dışı=0
