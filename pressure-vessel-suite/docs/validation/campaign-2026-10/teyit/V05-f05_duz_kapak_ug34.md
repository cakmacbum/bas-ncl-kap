# V05 — F05 düz kapak UG-34(c)(2) bağımsız teyit

## Gruplama ve hüküm

| Kök neden | Vaka sayısı | Hüküm | Yön | Fark (suite-reference) |
|---|---:|---|---|---:|
| CA, `d_corroded` içine `2CA` olarak ekleniyor; fakat t denklemine `+CA` olarak eklenmiyor | 5 | **SUITE_HATASI** | EMNİYETSİZ | −4.61%, −9.61%, −14.60%, −38.57%, −77.61% |

Sapma yüzdesi sonuç dosyasındaki `(suite-reference)/|reference|` tanımıdır. Düz dairesel kapak için UG-34(c)(2) hesabı `t_req = d√(CP/(SE)) + CA` (burada W=0); bu teyitte `E=1`, mill tol uygulanmıyor ve verilen `d` korozyonsuz çap kabul edilmiştir. Oracle `oracle.py:4-13` bu ifadeyi uyguluyor. Suite `design_code.py:486-491` ise `D=d+2CA` yapıyor, sonra `formulas.py:458-499` içinde yalnız `D√(CP/(SE))` hesaplıyor; `design_code.py:547-560` fonksiyona `CA=0` veriyor. Bu, korozyon payını basınç dayanımına çap büyümesi olarak sokup gereken kalınlık payını düşürüyor. Düzeltme önerisi: UG-34 için korozyonsuz tasarım çapını kullanıp CA'yı gerekli kalınlığa bir kez eklemek; ortak nominal kalınlık/negatif tolerans aşamasında ikinci kez eklenmediğini doğrulamak. Kod değiştirilmedi.

**Kanıt sınırı:** suite dalındaki `design_code.py:486-491` ve `547-560` gösterilen yöntem başlık (`Head`) dalıdır; kampanya girdilerinin API tarafından hangi nesneye eşlendiğini bu kapsamda okuyabildiğim paket kodundan tek başına kanıtlayamadım. Sonuç değerleri hatanın çapta CA kullanımı olduğunu güçlü biçimde gösteriyor; kampanya eşleme izi için açık kayıt bulunmuyor. `results.json` HIGH-S girdisini `S_MPa=137.895` olarak verir (etiket yanıltıcı); oracle hesabı da bu gerçek girdiye dayanır.

## Temsilci vakalar — elle hesap

Tüm vakalarda `W=0`, dolayısıyla bolt terimi sıfır; `MAWP = SE/d² × (t−CA)²/C` karşı düzenlemesiyle elde edilir. MAWP satırı kontrol değeri olup kampanyanın istenen miktarı t_req'dir. Ara değerler yaklaşık olarak yuvarlanmıştır.

**CA-1:** `d=500 mm, P=1 MPa, C=.20, CA=1 mm, S=137.895 MPa, E=1`. `CP/(SE)=.2/137.895=0.00145038`; `R=250 mm`; `√term=0.0380841`; `d√term=19.0420 mm`; `t_req=19.0420+1=20.0420 mm`. `MAWP` bu t_req ile CA düşüldüğünde `1.000 MPa`. Oracle `20.041920 mm`; suite `19.118088 mm` (−4.6095%). Suite'e uyan ara yol `(500+2×1)×0.0380841=19.1181 mm`, CA eki olmadan.

**CA-5:** `d=1000 mm, P=1 MPa, C=.25, CA=5 mm, S=137.895 MPa, E=1`. `CP/(SE)=.25/137.895=0.0018130`; `R=500 mm`; `√term=0.0425790`; `d√term=42.5790 mm`; `t_req=42.5790+5=47.5790 mm`; `MAWP=1.000 MPa`. Oracle `47.579028 mm`; suite `43.004818 mm` (−9.6139%). Suite yolu `1010×0.0425790=43.0048 mm`, CA eki olmadan.

**CA-20 (üçüncü kontrol):** `d=1500 mm, P=2 MPa, C=.30, CA=20 mm, S=137.895 MPa, E=1`; `CP/(SE)=.6/137.895≈0.004350`; `√term≈0.06596`; `d√term≈98.94 mm`; `t_req≈118.94 mm`; oracle `118.944720 mm`, suite `101.583246 mm`, −14.5963%. Bu vaka aynı kök nedene girer.

**LOW-S:** `d=1000 mm, P=1 MPa, C=.20, CA=50 mm, S=50 MPa, E=1`. `CP/(SE)=.2/50=.004`; `R=500 mm`; `√term=.0632456`; `d√term=63.2456 mm`; `t_req=113.2456 mm`; oracle `113.245553 mm`; suite `69.570109 mm` (−38.5670%). Suite izi `1100×.0632456=69.5701 mm`; yine CA kalınlığa eklenmiyor.

**HIGH-S etiketi:** sonuç girdisi `S=137.895 MPa` (200 MPa değil), `d=1000 mm, P=1 MPa, C=.20, CA=200 mm, E=1`. `CP/(SE)=.2/137.895=.00145038`; `R=500 mm`; `d√term=38.0838 mm`; `t_req=238.0838 mm`; oracle `238.083841 mm`, suite `53.317377 mm` (−77.6056%). Suite izi `1400×.0380841=53.3174 mm`. Vaka adı HIGH-S olsa da doğrulamada gerçek parametre olan 137.895 kullanıldı.

## Kapsam / öneri

Beş sapma da aynı hata grubudur; etkilenen vaka sayısı 5. Suite her vakada gereken kalınlığı düşük verdiği için emniyetsiz yöndedir. Düzeltme yalnız öneridir, uygulanmadı. İstenen ara değerlerden iç yarıçap `R=d/2` belirtildi; sonuçların tamamı d çapı üzerinden hesaplandı. Mill toleransı ve nominal et kalınlığı sonuçlarında ayrı girdiler bulunmadığından uygulanmadı; sonuçlar UG-34 basınç gereksinimidir.

HÜKÜM: suite_hatası=1 (emniyetsiz=1) · oracle_hatası=0 · formülasyon=0
