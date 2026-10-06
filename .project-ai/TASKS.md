# TASKS — M1 STEP içe aktarma

## BACKLOG
- T-1.4 Entegrasyon (P01+P02+P03 birleştirme)
- T-1.5 Doğrulama dalgası (test-verifier ‖ code-reviewer + security-auditor P02)
- T-1.6 Kapanış: limitations.md B kaydı, kasa, log

## IN_PROGRESS
### T-1.1 — P01 STEP tanıyıcı (risk: orta)
Kabul: S1/S2/S3 tanıyıcı seviyesinde; round-trip ID/t/L/sf %0.1; ret vakaları REJECTED/PARTIAL.
Doğrulama: `pytest tests/cad-validation/test_step_import.py`
DoD: [ ] round-trip 2:1/hemi/flat [ ] gerçek tori Rc/rk %0.5 [ ] builder-tori → elips oranı uyarısı
     [ ] nozullu vaka [ ] 4 ret vakası [ ] CadQuery yok → BLOCKED [ ] eski cad testleri yeşil

### T-1.2 — P02 API ucu (risk: orta, güvenlik yüzeyi)
Kabul: S4; 200 şema uyumlu; geçici dosya silinir.
Doğrulama: `pytest tests/api`
DoD: [ ] 200/413/415/503 testleri [ ] temp silme testi [ ] proje deposu değişmez

### T-1.3 — P03 UI (risk: düşük-orta)
Kabul: S1 (UI kısmı), S5, S6.
Doğrulama: `npm run build` + Browser pane
DoD: [ ] düğme [ ] çekmece onay satırları [ ] not_in_file rozetleri [ ] REJECTED'da form değişmez
     [ ] STL sekmesi [ ] tsc temiz

## DONE
- T-1.0 Plan + SPEC + sözleşme + checkpoint `a0d5619`
