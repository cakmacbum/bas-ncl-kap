# Calculation Coverage Matrix

> Bu matris, V1 sürümünde hangi hesapların **var**, hangilerinin **sonra** ekleneceğini ve
> hangilerinin **kapsam dışı** olduğunu gösterir. Proje başlangıcında kilitlenir; değişiklik
> tarihi ve gerekçesiyle birlikte revize edilir.

## Standart destek durumu

| Feature | ASME VIII-1 | EN 13445 + PED | V1 |
|---|---|---|---|
| Cylindrical shell — internal pressure | Yes | Yes | **Yes** |
| Elliptical head (2:1) | Yes | Yes | **Yes** |
| Torispherical head | Yes | Yes | **Yes** |
| Hemispherical head | Yes | Yes | **Yes** |
| MAWP (per-component + global) | Yes | Yes | **Yes** |
| Hydrostatic test pressure | Yes | Yes | **Yes** |
| Nozzle reinforcement (area replacement) | Yes | Yes | **Yes** |
| Corrosion allowance | Yes | Yes | **Yes** |
| Negative mill tolerance | Yes | Yes | **Yes** |
| Forming thinning | Yes | Yes | **Yes** |
| Joint efficiency / weld joint factor | Yes | Yes | **Yes** |
| External pressure / vacuum | Yes | Yes | **Yes** ✅ Faz 5 |
| Flange design | Yes | Yes | **Yes** ✅ Faz 5 |
| Support / saddle design | Yes | Yes | **Yes** ✅ Faz 5 |
| FEA integration | N/A | N/A | **Yes** ✅ Faz 5 (iskelet) |
| Fatigue analysis | Yes | Yes | No — Later |
| Wind / seismic loads | N/A | Yes | No — Later |
| Flat covers / blind flanges | Yes | Yes | No — Later |
| Conical sections | Yes | Yes | No — Later |
| Nozzle external loads (forces/moments) | Yes | Yes | No — Later |
| Creep / high-temperature | Yes | Yes | No — Later |

## PED / CE kapsamı (V1)

| Feature | Durum |
|---|---|
| PED classification engine (SEP → Cat IV) | **Yes** ✅ Faz 4 |
| ESR matrix | **Yes** ✅ Faz 4 |
| EU Declaration of Conformity | **Yes** ✅ Faz 4 |
| Nameplate generation | **Yes** ✅ Faz 4 |
| Module mapping (A, A2, B+D, …) | **Yes** ✅ Faz 4 |
| Risk analysis module | **Yes** ✅ Faz 4 |
| Technical file generation | **Yes** ✅ Faz 4 |

## EN 13445 rotası (V1)

| Feature | Durum |
|---|---|
| EN13445DesignCode (shell + head) | **Yes** ✅ Faz 4 |
| EN 13445-3 formülleri (5.4.2, 5.5.2-5.5.4, 10.2) | **Yes** ✅ Faz 4 |
| PED test basıncı (1.25× / 1.43×) | **Yes** ✅ Faz 4 |
| StandardPack modeli + manifest JSON | **Yes** ✅ Faz 4 |

## Faz 5 ek paketler

| Paket | Açıklama | Test |
|---|---|---|
| `external-pressure/` | UG-28 mantığı — dış basınç + vakum stabilite | 12 test ✅ |
| `flanges/` | Appendix 2 moment + gerilme kontrolleri | 12 test ✅ |
| `supports/` | Zick analizi (saddle) + skirt temeli | 14 test ✅ |
| `fea/` | CAD→mesh→solver→linearization→acceptance (iskelet) | 9 test ✅ |

## V1 kapsam notları

- **Tasarım rotası:** Backend ASME VIII-1 veya EN 13445 motorunu seçebilir. EN rotası aktif
  olmakla birlikte bazı modüller henüz kapsam dışıdır ve `REVIEW_REQUIRED`/`NOT_CALCULATED`
  dönebilir; UI’da EN seçimi uyarı ile sunulur.
- **Malzeme:** Manuel giriş (allowable stress, yield, tensile). Otomatik malzeme veritabanı yok.
- **Nozul:** Radyal nozullar, area-replacement yöntemi. Manşon, muf, manway ve flanşlı nozul tipleri.
- **Kap tipi:** Sabit, metalik, ateşle temas etmeyen, tek basınç odası.
- **Yön:** Yatay veya dikey.
- **Sıvı hesabı:** Statik sıvı yüksekliği V1'de yok (Later).
- **FEA:** İskelet modülü — çözücü kurulu değilse REVIEW_REQUIRED modu, sahte PASS üretmez.

---

*Oluşturma tarihi: 2026-07-19 · Revizyon: 2.0 — Faz 4/5 tamamlanmasına göre güncellendi (2026-07-24)*
