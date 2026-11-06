"""Bloklayıcı geometri tutarlılığı — UI kurallarının Python karşılığı.

Kaynak: apps/web-ui/src/geometryValidation.ts, vesselModel.ts (chainIssues),
geometrySteps/IssuesPanel.tsx (LEG_TOO_SHORT) ve geometrySteps/headDepth.ts
(HEAD_DEPTH_RANGE). Toleranslar UI ile aynıdır. Yalnız bloklayıcı
(blocking: true) kurallar vardır; uyarılar alınmadı.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from domain.enums import Orientation


@dataclass(frozen=True)
class GeometryIssue:
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _htype(h) -> str:
    return h.type.value if hasattr(h.type, "value") else str(h.type)


def _dome_height(h) -> float:
    di = h.inside_diameter
    t = _htype(h)
    if h.crown_depth is not None and h.crown_depth > 0:
        return h.crown_depth
    if t == "torispherical" and h.crown_radius and h.knuckle_radius:
        R, r = h.crown_radius, h.knuckle_radius
        q = (R - r) ** 2 - (di / 2 - r) ** 2
        if R > r and q >= 0:
            return R - math.sqrt(q)
    return {"hemispherical": di / 2, "elliptical": di / 4,
            "torispherical": di / 6, "flat": 0.0}.get(t, di / 4)


def _sequence(p) -> list:
    if p.component_sequence:
        return [(r.component_type, r.component_id) for r in p.component_sequence]
    out = []
    if len(p.heads) > 0:
        out.append(("head", p.heads[0].head_id))
    if len(p.shell_sections) > 0:
        out.append(("shell", p.shell_sections[0].section_id))
    if len(p.heads) > 1:
        out.append(("head", p.heads[1].head_id))
    return out


def _frames(p) -> list:
    """componentFrames karşılığı: dict(id, kind, z0, z1, ri0, ri1, t, side)."""
    lookup = {
        "shell": {s.section_id: s for s in p.shell_sections},
        "cone": {c.cone_id: c for c in p.cones},
        "head": {h.head_id: h for h in p.heads},
    }
    items, seen = [], set()
    for kind, cid in _sequence(p):
        item = lookup[kind].get(cid)
        if cid in seen or item is None:
            continue  # yinelenen/eksik referans domain doğrulayıcısında yakalanır
        seen.add(cid)
        items.append((kind, item))
    frames, z = [], 0.0
    for pos, (kind, it) in enumerate(items):
        prev = frames[-1] if frames else None
        t = it.nominal_thickness
        if kind == "shell":
            if it.inside_diameter is not None:
                ri = it.inside_diameter / 2
            elif it.outside_diameter is not None:
                ri = (it.outside_diameter - 2 * t) / 2
            else:
                ri = 0.5
            length = max(it.tangent_length, 1.0)
            frames.append(dict(id=it.section_id, kind=kind, z0=z, z1=z + length,
                               ri0=ri, ri1=ri, t=t, side=None))
            z += length
        elif kind == "cone":
            large, small = it.large_diameter / 2, it.small_diameter / 2
            pr = prev["ri1"] if prev else None
            expanding = pr is not None and abs(pr - small) < abs(pr - large)
            r0, r1 = (small, large) if expanding else (large, small)
            frames.append(dict(id=it.cone_id, kind=kind, z0=z, z1=z + it.length,
                               ri0=r0, ri1=r1, t=t, side=None))
            z += it.length
        else:
            ri = it.inside_diameter / 2
            sf = max(it.straight_flange_length or 0.0, 0.0)
            dome = _dome_height(it)
            side = "left" if pos == 0 else "right" if pos == len(items) - 1 else "internal"
            frames.append(dict(id=it.head_id, kind=kind, z0=z, z1=z + dome + sf,
                               ri0=0.0 if side == "left" else ri,
                               ri1=0.0 if side == "right" else ri, t=t, side=side))
            z += dome + sf
    return frames


def geometry_blockers(p) -> List[GeometryIssue]:
    """Hesabı engelleyen geometri sorunları (boş liste = geçerli)."""
    issues: List[GeometryIssue] = []
    # Zincir tanımlı değilse (açık component_sequence yok ve UI'nin varsayılan
    # bombe-gövde-bombe zinciri kurulamıyorsa) proje bileşen-düzeyi girdidir:
    # zincire dayalı kurallar (sıra, çap eşleşmesi, ayak boyu) uygulanmaz.
    chain_defined = bool(p.component_sequence) or (
        len(p.shell_sections) == 1 and len(p.heads) >= 2 and not p.cones)
    seq = _sequence(p) if chain_defined else []
    known = {
        "head": {h.head_id for h in p.heads},
        "shell": {x.section_id for x in p.shell_sections},
        "cone": {c.cone_id for c in p.cones},
    }
    seen_refs: set = set()
    for i, (kind, cid) in enumerate(seq):
        if (kind, cid) in seen_refs:
            issues.append(GeometryIssue(f"sequence-duplicate-{i}", f"{kind}:{cid} zincirde birden fazla kullanılamaz."))
        seen_refs.add((kind, cid))
        if cid not in known[kind]:
            issues.append(GeometryIssue(f"sequence-missing-{i}", f"{kind}:{cid} gerçek bileşen dizisinde bulunamadı."))
    if len(seq) >= 2 and (seq[0][0] != "head" or seq[-1][0] != "head"):
        issues.append(GeometryIssue("sequence-terminals", "Zincirin iki terminalinde bombe bulunmalıdır."))

    for s in p.shell_sections:
        if s.tangent_length <= 0:
            issues.append(GeometryIssue(f"shell-{s.section_id}-length", f"{s.section_id} teğet uzunluğu 0'dan büyük olmalıdır."))
    for c in p.cones:
        if c.large_diameter <= c.small_diameter:
            issues.append(GeometryIssue(f"cone-{c.cone_id}-diameter-order", f"{c.cone_id} büyük çapı küçük çapından büyük olmalıdır."))
        if c.half_apex_angle > 30:
            issues.append(GeometryIssue(f"cone-{c.cone_id}-knuckle-review", f"{c.cone_id}: α > 30° için torikonik/knuckle veya özel analiz gerekir."))
    for n in p.nozzles:
        if n.inside_diameter >= n.outside_diameter:
            issues.append(GeometryIssue(f"nozzle-{n.tag}-diameter", f"{n.tag} iç çapı dış çaptan küçük olmalıdır."))

    for h in p.heads:
        d = h.crown_depth
        if _htype(h) == "elliptical" and d is not None and d > 0:
            ratio = h.inside_diameter / (2 * d)
            if not (1 - 1e-9 <= ratio <= 3 + 1e-9):
                issues.append(GeometryIssue("HEAD_DEPTH_RANGE",
                    f"{h.head_id}: kubbe derinliği h = {d:g} mm geçersiz — 1 ≤ D/2h ≤ 3 gerekir (şu an {ratio:.2f})."))

    frames = _frames(p) if chain_defined else []
    last: Optional[dict] = None
    for fr in frames:
        if fr["side"] == "internal":
            issues.append(GeometryIssue("INTERNAL_HEAD", f"{fr['id']} zincirin ortasında."))
            continue
        if last is not None and abs(last["ri1"] - fr["ri0"]) > 0.5:
            issues.append(GeometryIssue("DIAMETER_MISMATCH",
                f"{last['id']} → {fr['id']}: iç çap {2 * last['ri1']:.1f} ≠ {2 * fr['ri0']:.1f} mm."))
        last = fr

    if frames and p.orientation == Orientation.VERTICAL:
        first = frames[0]
        left = first["z1"] if first["side"] == "left" else first["z0"]
        bottom = first["z0"] - first["t"] if first["side"] == "left" else first["z0"]
        for s in p.supports:
            if s.type != "leg":
                continue
            z_top = left + s.location_mm
            if z_top - s.height_mm > bottom + 1e-6:
                issues.append(GeometryIssue("LEG_TOO_SHORT",
                    f"{s.support_id}: ayak kap altına ulaşmıyor — profil boyu en az "
                    f"{z_top - bottom:.0f} mm olmalı (şu an {s.height_mm:.0f} mm)."))
    return issues
