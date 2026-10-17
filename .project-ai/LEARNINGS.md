# LEARNINGS

## [2026-10-06] Agent worktree'leri eski tabandan açılıyor
Problem: `isolation: "worktree"` alt-ajan worktree'si yerel `main`'den değil `origin/main`'den
(1f51a26, 7 commit geride) açıldı; P02 eski main.py üzerinde yazdı.
Çözüm: dönüşte `git cherry-pick <commit>` ile güncel main'e al + testleri main'de yeniden koş;
dağıtmadan önce `git push` yoksa brief'e "önce `git rebase main`" satırı ekle.
Codex betiği yerel HEAD'den açtığı için etkilenmez.

## [2026-10-17] Harness tek sahip kimliğiyle 50 proje tavanına çarptı
Problem: tüm vakalar tek `X-Client-Id` ile gitti; 50. projeden sonra 429 "Project limit reached" sessizce KAPSAM_DIŞI/BLOCKED sayıldı (T01 160/240, T04 250/300 …).
Çözüm: `harness.run_case` her vakaya `uuid4` sahip verir. Kural: "kapsam dışı" oranı yüksekse önce harness/HTTP hatasına bak.

## [2026-10-17] Codex paketlerinde yol kökü
Problem: onarım paketleri `tools/...`, `docs/...` yazdı; worktree kökü depo kökü (`pressure-vessel-suite/` alt klasörde) → Codex yolu bulamayıp hiçbir şey yazmadan döndü (çıkış 4 "hiçbir değişiklik üretmedi"); betik logu siliyor.
Çözüm: pakete "YOL KURALI: tüm yollar `pressure-vessel-suite/` köküne göre" satırı. Codex'in yazabildiğini boş klasörde küçük testle önce kanıtla.

## [2026-10-17] "Bağımsız" sütun API'nin kopyası olabilir
Problem: Haiku CSV'sinde `t_hesap` = `t_api` (300/300, string eşit). Kural: referans önce ayrı dosyaya yazılır (zaman damgası kanıt), API sonra çağrılır, karşılaştırma en sonda; birebir eşit string kırmızı bayraktır.

## [2026-10-17] Nozul oranı üç kez ters okundu
`utilization_ratio` nozulda mevcut/gerekli; test "≤1 PASS" varsaydı ve yüzlerce PASS'i BULGU saydı (T32, T51, T04). Bileşen türüne göre kural ayır.

## [2026-10-17] Kendi bulgumu madde metniyle sına
B-07'yi (nozul t_r E=1) hata sanmıştım; UG-37(a) t_r'yi dikişsiz kabuk için tanımlıyor → yanlış alarm. Bağımsız hesap formülün DOĞRU olduğunu değil yalnız tutarlı olduğunu kanıtlar.

## [2026-10-17] str tabanlı Enum'larda `str()` değeri vermez
`class X(str, Enum)` için `str(X.A)` → 'X.A'. HTML yardımcısında `isinstance(v, Enum)` ile `.value` al (report_engine `_esc`, compliance `esc`).

## [2026-10-17] Ajan worktree'si editable kurulumda ana ağaç kodunu yükler
Çözüm: PYTHONPATH'e worktree'nin suite kökü + `packages/*/src` başa eklenir; `python -c "import X; print(X.__file__)"` ile doğrula.
