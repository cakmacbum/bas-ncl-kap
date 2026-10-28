# MyTank Configurator — davranış spesifikasyonu (REA, clean-room)

- **Hedef:** Ziemann Holvrieka "MyTank Configurator" — `https://tank-config.ziemann-holvrieka.com/`
- **Tarih:** 2026-10-28 · **Paket:** D01
- **Amaç:** Basınçlı kap tasarım sihirbazımız (gövde zinciri → bombeler → flanşlı nozullar → manşonlar → ayaklar) için UX / veri akışı dersleri.
- **Yöntem:** Yerleşik tarayıcıda yalnız okuma/inceleme amaçlı sayfa içi JS (DOM, performance, sahte girdi olayları), statik bundle'da dize taraması, REA `capture_browser_scenario`.
- **Sınırlar:** Çerez bandında yalnız "Technically necessary" (Decline). Hesap açılmadı, form/teklif gönderilmedi, e-posta doğrulama ve 3D/PDF indirme tetiklenmedi, `/api/save` çağrılmadı. Hedef kodu kopyalanmadı; alan adları yalnız veri modelinin şeklini göstermek için verildi.

Etiketler: **[G]** gözlem (çalışma zamanında görüldü) · **[S]** statik bundle dizesinden çıkarım · **[Ç]** çıkarım · **[?]** bilinmeyen.

---

## 0. Teknik kimlik

| Konu | Bulgu | Tür |
|---|---|---|
| Uygulama | React SPA (`#root`), Vite yapısı: tek `index-<hash>.js` (~1,66 MB) + tek CSS | [G] |
| 3D | three.js **r170** (`window.__THREE__ = "170"`), WebGL canvas; bundle'da OrbitControls/drei izi ve CSG izi var | [G] / [S] |
| 2D | Ayrı `<canvas class="tank-canvas">` + filigran canvas'ı — ölçülendirilmiş teknik resim istemcide çiziliyor | [G] |
| Form/doğrulama | `<form>` yok; kontrollü input'lar; bundle'da `yup` izi | [G] / [S] |
| Çıktılar | jsPDF + html2canvas (PDF veri sayfası), 3D dosya uzantıları `.step` / `.stl` / `.obj`; QR kod harici servisten | [S] |
| Çeviri | EN / DE / ES düğmeleri; sayı biçimi Almanca binlik ayırıcı (`4.200 mm`, `24,4 %`) | [G] |

## 1. Adım sırası ve gezinme

**Sihirbaz değil — tek sayfa, akordeon form + kalıcı önizleme paneli.** [G]

Sol sütunda sabit sıralı bölümler (`[+]/[-]` ile açılır/kapanır, birbirinden bağımsız; aynı anda birden çok bölüm açık olabilir):

1. Standard Configurations — proje adı, **Template** (cct / bbt / water_storage_tank / juice_tank), Location (indoor/outdoor)
2. Basic Geometry — Diameter, Cylindrical Length, *Total Length (hesaplanan, salt-okunur)*, *Volume total (hesaplanan)*, Volume net, *Head space % (hesaplanan, disabled)* + formülü metin olarak, Orientation (vertical/horizontal), Maximum Construction Height
3. Upper Bottom — tip (dished / flat / cone / torispherical), koşullu Cone Angle, Board (düz kenar)
4. Lower Bottom — aynı yapı, koni varsayılan
5. Supports — Ceiling Penetration (checkbox), Type (pipe_feet / long_skirt / short_skirt / saddle / none), Free Space to Floor
6. Heating and Cooling — Execution (none / dimple_plates / coiled_half_tubes / other) → koşullu: soğutma/ısıtma checkbox'ları + "zones in shell" sayısı
7. Insulation — none / 50 / 100 / 150 mm
8. Internal Surface Finish — üst bombe / alt bombe / gövde ayrı ayrı (2B / electro_polished / others)
9. Material — 1.4301 / 1.4307 / 1.4404 / 1.4462 / others → koşullu serbest metin
10. Operational Conditions — basınç nominal/maks (bar g), sıcaklık min/maks, medya, yoğunluk, vakum dayanımı, yorum
11. Inquiry Data — kişisel/şirket verisi, onay kutuları, Save & Share, PDF, Send Inquiry

