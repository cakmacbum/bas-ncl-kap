# D1 geri-dönüş betikleri ve kılavuz

Mod: yaz
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

## Amaç
Canlı site (Vercel projesi `pv-suite-app`) değişirse ve beğenilmezse eski haline hızlı dönebilmek için
**salt-okur kontrol betiği**, **geri-dönüş betiği** ve **kısa Türkçe kılavuz** yazmak. Betikler yalnız
YAZILACAK; sen çalıştırmayacaksın (kabuk izni yok).

## Bilinen gerçekler (değiştirme, olduğu gibi kullan)
- Vercel ekibi/scope: `yusufsaglamci11-7502s-projects`, proje: `pv-suite-app`.
- Şu anki GÜVENLİ canlı sürüm: deployment `dpl_284RKQJGPkYKWSJYie5yNPvNFwUr`
  (`https://pv-suite-7uw401gz4-yusufsaglamci11-7502s-projects.vercel.app`), git commit `870e425`,
  git etiketi `canli-oncesi-2026-11-15`.
- Canlı adres: `https://app.zeyslabs-vessela.com`. Sağlık ucu: `/api/health` (cevap JSON, durum "ok").
- Vercel CLI global kurulu değil: her yerde `npx --yes vercel@latest` kullan, her komuta
  `--scope yusufsaglamci11-7502s-projects` ekle.
- Geri alma komutu: `npx --yes vercel@latest rollback <dpl-id-veya-url> --scope ...`
  (anında, yeniden build yok). Yedek yol: `git archive canli-oncesi-2026-11-15` ile temiz kopya + `vercel deploy --prod`.
- Dağıtım git push ile otomatik DEĞİL; elle `vercel deploy` çalıştırılır.

## Kapsam — yalnız bu dosyaları yaz
- `pressure-vessel-suite/tools/canli/kontrol.sh` — SALT OKUR. `vercel ls`/`vercel inspect` ile mevcut üretim
  deployment kimliğini yazdırır; `/api/health` isteği atar (curl, 15 sn zaman aşımı); canlıdaki
  `index-*.js` dosya adını sayfa HTML'inden çıkarıp yazdırır. Hiçbir şey değiştirmez.
- `pressure-vessel-suite/tools/canli/geri-don.sh` — argüman: hedef deployment kimliği (varsayılan:
  yukarıdaki güvenli sürüm). ÖNCE ne yapacağını ve hedefi yazdırır, ardından `evet` yazılmasını ister
  (onay olmadan ASLA çalıştırmaz; `--evet` bayrağı yok). Sonra `vercel rollback`, ardından
  `kontrol.sh` çağırır.
- `pressure-vessel-suite/tools/canli/README.md` — en çok 40 satır Türkçe: ne zaman kullanılır, adımlar,
  sorun olursa yedek yol (git etiketi). Gizli anahtar yazma.

## Kurallar
- `set -euo pipefail`; değişkenler tırnaklı; Windows Git Bash uyumlu (sade bash, `jq` KULLANMA, `curl` ve `sed` yeter).
- Hiçbir betik `--prod` ile deploy ETMEZ, `vercel rm`/`remove`/`alias set`/`env` KULLANMAZ, token/secret yazdırmaz.
- `.env*`, `vercel.json`, `.vercel/`, `packages/`, `apps/`, `tests/` DOKUNMA.
- Betiklere açıklama satırı (neden, ne yapar) ekle; gereksiz süs yok.

## Doğrulama
Kabuk çalıştıramadığın için: bitirince betikleri satır satır oku, her komutun salt-okur/onaylı olduğunu
kontrol et. Raporda "betikler çalıştırılmadı" yaz.

## Rapor (≤10 satır)
İlk satır: `D1 geri-donus — TAMAM | KISMİ | BAŞARISIZ`. Yazılan dosyalar · varsayımlar · açık risk.
