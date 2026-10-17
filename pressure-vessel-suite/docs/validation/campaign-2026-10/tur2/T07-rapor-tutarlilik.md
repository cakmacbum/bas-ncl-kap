# T07 — Rapor çıktısı ve hesap tutarlılığı

20 vaka çalıştırıldı; **0 geçti, 20 bulgu, 0 kapsam dışı**. Vakalar 10 farklı örnek projenin tekrarından oluşur. Her birinde hesap JSON'u ile `/report.html` çıktısı karşılaştırıldı.

| Önem | Yön | Bulgu | Dosya:satır |
|---|---|---|---|
| ORTA | emniyetli | Hesap payload'ındaki sayısal ara değerlerin bir kısmı HTML raporunda bulunamadı; bileşen kimlikleri ve PASS/REVIEW REQUIRED/OUT OF SCOPE durumları görünür. | `apps/api/services.py:189` |

Tam vaka girdileri ve gözlemler `tools/campaign/tur2/t07_rapor_tutarlilik/results.json` içindedir. PDF ayrıca doğrulanmadı: bu ortamda WeasyPrint native bağımlılıkları yüklenemedi. HTML doğrulaması tamamlandı.

SONUÇ: vaka=20 · geçti=0 · bulgu=20 (kritik=0, emniyetsiz=0) · kapsam_dışı=0
