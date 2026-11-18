# D2 Sitenin amacı ve hesap anlatımı
Mod: yaz
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`. Çıktı klasörü: `pressure-vessel-suite/docs/kilavuz2/`.

## KESİN KURALLAR
- HİÇBİR kabuk/terminal komutu çalıştırma (headless modda izin yok). Yalnız dosya okuma/arama/yazma/düzenleme araçları. PDF'i başka ajanlar basar; raporda "çalıştırılmadı" yaz.
- Yalnız bu paketin çıktı dosyasına yaz. Kaynak koda (`src/`, `packages/`, `apps/`), `.project-ai/`, `gemininin buldukları/` dokunma.
- Hedef okur: basınçlı kap, mühendislik ve ASME'yi HİÇ bilmeyen biri. Sade Türkçe; her teknik terim ilk geçtiği yerde parantez içinde sade dille açıklanır (ör. "MAWP (kabın taşıyabileceği en yüksek çalışma basıncı)").
- UYDURMA YOK: Her bilgi ya kodda/envanterde/`docs/` altındaki belgelerde vardır ya da genel mühendislik bilgisidir. Emin olmadığın bir sayıyı, formülü ya da madde numarasını YAZMA; "bu değeri malzeme sertifikasından / standarttan alın" de. İzin verilen gerilme, tablo değeri vb. telifli standart verisini yazma (kural K6): kullanıcıya "bu değeri standarttan/sertifikadan siz girin" de.
- Çıktı biçimi: HTML PARÇASI (doctype/head/body YOK). İzinli etiketler: section, h2, h3, p, ul, ol, li, table, thead, tbody, tr, th, td, figure, img, figcaption, dl, dt, dd, strong, em, div (yalnız class="ipucu" ya da class="uyari"). Görsel: `<figure><img src="img/DOSYA.png" alt="..."><figcaption>Şekil: ...</figcaption></figure>` (DOSYA, `docs/kilavuz2/img/INDEX.md` içindeki gerçek dosya adı olmalı; olmayan dosya adı yazma).

## GÖREV
Okur hiç bilmiyor. Şu bölümleri sırayla yaz (her biri `<section>` + `<h2>`):
1. **Bu site nedir, ne işe yarar?** Basınçlı kap nedir (günlük örneklerle: hava tankı, kazan, seperatör), neden hesap gerekir (güvenlik), Vessela'nın (zeyslabs-vessela) amacı, kime hitap ettiği, neleri YAPMADIĞI (resmî onay/ASME damgası vermez; sonuçlar mühendis kontrolüne tabidir - `docs/limitations.md`'ye bak).
2. **Neyi bulmak için hesap yapıyoruz?** Gerekli et kalınlığı, nominal kalınlık, izin verilen en yüksek çalışma basıncı (MAWP), hidrostatik test basıncı, nozul/açıklık takviyesi, mesnet/ayak kontrolü, kütle/maliyet (BOM). Her biri için "neden bulunur, sonuç ne ifade eder" 2-4 cümle.
3. **Hesap nasıl yapılır? (sade anlatım)** Kabuk (silindir) ve bombe (kapak) et kalınlığının mantığı: basınç + çap + malzeme dayanımı + kaynak verimi + korozyon payı -> gerekli kalınlık. Formülleri sadece `pressure-vessel-suite/packages/*/src` kodundan ve `pressure-vessel-suite/docs/calculation-coverage.md` + `pressure-vessel-suite/tests/golden_cases/test_hand_calc_ug27_ug32.py` içinden doğrulayarak ver (ASME VIII-1 UG-27 silindir, UG-32 bombe; EN 13445 destekleniyorsa kısaca belirt). **Bir örnek hesabı baştan sona anlat:** golden test dosyasındaki silindir örneği (iç çap 1800 mm, tasarım basıncı 2,5 MPa, izin verilen gerilme 138 MPa, kaynak verimi 1,0 -> gerekli kalınlık 16,484 mm) ve 2:1 elipsoidal bombe örneği (iç çap 2000 mm, 2,0 MPa -> 14,514 mm). Önce dosyayı oku, sayıları dosyadaki beklenen değerlerle bire bir eşleştir, formülü adım adım göster.
4. **Siteyi kullanma akışı (6 adım):** Yeni Proje -> Tasarım Koşulları -> Kap Geometrisi -> Hesap Sonuçları -> 3D Model -> Rapor & Çıktı; her adımın amacı 2-3 cümle (ayrıntılı alan anlatımı başka bölümde; "bkz. alan anlatımı" yaz). `pressure-vessel-suite/docs/kilavuz2/img/INDEX.md`'den uygun genel ekran görüntülerini ekle (açılış, yeni proje vb.).
5. **Sonuçları nasıl okurum?** PASS/FAIL, uyarılar (notices), varsayımlar listesi, "ne zaman mühendise danışmalı". Hesap sonuç ekranı görüntüsünü ekle (INDEX'ten).
6. **Önemli uyarılar:** küçük açıklık muafiyeti (UG-36(c)(3)) beyanı kullanıcının sorumluluğundadır; şablonlarda malzeme gerilmeleri BOŞtur, girmeden hesap hata verir; sonuç bir mühendis tarafından doğrulanmalıdır.
7. **Sözlük:** en az 25 terim (basınç, tasarım sıcaklığı, MAWP, korozyon payı, kaynak verimi, bombe, nozul, manşon, flanş, takviye, mesnet, eyer, etek, hidrotest, vb.), her biri 1-2 cümle.
Çıktı dosyası: `pressure-vessel-suite/docs/kilavuz2/parca-D2.html` (tek `<section id="d2">`; sözlük `<dl>`).
Rapor (<=8 satır): ilk satır `D2 amac-ve-hesap - TAMAM | KISMİ | BAŞARISIZ`; doğruladığın formül/örnek sayıları; emin olmadığın noktalar; çalıştırılmadı.
