# A2b Denetim - G2 (geometri 3.3, 3.4, 3.5)
Mod: oku
Proje kökü: BASINCLI-KAP (git). Uygulama: `pressure-vessel-suite/`.

KURAL: Kabuk komutu çalıştırma; dosya DEĞİŞTİRME (salt-okur). ZAMAN SINIRI SERT: toplam 12 dakikan var. Kodu bütün olarak okuma; yalnız aşağıda adı geçen alanlar için `grep`/arama ile ilgili birkaç satırı bul. 8. dakikada aramayı bırak ve raporu YAZ (eksik kalsa da yaz; "KISMİ" işaretle). Rapor yazılmazsa tüm iş kaybolur.
Rapor: ≤30 satır, önem sırasıyla KRİTİK/ORTA/DÜŞÜK; her maddede `<dt>` etiketi + sorun + doğru bilgi + doğruladığın dosya:satır. İlk satır `A2b denetim-g2 - TAMAM | KISMİ`.

## Görev
`pressure-vessel-suite/docs/kilavuz2/parca-G2.html` (nozul, manşon, mesnet) alan anlatımını kodla karşılaştır. Şu 12 alanı bul ve doğrula: nozul dış çap, nozul et kalınlığı, nozul konumu/açısı, nozul tipi (flanşlı/boru), takviye pedi, eğik nozul, manşon boyu, ayak sayısı, eyer açısı (teta), eyer konumu (A mesafesi), etek yüksekliği, mesnet malzeme/profil seçimi. Etiketleri `pressure-vessel-suite/apps/web-ui/src/pages.tsx` içinde `grep`le; hesap etkisini `pressure-vessel-suite/packages/nozzles/src` ve `packages/supports/src` (varsa) içinde ara.
Her biri için: birim doğru mu, varsayılan doğru mu, "arttırırsanız ne olur" doğru mu? Telifli tablo değeri (Zick katsayıları vb.) verilmişse işaretle.
