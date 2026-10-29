# Konfigüratör yerleşim araştırması ve Adım 03 spec'i (U01)

- **Tarih:** 2026-10-29 · **Paket:** U01 (yalnız araştırma, kod yok)
- **Yöntem:** Web araması (≥5 aday) + yerleşik tarayıcıda 3 hedefin salt-gözlemi (`getComputedStyle`, `getBoundingClientRect`, `matchMedia` kuralları). Form gönderilmedi, hesap/giriş yok, çerez bandında yalnız reddet. MXD'de adım 1→2 geçişi sunucuda anonim "taslak" açtı (ölçüm için başka bir şey yapılmadı). `rea` MCP bağlanamadı; tarayıcı ölçümü kullanıldı.
- **Ön bilgi:** MyTank davranışı `mytank-spec.md`'de; burada yalnız YERLEŞİM ölçüleri var. Metin/görsel/CSS kopyalanmadı; yalnız ölçü ve desen.
- Etiket: **[G]** tarayıcıda ölçüldü · **[W]** yalnız web/haber kaynağından · **[?]** doğrulanamadı.

## 1. Aday tablosu

| # | Ad | URL | Güçlü | Zayıf | Durum |
|---|---|---|---|---|---|
| 1 | MyTank Configurator (Ziemann Holvrieka) | https://tank-config.ziemann-holvrieka.com/ | Alan bölgesi: sol parametre / sağ önizleme, bağımsız kaydırma; akordeon gruplama; hesaplanan alanlar salt-okunur; mobilde yapışkan önizleme; kot çizgili 2D + 3D | Nozul/ayak ayrıntısı yok; görünüm düğmeleri sağ üstte küçük; hata mesajı yok | [G] ölçüldü |
| 2 | MXD Process Studio — Tank CPQ | https://designer.mxdprocess.app/ (giriş: mxdprocess.com/tank-designer) | 5 adımlı numaralı sekme şeridi (Industry/Size/Tank type/Adjust/Quote), "STEP 2 OF 5" üst etiketi, Geri/İleri alt çubuğu, her adımda tek soru | Adım 1-3'te önizleme yok; çok geniş tek sütun (945 px); "Saving…" ile sunucu taslağı | [G] ölçüldü (adım 1-2) |
| 3 | Mersen grafit eşanjör konfigüratörü | https://www.mersen.com/en/mersen-heat-exchanger-configurator | Sol 404 px marka/başlık bandı + sağ 605 px form; "ADIM 1" + % ilerleme + Restart; 3D ikinci adımda istek üzerine | Canlı 3D yok; sol panel dekoratif | [G] kısmen |
| 4 | mk QuickDesigner (konveyör) | https://www.quickdesigner.com | Çalışırken evrilen canlı 3D önizleme, uygulanabilirlik denetimi, 3D CAD dışa aktarım [W] | Giriş sayfası eski; iç ekran erişilemedi | [W]/[G] giriş |
| 5 | Rittal RiPanel | rittal.com → Configuration System | Plausibilite (makul değer) denetimi, 3D, delik kütüphanesi, CAD dışa aktarım [W] | İç ekran açılmadı | [W] |
| 6 | Pall Vessel Configurator | https://pall.com/en/oil-gas/vessel-configurator-program.html | Basınçlı kap: çap, nozul boyut/konum, malzeme, basınç; çizim ve 3D dakikalar içinde [W] | Doğrudan web arayüz görülmedi | [W] |
| 7 | Pentair Structural Super Tanks | https://pentair.eu/pl/node/403380 | Çok adımlı: boyut → delikler → opsiyon [W] | İç ekran açılmadı | [W] |
| 8 | TTP / Mersen / SolidRules (CADENAS PARTsolutions) | fluidpowerworld.com ve varindustries.vargroup.com | Sihirbaz → parametrik 3D → 150+ CAD biçimi [W] | Yalnız haber sayfası | [W] |

## 2. Seçilen hedef: MyTank (ölçü) + MXD (adım şeridi)

**Neden MyTank:** Tek alan-yakın örnek; panel ve önizleme **aynı anda görünür**, form her tuşta önizlemeyi günceller ve ölçüler tam olarak bizim sorunumuzun karşıtı: dar ama hiyerarşik panel, **geniş ve baskın önizleme**. MXD'den yalnız **numaralı adım şeridi + "ADIM x/y" etiketi + Geri/İleri alt çubuğu** desenini alıyoruz (zaten 3.1–3.5 sekmelerimiz var).

## 3. Ölçülü yerleşim (MyTank, gözlem)

