# G2 Alan anlatımı - Geometri 3.3, 3.4, 3.5
Mod: yaz
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`. Çıktı klasörü: `pressure-vessel-suite/docs/kilavuz2/`.

## KESİN KURALLAR
- HİÇBİR kabuk/terminal komutu çalıştırma (headless modda izin yok). Yalnız dosya okuma/arama/yazma/düzenleme araçları. PDF'i başka ajanlar basar; raporda "çalıştırılmadı" yaz.
- Yalnız bu paketin çıktı dosyasına yaz. Kaynak koda (`src/`, `packages/`, `apps/`), `.project-ai/`, `gemininin buldukları/` dokunma.
- Hedef okur: basınçlı kap, mühendislik ve ASME'yi HİÇ bilmeyen biri. Sade Türkçe; her teknik terim ilk geçtiği yerde parantez içinde sade dille açıklanır (ör. "MAWP (kabın taşıyabileceği en yüksek çalışma basıncı)").
- UYDURMA YOK: Her bilgi ya kodda/envanterde/`docs/` altındaki belgelerde vardır ya da genel mühendislik bilgisidir. Emin olmadığın bir sayıyı, formülü ya da madde numarasını YAZMA; "bu değeri malzeme sertifikasından / standarttan alın" de. İzin verilen gerilme, tablo değeri vb. telifli standart verisini yazma (kural K6): kullanıcıya "bu değeri standarttan/sertifikadan siz girin" de.
- Çıktı biçimi: HTML PARÇASI (doctype/head/body YOK). İzinli etiketler: section, h2, h3, p, ul, ol, li, table, thead, tbody, tr, th, td, figure, img, figcaption, dl, dt, dd, strong, em, div (yalnız class="ipucu" ya da class="uyari"). Görsel: `<figure><img src="img/DOSYA.png" alt="..."><figcaption>Şekil: ...</figcaption></figure>` (DOSYA, `docs/kilavuz2/img/INDEX.md` içindeki gerçek dosya adı olmalı; olmayan dosya adı yazma).

## GÖREV: Alan alan anlatım
Kaynaklar (OKU): `pressure-vessel-suite/docs/kilavuz2/alan-envanteri.json` (her kayıt: adim, alt_adim, etiket, tip, birim, varsayilan, secenekler, ipucu_kodda, gorsel, belirsiz), `pressure-vessel-suite/docs/kilavuz2/alan-envanteri.md`, `pressure-vessel-suite/docs/kilavuz2/img/INDEX.md`, gerekirse `pressure-vessel-suite/apps/web-ui/src/pages.tsx` ve `docs/`.
Her adım/alt adım için: kısa bir giriş paragrafı ("Bu ekran ne için?", 2-3 cümle) -> ilgili ekran görüntüsü (envanterdeki `gorsel` dosyası) -> her alan için `<dl>` içinde `<dt>Etiket (birim)</dt><dd>2-3 cümlelik açıklama</dd>`: alan NE demek, değerini nereden bulursunuz / tipik aralık nedir (yalnız eminsen), yanlış girilirse ne olur. Seçenekli alanlarda seçenekleri tek tek ve kısa anlat. Onay kutularında (beyan) neyi onayladığınızı ve sorumluluğun size ait olduğunu açıkça yaz.
KAPSAM KURALI: Envanterdeki HER alanı en az bir kez anlat (atlama; denetleyici etiketleri tek tek arayacak, etiketi envanterdeki gibi AYNEN yaz). İstisna: çok tekrarlı tablolar (WRC eğri/katsayı tabloları, nozul eğri tablosu hücreleri) - bunları hücre hücre yazma; tabloyu, satır/sütun anlamını ve ne zaman doldurulacağını TEK açıklamayla anlat. `belirsiz: true` alanları da anlat, açıklamanın başına "(Bu alan yalnız şu durumda görünür: ...)" yaz.
Ton: dostça, uzun cümle yok, jargon yok. Her adım sonunda `<div class="ipucu">` ile 1-3 maddelik "Sık yapılan hatalar".

KAPSAM: Adım 3 (Kap Geometrisi) içinde `alt_adim` metni "3.3 ..." (flanşlı nozullar), "3.4 ..." (manşonlar), "3.5 ..." (mesnetler: ayak, eyer, etek) ile başlayanların TAMAMI.
Çıktı dosyası: `pressure-vessel-suite/docs/kilavuz2/parca-G2.html` (tek `<section id="g2">`).
Rapor (<=8 satır): ilk satır `G2 alan-anlatimi - TAMAM | KISMİ | BAŞARISIZ`; anlatılan/kapsamdaki alan sayısı; atlananlar; çalıştırılmadı.
