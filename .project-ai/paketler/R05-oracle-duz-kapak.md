# PAKET R05-oracle-duz-kapak — f05_duz_kapak_ug34 oracle düzeltmesi + yeniden kıyas

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 2 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤15 satır rapor

## Bağlam
`docs/validation/campaign-2026-10/teyit/V05-f05_duz_kapak_ug34.md` teyidi SAPMA'ların oracle tarafında olduğunu gösterdi.
Şef notu: Suite `t_required` alanına CA eklemez; CA'yı nominal adımda bir kez ekler (`design_code.py:547-587`). Oracle t_required'a +CA ekleyip karşılaştırdı. Aynı tanımla kıyasla. Ayrıca UG-34'te d'nin korozyonlu çap (d+2CA) alınması emniyetli yönde bir formülasyon farkıdır; FORMÜLASYON_FARKI olarak etiketle.

## Görev
1. `tools/campaign/families/f05_duz_kapak_ug34/oracle.py` (gerekirse `run.py`/`variants.py`) düzelt. Oracle hâlâ temiz oda:
   Kod formülünden yazılır; suite'in yalnız **çıktı alanı tanımını** (`RESULT_CATALOG.md`) eşle.
2. `python -m tools.campaign.families.f05_duz_kapak_ug34.run` ile yeniden koştur; `results.json` + `docs/validation/campaign-2026-10/F05-duz_kapak_ug34.md`
   güncelle. Rapora "Tur 2 düzeltmesi" bölümü ekle: ne değişti, önceki ve yeni etiket dağılımı.
3. Hâlâ SAPMA kalırsa her biri için girdi + iki değer + muhtemel neden yaz.

## Kurallar
- Harness: `pressure-vessel-suite/tools/campaign/harness.py` (`run_case`, `find_results`, `value_of`), temel
  tanklar `bases.py`, çalışan örnekler `examples.py`, sonuç kataloğu `RESULT_CATALOG.md`. Harness `X-Client-Id`
  başlığını gönderir (P11). Harness'i değiştirme; eksik bir şey varsa kendi klasöründe sarmala.
- Suite koduna (`packages/**`, `apps/**`) DOKUNMA. Hata bulursan yalnız raporla (dosya:satır, girdi, beklenen,
  gözlenen, önem: KRİTİK/YÜKSEK/ORTA/DÜŞÜK, emniyetsiz/emniyetli yön). Düzeltme Yusuf onayından sonra yapılır.
- Oracle gereken testlerde temiz oda: oracle'ı Kod formülünden kendin yaz, `packages/code-*`, `nozzles`,
  `supports`, `external-pressure`, `mdmt`, `flanges` implementasyonlarını okuma. (T03/T05/T06/T07/T08/T12/T15
  oracle gerektirmez; bunlarda suite kodunu okuyabilirsin.)
- K6: Kod metni/tablosu kopyalanmaz. Gizli bilgi (.env, anahtar) kullanılmaz ve yazılmaz.
- Pytest: `--basetemp <sistem TEMP>/pv-<paket>` ve `-p no:cacheprovider`. Worktree içine geçici klasör açma.

## Kapsam
Yalnızca `tools/campaign/families/f05_duz_kapak_ug34/` ve `docs/validation/campaign-2026-10/F05-duz_kapak_ug34.md`.

## Kabul
Run hatasız; yeni dağılım raporda; son satır `SONUÇ: DOĞRULANDI=a · SAPMA=b · FORMÜLASYON_FARKI=c · KAPSAM_DIŞI=d`.
