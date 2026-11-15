# Canlı geri dönüş kılavuzu

Canlı site (`https://app.zeyslabs-vessela.com`, Vercel projesi `pv-suite-app`) değiştirildikten
sonra beğenilmezse hızlıca eski sürüme dönmek içindir. Yeni dağıtım siteyi bozduysa önce durumu gör.

## Adımlar
1. Salt-okur durum kontrolü (hiçbir şey değiştirmez):

   ```bash
   bash tools/canli/kontrol.sh
   ```

   Üretim deployment kimliği, `/api/health` cevabı ve canlı `index-*.js` adı görünür.

2. Güvenli sürüme dön (varsayılan `dpl_284RKQJGPkYKWSJYie5yNPvNFwUr`, git `870e425`,
   etiket `canli-oncesi-2026-11-15`):

   ```bash
   bash tools/canli/geri-don.sh
   ```

   Betik önce hedefi yazdırır, `evet` onayı ister; onay yoksa çalışmaz. Onay sonrası
   `vercel rollback` (anında, build yok) ve ardından `kontrol.sh` çalışır.

3. Belirli sürüme dönüş: `bash tools/canli/geri-don.sh dpl_BASKA_KIMLIK`

## Sorun olursa (yedek yol)
`vercel rollback` başarısızsa git etiketinden temiz kopya alıp elle yayınla:

```bash
git archive canli-oncesi-2026-11-15 | tar -x -C /tmp/pv-eski
cd /tmp/pv-eski && npx --yes vercel@latest deploy --prod --scope yusufsaglamci11-7502s-projects
```

CLI global değil; her yerde `npx --yes vercel@latest` ve `--scope` kullan. Betikler gizli
anahtar yazmaz, `--prod` ile deploy etmez, deployment silmez, alias/env değiştirmez.
Git Bash'te `bash tools/canli/geri-don.sh` yeterlidir (yürütme izni gerekmez).
