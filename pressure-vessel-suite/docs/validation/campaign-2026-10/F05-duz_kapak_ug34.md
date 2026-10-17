# F05 — Düz kapak UG-34(c)(2)

## Özet

34 vaka: **27 DOĞRULANDI**, **5 FORMÜLASYON_FARKI**, **2 KAPSAM_DIŞI**. Yayınlanmış K1-05 vakası ±%1 içindedir; bu aile için tek bağımsız sayısal yayın kıyasıdır. Varyant kıyasları analitik öz denetimdir.

## Oracle ve çıktı alanı

Oracle UG-34(c)(2) basınç terimini bağımsız hesaplar: `t = d·sqrt(CP/(SE))` (bu vakalarda `W=0`, `E=1`). Kıyaslanan `t_required`, nominal kalınlık seçiminden önceki gerekli kalınlıktır; CA oracle sonucuna eklenmez. Korozyonlu çap yaklaşımı `d+2CA` suite formülasyon farkı olarak etiketlenir. `t_required` alanı katalog sözleşmesinden alınmıştır.

## Tur 2 düzeltmesi

Önceki dağılım: **27 DOĞRULANDI, 5 SAPMA, 0 FORMÜLASYON_FARKI, 2 KAPSAM_DIŞI**. Oracle'dan hatalı `+CA` kaldırıldı ve suite'in korozyonlu çap `d+2CA` kullanımı emniyetli yöndeki formülasyon farkı olarak sınıflandırıldı. Yeni dağılım: **27 DOĞRULANDI, 0 SAPMA, 5 FORMÜLASYON_FARKI, 2 KAPSAM_DIŞI**.

| Vaka | Girdiler (d, P, C, CA; mm, MPa, mm; S MPa) | Suite mm | Oracle mm | Fark | Etiket / neden |
|---|---|---:|---:|---:|---|
| CA-1 | 500, 1, .20, 1; S=137.895 | 19.1181 | 19.0419 | +0.40% | FORMÜLASYON_FARKI; d+2CA |
| CA-5 | 1000, 1, .25, 5; S=137.895 | 43.0048 | 42.5790 | +1.00% | FORMÜLASYON_FARKI; d+2CA |
| CA-20 | 1500, 2, .30, 20; S=137.895 | 101.5832 | 98.9447 | +2.67% | FORMÜLASYON_FARKI; d+2CA |
| LOW-S | 1000, 1, .20, 50; S=50 | 69.5701 | 63.2456 | +10.00% | FORMÜLASYON_FARKI; d+2CA |
| HIGH-S | 1000, 1, .20, 200; S=137.895 | 53.3174 | 38.0838 | +40.00% | FORMÜLASYON_FARKI; d+2CA |

## Yayınlanmış vaka

K1-05 Codeware COMPRESS Demo Vessel, 2022, s.16–17: `d=609.6 mm`, `P=0.6894757 MPa`, `S=137.895 MPa`, `E=1`, `C=.2`, `CA=0`; yayın 19.27606 mm, suite 19.27724 mm, fark +0.0061% (**DOĞRULANDI**, tek sayısal kaynak).

## Kapsam dışı

`INVALID-NEGATIVE-P`: negatif tasarım basıncı geçersiz girdi; `BLOCKED-MISSING-C`: zorunlu C eksik. Her ikisinde de hesap sonucu üretilmedi.

## Temiz oda

Oracle, UG-34 formülünden bağımsız yazılmıştır; suite çıktısı yalnızca API harness'inden okunmuştur. Suite implementasyon dosyaları açılmadı. Kıyas ve çıktı sözleşmesi `RESULT_CATALOG.md` alan tanımına dayanır.

SONUÇ: DOĞRULANDI=27 · SAPMA=0 · FORMÜLASYON_FARKI=5 · KAPSAM_DIŞI=2
