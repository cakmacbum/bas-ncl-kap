# B05 — EN 13445-3 Madde 9 nozul takviyesi (basınç–alan yöntemi)

Mod: yaz · Motor: agy gemini-3.8-flash-high · Proje kökü: worktree kökü (yollar `pressure-vessel-suite/` ile başlar)

## Amaç
`EN13445DesignCode.calculate_nozzle` şu an NOT_CALCULATED döndürüyor. EN 13445-3 Madde 9 basınç–alan
(pressure–area) yöntemiyle tekil açıklık takviyesini hesapla. ASME UG-37 koduna/paketine ASLA fallback yapma
(`nozzles` paketindeki ASME alan hesabını çağırma; yalnız geometriyi nasıl okuduğunu örnek alabilirsin).

## Kapsam (yalnız bu dosyalara yaz)
1. YENİ `pressure-vessel-suite/packages/code-en-13445/src/code_en_13445/openings.py` — saf fonksiyonlar (float girer/çıkar).
2. `pressure-vessel-suite/packages/code-en-13445/src/code_en_13445/design_code.py` — YALNIZ `calculate_nozzle` metodunun gövdesi (+ hemen altına özel yardımcı). Başka yerine dokunma (paralelde başka paket `check_external_pressure`'ı düzenliyor).
3. YENİ `pressure-vessel-suite/tests/faz4/test_en13445_nozzle_reinforcement.py`.
Dokunma: domain, ASME, `nozzles` paketi, orchestrator, mevcut testler, UI.

## İçerik (formüller bellekten — verified=False)
- Kabul (9.5.2): (Af_s + Af_w)·(f_s − 0,5P) + Af_p·(f_op − 0,5P) + Af_b·(f_ob − 0,5P) ≥ P·(Ap_s + Ap_b + 0,5·Ap_φ)
  f_ob = min(f_b, f_s), f_op = min(f_p, f_s).
- Etkin boylar: gövde l_so = √((2R_is + e_c)·e_c) (silindir), küre/bombe için aynı biçim R = iç yarıçap (bombede 7.5.4/7.5.3 taç yarıçapı — mevcut yardımcıları kullan);
  nozul l_bo = √((d_eb − e_b)·e_b); içeri çıkıntı l'_bi = min(çıkıntı, 0,5·l_bo).
- Alanlar: Af_s = l'_s·e_c, Af_b = e_b·(l'_bo + l'_bi + e_s), Af_p = takviye pedi (Nozzle'da ped alanları varsa; yoksa 0), Af_w = kaynak (0 al, varsayım yaz).
  Ap_s silindirde = R_is·(l'_so + a), a = d/2 (dairesel açıklık, dik nozul); Ap_b = 0,5·d_ib·(l'_bo + e_s). Bombede Ap_s = 0,5·R²·(l'_so + a)/(0,5·e_c + R) yerine sadeleştirilmiş küre ifadesini kullan ve varsayımı yaz.
- e_c, e_b, e_p = analiz kalınlıkları: nominal − korozyon − tolerans (mevcut EN kabuk/bombe hesabındaki desen). f değerleri malzeme tasarım gerilmesi (mevcut `_find_material` + diğer EN metotlarındaki f elde etme deseni).
- Eğik nozul (inclination ≠ 0), eksen dışı, 9.4 uygulanabilirlik sınırı (d/D ve e/D) aşıldığında → OUT_OF_SCOPE (`set_out_of_scope`, mesaj açık). Koni/düz kapak üzerindeki nozul → NOT_CALCULATED.
- Sonuç: PASS/FAIL, sonra `self._cap_unverified(result, "EN 13445-3, 9.5")`. `calculation_type="nozzle_reinforcement"`, `component_type="nozzle"`, `component_id=nozzle.tag`, `clause_reference="EN 13445-3, 9.5"`. Sol/sağ taraf ve tüm ara alanlar sonuçta görünsün (diğer EN hesaplarındaki desen).
- Girdi sözleşmesi: orchestrator `calculate_nozzle({...})`'e ne gönderiyorsa onu kullan (`packages/calc-core/src/calc_core/orchestrator.py` ~193. satır). ASME `calculate_nozzle`'ın aynı dict anahtarlarını nasıl okuduğuna bak.

## Testler (yeni dosya)
- Silindir üzerinde dik nozul: elle adım adım hesap (yorumda), sol/sağ taraf göreli tolerans ≤ %0,5; yeterli ve yetersiz takviye örnekleri (REVIEW_REQUIRED / FAIL).
- PASS asla dönmez. Eğik nozul → OUT_OF_SCOPE. Sonuç `code == "EN 13445"`, ASME clause yok.
- Fixture: `tests/faz4/test_faz4_en13445.py` desenini örnek al; geometri tutarlı olsun (G01 kapısı).

## Ortam notu
Komut çalıştırma iznin olmayabilir; test koşamazsan raporda "Test: koşulamadı" yaz, şef koşacak.

## Dönüş
≤15 satır RAPOR: durum · dosyalar · formül listesi · hangi domain alanlarını kullandığın · açık riskler.
