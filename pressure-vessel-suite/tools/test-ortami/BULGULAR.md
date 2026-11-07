# Test ortamı — ilk kıyas bulguları (2026-11-08)

Bağımsız motor (`hesap.js`) ↔ yerel API (`/api/calculate`), 4 örnek, tolerans ✅ ≤ %0.5 · ⚠️ ≤ %2.

| Örnek | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| elips (2:1) | 12 | 0 | 0 |
| yarım küre | 12 | 0 | 0 |
| torisferik | 3 | 9 | 0 |
| düz kapak | 7 | 5 | 0 |

## T-01 — Torisferik bombe: L ve r korozyonsuz kullanılıyor (site, emniyetli yön, ~%0.67)
Site `thickness` satırı: `L=1020 r=61.2` (yeni ölçü) → `M=1.77062`, `t=10.636 mm`.
Bağımsız: korozyonlu `L+CA=1022`, `r+CA=63.2` → `M=1.75533`, `t=10.565 mm`.
UG-32(e) ölçüleri korozyonlu durumda ister (V-16 kuralı: iç ölçü korozyonla büyür). Site
M'yi korozyonsuz r ile büyük buluyor → kalınlık %0.67 fazla, MAWP %0.67 düşük → **emniyetli** ama
V-16 tekilleştirmesinin torisferik L/r'ye uygulanmadığını gösteriyor. Global MAWP ve test
basınçları da aynı oranda kayıyor.

## T-02 — Düz kapak MAWP'de d korozyonsuz (site, emniyetsiz yön, ~%0.8)
Site `thickness`: `d_corroded=1004` ✓. Site `mawp`: `d_corroded=1000` (adı korozyonlu, değeri
yeni çap) → MAWP 0.014083 MPa; bağımsız `d=1004` ile 0.013971 MPa. Aynı bileşende kalınlık ve
MAWP farklı çap kullanıyor → MAWP **%0.8 yüksek (emniyetsiz)**. Küçük ama yön yanlış.

## T-03 — Düz kapak `mawp` satırı PASS (gözlem)
MAWP 0.014 MPa ≪ P=1.2 MPa iken `mawp` satırı `PASS`, `thickness` satırı `FAIL`. MAWP satırının
durumu "hesap yapıldı" anlamında olabilir; kullanıcı açısından yanıltıcı — incelenmeli.

## Not
`flat_attachment_factor` girilmezse site düz kapağı `BLOCKED_MISSING_INPUT` yapıyor (doğru
davranış). Örnekte C=0.33 seçildi; bu UG-34 şekline göre doğrulanmış bir değer değil.
Düzeltmeler bu turda yapılmadı.
