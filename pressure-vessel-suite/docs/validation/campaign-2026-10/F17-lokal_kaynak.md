# F17 — Lokal gerilme ve kaynak hattı

## 1. Özet

25 vaka koşturuldu: 24 `DOĞRULANDI`, 1 `TEK_KAYNAK`; `FORMÜLASYON_FARKI`, `SAPMA`, `KAYNAK_BEKLİYOR` ve `KAPSAM_DIŞI`: 0. 24 API vakası `leg_weld_check` satırındaki `pad_to_shell_stress` için sayısal kıyaslandı. Bağımsız denklem aynı API yük ve etkin geometri ara değerleriyle tekrar hesaplandığında farkların tümü 0% (karşılaştırma toleransı içinde).

## 2. Oracle formülleri

1. Kapalı dikdörtgen kaynak hattı: ham `Lw = 2(b+d)`.
2. Blodgett yönlü kesit modülü: `Sw = bd + d²/3`.
3. API `pad_to_shell_Lw`, `pad_to_shell_Sw`, `pad_to_shell_shear`, `pad_to_shell_normal` ve `pad_to_shell_moment` ara değerleri etkin geometri/yük girdisi olarak alındı. Oracle bağımsız olarak `q = sqrt((V/Lw)² + (N/Lw + M/Sw)²)`, `a = 0.707z`, `τ = q/a` hesapladı. Bu eşitlik API satırının formül açıklamasındaki line-force ve boğaz dönüşümünü dışarıdan yeniden kurar.
4. API etkin geometriyi köşe/krater düzeltmesiyle verdiğinden ham Blodgett Lw/Sw ayrıca raporlandı; bu tur etkin Lw/Sw düzeltmesinin bağımsız doğrulaması değildir. Kuvvetler API ara değerlerinden kullanıldı; bu kıyas kaynak grubunun gerilme dönüşümünü sınar, toplam yük hesabını bağımsız doğrulamaz.
5. WRC katsayıları kullanıcı tarafından lisanslı bülletenden okunmalıdır. `examples.py` içindeki sıfır katsayılar bir yayın oracle'ı olmadığından WRC satırları sayısal kıyasa alınmadı.

Dayanak: Blodgett, *Design of Welded Structures*, §7.4 (önceki engineering-source-review-2026-09-30.md §3); sonuç tipi ve alan isimleri `tools/campaign/RESULT_CATALOG.md` `leg_weld_check` girdisi.

## 3. SAPMA tablosu

SAPMA yok; emniyetsiz/emniyetli yönü atanacak sayısal fark bulunmadı. 24 vakada API sonucu ile stres oracle'ı aynı etkin Lw/Sw ve kuvvetleri kullandığı için özdeşleşti. Geometri girdilerindeki varyasyonlar SAPMA olarak yorumlanamaz; etkin geometrinin düzeltme yöntemine dair bağımsız kaynak bulunmadı.

| Sonuç | Vaka sayısı | Yön |
|---|---:|---|
| SAPMA | 0 | uygulanamaz |

## 4. Yayınlanmış vakalar

| case_id | Kaynak / girdiler | Oracle | Suite | Etiket |
|---|---|---:|---|---|
| PUB-K3-22 | Union College MER419, Shigley 10. bas. Tablo 9-2; `b=70 mm`, `d=120 mm`; sources-K3.md K3-22 | `Sw=13,200 mm²` | API bu yayın örneğinin Sw değerini üretmiyor; ayrı API geometri varyantında sayısal stres satırı bulunur | TEK_KAYNAK |

## 5. Kapsam ve sınırlamalar

24 geçerli API vakası katalogdaki çalışan `example_leg_weld_check()` projesinden türetildi; ped boyutu ve `pad_to_shell_weld_leg_mm` değiştirildi. Tam proje `leg_weld_check` satırı döndürdü. Ek olarak sonuç kataloğundaki `wrc_local_stress` girdileri örnekte mevcut olsa da katsayılar sıfır ve yalnızca kullanıcı okuması girdisidir; WRC katsayı doğruluğu veya lokal gerilme denklemi için yayınlanmış sayısal oracle olmadığından bu vakalar sayı dağılımına eklenmedi.

## 6. Temiz oda beyanı

Yasaklı `packages/code-*`, `nozzles`, `supports`, `external-pressure`, `mdmt`, `flanges` ve `calc-core` implementasyonları açılmadı veya okunmadı. Suite sonuçları yalnız `run_case` public API yanıtı ve katalogda tanımlanan `leg_weld_check` intermediate_values üzerinden alındı. Oracle Blodgett kapalı çizgi bağıntıları ve bağımsız line-force/etkin boğaz denklemiyle kuruldu. Katalog ve `examples.py` kullanıldı; harness değiştirilmedi. Etkin API Lw/Sw düzeltmesinin fiziksel/kaynak dayanağı açık sorudur.
