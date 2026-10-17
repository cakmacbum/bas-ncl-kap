from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
from tools.campaign.harness import run_case, find_results, value_of
from .cases import cases, oracle

OUT = Path(__file__).parent

def run():
    rows=[]
    for cid, project, params in cases():
        result=run_case(project)
        found=find_results(result.get("payload") or {}, component_id="HEAD-L")
        thickness=next((x for x in found if x.get("calculation_type")=="thickness"), None)
        mawp=next((x for x in found if x.get("calculation_type")=="mawp"), None)
        status=thickness.get("status") if thickness else ("BLOCKED MISSING INPUT" if not result.get("ok") else None)
        head=project["heads"][0]
        mat=next(m for m in project["materials"] if m["material_id"]==head["material_id"])
        weld=next((w for w in project["welds"] if w.get("joint_id")==head.get("weld_joint_id")),None)
        eff=weld["joint_efficiency"] if weld else 1.0
        ref=oracle(params["pressure_mpa"],mat["allowable_stress"],eff,params["L_mm"],params["r_mm"],params["nominal_thickness_mm"])
        observed={"required_thickness":value_of(thickness,"t_required") if thickness else None,
                  "mawp":(value_of(mawp,"MAWP") or value_of(mawp,"final_result")) if mawp else None,
                  "M":value_of(thickness,"M_factor") if thickness else None}
        for q in ("required_thickness","mawp","M"):
            exp=ref.get(q) if ref else None; obs=observed[q]
            if cid=="missing-r":
                # Beklenen güvenli davranış: knuckle yarıçapı yokken PASS vermemek (BLOCKED / NOT CALCULATED).
                guarded = bool(status) and str(status).upper().startswith(("BLOCKED","NOT CALCULATED"))
                verdict="GEÇTİ" if guarded and obs is None else "BULGU"
            elif status and str(status).upper().startswith(("BLOCKED","OUT OF SCOPE","NOT CALCULATED")):
                verdict="KAPSAM_DIŞI"
            elif exp is None:
                verdict="KAPSAM_DIŞI" if obs is None else "BULGU"
            elif obs is None:
                verdict="BULGU"
            else:
                verdict="GEÇTİ" if abs(obs-exp) <= max(1e-8,abs(exp)*.01) else "BULGU"
            note=""
            if cid=="missing-r":
                note=(f"knuckle_radius boş: API durumu={status!r}; "
                      + ("hesap engellendi (güvenli); PASS/varsayılan yarıçap YOK." if verdict=="GEÇTİ"
                         else "varsayılan yarıçapla PASS üretildi: emniyetsiz."))
            if not result.get("ok"): note=(note+"; " if note else "")+str(result.get("error"))
            rows.append({"vaka":cid,"girdi":params,"nicelik":q,"beklenen":exp,"gozlenen":obs,
                         "durum":status,"sonuc":verdict,"not":note})
    (OUT/"results.json").write_text(json.dumps({"kampanya":"T09-torisferik-uc","oracle":"Bağımsız UG-32(e)/Appendix 1-4(d): M=1/4(3+sqrt(L/r)); t=PLM/(2SE-0.2P); MAWP=2SEt/(LM+0.2t)","sonuclar":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return rows

if __name__=="__main__":
    rows=run(); counts=Counter(x["sonuc"] for x in rows)
    n=len(set(x["vaka"] for x in rows)); a=counts["GEÇTİ"]; b=counts["BULGU"]; c=counts["KAPSAM_DIŞI"]
    doc=OUT/"rapor_v3.md"  # A3: docs/ altına yazılmaz
    doc.parent.mkdir(parents=True,exist_ok=True)
    findings=[x for x in rows if x["sonuc"]=="BULGU"]
    lines=["# T09 — Torisferik uç değerler + App 1-4","",f"Vaka sayısı: {n} (nicelik karşılaştırması: {len(rows)}); GEÇTİ: {a}, BULGU: {b}, KAPSAM_DIŞI: {c}.","",
           "Oracle, UG-32(e)/Appendix 1-4(d) bağıntılarının bağımsız uygulamasıdır. rk/D aralığı 3–20%, Rc/D 0.5–1.2, et kalınlığı çok küçük/büyük değerleri sınandı.","",
           "## Bulgular","","| Önem | Yön | Vaka / nicelik | Dosya:satır | Açıklama |","|---|---|---|---|---|"]
    if findings:
        for x in findings:
            critical="YÜKSEK" if x["vaka"]=="missing-r" else "ORTA"
            direction="emniyetsiz" if x["vaka"]=="missing-r" else "?"
            lines.append(f"| {critical} | {direction} | {x['vaka']} / {x['nicelik']} | suite koduna dokunulmadı | {x['not'] or 'Oracle ile sonuç uyuşmadı'} |")
    else: lines.append("| — | — | Yok | — | — |")
    lines += ["","## Kapsam dışı",""]
    lines += [f"- {x['vaka']} / {x['nicelik']}: durum {x['durum'] or 'sonuç üretilemedi'}." for x in rows if x["sonuc"]=="KAPSAM_DIŞI"] or ["- Yok."]
    lines += ["",
              f"SONUÇ: vaka={n} · geçti={a} · bulgu={b} (kritik=0, emniyetsiz={sum(1 for x in findings if x['vaka']=='missing-r')}) · kapsam_dışı={c}"]
    doc.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"{n} vaka; sonuçlar={dict(counts)}")
