# UI Design Notes — Basınçlı Kap Suite

## 2026-09-16 — Mühendislik çalışma alanı yenilemesi

Güncel sunum katmanı `apps/web-ui/src/workspace.css` dosyasındadır ve temel
`theme.css` dosyasından sonra yüklenir. Aşağıdaki eski palet notları önceki
tasarımın kaydıdır; güncel vurgu açık temada #126d67, koyu temada #66c5bc'dir.

- Lacivert gezinme alanı, açık çalışma yüzeyi ve IBM Plex Sans/Mono tipografisi.
- Varsayılan açık tema; mevcut tema düğmesiyle koyu görünüm korunur.
- Proje girişinde mevcut VesselSchematic bileşeni ve gerçek proje girdileriyle
  teknik önizleme. Önizleme bir hesap onayı veya imalat çizimi olarak sunulmaz.
- Altı adımlı hesap akışı korunur. Gezilen adımlar başarı işareti almaz;
  etkin adım `aria-current` ile belirtilir.
- Hesap hataları, eksik veri durumları, boş sonuç açıklamaları ve madde
  referansları mevcut bileşenlerden gösterilmeye devam eder.
- 1200 px altında proje özeti tek sütuna, 760 px altında gezinme yatay şeride
  geçer. Klavye için içeriğe geç bağlantısı ve azaltılmış hareket desteği vardır.
- Hesap motoru, API, proje veri modeli ve CAD geometri fonksiyonları değişmedi.

Doğrulama: TypeScript ve Vite üretim derlemesi başarılı; tam Python test
koşusunda 567 test geçti, 1 test atlandı. Bağlı tarayıcı
bulunmadığı için gerçek ekran boyutlarında görsel kontrol yapılmadı.

## Tasarım Yönü: Refined Minimalism / Precision

Basınçlı Kap Suite, bir mühendislik/teknik SaaS aracıdır (PV Elite/COMPRESS muadili). Kullanıcılar mühendisler, teknik ressamlar ve basınçlı kap tasarımcılarıdır. Arayüz, veri-yoğun, hassas ve profesyonel olmalıdır.

### Temel İlkeler

1. **Netlik (Clarity)**: Her bilgi net bir hiyerarşi ile sunulmalı. Kullanıcı hangi değerin ne anlama geldiğini hızlıca anlamalı.
2. **Hiyerarşi (Hierarchy)**: Kritik bilgiler (PASS/FAIL, MAWP, governing bileşen) görsel olarak öne çıkmalı.
3. **Erişilebilirlik (Accessibility)**: WCAG 2.1 AA uyumu (kontrast ≥ 4.5:1), klavye navigasyonu, ekran okuyucu desteği.
4. **Tutarlılık (Consistency)**: Mevcut token seti (IBM Plex Sans/Mono, koyu tema ağırlıklı) korunmalı, yeni bileşenler aynı tasarım dilini kullanmalı.

### Renk Paleti

Mevcut palet (`theme.css`) korunur ve genişletilir:

#### Temel Renkler (Koyu Tema)
- `--bg: #0d1219` — Ana arka plan (koyu lacivert)
- `--panel: #131b26` — Panel arka planı
- `--panel-2: #182231` — İkincil panel
- `--panel-raised: #1c2836` — Yükseltilmiş panel
- `--text: #e6edf5` — Ana metin rengi
- `--text-dim: #93a4b8` — Soluk metin
- `--text-faint: #5f7189` — Çok soluk metin

#### Vurgu Renkleri
- `--accent: #f2a13d` — Birincil vurgu (amber)
- `--accent-dim: #6b4d24` — Soluk vurgu
- `--accent-glow: rgba(242, 161, 61, 0.14)` — Vurgu parıltısı

#### Durum Renkleri
- `--pass: #37c98b` — Başarılı (yeşil)
- `--fail: #ef5a63` — Başarısız (kırmızı)
- `--review: #f2a13d` — İnceleme gerekli (amber)
- `--nc: #7d8ea3` — Kapsam dışı (gri)
- `--scope: #4aa8e0` — Kapsam (mavi)

#### Yeni Durum Renkleri (Eklenecek)
- `--blocked: #8b5cf6` — Engelli durum (mor) — hem "Veri Engelli (lisans)" hem "Girdi Eksik" için

