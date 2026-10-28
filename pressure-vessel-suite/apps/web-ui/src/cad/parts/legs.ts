// D08 — ayaklar: leg_count adet (θᵢ = i·360/n), boru/profil kesiti, gövdeye ped + taban plakası.
// Dikey kap: ayaklar eksene paralel, θᵢ çevresel; üst = supportZ, alt = kap dış altı − height_mm.
// Yatay kap: ayaklar −X'e iner; ikişer sıra (y = ±R·sin35°) halinde eksen boyunca dizilir.
// Kolon yerelde "aşağı −Z, üst z=0" kurulur, sonra yerleştirilir.
import type { Shape3D } from "replicad";
import type { PartModule } from "../../geometryContract";
import type { Support } from "../../types";
import { supportZ } from "../../vesselModel";
import type { Pt } from "../geom";
import { box, cyl, DEG, fuseAll, outerRadiusAt, prism, vesselBottomZ, zHoles } from "./supportGeom";

interface Section {
  h: number;
  w: number;
  solid: (z0: number, z1: number) => Shape3D;
}

function section(p: Support): Section {
  const type = p.leg_section_type ?? "pipe";
  const t = Math.max(p.leg_thickness_mm ?? 6, 1);
  if (type === "pipe") {
    const d = p.leg_diameter_mm ?? 114.3;
    return { h: d, w: d, solid: (a, b) => cyl(d / 2, a, b).cut(cyl(Math.max(d / 2 - t, 0.5), a - 1, b + 1)) };
  }
  const h = p.leg_profile_height_mm ?? p.leg_diameter_mm ?? 100;
  const w = p.leg_profile_width_mm ?? h;
  const tw = p.leg_web_thickness_mm ?? t;
  const tf = p.leg_flange_thickness_mm ?? t;
  if (type === "box") {
    return {
      h, w,
      solid: (a, b) =>
        box(-h / 2, h / 2, -w / 2, w / 2, a, b).cut(box(-h / 2 + tf, h / 2 - tf, -w / 2 + tw, w / 2 - tw, a - 1, b + 1)),
    };
  }
  const pts: Pt[] =
    type === "channel"
      ? [[-h / 2, -w / 2], [h / 2, -w / 2], [h / 2, w / 2], [h / 2 - tf, w / 2], [h / 2 - tf, -w / 2 + tw],
         [-h / 2 + tf, -w / 2 + tw], [-h / 2 + tf, w / 2], [-h / 2, w / 2]]
      : [[-h / 2, -w / 2], [h / 2, -w / 2], [h / 2, -w / 2 + t], [-h / 2 + t, -w / 2 + t], [-h / 2 + t, w / 2], [-h / 2, w / 2]];
  return { h, w, solid: (a, b) => prism(pts, a, b) };
}

export const legs: PartModule<Support> = {
  build(p, frame, ctx) {
    const n = Math.max(Math.round(p.leg_count ?? 4), 1);
    const sec = section(p);
    const vertical = ctx.orientation === "vertical";
    const zA = supportZ(p, ctx.frames);
    const R = outerRadiusAt(ctx.frames, zA, frame);
    const H = Math.max(p.height_mm || 500, 50);
    const padT = Math.max(p.leg_pad_thickness_mm ?? 10, 1);
    const padL = p.leg_pad_length_mm ?? 2.5 * sec.h;
    const padW = p.leg_pad_width_mm ?? 2 * sec.w;
    const tb = Math.max(p.base_plate_thickness_mm ?? 16, 1);
    const area = p.base_plate_area_mm2 ? Math.sqrt(p.base_plate_area_mm2) : 0;
    const bpL = p.base_plate_length_mm ?? (area || 2 * sec.h + 40);
    const bpW = p.base_plate_width_mm ?? (area || 2 * sec.w + 40);
    const boltD = (p.anchor_bolt_diameter_mm ?? 20) + 2;

    // Yerel kolon: üst z=0, taban plakası alt yüzü z=−Lc.
    const column = (Lc: number): Shape3D => {
      let plate = box(-bpL / 2, bpL / 2, -bpW / 2, bpW / 2, -Lc, -Lc + tb);
      if (ctx.level === "exact") {
        const ix = Math.min(30, bpL / 4);
        const iy = Math.min(30, bpW / 4);
        const hp: Pt[] = [[1, 1], [1, -1], [-1, 1], [-1, -1]].map(
          ([a, b]) => [a * (bpL / 2 - ix), b * (bpW / 2 - iy)] as Pt,
        );
        for (const h of zHoles(hp, boltD, -Lc, -Lc + tb)) plate = plate.cut(h);
      }
      return plate.fuse(sec.solid(-Lc + tb, 0));
    };
    // Gövdeye oturan eğri ped: (R+padT)−R kabuğu ∩ bölge kutusu
    const pad = (region: Shape3D, zLo: number, zHi: number): Shape3D =>
      cyl(R + padT, zLo - 1, zHi + 1).cut(cyl(R, zLo - 2, zHi + 2)).intersect(region);

    const parts: Shape3D[] = [];
    if (vertical) {
      const rs = p.support_radius_mm ?? R + sec.h / 2;
      const zBot = vesselBottomZ(ctx.frames) - H;
      const Lc = zA - zBot;
      for (let i = 0; i < n; i++) {
        const th = (360 * i) / n;
        const leg = column(Lc).translate(rs, 0, zA);
        const pd = pad(box(0, R + padT + 1, -padW / 2, padW / 2, zA - padL, zA), zA - padL, zA);
        parts.push(fuseAll([leg, pd]).rotate(th, [0, 0, 0], [0, 0, 1]));
      }
    } else {
      const a = 35 * DEG;
      const stations = Math.ceil(n / 2);
      const pitch = Math.max(3 * sec.w, 2 * R);
      const xBot = -(R + H);
      for (let i = 0; i < n; i++) {
        const k = Math.floor(i / 2);
        const y = (i % 2 === 0 ? 1 : -1) * R * Math.sin(a);
        const zk = zA + (k - (stations - 1) / 2) * pitch;
        const xTop = -Math.sqrt((R + padT) ** 2 - y * y);
        const leg = column(xTop - xBot).rotate(90, [0, 0, 0], [0, 1, 0]).translate(xTop, y, zk);
        const zl = zk - padL / 2;
        const zh = zk + padL / 2;
        const pd = pad(box(-(R + padT) - 1, 0, y - padW / 2, y + padW / 2, zl, zh), zl, zh);
        parts.push(fuseAll([leg, pd]));
      }
    }
    return fuseAll(parts);
  },
};
