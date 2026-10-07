# F21 — Flanş Appendix 2 doğrulama kampanyası

## 1. Özet

30 üretilmiş varyant ve kaynak kimlikleriyle 2 yayınlanmış kayıt (K2-12, K2-13) vardır. `results.json` toplam 256 metrik satırı içerir. Etiket dağılımı: DOĞRULANDI 0, FORMÜLASYON_FARKI 0, SAPMA 0, TEK_KAYNAK 0, KAYNAK_BEKLİYOR 176, KAPSAM_DIŞI 80. Pozitif karşılaştırma bulunmadığından bu sayım formül doğrulaması değildir.

Varyantlar gevşek/integral-hublu tip, boyutlar, cıvata sayısı/alanı, conta m/y, basınç ve eksik/geçersiz kullanıcı faktörlerini örnekler. API 30 vakayı çalıştırdı; talep edilen App. 2 yük/gerilme ara değerleri ile eşleşen hesap satırı sağlamadı. Veri modeli ayrıca conta temas boyutlarını ve cıvata dairesi/aralığı girdilerini taşımıyor.

## 2. Temiz oda oracle formülleri

- App. 2-5: (W_{m1}=H+H_p), (W_{m2}=pi bGy), (A_m=W_{m1}/S_a), (W=(A_m+A_b)S_a/2). b/G için halka conta geometrisi ve H/Hp için basınç etkin alanı gerekir. Varyant modelinde eksik olan boyutları varsaymadım; oracle bu kalemleri null bırakır.
- App. 2-6: (M_o=M_D+M_G+M_T); operasyon ve montaj momentleri farklı yük bileşimleridir. Gerekli girdiler/terimler tam değil.
- App. 2-7: (S_H,S_R,S_T), Appendix 2 faktörleri ve moment/yük girdilerinden hesaplanır; yayınlanmış K2 örnekleriyle doğrulanabilir, ancak API eşleşen değer vermedi.
- App. 2-3 bolt spacing: kaynak K2-13'te (B_{sc}=1.1893) bildirilmiştir. Örnekten bu katsayının nedenini kaydettim; projede cıvata aralığı verisi bulunmadığından suite uygulamasını ölçemedim. Uygulayıp uygulamadığı hakkında SAPMA/FORMÜLASYON_FARKI hükmü verilemez.

## 3. SAPMA tablosu

SAPMA etiketi yok. Sayısal suite/oracle eşleşmesi olmadığından fark yüzdesi ve emniyet yönü hesaplanamaz. API satırı bulunmaması, düşük/yüksek gerilme anlamına gelmez.

## 4. Yayınlanmış vakalar

| case_id | Kaynak ve yayınlanmış başlıca değerler | Suite karşılığı |
|---|---|---|
| K2-12 | Paget, APV 9.1.1, pp. 22–26: Wm1 362291 lb, Wm2 182053 lb, Am 14.4916 in², W 635645 lb, Mo 782355 in·lb; operasyon SH/SR/ST 14545/80/10958 psi | KAYNAK_BEKLİYOR; API eşleşen Appendix 2 satırı üretmedi, ayrıca tam conta geometrisi modelde yok |
| K2-13 | PVE-4293, pp. 11–15: Wm1 53966 lb, Wm2 50647 lb, Am 2.159 in², W 67383 lb, Mop 97547 in·lb; operasyon SH/SR/ST 19821/1180/8884 psi; Bsc 1.1893 | KAYNAK_BEKLİYOR; API eşleşen satır ve bazı faktörler yok |

Bu değerler `sources-K2.md` içindeki yayınlanmış kayıtların kaynak birimleriyle aktarımıdır; suite sonucuyla eşleştiği iddia edilmez. K2-14 flanş vakası değildir (dış basınç silindirik gövde) ve dahil edilmedi.

## 5. Kapsam dışı ve bloklanan vakalar

API 30 varyant boyunca flange Appendix 2 için eşleşen çıktı vermedi. Zorunlu girdi eksik/geçersiz vakalarda bu nedenle KAPSAM_DIŞI satırları oluştu; API envelope hata durumları ve status değerleri ham sonuçlarda saklıdır. Kullanıcı faktörleri eksikken beklenen BLOCKED davranışı için ham durum kontrol edilmelidir; bu çalışma UI/API sonuçlarından ayrı bir K4 uyarı metni doğrulayamadı. KAPSAM_DIŞI, geçersiz girdinin beklenen biçimde reddedildiğini tek başına kanıtlamaz.

## 6. Temiz oda beyanı

Oracle kodu bu aile klasöründe bağımsız yazılmıştır; yasaklı hesap implementasyonlarını bilerek incelemedim. Ancak ilk keşif sırasında `rg` araması yasaklı `packages/code-asme-viii-1` ve `packages/calc-core` dosyalarından eşleşme satırlarını terminal çıktısına getirdi; ayrıca arama `packages/flanges` yolundan da sonuç içerdi. Bu istenmeyen okuma temiz oda şartına sapmadır ve sonuçlar suite implementasyonuna göre kalibre edilmemiştir. Domain modelleri, harness, kaynak notları ve API çıktısı dışındaki hesap kodlarından hiçbir formül alınmadı.
