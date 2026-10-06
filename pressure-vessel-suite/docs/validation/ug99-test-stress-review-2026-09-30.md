# UG-99(b) test gerilmesi incelemesi — 2026-09-30

## Bulgular

- `calculate_hydrotest_pressure` (`packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py`) test basıncını MAWP ve basınç sınırı malzemelerinin en düşük `S_test/S_design` oranından hesaplıyor. Mevcut testler oranı ve eksik test sıcaklığı verisinde `REVIEW_REQUIRED` davranışını sınar; her basınç bileşeninin hidrotest gerilmesini veya test sıcaklığındaki akma dayanımını sınamaz.
- ASME'nin resmî ürün kaydı BPVC VIII.1 için 2025 baskısını yürürlükteki baskı olarak listeliyor. UG-99(b), Bölüm II-D kaynaklı S oranını kullanarak gereken minimum test basıncını belirler; UG-22(j) test basıncı ve eşzamanlı statik yükün tasarımda dikkate alınmasını ister. Bu gereklilikler tek başına bileşen bazlı sayısal bir gerilme kabul ölçütü sağlamaz.
- National Board Bulletin'de yayımlanan bir teknik inceleme, VIII-1'in hidrotest yükleri için yöntem/kabul ölçütü tanımlamadığını; görünür kalıcı distorsiyonu reddetme ölçütü olarak verdiğini açıklar. Makale, silindirik kabuk için yeni durum geometrisi ve test sıcaklığındaki akma dayanımının %90'ını kullanan bir membran gerilmesi yöntemini kendi değerlendirme yöntemi olarak sunar. Bu, UG-99(b)'nin normatif bir 0.9 Sy kuralı olarak sunulamaz.

## Teknik karar

Mevcut veriyle bu açığı UG-99(b)'ye uygun otomatik PASS/FAIL kontrolü diye güvenli biçimde uygulamak mümkün değil. 0.9 Sy sınırını kod şartı olarak sabitlemeyin. Önce yetkili mühendis/kullanıcı tarafından seçilip onaylanmış değerlendirme kriteri ve kapsamı gerekir. Böyle bir kriter onaylanırsa yeni kontrol; her basınç sınırı bileşeni için test basıncıyla birlikte sıvı statik başını, gerçek test konumunu, yeni/korozyonlu geometrisini, malzemenin test sıcaklığındaki Sy değerini ve gerekli membran/eğilme veya yerel gerilme girdilerini kapsamalı; eksik bileşen/veride sonucu REVIEW_REQUIRED/BLOCKED bırakmalıdır. Mevcut LSR hesabı ve bu ayrı değerlendirme birbirine karıştırılmamalıdır.

## Eksik girdiler

- Her basınç sınırı elemanı/nozul ve ilgili kaynak/bağlantı geometrisi ile test konumundaki yerel basınç ve statik baş.
- Malzeme, ürün formu ve kod baskısıyla izlenebilir test sıcaklığı Sy; mevcut modelde `yield_strength` sıcaklığa bağlanmış değil.
- Kullanılacak kabul yöntemi (ör. yalnız membran sınırı mı, yoksa membran + eğilme/yerel gerilme mi), yeni veya korozyonlu kondisyon ve yetkili mühendis onayı.

## Kaynaklar

- ASME, *BPVC Section VIII, Division 1*, 2025 ürün ve baskı kaydı: https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1
- ASME, BPVC kaynakları; Bölüm II-D gerilme tabloları ve kod yorumları için resmî erişim kanalları: https://www.asme.org/codes-standards/publications-information/bpvc-resources
- National Board of Boiler and Pressure Vessel Inspectors, Francis Brown, “Pressures Associated with Pressure Vessel Design as Relating to ASME Section VIII, Division 1,” *National Board Bulletin*, Summer 2012, s. 8–10: https://www.nationalboard.org/SiteDocuments/Bulletins/SU2012.pdf

ASME'nin lisanslı kod metni burada alıntılanmamış veya kopyalanmamıştır. National Board makalesi yetkili yorum değil, yayımlanmış mühendislik değerlendirmesidir; 2025 baskısındaki madde değişikliklerini lisanslı nüshadan doğrulama gereği sürer.
