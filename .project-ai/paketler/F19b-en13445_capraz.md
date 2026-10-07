# PAKET F19b — en13445 capraz: katalogla kıyası tamamla

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · Dalga: 1b · Yürütücü: codex:yaz · 2026-10-07
> Mod: yaz → ≤15 satır rapor

## Durum
Bu ailenin ilk turu (`.project-ai/paketler/F19-en13445_capraz.md` paketi, raporu `F19-en13445_capraz.RAPOR.md`) KISMİ kaldı:
suite sonuç satırları bulunamadı veya girdiler eksik olduğu için BLOCKED alındı, sayısal kıyas çoğunlukla
yapılamadı. Şimdi elinde sonuç kataloğu var:
- `pressure-vessel-suite/tools/campaign/RESULT_CATALOG.md`: her calculation_type için tetikleyen girdiler,
  zorunlu alanlar, intermediate_values adları ve durum anlamları.
- `pressure-vessel-suite/tools/campaign/examples.py`: her tip için BLOCKED olmayan çalışan örnek proje.

## Görev
1. Önce kendi önceki çıktını oku: `tools/campaign/families/f19_en13445_capraz/` ve
   `docs/validation/campaign-2026-10/F19-en13445_capraz.md`. Orijinal paketteki hedefler, varyant ekseni ve
   oracle dayanağı geçerlidir.
2. Varyantları katalogdaki doğru girdilerle yeniden kur. `examples.py` örneklerini taban al.
   Sonuçları doğru `calculation_type` ve `intermediate_values` adlarıyla çek.
3. Oracle'ını gerekiyorsa düzelt ve yeniden koştur. `results.json` ve rapor dosyasını **güncelle**,
   eski "bulunamadı" ifadelerini kaldır.
4. Hedef: sayısal kıyaslanan (DOĞRULANDI / FORMÜLASYON_FARKI / SAPMA) vaka sayısı ≥20. Bu
   ulaşılamıyorsa nedenini kataloğa dayanarak açıkla. Yayınlanmış vakaları (`sources-K*.md`) mümkün
   olduğunca gerçek API vakası olarak koştur.

## Temiz oda (aynen geçerli)
Oracle'ı Kod formülünden kendin yaz. `packages/code-*`, `nozzles`, `supports`, `external-pressure`,
`mdmt`, `flanges`, `calc-core` implementasyonlarını OKUMA. Katalog ve examples serbesttir.

## Kapsam
Yalnızca şunlara yaz: `pressure-vessel-suite/tools/campaign/families/f19_en13445_capraz/` ve
`pressure-vessel-suite/docs/validation/campaign-2026-10/F19-en13445_capraz.md`. Harness, katalog ve suite koduna
dokunma. Pytest kullanacaksan `--basetemp` ile sistem TEMP dizinini ver; worktree içine
`.pytest-tmp` açma.

## Kabul
`python -m tools.campaign.families.f19_en13445_capraz.run` hatasız biter. Raporda yeni etiket dağılımı, SAPMA
tablosu (yön: emniyetsiz/emniyetli) ve temiz oda beyanı bulunur.
