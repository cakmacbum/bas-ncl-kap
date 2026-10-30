# Dalga 4 ekleri — F4 (E/ν alanları) + V1 (torisferik hamut doğrulaması)
Yol kuralı: `pressure-vessel-suite/` kökü. Ortak kabul: `cd apps/web-ui && npm test && npm run build` + `python -m pytest tests/unit tests/api tests/faz5 -q`
yeşil; tsconfig.tsbuildinfo commit dışı; commit sonu `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. K4/K6: uydurma değer yok.

## F4 — Malzemeye E ve ν — Sonnet
- `MaterialProperty` (Python domain + `apps/web-ui/src/types.ts`): `elastic_modulus_MPa`, `poisson_ratio` (Optional; E>0, 0<ν<0,5).
  Mevcut malzeme veritabanında (packages/materials veya web-ui data) E değeri zaten varsa onu kullan/eşle, ikinci alan açma.
  Tasarım sıcaklığına bağlı E tablosu bellekten YAZILMAZ; kullanıcı girer, boşsa mevcut varsayım (200 GPa/0,3) + uyarı.
- FEA (`apps/web-ui/src/fea/`): gövde malzemesinin E/ν'sini kullan; bileşen bazında farklı malzeme varsa eleman bazında E/ν
  (`elemComponent` → bileşenin malzemesi). Uyarı yalnız varsayım kullanılan bileşenler için.
- UI: malzeme girişine iki sayı alanı. Test: E iki katına → yer değiştirme yarıya, gerilme (statik belirli) değişmez; ν uyarısı.

## V1 — Torisferik hamut: analitik (P03) vs FEA (P12) — Opus
Sorun: D1000/t10/P=1 MPa torisferik bombede hamut tepe gerilmesi P03 `stress/analyticField.ts` ≈715 MPa, P12 FEA ≈237 MPa.
1. Bağımsız referans A — yayımlanmış elastik sayısal/deneysel sonuç (kaynak künyesi, geometri Rc/D, rk/D, t/D, değer). Web araması
   kullan; künyesi doğrulanamayan sayı kullanma.
2. Bağımsız referans B — eksenel simetrik ince kabuk denklemlerinin (Reissner–Meissner, kesikli meridyen: taç küre + hamut torus +
   silindir, sınırlarda süreklilik) sayısal çözümü, Python (numpy/scipy `solve_bvp` veya transfer matrisi). Yeni dosya
   `tools/verification/torispherical_shell.py` + `tests/unit/test_torispherical_reference.py` (yalnız kendi iç tutarlılığı:
   küre/silindir uzak alan PR/2t, PR/t; kalın-ince sınırında makul).
3. Aynı geometrileri (en az 3: rk/D=0,06/0,10/0,17; t/D=0,01) P12 FEA ve P03 ile koştur (TS tarafında vitest ile tablo üret;
   `apps/web-ui/src/__tests__/feaKnuckleCompare.test.ts`). Karşılaştırma tablosunu
   `docs/validation/torispherical-knuckle.md`'ye yaz: geometri, A, B, FEA, P03, farklar.
4. Karar: FEA, A ve B ile tutarlıysa (≈%10–15) P03 hamut hesabı hatalıdır → P03'te hamutu düzelt (ör. hamut membran değeri yerine
   doğrulanmış yaklaşım; yeni formül kaynaksızsa koyma, bölgeyi "FEA kullanın" + düşük güven olarak işaretle) ve P13 uyarı metnini
   sonuca göre güncelle. FEA tutarsızsa FEA'yı düzeltme — raporla, şef karar verir.
`apps/web-ui/src/fea/` dosyalarına DOKUNMA (F4 paralelde orada çalışıyor) — yalnız oku/çağır.
