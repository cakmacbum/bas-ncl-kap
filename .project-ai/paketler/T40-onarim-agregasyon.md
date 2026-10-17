# PAKET T40-onarim-agregasyon — Tur 3 satır durumu yeniden hesaplama

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir. Örn. `tools/campaign/...` = `pressure-vessel-suite/tools/campaign/...`. Depo kökünde `tools/` yoktur.

## Bağlam
T30, T31, T32, T33 çıktıları (`tools/campaign/tur3/mega_*/results.json`). T32'de 110/110 satır BULGU; oysa alt kontroller GEÇTİ/PASS. Satır durumu hatalı birleştirilmiş.

## Görev
0. ÖN ADIM (zorunlu): sahip tavanı düzeltildi (harness her vakaya ayrı X-Client-Id verir). T30–T33 sonuçlarında 'Project limit reached' hatası var; bunlar hesap değil, eski harness artefaktı. Önce `python -m tools.campaign.tur3.mega_govde.run`, `mega_destek.run`, `mega_nozul.run`, `mega_yuk.run` komutlarını yeniden koştur. Sonra aşağıdaki adımlara geç.
1. `results.json` içindeki her satır için `kontrol` listesini oku.
2. Satır durumunu şöyle yeniden hesapla: herhangi bir kontrolün durumu `BULGU` ise `BULGU`; `BLOCKED` ise `BLOCKED_BEKLENEN`; tümü `PASS`/`GEÇTİ` ise `GEÇTİ`.
3. Bu kural ile hâlâ BULGU çıkan satırları tek tek incele: hangi kontrol başarısız, neden? Gerçek bir uygulama hatası mı, yoksa kontrol tanımı mı yanlış? Her grup için 2 örnekle raporla.
4. Düzeltilmiş `results.json` yaz (`results_v2.json`); aggregate için eski dosyayı silme.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T40-onarim-agregasyon.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T40-onarim-agregasyon` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
Yeniden hesaplanmış dağılım raporda; kontrol tanımı hatası (geçersiz_test) ile gerçek bulgu ayrı sayılmış.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
