# Vessela — Alan Envanteri

Kaynak: apps/web-ui/src (pages.tsx, geometrySteps/*, inputs/*, store.ts varsayılanları). Ayrıntı: alan-envanteri.json. (?) = belirsiz (koda göre koşullu / ekran görüntüsü yok).

Toplam kayıt: 401; belirsiz: 25.


## Adım 1 — Yeni Proje

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| Kayıtlı Projeler | Proje aç | seçim |  | (boş: 'Proje seçin…') | <sunucudaki projeler: 'no · ad · Rev X'> | Önce 'Projeleri Yenile' düğmesi; kaydedilmemiş değişiklik varsa onay sorar. | 05-yeni-proje-kayitli-proje.png |
| Başlangıç Şablonları | Şablonu Uygula (düğme) | seçim |  |  | Yatay Hava Tankı; Vakumlu Proses Tankı; Dikey Seperatör | Şablonlar yalnız geometri ve tasarım koşullarını doldurur; malzeme dayanımları (S, akma, çekme) girilmez (0). | 03-yeni-proje-sablon-hava-tanki.png; 04-yeni-proje-sablon-vakum-tanki.png |
| Proje Kimliği | Proje Numarası | metin |  | PRJ-001 |  |  | 02-yeni-proje.png |
| Proje Kimliği | Proje Adı | metin |  | Yeni Basınçlı Kap |  |  | 02-yeni-proje.png |
| Proje Kimliği | Müşteri | metin |  | (boş) |  |  | 02-yeni-proje.png |
| Proje Kimliği | Revizyon | metin |  | A |  |  | 02-yeni-proje.png |
| Hesap Rotası | Hesap Standardı | seçim |  | ASME VIII Division 1 | ASME VIII Division 1; EN 13445 | EN 13445 seçilince uyarı: kapsamı tamamlanmamış modüller REVIEW_REQUIRED/NOT_CALCULATED dönebilir. | 02-yeni-proje.png |
| Hesap Rotası | Standart Sürümü | metin |  | 2025 |  |  | 02-yeni-proje.png |
| Hesap Rotası | Kap Yönelimi | seçim |  | Yatay | Yatay; Dikey |  | 02-yeni-proje.png |

## Adım 2 — Tasarım Koşulları

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| Basınçlar | Çalışma Basıncı | sayı | MPa | 1 |  |  | 06-tasarim-kosullari.png |
| Basınçlar | Tasarım Basıncı | sayı | MPa | 1,2 |  | Hesaplarda kullanılan basınç | 06-tasarim-kosullari.png |
| Basınçlar | Azami İzin Verilen (PS) | sayı | MPa | 1,5 |  | PED / isim plakası | 06-tasarim-kosullari.png |
| Basınç Tahliye Sistemi | Tahliye sistemi | seçim |  | Tanımlı değil | Tanımlı değil; Etkin | Emniyet vanası/patlama diski ayarını girin. Kapasite sertifikası olmadan sonuç nihai PASS değildir. | 06-tasarim-kosullari.png |
| Basınç Tahliye Sistemi | Korunan MAWP | sayı | MPa | 0 (boş) |  | Boş bırakılırsa hesaplanan global MAWP kullanılır | 06-tasarim-kosullari.png |
| Basınç Tahliye Sistemi | İzin verilen accumulation | sayı | % | 10 |  |  | 06-tasarim-kosullari.png |
| Basınç Tahliye Sistemi | Cihaz tipi (yalnız tahliye 'Etkin' iken görünür) | seçim |  | Emniyet vanası | Emniyet vanası; Patlama diski |  | 08-tasarim-tahliye-etkin.png |
| Basınç Tahliye Sistemi | Set / burst basıncı (yalnız 'Etkin' iken) | sayı | MPa | tasarım basıncı |  | Kapasite, blowdown ve senaryo doğrulaması yetkin mühendis/üretici verisiyle tamamlanmalıdır. | 08-tasarim-tahliye-etkin.png |
| Sıcaklıklar | Çalışma Sıcaklığı | sayı | °C | 120 |  |  | 06-tasarim-kosullari.png |
| Sıcaklıklar | Tasarım Sıcaklığı | sayı | °C | 150 |  |  | 06-tasarim-kosullari.png |
| Sıcaklıklar | Asgari Tasarım Sıcaklığı | sayı | °C | -10 |  |  | 06-tasarim-kosullari.png |
| Sıcaklıklar | Hidrotest Sıcaklığı | sayı | °C | 20 |  |  | 06-tasarim-kosullari.png |
| Sıcaklıklar | Darbe Testi Sıcaklığı | sayı | °C | 0 |  | 0 = darbe testi yapılmadı. ?: Charpy darbe testinin yapıldığı sıcaklık; UCS-66 muafiyet değerlendirmesinde kullanılır. | 06-tasarim-kosullari.png |
| Dış Basınç / Vakum | Dış Basınç | sayı | MPa | 0 |  | ?: 0 bırakılırsa UG-28 kontrolü yapılmaz. | 06-tasarim-kosullari.png |
| Dış Basınç / Vakum | Vakum Koşulu | seçim |  | Yok | Yok; Var | ?: 'Var' seçilirse 0,1013 MPa dış basınç olarak değerlendirilir. | 06-tasarim-kosullari.png |
| Akışkan | Akışkan Yoğunluğu | sayı | kg/m³ | 0 |  | 0 = statik kafa düzeltmesi uygulanmaz. ?: Su için 1000. | 06-tasarim-kosullari.png |
| Akışkan | Sıvı Seviyesi | sayı | mm | (boş) |  | Kabın en alt noktasından sıvı yüzeyine yükseklik. Boşsa statik kafa uygulanmaz. Dikey kapta bileşen sırası boşsa uyarı çıkar. | 06-tasarim-kosullari.png |
| Korozyon Payı | İç Korozyon Payı | sayı | mm | 2 |  |  | 06-tasarim-kosullari.png |
| Korozyon Payı | Dış Korozyon Payı | sayı | mm | 0 |  |  | 06-tasarim-kosullari.png |

## Adım 3 — Kap Geometrisi

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| Üst çubuk | Modelden içe aktar (dosya seç) (?) | metin |  |  | *.step; *.stp; *.stl | STL yalnız görüntülenir (hesaba girmez); STEP için tanıma çekmecesi açılır, seçilenler onay kutularıyla uygulanır (Seçilenleri uygula). | 09-geometri-31-govde.png |
| Panel sekmesi | Geometri / Hesap girdileri | seçim |  | Geometri | Geometri; Hesap girdileri |  | 25-girdiler-sekme.png |
| Önizleme | Önizleme görünümü | seçim |  | 3D Önizleme | 3D Önizleme; Ölçülü Kesit; Kesin Model; Gerilme; Yüklenen model (yalnız dosya yüklenince) |  | 20-onizleme-3d.png; 21-onizleme-olculu-kesit.png; 22-onizleme-kesin-model.png; 23-onizleme-gerilme.png |
| Önizleme | Gerilme kaynağı (Gerilme sekmesinde) | seçim |  | Analitik | Analitik; FEA | Gösterge amaçlı — ASME tasarım onayı değildir. | 23-onizleme-gerilme.png |
| Önizleme | SCL eşdeğer gerilme (FEA çalışınca) (?) | seçim |  | von Mises | von Mises; Tresca |  | 23-onizleme-gerilme.png |
| Önizleme | Dışa aktar menüsü (?) | seçim |  |  | STEP / STL / çizim (DXF-SVG) biçimleri — EXPORT_OPTIONS |  | 24-onizleme-disa-aktar-menu.png |
| 3.1 Gövde zinciri | Zincir halkası seçimi (şerit) | seçim |  | (seçili yok) | SHELL-01 …; <koni halkaları> | Düzenlemek için halkaya tıklayın (3D modelde de tıklanabilir). | 09-geometri-31-govde.png |
| 3.1 Gövde zinciri / + Sol/+ Sağ ekle | Eklenecek parça | seçim |  | Silindir | Silindir; Koni; Daralt + Silindir |  | 11-geometri-31-uc-ekle-koni-form.png |
| 3.1 Gövde zinciri / ekle | Uç çapı (Koni, Daralt) | sayı | mm | uç çapının %60'ı (10'a yuvarlı, ≥50) |  | izinli 50–20000; eşit çapta koni eklenemez | 11-geometri-31-uc-ekle-koni-form.png |
| 3.1 Gövde zinciri / ekle | Koni boyu (Koni, Daralt) | sayı | mm | 500 |  | izinli 10–30000; yarı tepe açısı α>30° kırmızı | 11-geometri-31-uc-ekle-koni-form.png |
| 3.1 Gövde zinciri / ekle | Teğet boyu / Yeni silindir boyu | sayı | mm | 1000 |  | izinli 10–60000 | 11-geometri-31-uc-ekle-koni-form.png |
| 3.1 Gövde zinciri / ekle | Et kalınlığı (Silindir, Koni) | sayı | mm | komşu halkanın kalınlığı |  | izinli 1–250 | 11-geometri-31-uc-ekle-koni-form.png |
| 3.1 Gövde zinciri / seçili halka | Düğme: ← Taşı | seçim |  |  |  | Zincir en az 3 elemanlı olmalı; son gövde silinemez. | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / seçili halka | Düğme: Taşı → | seçim |  |  |  | Zincir en az 3 elemanlı olmalı; son gövde silinemez. | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / seçili halka | Düğme: Kopyala | seçim |  |  |  | Zincir en az 3 elemanlı olmalı; son gövde silinemez. | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / seçili halka | Düğme: Sil | seçim |  |  |  | Zincir en az 3 elemanlı olmalı; son gövde silinemez. | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / seçili halka / Ana ölçüler (silindir) | İç çap (ID) | sayı | mm | 1000 |  | izinli 50–20000 | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ana ölçüler (silindir) | Et kalınlığı (t) | sayı | mm | 12 |  | izinli 1–250 | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ana ölçüler (silindir) | Teğet boyu (L) | sayı | mm | 2000 |  | izinli 10–60000 | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ana ölçüler (koni) | Büyük çap (?) | sayı | mm |  |  | izinli 50–20000 |  |
| 3.1 Gövde zinciri / Ana ölçüler (koni) | Küçük çap (?) | sayı | mm |  |  | izinli 50 – (büyük çap−1) |  |
| 3.1 Gövde zinciri / Ana ölçüler (koni) | Boy (?) | sayı | mm |  |  | izinli 10–30000 |  |
| 3.1 Gövde zinciri / Ana ölçüler (koni) | Et kalınlığı (t) (?) | sayı | mm |  |  | izinli 1–250 |  |
| 3.1 Gövde zinciri / Ayrıntılar (koni) | Yarı tepe açısı α (?) | sayı | ° | hesaplanan (salt okunur) |  | 30° üzeri özel analiz, 60° üzeri Appendix 1-8 kapsam dışı. |  |
| 3.1 Gövde zinciri / Ayrıntılar | Malzeme | seçim |  | MAT-01 | <proje malzemeleri: 'ID — tanım'> |  | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ayrıntılar | İç korozyon payı | sayı | mm | 2 |  |  | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ayrıntılar | Sac toleransı | sayı | % | 12,5 |  |  | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ayrıntılar | Kaynak birleşimi | seçim |  | WJ-01 | — yok —; <kaynak birleşimleri> |  | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ayrıntılar (yalnız silindir) | UG-28 A faktörü | sayı |  | 0 (girilmedi) |  | 0 = girilmedi (dış basınç bloke) | 10-geometri-31-govde-form.png |
| 3.1 Gövde zinciri / Ayrıntılar (yalnız silindir) | UG-28 B faktörü | sayı | MPa | 0 (girilmedi) |  | 0 = girilmedi | 10-geometri-31-govde-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) | Bombe tipi | seçim |  | Elipsoidal (2:1) | Elipsoidal (2:1); Torisferik; Yarım küresel; Düz kapak |  | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) | Çap ilişkisi | seçim |  | Bağlı (linked) | Bağlı (linked); Bağımsız (independent) | Bağlı: bombe çapı zincirden otomatik. Bağımsız: bombe çapını elle gir. | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ana ölçüler | Bombe iç çapı | sayı | mm | 1000 (Bağlı iken salt okunur) |  | izinli 50–20000; zincir ucuyla uyuşmazsa kırmızı uyarı | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ana ölçüler | Et kalınlığı (t) | sayı | mm | 12 |  | izinli 1–250 | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | Düz flanş boyu (sf) | sayı | mm | 40 |  | izinli 0–500 | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar (eliptik) | Kubbe derinliği (h) | sayı | mm | 0 |  | 0 = standart 2:1 (h = Di/4) | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar (torisferik) | Taç yarıçapı (R) (?) | sayı | mm | 0 |  | 0 = standart (R = Di) |  |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar (torisferik) | Mafsal yarıçapı (r) (?) | sayı | mm | 0 |  | 0 = standart (r = 0,06·Di) |  |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar (düz kapak) | Düz kapak C katsayısı (UG-34) (?) | sayı |  | 0 (girilmedi) |  | 0 = girilmedi |  |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar (düz kapak) | Düz kapak C katsayısı (EN 13445-3 Md.10) (?) | sayı |  | 0 (girilmedi) |  | 0 = girilmedi (EN hesabı bloke); UG-34 C'si ile aynı değil |  |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | Malzeme | seçim |  | MAT-01 | <proje malzemeleri> |  | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | Kaynak birleşimi | seçim |  | WJ-01 | — yok —; <kaynak birleşimleri> |  | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | İç korozyon payı | sayı | mm | 2 |  |  | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | Sac toleransı | sayı | % | 12,5 |  |  | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | UG-33 A faktörü | sayı |  | 0 |  | 0 = girilmedi (dış basınç bloke) | 13-geometri-32-bombe-form.png |
| 3.2 Bombeler (sol/alt ve sağ/üst bombe için ayrı kart) / Ayrıntılar | UG-33 B faktörü | sayı | MPa | 0 |  | 0 = girilmedi | 13-geometri-32-bombe-form.png |
| 3.3 Flanşlı nozullar / Yeni flanşlı nozul / Ana ölçüler | Tip | seçim |  | Flanşlı | Flanşlı; Slip-on flanş; Pedli takviyeli; Adam deliği (manway) |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ana ölçüler | Boyut (NPS / DN) | seçim |  | 4" (DN100) | <boru katalog boyutları> | Boru ve flanş ölçüleri katalogdan gelir. | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ana ölçüler | Et serisi (SCH) | seçim |  | SCH40 | SCH… — et X mm (boyuta bağlı) |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ana ölçüler | Host (nereye gelecek?) | seçim |  | ilk gövde | <gövde/koni/uç bombeler> |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ana ölçüler | Konum z (host başından) — gövde/koni host | sayı | mm | host boyunun yarısı |  | izinli 0–host boyu; kaydırıcı da var; aralık dışı eklenemez (kırpılmaz) | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ana ölçüler | Yerleşim çapı (bombe ekseninden) — bombe host (?) | sayı | mm | 0 |  | 0 = tepe; izinli 0–2×bombe yarıçapı |  |
| 3.3 Flanşlı nozullar / Ana ölçüler | Çevresel açı θ | sayı | ° | 0 | hızlı düğmeler: 0, 90, 180, 270 | izinli 0–360 (yatayda 0° Üst, 90° Sağ, 180° Alt, 270° Sol) | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ayrıntılar | Flanş sınıfı | seçim |  | Class 150 | Class 150; Class 300; Class 600; Class 900; Class 1500; Class 2500 |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ayrıntılar | Takviye pedi | onay |  | kapalı | (Pedli takviyeli tipte zorunlu açık) |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Ayrıntılar | Ped dış çapı (ped açıkken) (?) | sayı | mm | 2 × boru dış çapı |  | izinli 1,1×OD – 4×OD |  |
| 3.3 Flanşlı nozullar / Ayrıntılar | Ped kalınlığı (ped açıkken) (?) | sayı | mm | host et kalınlığı |  | izinli 1–200 |  |
| 3.3 Flanşlı nozullar / Nozul listesi (düzenle) | Host / z veya D / θ (seçili nozul) | sayı | mm/° | (nozulun değeri) | Host seçimi | Boyut değişimi için nozulu silip yeniden ekleyin. | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Nozul listesi (düzenle) | Takviye pedi (seçili nozul) + Ped dış çapı + Ped kalınlığı | onay | mm |  |  |  | 15-geometri-33-nozul-form.png |
| 3.3 Flanşlı nozullar / Nozul listesi | Satır silme (✕) | seçim |  |  |  |  | 15-geometri-33-nozul-form.png |
| 3.4 Manşonlar / Ana ölçüler | Bağlantı | seçim |  | Dişli (threaded) manşon | Dişli (threaded) manşon; Soket kaynaklı (socket weld) |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar | Boyut (NPS / DN) | seçim |  | 1" | 1/2" – 4" (DN15–DN100) |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar | Manşon formu | seçim |  | Tam manşon | Tam manşon; Yarım manşon; Weldolet (katalogda yok, seçilemez) |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar | Host (nereye gelecek?) | seçim |  | ilk gövde | <gövde/koni/uç bombeler> |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar | Konum z (host başından) / Yerleşim çapı (bombe) | sayı | mm | host boyunun yarısı / 0 |  |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar | Çevresel açı θ | sayı | ° | 0 | 0°; 90°; 180°; 270° |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar / Ayrıntılar | Sınıf | seçim |  | 3000# | 3000#; 6000# |  | 17-geometri-34-manson-form.png |
| 3.4 Manşonlar / Manşon listesi (düzenle) | Host / z / θ (seçili manşon) | sayı | mm/° |  |  | Boyut değişimi için silip yeniden ekleyin. | 17-geometri-34-manson-form.png |
| 3.5 Mesnetler / Öneri | Öneri düğmeleri | seçim |  |  | Etek ekle; 3 ayak; 4 ayak (dikey); 2 eyer öner; Kabı dikey yap (yatay) | Yatay: %20 ve %80 noktalarına 2 eyer (Zick). Dikey: etek ya da 3/4 ayak. | 18-geometri-35-mesnet-ayak.png |
| 3.5 Mesnetler / Öneri | Başka destek ekle | seçim |  | Etek (dikey) / Eyer (yatay) | Eyer (saddle); Etek (skirt); Ayak (leg) | Dikeyde eyer, yatayda etek/ayak olağan değil uyarısı. | 18-geometri-35-mesnet-ayak.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler | Kesit tipi | seçim |  | Boru | U profil (UPN); Boru; Kutu profil; Köşebent (L) |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler (U profil) | Hazır UPN seç (EN 10279) (?) | seçim |  | — elle gir — | — elle gir —; <UPN katalog satırları> |  |  |
| 3.5 Mesnetler / Ayak / Ana ölçüler (U profil) | U yönü (?) | seçim |  | Sırtı pede | Sırtı pede; Kanatlar pede |  |  |
| 3.5 Mesnetler / Ayak / Ana ölçüler (Boru) | Boru dış çapı | sayı | mm | 114,3 |  | min 1 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler (Boru) | Et kalınlığı | sayı | mm | 6 |  | izinli 1–Ø/2 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler (Kutu, Köşebent) | Profil yüksekliği h (?) | sayı | mm | 100 |  |  |  |
| 3.5 Mesnetler / Ayak / Ana ölçüler (Kutu, Köşebent) | Kanat genişliği b (?) | sayı | mm | h |  |  |  |
| 3.5 Mesnetler / Ayak / Ana ölçüler | Ayak sayısı | sayı | adet | 4 |  | izinli 3–8 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler | Profil boyu | sayı | mm | 500 (ekleme varsayılanı) |  | izinli 50–20000; dikeyde 'Ayak üst ucundan taban sacına' | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ana ölçüler | Üst ucu kotu (alt teğetten) [dikey] / Konum (sol teğetten) [yatay] | sayı | mm |  |  |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayrıntılar | Host bileşen | seçim |  | gövde | — seç —; <host'lar> |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayrıntılar (U profil) | Profil yüksekliği h + Kanat genişliği b (iki alan) (?) | sayı | mm |  |  |  |  |
| 3.5 Mesnetler / Ayak / Ayrıntılar (Köşebent) | Et kalınlığı (?) | sayı | mm |  |  |  |  |
| 3.5 Mesnetler / Ayak / Ayrıntılar (U profil, Kutu) | Gövde kalınlığı tw (?) | sayı | mm |  |  | U profilde izinli 0,1–h/2 |  |
| 3.5 Mesnetler / Ayak / Ayrıntılar (U profil, Kutu) | Kanat kalınlığı tf (?) | sayı | mm |  |  | U profilde izinli 0,1–b |  |
| 3.5 Mesnetler / Ayak / Ayrıntılar | İlk ayak açısı | sayı | ° | 0 |  | izinli −360–360 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayrıntılar | Yerleşim yarıçapı | sayı | mm | 0 (otomatik) |  | 0 = otomatik (dış yarıçap + ped kalınlığı + kanat genişliği/2) | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayak pedi | Ped boyu | sayı | mm | 2,5·h |  | varsayılan 2.5·h | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayak pedi | Ped eni | sayı | mm | 2·b |  | varsayılan 2·b | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayak pedi | Ped kalınlığı | sayı | mm | 10 |  |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Ayak pedi | Üst taşma | sayı | mm | 50 |  | Pedin ayak üst ucunun üstüne çıkan kısmı. | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Taban sacı | Sac boyu | sayı | mm | 2·h+40 |  | varsayılan 2·h + 40 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Taban sacı | Sac eni | sayı | mm | 2·b+40 |  | varsayılan 2·b + 40 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Taban sacı | Sac kalınlığı | sayı | mm | 16 |  |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Taban sacı | Ankraj adedi | sayı | adet | 4 |  | min 1 | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Ayak / Taban sacı | Ankraj çapı | sayı | mm | 20 |  |  | 19-geometri-35-mesnet-ayak-form.png |
| 3.5 Mesnetler / Eyer-Etek / Ana ölçüler | Host bileşen | seçim |  | gövde | <eyer: yalnız gövdeler> |  | 50-yatay-geometri-35-mesnet-eyer.png; 60-etek-geometri-35-mesnet.png |
| 3.5 Mesnetler / Eyer / Ana ölçüler | Konum (sol teğetten) | sayı | mm | %20 × teğet aralığı |  | izinli: host aralığı içinde | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer-Etek / Ana ölçüler | Yükseklik | sayı | mm | 500 (eyer) / 1500 (etek) |  | izinli 50–3000 (eyer), 50–20000 (etek). Etekte konum girdisi kullanılmaz. | 51-yatay-geometri-35-eyer-form.png; 61-etek-geometri-35-form.png |
| 3.5 Mesnetler / Eyer / Ana ölçüler | Genişlik | sayı | mm | 200 |  | izinli 50–2000 | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Ayrıntılar | Temas (sarma) açısı | sayı | ° | 120 |  | izinli 120–180 | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Aşınma plakası kalınlığı | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Web kalınlığı | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Kanat adedi | sayı | adet | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Kanat kalınlığı | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Taban plakası boyu | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Taban plakası eni | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Eyer / Eyer plakaları (BOM kütlesi) | Taban plakası kalınlığı | sayı | mm | (boş) |  | Boş alan = ölçü girilmedi; BOM o parçayı 'EKSİK' işaretler. | 51-yatay-geometri-35-eyer-form.png |
| 3.5 Mesnetler / Mesnet listesi | Satır silme (✕) | seçim |  |  |  |  | 18-geometri-35-mesnet-ayak.png |
| Hesap girdileri sekmesi / Nozul dış yükleri (WRC 537/297) | Nozul | seçim |  | ilk nozul | <nozul etiketleri> |  | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Yöntem | seçim |  | WRC 537 (gövde tarafı) | WRC 537 (gövde tarafı); WRC 297 (gövde + nozul) | ?: WRC 297 bu sürümde her zaman 'kod verisi bekliyor' döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Eşdeğer gerilme | seçim |  | Tresca (WRC 107) | Tresca (WRC 107); von Mises |  | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Fr (radyal) | sayı | N | 0 |  | ?: Radyal kuvvet; + = dışa çekme. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Vc (çevresel kesme) | sayı | N | 0 |  | ?: Çevre yönünde kesme kuvveti. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | VL (boyuna kesme) | sayı | N | 0 |  | ?: Kap ekseni yönünde kesme kuvveti. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Mc (çevresel moment) | sayı | N·mm | 0 |  | ?: Çevre doğrultusunda eğen moment. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | ML (boyuna moment) | sayı | N·mm | 0 |  | ?: Kap ekseni doğrultusunda eğen moment. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Mt (burulma) | sayı | N·mm | 0 |  | ?: Nozul ekseni etrafında burulma momenti. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Kn (membran yığılma) | sayı |  | 1 |  | ≥1 olmalı (aksi 1) | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Kb (eğilme yığılma) | sayı |  | 1 |  | ≥1 olmalı (aksi 1) | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — A/B · Nphi  [P.Nphi.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — A/B · Nx  [P.Nx.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — A/B · Mphi  [P.Mphi.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — A/B · Mx  [P.Mx.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — C/D · Nphi  [P.Nphi.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — C/D · Nx  [P.Nx.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — C/D · Mphi  [P.Mphi.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | P (radyal) — C/D · Mx  [P.Mx.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | Mc — C/D · Nphi  [MC.Nphi.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | Mc — C/D · Nx  [MC.Nx.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | Mc — C/D · Mphi  [MC.Mphi.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | Mc — C/D · Mx  [MC.Mx.CD] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | ML — A/B · Nphi  [ML.Nphi.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | ML — A/B · Nx  [ML.Nx.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | ML — A/B · Mphi  [ML.Mphi.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri / WRC 537 eğri tablosu (yalnız WRC537 ve yük takımı varken) | ML — A/B · Mx  [ML.Mx.AB] | sayı |  | (boş) |  | Lisanslı bültenden okunur; boş değer sıfır sayılmaz, hesap BLOCKED CODE DATA döner. | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul dış yükleri | Bu nozulun yük takımını sil (düğme) | seçim |  |  |  |  | 26-girdiler-nozul-dis-yukleri.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Etiket (Tag) | metin |  | N1 |  | Nozulun imalat, hesap ve rapor üzerindeki benzersiz etiketi. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Nozul Tipi | seçim |  | Flanşlı |  | Flanşlı, Slip-on flanş, Soket kaynaklı, Manşon, Adam deliği, Pedli takviyeli. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Host Bileşen | seçim |  | SHELL-01 |  | Bağlı olduğu gövde/bombe. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Eksenel Konum (z) [gövde host] / Yerleşim Çapı [bombe host] | sayı | mm | 800 / 0 |  | z: sol teğet çizgisinden uzaklık. Yerleşim çapı: 0 = tam tepe. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Çevresel Açı (θ) | sayı | ° | 90 |  | 0° = tam üst, 90° = yan. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Eğim Açısı (α) | sayı | ° | 0 |  | Gövdede 0° = radyal, 90° = teğetsel; bombede yüzey normaline göre. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Anma Çapı (katalog) | seçim |  | (katalog eşleşmesi) / Özel ölçü (elle) |  | Katalogdan seçilince OD/ID/et dolar; elle değiştirirsen 'Özel ölçü'ye döner. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Et Serisi | seçim |  | (eşleşen seri) |  | Yalnız katalogdan anma çapı seçiliyken etkili. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Nozul Malzemesi | seçim |  | MAT-01 |  |  | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Dış Çap | sayı | mm | 168,3 |  | Nozul borusunun dış çapı. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | İç Çap | sayı | mm | 154,1 |  | Açıklık takviye hesabında kullanılır. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Boyun Kalınlığı | sayı | mm | 7,1 |  | Takviye alanına katkı sağlar. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | İç Çıkıntı | sayı | mm | 0 |  | Kabın içine doğru uzanma. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Dış Çıkıntı | sayı | mm | 150 |  | Kabın dışına doğru uzanma. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Takviye Pedi Dış Çapı | sayı | mm | 300 |  | 0 = ped yok. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Pedi Kalınlığı | sayı | mm | 10 |  | Takviye pedi sac kalınlığı. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) | Açıklık Kaynak Verimi E1 | sayı |  | 0 (boş → E1=1 varsayılır, uyarı) |  | UG-37(a): Kategori B dışı dikişten geçiyorsa o dikişin verimi (0,05–1). | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) / Küçük açıklık muafiyeti (UG-36(c)(3)) — kullanıcı beyanı | Kap hızlı basınç dalgalanmasına maruz değil | onay |  | işaretsiz |  | Bu beyanlar kullanıcının sorumluluğundadır; üçü de işaretlenmeden muafiyet uygulanmaz; muafiyet uygulansa bile boyun et kalınlığı kontrolü yapılır. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) / Küçük açıklık muafiyeti (UG-36(c)(3)) — kullanıcı beyanı | Komşu açıklık aralığı koşulları sağlanıyor | onay |  | işaretsiz |  | Bu beyanlar kullanıcının sorumluluğundadır; üçü de işaretlenmeden muafiyet uygulanmaz; muafiyet uygulansa bile boyun et kalınlığı kontrolü yapılır. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Nozul ayrıntıları (seçili nozul) / Küçük açıklık muafiyeti (UG-36(c)(3)) — kullanıcı beyanı | Bağlantı kaynaklı (dişli/saplamalı/genişletmeli tip değil) | onay |  | işaretsiz |  | Bu beyanlar kullanıcının sorumluluğundadır; üçü de işaretlenmeden muafiyet uygulanmaz; muafiyet uygulansa bile boyun et kalınlığı kontrolü yapılır. | 27-girdiler-nozul-ayrintilari.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | ＋ Flanş Ekle / flanş kartı / ✕ sil | seçim |  | 0 adet |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Flanş Kimliği | metin |  | FL-1 |  | Benzersiz etiket. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Flanş Tipi | seçim |  | Integral | Integral; Gevşek (loose) | Gevşek (loose) bu formüllerle hesaplanmaz. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Flanş Malzemesi | seçim |  | MAT-01 |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | İç Çap (B) | sayı | mm | 500 |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Dış Çap (A) | sayı | mm | 700 |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Flanş Kalınlığı (t) | sayı | mm | 50 |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Hub Kalınlığı, küçük uç (g0) | sayı | mm | 20 |  | h0 = √(B·g0) için. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Hub Kalınlığı, büyük uç (g1) | sayı | mm | 0 (girilmedi) |  | 0 = girilmedi (flanş hesabı bloke) | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Hub Uzunluğu (h) | sayı | mm | 50 |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Conta m Faktörü | sayı |  | 0 (girilmedi) |  | Lisanslı çizelgeden okunur. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Conta y Değeri | sayı | MPa | 0 (girilmedi) |  | Min. oturma gerilmesi. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Cıvata Sayısı | sayı | adet | 0 (girilmedi) |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Cıvata Alanı | sayı | mm² | 0 (girilmedi) |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Cıvata İzin Gerilmesi | sayı | MPa | 0 (girilmedi) |  |  | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Y Faktörü | sayı |  | 0 (girilmedi) |  | Appendix 2 çizelgesi; program içermez (K6). | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | f Faktörü (hub düzeltme) | sayı |  | 0 (girilmedi) |  | K6 | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | F Faktörü | sayı |  | 0 (girilmedi) |  | Şekil 2-7.1 | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | V Faktörü | sayı |  | 0 (girilmedi) |  | Şekil 2-7.1 | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | T Faktörü | sayı |  | 0 (girilmedi) |  | Şekil 2-7.1 | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | U Faktörü | sayı |  | 0 (girilmedi) |  | Şekil 2-7.1 | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Cıvata Tasarım Yükü W | sayı | N | 0 (girilmedi) |  | Appendix 2 çalışma sayfanızdan girilir. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Flanşlar (Appendix 2) | Flanş Momenti M | sayı | N·mm | 0 (girilmedi) |  | Appendix 2 çalışma sayfanızdan girilir. | 28-girdiler-flanslar-appendix2.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Destek Tipi | seçim |  |  |  | Eyer (saddle) / Etek (skirt) / Ayak (leg) | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Bağlandığı Bileşen | seçim |  |  |  | Eyer yalnız gövdeye oturur. | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Destek Malzemesi | seçim |  | MAT-01 |  |  | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Konum | sayı | mm |  |  | Kap ekseni boyunca; etek/ayak için taban kotu. | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Genişlik | sayı | mm | 200 |  | Eyerde temas genişliği. | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) | Yükseklik | sayı | mm | 500/1500 |  |  | 29-girdiler-destek-ayak.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Etek) | Etek Ortalama Çapı | sayı | mm | 0 (boş) |  | D_ort = D_dış − t; hesap için zorunlu. | 62-etek-girdiler-destek.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Etek) | Etek İzin Verilen Basma B (UG-23(b)) | sayı | MPa | 0 (girilmedi) |  | Girilmezse etek burkulma kontrolü BLOKLU. | 62-etek-girdiler-destek.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Etek) | Etek Kaynak Verimi E | sayı |  | 0 (0,6 varsayılır) |  | 0–1. | 62-etek-girdiler-destek.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Etek) | Etek Et Kalınlığı | sayı | mm | 0 (boş) |  | Hesap için zorunlu. | 62-etek-girdiler-destek.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Sarma Açısı | sayı | ° | 120 | k; o; d;  ; a; s; g; a; r; i;  ; 1; 2; 0; °; ;;  ; t; e; k;  ; e; y; e; r; d; e;  ; u; y; a; r; ı | 52-yatay-girdiler-eyer-zick.png |  |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Eyer Düzleminde Halka | seçim |  | Seçin (girilmedi) | Seçin (girilmedi); Halka yok; Halka var | Seçilmezse Zick hesabı BLOKE. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Zick K1 | sayı |  | 0 (girilmedi) |  | Eyer kesiti boyuna eğilme sabiti; halkalı/A≤R/2 ise π. Tablodan (Zick 1951/Moss) okunur; 0 = girilmedi → BLOCKED_CODE_DATA. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Zick K2 | sayı |  | 0 (girilmedi) |  | Kabuk teğetsel kesme sabiti. Tablodan (Zick 1951/Moss) okunur; 0 = girilmedi → BLOCKED_CODE_DATA. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Zick K3 (başlık kesmesi) | sayı |  | 0 (girilmedi) |  | Yalnız A ≤ R/2 halkasız. Tablodan (Zick 1951/Moss) okunur; 0 = girilmedi → BLOCKED_CODE_DATA. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Zick K6 | sayı |  | 0 (girilmedi) |  | Eyer boynuzu çevresel eğilme sabiti; halkalıda kullanılmaz. Tablodan (Zick 1951/Moss) okunur; 0 = girilmedi → BLOCKED_CODE_DATA. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (yalnız Eyer) | Zick K7 | sayı |  | 0 (girilmedi) |  | Eyer altı çevresel basma; her durumda gerekir. Tablodan (Zick 1951/Moss) okunur; 0 = girilmedi → BLOCKED_CODE_DATA. | 52-yatay-girdiler-eyer-zick.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Etek, Ayak) | Devirme Momenti | sayı | N·mm | 0 | 0;  ; =;  ; m; o; m; e; n; t;  ; y; o; k;  ; (; v; a; r; s; a; y; ı; m;  ; s; o; n; u; c; a;  ; y; a; z; ı; l; ı; r; ); ;;  ; y; ü; k;  ; d; u; r; u; m; l; a; r; ı; n; d; a; n;  ; t; ü; r; e; t; i; l; e; n; l; e;  ; b; ü; y; ü; k;  ; o; l; a; n;  ; a; l; ı; n; ı; r; . | 62-etek-girdiler-destek.png |  |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Bağlantı Yeri | seçim |  | Seçin (girilmedi) | Seçin (girilmedi); Gövde (shell); Alt bombe (bottom head) | Lokal gerilme (WRC) kontrolünün hangi cidara uygulanacağını belirler. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Kesit Tipi | seçim |  | Boru (eski davranış) | Boru (eski davranış); Boru (pipe); U profil (channel); Kutu profil (box); Köşebent (angle) | Boş = boru. Profil katalog değerleri programda yoktur (K6). | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Sayısı | sayı | adet |  |  | Taşıyıcı ayak adedi. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Dağılım Yarıçapı | sayı | mm |  |  | Moment hesabı için zorunlu. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Çapı (yalnız boru) | sayı | mm |  |  | Hesap için zorunlu. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Ayak Et Kalınlığı (yalnız boru) | sayı | mm |  |  | Hesap için zorunlu. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Profil Yüksekliği (profilde) | sayı | mm |  |  |  | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Profil Genişliği (profilde) | sayı | mm |  |  |  | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Gövde (Web) Kalınlığı (profilde) | sayı | mm |  |  |  | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Flanş Kalınlığı (yalnız U profil) | sayı | mm |  |  |  | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Bağlanmamış (Burkulma) Boyu | sayı | mm |  |  | Yanal desteksiz boy. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Eksantriklik e | sayı | mm |  |  | Ek eğilme momenti üretir. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Bağlantı ve Kesit | Etkin Boy Faktörü K | sayı |  | boş → 2,1 |  | Boşsa 2,1 (ankastre-serbest, konservatif) varsayılır. | 30-girdiler-ayak-baglanti-kesit.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Takviye Pedi | Bağlantı Pedi Boyu | sayı | mm |  |  |  | 31-girdiler-ayak-takviye-pedi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Takviye Pedi | Bağlantı Pedi Eni | sayı | mm |  |  |  | 31-girdiler-ayak-takviye-pedi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Takviye Pedi | Bağlantı Pedi Kalınlığı | sayı | mm |  |  |  | 31-girdiler-ayak-takviye-pedi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Takviye Pedi | Ped Temas Oranı | sayı |  | boş → 1,0 |  | Profilin pede kaynaklanabilen oranı (0–1). | 31-girdiler-ayak-takviye-pedi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Taban Plakası Boyu | sayı | mm |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Taban Plakası Eni | sayı | mm |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Taban Plakası Kalınlığı | sayı | mm |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Taban Plakası Akma Dayanımı | sayı | MPa |  |  | Fy | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Temel İzin Verilen Yataklık Basıncı | sayı | MPa |  |  | Boşsa yataklık kontrol edilmez. | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Taban Plakası Alanı | sayı | mm² |  |  | Yalnız yataklık raporu için. | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Ankraj Cıvatası Adedi | sayı | adet |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Ankraj Cıvatası Nominal Çapı | sayı | mm |  |  | Bilgi/rapor için; çap tek başına kapasite üretmez. | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Ankraj İzinli Çekme | sayı | N |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Ankraj İzinli Kesme | sayı | N |  |  |  | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Taban Plakası | Yatay Taban Yükü | sayı | N | 0 |  | Ankraj kesme kontrolüne aktarılan yatay kuvvet. | 32-girdiler-ayak-taban-plakasi.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Kaynaklar | Ped–Gövde Kaynak Bacağı | sayı | mm |  |  |  | 33-girdiler-ayak-kaynaklar.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Kaynaklar | Ayak–Ped Kaynak Bacağı | sayı | mm |  |  |  | 33-girdiler-ayak-kaynaklar.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Kaynaklar | Ayak–Taban Plakası Kaynak Bacağı | sayı | mm |  |  |  | 33-girdiler-ayak-kaynaklar.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Kaynaklar | Elektrot Dayanımı Fexx | sayı | MPa |  |  | ör. 480 | 33-girdiler-ayak-kaynaklar.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / Kaynaklar | Asgari Köşe Kaynak Bacağı | sayı | mm |  |  | AWS D1.1 tablosu programda yok; kendi tablonuzdan girin. | 33-girdiler-ayak-kaynaklar.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları | ML Eğrisi β | sayı |  |  |  | ML≠0 iken boşsa WRC hesabı bloklanır. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları | MC Eğrisi β | sayı |  |  |  | MC≠0 iken boşsa bloklanır. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · P (radyal) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · P (radyal) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · P (radyal) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · P (radyal) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · ML (boyuna moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · ML (boyuna moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · ML (boyuna moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · ML (boyuna moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · MC (çevresel moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · MC (çevresel moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · MC (çevresel moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · MC (çevresel moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VL (boyuna kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VL (boyuna kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VL (boyuna kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VL (boyuna kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VC (çevresel kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VC (çevresel kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VC (çevresel kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta A · VC (çevresel kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · P (radyal) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · P (radyal) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · P (radyal) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · P (radyal) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · ML (boyuna moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · ML (boyuna moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · ML (boyuna moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · ML (boyuna moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · MC (çevresel moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · MC (çevresel moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · MC (çevresel moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · MC (çevresel moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VL (boyuna kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VL (boyuna kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VL (boyuna kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VL (boyuna kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VC (çevresel kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VC (çevresel kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VC (çevresel kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta B · VC (çevresel kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · P (radyal) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · P (radyal) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · P (radyal) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · P (radyal) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · ML (boyuna moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · ML (boyuna moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · ML (boyuna moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · ML (boyuna moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · MC (çevresel moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · MC (çevresel moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · MC (çevresel moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · MC (çevresel moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VL (boyuna kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VL (boyuna kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VL (boyuna kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VL (boyuna kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VC (çevresel kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VC (çevresel kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VC (çevresel kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta C · VC (çevresel kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · P (radyal) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · P (radyal) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · P (radyal) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · P (radyal) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · ML (boyuna moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · ML (boyuna moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · ML (boyuna moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · ML (boyuna moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · MC (çevresel moment) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · MC (çevresel moment) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · MC (çevresel moment) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · MC (çevresel moment) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VL (boyuna kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VL (boyuna kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VL (boyuna kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VL (boyuna kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VC (çevresel kesme) · Nx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VC (çevresel kesme) · Ny | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VC (çevresel kesme) · Mx | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Destek ayrıntıları (seçili destek) (Ayak) / WRC Katsayıları tablosu | Nokta D · VC (çevresel kesme) · My | sayı |  | (boş) |  | Boş = okunmadı; 0 = gerçek sıfır. Aktif yükte dört bileşen de zorunlu. | 34-girdiler-ayak-wrc.png |
| Hesap girdileri sekmesi / Malzeme | Malzeme listesi: seçim kartı / + Malzeme Ekle / ✕ sil | seçim |  | MAT-01 |  |  | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Malzeme Tanımı | metin |  | SA-516 Gr.70 |  | Sertifikadaki tam tanım. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | İzin Verilen Gerilme (S) | sayı | MPa | 138 |  | Tasarım sıcaklığındaki S; et kalınlığını belirler. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | S Değerinin Sıcaklığı | sayı | °C | 150 |  | Tasarım sıcaklığıyla aynı olmalı. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Kalınlık Aralığı — En Az | sayı | mm | 0 |  |  | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Kalınlık Aralığı — En Çok | sayı | mm | 1000 |  | 0 girilirse 999. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Test Sıcaklığında S | sayı | MPa | 0 (girilmedi) |  | UG-99(b) LSR için. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Akma Dayanımı | sayı | MPa | 260 |  |  | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Çekme Dayanımı | sayı | MPa | 485 |  |  | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Yoğunluk | sayı | kg/m³ | 7850 |  | Ağırlık hesabı. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Elastisite Modülü E | sayı | MPa | 0 (girilmedi) |  | FEA için; 0 = 200 GPa varsayılır. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | Poisson Oranı ν | sayı |  | 0 (girilmedi) |  | 0<ν<0,5; boşsa 0,3. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Malzeme | UCS-66 Eğri Grubu | seçim |  | — girilmedi — | — girilmedi —; A; B; C; D | Girilmezse MDMT kontrolü yapılmaz. | 35-girdiler-malzeme.png |
| Hesap girdileri sekmesi / Kaynak & NDT | Kaynak listesi: seçim kartı / + Kaynak Ekle / ✕ sil | seçim |  | WJ-01 |  |  | 36-girdiler-kaynak-ndt.png |
| Hesap girdileri sekmesi / Kaynak & NDT | Kaynak Verimi (E) | sayı |  | 1,0 | 0; ,; 7; 0; –; 1; ,; 0; 0; ;;  ; N; D; T;  ; k; a; p; s; a; m; ı; n; a;  ; b; a; ğ; l; ı; . | 36-girdiler-kaynak-ndt.png |  |
| Hesap girdileri sekmesi / Kaynak & NDT | NDE Yöntemi | metin |  | RT-1 | ö; r; .;  ; R; T; ,;  ; U; T; ,;  ; P; T | 36-girdiler-kaynak-ndt.png |  |
| Hesap girdileri sekmesi / Kaynak & NDT | NDE Kapsamı | metin |  | 100% | ö; r; .;  ; 1; 0; 0; %;  ; v; e; y; a;  ; s; p; o; t | 36-girdiler-kaynak-ndt.png |  |
| Hesap girdileri sekmesi / Kaynak & NDT | Seçili gövde (…) kaynak birleşimi | seçim |  | WJ-01 | — yok —; <kaynaklar> |  | 36-girdiler-kaynak-ndt.png |
| Hesap girdileri sekmesi / BOM maliyet girdileri | <Malzeme tanımı> (<ID>) birim fiyatı (malzeme başına bir alan) | sayı | €/kg | (boş) | B; i; r; i; m;  ; f; i; y; a; t;  ; v; a; r; s; a; y; ı; l; a; n; ı;  ; y; o; k; t; u; r; ;;  ; b; o; ş; s; a;  ; m; a; l; i; y; e; t;  ; h; e; s; a; p; l; a; n; m; a; z; . | 37-girdiler-bom-maliyet.png |  |
| Hesap girdileri sekmesi / BOM maliyet girdileri | Kaynak / işçilik süresi | sayı | saat | (boş) |  |  | 37-girdiler-bom-maliyet.png |
| Hesap girdileri sekmesi / BOM maliyet girdileri | Saat ücreti | sayı | €/saat | (boş) |  |  | 37-girdiler-bom-maliyet.png |
| Hesap girdileri sekmesi / BOM maliyet girdileri | NDT toplam bedeli | sayı | € | (boş) |  |  | 37-girdiler-bom-maliyet.png |
| Hesap girdileri sekmesi / BOM maliyet girdileri | Boya / kaplama toplam bedeli | sayı | € | (boş) |  |  | 37-girdiler-bom-maliyet.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Kaldırma kulağı ekle / Kulakları kaldır (düğmeler) | seçim |  | tanımsız |  | Kulak yoksa kontrol yapılmaz. | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Kulak sayısı | sayı | adet | 2 |  | 1–4; 3+ kulakta yalnız 2 kulak yük taşır varsayımı. | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Konum | seçim |  | Gövde üstü | Gövde üstü; Bombe |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Plaka kalınlığı t | sayı | mm | 20 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Plaka genişliği b | sayı | mm | 150 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Delik çapı | sayı | mm | 50 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Delik merkezi-kenar mesafesi e | sayı | mm | 75 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Delik yüksekliği h (kabuktan) | sayı | mm | 100 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Taban genişliği | sayı | mm | 150 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Kaynak boyu (toplam) | sayı | mm | 400 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Kaynak ayak ölçüsü | sayı | mm | 10 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Sapan açısı (düşeyden) | sayı | ° | 0 |  | 0–89 | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Darbe katsayısı | sayı |  | 1,5 |  | Tipik 1,5–2,0; min 1 | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Plaka akma dayanımı Fy | sayı | MPa | 250 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Kaldırma kulağı | Ek kaldırılan kütle | sayı | kg | 0 |  |  | 38-girdiler-kaldirma-kulagi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası | <Junction> Δ (Table 1-5.2) (koni birleşimi başına) (?) | sayı | ° | 0 | B; o; ş; /; 0;  ; →;  ; Δ; =; 0;  ; (; g; ü; v; e; n; l; i;  ; t; a; r; a; f; ); . |  | 39-girdiler-koni-birlesimi-ayak-kabi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası | <Junction> ek halka alanı (koni birleşimi başına) (?) | sayı | mm² | 0 |  |  | 39-girdiler-koni-birlesimi-ayak-kabi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Halka dış çapı | sayı | mm | 0 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Halka iç çapı | sayı | mm | 0 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Halka kalınlığı | sayı | mm | 0 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Halka Fy | sayı | MPa | 250 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Cıvata dairesi çapı | sayı | mm | 0 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Cıvata adedi | sayı | adet | 8 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Cıvata çapı | sayı | mm | 24 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Cıvata izin çekme | sayı | MPa | 0 |  | Zorunlu (K6): yoksa hesap BLOCKED. | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Cıvata izin kesme | sayı | MPa | 0 |  | Yatay yük varsa zorunlu. | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Beton f'c | sayı | MPa | 25 |  |  | 63-etek-girdiler-taban-halkasi.png |
| Hesap girdileri sekmesi / Koni birleşimi (App. 1-5) ve etek taban halkası (yalnız Etek desteği varsa) | Beton izin yataklık (opsiyonel) | sayı | MPa | 0 |  | Boşsa 0,85·f'c/2,31 varsayılır. | 63-etek-girdiler-taban-halkasi.png |

## Adım 4 — Hesap Sonuçları

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| Hesap | Hesapla / ↻ Yeniden Hesapla (düğme) | seçim |  |  |  | Girdi alanı yok; sonuç satırına tıklayınca ara değerler, uyarılar, varsayımlar açılır. | 40-sonuc-ozet.png; 40b-sonuc-kpi-ve-tablolar.png; 41-sonuc-tam.png; 42-sonuc-satir-acik.png |

## Adım 5 — 3D Model

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| 3D model | 3D Modeli Oluştur / ↻ Yenile / ⬇ STEP (düğmeler) | seçim |  |  |  |  | 43-3d-model.png |
| 3D model | ⧗ Kesit Görünümü ↔ ▣ Tam Görünüm | seçim |  | Tam Görünüm |  |  | 44-3d-model-kesit.png |
| 3D model | ⏸ Döndürmeyi Durdur ↔ ↻ Otomatik Döndür | seçim |  | Otomatik döndürme açık |  |  | 43-3d-model.png |
| 3D model | Kamera çubuğu (İzo / Üst / Ön / Yan / Sığdır) | seçim |  | İzo | İzo; Üst; Ön; Yan; Sığdır |  | 43-3d-model.png |

## Adım 6 — Rapor & Çıktı

| Alt adım | Etiket | Tip | Birim | Varsayılan | Seçenekler | İpucu | Görsel |
|---|---|---|---|---|---|---|---|
| Rapor | Raporu Üret (düğme) | seçim |  |  |  |  | 45-rapor-sayfa.png |
| Rapor / Açınım şablonları | Kaynak ağzı payı (mm) | sayı | mm | 0 | m; i; n;  ; 0 | 49-rapor-sayfa-tam-acinim.png |  |
| Rapor / Açınım şablonları | Bombe petal sayısı | sayı | adet | 8 | m; i; n;  ; 3 | 49-rapor-sayfa-tam-acinim.png |  |
| Rapor | Yeni Sekmede / PDF indir / STEP indir / DXF indir (düğmeler) | seçim |  |  |  | PDF indir tarayıcı yazdırma penceresini açar. | 45-rapor-sayfa.png; 46-rapor-html-1.png |
