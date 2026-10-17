# T63 plan — Tam döngü kampanyası

Tohum: 630. Toplam 240 API vakası; her bileşen için 120 vaka.

| Bileşen | Vaka girdileri | Bağımsız kontrol | Kabul kriteri |
|---|---|---|---|
| A — `nozzle_reinforcement` | D_i 300–2500 mm, nozul d/D 0.05–0.4, P 0.2–8 MPa, S 100–200 MPa, E 0.85–1.0. Nozul dış çapı d + 2t_n, pozitif boyun kalınlığı. | API `utilization_ratio` değeri `intermediate_values` ya da final sonuçtan okunur; geçiş eşiği 1.0. | Veri varsa API `PASS` ⇔ utilization ≥ 1 ve `FAIL` ⇔ utilization < 1. Bu karar tutarlı ise UYUŞUR. Sonuç/değer eksikse VERİ_YOK. |
| B — eliptik bombe UG-32(d) | D_i 300–2500 mm, P 0.2–8 MPa, CA_i 0–3 mm, S 100–200 MPa, E 0.85–1.0. | R_c = D_i/2 + CA_i; D_c = D_i + 2·CA_i; K=1 ve t = P·D_c/(2·S·E − 0.2·P). | API `t_required`, bağımsız t ile ±%1 bağıl tolerans içinde ise UYUŞUR; değilse UYUŞMUYOR. Sonuçlardan biri yoksa VERİ_YOK. |

Her bileşende 120 vaka; tekrar üretilebilir parametreler `random.Random(630)` ile üretilir. Sonuç ve bileşen bazlı toplamlar `results.json` ve `kontrol.json` dosyalarında tutulur. `run_case` üzerinden herkese açık API hesaplaması çalıştırılır.
