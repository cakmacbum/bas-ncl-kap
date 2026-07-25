# Limitations and Out-of-Scope Items

> Bu doküman, V1 sürümünün kapsam dışı bıraktığı özellikleri ve bilinen sınırlamaları listeler.

## V1 kapsam dışı (Later)

| Kategori | Özellik | Gerekçe |
|---|---|---|
| Yük | Rüzgâr ve deprem | Sonraki sürüm |
| Yük | Nozula gelen harici boru yükleri | Sonraki sürüm |
| Yük | Yorulma analizi | Sonraki sürüm |
| Yapı | Düz kapak / kör flanş | Sonraki sürüm |
| Yapı | Konik bölüm | Sonraki sürüm |
| Yapı | Ceketli kaplar | Kapsam dışı |
| Yapı | Çok odalı kaplar | Kapsam dışı |
| Yapı | Eşanjör tüp demetleri | Kapsam dışı |
| Analiz | Design by Analysis | Sonraki sürüm |
| Malzeme | Otomatik malzeme veritabanı | Sonraki sürüm |
| Malzeme | Sünme / yüksek sıcaklık | Sonraki sürüm |
| Malzeme | Kompozit Type III/IV | Kapsam dışı |
| Akışkan | Kriyojenik özel kurallar | Kapsam dışı |
| Düzen | Taşınabilir gaz tüpleri / ADR | Kapsam dışı |
| Düzen | Ateşle temas eden ekipmanlar | Kapsam dışı |

## Tamamlanan Faz 4/5 özellikleri

Aşağıdaki özellikler planlanan "Later" kapsamından çıkarılmış ve V1'e dahil edilmiştir:

| Özellik | Paket | Durum |
|---|---|---|
| Dış basınç / vakum (UG-28) | `external-pressure/` | ✅ Faz 5 |
| Flanş tasarımı (Appendix 2) | `flanges/` | ✅ Faz 5 |
| Destek / saddle (Zick) | `supports/` | ✅ Faz 5 |
| FEA entegrasyonu (iskelet) | `fea/` | ✅ Faz 5 |
| PED sınıflandırma motoru | `ped-2014-68-eu/` | ✅ Faz 4 |
| EN 13445 hesap rotası | `code-en-13445/` | ✅ Faz 4 |
| ESR matrisi + DoC + isim plakası | `compliance/` | ✅ Faz 4 |
| StandardPack sürüm kilidi | `standards/manifests/` | ✅ Faz 4 |

## Bilinen sınırlamalar

- **Malzeme girişi:** V1'de kullanıcı izin verilen gerilme, akma ve çekme dayanımlarını manuel girer.
  Otomatik malzeme veritabanı veya lisanslı paket import'u yoktur.
- **Statik sıvı yüksekliği:** V1'de hesaba dahil değildir.
- **FEA:** İskelet modülü — çözücü (CalculiX / Code_Aster) kurulu değilse `REVIEW_REQUIRED` durumu döner; sahte PASS üretmez.
- **CAD — torisferik bombeler:** Görsel amaçlı yaklaşık elipsoidal profil revolve edilir; gerçek torisferik geometri (crown + knuckle) henüz yok.
- **CAD — düz flanş:** Union-tabanlı mimari (plaka + skirt); diğer bombelerden farklı strateji, daha kırılgan.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 2.0 — Faz 4/5 tamamlanmasına göre güncellendi (2026-07-24)*
