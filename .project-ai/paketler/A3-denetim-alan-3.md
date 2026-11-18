# A3 Denetim — alan anlatımı G3 (DeepSeek denetler, Gemini yazmıştı)

Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME. Yalnız oku ve rapor yaz.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-G3.html`: "Hesap girdileri" sekmesi (nozul yükleri, nozul ayrıntıları ve küçük açıklık muafiyeti beyanı, flanşlar, destek ayrıntıları, malzeme, kaynak & NDT, BOM, kaldırma kulağı, koni birleşimi) ve Adım 4-6 anlatımı. Kaynak: `pressure-vessel-suite/apps/web-ui/src/pages.tsx`, `types.ts`, `store.ts`, `pressure-vessel-suite/packages/*/src`, `docs/kilavuz2/alan-envanteri.json`.
1. **Yanlış anlatım:** alanın anlamı/birimi/varsayılanı/seçenekleri kodla uyuşmuyor mu? Hesaba etkisi ters/yanlış mı?
2. **Muafiyet beyanı (UG-36(c)(3)) bölümü ÖZEL dikkat:** Üç onay kutusunun (`no_rapid_pressure_fluctuation_confirmed`, `opening_spacing_confirmed`, `welded_attachment_confirmed`) anlatımı `packages/nozzles/src/nozzles/reinforcement.py` içindeki gerçek davranışla uyuşuyor mu? (Üçü de işaretlenmeden muafiyet uygulanmaz; muafiyette bile boyun et kalınlığı kontrolü yapılır; boyut sınırları.) Uyumsuzluk varsa KRİTİK.
3. **Malzeme alanları:** izin verilen gerilme/akma/çekme için sayı verilmiş mi? (verilmemeli, K6) Boş/0 bırakılınca ne olduğu doğru mu?
4. **Adım 4 (sonuçlar):** PASS/FAIL, MAWP, hidrotest anlatımı gerçek sonuç alanlarıyla uyumlu mu (`packages/*/src` ve API şeması)?
5. **Uydurma/emin olunmayan sayı**, tutarsızlık, jargonlu en kötü 10 cümle (alıntı + sade hâli).
## Çıktı
`.project-ai/paketler/A3-denetim-alan-3.DONUS.md`: ≤45 satır, önem sırasıyla (KRİTİK/ORTA/DÜŞÜK), her maddede `<dt>` etiketi + sorun + doğru bilgi + doğruladığın dosya/satır. İlk satır: `A3 denetim-alan-3 — TAMAM | KISMİ`.
