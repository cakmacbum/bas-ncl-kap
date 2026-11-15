# Canlıdan eski sürüme dönüş (pv-suite-app)

Son güncelleme: 2026-11-15

## Sürümler
| | Deployment | Commit | Not |
|---|---|---|---|
| ESKİ (güvenli) | `dpl_284RKQJGPkYKWSJYie5yNPvNFwUr` | `870e425` (git etiketi `canli-oncesi-2026-11-15`) | 6 Kasım'dan beri canlıdaydı, paket `index-KmHxBuQe.js` |
| YENİ (şu an canlı) | `dpl_CcxjY52roYTcGeboP2nFRftJ3b69` | `3374a5f` (dal `gemini-ug36c3-ui-hata-siniri`) | 15 Kasım'da yayınlandı, paket `index-Det3r08p.js` |

Vercel scope: `yusufsaglamci11-7502s-projects` · Canlı adres: https://app.zeyslabs-vessela.com

## Yol 1 — Hızlı (önerilen, yaklaşık 1 dakika, yeniden build yok)
Git Bash'te, depo kökünden:
```bash
bash pressure-vessel-suite/tools/canli/geri-don.sh
```
Hedefi (eski sürüm) yazar, `evet` yazmanızı ister, sonra rollback yapar ve kontrol çalıştırır.

Elle yapmak isterseniz:
```bash
cd pressure-vessel-suite
npx --yes vercel@latest rollback dpl_284RKQJGPkYKWSJYie5yNPvNFwUr --scope yusufsaglamci11-7502s-projects
```

## Yol 2 — Yedek (Yol 1 çalışmazsa)
```bash
D="$(mktemp -d)"
git archive canli-oncesi-2026-11-15 pressure-vessel-suite | tar -x -C "$D"
mkdir -p "$D/pressure-vessel-suite/.vercel"
cp pressure-vessel-suite/.vercel/project.json "$D/pressure-vessel-suite/.vercel/"
cd "$D/pressure-vessel-suite"
npx --yes vercel@latest deploy --prod --scope yusufsaglamci11-7502s-projects --yes
```

## Dönüşü doğrulama
```bash
bash pressure-vessel-suite/tools/canli/kontrol.sh
```
Beklenen: `/api/health` → `{"status":"ok",...}`, canlı paket `index-KmHxBuQe.js`, alias `dpl_284RKQ…`.
Windows Git Bash'te `/api/...` gibi yollar bozulursa önce `export MSYS_NO_PATHCONV=1`.

## Notlar
- Vercel, rollback sonrası domain'lerin yeni üretim deploy'larına otomatik bağlanmasını durdurabilir (Vercel belgesine göre; doğrulanmadı). Sonraki bir `deploy --prod` canlıya yansımazsa `npx --yes vercel@latest promote <dpl>` gerekebilir.
- Dağıtım git push ile otomatik değildir; elle `vercel deploy --prod` ile yapılır.
- Etiket GitHub'da (`origin`) da durur; yerel kopya kaybolsa bile oradan alınır.
