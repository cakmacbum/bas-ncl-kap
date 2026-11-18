# M1 Marka alanı: yeni simge + "Yusuf Sağlamcı tarafından oluşturuldu"

Mod: yaz
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/apps/web-ui/`.

## KESİN KURALLAR
- Kabuk komutu çalıştırma (headless). Yalnız dosya okuma/arama/yazma/düzenleme.
- Yalnız şu dosyalara dokun: `src/App.tsx` (yalnız `<div className="brand">…</div>` bloğu), `src/workspace.css` (yalnız `.brand*` kuralları), yeni `src/assets/brand-mark.svg` (ya da `public/brand-mark.svg`), `public/favicon.svg` (yeni), `index.html` (yalnız favicon `<link>`). Hesap/domain/test koduna dokunma.

## Mevcut durum
`App.tsx` ~65-71: `.brand` bloğu = `.brand__mark` (CSS ile çizilmiş boş dikdörtgen kutu, 30x38) + `.brand__name` "Basınçlı Kap Suite" + `.brand__sub` "MÜHENDİSLİK ÇALIŞMA ALANI". Stil: `workspace.css` satır 6-11 (+ mobil 161-162). Alan 252px genişlik, 80px yükseklik; koyu zemin (`--nav-bg`), vurgu rengi `var(--accent)`, metin `var(--nav-text)`, soluk `var(--nav-dim)`.

## Görev
1. **Simge tasarla (SVG, kendin çiz):** basınçlı kabı simgeleyen sade, modern, tek renk + vurgu rengi bir logo: yatay ya da dikey silindirik kap, elipsoidal (bombeli) uçlar, üstte bir nozul, altta iki eyer/ayak. Çizgi tabanlı (stroke) teknik-çizim hissi; `viewBox="0 0 48 48"`; renkler `currentColor` (gövde) ve `var(--accent)` (iç vurgu/nozul) kullan ki tema ile uyumlu olsun; 30-40px'te net okunmalı. Ayrıca aynı çizimin bağımsız hâlini `public/favicon.svg` olarak yaz (sabit renk: gövde `#E8EEF5`, vurgu `#F59E0B`, koyu yuvarlatılmış kare zemin `#0F172A`) ve `index.html` `<head>` içine `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />` ekle (zaten bir favicon bağlantısı varsa değiştir).
2. **Marka bloğu:** `.brand__mark` boş kutusunu bu SVG ile değiştir (satır içi `<svg aria-hidden="true">` kullan; görsel dosya import'una ihtiyaç bırakma). `brand__sub` altına yeni bir satır ekle: `<div className="brand__by">Yusuf Sağlamcı tarafından oluşturuldu</div>`. Metni AYNEN bu yaz.
3. **CSS (`workspace.css`):** `.brand__by` = küçük (9.5-10px), `var(--nav-dim)`, normal harf (büyük harfe çevirme), `margin-top: 3px`, `line-height: 1.25`, tek satırda sığmazsa en çok 2 satıra sarsın, taşma olmasın. Marka bloğu 80px yüksekliğe sığmalı (üç satır metin + boşluk). Eski `.brand__mark` kurallarını (kutu çerçevesi, `::after`) yeni SVG ile çakışmayacak şekilde sadeleştir (genişlik/yükseklik 36px, çerçeve yok, `flex: none`). Mobil kuralı (satır 161-172; ≤ küçük ekranda `.brand` gizli) bozulmasın.
4. Erişilebilirlik: logo süs olduğu için `aria-hidden`; metin kontrastı koyu zeminde okunur olsun.

## Çıktı
Değişiklikleri yap, sonra `.project-ai/paketler/M1-marka-imza.RAPOR.md` yaz (≤10 satır): ilk satır `M1 marka-imza - TAMAM | KISMİ | BAŞARISIZ`; değişen dosyalar; SVG'nin kısa tarifi; çalıştırılmadı.
