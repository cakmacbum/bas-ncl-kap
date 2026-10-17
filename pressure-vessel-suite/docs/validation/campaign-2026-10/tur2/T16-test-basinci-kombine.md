# T16 — Test basıncı, statik kafa ve yöneten bileşen

Vaka: 48 · geçti: 6 · bulgu: 42 · kapsam dışı: 0

Oracle: UG-99(b) üst basıncı = 1,3 × en düşük bileşen MAWP × S_test/S_design; alt nokta = üst basınç + ρgh. Statik kafa SI dönüşümü bağımsız hesaplanır.

| Önem | Yön | Dosya:satır | Vaka | Beklenen | Gözlenen |
|---|---|---|---|---:|---:|
| YÜKSEK | Emniyetsiz düşük basınç: statik kafa eksik | API sonucu (uygulama dosya:satır clean-room gereği incelenmedi) | 18 MAWP vakası; ör. T16-07-vertical-500-0.8-mawp | 1.790467 MPa | 1.778208 MPa |
| ORTA | Emniyetli yüksek basınç: design_pressure yerine MAWP tabanı | API sonucu (uygulama dosya:satır clean-room gereği incelenmedi) | 24 tasarım tabanı kontrolü; ör. T16-02-vertical-0-0.8-design | 1.040000 MPa | 1.778208 MPa |

Kapsam dışı vakalar: yok

SONUÇ: vaka=48 · geçti=6 · bulgu=42 (kritik=0, emniyetsiz=18) · kapsam_dışı=0
