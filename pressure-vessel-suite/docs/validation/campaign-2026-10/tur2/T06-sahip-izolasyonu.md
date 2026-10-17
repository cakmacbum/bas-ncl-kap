# T06 — Proje sahibi izolasyonu

Çalıştırma: `python -m tools.campaign.tur2.t06_sahip_izolasyonu.run`

`apps/api/main.py` içindeki 11 rota envantere alındı: health; geometry interpret; proje list/create/read/update/calculate/report HTML/STEP/STL; STEP import. Proje silme rotası tanımlı değil. A ve B sahipleriyle okuma, güncelleme, hesaplama, rapor ve model indirme istekleri sınandı. B, A'nın projesinde 404 aldı; A'nın özgün proje verisi korundu. Liste yalnız sahibinin projesini döndürdü. Delete kapsam dışı: endpoint yok.

Boş ve geçersiz UUID başlıkları 400 döndürdü. Büyük harfli UUID, tüm korumalı rotalarda A'nın aynı UUID'sine eşlenerek kabul edildi. Bu bulgu başlık biçimi şartını ihlal ediyor; farklı sahibin verisine erişim sağlamadığı için bu kampanyada emniyetli yön olarak sınıflandı. 10 başarısız vaka aynı doğrulama kusurunun rota bazlı tekrarlarıdır.

| Önem | Yön | Dosya:satır | Vaka | Beklenen → gözlenen |
|---|---|---|---|---|
| ORTA | Emniyetli (aynı UUID sahibine normalleşiyor) | `apps/api/auth.py:118` | uppercase-uuid, uppercase-list/create/read/update/calculate/report/step/stl/import | 400 → başlığa ve rotaya göre 200/201/404/415 |

Kapsam dışı: delete rotası mevcut değil. Harness değiştirilmedi; suite koduna yazılmadı.

SONUÇ: vaka=27 · geçti=17 · bulgu=10 (kritik=0, emniyetsiz=0) · kapsam_dışı=0