#### Temel Renkler (Açık Tema)
- `--bg: #eef1f5` — Ana arka plan (açık gri)
- `--panel: #ffffff` — Panel arka planı
- `--text: #16202c` — Ana metin rengi
- `--text-dim: #3a4a5c` — Soluk metin (AA 4.5:1 için koyulaştırıldı)
- `--accent: #b56815` — Birincil vurgu (koyulaştırıldı)
- `--pass: #0f7a4a` — Başarılı (koyulaştırıldı)
- `--fail: #b82e36` — Başarısız (koyulaştırıldı)
- `--blocked: #6d28d9` — Engelli durum (koyulaştırıldı)

### Tipografi

Mevcut tipografi ölçeği korunur:

#### Font Ailesi
- `--font-sans: "IBM Plex Sans", system-ui, sans-serif` — Ana metin
- `--font-mono: "IBM Plex Mono", ui-monospace, monospace` — Teknik metin, kod, sayılar

#### Tipografi Ölçeği (8 Kademe)
- `--fs-2xs: 11px` — Rozet, meta, alt-bilgi
- `--fs-xs: 12px` — Etiket, birim
- `--fs-sm: 13px` — Panel başlığı, buton, tablo, girdi
- `--fs-base: 14px` — Gövde metin
- `--fs-md: 16px` — Alt başlık, vurgu metin
- `--fs-lg: 20px` — Mobil sayfa başlığı
- `--fs-xl: 26px` — Sayfa başlığı, KPI değeri
- `--fs-2xl: 32px` — Hero / büyük KPI

#### Satır Yüksekliği
- `--lh-heading: 1.2` — Başlıklar
- `--lh-body: 1.5` — Gövde metin
- `--lh-mono: 1.45` — Mono / teknik metin

#### Harf Aralığı
- `--ls-heading: -0.01em` — Başlıklar (hafif sikitleştirme)
- `--ls-body: 0` — Gövde (doğal)
- `--ls-mono: -0.015em` — Mono (hafif negatif tracking)

### Gölgeler

İki katmanlı gölge sistemi (üst highlight + yumuşak drop):
- `--shadow` — Ana gölge
- `--shadow-sm` — Küçük gölge
- `--shadow-card` — Kart gölgesi

### Mikro-Etkileşimler
- `--dur: 0.18s` — Geçiş süresi
- `--ease: cubic-bezier(0.25, 0.46, 0.45, 0.94)` — Geçiş eğrisi

### Durum Gösterimi

Durumlar tek renkle gösterilmez: renk + ikon + metin birlikte kullanılır.

#### Badge Sınıfları
- `.badge--pass` — Başarılı (yeşil + onay ikonu + "PASS")
- `.badge--fail` — Başarısız (kırmızı + X ikonu + "FAIL")
- `.badge--review` — İnceleme gerekli (amber + uyarı ikonu + "REVIEW")
- `.badge--nc` — Kapsam dışı (gri + dışlama ikonu + "NC")
- `.badge--scope` — Kapsam (mavi + bilgi ikonu + "SCOPE")
- `.badge--blocked` — Engelli (mor + kilit ikonu + "BLOCKED") — YENİ

#### Erişilebilirlik Gereksinimleri
- Kontrast oranı ≥ 4.5:1 (WCAG 2.1 AA)
- Focus ring (2px solid accent, 2px offset)
- Klavye navigasyonu (Tab, Enter, Space)
- Ekran okuyucu desteği (aria-label, role="button")
- Reduced motion desteği (prefers-reduced-motion)

### Responsive Tasarım

Breakpoint'ler:
- 375px — Mobil
- 768px — Tablet
- 1440px — Masaüstü

Yatay kaydırma yok, içerik viewport genişliğine sığmalı.

### Anti-Pattern (Kaçınılacaklar)
- Emoji ikon kullanma (SVG ikon kullan)
- Layout kayması (hover'da transform: scale kullanma)
- Tek renkli durum gösterimi
- Düşük kontrast (< 4.5:1)
- Yatay kaydırma
- Focus ring eksikliği

### Uygulama Notları

1. Mevcut `theme.css` dosyası 1186 satır, IBM Plex Sans/Mono, oturmuş token seti. Bu tasarım dilini YIKMA — genişlet.
2. Yeni token'lar mevcut desenlere uygun eklenmeli.
3. Badge sınıfları mevcut `.badge--*` desenini taklit etmeli.
4. SVG ikonlar inline olarak eklenmeli (emoji kullanılmamalı).
5. Responsive grid sistemi mevcut `.app` grid yapısına uygun olmalı.

---

*Bu notlar, Basınçlı Kap Suite Faz A-UI çalışması için hazırlanmıştır. Mevcut tasarım dilini koruyarak yeni özellikleri entegre etmeyi hedefler.*
