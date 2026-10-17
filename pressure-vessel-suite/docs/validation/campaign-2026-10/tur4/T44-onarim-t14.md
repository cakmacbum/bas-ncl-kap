# T44 — T14 etekli kolon yeniden yazımı

- Komut: `python -m tools.campaign.tur2.t14_dikey_kolon_yuk.run` — tamamlandı; 30 vaka satırı ve `SONUÇ` özeti üretildi.
- H/D aralığı: 3–20; rüzgâr: 20/35/50 m/s; deprem katsayısı: 0/0.2/0.4.
- Etek gerilmesi (`skirt_stress`): 30/30 vakada mevcut.
- Taban halkası sonucu: 0/30 vakada mevcut. API çıktısında ayrı bir taban halkası hesaplama türü bulunmuyor; bu bir kapsam bulgusudur.
- Eski “Project limit reached” satırları aramasında bulunmadı. Mevcut F14 ailesinin yeniden çalıştırılması `results.json` dosyasını kapsam dışındaki bir klasöre yazacağından o dosya değiştirilmedi.
- Yanlış iç içe yoldaki deneme dosyaları kaldırılmadı.
- SONUÇ: vaka=30 · GEÇTİ=30 · BULGU=0 · BLOCKED=0 · KAPSAM_DIŞI=0 · geçersiz_test=0
