# F19 — EN 13445 ↔ ASME çapraz kontrol

## 1. Özet

30 vaka üretildi: 13 SAPMA, 17 KAPSAM_DIŞI. API PASS satırları döndürdü; ancak ASME satırlarında ölçüm değeri seçilemedi. Büyük EN farkları girdi/formülasyon farkı adayıdır; doğrulanmış hata değildir.

## 2. Oracle formülleri

`oracle.py` bağımsız EN 13445-3 7.4.2 hesabını uygular: `e=P·Di/(2·f·z−P)`, `f=min(Rp0.2/1.5,Rm/2.4)`. ASME kıyas bağıntısı `t=P·Di/(2·S·E−0.2P)`. EN 13445-3 7.5.3 bombe beta/geometri verisi ve 10.2.3.3 test basıncı API sonuçlarına güvenilir eşleşmedi; test basıncı formülü oracle'da yer alır.

## 3. SAPMA tablosu

Otomatik SAPMA etiketleri kodlar arası formülasyon/girdi farkından etkilenebilir; gerçek sapma hükmü değildir. Her vakanın girdisi, suite/oracle değeri ve yüzde farkı `results.json` alanlarında kayıtlıdır. Emniyet yönü belirsizdir. Olası neden (tahmin): suite allowable stress girdisiyle, oracle Rp0.2/Rm sınırlarından türetilmiş f ile çalışıyor.

## 4. Yayınlanmış vakalar

K4-01 CERN worksheet: Di=25 mm, f=154 MPa, z=1, P=4 MPa, e=0.329 mm (orta güven; P/z geri türetilmiş). K4-04 Ray Delaforce: P=300 psi, D=60 in, f varsayımı 20,000 psi, e=0.4533 in; yayınlanmış EN 0.453 in. K4-06: P=8.25 MPa, Di=2900 mm, yayınlanmış kalınlık 40/48 mm; bağımsız yeniden hesap 40.6/48.7 mm. K4-05 eliptik bombe sonucu dolaylı/düşük güvenlidir. Yayınlanmış vakalar API ile doğrulanmış karşılaştırmaya dönüşmedi.

## 5. Kapsam dışı / bloklanan vakalar

17 vaka KAPSAM_DIŞI: ASME satırlarında seçilen `e_required` alanı yoktu; bombe ve geçersiz/eksik malzeme girdileri güvenilir sayı sağlamadı. K4, EN 13445-5 test basıncı için doğrulanmış sayısal örnek olmadığını bildiriyor. API test basıncı ve bombe beta sonuçları açık.

## 6. Temiz oda beyanı

Temiz oda kuralına uyuldu. Yasaklı kod paketleri açılmadı/okunmadı; suite değerleri yalnızca `run_case` API çıktısından alındı. İzinli domain modelleri, harness, K4 ve doğrulama dokümantasyonu okundu.
