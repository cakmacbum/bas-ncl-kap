# A2 Denetim — alan anlatımı G1+G2 (DeepSeek denetler, Gemini yazmıştı)

Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME. Yalnız oku ve rapor yaz.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-G1.html` ve `parca-G2.html`, sitedeki girdi alanlarını 2-3 cümleyle anlatan kılavuz bölümleri (Adım 1, 2, geometri 3.1-3.5). Gerçeği kaynak koddan kontrol et: `pressure-vessel-suite/apps/web-ui/src/pages.tsx`, `types.ts`, `store.ts`, `vesselPresets.ts`, ayrıca `pressure-vessel-suite/packages/*/src` (alanın hesaba etkisi) ve `pressure-vessel-suite/docs/kilavuz2/alan-envanteri.json`.
1. **Yanlış anlatım:** Alanın anlamı, birimi, varsayılanı, seçenekleri kodla uyuşmuyor mu? Hesaba etkisi yanlış mı (ör. "bu değeri artırırsanız kalınlık azalır" gibi ters iddia)?
2. **Uydurma/emin olunmayan sayı:** Standartlardan tipik değer verilmiş ve kaynaksız mı? (telifli veri/kural K6 ihlali olabilir)
3. **Tutarsızlık:** Aynı alan iki yerde farklı anlatılmış mı? Aynı kavram farklı adla geçiyor mu?
4. **Anlaşılırlık:** Başlangıç düzeyi için karmaşık/jargonlu 10 en kötü cümle (alıntı + sade hâli).
## Çıktı
`.project-ai/paketler/A2-denetim-alan-12.DONUS.md`: ≤45 satır, önem sırasıyla (KRİTİK/ORTA/DÜŞÜK), her maddede dosya (G1/G2) + `<dt>` etiketi + sorun + doğru bilgi + kodda hangi dosya/satırdan doğruladığın. İlk satır: `A2 denetim-alan-12 — TAMAM | KISMİ`.
