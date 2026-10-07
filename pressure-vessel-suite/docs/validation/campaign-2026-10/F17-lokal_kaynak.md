# F17 — Lokal gerilme ve kaynak hattı

## 1. Özet

31 vaka koşturuldu: 27 `KAYNAK_BEKLİYOR`, 3 `KAPSAM_DIŞI` (API 422 ile bloklanan geçersiz girdiler), 1 `TEK_KAYNAK` (yayınlanmış geometri). `DOĞRULANDI`, `FORMÜLASYON_FARKI` ve `SAPMA`: 0. API vakalarının hiçbiri kaynak geometrisi veya kaynak gerilmesi döndürmediği için sayısal suite karşılaştırması yapılamadı.

## 2. Oracle formülleri

1. Kapalı dikdörtgen çizgi-kaynak: `Lw = 2(b+d)`.
2. Blodgett kesit modülü: `Sw = bd + d²/3`; dikdörtgen çizgiler üzerinde `Iw = ∫y² ds`, `c=d/2`, `Sw=Iw/c`.
3. Daire: `Lw = πD`, `Sw = πD²/4`.
4. Geometrik polar çizgi integrali `Jw = ∮r² ds`; dikdörtgen için `(b³+d³)/3 + bd(b+d)/2`, daire için `πD³/4`. Bu, yönlü `Sw` yerine geçmez.
5. Kaynak gerilmesi için API'den eşleşen yük ve yön bileşenleri alınamadı; tahmini bir gerilme üretilmedi. WRC katsayısı girdisi yalnız boyutsal ölçekleme parametresi; fiziksel katsayı doğrulaması değildir.

Dayanak: Blodgett, *Design of Welded Structures*, §7.4 (engineering-source-review-2026-09-30.md §3); bağımsız çizgi integralleri.

## 3. SAPMA tablosu

SAPMA vakası yok. 27 geçerli API vakasında `leg_stress` sonucu `REVIEW REQUIRED` ve sayısal aksiyel gerilme verdi; fakat Lw/Sw/Jw/kaynak gerilmesi sunmadığı için bunlar farklı büyüklüklerdir ve kıyas dışı bırakıldı. Bu sonuçlara yapay fark veya emniyet yönü atanmadı.

## 4. Yayınlanmış vakalar

| case_id | Kaynak / girdiler | Oracle | Suite | Etiket |
|---|---|---:|---|---|
| PUB-K3-22 | Union College MER419, Shigley 10. bas. Tablo 9-2; `b=70 mm`, `d=120 mm`; sources-K3.md K3-22 | `Sw=13,200 mm²`, `Lw=380 mm` | API'de Sw/Lw yok | TEK_KAYNAK |

K3-22'nin yayınlanan `Iu/c` türetimi oracle Sw ile eşleşir. Kaynak aile politikası gereği tek vaka, formülü DOĞRULANDI saymaya yetmez.

## 5. Kapsam dışı ve bloklanan vakalar

| case_id | Neden |
|---|---|
| INVALID-ZERO | Negatif tasarım basıncıyla API 422 / `BLOCKED INVALID INPUT` |
| INVALID-NEGATIVE | Negatif tasarım basıncıyla API 422 / `BLOCKED INVALID INPUT` |
| INVALID-MISSING | Negatif tasarım basıncıyla API 422 / `BLOCKED MISSING INPUT` |

API blokajı kaynağı geçersiz geometriyi değerlendirmeden proje oluşturma doğrulamasında oluştu; bu nedenle vakalar `KAPSAM_DIŞI` sınıfında. Diğer API vakaları için lokal kaynak/WRC hesap sonucu mevcut değil; bunlar sonuç üretmeyen destek vakaları olarak raporlandı.

## 6. Temiz oda beyanı

Yasaklı implementasyon paketleri açılmadı veya okunmadı. Suite sonuçları yalnız `run_case` üzerinden public API yanıtından alındı. Oracle, yayınlanmış kaynak notlarındaki geometri bağıntılarından ve bağımsız çizgi integrallerinden sıfırdan kuruldu. Domain modelleri, campaign harness/karşılaştırıcı ve validation kaynak notları okundu. `.project-ai/ORKESTRA.md` bu worktree'de bulunmadığından C-1/C-2 metni incelenemedi.
