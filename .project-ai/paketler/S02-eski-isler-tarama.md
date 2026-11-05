# S02 — Eski açık işlerin mevcut durumu (SALT OKUR, kod yazma)
Yollar `pressure-vessel-suite/` köküne göre (repo kökü bir üst klasör). Gizli bilgi yok.

Her madde için: bugün kodda var mı, kısmen mi, hiç mi? Kanıt dosya:satır.
1. `liquid_level_mm`: domain modelde (packages/domain) var mı, hesapta (calc_core/hydrostatics.py, orchestrator) kullanılıyor mu,
   web-ui'da (apps/web-ui/src) giriş alanı var mı? `component_sequence` yoksa kullanıcıya uyarı veriliyor mu?
2. Hidrotest UG-99 statik basınç kafası: hidrotest hesabında sıvı sütunu (ρ·g·h) ekleniyor mu (packages/code-asme-viii-1, calc_core)?
   Ayrıca `.project-ai/arsiv/worktree-yamalari/agent-a03eb4b0cead35772.patch` bu iş için yarım kalmış bir yama — ne yapmaya çalışıyor, özetle.
3. Nozulda E1 < 1 (açıklık Kategori B dışı kaynak dikişinden geçerse): reinforcement hesabında E1 nasıl belirleniyor (packages/nozzles/.../reinforcement.py)?
   Ayrıca `.project-ai/arsiv/worktree-yamalari/agent-afcd30bff3cfbf39c.patch` ilgili mi, özetle.
4. Tarayıcı e2e: repoda Playwright/e2e altyapısı var mı (package.json, tests/e2e, playwright.config)? `docs/validation/campaign-2026-10/`
   içinde "3 temel tank" tanımı nerede?
5. `.project-ai/TASKS.md` BACKLOG'da (T-2.7, T-2.8, T-2.12, T-2.14) olup bugün aslında kapanmış görünen var mı?

Çıktı (DONUS'a): her madde için durum (VAR/KISMİ/YOK) + kanıt + yapılması gereken net iş (1–3 satır) + etkilenecek dosyalar.