| Genişlik (vw) | Izgara | Panel | Önizleme | Not |
|---|---|---|---|---|
| 1440 | `500px 735px` | 500 (%34,7) | 735 (%51; kalan ~%14 boşluk/kenar) | Panel sabit px, önizleme `fr` |
| 1024 | `450px 574px` | 450 (%44) | 574 | Eşik 1200 px'te panel 500→450 |
| 768 | tek sütun `1fr` | 753 | 753×369, **sticky top 56 px** | Önizleme üstte yapışkan, form altta akar |
| 375 | tek sütun | 375 | 375×292 (≈%36 yükseklik), sticky top 56 | Giriş 15 px yazı |

Medya sorguları: 1200 / 1000 / 768 / 545 px. Giriş kutusu 39–40 px yükseklik, 16 px yazı, etiket kutunun ÜSTÜNDE. Bölüm başlık çubuğu ~38 px, koyu lacivert, sağda `[−]/[+]`. Panel (`configurator-column`) kendi başına `overflow:auto`; sayfa kaydırması yok (masaüstü). Önizlemenin sağ üstünde bir bilgi kartı (Technical Specifications) + `2D | 3D` düğmeleri (~98×30 px) bulunur.

### ASCII — masaüstü (1440×900)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [logo]  Başlık                                                          │
├───────────────────────────┬─────────────────────────────────────────────┤
│ 500 px  (kendi scroll)    │ ≈ 735 px  — önizleme TÜM yüksekliği doldurur│
│ ┌───────────────────────┐ │                         ┌───────────────┐   │
│ │ Reset           EN DE │ │                         │ Özet kartı    │   │
│ ├───────────────────────┤ │                         │ [2D][3D]      │   │
│ │ ▌Standart [−]         │ │       ┌────┐            └───────────────┘   │
│ │  etiket               │ │       │ kap│  ölçü çizgileri                │
│ │  [ giriş 39px ]       │ │       └────┘                                │
│ │ ▌Temel Geometri [−]   │ │                                             │
│ │  ...                  │ │  (kamera düğmeleri: sol alt/sağ üst)        │
│ └───────────────────────┘ │                                             │
└───────────────────────────┴─────────────────────────────────────────────┘
```

### ASCII — ≤768 px

```
┌───────────────────────┐ ← üst bar 56 px
├───────────────────────┤
│ ÖNİZLEME sticky       │ 292–369 px (top:56)
├───────────────────────┤
│ form akışı (sayfa     │
│ kaydırır, önizleme    │
│ yukarıda kalır)       │
└───────────────────────┘
```

## 4. Hiyerarşi (hedef desen)

Başlık → **Adım** (şerit) → **Grup** (kart/akordeon) → **Alan**:

```
Adım 03 Kap Geometrisi            ← sayfa başlığı (1 satır) + 1 cümle özet
[3.1 Gövde][3.2 Bombeler][3.3 Nozullar][3.4 Manşonlar][3.5 Mesnetler]   ← adım şeridi, numaralı, ilerleme
  Grup: "Ana ölçüler"            ← kart, başlık 38 px, açılır/kapanır, varsayılan AÇIK
    Alan: etiket üstte, giriş 40 px, birim sağda içte, ipucu altta 12 px
    Alan: hesaplanan (salt-okunur, gri zemin, "hesaplanan" rozeti)
  Grup: "Ayrıntılar"              ← varsayılan KAPALI (gelişmiş)
