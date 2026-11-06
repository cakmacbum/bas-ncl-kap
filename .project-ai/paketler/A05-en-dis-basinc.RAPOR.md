# RAPOR A05-en-dis-basinc

> Yürütücü: agy gemini-3.8-flash-high (yaz) · 2026-11-07 00:19
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/A05 · Dal: ork/A05 · Taban: 20f1018
> Token: 623530 / 92888 / 716418 (girdi/çıktı/toplam)

A05 EN 13445 Dış Basınç (8.5 / 8.7) — TAMAM
Dosyalar: packages/code-en-13445/src/code_en_13445/external_pressure.py (yeni), packages/code-en-13445/src/code_en_13445/design_code.py (yalnız check_external_pressure + yardımcılar), tests/faz4/test_en13445_external_pressure.py (yeni)
Test: pytest tests/faz4/test_en13445_external_pressure.py -> koşulamadı (RunCommand yasağı; şef koşacak; el hesapları adım adım rel_tol <= %0,5 ile test dosyasına yazıldı)
Sözleşme: uyuldu | sapma: yok (RunCommand kullanılmadı, commit atılmadı, ASME fallback yok, kapsam dışı dosyalara dokunulmadı)
L için kullanılan alan: shell.tangent_length + (1/3)*head_1_depth + (1/3)*head_2_depth (Domain modelinde takviye halkası alanı bulunmadığından Madde 8.5 kuralı ve add_assumption ile hesaplandı)
Kullanılan formüller:
- Silindir (8.5): e_a = e - c - delta_e; p_m(n) von Mises / 8.5.2 (Z=pi*R/L, n=2..20 minimize); p_y = sigma_e*e_a/R; p_r/p_y Şekil 8.5-5 (parçalı elastoplastik geçiş); P_allow = p_r/1.5
- Küre/Bombe (8.7): p_m = 1.21*E*e_a^2/R^2; p_y = 2*sigma_e*e_a/R; Şekil 8.7-1 (p_r/p_y); P_allow = p_r/1.5; R torisferik taç yarıçapı veya elipsoidal 7.5.4 eşdeğer Rc
- Durum akışı: PASS olan her sonuç self._cap_unverified ile REVIEW_REQUIRED yapılır; eksik veri NOT_CALCULATED/BLOCKED; düz kapak ve koni _unsupported_result
Açık soru / risk: Şekil 8.5-5 ve Şekil 8.7-1 p_r/p_y geçiş eğrileri lisanslı grafik tablosu yerine bellekten analitik parçalı fonksiyonla yazılmıştır (verified=False); bağımsız mühendis onayı gerekir.

```
 .../code-en-13445/src/code_en_13445/design_code.py | 359 +++++++++++++++++++-
 .../src/code_en_13445/external_pressure.py         | 344 ++++++++++++++++++++
 .../tests/faz4/test_en13445_external_pressure.py   | 361 +++++++++++++++++++++
 3 files changed, 1046 insertions(+), 18 deletions(-)
```
