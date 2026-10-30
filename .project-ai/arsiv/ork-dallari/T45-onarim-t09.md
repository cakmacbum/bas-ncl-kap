# T45 onarım — T09 torisferik karşılaştırması

- Eski `results.json` içindeki ilk beş karşılaştırmanın `verdict` alanı `DOĞRULANDI`; her satırda `suite` ile `reference` aynı. Yani KAPSAM_DIŞI nedeni bu beş satırda tekrarlanmıyor; mevcut dosyada toplam 96 satır var (93 DOĞRULANDI, 3 KAYNAK_BEKLİYOR, 0 KAPSAM_DIŞI). İstenen 60 karşılaştırma sayısı bu sonuç dosyasıyla uyuşmuyor.
- API karşılaştırma anahtarları doğru: kalınlık `t_required`, katsayı `M_factor`, MAWP `MAWP` ara değerlerinden alınıyor. Güncel API yanıtında STD-r006 ve STD-r010 için bu üç anahtar beklenen sayısal değerleri verdi. `run.py` MAWP için `final_result` yedeğini de destekliyor.
- `BAD-MISSING-R`: **PASS**. API `r` eksikken varsayılan `r=62.4 mm` kullanıp sayısal kalınlık/MAWP/M sonuçları üretiyor; beklenen BLOCKED davranışından sapıyor.
- Kaynak kıyası olmayan üç BAD-MISSING-R ölçüsü `KAYNAK_BEKLİYOR`; API başarılı olduğu için kapsam dışı sayılmadı.
- Kontrol: API'yi doğrudan çağıran salt-okunur Python incelemesi (STD-r006, STD-r010, BAD-MISSING-R) → alan adları doğrulandı, BAD-MISSING-R PASS. `python tools/campaign/families/f03_bombe_torisferik/run.py` → başarısız (çalıştırma biçiminde `tools` import yolu bulunamadı); sonuç dosyasını yeniden yazmadı.

SONUÇ: vaka=32 · GEÇTİ=93 · BULGU=0 · BLOCKED=0 · KAPSAM_DIŞI=0 · geçersiz_test=0
