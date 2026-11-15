#!/usr/bin/env bash
# canli/kontrol.sh — canlı sitenin durumunu SALT OKUR ve yazdırır.
# Hiçbir deployment/alias/env değiştirmez; yalnız vercel ls/inspect ve curl kullanır.
set -euo pipefail

SCOPE="yusufsaglamci11-7502s-projects"
PROJE="pv-suite-app"
CANLI_ADRES="https://app.zeyslabs-vessela.com"
VERCEL="npx --yes vercel@latest"

echo "== Canlı kontrol =="
echo "Adres : $CANLI_ADRES"
echo "Proje : $PROJE (scope: $SCOPE)"
echo

echo "-- Deployment listesi (vercel ls; salt-okur) --"
if ! $VERCEL ls "$PROJE" --scope "$SCOPE"; then
  echo "UYARI: 'vercel ls' başarısız oldu (oturum/izin?)."
fi
echo

echo "-- Canlı adresin deployment bilgisi (vercel inspect; salt-okur) --"
if ! $VERCEL inspect "$CANLI_ADRES" --scope "$SCOPE"; then
  echo "UYARI: 'vercel inspect' başarısız oldu."
fi
echo

echo "-- Sağlık ucu: /api/health (15 sn zaman aşımı) --"
if ! curl -sS --max-time 15 "$CANLI_ADRES/api/health"; then
  echo "UYARI: sağlık ucu yanıt vermedi."
fi
echo
echo

echo "-- Canlı index-*.js dosya adı(ları) --"
HTML="$(curl -sS --max-time 15 "$CANLI_ADRES/" || true)"
VAR_MI=0
if [ -n "$HTML" ]; then
  # Etiketleri satırlara bölüp index-*.js adlarını sed ile çıkar.
  ADLAR="$(printf '%s' "$HTML" | sed 's/></>\n</g' | sed -n 's/.*\(index-[A-Za-z0-9_.-]*\.js\).*/\1/p' | sort -u)"
  if [ -n "$ADLAR" ]; then
    printf '%s\n' "$ADLAR"
    VAR_MI=1
  fi
fi
if [ "$VAR_MI" -eq 0 ]; then
  echo "UYARI: sayfa HTML'inde index-*.js bulunamadı veya sayfa alınamadı."
fi

echo
echo "Kontrol bitti; hiçbir şey değiştirilmedi."
