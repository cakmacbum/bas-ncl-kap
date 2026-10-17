# T41 onarım — T01 metamorfik sınıflandırma

Yeniden çalıştırılan `tools/campaign/tur2/t01_metamorfik/run.py` 240 vaka üretti. Sınıflandırma `results.json` içindeki `result` alanını değil, `expected`, `observed` ve ardışık ölçüm değerlerini esas alır. Tam sınıflandırma: `tools/campaign/tur2/t01_metamorfik/results_v2.json`.

## Durum dağılımı

- GEÇTİ: 120
- BULGU: 0
- BLOCKED_BEKLENEN: 120 (çıkarılabilir sonuç bulunmadı; dört bileşen ailesi)
- KAPSAM_DIŞI: 0
- geçersiz_test: 0

## Monotonluk yönü denetimi

Altı ilişkinin her biri, sekiz bileşen ailesinde (48 ilişki grubu) incelendi. P↑ → t_required↑, S↑ → t_required↓, CA↑ → nominal gereksinim↑, E↓ → t_required↑, nominal kalınlık↑ → MAWP↑ ve sıcaklık↑/S↓ → t_required↑ yönleri gözlenen tüm sayısal ardışık sonuçlarda sağlandı. Yön hatası: yok.

Sonuç yok vakaları: düz kapak, koni, nozul ve dış basınç grupları. Bu gruplarda beş örnek üzerinden ilişkisel karşılaştırma yapılamadı; bunlar geçer/bulgu sayılmadı.

SONUÇ: vaka=240 · GEÇTİ=120 · BULGU=0 · BLOCKED=120 · KAPSAM_DIŞI=0 · geçersiz_test=0
