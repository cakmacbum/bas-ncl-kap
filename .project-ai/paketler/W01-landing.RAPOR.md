# RAPOR W01-landing

> Yürütücü: Codex gpt-6-luna·medium (yaz) · 2026-10-09 20:11
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/W01 · Dal: ork/W01 · Taban: 048b039

W01 English landing page — TAMAM  
Dosyalar: `pressure-vessel-suite/apps/landing/` altındaki 11 dosya · Teknik çizim estetiği, mobil düzen ve açık mühendislik sınırlamaları eklendi.  
Test: `node --check main.js` → geçti; yasaklı ifade, CTA ve Vercel ayarı kontrolleri → geçti.  
Sözleşme: uyuldu · Yalnızca Kapsam dosyaları değiştirildi; commit atılmadı.  
Açık soru / risk: `APP_URL` yayına almadan önce gerçek uygulama adresiyle değiştirilmeli.
```
 pressure-vessel-suite/apps/landing/404.html        |  1 +
 pressure-vessel-suite/apps/landing/README.md       |  7 ++++++
 .../apps/landing/assets/favicon.svg                |  1 +
 pressure-vessel-suite/apps/landing/assets/og.svg   |  1 +
 pressure-vessel-suite/apps/landing/index.html      | 25 ++++++++++++++++++++++
 pressure-vessel-suite/apps/landing/main.js         | 25 ++++++++++++++++++++++
 pressure-vessel-suite/apps/landing/privacy.html    |  1 +
 pressure-vessel-suite/apps/landing/robots.txt      |  2 ++
 pressure-vessel-suite/apps/landing/styles.css      |  5 +++++
 pressure-vessel-suite/apps/landing/terms.html      |  1 +
 pressure-vessel-suite/apps/landing/vercel.json     | 15 +++++++++++++
 11 files changed, 84 insertions(+)
```
