# PAKET T42-onarim-t11 — T11 yatay tank kapsam dışı sınıflandırması

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir. Örn. `tools/campaign/...` = `pressure-vessel-suite/tools/campaign/...`. Depo kökünde `tools/` yoktur.

## Bağlam
T11 (`tools/campaign/tur2/t11_yatay_tank_tarama/`) 144 vakanın tamamı KAPSAM_DIŞI. Zick sonuçları (saddle_stress) varsa bağla.

## Görev
0. ÖN ADIM (zorunlu): harness sahip tavanı düzeltildi. Mevcut results.json dosyalarındaki 'Project limit reached' satırları hesap değil, eski harness artefaktıdır. Bu paketin ilk işi: ilgili run.py'yi YENİDEN koştur, ardından aşağıdaki adımlara geç.
1. Sonuç kataloğunu (`tools/campaign/RESULT_CATALOG.md`) kullanarak saddle sonuç tipini bul. Vakalardan gelen `available_results` listesini incele.
2. Yatay tank temel vakasının saddle ile hesaplandığından emin ol; `supports` girdileri (saddle sayısı, konum, kontak açısı) eksik mi?
3. Düzelt, yeniden koştur. Hâlâ kapsam dışı kalanlar için neden (girdi eksik / sonuç tipi yok) tablo halinde yaz.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T42-onarim-t11.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T42-onarim-t11` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
KAPSAM_DIŞI oranı açıklanmış; mümkün olanlar GEÇTİ/BULGU'ya dönmüş.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
