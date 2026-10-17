# T03 — Sınır ve geçersiz girdiler

Çalıştırma: `python -m tools.campaign.tur2.t03_sinir_girdi.run` · 57 vaka.
Sonuçlar vaka girdisi, beklenen yanıt, HTTP/status ve sınıflandırma ile
`tools/campaign/tur2/t03_sinir_girdi/results.json` dosyasındadır.

Dağılım: 32 GEÇTİ, 25 BULGU, 0 KAPSAM_DIŞI. Beklenti 422 veya
BLOCKED/NOT CALCULATED idi. HTTP 200 ile PASS/FAIL/REVIEW REQUIRED dönenler,
beklenen fail-closed sınır yanıtını vermediği için bulgudur.

| Önem | Yön | Dosya:satır | Vaka / girdi | Beklenen → gözlenen |
|---|---|---|---|---|
| YÜKSEK | emniyetsiz: hatalı girdide hesap sonuçları üretildi | `apps/api/main.py:96-102`, `packages/domain/src/domain/conditions.py:24-29` | pressure-design-3/4; pressure-operating-3/4; temperature-1..4; shell-thickness-3/4; shell-diameter-3/4; shape-enum-01/07..10/16..17/19 | 422 veya BLOCKED/NOT CALCULATED → HTTP 200, içinde PASS/FAIL/REVIEW REQUIRED |
| YÜKSEK | emniyetli kapanmıyor: sunucu hatası | `apps/api/main.py:96-102`, `packages/domain/src/domain/conditions.py:24-29` | pressure-design-7/8, pressure-operating-7, temperature-7, shell-thickness-7 | 422 veya BLOCKED/NOT CALCULATED → HTTP 500 (NaN/Infinity) |

Şema bağlamı: `conditions.py:24-29` basınç için yalnız `gt=0` tanımlıyor;
`geometry.py:22-35` çap ve et kalınlığı için pozitiflik kullanıyor. 1e9,
string numeric ve bazı aşırı değerler HTTP model doğrulamasından geçiyor.
Doğrudan 422 dönen 32 vaka GEÇTİ olarak sınıflandı. Kapsam dışı vaka yok.

SONUÇ: vaka=57 · geçti=32 · bulgu=25 (kritik=0, emniyetsiz=25) · kapsam_dışı=0
