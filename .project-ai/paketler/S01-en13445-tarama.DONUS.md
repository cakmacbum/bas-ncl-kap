# S01 DONUS — EN 13445 boşluk taraması (salt okur)

Yollar `pressure-vessel-suite/` köküne göre. EN paketi: `packages/code-en-13445/src/code_en_13445/` = `design_code.py` (772 satır), `formulas.py` (356), `__init__.py`. Başka modül yok (malzeme, kaynak, nozul, dış basınç, destek alt paketi yok).

## 1. EN 13445 kapsam tablosu

Not: `_unsupported_result` (design_code.py:653) `out_of_scope` seçeneğini destekler ama hiçbir çağrı `status="out_of_scope"` vermiyor (grep `status=` yalnız tanımda); yani pratikte EN'de OUT_OF_SCOPE dönen yol yok, hepsi NOT_CALCULATED (flanş/yük/dış basınç/nozul) veya BLOCKED_MISSING_INPUT (yorulma, girdi yoksa).
`verified` bayrağı yok; en yüksek durum "PASS/FAIL + REVIEW_REQUIRED"; bağımsız yayınlanmış EN vakası yok (docs/calculation-coverage.md:75-80, limitations.md:152-155).

| EN 13445 konu | durum | dosya:satır | not |
|---|---|---|---|
| Silindirik gövde, iç basınç, "5.4.2" | VAR (ön kontrol) | formulas.py:18 (`shell_thickness_internal_pressure`), design_code.py:107 (`calculate_shell_thickness`) | Çevresel + boyuna e; f·z - P/2 paydası. z "Tablo 5.4.2-1" yorumu (design_code.py:144) ama z kullanıcı `joint_coefficient`'inden geliyor, tablo kodlanmamış. f elle girilir (K4), EN malzeme tablosu yok |
| Nominal kalınlık (mill tol., incelme, korozyon) | VAR | formulas.py:68 | Madde no kodda yok. Varsayılan %10 tol. sessiz değil, varsayım kaydı |
| Elipsoidal bombe "5.5.2" | VAR (ön kontrol) | formulas.py:107; design_code.py:259, 320 | shape_factor sabit 1.0 (2:1). Yalnız ince-et formülü; K/ham-şekil (d/D) ve bombe Tablo/Şekil kontrolleri yok |
| Torisferik bombe "5.5.3" | KISMİ | formulas.py:142-190; design_code.py:30-60, 327 | Docstring: "Basitleştirilmiş yaklaşım ... karmaşık formül" yani tam EN prosedürü (Q, ek denklemler, kırılma/burkulma kontrolleri) YOK. r varsayılan 0.10 D doğrulanmadı (B-09; limitations.md:152) |
| Yarım küre "5.5.4" | VAR (ön kontrol) | formulas.py:195; design_code.py:337 | |
| MAWP gövde/bombe | VAR (ön kontrol) | formulas.py:262, 291; design_code.py:411-530 | Koni bileşeni: NOT_CALCULATED (calculation-coverage.md:84) |
| Düz kapak | YOK | design_code.py:343 (HeadType.FLAT -> not_calculated) | EN düz kapak maddesi kodda yok; ASME'de var (flat_head_thickness) |
| Konik bölüm | YOK | `calculate_cone_thickness` EN'de tanımlı değil (calculation-coverage.md:85; orchestrator.py:167 çağırır) | hesap hatası kaydı düşer |
| Hidrotest, "EN 13445-5, 10.2 / 10.2.3.3.1" | KISMİ | formulas.py:225 (`ped_test_pressure`, 1.43/1.25); design_code.py:532-635 | fa/ft uygulanmıyor, oran eksik/eşik 1.144 üstü -> REVIEW_REQUIRED (design_code.py:605). Metin lisanslı kaynakla doğrulanmalı (satır 632) |
| Pnömatik test | YOK | taban sınıf (calc-core/code_interface.py:143) NOT_CALCULATED | EN override yok |
| Nozul takviyesi | YOK | design_code.py:636-651 | NOT_CALCULATED "future phase" |
| Dış basınç / vakum, "Part 8" | YOK (NOT_CALCULATED) | design_code.py:681-707 | eğri/veri paketi ve halka stiffener doğrulaması yok; ASME UG-28'e düşmez (iyi) |
| Yük kombinasyonları, "5 / 16" | YOK (NOT_CALCULATED) | design_code.py:709-735 | madde no kodda böyle yazılı, doğrulanmamış |
| Flanş, "11" | YOK (NOT_CALCULATED) | design_code.py:737-747 | |
| Yorulma, "18" | YOK | design_code.py:749-769 | girdi yoksa BLOCKED_MISSING_INPUT, varsa yine NOT_CALCULATED |
| Malzeme veri kapısı (sıcaklık/kalınlık aralığı) | KISMİ | design_code.py:84-105 | yalnız metadata uyuşmazlığı REVIEW_REQUIRED; f değerinin doğruluğunu kanıtlamaz. NOT: docs/calculation-coverage.md:82 "EN'de B-31 uygulanmıyor" diyor, limitations.md:436 "EN B-31 gate eklendi (2026-09-30)" diyor -> doküman çelişkisi |
| MDMT, destekler, kaynak doğrulama (validate_weld/s), nozul çakışması, tahliye | YOK (sessiz) | taban sınıf code_interface.py:71-129 boş liste/NOT_CALCULATED | EN override etmiyor: hiç sonuç satırı üretilmez (calculation-coverage.md:92). En tehlikeli sınıf: "boş = sorun yok" gibi okunabilir |
| check_junctions (koni-silindir birleşimi), check_lifting_lugs | YOK (sessiz) | orchestrator.py:318, 333 getattr ile ->boş | EN'de tanımlı değil |
| EN 13445-2 malzeme, EN 13445-4 imalat, -5 muayene (hidrotest dışı) | YOK | — | EN-5 yalnız 10.2 test basıncı; kaynak sınıfı/muayene oranı -> z eşlemesi (EN-5/EN-3 Bölüm 5 tablo) kodda yok, z kullanıcı girdisi |

