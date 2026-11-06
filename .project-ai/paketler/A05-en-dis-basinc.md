# A05 — EN 13445-3 Madde 8 dış basınç (silindir + bombe)

Mod: yaz · Motor: agy gemini-3.8-flash-high · Proje kökü: worktree kökü (yollar `pressure-vessel-suite/` ile başlar)

## Amaç
`EN13445DesignCode.check_external_pressure` şu an her gövde/bombe için NOT_CALCULATED döndürüyor.
EN 13445-3 Madde 8 (dış basınç) için gerçek hesap yaz. ASME UG-28 değerlerine/koduna ASLA fallback yapma.

## Kapsam (yalnız bu dosyalara yaz)
1. YENİ `pressure-vessel-suite/packages/code-en-13445/src/code_en_13445/external_pressure.py` — saf fonksiyonlar (domain'e bağımsız, float girer/çıkar).
2. `pressure-vessel-suite/packages/code-en-13445/src/code_en_13445/design_code.py` — YALNIZ `check_external_pressure` metodunun gövdesi (+ gerekirse hemen altına özel yardımcı metot). Dosyanın başka hiçbir yerine dokunma (paralelde başka paket `calculate_nozzle`'ı düzenliyor).
3. YENİ `pressure-vessel-suite/tests/faz4/test_en13445_external_pressure.py`.
Dokunma: domain paketi, ASME paketi, `external-pressure` paketi, mevcut testler, UI.

## İçerik (formüller bellekten — her sonuçta verified=False)
- Silindir (8.5, aralarında takviye halkası olmayan boy L): elastik göçme basıncı p_m (von Mises / 8.5.2 ifadesi, n dalga sayısı üzerinden minimize; ν=0,3),
  akma basıncı p_y = σ_e·e_a/R (σ_e = R_p0,2/T), p_r/p_y oranı Şekil 8.5-5 eğrisinden (eğrinin parçalı ifadesini fonksiyon olarak yaz, kaynağını docstring'e "bellekten" diye not et),
  kabul: P ≤ p_r/S, S = 1,5 (tasarım), test durumu 1,1. Ayrıca e_a = e − c − δe (korozyon + tolerans) kullan.
- Küresel kabuk / bombe (8.7): küre için p_m = 1,21·E·e_a²/R², p_y = 2·σ_e·e_a/R, aynı p_r/p_y eğrisi (küre için Şekil 8.7-1 ifadesi). Torisferik → R = taç yarıçapı; elipsoidal → R = 7.5.4 eşdeğer taç yarıçapı (mevcut `_ellipsoidal_radii_en` / `_torispherical_radii_en` yardımcılarını kullan).
- Girdi: `project.design_conditions.external_pressure` (MPa) ve `vacuum_condition` (vakumda P = 0,1 MPa). İkisi de yoksa `[]` döndür (ASME ile aynı davranış).
- Silindir boyu L: domain'de takviye halkası/tasarım boyu alanı var mı bak (ASME `external-pressure` paketi nereden alıyor, onu oku). Yoksa gövde uzunluğu + her iki bombe derinliğinin 1/3'ü (8.5'teki yaklaşım) — varsayımı `add_assumption` ile yaz.
- E: malzemede `elastic_modulus` varsa onu kullan, yoksa 200 000 MPa + uyarı. σ_e için malzemenin tasarım sıcaklığındaki akma değeri (mevcut kodda f hesaplamada nasıl alınıyorsa).
- Durum: hesap çıkarsa PASS/FAIL, sonra mevcut `self._cap_unverified(result, clause)` ile PASS → REVIEW_REQUIRED. Eksik veri → NOT_CALCULATED (mesaj açık). Bombe tipi düz kapak/koni → bu pakette `_unsupported_result` (NOT_CALCULATED).
- `calculation_type="external_pressure"`, `clause_reference="EN 13445-3, 8.5"` (silindir) / `"EN 13445-3, 8.7"` (bombe). `input_snapshot` ve ara değerleri (p_m, p_y, p_r, L, n) sonuç nesnesine mevcut diğer EN hesaplarındaki desenle koy.

## Testler (yeni dosya)
- Elle hesaplanmış en az 1 silindir ve 1 küre örneği (yorumda el hesabı adım adım), göreli tolerans ≤ %0,5.
- Dış basınç yok → boş liste. Vakum → P = 0,1. PASS asla dönmez (REVIEW_REQUIRED). Çok ince kabuk → FAIL.
- ASME'ye fallback yok: sonuç `code == "EN 13445"` ve clause "EN 13445-3, 8." ile başlar.
- Fixture olarak `tests/faz4/test_faz4_en13445.py` içindeki proje kurulum desenini örnek al (geometri tutarlı olmalı: bombe çapı = gövde çapı; G01 kapısı tutarsız geometriyi reddeder).

## Ortam notu
Komut çalıştırma iznin olmayabilir; test koşamazsan raporda "Test: koşulamadı" yaz, şef koşacak. Kod Python 3.12, mevcut stil (Türkçe docstring, tipli imza).

## Dönüş
≤15 satır RAPOR: durum · dosyalar · kullandığın formüllerin listesi + hangi alanı L için kullandığın · açık riskler.