```

Kural: bir adımda en çok 2 grup açık, grup başına en çok 6 alan görünür; gerisi "Ayrıntılar".

## 5. İpucu / yardım deseni

- Alan altı **tek satır ipucu** (12 px, soluk): birim + izin verilen aralık (ör. "mm · 500–6000"). Uzun açıklama yok.
- Ayrıntı için etiketin yanında `?` simgesi → tıklayınca küçük balon (tek açık). Hover'a bağlı değil (dokunmatik).
- Hesaplanan alanlar: salt-okunur, gri, formül metni **balonun içinde** (panelde kalabalık yapmaz).
- Önizleme sol altında "Kontroller" yardım balonu (sürükle=döndür, tekerlek=yakınlaş).

## 6. 3D araç çubuğu ve görünüm sekmeleri

- **Görünüm sekmeleri** (3D Önizleme / Ölçülü Kesit / Kesin Model): önizleme alanının **üst sol köşesinde** segment kontrol, 32 px yükseklik, tek satır; MyTank'ta 2D|3D sağ üstteydi — bizde sol üste al, sağ üst özet kartına kalsın.
- **Kamera düğmeleri** (İzo/Üst/Ön/Yan/Sığdır): önizlemenin **alt ortası**nda yatay yüzen çubuk, 36 px, yalnız ikon+kısa etiket; mobilde yalnız ikon.
- **STEP/STL indir**: sağ üstte tek "Dışa aktar ▾" menüsü (3 satır sığmaz).
- Bilgi kartı (hacim, çap, toplam boy): sağ üstte 220 px, kapanabilir.
- Önizleme tuvali kendi kutusunu doldurur; oran sabitlemesi yok (kutu yüksekliği = ekran − üst bar).

## 7. Uyarı (hata) sunumu

MyTank'ta mesaj yok; ders: biz ekleyeceğiz. Üç katman:
1. **Alan içi:** kırmızı çerçeve + alan altında tek satır sebep (ipucu satırının yerine geçer).
2. **Grup rozeti:** grup başlığında sayaç (ör. kırmızı "2"), kapalı gruptayken de görünür.
3. **Sorunlar:** panel üstünde değil, **adım şeridinin hemen altında** daraltılmış özet ("3 sorun" → tıkla aç → listeden alana git). Hata yokken satır hiç yer kaplamaz.
Önizlemede sorunlu bileşen kırmızı kontur (opsiyonel).

## 8. Kaydırma davranışı

- Masaüstü: **sayfa kaydırmaz**; yalnız sol panel kendi içinde kayar; üst bar + adım şeridi + (sabit) Önceki/Sonraki alt çubuğu panelde yapışkan.
- Önizleme tam yükseklik, kaydırmaz.
- Hesap akordeonları (sonuç/ara değer) Önceki/Sonraki çubuğunun **altında**, formun sonunda; adım şeridiyle karışmaz.
- Mobil: önizleme sticky üstte, form sayfayla kayar.

## 9. Kırılma noktaları (3)

| Aralık | Davranış |
|---|---|
| ≥1200 px | Panel **480 px**, önizleme `1fr` (≥720). |
| 1000–1199 px | Panel **420 px**, araç çubuğu ikon-only, bilgi kartı kapalı varsayılan. |
| 769–999 px | Panel **360 px** kalıcı, önizleme `1fr`; kamera çubuğu ikon-only. |
| ≤768 px | Tek sütun: önizleme üstte sticky, yükseklik `min(36vh, 300px)`, alt: form; adım şeridi yatay kayar. |

(MyTank'ın 1200/1000/768/545 eşikleri esas alındı; biz 545'i atladık.)

## 10. Adım 03'e uygulanacak 10 madde

1. **Izgara:** `main` iki sütun; panel 480 px sabit (≥1200), 420 (1000–1199), 360 (769–999); önizleme `1fr`. Panel ≤ %40 genişlik, önizleme ≥ %55.
2. **Yüksekliği tek yerde kilitle:** gövde `100vh − üst bar`; yalnız panel `overflow:auto`; önizleme tam yükseklik (şu an dar panel + uzun önizleme oransızlığı kalkar).
3. **Panel üstü sırası:** (a) adım başlığı 1 satır, (b) alt adım sekmeleri 3.1–3.5 tek satır 40 px, kaydırılabilir, numaralı; (c) Sorunlar özeti (sadece hata varsa); (d) form.
4. **Alt adım başına en çok 2 açık grup:** "Ana ölçüler" (açık) ve "Ayrıntılar" (kapalı). Alan etiketi üstte, giriş 40 px, 16 px yazı, grup içi boşluk 12 px.
5. **İpucu:** her alanın altında tek satır 12 px (birim · aralık); açıklama `?` balonunda; hesaplanan alanlar gri salt-okunur + "hesaplanan" rozeti.
6. **Önceki/Sonraki:** panelin altında **sabit** 56 px çubuk (sol Önceki, sağ Sonraki, ortada "3.2 / 5"); formun içinden çıkar.
7. **Hesap akordeonları** (sonuçlar) Önceki/Sonraki çubuğunun altına değil, **formun sonuna** ve varsayılan kapalı; her biri 38 px başlık.
8. **Görünüm sekmeleri** (3D Önizleme / Ölçülü Kesit / Kesin Model) önizleme **sol üstüne** 32 px segment kontrol; **kamera düğmeleri** alt ortada yüzen 36 px çubuk; **STEP/STL** sağ üstte tek "Dışa aktar ▾".
9. **Sorunlar:** panelin altına değil, adım şeridinin altında sayaçlı daraltılmış satır; alan içi kırmızı çerçeve + tek satır sebep; grup başlığında rozet.
10. **Mobil (≤768):** tek sütun, önizleme sticky üstte `min(36vh, 300px)`, adım şeridi yatay kayar, alt Önceki/Sonraki çubuğu ekranın altında yapışkan; kamera çubuğu yalnız ikon.

## 11. Doğrulanamayanlar

- MXD'nin "Adjust" adımındaki canlı önizleme yerleşimi (adım 4) ölçülmedi; anonim sunucu taslağı açmamak için 2. adımda durduruldu. [?]
- QuickDesigner, RiPanel, Pall iç ekranları açılamadı; yalnız web haberlerine dayanıyor. [W]
- MyTank'ın tuval kontrol düğmesi konumları ekran görüntüsünden yaklaşık; hassas ölçü alınmadı. [?]
