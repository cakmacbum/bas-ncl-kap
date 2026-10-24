# Teknik işler planı (Render hariç) — Gemini yazar, Claude şef (2026-10-24)

Rol: Claude = şef (böler, sözleşme yazar, bağımsız test/oracle'ı kendi hazırlar, diff'i inceler, ana ağaçta tam paketi koşturur, commit eder). Gemini = kodu yazar.
Engel: Gemini CLI kişisel hesapla kapalı (IneligibleTierError, Antigravity'ye taşındı) → şef doğrudan çağıramaz. Yol: her iş `G<NN>-*.md` kendi başına yeterli paket (MiMo akışı), Yusuf Gemini/Antigravity'de çalıştırır, cevap `G<NN>.DONUS.md` / diff olarak döner.
Kural: çekirdek hesap işlerinde (G02, G04–G09) bağımsız beklenen değerleri ŞEF yazar ve pakete koyar; Gemini bu sayıları görüp testi geçecek kodu yazar. Telifli tablo/metin yok (K6), uydurma değer yok (K4).

| # | İş | Büyüklük | Gemini'ye uygun mu |
|---|---|---|---|
| G01 | Nozul E1: dikiş geçişini domain'den çıkar | küçük | evet |
| G02 | Hidrotest: bileşen bazlı test gerilmesi kontrolü | orta | evet (şef formülü yazar) |
| G03 | Playwright e2e: 3 temel tank UI'dan | orta | evet, en uygun |
| G04 | EN 13445 flanş tetikleme | orta | evet |
| G05 | EN 13445 yük kombinasyonları | orta-büyük | evet |
| G06 | EN 13445 yorulma | büyük | kapsam kararı sonra |
| G07 | Saddle OUT OF SCOPE koşulu (ağırlık merkezi) | küçük | evet |
| G08 | Etek taban halkası / ankraj hesabı | orta | evet (şef formülü yazar) |
| G09 | Tahliye UG-125…136 kapsamı | büyük | bölünür |
| G10 | MDMT coincident ratio otomatik hesabı | orta | evet |
| G11 | Koni arayüz formu | küçük-orta | evet |
| G12 | Ajan worktree temizliği | küçük | şef (Yusuf onayı) |
