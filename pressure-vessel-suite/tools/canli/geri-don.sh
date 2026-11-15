#!/usr/bin/env bash
# canli/geri-don.sh — üretimi bilinen güvenli deployment'a geri alır (yeni build yok).
# Önce hedefi yazdırır, 'evet' onayı ister; onay yoksa hiçbir şey yapmaz.
# Kullanım: bash geri-don.sh [deployment-kimliği-veya-url]
set -euo pipefail

SCOPE="yusufsaglamci11-7502s-projects"
GUVENLI_DPL="dpl_284RKQJGPkYKWSJYie5yNPvNFwUr"
HEDEF="${1:-$GUVENLI_DPL}"
VERCEL="npx --yes vercel@latest"
BETIK_DIZINI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$HEDEF" ]; then
  echo "HATA: hedef deployment kimliği boş olamaz." >&2
  exit 1
fi

echo "== Geri dönüş planı =="
echo "Yapılacak : Üretim deployment'ı aşağıdaki hedefe geri alınacak (anında, yeniden build yok)."
echo "Hedef     : $HEDEF"
echo "Kapsam    : $SCOPE (proje: pv-suite-app)"
echo "Sonrasında: canlı durum kontrolü (kontrol.sh) çalıştırılacak."
echo
printf "Devam etmek için 'evet' yazın: "
ONAY=""
read -r ONAY || ONAY=""
if [ "$ONAY" != "evet" ]; then
  echo "Onay verilmedi; hiçbir şey yapılmadı."
  exit 1
fi

echo
echo "-- vercel rollback çalıştırılıyor --"
$VERCEL rollback "$HEDEF" --scope "$SCOPE"

echo
echo "-- Geri dönüş sonrası canlı kontrol --"
"$BETIK_DIZINI/kontrol.sh"
