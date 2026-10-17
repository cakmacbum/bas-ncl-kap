import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _f(x):
    try:
        return float(x) if x not in ("", None, "None") else None
    except ValueError:
        return None


def compare():
    ref = {r["id"]: r for r in csv.DictReader(open(HERE / "ref.csv", encoding="utf-8"))}
    api = {r["id"]: r for r in csv.DictReader(open(HERE / "api.csv", encoding="utf-8"))}
    cols = ["id", "type", "subgroup", "ref_value", "api_value", "rel_err", "durum",
            "ref_V2", "rel_err_V2", "nozul_uyum", "same_string"]
    with open(HERE / "sonuc.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for i, r in ref.items():
            a = api.get(i, {})
            rv, av = _f(r["ref_value"]), _f(a.get("api_value"))
            row = {"id": i, "type": r["type"], "subgroup": r["subgroup"], "ref_value": r["ref_value"],
                   "api_value": a.get("api_value", ""), "ref_V2": r.get("ref_value_V2", ""),
                   "same_string": r["ref_value"] == a.get("api_value", "")}
            if av is None or rv is None:
                row["durum"] = "VERİ_YOK"
            else:
                e = abs(av - rv) / abs(rv)
                row["rel_err"] = repr(e)
                row["durum"] = "UYUŞUR" if e <= 0.01 else "UYUŞMUYOR"
                if r["type"] == "nozzle":
                    r2 = _f(r["ref_value_V2"])
                    e2 = abs(av - r2) / abs(r2)
                    row["rel_err_V2"] = repr(e2)
                    v1, v2 = e <= 0.01, e2 <= 0.01
                    row["nozul_uyum"] = ("V1+V2" if v1 and v2 else "V1" if v1 else
                                         "V2" if v2 else "hiçbiri")
            w.writerow(row)
    rows = list(csv.DictReader(open(HERE / "sonuc.csv", encoding="utf-8")))
    for g in ("shell", "head_std", "head_h", "nozzle"):
        sub = [r for r in rows if r["subgroup"] == g]
        print(g, dict(Counter(r["durum"] for r in sub)))
    print("nozul", dict(Counter(r["nozul_uyum"] for r in rows if r["type"] == "nozzle")))
    print("same_string", sum(r["same_string"] == "True" for r in rows))
