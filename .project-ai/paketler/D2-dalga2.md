# Dalga 2 — yeni hesap modülleri (P06–P09)
Yol kuralı: yollar `pressure-vessel-suite/` köküne göre. Her paket kendi worktree dalında.
Ortak kabul: `cd apps/web-ui && npm test && npm run build` + `python -m pytest tests/unit tests/api tests/faz5 -q` yeşil; tsconfig.tsbuildinfo
commit dışı; commit sonu `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; Türkçe ≤12 satır rapor. Sessiz kırpma yok (K4):
geçersiz/eksik girdi → issue/BLOCKED, uydurma sayı yok. Kod tablosu/katsayı bellekten emin değilse `verified:false` + kaynak notu.

## Paylaşılan dosya kuralı (çakışmayı küçük tutmak için)
- Hesap kodu YENİ modül dosyasında. Domain modeli yeni dosyada (`packages/domain/src/domain/<ad>.py`); `VesselProject`'e yalnız
  TEK alan eklenir (Optional, varsayılan None) — mevcut alanlar değişmez.
- `packages/code-asme-viii-1/src/code_asme_viii_1/design_code.py`'ye yalnız tek çağrı bloğu (yorumla işaretli `# --- P0N ---`).
  Sonuçlar mevcut check/result yapısıyla döner → rapor otomatik alır; `report-engine` generator'a dokunma.
- UI: yeni dosya `apps/web-ui/src/inputs/<Ad>Inputs.tsx`; `pages.tsx` "Hesap girdileri" sekmesine yalnız tek satır `<XInputs />`
  ve bir import. `types.ts`'e yalnız yeni tip + VesselProject'e tek opsiyonel alan. store.ts'e dokunmak gerekirse yalnız setter.
- Bilerek: birleştirmede şef küçük ekleme çakışmalarını çözer.

## P06 Kaldırma kulağı (lifting lug) + rigging — Sonnet
- Girdi: kulak sayısı, konum (gövde üstü / bombe), plaka kalınlığı/genişlik/delik çapı, kaynak boyu, kaldırma açısı, darbe katsayısı (varsayılan 1,5–2,0 kullanıcı seçer).
- Kontroller: kulak çekme/kesme/yatak (pin hole) gerilmesi, kaynak kesme, gövde yerel gerilmesi (basit WRC-107 benzeri yerine kendi tutucu yaklaşımı; mevcut `supports/wrc.py` yeniden kullanılabiliyorsa kullan).
- Kaynak: ASME BTH-1 / Moss PVDM lifting lug prosedürü (formül kaynağını yoruma yaz). Toplam kütle `calc_core/volume_mass.py`'den.

## P07 WRC 537 / 297 nozul yükü — Opus (çekirdek)
- Mevcut `packages/supports/src/supports/wrc.py` (WRC 107) incele; 537 = 107'nin yeniden düzenlenmiş eğri denklemleri. Eğri katsayılarını
  bellekten güvenle yazamıyorsan uydurma — altyapıyı (eğri arayüzü, geometri sınırları d/D<0,33, gerilme birleştirme, Div.2 sınırları
  Pm/PL/PL+Pb+Q) kur, katsayı tablosunu boş + BLOCKED bırak ve raporda açıkça söyle (P05 deseni).
- WRC 297: nozul tarafı + kabuk tarafı (silindir) — aynı kural.
- Nozul başına yük girdisi (Fr, Vc, VL, Mc, ML, Mt) zaten varsa kullan, yoksa ekle.

## P08 Koni birleşimi App. 1-5 + taban halkası/ankraj — Sonnet
- Önce ASME `design_code.py`/`formulas.py`'de App. 1-5 (Δ, takviye alanı, büyük/küçük uç) var mı bak; eksik kısmı tamamla.
- Skirt varsa taban halkası (base ring) kalınlığı, ankraj cıvatası çekme/kesme (rüzgâr/deprem momenti mevcut `global_loads`'tan varsa; yoksa kullanıcı moment girer), beton basıncı. Kaynak: Moss PVDM Procedure 3-9 / Jawad-Farr.

## P09 Malzeme listesi (BOM) + maliyet tahmini — Sonnet
- `calc_core/volume_mass.py`'den parça bazlı kütle: gövde sacı, bombeler, nozul boruları, flanşlar, pedler, destekler, ayaklar.
- BOM tablosu (parça, malzeme, ölçü, adet, kütle). Maliyet: malzeme €/kg (malzeme başına), kaynak/işçilik saat ve saat ücreti, NDT, boya — TÜM birim fiyatları kullanıcı girer (varsayılan boş = maliyet hesaplanmaz, uyarı).
- Sonuç sayfasında BOM + maliyet kartı, CSV indir. Hesap kodu kontrol (check) değil, bilgi bölümü olarak dönsün.
