"""python -m tools.campaign.tur7.run : 1) ref.csv  2) api.csv  3) sonuc.csv (sira zorunlu)."""
import csv
from pathlib import Path

from tools.campaign.tur7 import oracle
from tools.campaign.tur7.cases import cases

HERE = Path(__file__).resolve().parent


def write_ref(cs):
    cols = ["id", "type", "subgroup", "D_i", "P", "S", "E", "CA", "crown_depth", "nozzle_d",
            "neck_t", "ref_value", "ref_value_V2", "ref_value_dcorr_V1", "ref_value_dcorr_V2"]
    with open(HERE / "ref.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for c in cs:
            r = {k: c[k] for k in cols if k in c}
            a = (c["P"], c["S"], c["E"], c["D_i"], c["CA"])
            if c["type"] == "shell":
                r["ref_value"] = repr(oracle.shell_ug27c1(*a))
            elif c["type"] == "head":
                r["ref_value"] = repr(oracle.head_ug32d(*a, crown_depth=c["crown_depth"]))
            else:
                d = c["nozzle_d"]
                r["ref_value"] = repr(oracle.nozzle_A_required(*a, d, use_E=True))
                r["ref_value_V2"] = repr(oracle.nozzle_A_required(*a, d, use_E=False))
                dc = d + 2 * c["CA"]
                r["ref_value_dcorr_V1"] = repr(oracle.nozzle_A_required(*a, dc, use_E=True))
                r["ref_value_dcorr_V2"] = repr(oracle.nozzle_A_required(*a, dc, use_E=False))
            w.writerow(r)


def write_api(cs):
    from tools.campaign.harness import find_results, run_case, value_of
    cols = ["id", "http_status", "ok", "api_value", "api_A1", "api_A_total", "error"]
    with open(HERE / "api.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for c in cs:
            o = run_case(c["project"])
            p = o.get("payload") or {}
            row = {"id": c["id"], "http_status": o.get("http_status"), "ok": o.get("ok"),
                   "error": (o.get("error") or "")[:200]}
            if c["type"] == "shell":
                rs = find_results(p, component_id="SHELL-01", calculation_type="thickness",
                                  clause_prefix="UG-27")
                v = value_of(rs[0], "t_required") if rs else None
            elif c["type"] == "head":
                rs = find_results(p, component_id="HEAD-L", calculation_type="thickness",
                                  clause_prefix="UG-32")
                v = value_of(rs[0], "t_required") if rs else None
            else:
                rs = find_results(p, calculation_type="nozzle_reinforcement")
                v = value_of(rs[0], "A_required") if rs else None
                if rs:
                    row["api_A1"] = value_of(rs[0], "A1")
                    row["api_A_total"] = value_of(rs[0], "A_total")
            row["api_value"] = "" if v is None else repr(v)
            w.writerow(row)


if __name__ == "__main__":
    from tools.campaign.tur7.compare import compare
    cs = cases()
    write_ref(cs)      # API cagrilmadan ONCE
    write_api(cs)
    compare()
