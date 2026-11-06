# RAPOR B05-en-nozul-takviye

> Yürütücü: agy gemini-3.8-flash-high (yaz) · 2026-11-07 00:00
> Worktree: /c/Users/yusuf/.orkestra-wt/BASINCLI-KAP/B05 · Dal: ork/B05 · Taban: 20f1018
> Token: 164659 / 47338 / 211997 (girdi/çıktı/toplam)

B05 EN 13445-3 Madde 9 nozul takviyesi — TAMAM
Dosyalar: packages/code-en-13445/src/code_en_13445/openings.py (yeni) · packages/code-en-13445/src/code_en_13445/design_code.py (calculate_nozzle) · tests/faz4/test_en13445_nozzle_reinforcement.py (yeni)
Test: pytest tests/faz4/test_en13445_nozzle_reinforcement.py -> koşulamadı (RunCommand kesin yasağı; şef koşacak)
Sözleşme: uyuldu | sapma: yok
Formüller: 9.5.2 (Af_s+Af_w)(f_s−0.5P) + Af_p(f_op−0.5P) + Af_b(f_ob−0.5P) ≥ P(Ap_s+Ap_b+0.5Ap_φ); f_ob=min(f_b,f_s), f_op=min(f_p,f_s); l_so=√((2R_is+e_c)e_c); l_bo=√((d_eb−e_b)e_b); l'_bi=min(c_i, 0.5l_bo); Af_s=l_so·e_c; Af_b=e_b(l'_bo+l'_bi+e_c); Af_p=l'_p·e_p; Af_w=0; Ap_s=R_is(l_so+a) (silindir) ve 0.5R_is(l_so+a) (bombe sadeleştirilmiş küre); Ap_b=0.5d_ib(l'_bo+e_c); Ap_φ=0 (dik).
Domain alanları: Nozzle (outside/inside_diameter, neck_thickness, outside/inside_projection, inclination_angle, reinforcement_pad/_thickness/_od, corrosion_allowance), ShellSection, Head (torispherical, elliptical, hemispherical, flat), DesignConditions, MaterialProperty.
Uygulanan kurallar: Eğik nozul (inclination ≠ 0) ve Madde 9.4 sınırları (d_ib/D_is > 1.0, e_c/D_is > 0.1) → OUT_OF_SCOPE; koni/düz kapak nozulları → NOT_CALCULATED; PASS asla dönmez, _cap_unverified ile REVIEW_REQUIRED'a çekilir; ASME UG-37'ye hiçbir fallback yapılmadı.
Açık soru / risk: Formüller bellekten uygulandı (verified=False); lisanslı EN 13445-3:2021 Madde 9 metniyle resmi doğrulama gereklidir.

```
 .../code-en-13445/src/code_en_13445/design_code.py | 297 +++++++++++-
 .../code-en-13445/src/code_en_13445/openings.py    | 198 ++++++++
 .../faz4/test_en13445_nozzle_reinforcement.py      | 537 +++++++++++++++++++++
 3 files changed, 1026 insertions(+), 6 deletions(-)
```
