# A2a Denetim - G1 (Adım 1, 2, geometri 3.1-3.2)
Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME (salt-okur). ZAMAN SINIRI SERT: toplam 12 dakikan var. Kodu bütün olarak okuma; yalnız aşağıda adı geçen alanlar için `grep`/arama ile ilgili birkaç satırı bul. 8. dakikada aramayı bırak ve raporu YAZ (eksik kalsa da yaz; "KISMİ" işaretle). Rapor yazılmazsa tüm iş kaybolur.
Rapor: ≤30 satır, önem sırasıyla KRİTİK/ORTA/DÜŞÜK; her maddede `<dt>` etiketi + sorun + doğru bilgi + doğruladığın dosya:satır. İlk satır `A2a denetim-g1 - TAMAM | KISMİ`.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-G1.html` alan anlatımını kodla karşılaştır. Önce parçada şu 12 alanı bul ve kod karşılığını doğrula (`pressure-vessel-suite/apps/web-ui/src/pages.tsx` içinde etiketi `grep`le; hesap etkisi için `pressure-vessel-suite/packages/*/src`):
tasarım basıncı, tasarım sıcaklığı, dış basınç/vakum, korozyon payı, iç çap, silindir uzunluğu/boyu, bombe tipi seçenekleri, kaynak verimi (E), akışkan/yoğunluk, basınç tahliye ayarı, hesap rotası (standart/sürüm), yönelim (dikey/yatay).
Her biri için: birim doğru mu, varsayılan doğru mu, "arttırırsanız ne olur" iddiası fiziksel/kodsal olarak doğru mu? Ayrıca telifli standart tablosundan sayı verilmişse (K6) işaretle.
