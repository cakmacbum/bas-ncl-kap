# F14 — Etek desteği

## 1. Özet

33 vaka kimliği (31 API sayısal vaka, 2 bloklanan/geçersiz vaka), toplam 66 nicelik satırı.
Etiket dağılımı: DOĞRULANDI 32 · FORMÜLASYON_FARKI 29 · SAPMA 1 · TEK_KAYNAK 0 · KAYNAK_BEKLİYOR 0 · KAPSAM_DIŞI 4.
API'den sayı üreten vakalar `REVIEW REQUIRED` statüsündedir; normal sayısal kıyasa alındılar.

## 2. Oracle formülleri

- Etek halkası ince cidarlı kesit: `A = πDt`, `Z = πD²t/4`; eksenel aşırı lif gerilmesi `σ = |W/A| + |M/Z| = |W/(πDt)| + |4M/(πD²t)|`.
- Çekme tarafı kaynak gerilmesi: `max(0, -W/A + M/Z)/E`. Basma tarafındaki UG-23(b) B sınırı kullanıcı verisidir; bağımsız oracle bu malzeme/standart limitini türetmez.
- Kuvvet N, uzunluk mm kullanıldığından gerilme MPa çıkar. API'nin `W_total` ve `M_overturning` ara yükleri bağımsız geometri denklemlerine girer; API gerilme ara değerleri oracle girdisi yapılmaz.

## 3. SAPMA tablosu

| case_id | girdiler | suite | oracle | fark % | yön | olası neden |
|---|---|---:|---:|---:|---|---|
| K3-08 | Yayın: W=720 kN, M=2050 kN·m, D=4250 mm, t=10 mm; API temel tank yükü | 14.514 MPa | 19.843 MPa | -26.86 | suite düşük: emniyetsiz gösterim | Yayın vaka yükü 720 kN ile API temel tankının hesaplanan ağırlığı eşleşmedi; bu satır uçtan uca aynı girdi değildir. Yük aktarım arayüzü yok. |

## 4. Yayınlanmış vakalar

| case_id | kaynak | yayımlanmış değer | kıyas |
|---|---|---:|---|
| K3-08 | CRC Press (2005), “Chapter ten: Design of vessel supports”, §10.3.1–10.3.2, denklem (10.2)–(10.6), K3 kaynak kaydı | 19.84 MPa etek basması | Bağımsız denklem girdilerden 19.843 MPa üretir (yayınla uyum). API suite değeri 14.514 MPa; W girdisi temel tank API yükü olduğundan doğrudan doğrulama sayılmaz. |

K3-09/10/11/12 ayrı vaka yapılmadı: K3-09 için kaynakta etek üst/alt farklı geometri-yük durumu mevcut, fakat harness tek destek modeli bu aktarımı kurmuyor; K3-10 basınç ve deprem birleşik yüklerini ayrı tarif ediyor; K3-11 A/Z tarama örneği yayın verileriyle tam kurulabilir olsa da API'nin aynı W verisini alması mümkün değil; K3-12 etek geometrisi belirsiz.

## 5. Kapsam dışı ve bloklanan vakalar

| case_id | durum | neden |
|---|---|---|
| MISSING-B | BLOCKED → KAPSAM_DIŞI (iki nicelik) | `skirt_allowable_compressive_MPa` girilmedi; B değeri standart tablosundan tahmin edilmedi. |
| INVALID-THICKNESS | HTTP 422 / BLOCKED → KAPSAM_DIŞI (iki nicelik) | Sıfır etek kalınlığı domain kısıtını ihlal ediyor. |

İstenen yük, test ağırlığı ve rüzgâr momenti varyantlarından moment doğrudan destek girdisiyle değiştirildi. Harness destek yüküne bağımsız ağırlık girişi sunmadığı için W varyasyonu uygulanamadı; grid vaka ağırlığı sabit temel tankın API hesabından gelir. Bu sınırlama K3-08 kıyasını etkiliyor. Kaynak verimi 0.55–1 aralığında tarandı; oracle kaynak tarafında E uygular, suite tarafındaki ilgili sonuç `S_tension` değeridir.

## 6. Temiz oda beyanı

Oracle sıfırdan halka kesit alanı ve kesit modülüyle yazıldı. Yasaklı hesap paketleri açılmadı/okunmadı; suite çıktısı yalnızca harness'in FastAPI `/api/projects/{id}/calculate` API yolundan alındı. Yalnızca izinli aile klasörüne ve bu rapor dosyasına yazıldı.
