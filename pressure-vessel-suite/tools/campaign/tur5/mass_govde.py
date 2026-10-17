"""Kütle gövde koşusu: N tohumlu vaka, API t_required ve MAWP, bağımsız UG-27 formülüyle karşılaştırılır.

Bağımsız formül (bu dosyada yazılmıştır, suite kodu okunmadı):
  R_c = D_i/2 + CA_i
  t_req = P·R_c / (S·E − 0.6·P)
  t_net = t_nom·(1 − mill) − CA_i − CA_o
  MAWP = S·E·t_net / (R_c + 0.6·t_net)
CA_o MAWP'de düşülmelidir (bkz. BULGULAR.md B-01); bu koşu bunu ayrıca etiketler.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import find_results, run_case, value_of

HERE = Path(__file__).resolve().parent
TOL = 0.01


def _cases(n: int, seed: int):
    rng = random.Random(seed)
    for i in range(n):
        d = rng.uniform(300, 4000)
        p = rng.uniform(0.2, 8.0)
        s = rng.choice((100.0, 120.0, 138.0, 150.0, 175.0, 200.0))
        e = rng.choice((0.7, 0.85, 1.0))
        cai = rng.choice((0.0, 1.0, 2.0, 4.0))
        cao = rng.choice((0.0, 1.0, 2.0))
        mill = rng.choice((0.0, 6.0, 12.5))
        t_nom = rng.choice((8.0, 12.0, 20.0, 30.0))
        project = vertical_leg_tank()
        project["project_number"] = f"MASS-{seed}-{i:04d}"
        shell = project["shell_sections"][0]
        shell.update(inside_diameter=round(d, 3), outside_diameter=None, nominal_thickness=t_nom,
                     internal_corrosion_allowance=cai, external_corrosion_allowance=cao,
                     mill_tolerance=mill)
        project["design_conditions"].update(design_pressure=round(p, 4), operating_pressure=round(p, 4),
                                            maximum_allowable_pressure_ps=round(p, 4))
        project["materials"][0]["allowable_stress"] = s
        project["welds"][0]["joint_efficiency"] = e
        yield {"id": f"MASS-{seed}-{i:04d}", "D_i": d, "P": p, "S": s, "E": e, "CA_i": cai,
               "CA_o": cao, "mill": mill, "t_nom": t_nom}, project


def _indep(c):
    rc = c["D_i"] / 2 + c["CA_i"]
    t_req = c["P"] * rc / (c["S"] * c["E"] - 0.6 * c["P"])
    t_net = c["t_nom"] * (1 - c["mill"] / 100) - c["CA_i"] - c["CA_o"]
    mawp = c["S"] * c["E"] * t_net / (rc + 0.6 * t_net)
    mawp_no_cao = c["S"] * c["E"] * (t_net + c["CA_o"]) / (rc + 0.6 * (t_net + c["CA_o"]))
    return t_req, mawp, mawp_no_cao


def _rel(a, b):
    return abs(a - b) / abs(b) if b else (0.0 if a == b else float("inf"))


def run(n: int = 500, seed: int = 20261017) -> dict:
    out_rows = []
    for c, project in _cases(n, seed):
        outcome = run_case(project)
        payload = outcome.get("payload") or {}
        res = find_results(payload, component_id="SHELL-01", clause_prefix="UG-27")
        th = next((r for r in res if r.get("calculation_type") == "thickness"), None)
        mw = next((r for r in res if r.get("calculation_type") == "mawp"), None)
        t_api = value_of(th, "t_required") if th else None
        m_api = mw.get("final_result") if mw else None
        t_ind, m_ind, m_no_cao = _indep(c)
        if outcome.get("http_status") != 200 or t_api is None:
            verdict = "API_VERI_YOK"
        else:
            dt = _rel(t_api, t_ind)
            dm = _rel(m_api, m_ind) if m_api is not None else None
            if dt > TOL:
                verdict = "SAPMA_T_REQ"
            elif dm is None:
                verdict = "API_MAWP_YOK"
            elif dm <= TOL:
                verdict = "UYUŞUR"
            elif c["CA_o"] > 0 and _rel(m_api, m_no_cao) <= TOL:
                verdict = "SAPMA_CAO_MAWP"  # bilinen B-01 kalıbı
            else:
                verdict = "SAPMA_MAWP"
        out_rows.append({**c, "t_api": t_api, "t_ind": round(t_ind, 6), "mawp_api": m_api,
                         "mawp_ind": round(m_ind, 6), "verdict": verdict,
                         "http": outcome.get("http_status")})
    counts = {}
    for r in out_rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    csv_path = HERE / f"mass_govde_{seed}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    summary = {"n": n, "seed": seed, "counts": counts, "csv": str(csv_path)}
    (HERE / f"mass_govde_{seed}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    print(json.dumps(run(n), ensure_ascii=False))
