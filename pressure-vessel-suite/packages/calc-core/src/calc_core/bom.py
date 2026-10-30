"""Malzeme listesi (BOM) + maliyet tahmini — P09.

Bu bir KONTROL (check) değil, BİLGİ bölümüdür. Kütleler geometriden türetilir;
gövde/bombe/koni kütlesi tek kaynak `calc_core.volume_mass`'tan gelir (K5).

Kapsam ve yaklaşımlar (K4 — sessiz kırpma yok):
  - Nozul boynu: boru, uzunluk = dış çıkıntı + iç çıkıntı + host cidar kalınlığı
    (host bulunamazsa cidar eklenmez, satır notuna yazılır).
  - Takviye pedi: düz halka π/4(OD_ped² − OD_nozul²)·t (eğrilik ve delik payı yok).
  - Flanş (Appendix 2): halka + hub borusu, yaklaşık (cıvata/conta dahil değil).
  - Destek: etek (silindir kabuk), boru ayak + ayak pedi + taban plakası.
    Eyer ve profil (channel/box/angle) ayakları için katalog/plaka geometrisi
    olmadığından kütle ÜRETİLMEZ (None); toplam "eksik" işaretlenir.
  - Kesim firesi, kaynak metali, cıvata/conta BOM dışı.
Maliyet: tüm birim fiyatları kullanıcı girer; eksikse toplam üretilmez (uydurma yok).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from calc_core.volume_mass import calculate_vessel_volume_mass
from domain.project import VesselProject

_DEFAULT_DENSITY = 7850.0  # volume_mass ile aynı varsayılan


@dataclass
class BomLine:
    part: str
    material_id: str
    material: str
    dimensions: str
    qty: int
    unit_mass_kg: Optional[float]
    note: str = ""

    @property
    def total_mass_kg(self) -> Optional[float]:
        return None if self.unit_mass_kg is None else self.unit_mass_kg * self.qty

    def to_dict(self) -> dict:
        return {
            "part": self.part,
            "material_id": self.material_id,
            "material": self.material,
            "dimensions": self.dimensions,
            "qty": self.qty,
            "unit_mass_kg": _r(self.unit_mass_kg),
            "total_mass_kg": _r(self.total_mass_kg),
            "note": self.note,
        }


@dataclass
class BomReport:
    lines: List[BomLine] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cost: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_mass_kg(self) -> float:
        return sum(l.total_mass_kg or 0.0 for l in self.lines)

    @property
    def mass_complete(self) -> bool:
        return all(l.unit_mass_kg is not None for l in self.lines)

    def to_dict(self) -> dict:
        return {
            "lines": [l.to_dict() for l in self.lines],
            "total_mass_kg": _r(self.total_mass_kg),
            "mass_complete": self.mass_complete,
            "warnings": self.warnings,
            "cost": self.cost,
        }


def _r(v: Optional[float]) -> Optional[float]:
    return None if v is None else round(v, 2)


def _tube_mass(od: float, t: float, length: float, rho: float) -> Optional[float]:
    if od <= 0 or t <= 0 or length <= 0 or 2 * t >= od:
        return None
    return math.pi / 4.0 * (od**2 - (od - 2 * t) ** 2) * length / 1e9 * rho


def _plate_mass(length: float, width: float, t: float, rho: float) -> float:
    return length * width * t / 1e9 * rho


def build_bom(project: VesselProject) -> BomReport:
    rep = BomReport()
    mats = {m.material_id: m for m in project.materials}

    def mat_info(mid: str):
        m = mats.get(mid)
        if m is None:
            rep.warnings.append(f"Malzeme '{mid}' listede yok; yoğunluk {_DEFAULT_DENSITY:.0f} kg/m³ varsayıldı.")
            return mid, _DEFAULT_DENSITY
        return m.material_designation, m.density

    warned: set = set()

    def mat_info_once(mid: str):
        if mid in mats or mid in warned:
            m = mats.get(mid)
            return (m.material_designation, m.density) if m else (mid, _DEFAULT_DENSITY)
        warned.add(mid)
        return mat_info(mid)

    def add(part, mid, dims, qty, mass, note=""):
        name, _ = mat_info_once(mid)
        rep.lines.append(BomLine(part, mid, name, dims, qty, mass, note))

    # Gövde / bombe / koni — volume_mass tek kaynak (sıra: volume_results ↔ mass_results)
    vm = calculate_vessel_volume_mass(project)
    comps: Dict[tuple, Any] = {}
    for s in project.shell_sections:
        comps[("shell", s.section_id)] = s
    for h in project.heads:
        comps[("head", h.head_id)] = h
    for c in project.cones:
        comps[("cone", c.cone_id)] = c
    for vr, mr in zip(vm.volume_results, vm.mass_results):
        comp = comps.get((mr.component_type, mr.component_id))
        if comp is None:
            continue
        if mr.component_type == "shell":
            d = comp.inside_diameter or comp.outside_diameter or 0.0
            dims = f"Ø{d:g} × t{comp.nominal_thickness:g} × L{comp.tangent_length:g}"
            label = "Gövde"
        elif mr.component_type == "head":
            dims = f"Ø{comp.inside_diameter:g} × t{comp.nominal_thickness:g}"
            label = f"Bombe ({comp.type.value})"
        else:
            dims = f"Ø{comp.large_diameter:g}/Ø{comp.small_diameter:g} × t{comp.nominal_thickness:g} × L{comp.length:g}"
            label = "Koni"
        note = ""
        if mr.component_type == "head":
            note = "Hacim bombe tipine göre yaklaşık formülden (volume_mass)."
        add(f"{label} {mr.component_id}", comp.material_id, dims, 1, mr.metal_mass_kg, note)

    # Nozullar + takviye pedleri
    wall_by_host: Dict[str, float] = {}
    for s in project.shell_sections:
        wall_by_host[s.section_id] = s.nominal_thickness
    for h in project.heads:
        wall_by_host[h.head_id] = h.nominal_thickness
    for c in project.cones:
        wall_by_host[c.cone_id] = c.nominal_thickness
    for nz in project.nozzles:
        _, rho = mat_info_once(nz.material_id)
        wall = wall_by_host.get(nz.host_component_id)
        length = nz.outside_projection + nz.inside_projection + (wall or 0.0)
        note = "" if wall is not None else "Host cidar kalınlığı bulunamadı; boy cidarsız."
        if nz.rating_class:
            note = (note + " " if note else "") + "Nozul flanşı (rating) BOM'a dahil değil."
        add(f"Nozul {nz.tag}", nz.material_id,
            f"Ø{nz.outside_diameter:g} × t{nz.neck_thickness:g} × L{length:g}", 1,
            _tube_mass(nz.outside_diameter, nz.neck_thickness, length, rho), note)
        if nz.reinforcement_pad:
            od, t = nz.reinforcement_pad_od, nz.reinforcement_pad_thickness
            if od and t and od > nz.outside_diameter:
                m = math.pi / 4.0 * (od**2 - nz.outside_diameter**2) * t / 1e9 * rho
                add(f"Takviye pedi {nz.tag}", nz.material_id, f"OD{od:g} × t{t:g}", 1, m,
                    "Düz halka yaklaşımı (eğrilik yok).")
            else:
                add(f"Takviye pedi {nz.tag}", nz.material_id, "ölçü eksik", 1, None,
                    "Ped işaretli ama OD/kalınlık girilmemiş veya nozul OD'sinden küçük.")

    # Flanşlar (Appendix 2)
    for fl in project.flanges:
        _, rho = mat_info_once(fl.material_id)
        ring = math.pi / 4.0 * (fl.outside_diameter**2 - fl.inside_diameter**2) * fl.thickness
        t_hub = (fl.hub_small_thickness + (fl.hub_large_thickness or fl.hub_small_thickness)) / 2.0
        hub = math.pi * (fl.inside_diameter + t_hub) * t_hub * fl.hub_length
        add(f"Flanş {fl.flange_id}", fl.material_id,
            f"OD{fl.outside_diameter:g} / ID{fl.inside_diameter:g} × t{fl.thickness:g}", 1,
            (ring + hub) / 1e9 * rho, "Halka + hub borusu yaklaşık; cıvata/conta yok.")

    # Destekler
    for sp in project.supports:
        _, rho = mat_info_once(sp.material_id)
        if sp.type == "skirt":
            if sp.diameter_mm and sp.thickness_mm:
                m = math.pi * sp.diameter_mm * sp.thickness_mm * sp.height_mm / 1e9 * rho
                add(f"Etek {sp.support_id}", sp.material_id,
                    f"Ø{sp.diameter_mm:g}(ort.) × t{sp.thickness_mm:g} × H{sp.height_mm:g}", 1, m)
            else:
                add(f"Etek {sp.support_id}", sp.material_id, "ölçü eksik", 1, None,
                    "Etek ortalama çapı veya kalınlığı girilmemiş.")
        elif sp.type == "leg":
            n = sp.leg_count or 0
            if n and sp.leg_diameter_mm and sp.leg_thickness_mm and not (
                    sp.leg_section_type and sp.leg_section_type != "pipe"):
                add(f"Ayak {sp.support_id}", sp.material_id,
                    f"Ø{sp.leg_diameter_mm:g} × t{sp.leg_thickness_mm:g} × H{sp.height_mm:g}", n,
                    _tube_mass(sp.leg_diameter_mm, sp.leg_thickness_mm, sp.height_mm, rho))
            else:
                add(f"Ayak {sp.support_id}", sp.material_id, "profil", n or 1, None,
                    "Boru dışı profil / eksik ölçü: katalog gömülü değil, kütle üretilmedi.")
            if n and sp.leg_pad_length_mm and sp.leg_pad_width_mm and sp.leg_pad_thickness_mm:
                add(f"Ayak pedi {sp.support_id}", sp.material_id,
                    f"{sp.leg_pad_length_mm:g}×{sp.leg_pad_width_mm:g}×t{sp.leg_pad_thickness_mm:g}", n,
                    _plate_mass(sp.leg_pad_length_mm, sp.leg_pad_width_mm, sp.leg_pad_thickness_mm, rho),
                    "Düz plaka (eğrilik yok).")
            if n and sp.base_plate_length_mm and sp.base_plate_width_mm and sp.base_plate_thickness_mm:
                add(f"Taban plakası {sp.support_id}", sp.material_id,
                    f"{sp.base_plate_length_mm:g}×{sp.base_plate_width_mm:g}×t{sp.base_plate_thickness_mm:g}", n,
                    _plate_mass(sp.base_plate_length_mm, sp.base_plate_width_mm, sp.base_plate_thickness_mm, rho))
        else:
            add(f"Eyer {sp.support_id}", sp.material_id, f"W{sp.width_mm:g} × H{sp.height_mm:g}", 1, None,
                "Eyer plaka/kaburga geometrisi modelde yok; kütle üretilmedi.")

    if not rep.mass_complete:
        rep.warnings.append("Bazı parçaların kütlesi üretilemedi; toplam kütle EKSİKTİR (alt sınır).")
    rep.cost = _cost(project, rep)
    return rep


def _cost(project: VesselProject, rep: BomReport) -> Dict[str, Any]:
    ci = project.cost_inputs
    if ci is None:
        return {"status": "NOT_CALCULATED", "total_eur": None, "items": [],
                "missing": ["Birim fiyatlar girilmedi (Hesap girdileri > BOM maliyet)."]}
    missing: List[str] = []
    items: List[Dict[str, Any]] = []
    mass_by_mat: Dict[str, float] = {}
    for l in rep.lines:
        if l.total_mass_kg:
            mass_by_mat[l.material_id] = mass_by_mat.get(l.material_id, 0.0) + l.total_mass_kg
    for mid, kg in mass_by_mat.items():
        price = ci.material_price_eur_per_kg.get(mid)
        if price is None:
            missing.append(f"Malzeme fiyatı (€/kg): {mid}")
        else:
            items.append({"item": f"Malzeme {mid}", "basis": f"{kg:.1f} kg × {price:g} €/kg",
                          "cost_eur": round(kg * price, 2)})
    if ci.welding_hours is None or ci.labor_rate_eur_per_hour is None:
        missing.append("Kaynak/işçilik saati ve saat ücreti")
    else:
        items.append({"item": "Kaynak/işçilik",
                      "basis": f"{ci.welding_hours:g} sa × {ci.labor_rate_eur_per_hour:g} €/sa",
                      "cost_eur": round(ci.welding_hours * ci.labor_rate_eur_per_hour, 2)})
    for key, label in (("ndt_cost_eur", "NDT"), ("paint_cost_eur", "Boya")):
        v = getattr(ci, key)
        if v is None:
            missing.append(f"{label} bedeli")
        else:
            items.append({"item": label, "basis": "toplam bedel", "cost_eur": round(v, 2)})
    if not rep.mass_complete:
        missing.append("Eksik kütleli parçalar (malzeme maliyeti eksik kalır)")
    complete = not missing
    return {
        "status": "OK" if complete else "INCOMPLETE",
        "total_eur": round(sum(i["cost_eur"] for i in items), 2) if complete else None,
        "partial_eur": None if complete else round(sum(i["cost_eur"] for i in items), 2),
        "items": items,
        "missing": missing,
    }


__all__ = ["BomLine", "BomReport", "build_bom"]
