# V01 — F01 UG-27 bağımsız sapma teyidi

## Kapsam ve yöntem

`results.json` içindeki dokuz SAPMA'nın tümü MAWP miktarıdır. `variants.py` girdileri ve suite formül akışı kontrol edildi. UG-27(c)(1) için bağımsız ters form kullanıldı: `t_req=P·R/(S·E−0.6P)` ve `MAWP=S·E·t_net/(R+0.6t_net)`. Burada MAWP değerlendirmesinde `t_net=t_nom·(1−mill)−CA_i−CA_o`; iç çap verildiyse `R=D_i/2+CA_i`, OD verildiyse `R=D_o/2−t_min+CA_o`. Kullanılan gerilme/efektiflik girdileri vaka girdileridir; P birimi MPa, boylar mm'dir.

## Gruplar

| Kök neden | Vaka sayısı | Hüküm | Yön | Suite MAWP farkı |
|---|---:|---|---|---:|
| MAWP net cidarından CAo çıkarılmıyor (grid-04/06/08/10, ca-16, large-21, medium-25/27 ve outside-23) | 9 | SUITE_HATASI | EMNİYETSİZ | +6.29%…+41.74% |
| OD yarıçapında CAo yerine CAi kullanılıyor (outside-23; birinci grupla çakışır) | 1 | SUITE_HATASI | EMNİYETSİZ | bu vakada yarıçap tek başına da hatalı; toplam fark +7.06% |

Büyüklük, raporlanan suite/reference farkıdır: `100·(suite/reference−1)`. Gruplar çakıştığı için benzersiz etkilenen SAPMA sayısı 9'dur. Birinci grubun etkilenen sayısı 9; ikinci kök neden için 1. UG-27(c)(1) ters cebirinde korozyon allowance'ları MAWP için elde kalan cidardan çıkarılır; dış yüzey CA'sı da mekanik/korozif kaybı temsil eder. `t_min` üzerinden hesaplanan ID de teslim iç yarıçaptır; OD'den iç yarıçap türetirken CAo eklenmeli, CAi değil.

## Bağımsız temsilci hesapları

### grid-04:mawp — CAo net cidardan düşülmüyor

Girdi: `D_i=1000`, `P=1.2`, `S=138`, `E=1`, `CA_i=2`, `CA_o=1`, `t_nom=20`, `mill=12.5%`. `R=500+2=502`; `t_min=20·0.875=17.5`; `t_net=17.5−2−1=14.5` mm. `t_req=1.2·502/(138−0.72)=4.38811` mm. `MAWP=138·14.5/(502+0.6·14.5)=2001/510.7=3.91815 MPa`. Oracle 3.91815 ile uyuşur; suite 4.18345 (+6.77%). Suite `t_actual=17.5` değerinden yalnız `CA_i=2` düşürüp CAo=1'i atlar; düzeltme önerisi: CAi ve CAo'yu MAWP net kalınlığından birlikte düşür. Bu bir suite hatasıdır, kodda uygulanmadı.

### ca-16:mawp — dış CA etkisi

Girdi: `D_i=900`, `P=2.5`, `S=138`, `E=1`, `CA_i=0`, `CA_o=6`, `t_nom=20`, `mill=0`. `R=450`; `t_min=20`; `t_net=20−0−6=14` mm. `t_req=2.5·450/(138−1.5)=8.24176` mm. `MAWP=138·14/(450+8.4)=1932/458.4=4.21466 MPa`. Oracle ile uyuşur; suite 5.97403 (+41.74%) CAo'yu cidardan düşmediği için yüksek.

### outside-23:mawp — CAo eksikliği ve OD yarıçapı

Girdi: `D_o=1620`, `P=3`, `S=160`, `E=0.85`, `CA_i=3`, `CA_o=1`, `t_nom=20`, `mill=12.5%`. `t_min=17.5`; `R=810−17.5+1=793.5`; `t_net=17.5−3−1=13.5` mm. `t_req=3·793.5/(136−1.8)=17.73845` mm. `MAWP=136·13.5/(793.5+8.1)=1836/801.6=2.29042 MPa`, oracle ile uyuşur. Suite 2.45213 (+7.06%). Suite yarıçapı `810−17.5+3=795.5` ile CAi'yi yanlış yöne uygular ve cidarda CAo'yu atlar. Öneri: OD dalında teslim iç yarıçapı `D_o/2−t_min+CA_o`; MAWP net kalınlığını `t_min−CA_i−CA_o` kur. İki suite düzeltmesi öneridir, uygulanmadı.

## Satır kanıtı ve hüküm

`packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py:653-655` mill tol uygulanmış `t_actual` kuruyor; `:692` yalnız CAi'yi `C` olarak alıyor; `:718-722` OD dalında `D_o/2−t_actual` yapıp `+C` (CAi) ekliyor; `:724` bu değerleri MAWP formülüne veriyor. `packages/code-asme-viii-1/src/code_asme_viii_1/formulas.py:356-360` `t_actual−C` hesaplayıp UG-27(c)(1) ters formülünü uyguluyor. Böylece CAo eksik ve OD yarıçapında CAi yanlış uygulanıyor. `results.json` farkları dokuz vakanın tamamını kapsıyor; iki nedenin dışında kalan SAPMA yok. Her iki grup da SUITE_HATASI'dır; düzeltilmesi önerilir, bu teyitte kod değiştirilmemiştir.

HÜKÜM: suite_hatası=2 (emniyetsiz=2) · oracle_hatası=0 · formülasyon=0

