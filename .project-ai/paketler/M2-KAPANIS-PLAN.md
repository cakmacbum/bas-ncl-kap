# M2 kapanış planı — açık eksikler (2026-10-18)

Yöntem (DEC-006): Sonnet ajanları izole worktree'de, commit atmaz; şef diff'i inceler, yalnız ilgili dosyaları ana ağaca alır,
tam paketi koşturur, commit eder. Codex yalnız `tools/campaign/**` (K2/DEC-005: çekirdek kod Claude'da). Yol kuralı: `pressure-vessel-suite/` köküne göre.

| Paket | Yürütücü | Kapsam | Dosya alanı (çakışmasın) |
|---|---|---|---|
| K1 | Sonnet | Hidrotest (UG-99) statik kafası | calc-core test-basıncı kodu + test |
| K2 | Sonnet (frontend) | Arayüze `liquid_level_mm` + dikeyde `component_sequence` yoksa açık uyarı | apps/web-ui, test_ui_parity |
| K3 | Sonnet | MDMT coincident ratio bağlama (B-04) + nozul E1<1 (T-2.14) | packages/mdmt, packages/nozzles (+ orchestrator'a minimum dokunuş) |
| K4 | Sonnet | G-05 taban halkası sonucu, G-06 saddle OUT OF SCOPE kapsam belgesi/neden, B-08 nozul yerleşim sayısal çıktı | packages/supports, docs/limitations.md |
| C1 | Codex luna | T63 nozul bağımsız değer + eliptik crown_depth yeniden yazımı (T-07/T-08/P-02), T45 torisferik | tools/campaign/tur6, tur3 |
| — | şef | EN 13445 flanş/yük/yorulma (B-06) — kapsam büyük: K4 sonrası ayrı karar; Browser e2e (T-2.12) K2 sonrası |  |

Kabul: tam paket yeşil, her değişiklik için bağımsız test, EKSIKLER.md satırı güncellenir.
