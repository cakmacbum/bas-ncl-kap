# A1 Denetim — amaç/hesap bölümü (Gemini denetler, DeepSeek yazmıştı)

Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME (salt-okur). Yalnız oku ve rapor yaz.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-D2.html` basınçlı kap/ASME bilmeyen birine yazılmış "sitenin amacı ve hesap" bölümü. Hedef okur: HİÇBİR şey bilmiyor. Şunlara bak:
1. **Eksik konu:** Böyle bir okur için hangi kavram/adım/uyarı eksik? Site neleri hesaplıyor (`pressure-vessel-suite/docs/calculation-coverage.md`, `docs/limitations.md`) ve bu bölüm bunların hepsini anlatıyor mu? Eksikleri tek tek say.
2. **Anlaşılmaz yer:** Açıklanmadan kullanılan terim/kısaltma, atlanan adım, çok uzun/karmaşık cümle. Alıntıla (kısa) ve basit hâlini öner.
3. **Hata şüphesi:** Teknik olarak yanlış ya da yanıltıcı cümle; sayı/formül uyuşmazlığı (örnek hesaplar `tests/golden_cases/test_hand_calc_ug27_ug32.py` ile birebir mi?). Emin olmadığını "şüpheli" diye işaretle, kesin hükmetme.
4. **Ton/yapı:** Okuru yoruyor mu, sıralama mantıklı mı, hangi bölüm kısaltılmalı/genişletilmeli.
## Çıktı
`.project-ai/paketler/A1-denetim-amac.DONUS.md` (betik üretir). İçerik: ≤40 satır, madde madde, önem sırasıyla (KRİTİK / ORTA / DÜŞÜK), her maddede bölüm adı + alıntı + öneri. İlk satır: `A1 denetim-amac — TAMAM | KISMİ`.
