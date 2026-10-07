# F03 — Torisferik bombe doğrulama (UG-32(e) + Appendix 1-4(d))

## 1. Özet

32 vaka, 96 nicelik karşılaştırması. Etiket dağılımı: DOĞRULANDI 93; KAYNAK_BEKLİYOR 3; FORMÜLASYON_FARKI 0; SAPMA 0; TEK_KAYNAK 0; KAPSAM_DIŞI 0. 31 girdi vakası hesaplandı (30 geometrik varyant + K1-10 yayın vakası); BAD-MISSING-R API tarafından varsayılan yarıçapla hesaplandı ve ayrı notlandı.

## 2. Oracle formülleri

- ASME VIII-1 UG-32(e), torisferik başlık: `M = 1/4(3 + √(L/r))`; `t = PLM/(2SE − 0.2P)`.
- Appendix 1-4(d) ters basınç bağıntısı: `MAWP = 2SEt/(LM + 0.2t)`.
- Oracle bağımsız Python hesabında P ve S MPa, boyutlar mm kullanıldı. Nominal kalınlık ile hesap kalınlığı ayrımı korunarak API `t_required` kıyaslandı.

## 3. SAPMA tablosu

SAPMA etiketi alan vaka yok. Yayın vakasında API ve bağımsız sonuçlar 1% tolerans içinde kaldı. Standart rotada r/D=5.9% kasıtlı alt-sınır denemesidir; API `FAIL` durumu verdi, fakat nicel değer formülle örtüştü. `judge` API durumuna bakmadan üretilen sayısal sonucu karşılaştırır.

| case_id | Girdi / ölçüt | Suite | Oracle / yayın | Fark | Yön | Olası neden |
|---|---|---:|---:|---:|---|---|
| PUB-K1-10 | Dᵢ=47 in, L=48 in, r=2.9273 in, P=420 psi; kalınlık | 0.8894 in | 0.8901 in | −0.077% | hafif emniyetsiz | yayın yuvarlaması / COMPRESS hassasiyeti (tahmin) |
| PUB-K1-10 | aynı; M | 1.762341 | 1.7623 | +0.0024% | — | yuvarlama |
| PUB-K1-10 | aynı; MAWP | 420.32 psi | 420.01 psi | +0.075% | — | — |

Yön, gereken kalınlığın düşük çıkmasının olası muhafazakârlık kaybı anlamında emniyetsiz olarak işaretlenmiştir.

## 4. Yayınlanmış vakalar

| case_id | Kaynak | Yayınlanan sonuç | Suite | Etiket |
|---|---|---|---|---|
| PUB-K1-10 | PVE Four Heads / COMPRESS, VIII-1 2015, s. 9–10; `sources-K1.md` K1-10 | M=1.7623; t=0.8901 in; MAWP=420.01 psi | t=0.8894 in; M=1.762341; MAWP=420.32 psi | DOĞRULANDI |

PVE-FD tablosu, `asme-worked-examples.md` tur 2’deki 14 temsilci noktanın kampanya girdisi veya tekil vaka verileri burada mevcut olmadığından ayrı sayısal vaka olarak çoğaltılmadı; bu tablo kümesi bu raporda kapsanmıyor.

## 5. Kapsam dışı ve bloklanan vakalar

- BAD-MISSING-R: `knuckle_radius` boş bırakıldı. Beklenti BLOCKED iken API otomatik standart yarıçap kabul edip PASS ve sayısal t/M/MAWP üretti. Bu, eksik girdinin bloke edilmesi sözleşmesine sapmadır; üç sayısal kıyas kaynak olmadığı için KAYNAK_BEKLİYOR olarak bırakıldı, KAPSAM_DIŞI sayılmadı.
- r/L alt sınırı vakası STD-r0059 API'de FAIL oldu ancak sayısal sonuç üretti; beklenen uyarı doğrulandı.
- Bloke hesap bulunmadı. `REVIEW REQUIRED` satırları mevcut değildi.

## 6. Temiz oda beyanı

Oracle, yalnızca bu dosyalardaki bağımsız UG-32(e)/Appendix 1-4(d) denklemleriyle hesaplandı. Suite sonuçları yalnızca kampanya harness’inin API çıktısından alındı. Yasaklanan code/plugin implementasyonları okunmadı; temiz oda kuralına uyuldu.

