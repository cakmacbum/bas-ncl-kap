# S01 — EN 13445 boşluk taraması (SALT OKUR, kod yazma)
Yollar `pressure-vessel-suite/` köküne göre. Gizli bilgi yok.

Amaç: `packages/code-en-13445/` paketinde EN 13445-3 (ve gerekiyorsa -2 malzeme / -5 muayene) kapsamında NE VAR, NE YOK listesi.
1. `packages/code-en-13445/src/` altındaki her hesap fonksiyonunu/sınıfı listele: hangi EN 13445-3 maddesi (dosyadaki yorum/docstring'e göre),
   girdi, `verified`/OUT_OF_SCOPE/BLOCKED durumu. `design_code.py`'de hangi `check_*` metotları gerçek hesap, hangileri OUT_OF_SCOPE dönüyor.
2. Karşılaştırma için ASME tarafı: `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` `check_*` listesi — ASME'de olup
   EN'de olmayan kontrolleri çıkar (ör. dış basınç, açıklık takviyesi, flanş, koni, düz kapak, destek, yorulma, hidrotest).
3. `tests/` altında EN 13445'e ait testleri say (dosya adları + test sayısı).
4. `docs/` ve `.project-ai/` içinde EN 13445 için yazılmış eksik/limitasyon notlarını bul (dosya:satır).

Çıktı (DONUS'a): tablo — | EN 13445-3 madde/konu | durum (VAR / KISMİ / YOK / OUT_OF_SCOPE) | dosya:satır | not |, sonra
ASME'ye göre eksik kontroller listesi, sonra önerilen paketleme (bağımsız, paralel yapılabilir 3–5 paket; her biri hangi dosyalar).
Uydurma madde numarası yazma; dosyada geçmiyorsa "madde no kodda yok" de.
