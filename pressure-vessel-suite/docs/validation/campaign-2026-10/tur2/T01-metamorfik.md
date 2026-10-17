# T01 — Metamorfik / monotonluk

## Dağılım

Planlanan tarama: 8 bileşen ailesi × 6 ilişki × 5 nokta = 240 vaka. `run.py` tamamlandı ve `results.json` üretildi. Sonuçlar: 0 geçti, 0 bulgu, 240 kapsam dışı. Bu nedenle monotonluk hakkında geçerli bir sonuç çıkarılamadı.

## Bulgular

Bulgu yok; karşılaştırılabilir beş noktalı ölçüm serisi oluşturulamadı. Harness çağrılarının önemli bir kısmı API'nin proje limitine (`{"detail":"Project limit reached"}`) takıldı. Diğer bazı girdiler, terminal bombe zorunlu bileşen sıralaması doğrulamasından geçmedi. `run_case` proje temizleme/limit sıfırlama sunmadığından ölçüm serileri doğrulanamadı.

| Önem | Yön | Dosya:satır | Durum |
|---|---|---|---|
| — | — | — | Doğrulanmış ihlal yok; tarama altyapısı vaka sonuçlarını ölçmeye izin vermedi. |

## Kapsam dışı

- Bütün 240 kayıt geçerli ölçüm üretemedi.
- Koni ve tek başlı proje girdileri mevcut API doğrulamasına uygun tam bileşen sırası sağlamadı.
- Nozul alan ölçümü ile dış basınç ve sıcaklık ilişkilerinin sayısal metrik eşlemesi doğrulanamadı.

SONUÇ: vaka=240 · geçti=0 · bulgu=0 (kritik=0, emniyetsiz=0) · kapsam_dışı=240
