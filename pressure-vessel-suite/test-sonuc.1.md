# 20 tank için basınç ve ayak karşılaştırması

**Çalıştırma:** 26.09.2026 · ASME VIII-1 2025 hesap servisi · 20/20 vaka tamamlandı. Bu oturumda kullanılabilir tarayıcı olmadığı için kullanıcı arayüzü yolu çalıştırılamadı; aynı uygulamanın `/api/projects/{id}/calculate` hesap servisi kullanıldı.

**Sonuç sütunlarının anlamı:** Programın gerçek çıktısı değerleri, her vakayı uygulamanın hesap API'sine gönderip dönen hesap yanıtından alınmıştır; elle yazılmış veya tahmin edilmiş program sonuçları değildir. Bağımsız dış formül hesabı değerleri ise uygulama kodundan bağımsız hesaplanıp kamuya açık teknik kaynaklardaki denklemlerle kontrol edilmiştir. Bunlar ayrı bir ticari yazılımın sonuçları değildir. Her iki tarafta aynı geometri ve tasarım girdileri kullanılmıştır.

## Referans yöntemi ve girdiler

Bağımsız sonuçlar uygulamanın kodunu çağırmadan UG-27(c)(1)/(2) gövde ve UG-32(d) 2:1 elipsoidal bombe formülleriyle hesaplandı. Kaynaklar: [Pressure Vessel Engineering örnek UG-27 ve UG-32 hesabı](https://www.pveng.com/wp-content/uploads/2016/06/ASME9_FEA_Report.pdf), [kamuya açık UG-27/UG-32 formül özeti](https://mechconcepts.tech/asme-viii-1-pressure-vessel-thickness-calculator/) ve [ASME BPVC 2025](https://www.asme.org/codes-standards/bpvc-standards/bpvc-2025).

Sabitler: SA-516 Gr.70; arayüz varsayılanı S=138 MPa; E=1; korozyon payı 2 mm; sac negatif toleransı %12,5; bombe şekillendirme incelmesi 1 mm; çelik yoğunluğu 7850 kg/m³; su 1000 kg/m³; 4 ayak; rüzgâr veya devrilme momenti yok. Çaplar 600–1500 mm, teğet boylar 900–4500 mm, tasarım basınçları 0,5–1,6 MPa. Ayak boruları tank çapına göre 114,3×8, 168,3×10, 219,1×12 veya 273×14 mm seçildi. Ayaklar için su dolu ve boş tank yükü ayrı hesaplandı; eşit ayak paylaşımı W/4 ve boru halka alanı A=π/4·(D²−d²) kullanıldı. Dikey kap ayak yükü dağılımı için [Pressure Vessel Design Handbook](https://electronicsandbooks.com/edt/manual/Publischer/V/Van%20Nostrand%20Reinhold/Pressure%20Vessel%20Design%20Handbook%2C%20H%20Bednar%201981%200442254164%20OCR%20c20140816%20%5B331%5D.pdf) referans alındı.

## 20 vaka çıktısı

| Vaka | D×L (mm) | P (MPa) | Seçilen t gövde/bombe (mm) | Gerekli t gövde (Dış hesap / Program API) (mm) | Gerekli t bombe (Dış hesap / Program API) (mm) | MAWP (Dış hesap / Program API) (MPa) | Boş ayak σ (Dış hesap) (MPa) | Su dolu ayak σ (Dış hesap / Program API) (MPa) | Uygulama ayak durumu |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PV20-01 | 600×900 | 0,5 | 8/8 | 3,539/3,539 | 4,680/4,680 | 1,825/2,709 (+48,4%) | 0,176 | 0,478/0,478 | REVIEW REQUIRED |
| PV20-02 | 600×1200 | 0,8 | 6/6 | 4,294/4,294 | 5,431/5,431 | 1,027/1,813 (+76,5%) | 0,173 | 0,552/0,552 | REVIEW REQUIRED |
| PV20-03 | 600×1500 | 1,2 | 6/8 | 5,303/5,303 | 6,432/6,432 | 1,476/1,813 (+22,9%) | 0,217 | 0,672/0,672 | REVIEW REQUIRED |
| PV20-04 | 600×1800 | 1,6 | 8/8 | 6,315/6,315 | 7,435/7,435 | 1,825/2,709 (+48,4%) | 0,299 | 0,832/0,832 | REVIEW REQUIRED |
| PV20-05 | 800×1200 | 0,5 | 4/6 | 3,954/3,954 | 5,094/5,094 | 0,514/0,685 (+33,2%) | 0,108 | 0,487/0,487 | REVIEW REQUIRED |
| PV20-06 | 800×1600 | 0,8 | 6/8 | 4,958/4,958 | 6,093/6,093 | 1,110/1,365 (+22,9%) | 0,172 | 0,650/0,650 | REVIEW REQUIRED |
| PV20-07 | 800×2000 | 1,2 | 8/8 | 6,302/6,302 | 7,427/7,427 | 1,372/2,041 (+48,8%) | 0,243 | 0,819/0,819 | REVIEW REQUIRED |
| PV20-08 | 800×2400 | 1,6 | 8/10 | 7,650/7,650 | 8,761/8,761 | 1,704/2,041 (+19,8%) | 0,292 | 0,966/0,966 | REVIEW REQUIRED |
| PV20-09 | 1000×1500 | 0,5 | 6/6 | 4,369/4,369 | 5,508/5,508 | 0,618/1,094 (+77,0%) | 0,203 | 0,938/0,938 | REVIEW REQUIRED |
| PV20-10 | 1000×2000 | 0,8 | 6/8 | 5,623/5,623 | 6,756/6,756 | 0,890/1,094 (+23,0%) | 0,267 | 1,193/1,193 | REVIEW REQUIRED |
| PV20-11 | 1000×2500 | 1,2 | 8/10 | 7,301/7,301 | 8,422/8,422 | 1,366/1,638 (+19,9%) | 0,392 | 1,510/1,510 | REVIEW REQUIRED |
| PV20-12 | 1000×3000 | 1,6 | 10/12 | 8,984/8,984 | 10,088/10,088 | 1,841/2,178 (+18,3%) | 0,542 | 1,852/1,852 | REVIEW REQUIRED |
| PV20-13 | 1200×1800 | 0,5 | 6/6 | 4,784/4,784 | 5,922/5,922 | 0,516/0,913 (+77,1%) | 0,185 | 0,989/0,989 | REVIEW REQUIRED |
| PV20-14 | 1200×2400 | 0,8 | 8/8 | 6,288/6,288 | 7,419/7,419 | 0,916/1,367 (+49,2%) | 0,288 | 1,303/1,303 | REVIEW REQUIRED |
| PV20-15 | 1200×3000 | 1,2 | 10/10 | 8,300/8,300 | 9,416/9,416 | 1,317/1,819 (+38,2%) | 0,414 | 1,641/1,641 | REVIEW REQUIRED |
| PV20-16 | 1200×3600 | 1,6 | 12/12 | 10,318/10,318 | 11,415/11,415 | 1,717/2,270 (+32,2%) | 0,562 | 2,001/2,001 | REVIEW REQUIRED |
| PV20-17 | 1500×2250 | 0,5 | 6/8 | 5,406/5,406 | 6,544/6,544 | 0,595/0,732 (+23,0%) | 0,210 | 1,280/1,280 | REVIEW REQUIRED |
| PV20-18 | 1500×3000 | 0,8 | 8/10 | 7,285/7,285 | 8,414/8,414 | 0,914/1,096 (+19,9%) | 0,320 | 1,674/1,674 | REVIEW REQUIRED |
| PV20-19 | 1500×3750 | 1,2 | 10/12 | 9,798/9,798 | 10,908/10,908 | 1,232/1,459 (+18,4%) | 0,454 | 2,091/2,091 | REVIEW REQUIRED |
| PV20-20 | 1500×4500 | 1,6 | 14/14 | 12,320/12,320 | 13,405/13,405 | 1,695/2,181 (+28,7%) | 0,685 | 2,606/2,606 | REVIEW REQUIRED |

## Bulgular

- Programın API yanıtındaki gerekli gövde/bombe kalınlıkları 20/20 vakada bağımsız dış formül hesabıyla aynıdır; fark 0,000 mm.
- Program API yanıtındaki MAWP 20/20 vakada bağımsız dış formül hesabından yüksektir; fazla tahmin %18,3–%77,1. Sonuç izinde uygulama MAWP hesabının nominal etten korozyon payını düşürdüğü, ancak %12,5 sac toleransını ve bombede buna ek olarak 1 mm şekillendirme incelmesini hesaba katmadığı görüldü. Bu set için emniyetsiz yönde sapma vardır.
- Program API yanıtındaki su dolu ayak gerilmesi 20/20 vakada bağımsız W/4/A hesabıyla örtüştü. Uygulama hidrotest yükünü (kap metali + su) ayak kontrolünde kullandı ve boş metal ağırlığını raporladı. Boş tank ayak gerilmesi bağımsız hesaplandı; uygulama boş durum için ayrı ayak gerilme sonucu üretmiyor.
- Ayak sonuçlarının tamamı `REVIEW REQUIRED`; uygulama nihai onay vermiyor. Ankraj, temel yatak basıncı, rüzgâr/deprem ve devrilme momenti bu setin kapsamında değildi.
- Örnek Vaka 01: D=600 mm, L=900 mm, P=0,5 MPa; gereken gövde/bombe nominal etleri 3,539/4,680 mm; seçilen etler 8/8 mm. Referans MAWP 1,825 MPa, uygulama 2,709 MPa (+%48,4). Boş ayak gerilmesi 0,176 MPa, su dolu gerilme 0,478 MPa.

Bu çalışma kamuya açık formüllerle bağımsız sayısal çapraz kontroldür; lisanslı ASME metninden tam uygunluk incelemesi veya yetkin mühendis onayı değildir. 20 proje uygulamanın geçici belleğinde `PV20-01`–`PV20-20` olarak oluşturuldu.


