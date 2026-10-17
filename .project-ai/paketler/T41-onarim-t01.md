# PAKET T41-onarim-t01 — T01 metamorfik sınıflandırma

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir. Örn. `tools/campaign/...` = `pressure-vessel-suite/tools/campaign/...`. Depo kökünde `tools/` yoktur.

## Bağlam
T01 çıktısında 240 satırın `durum` alanı yok; sonuç `result` alanında. Ayrıca `relation` ilişkilerinin ikisi de hesaba girmeli.

## Görev
0. ÖN ADIM (zorunlu): harness sahip tavanı düzeltildi. Mevcut results.json dosyalarındaki 'Project limit reached' satırları hesap değil, eski harness artefaktıdır. Bu paketin ilk işi: ilgili run.py'yi YENİDEN koştur, ardından aşağıdaki adımlara geç.
1. `tools/campaign/tur2/t01_metamorfik/results.json` satırlarında `result` alanını oku; `expected`/`observed` ile karşılaştır.
2. Her satır için durumu ata: GEÇTİ (ilişki sağlanıyor), BULGU (ilişki ihlal), BLOCKED_BEKLENEN (sonuç yok, girdi eksik).
3. Monotonluk yönlerini tekrar doğrula: P artınca t_required artar; S artınca t_required azalır; CAi artınca nominal gereksinim artar; E artınca t_required azalır.
4. Yeni `results_v2.json` yaz.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T41-onarim-t01.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T41-onarim-t01` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
240 satırın tamamının durumu var; durum dağılımı raporda; yön hatası olan ilişkiler ayrı listelenmiş.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
