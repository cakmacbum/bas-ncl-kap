"""Run T12 material consistency checks against suite material helpers."""
import json
from pathlib import Path

from materials.data_pack import interpolate_pack_property
from tools.campaign.tur2.t12_malzeme_db.cases import cases

OUT = Path(__file__).parent

def run():
    rows = []
    for c in cases():
        observed = None
        expected = c.get("expected")
        verdict = "GEÇTİ"
        if c["kind"] == "temperature":
            verdict, observed = "KAPSAM_DIŞI", "eğri verisi yok"
        elif c["kind"] == "monotonic":
            observed = [b[1] <= a[1] for a, b in zip(c["points"], c["points"][1:])]
            if not all(observed): verdict = "BULGU"
        elif c["kind"] in ("linear", "boundary"):
            observed = interpolate_pack_property(c["points"], c["temperature"])
            if abs(observed - expected) > 1e-9: verdict = "BULGU"
        elif c["kind"] == "outside":
            try:
                observed = interpolate_pack_property(c["points"], c["temperature"])
                verdict = "BULGU"
            except LookupError:
                observed = "BLOCKED"; expected = "BLOCKED"
        else:
            observed = c["minimum"] <= c["maximum"]
            expected = True
            if not observed: verdict = "BULGU"
        rows.append({"vaka": c["id"], "girdi": {k:v for k,v in c.items() if k not in ("id",)}, "beklenen": expected, "gözlenen": observed, "sonuç": verdict})
    (OUT / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows

if __name__ == "__main__":
    run()
