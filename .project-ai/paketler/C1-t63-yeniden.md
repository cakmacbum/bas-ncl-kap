# PAKET C1 — T63 yeniden: bağımsız nozul kontrolü + eliptik crown_depth + T45 torisferik

> Proje: BASINCLI-KAP · M2 kapanış · Yürütücü: codex:yaz
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir. `packages/**` ve `apps/**` DOKUNMA.

## Görev
`tools/campaign/tur6/t63_dongu/` içindeki önceki sürümde iki hata vardı:
1. Nozul kontrolü bağımsız değer üretmiyordu ("UYUŞUR" boş geçiş). Düzelt: referans `required_area`'yı UG-37(a) ile sıfırdan hesapla
   (A_req = d·t_r·F + 2·t_n·t_r·F·(1−f_r1), t_r = P·R/(S·E−0.6P), E=1 host için, F=1), referansı API çağrısından ÖNCE `ref.csv`'ye yaz,
   sonra API'yi çağır ve ±%1 kıyasla (`utilization_ratio` mevcut/gerekli; PASS ⇔ ≥1). API değerini referans sütununa ASLA kopyalama.
2. Eliptik testte 9 "uyuşmazlık" test tanımı hatasıydı (crown_depth). Girdide `crown_depth` kullanma/yanlış verme; t_required kıyası
   t = P·D_c/(2SE−0.2P), D_c = D_i+2CA_i, ±%1.
3. T45: torisferik (UG-32(e), standart F&D L=D_o, r=0.06L ve özel L/r) 60 vaka, aynı bağımsız-referans disiplini.
Çalıştır: `python -m tools.campaign.tur6.t63_dongu.run`; sonuç `results.json`, sayılar `kontrol.json`.
Rapor: `docs/validation/campaign-2026-10/tur6/C1.md` (≤40 satır, UYUŞUR/UYUŞMUYOR sayıları; sapma varsa girdi özeti).
