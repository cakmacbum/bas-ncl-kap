# PAKET T15-performans — Performans ve eşzamanlılık

> Proje: BASINCLI-KAP (kod `pressure-vessel-suite/`) · M2 Tur 2 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤15 satır rapor

## Görev
100 farklı projeyi sıralı ve 8 iş parçacığıyla eşzamanlı koştur. Ortalama/p95 süre, hata oranı, eşzamanlı isteklerde sonuçların karışmadığını (her yanıt kendi projesine ait mi) sına. Bellek artışı gözle.

Çıktılar:
- `pressure-vessel-suite/tools/campaign/tur2/t15_performans/` → `cases.py`, `run.py` (`python -m tools.campaign.tur2.t15_performans.run`
  ile koşar), `results.json` (vaka, girdi, beklenen, gözlenen, sonuç: GEÇTİ/BULGU/KAPSAM_DIŞI).
- `pressure-vessel-suite/docs/validation/campaign-2026-10/tur2/T15-performans.md` → vaka sayısı, geçti/bulgu dağılımı,
  bulgu tablosu (önem, yön, dosya:satır), kapsam dışı listesi. Son satır:
  `SONUÇ: vaka=N · geçti=a · bulgu=b (kritik=k, emniyetsiz=u) · kapsam_dışı=c`.

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
Yalnızca kendi iki yoluna yaz: `tools/campaign/tur2/t15_performans/` (ve gerekiyorsa boş `tools/campaign/tur2/__init__.py`
yoksa oluştur) ile `docs/validation/campaign-2026-10/tur2/T15-performans.md`.

## Kabul
`run.py` hatasız biter, ≥20 vaka (T03 ≥40, T04 300, T15 100), rapor son satırı biçime uygun.
