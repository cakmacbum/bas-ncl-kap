# PAKET T63 — Tam döngü: planla, yaz, koş, kendi kontrolünü yap

> Proje: BASINCLI-KAP · M2 Tur 6 · Yürütücü: codex:yaz · 2026-10-17
> Mod: yaz → ≤10 satır rapor
> YOL KURALI: Tüm yollar `pressure-vessel-suite/` köküne göredir.

## Rol ve sınır
Sen bu turda kampanya yöneticisisin. Planı sen yazıyorsun, testleri sen yazıyorsun, koşturuyorsun, sonucu sen
kontrol ediyorsun. Bir şeyi atlayıp başkasının yapmasını bekleme.

## Adım 1 — Plan (`docs/validation/campaign-2026-10/tur6/T63-plan.md`)
Hedef: iki bileşen için 240 vaka (120 + 120).
- A: nozul takviyesi (`nozzle_reinforcement`), tek tip girdi aralıkları: D_i 300–2500, nozul d/D 0.05–0.4,
  P 0.2–8, S 100–200, E 0.85–1.0. Kontrol: API'nin `utilization_ratio` (mevcut/gerekli) ≥ 1 ⇔ PASS.
- B: eliptik bombe UG-32(d) t_required. Bağımsız formül: R_c = D_i/2 + CA_i, t = P·D_c/(2·S·E − 0.2·P),
  D_c = D_i + 2·CA_i, K=1. API `t_required` ile ±%1.
Planı yaz: kaç vaka, hangi parametre, hangi kontrol, kabul kriteri.

## Adım 2 — Yaz (`pressure-vessel-suite/tools/campaign/tur6/t63_dongu/`)
- `__init__.py`, `cases.py` (tohum 630; her bileşen 120 vaka), `run.py` (her vakayı
  `tools.campaign.harness.run_case` ile çalıştırır; her iki bileşen için bağımsız kontrolü yazar).
- Bağımsız kontrolleri kendin yaz; suite kodu (`packages/**`) OKUMA.

## Adım 3 — Koş
`python -m tools.campaign.tur6.t63_dongu.run` — hatasız bitmeli; `results.json` 240 satır.

## Adım 4 — Kendi kontrolün
Sonuçları say: her bileşen için UYUŞUR / UYUŞMUYOR / VERİ_YOK. Tutarsızlık varsa, nedenini bir
cümleyle yaz (girdi mi, formül mü, API mi). `kontrol.json` olarak yaz: bileşen başına sayılar.

## Adım 5 — Rapor (`docs/validation/campaign-2026-10/tur6/T63.md`)
Plan özeti, sayılar, tutarsızlık açıklaması. Son satır:
`SONUÇ: vaka=240 · uyuşur=a · uyuşmaz=b · veri_yok=c · kendi_kontrol=tamam|eksik`

## Kapsam
Yalnız `tools/campaign/tur6/t63_dongu/` ve `docs/validation/campaign-2026-10/tur6/`. `packages/**`, `apps/**`,
`harness.py` değiştirme.

## Kabul
Plan dosyası, 240 satırlık `results.json`, `kontrol.json`, rapor ve SONUÇ satırı var.
