# Eksikler ve açık konular — 2026-11-06
Öncelik: 🔴 emniyet/doğruluk · 🟠 kapsam boşluğu · 🟡 iyileştirme · ⚪ Yusuf kararı/verisi

## 🔴 Emniyet / doğruluk
- **EN elipsoidal bombe** — E06 ile main'de DÜZELDİ (2:1 örnek: 1,84 → 4,21 mm). Canlı sitede hâlâ eski hal — canlıya alma bekliyor.
- **Kampanya 2026-10 çıktıları geçersiz** — tutarsız geometri (bombe 800 / gövde 1000, ayak 600) ile üretildi; yeniden koşulmalı.
- **EN formülleri bellekten yazıldı** (lisanslı metin yok, hepsi verified=False → en fazla REVIEW_REQUIRED). En zayıflar:
  E02 koni küçük uç τ/β_H · E03 β polinom katsayıları, eb'deki 111 ve 0,825 · E04 pnömatik formül biçimi, çok malzemede fa/fT seçimi,
  döküm bölenleri (1,9/3/1,33), Tablo 5.6-1 test alt grupları, hidrotestte Pd/PS · E06 7.5.4 katsayıları ve K aralığı.
  → EN 13445-3 metni ya da çözülmüş örnekle karşılaştırılmalı.

## 🟠 Kapsam boşlukları
- EN: dış basınç (Part 8), nozul takviyesi → E05. Flanş, yorulma, yük kombinasyonu → FUTURE.
- EN: bükümlü koni birleşimi (7.6.7), koni–bombe birleşimi, cıvatalı düz kapak (10.5), koni MAWP'ye birleşim sınırı katılmadı.
- EN: test durumunda bileşen bazında f_test gerilme kontrolü (statik kafa dahil) yok; NDT kapsamı ↔ test grubu uyumu ve test grubu 4 kısıtları yok.
- EN torisferik: taç/hamut ayrı kalınlık yok; östenitik soğuk sıvama bayrağı yok; Rp0,2/T sıcaklık eğrisinden okunmuyor.
- G01: bileşen sırası tanımsızken zincir kuralları atlanıyor; nozul yerleşim sınırı ve LEG_PROFILE_INVALID API'de yok.
- Arayüz formu olmayan alanlar: koni girişi, EN pnömatik k katsayısı, malzeme grubu/uzama A/Rp1,0, kaynak test grubu.
- Hidrotest (H01): σ ≤ Sy normatif değil; Sy sıcaklıktan bağımsız; yatay kapta koni/nozul/flanş test gerilmesi yok; dikey kabın yatay atölye testi yok.
- BOM: eyer kanatları düz plaka sayılıyor, ankraj delikleri düşülmüyor (kütle hafif düşük).
- İmalat resmi: nozul boynu gövdede delik açmıyor, kesit taraması yok, etek çizilmiyor.
- FEA: yalnız eksenel simetrik (eksen dışı nozul, destek, dış yük yok); düz kapak köşesi tekil.

## ⚪ Yusuf'un verisi / kararı bekleyenler
- Zick K katsayıları (Moss PVDM / Zick 1951) — tablo boş.
- WRC 537 eğri katsayıları (lisanslı bülten) — boş, BLOCKED.
- ASME Tablo 1-5.2 (Δ) — boşsa Δ=0 (güvenli taraf).
- EN 13445-3 metni / çözülmüş örnek (yukarıdaki bellekten ifadeler için).
- Hidrotest gerilme sınırı: σ ≤ Sy mi, 0,9·Sy mi?
- agy için settings.json izin kuralı (açılırsa test/tarama agy'ye döner).
- Canlıya alma onayı (E06 sonrası).
- `~/.orkestra-wt/BASINCLI-KAP` altında izni kilitli 4 boş klasör (yönetici PowerShell ile silinebilir).
- Disk: 465 GB C: neredeyse dolu — ne kapladığının dökümü istenirse çıkarılır.

## Ertelenenler (FUTURE)
P14 3D CalculiX sunucusu · CFD (OpenFOAM) · rüzgâr/deprem (ASCE 7 / EN 1991) · EN flanş/yorulma/yük kombinasyonu.
