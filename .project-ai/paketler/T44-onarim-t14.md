# PAKET T44-onarim-t14 — T14 etekli kolon yeniden yazımı

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 4 (onarım) · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor

## Bağlam
T14 modül bulunamadı; deneme dosyaları `pressure-vessel-suite/pressure-vessel-suite/` altına yanlış yazılmış. Rapor yok.

## Görev
1. Yanlış yoldaki dosyaları KALDIRMA; yalnız görmezden gel ve raporda belirt.
2. `tools/campaign/tur2/t14_dikey_kolon_yuk/` içine doğru modülü yaz (`__init__.py`, `run.py`, `cases.py`). Etekli kolon temel tankını `bases.py` `skirt_column` ile kur.
3. 30 vaka: H/D 3–20, rüzgâr hızı ve deprem bölgesi değişimi. Her vaka için etek gerilmesi ve taban halkası sonucunun var olup olmadığını kontrol et.
4. Çalıştır; sonuç üret.

## Kurallar
- `packages/**` ve `apps/**` DOKUNMA. Harness (`tools/campaign/harness.py`) değiştirme.
- Yalnız kendi klasörüne yaz; rapor `docs/validation/campaign-2026-10/tur4/T44-onarim-t14.md`.
- Pytest: `--basetemp <sistem TEMP>/pv-T44-onarim-t14` ve `-p no:cacheprovider`.
- Gizli bilgi yok. Kod okuma kısıtı yok (bu bir test onarımıdır).

## Kabul
`python -m tools.campaign.tur2.t14_dikey_kolon_yuk.run` hatasız biter; 30 satır; SONUÇ satırı var.
Son satır: `SONUÇ: vaka=N · GEÇTİ=a · BULGU=b · BLOCKED=c · KAPSAM_DIŞI=d · geçersiz_test=e`.
