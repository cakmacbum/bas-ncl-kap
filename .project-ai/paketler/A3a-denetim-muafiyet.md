# A3a Denetim - G3 kritik kısım: muafiyet beyanı, malzeme, Adım 4
Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME (salt-okur). ZAMAN SINIRI SERT: toplam 12 dakikan var. Kodu bütün olarak okuma; yalnız aşağıda adı geçen alanlar için `grep`/arama ile ilgili birkaç satırı bul. 8. dakikada aramayı bırak ve raporu YAZ (eksik kalsa da yaz; "KISMİ" işaretle). Rapor yazılmazsa tüm iş kaybolur.
Rapor: ≤30 satır, önem sırasıyla KRİTİK/ORTA/DÜŞÜK; her maddede `<dt>` etiketi + sorun + doğru bilgi + doğruladığın dosya:satır. İlk satır `A3a denetim-muafiyet - TAMAM | KISMİ`.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-G3.html` içinde SADECE şu üç yeri denetle:
1. **Küçük açıklık muafiyeti (UG-36(c)(3)) beyanı:** üç onay kutusunun anlatımı, `pressure-vessel-suite/packages/nozzles/src/nozzles/reinforcement.py` içindeki `_apply_ug36c3` gerçek davranışıyla uyuşuyor mu? Doğru davranış: ÜÇ beyanın hepsi işaretlenmeden muafiyet uygulanmaz; eksikse sonuçta "UYGULANMADI" bildirimi çıkar; muafiyet uygulansa bile boyun et kalınlığı kontrol edilir; çap sınırları 89 mm / 60 mm civarı (sayıları kodda doğrula). Uyumsuzluk = KRİTİK.
2. **Malzeme alanları (izin verilen gerilme, akma, çekme):** parçada sayı verilmiş mi (verilmemeli)? Boş/0 bırakılınca ne olduğu doğru mu (hesap hata/422 verir mi, `pressure-vessel-suite/apps/web-ui/src/apiErrors.ts` ve `packages/domain/src/domain/materials*.py` ile doğrula)?
3. **Adım 4 (Hesap Sonuçları) anlatımı:** PASS/FAIL, MAWP, hidrotest, notlar/varsayımlar alanlarının anlatımı gerçek sonuç alanlarıyla (`pressure-vessel-suite/apps/api` yanıt şeması / `CalculationResult`) uyumlu mu?