- Adımlar arası "ileri/geri" yok; geri dönüş = ilgili bölümü açıp alanı düzenlemek. Her değişiklik anında önizlemeye yansır. [G]
- **Template seçimi bir "yama"dır:** yalnız ilgili alanları üzerine yazar (ör. bbt → silindir 15000, alt dished; water_storage → D 6000, üst cone 15°, alt flat, ayak none), kullanıcının girdiği net hacim / maks. yükseklik gibi alanlara dokunmaz. [G]
- **Orientation = horizontal** seçilince bağımlı alanlar otomatik değişti: support → saddle, alt bombe → dished, zemin boşluğu 2000 → 1000. [G] (Kural tablosu tam görülmedi [?])
- Reset düğmesi var; sayfa yenilemede durum kaybolur — localStorage/sessionStorage boş, URL'de durum yok. [G]
- Kalıcılık yalnız sunucu üzerinden: `?id=<configId>` → `GET /api/load/{id}`; geçersiz id → **400 ve sessizce varsayılanlara düşüş**, kullanıcıya mesaj yok. [G] ("Loading configuration..." metni bundle'da [S])

## 2. Parça ekleme etkileşimi (nozul / manway / ayak)

- **Nozul, manway, manşon ekleme özelliği YOK.** Ne listede ne 3D'de konum/açı girişi var. [G] Bundle'da `nozzle|manway|flange|socket` dizeleri bulunmadı. [S]
- Bağlantılar için en yakın şey, kayıt şemasında görünen ama arayüzde render edilmeyen "ancillary location upper / lower / shell / other" alanları — yani **yalnız bölge etiketi, konum değil**. Ayrıca `agitator`, `ladderAndAccess`, `walkwayComments`, `materialThickness{Upper,Shell,Lower}`, `pressureDirective`, `code` alanları da şemada var. [S] Arayüzde neden görünmedikleri bilinmiyor [?].
- Ayaklar: tip seçimi + tek ölçü (zemine serbest mesafe). Ayak sayısı, açısal yerleşim, PCD girilemiyor; 3D'de sabit 4 boru ayak + bağlantı halkası çiziliyor. [G]
- **3D'den seçim yok:** gövdeye tıklamak hiçbir şey seçmedi. 3D yalnız görüntüleme: sürükle-döndür, tekerlek-zoom, Zoom In/Out, Rotate Left/Right, Reset View düğmeleri, "Controls" yardım balonu, "Info" (Tank Specifications) paneli, Ø çipi (`Ø 4200mm`). [G]

## 3. Parametre değişince 2D/3D güncellemesi

- **Tamamen istemci tarafı.** Çap ve silindir boyu değişince ağda hiçbir istek yok — hem sayfa içi fetch/XHR kancası hem REA senaryosu (yalnız statik varlıklar: js, css, png, font, bayrak svg) bunu doğruladı. Geometri, hacim, toplam boy tarayıcıda hesaplanıyor. [G] (Evidence `ev_d0b91f8e5e13073a84fca85749241bf4cb9ce301200349c4622e0c66e497bc30`)
- **Hesaplanan alanlar her tuş vuruşunda güncelleniyor:** input olayından ~50 ms içinde Total Length / Volume / sağ paneldeki "Technical Specifications" değişti. Senkron işleyici ~8,5 ms, iki kare ~87 ms. [G]
- **3D yeniden kurulumu pahalı:** çap değişiminden sonra 58 ms + 444 ms'lik "long task"; art arda 4 tuş vuruşu tek bir ~296 ms long task üretti → yeniden kurulum toplu/ertelenmiş olabilir. [G] / [Ç] (debounce süresi [?])
- 2D görünüm: kotlu teknik resim (çap, silindir boyu, koni yüksekliği, zemin boşluğu, toplam boy) + **"Maximum Construction Height" kırmızı kot çizgisi** + ölçek çubuğu ("500 mm", "Scale 1:…"). [G]
- 2D/3D arasında geçiş ağ isteği üretmiyor; 3D sahne ilk geçişte kuruluyor. [G]

## 4. İstek/yanıt veri modeli şekli (genelleştirilmiş)

Alan adları kayıt yükünden gruplandı; değerler gösterilmiyor.

```
Konfigurasyon (düz, tek seviyeli JSON nesnesi)
├─ meta        : projectName, template(enum), location(enum)
├─ geometry    : diameter, cylindricalLength, totalHeight*, heightH2..H4*, volumeTotal*, volumeNet,
│                orientation(enum), maxConstructionHeight
├─ heads       : upper{type(enum), coneAngle?, board}, lower{type, coneAngle?, board}
├─ supports    : ceilingPenetration(bool), type(enum), freeSpaceToFloor
├─ thermal     : execution(enum), cooling(bool), heating(bool), zonesInShell, insulation(enum)
├─ surfaces    : upper / lower / shell (enum)
├─ material    : grade(enum) | gradeOther(text), thicknessUpper/Shell/Lower
├─ operating   : pressureNominal, pressureMax, tempMin, tempMax, media, density, vacuum, comment,
│                pressureDirective(+Other), code(+Other)
├─ ancillary   : locationUpper/Lower/Shell/Other, agitator(+comments), ladderAndAccess, walkwayComments
├─ contact     : firstName, surname*, email*, telephone, companyName*, street, zipCode, city, country,
│                message, reference, inquiryComment
└─ zaman/çıktı : savedAt | submittedAt, printableTankImage (önizleme resmi, yalnız inquiry'de)
  (* hesaplanan değerler de yüke yazılıyor)
```

| Uç nokta | Yöntem | Davranış |
|---|---|---|
| `/api/load/{configId}` | GET | `?id=` varsa açılışta çağrılır; 400 → sessiz varsayılan [G] |
| `/api/save` | POST JSON | Yanıtta `configId` → paylaşım linki + QR [S] |
| `/api/send-inquiry` | POST JSON | Konfig + iletişim + önizleme resmi; hata → modal (SweetAlert tarzı) [S] |
| `/api/verify-email/{status,send-code,confirm-code}` | POST JSON | E-posta kod doğrulaması; durumlar: sending → code_sent → verifying → valid / error / rate_limited [S] |

- Birimler yüke **mm, L, bar g, °C, kg/m³** olarak sabit; birim seçimi yok. Input'larda görüntü metni birim ekli string (`"4.200 mm"`), iç değer sayı. [G] / [Ç]
- Hesaplanan değerler sunucuya da gönderiliyor (sunucunun yeniden hesaplayıp hesaplamadığı [?]).

## 5. Doğrulama ve uyarı gösterimi

- **Girdi temizleme:** yazarken sayısal olmayan karakterler atılıyor (`abc` → 0, `-500` → 500). Negatif sayı girilemiyor. [G]
- **Kıstırma (clamp) odak kaybında:** yazarken ham değer kalıyor, blur'da aralığa kıstırılıyor ve birim+binlik biçim uygulanıyor (Board 500 → 250; zemin boşluğu 50 → 100, 9000 → 6000). [G]
- **Aralık ipucu alan altında sürekli görünür:** "50 mm, Acceptable values (0 - 250 mm)." — mevcut değer + izinli aralık birlikte. [G]
- **Çapraz-alan hataları türetilmiş ve reaktif:** kırmızı zeminli kutu, ilgili alanın hemen altında, "Error: …" önekiyle. Görülenler:
  - "Volume (net) exceeds Volume (total)." (net hacim alanı altında)
  - "Total Height is higher than Maximum Construction Height." (maks. yükseklik alanı altında)
  Geometri değişince otomatik açılır/kapanır (silindir 2000 → hata gider, 20000 → geri gelir). [G]
- **Engelleyici değil:** hata varken 2D/3D çizim ve diğer alanlar çalışmaya devam ediyor; yalnız mesaj. [G]
- **Eksik doğrulamalar (ders):** çap 0 veya 100 mm kabul ediliyor, D = 0'da bile "14 L" hacim gösteriliyor; çapın üst/alt sınırı yok; 99999 mm çap kabul. [G]
- **Eylem kilidi tooltip ile:** Save/PDF/Send düğmeleri devre dışı ve gerekçesi `title` olarak: "Please accept the privacy policy to continue", "Please fill in all required fields". [G]

## 6. Bizim sihirbaz için öneriler (12)

1. **Sihirbaz + kalıcı canlı önizleme:** adımları akordeon gibi serbest gezilebilir yap (her adım her an açılabilir), ama bizdeki bağımlılık zinciri (gövde → bombe → nozul → manşon → ayak) için adım başlığında durum rozeti (tamam / uyarı / hata sayısı) göster. MyTank'te bu yok; hatalar bölüm kapalıyken görünmüyor.
2. **Hesaplanan değerleri form içinde salt-okunur alan olarak göster** (toplam boy, brüt hacim, boşluk %) ve formülü alan altında yaz — kullanıcı sonucun nereden geldiğini görür. Bizde ek olarak gerekli et kalınlığı / MAWP buraya.
3. **"Ham yaz, blur'da kıstır/biçimle" deseni** + alan altında "mevcut değer, izinli aralık" ipucu. Ancak sessiz kıstırma yerine kısa bir "250'ye ayarlandı" notu ver — mühendislik verisinde sessiz değişiklik risklidir.
4. **Çapraz-alan kuralları için türetilmiş doğrulama katmanı:** kurallar saf fonksiyon (`config → Issue[]`), her Issue `{alan yolu, seviye: hata/uyarı/bilgi, mesaj, kural kodu}`; UI yalnız render eder. MyTank'te mesajlar alan altında ama bölüm/özet düzeyinde toplanmıyor — biz bir "Sorunlar" paneli ekleyelim, tıklayınca alana gitsin.
5. **Fiziksel sınırları zorunlu kıl:** D > 0, uzunluk > 0, makul üst sınırlar, koni açısı aralığı. MyTank D = 0'ı kabul edip hacim gösteriyor; biz hesap motoruna geçersiz geometri asla gitmesin.
6. **Şablon = kısmi yama:** ön ayarlar (ör. "dikey, 2:1 elips bombe, 4 bacak", "yatay, saddle") yalnız kendi alanlarını değiştirsin; kullanıcı girdilerini korusun. Uygularken hangi alanların değiştiğini bir kerelik vurgula / geri al seçeneği sun.
7. **Bağımlı varsayılan geçişleri açık kural tablosu olarak tut** (yatay → saddle, dikey → ayak/etek). MyTank bunu sessiz yapıyor; biz "Yönelim değişti: destek tipi Saddle yapıldı" bilgisi gösterelim.
8. **Geometri ve hesap tamamen istemcide, anında** (MyTank gibi ağsız); ama 3D yeniden kurulumu (bizde nozul delikleri / CSG daha da pahalı) **debounce + Web Worker** ile ana iş parçacığından çıkar. Hedef: hesaplanan sayılar <50 ms, 3D <300 ms ve yazmayı bloklamasın.
9. **MyTank'in boşluğu bizim fırsatımız — nozul/manşon editörü:** tablo satırı (etiket, DN, PN/flanş, bölge = gövde/üst/alt bombe, eksenel konum veya açısal konum, iç çıkıntı) + 3D'de seçilen satırın vurgulanması; 3D'de tıklayınca satıra gitme (raycast seçim) ikinci aşama. Konum doğrulaması: kaynak dikişine / bombe geçişine / diğer nozula minimum mesafe → Issue.
10. **Ayaklar için sayı + açısal yerleşim + PCD** girilsin; MyTank yalnız tip ve zemin boşluğu alıyor, 3D'de sabit 4 ayak çiziyor.
11. **2D kotlu teknik resim görünümü + kısıt çizgisi:** maks. yapım yüksekliği gibi kısıtı resimde kırmızı çizgi olarak göstermek çok anlaşılır. Biz nozul kotları ve dikiş çizgilerini de 2D'de verelim; 2D/3D tek düğmeyle değişsin.
12. **Veri modeli: hiyerarşik, birimli, sürümlü JSON.** MyTank düz alan listesi kullanıyor ve hesaplananları da kaydediyor. Biz girdi ile türetilmişi ayıralım (türetilmiş her yüklemede yeniden hesaplansın), `schemaVersion` koyalım, paylaşım linki geçersiz/eski id'de **kullanıcıya hata göstersin** (MyTank 400'de sessizce varsayılana düşüyor). Hesap yapmadan kaydetme/paylaşma localStorage taslağı ile de olsun; yenilemede iş kaybolmasın.

