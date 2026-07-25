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

### Bağımsız doğrulama turu 1'de ortaya çıkanlar (2026-07-26)

Kaynak: [`validation/asme-worked-examples.md`](validation/asme-worked-examples.md).

- **B-02 — Eliptik bombede yalnızca 2:1 destekleniyor.** `head_elliptical_thickness`
  `K = 1.0`'ı sabit alıyor; `Head` modelinde bombe derinliği / en-boy oranı alanı yok.
  2:1 dışında bir elipsoidal bombe (ör. `K = 0.99`, karşılaştırma kaynağında görüldü)
  girilirse sessizce 2:1 gibi hesaplanır. UG-32(d) zaten yalnız 2:1'i kapsar; genel oran
  **Appendix 1-4(c)** ister ve o da yok. Kullanıcı 2:1 dışı bombe giremediği için bugün
  yanlış sonuç riski yok — ama bombe oranı girdisi eklenirse **önce** bu kapatılmalı.
- **B-03 — Dış çap alternatifleri (App 1-1(a)(1), 1-4(c)) implement edilmemiş.**
  Karşılaştırılan iki ticari yazılım da varsayılan olarak bu formları kullanıyor. Suite'in
  iç çap formları %0.4-0.9 **daha ince** kalınlık üretiyor. Küçük ama sistematik ve
  emniyetsiz yönde; imalatçı çıktıyı ticari yazılımla karşılaştırırsa fark görecektir.
- **B-04 — UG-34(c)(3) (dairesel olmayan düz kapak, `Z` faktörü) yok.** Yalnız
  UG-34(c)(2) dairesel kapak var.
- ~~**B-05 — UG-32(e) torisferik ve UG-32(f) yarım küre bağımsız teyit almadı.**~~
  **Kapatıldı (tur 2, 2026-07-26):** torisferik anma tablosuyla 90 nokta üzerinden,
  yarım küre bombe tipi karşılaştırmasıyla doğrulandı.
- **B-06 — Torisferik taç yarıçapı varsayılanı iç çaptır, standart ASME F&D dış çap kullanır.**
  Kullanıcı taç yarıçapını girmezse `L = D` (iç çap) varsayılıyor; yayınlanmış karşılaştırma
  taç yarıçapının **dış çapa** eşit olduğunu gösteriyor (tur 2, V-14). Fark %0.5 mertebesinde
  ve emniyetsiz tarafta. `Head` modelinde dış çap alanı olmadığı için bu turda değiştirilmedi;
  varsayım kullanıldığında uyarı veriliyor. Taç yarıçapı girildiğinde sorun yok.

- **B-07 — Nozul takviyesi yalnız radyal nozul içindir.** UG-37'nin eğik nozul `F`
  faktörü uygulanmıyor (`F = 1.0` alınıyor); eğik nozul girilirse uyarı veriliyor.
- **B-08 — Appendix 1-7 büyük açıklık kontrolü yok.** Karşılaştırma kaynağı aynı nozul
  için App 1-7'yi de uyguluyor; suite yalnız UG-37/UG-40 alan değiştirme yöntemini yapıyor.
  Büyük açıklıklarda (yaklaşık `d > D/2` veya `d > 40 in`) bu ek kontrol gerekir.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 2.3 — bağımsız doğrulama turu 3 (2026-07-26)*