## 2. ASME'de olup EN'de olmayan kontroller
Kaynak: `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py` (`calculate_*` / `check_*`):
- calculate_pneumatic_test_pressure (980)
- calculate_nozzle (1095) — takviye alanı
- calculate_flange (1176) — Appendix 2
- calculate_cone_thickness (2243)
- check_nozzle_clashes (1248)
- check_mdmt (1266)
- check_junctions (1417) — koni/silindir birleşimi
- check_supports (1585)
- check_external_pressure (2067) — EN'de sadece NOT_CALCULATED iskeleti var
- check_lifting_lugs (2182)
- düz kapak (calculate_head_thickness içinde FLAT; EN'de NOT_CALCULATED)
- Ayrıca B-31 malzeme kapısı EN'de yalnız metadata düzeyinde; hidrotest bileşen-bazlı kontrol (STATE.md:61, EKSIKLER.md:73) iki tarafta da açık.
Yorulma: ASME'de de `calculate_fatigue` yok (tarama bulgusu değil, kontrol edilmedi: yalnız EN'de var).

## 3. Testler
- tests/faz4/test_faz4_en13445.py: 27 test, 525 satır (formül birim ~10, design_code ~14, pack/clause 4). Tamamı sentetik/iç tutarlılık; yayınlanmış EN vakası yok.
- Diğer dosyalarda EN geçenler: test_faz4_compliance.py (24 test, 4 EN anma), test_compliance_html_escape.py (5/4), tests/api/test_api_smoke.py (7/2), tests/wiring/test_no_ghost_features.py (3/1), tests/wiring/test_ui_parity.py (4/1).
- Dış basınç/yük/flanş/yorulma/nozul için "NOT_CALCULATED döner" testi yalnız nozul (test_nozzle_not_calculated, satır 392). Flanş/yorulma/yük/dış basınç/koni/düz kapak için test görünmedi (isim taraması; içerik tam okunmadı).
- Kampanya: docs/validation/campaign-2026-10/OZET.md:62 F19-en13445_capraz: 26 DOĞRULANDI, 4 KAPSAM_DIŞI (çapraz kıyas, bağımsız yayın değil).