## 7. Kanıt kapsamı ve erişilemeyenler

| Soru | Durum | Kanıt |
|---|---|---|
| Adım sırası / gezinme | Cevaplandı | DOM alan envanteri, bölüm aç/kapa, şablon/yönelim denemeleri [G] |
| Parça ekleme / 3D seçim | Cevaplandı (özellik yok) | arayüz + bundle dize taraması [G]/[S] |
| 3D güncelleme yeri / gecikme | Cevaplandı | fetch/XHR kancası, Resource Timing, Long Task; REA `ev_d0b91f8e…` |
| Veri modeli şekli | Kısmen | bundle'daki yük anahtarları [S]; gerçek POST gözlenmedi |
| Doğrulama gösterimi | Cevaplandı | sınır değer denemeleri, `.error-meldung` konumları [G] |

**Erişilemeyen / bilinçli yapılmayan:**
- `/api/save`, `/api/send-inquiry`, e-posta doğrulama, 3D (STEP/STL/OBJ) ve PDF indirme tetiklenmedi (form gönderimi + kişisel veri + onay gerektiriyor). Bu yüzden yanıt gövdeleri, sunucu tarafı doğrulama ve indirme dosyası içeriği **[?]**.
- 3D indirme dosyasının istemcide mi üretildiği yoksa sunucudan mı geldiği **[?]** (bundle'da uzantı dizeleri var; e-posta doğrulamasıyla kilitli olduğu [Ç]).
- Şemada görülen agitator / ancillary location / ladder / directive / code / material thickness alanlarının arayüzde neden görünmediği **[?]** (başka bir sürüm veya gizli bölüm olabilir).
- REA senaryosunda 3D düğmesine tıklama adımı seçici hatasıyla zaman aşımına uğradı; 3D'ye geçişin ağsız olduğu yerleşik tarayıcıda Resource Timing ile ayrıca doğrulandı.
- Toplam boy formülünün (bombe yükseklikleri, board, zemin boşluğu) tam çözümü yapılmadı; gözlem: toplam boy zemin boşluğunu ve iki board'u içeriyor (D = 0'da 12000 + 2000 + 2×50 = 14100).
