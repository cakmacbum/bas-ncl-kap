# V04 baÄŸÄ±msÄ±z teyit â€” UG-32(f)

## Gruplama ve hÃ¼kÃ¼m

| Grup | SAPMA vaka adedi | HÃ¼kÃ¼m | YÃ¶n | Fark |
|---|---:|---|---|---:|
| Etkin E verimi farklÄ± (oracle E=1.00, suite E=0.875) | 34 | SUITE_HATASI | EMNÄ°YETLÄ°; gereken t yÃ¼ksek | +%14.2857 |

34 SAPMA satÄ±rÄ±nÄ±n tÃ¼mÃ¼ `required_thickness`; MAWP satÄ±rlarÄ± eÅŸleÅŸir. AynÄ± fark 34 vaka boyunca sabit olduÄŸundan tek kÃ¶k neden etkin E'dir. Bu vaka kÃ¼mesinde suite gereken kalÄ±nlÄ±ÄŸÄ± dÃ¼ÅŸÃ¼rmÃ¼yor ve MAWP'yi yÃ¼kseltmiyor.

## BaÄŸÄ±msÄ±z el hesabÄ±

ASME VIII-1 UG-32(f): `t = P R / (2 S E - 0.2 P)`, `R=D_i/2`; nominal talep korozyon payÄ± `CA` varsa ayrÄ±ca deÄŸerlendirilir. Buradaki SAPMA temsilcilerinde `CA=0`, mill tol=0, `D_i=D`, `S=138 MPa`; ortak `E=1` olduÄŸundan `t_oracle=P(D/2)/(276-0.2P)`. Suite'in efektif `E=.875` kullanmasÄ± paydadaki `2SE` terimini `241.5` yapar.

| Temsilci | R mm | P MPa | S MPa | E | CA / mill tol | t(E=1) mm | t(E=.875) mm | MAWP gÃ¶zlemi MPa |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| grid-D300-P0.1 | 150 | 0.1 | 138 | 1 / .875 | 0 / 0% | 0.054352 | 0.062116 | 42.7907 |
| grid-D300-P20 | 150 | 20 | 138 | 1 / .875 | 0 / 0% | 11.029412 | 12.605042 | 42.7907 |

Hesap kontrolÃ¼: ilk Ã¶rnek oracle `15/(276-.02)=0.0543518 mm`; suite `15/(241.5-.02)=0.0621163 mm`. Ä°kinci Ã¶rnek oracle `3000/(276-4)=11.0294 mm`; suite `3000/(241.5-4)=12.6050 mm`. Her ikisinde baÄŸÄ±l fark `(t_suite/t_oracle-1)*100 = 14.2857%`. MAWP nominal 24 mm Ã¼zerinden suite ve oracle'da aynÄ±; 300 mm Ã§ap iÃ§in `2*138*24/(150+0.2*24)=42.7907 MPa`.

## Kod kanÄ±tÄ± ve karar

Suite `calculate_head_thickness` iÃ§inde `design_code.py:477-481` eÅŸleÅŸen weld kaydÄ±ndan `E = w.joint_efficiency` atÄ±yor; sonrasÄ±nda `design_code.py:533` bu E'yi UG-32(f) fonksiyonuna veriyor. `formulas.py:252-286` paydada `2*S*E - 0.2*P` kullanÄ±yor. MAWP kolu `design_code.py:753-755` aynÄ± kaynak kaydÄ±nÄ± kullanÄ±p `formulas.py:394-426` ile ters Ã§Ã¶zÃ¼m yapÄ±yor. Bu durumda suite'in kendi kalÄ±nlÄ±k ve MAWP sonuÃ§larÄ± birbiriyle tutarlÄ±.

Varyant Ã¼reticisi `variants.py:6-21` varsayÄ±lan `efficiency=1.0` iken kaynaÄŸÄ± deÄŸiÅŸtirmiyor. Oracle `oracle.py:7-12` ise `values()` iÃ§inde kaynak verimini Ã§Ã¶zse de kampanya referansÄ±nÄ±n gÃ¶zlenen deÄŸeri her SAPMA'da E=1 hesabÄ±na karÅŸÄ±lÄ±k geliyor. `grid-D300-P0.1` gibi temsilcilerde test verisi weld E'si 0.875 olduÄŸundan, oracle kÄ±yaslamasÄ± yanlÄ±ÅŸ girdiyi kullanmÄ±ÅŸ; SUITE_HATASI kararÄ± bu yÃ¼zden deÄŸil, SAPMA'nÄ±n suiteten kaynaklandÄ±ÄŸÄ± iddiasÄ± bakÄ±mÄ±ndan deÄŸildir.

Daha doÄŸru sÄ±nÄ±flama: ham SAPMA etiketi **ORACLE_HATASI**. Oracle E'yi suite ile aynÄ± weld kaydÄ±ndan almalÄ±dÄ±r; dÃ¼zeltilince 34 kalÄ±nlÄ±k satÄ±rÄ± Ã¶rtÃ¼ÅŸÃ¼r. DÃ¼zeltme Ã¶nerisi: `oracle.values` iÃ§inde kaynak kaydÄ±nÄ±n gerÃ§ekten eÅŸleÅŸen anahtarÄ± ve `joint_efficiency` alanÄ±nÄ± okuyup, sonuÃ§ta kullanÄ±lan E'yi aÃ§Ä±kÃ§a kaydetmek; `eff-0.85` temsilcisinde suite/oracle ikilisini baÄŸÄ±msÄ±z karÅŸÄ±laÅŸtÄ±rmak. Suite formÃ¼lÃ¼ ve satÄ±r dÃ¼zeyindeki uygulama UG-32(f) ile uyumlu.

## HÃœKÃœM

HÃœKÃœM: suite_hatasÄ±=0 (emniyetsiz=0) Â· oracle_hatasÄ±=34 Â· formÃ¼lasyon=0