## 4. Mevcut eksik/limitasyon notları
- pressure-vessel-suite/docs/calculation-coverage.md:75-92 (ana matris), :82 B-31 çelişkisi
- pressure-vessel-suite/docs/limitations.md:30 (EN kapsamı dar), :152-155 (B-09 torisferik r), :280, :355 (fa/ft uygulanmıyor), :436 (EN B-31 gate)
- docs/validation/campaign-2026-10/BULGULAR.md:24 ve EKSIKLER.md:16,73 (B-06 flanş/yük/yorulma tetiklenemiyor)
- docs/validation/campaign-2026-10/sources-K4.md:142-144 (EN-3 tam metni/çözümlü örnek ve Bölüm 8 sayısal örneği YOK; UNM background PDF var)
- .project-ai/paketler/P00c-katalog-eksik.RAPOR.md:11
- .project-ai/STATE.md:61 (B-06 açık)
- Kök: eksikler.md:98 (P0-01, eski), :282 (5.11), :426 (Faz D); 20.09.2026-son-eksikler.md:72,96; 24.09.2026-muhendislik-hesap-karsilastirmasi.md:26

## 5. Önerilen paketleme (bağımsız, paralel, yoldaki dosyalar çakışmaz)
Genel kural: madde numarasını yalnızca lisanslı metinden doğrulanmışsa kodla; kaynak (lisanslı EN metni) yoksa paket formülü "REVIEW_REQUIRED" bırakır. Telif nedeniyle EN tabloları/eğrileri Yusuf'tan veya açık kaynaktan (UNM background, sources-K4) gelmeli.

- **E01 — EN sessiz-boşluk kapatma (küçük, S, öncelik 1):** EN'de MDMT/destek/kaynak/nozul çakışması/junction/lifting-lug/pnömatik için açık NOT_CALCULATED sonuç satırları (override), kullanılmayan `out_of_scope` yolunu gerçekten kullanma, B-31 doküman çelişkisini düzeltme. Dosyalar: code-en-13445/design_code.py (yeni override'lar), docs/calculation-coverage.md, tests/faz4/test_faz4_en13445.py (yeni test dosyası önerilir: tests/faz4/test_faz4_en13445_gaps.py). ~120-180 satır.
- **E02 — Konik bölüm + düz kapak (M):** `calculate_cone_thickness`, MAWP cone dalı, FLAT head; ASME'deki emsallerin EN karşılığı, formüller lisanslı kaynakla. Dosyalar: code-en-13445/formulas.py (ekle), design_code.py (calculate_head_thickness:343, calculate_mawp), testler. Kaynak şartı yüksek. ~250 satır.
- **E03 — Torisferik tam prosedür + eliptik K düzeltmesi (M):** formulas.py:142-190'daki "basitleştirilmiş" yaklaşımı gerçek EN prosedürüne taşı, B-09 r varsayılanını netleştir. Dosyalar: formulas.py, design_code.py:30-60,259-345; yalnız bu iki dosya (E02 ile formulas.py'de çakışır -> sıralı veya ayrı fonksiyon bloğu). Kaynak şartı yüksek.
- **E04 — Hidrotest + EN-5 muayene/z eşlemesi (S-M):** fa/ft uygulaması, kaynak sınıfı/muayene oranı -> z tablosu (EN-3 Bölüm 5 / EN-5), pnömatik test. Dosyalar: formulas.py (ped_test_pressure bölümü), design_code.py:532-635, tests. Kaynak: lisanslı metin şart.
- **E05 — EN dış basınç + nozul takviyesi (L, Codex adayı):** en büyük iki eksik. Dış basınç (Part 8) ve nozul takviyesi ayrı yeni modüller (`external_pressure_en.py`, `nozzle_en.py`) olmalı, design_code.py'de yalnız bağlama. Büyük, veri paketi (eğri/Şekil değerleri) gerektirir; önce kaynak/lisans kararı. Flanş (11), yorulma (18), yük kombinasyonları bu paketin ardına bırakılsın: EN'de tam kapsam çok büyük.
Sıra: E01 (hemen, kaynak gerektirmez) -> E04/E02/E03 (kaynak gelince) -> E05.
Tüm paketler design_code.py'ye dokunduğu için entegrasyon sırası şefte; E05 ayrı modüllerde çalışırsa çakışma düşük.
