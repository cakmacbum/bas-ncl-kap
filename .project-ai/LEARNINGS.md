# LEARNINGS

## [2026-10-06] Agent worktree'leri eski tabandan açılıyor
Problem: `isolation: "worktree"` alt-ajan worktree'si yerel `main`'den değil `origin/main`'den
(1f51a26, 7 commit geride) açıldı; P02 eski main.py üzerinde yazdı.
Çözüm: dönüşte `git cherry-pick <commit>` ile güncel main'e al + testleri main'de yeniden koş;
dağıtmadan önce `git push` yoksa brief'e "önce `git rebase main`" satırı ekle.
Codex betiği yerel HEAD'den açtığı için etkilenmez.
