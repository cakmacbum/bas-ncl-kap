#!/usr/bin/env bash
# Kod için dönüş noktası: git etiketi + GitHub'a push.
#   nokta.sh al "<kisa-ad>"   -> donus/<tarih>-<ad> etiketini HEAD'e koy, origin'e it
#   nokta.sh liste            -> son dönüş noktaları
#   nokta.sh don <etiket>     -> ŞU ANKİ hali yedek/* ile koruyup etikete geri sar (onay ister)
# Bağımlılık dosyaları (node_modules, .venv) git'te yok; geri dönünce gerekirse `npm ci`.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
cmd="${1:-}"; shift || true

case "$cmd" in
  al)
    ad="$(printf '%s' "${1:-nokta}" | tr -c 'A-Za-z0-9._-' '-' | sed 's/-*$//')"
    if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
      echo "UYARI: izlenen dosyalarda commit'lenmemiş değişiklik var; etiket yalnız HEAD'i korur."
      echo "Önce commit atın (git commit -am ...), sonra tekrar çalıştırın. Zorlamak için NOKTA_ZORLA=1."
      [ "${NOKTA_ZORLA:-0}" = "1" ] || exit 2
    fi
    etiket="donus/$(date +%Y-%m-%d-%H%M)-$ad"
    git tag -a "$etiket" -m "Dönüş noktası: $ad ($(git rev-parse --short HEAD))"
    git push origin "$etiket"
    echo "OK: $etiket -> $(git rev-parse --short HEAD)"
    ;;
  liste)
    git tag -l 'donus/*' --sort=-creatordate --format='%(refname:short)  %(objectname:short)  %(subject)' | head -20
    ;;
  don)
    hedef="${1:?kullanım: nokta.sh don <etiket>}"
    git rev-parse -q --verify "refs/tags/$hedef" >/dev/null || { echo "Etiket yok: $hedef"; exit 1; }
    yedek="yedek/$(date +%Y-%m-%d-%H%M%S)"
    echo "Hedef : $hedef ($(git rev-parse --short "$hedef^{commit}"))"
    echo "Şimdi : $(git rev-parse --short HEAD)  -> önce $yedek etiketiyle korunacak"
    git diff --stat "$hedef" HEAD | tail -5
    read -r -p "Çalışma ağacını hedefe döndürmek için 'evet' yazın: " c
    [ "$c" = "evet" ] || { echo "İptal."; exit 1; }
    git tag "$yedek" HEAD
    # Geçmişi silmeden: hedefin içeriğini yeni bir commit olarak uygula (push güvenli)
    git read-tree -u --reset "$hedef^{tree}"
    git commit -q -m "geri dön: $hedef içeriği (önceki hal: $yedek)" || echo "Fark yok."
    echo "OK. Önceki hale dönmek için: nokta.sh don $yedek"
    ;;
  *)
    sed -n '2,6p' "$0"; exit 1 ;;
esac
