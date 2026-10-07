# F18 — Rüzgâr, deprem ve yük kombinasyonları

## 1. Özet

`results.json` 31 kayıt içerir: 18 rüzgâr hızı/bölge/ölçü ızgara vakası, 6 sınır/geçersiz girdi, 6 yük faktörü varyantı ve 1 yayınlanmış vaka. Etiket dağılımı: DOĞRULANDI 0 · FORMÜLASYON_FARKI 0 · SAPMA 0 · TEK_KAYNAK 1 · KAYNAK_BEKLİYOR 30 · KAPSAM_DIŞI 0. API hesap payload'ında rüzgâr/deprem satırı bulunmadığından nicel kıyas yapılamadı.

## 2. Oracle formülleri

1. Düzgün dağılmış rüzgâr yükü için dinamik basınç: `q = 0.613 V²` (N/m²).
2. Projeksiyon kuvveti: `F = q Cf A`; düzgün dağılım varsayımıyla taban momenti `M = F h/2`.
3. Deprem taban kesmesi: `V = Cs W`. Faktörlü bileşim `Σ γᵢ Lᵢ`; devrilme momenti `V h/2`.
4. Bu denklemler temel bağımsız kontrollerdir; `Cf`, ağırlık, etkin yükseklik ve API'den eşleşen sonuç olmadığı için vaka başına sayısal oracle üretilemedi.

## 3. SAPMA tablosu

SAPMA yok. Rüzgâr/deprem API sonucu bulunmadığı için suite ve oracle değerleri kıyaslanamadı; emniyetsiz/emniyetli yön tayin edilemez. İlgili 30 kayıt `KAYNAK_BEKLİYOR` etiketlidir.

| case_id | suite | oracle | fark | yön | açıklama |
|---|---:|---:|---:|---|---|
| GRID-01…18, EDGE-*, INVALID-*, MISSING-WIND, FACTOR-* | yok | eşleşen vaka değeri yok | — | tayin edilemez | API payload'ında rüzgâr/deprem sonucu yok |

## 4. Yayınlanmış vakalar

| case_id | Kaynak ve yayınlanmış değer | Suite karşılaştırması | Etiket |
|---|---|---|---|
| K3-19-PUBLISHED | ASCE Petrochemical Committee, *Wind Loads for Petrochemical and Other Industrial Facilities* (2011), §6.4, s.140–149. Ayrıntılı yöntem toplam taban kesmesi 58,868 lb; basit yöntem 82,496 lb. | API'de eşleşen ASCE yöntemi/çıktısı yok. `results.json` ayrıntılı toplamı kaynak değeri olarak saklar. | TEK_KAYNAK |

## 5. Kapsam dışı ve bloklanan vakalar

API, projeleri kabul edip hesap payload'ı döndürdü; ancak payload'larda rüzgâr/deprem hesap satırı olmadığından geçerli varyantlarda hesaplanabilir taban kesmesi/momenti yoktu. Bu yüzden bunları `KAPSAM_DIŞI` diye etiketlemek yerine kaynak eksikliği olarak `KAYNAK_BEKLİYOR` kaydettik. `INVALID-NEGATIVE`, `MISSING-WIND` ve `INVALID-ZONE` de API tarafından BLOCKED dönmedi; eksik/geçersiz durum için zorunlu BLOCKED davranışı doğrulanamadı. K3-19 bağımsız yayınlanmış kaynakla sınırlı kaldı.

## 6. Temiz oda beyanı

Oracle, basınç ve yük hesaplama implementasyonlarını okumadan bu ailede sıfırdan yazılmış temel denklemleri kullanır. Yasaklı paketler açılmadı; suite değerleri yalnızca kampanya harness'inin API payload'ından okunmaya çalışıldı. Domain şeması, harness belgeleri/kodları, kaynak politikası ve K3 kaynak kaydı okundu. `.project-ai/ORKESTRA.md` worktree'de bulunmadı. Temiz oda kuralına uyuldu.
