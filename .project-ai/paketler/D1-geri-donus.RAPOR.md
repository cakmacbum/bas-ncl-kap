# RAPOR D1-geri-donus

> Yürütücü: OpenCode evren/deepseek-v4.1-flash (yaz) · 2026-11-15 20:45
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/D1 · Dal: ork/D1 · Taban: 7322a76
> Token: 198017 / 4567 / 206578 (girdi/çıktı/toplam)

D1 geri-donus — TAMAM

Dosyalar:
- `pressure-vessel-suite/tools/canli/kontrol.sh` (salt-okur: `vercel ls`/`inspect`, `/api/health` curl 15 sn, HTML'den `index-*.js`)
- `pressure-vessel-suite/tools/canli/geri-don.sh` (hedef yazdırır, `evet` onayı ister; onay yoksa çıkmaz; `vercel rollback` + `kontrol.sh`)
- `pressure-vessel-suite/tools/canli/README.md` (37 satır Türkçe, yedek yol git etiketi)

Test: kabuk izni yok — betikler **çalıştırılmadı**; satır satır okundu, `bash -n` dahi denenmedi.
Sözleşme: uyuldu — `set -euo pipefail`, tırnaklı değişkenler, `jq` yok, `--prod` deploy yok, `rm/remove/alias/env` yok, token yazılmıyor, kapsam dışına dokunulmadı, commit atılmadı.
Varsayımlar: `read -r` EOF'ta onaysız sayılır (`|| ONAY=""`); `vercel inspect` canlı alias URL'sini kabul eder, etmezse uyarı basıp devam eder.
Açık risk: `vercel inspect "$CANLI_ADRES"` alias çözümlemesi sürüm/CLI'ye göre değişebilir; `vercel ls --prod` yerine üretim kimliği inspect çıktısından okunur. Betiklerin yürütme biti yok; Git Bash'te `bash <dosya>` ile çağrılmalı.
```
 pressure-vessel-suite/tools/canli/README.md   | 37 +++++++++++++++++++
 pressure-vessel-suite/tools/canli/geri-don.sh | 38 ++++++++++++++++++++
 pressure-vessel-suite/tools/canli/kontrol.sh  | 51 +++++++++++++++++++++++++++
 3 files changed, 126 insertions(+)
```
