# T02 — Birim ve ölçek tutarlılığı

## Yöntem ve şema

21 public API vakası `SHELL-01` için `thickness.t_required` değerini karşılaştırdı. SI vakalarında tüm uzunluk girdileri `k` ile çarpıldı, basınç 1.2 MPa sabit tutuldu ve beklenen değer temel vakanın `k` katı alındı. Tolerans ±0.1% (göreli). Imperial vakaları aynı fiziksel boyutların inç, basıncın psi karşılıklarıyla `unit_system=Imperial` gönderildi; beklenen çıktı inç cinsinden temel değerin `k/25.4` katıydı.

Domain şemasında `VesselProject.unit_system` SI/Imperial olarak tanımlı (`packages/domain/src/domain/project.py:64`). Bununla birlikte geometri alan açıklamaları mm (`packages/domain/src/domain/geometry.py:22-32`), tasarım basıncı MPa (`packages/domain/src/domain/conditions.py:24-27`) diyor. Şemada alan bazlı alternatif birim veya dönüşüm bildirimi yok.

## Sonuçlar

- Vaka sayısı: 21
- GEÇTİ: 11 (temel vaka ve 10 SI ölçek vakası)
- BULGU: 10 (Imperial etiketli, dönüştürülmüş girdiler)
- KAPSAM_DIŞI: 0

| Önem | Yön | Dosya:satır | Girdi / beklenen / gözlenen |
|---|---|---|---|
| ORTA | Güvenli (gereken et kalınlığını fazla bildiriyor) | `packages/domain/src/domain/project.py:64`; birim alanı API hesap girişinde normalize edilmiyor | Imperial: mm→in ve MPa→psi değerleri, `unit_system=Imperial`. Beklenen `t_required` 0.1727603 in temel vakada; gözlenen 102.457635 mm eşdeğer sayısal değer. 0.1% tolerans dışı. Aynı fark 10 ölçek katsayısında da sürüyor. |

## Kapsam dışı

- Yok. Dönüşüm şemasının belirsizliği nedeniyle Imperial davranışı gözlenen sözleşmeye göre BULGU olarak tutuldu.

SONUÇ: vaka=21 · geçti=11 · bulgu=10 (kritik=0, emniyetsiz=0) · kapsam_dışı=0
