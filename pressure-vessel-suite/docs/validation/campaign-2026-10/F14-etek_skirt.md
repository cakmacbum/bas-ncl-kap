# F14 — Etek desteği

## 1. Özet

33 vaka kimliği, 66 nicelik satırı üretildi. 31 vaka API'den sayısal sonuç verdi ve 62 nicelik satırı bağımsız oracle ile kıyaslandı. Etiket dağılımı: DOĞRULANDI 34 · FORMÜLASYON_FARKI 28 · SAPMA 0 · TEK_KAYNAK 0 · KAYNAK_BEKLİYOR 0 · KAPSAM_DIŞI 4. Sayısal satırların tümü `REVIEW REQUIRED`; sonuç ürettikleri için kıyaslandı.

## 2. Oracle formülleri

- İnce cidarlı dairesel etek: `A = πDt`, `Z = πD²t/4`; eksenel uç lif gerilmesi `σmax = |W/A| + |M/Z|`.
- Kaynak tarafı: çekme gerilmesi `max(0, −W/A + M/Z) / E`; E kaynak verimidir.
- N ve mm birimleri MPa verir. W ve geometri API satırındaki `W_total`, `D_skirt_mean`, `t_skirt` alanlarından; M `M_overturning` alanından alındı. Oracle, API gerilme sonuçlarını girdi olarak kullanmaz.
- UG-23(b) izin verilen basma B değeri standarttan türetilmedi; yalnız kullanıcı girdisi olarak kaldı.

## 3. SAPMA tablosu

Bu koşturmada SAPMA etiketi alan nicelik yoktur. API'nin hesapladığı girdilerle bağımsız denklemler eşleşti; SAPMA tablosu boştur. K3-08'in yayınlanmış 19.84 MPa değeri API değeriyle aynı yük girdisi değildir; aşağıdaki kaynak tablosunda ayrı ele alınmıştır.

Yön tanımı: suite oracle'dan düşükse emniyetsiz, yüksekse emniyetli gösterim olurdu. Bu turda bu yönde sınıflandırılacak SAPMA bulunmadı.

## 4. Yayınlanmış vakalar

| case_id | Kaynak ve yayın değeri | API kıyası |
|---|---|---|
| K3-08 | CRC Press (2005), “Chapter ten: Design of vessel supports”, §10.3.1–10.3.2, (10.2)–(10.6): W=720 kN, M=2050 kN·m, D=4250 mm, t=10 mm; yayımlanan etek basması 19.84 MPa. | Geometri ve moment API örneğine aktarıldı. Harness temel tankın `W_total` yükü 720 kN olarak ayarlanamıyor; API 14.514 MPa üretti. Bu nedenle yayın değeri doğrudan API doğrulaması sayılmaz. `results.json` içindeki K3-08 oracle kıyası API'nin kendi W girdisini kullanır ve yayınlanan 19.84 MPa ile kıyas değildir. |

K3-09/10/11/12 için kaynakta farklı geometri/yük birleşimleri, basınç-deprem durumları veya belirsiz etek geometrisi bulunur. Bu harness arayüzüyle eşdeğer vaka kurulamamıştır; kaynak sayıları API kıyası gibi sunulmadı.

## 5. Kapsam dışı ve bloklanan vakalar

| case_id | Durum | Neden |
|---|---|---|
| MISSING-B | BLOCKED → KAPSAM_DIŞI (2 nicelik) | `skirt_allowable_compressive_MPa` eksik; B değeri standarttan tahmin edilmedi. |
| INVALID-THICKNESS | HTTP 422 → KAPSAM_DIŞI (2 nicelik) | Sıfır etek kalınlığı girdi kısıtını ihlal ediyor. |

30 GRID varyantında çap, kalınlık, yükseklik, kaynak verimi ve devrilme momenti değiştirildi. `skirt_column()` örnek projesinin kullanılabilir ağırlığı varyant girdisi değildir; bu nedenle W sabit suite modelinden alındı. İşletme/test ağırlığı varyantı bu harness sözleşmesiyle kurulamıyor. K3-08 bu sınıra örnektir.

## 6. Temiz oda beyanı

Oracle bağımsız ince cidarlı halka denklemlerinden yazıldı. Yasaklı hesap implementasyonları açılmadı/okunmadı. Örnek girdileri ve sonuç satırları katalog sözleşmesine göre seçildi; suite sayıları yalnız FastAPI `/api/projects/{id}/calculate` yolundan alındı. Yalnız F14 aile klasörüne ve bu rapora yazıldı.
