// D08/E01 — ayaklar: leg_count adet, profil/boru kesiti + gövdeye sarılı ped + taban sacı.
//
// Kesit yerel çerçevesi (kolon ekseni = yerel Z, üst uç z=0, aşağı −Z):
//   yerel X = radyal (dışa +), derinlik = profil kanat genişliği b (`leg_profile_width_mm`)
//   yerel Y = teğetsel, en = profil yüksekliği h (`leg_profile_height_mm`)
// "web" (varsayılan): U'nun sırtı iç yüzde (−X) → sırt pedin dış yüzüne yaslanır.
// "flanges": kesit X'te aynalanır → kanat uçları pede bakar. Boru/kutu/köşebent de aynı
// "iç yüz (x = −radyal/2) pedin dış yüzüne değer" kuralıyla yerleşir.
//
// Dikey kap: height_mm = ayak boyu (taban sacı ALT yüzü → ayak üst ucu); üst uç = supportZ.
//   Ayak ekseni yarıçapı rs = R + padT + radyal/2 (ya da support_radius_mm).
//   Ped z ∈ [üst + ext − padL, üst + ext]; açılar start + i·360/n.
// Yatay kap: ayaklar −X'e iner; ikişer sıra (y = ±R·sin35°); yerel radyal → ±Y (kap orta
//   düzleminden dışa), teğetsel → kap ekseni. Taban sacı alt yüzü x = −(R + height_mm).
// Sessiz kırpma yok (K4): geçersiz değer olduğu gibi çizilir; kurulamazsa worker BOOLEAN_FAILED verir.
// Ayak (kolon+sac) ile ped yalnız temas eder (kesişim hacmi 0) → ayrı katılar, tek compound.
import { makeCompound } from "replicad";
import type { Shape3D } from "replicad";
import type { ComponentFrame, PartCtx, PartModule } from "../../geometryContract";
import type { Support } from "../../types";
import { supportZ } from "../../vesselModel";
import type { Pt } from "../geom";
import { box, cyl, DEG, outerRadiusAt, prism, zHoles } from "./supportGeom";

interface Section {
  /** Radyal derinlik (yerel X). */
  rad: number;
  /** Teğetsel en (yerel Y). */
  tan: number;
  solid: (z0: number, z1: number) => Shape3D;
}

function section(p: Support): Section {
  const type = p.leg_section_type ?? "pipe";
  const t = p.leg_thickness_mm ?? 6;
  if (type === "pipe") {
    const d = p.leg_diameter_mm ?? 114.3;
    return { rad: d, tan: d, solid: (a, b) => cyl(d / 2, a, b).cut(cyl(d / 2 - t, a - 1, b + 1)) };
  }
  const h = p.leg_profile_height_mm ?? p.leg_diameter_mm ?? 100; // teğetsel
  const b = p.leg_profile_width_mm ?? h; // radyal
  const tw = p.leg_web_thickness_mm ?? t;
  const tf = p.leg_flange_thickness_mm ?? t;
  if (type === "box") {
    return {
      rad: b, tan: h,
      solid: (z0, z1) => box(-b / 2, b / 2, -h / 2, h / 2, z0, z1)
        .cut(box(-b / 2 + tw, b / 2 - tw, -h / 2 + tw, h / 2 - tw, z0 - 1, z1 + 1)),
    };
  }
  // Sırt/kol iç yüzde (x = −b/2); "flanges" → X aynası.
  const base: Pt[] =
    type === "channel"
      ? [[-b / 2, -h / 2], [b / 2, -h / 2], [b / 2, -h / 2 + tf], [-b / 2 + tw, -h / 2 + tf],
         [-b / 2 + tw, h / 2 - tf], [b / 2, h / 2 - tf], [b / 2, h / 2], [-b / 2, h / 2]]
      : [[-b / 2, -h / 2], [b / 2, -h / 2], [b / 2, -h / 2 + tw], [-b / 2 + tw, -h / 2 + tw],
         [-b / 2 + tw, h / 2], [-b / 2, h / 2]];
  const flip = (p.leg_channel_facing ?? "web") === "flanges";
  const pts = flip ? base.map(([x, y]) => [-x, y] as Pt) : base;
  return { rad: b, tan: h, solid: (z0, z1) => prism(pts, z0, z1) };
}

/** Taban sacı ankraj deliği konumları (yerel XY): 1 → merkez, 2 → teğetsel eksende, 4 → köşeler. */
function boltPoints(n: number, W: number, L: number): Pt[] {
  const ix = Math.min(30, W / 4);
  const iy = Math.min(30, L / 4);
  const ax = W / 2 - ix;
  const ay = L / 2 - iy;
  if (n === 1) return [[0, 0]];
  if (n === 2) return [[0, ay], [0, -ay]];
  if (n === 4) return [[ax, ay], [ax, -ay], [-ax, ay], [-ax, -ay]];
  // Diğer adetler (UI issue'su): elips üzerinde eşit aralıklı, olduğu gibi çizilir.
  return Array.from({ length: n }, (_, k) => {
    const a = (2 * Math.PI * k) / n;
    return [ax * Math.cos(a), ay * Math.sin(a)] as Pt;
  });
}

export interface LegAssembly {
  /** Ayak başına kolon + taban sacı (birleşik). */
  columns: Shape3D[];
  /** Ayak başına gövde pedi. */
  pads: Shape3D[];
}

/** Ayak takımını (kolonlar + pedler) ayrı ayrı kurar — test/doğrulama için de kullanılır. */
export function legAssembly(p: Support, frame: ComponentFrame | null, ctx: PartCtx): LegAssembly {
  const n = p.leg_count ?? 4;
  if (!(n >= 1)) throw new Error(`${p.support_id}: leg_count ≥ 1 olmalı (${n})`);
  const sec = section(p);
  const zA = supportZ(p, ctx.frames);
  const R = outerRadiusAt(ctx.frames, zA, frame);
  const H = p.height_mm;
  const padT = p.leg_pad_thickness_mm ?? 10;
  const padL = p.leg_pad_length_mm ?? 2.5 * sec.tan;
  const padW = p.leg_pad_width_mm ?? 2 * sec.tan;
  const ext = p.leg_pad_top_extension_mm ?? 50;
  const tb = p.base_plate_thickness_mm ?? 16;
  const area = p.base_plate_area_mm2 ? Math.sqrt(p.base_plate_area_mm2) : 0;
  const bpL = p.base_plate_length_mm ?? (area || 2 * sec.tan + 40); // teğetsel (profil yüksekliği yönü)
  const bpW = p.base_plate_width_mm ?? (area || 2 * sec.rad + 40); // radyal
  const boltN = p.anchor_bolt_count ?? 4;
  const boltD = (p.anchor_bolt_diameter_mm ?? 20) + 2;

  // Yerel kolon: üst z=0, taban sacı alt yüzü z=−Lc (sac üst yüzü = kolon alt ucu).
  const column = (Lc: number): Shape3D => {
    let plate = box(-bpW / 2, bpW / 2, -bpL / 2, bpL / 2, -Lc, -Lc + tb);
    if (ctx.level === "exact") {
      for (const h of zHoles(boltPoints(boltN, bpW, bpL), boltD, -Lc, -Lc + tb)) plate = plate.cut(h);
    }
    return plate.fuse(sec.solid(-Lc + tb, 0));
  };
  // Gövdeye sarılı ped: (R+padT)−R kabuğu ∩ bölge kutusu
  const pad = (region: Shape3D, zLo: number, zHi: number): Shape3D =>
    cyl(R + padT, zLo - 1, zHi + 1).cut(cyl(R, zLo - 2, zHi + 2)).intersect(region);

  const columns: Shape3D[] = [];
  const pads: Shape3D[] = [];
  if (ctx.orientation === "vertical") {
    const rs = p.support_radius_mm ?? R + padT + sec.rad / 2;
    const start = p.leg_start_angle_deg ?? (n === 4 ? 45 : 0);
    const zHi = zA + ext;
    const zLo = zHi - padL;
    for (let i = 0; i < n; i++) {
      const th = start + (360 * i) / n;
      columns.push(column(H).translate(rs, 0, zA).rotate(th, [0, 0, 0], [0, 0, 1]));
      pads.push(pad(box(0, R + padT + 1, -padW / 2, padW / 2, zLo, zHi), zLo, zHi).rotate(th, [0, 0, 0], [0, 0, 1]));
    }
  } else {
    const a = 35 * DEG;
    const stations = Math.ceil(n / 2);
    const pitch = Math.max(3 * sec.tan, 2 * R);
    const xBot = -(R + H);
    for (let i = 0; i < n; i++) {
      const k = Math.floor(i / 2);
      const s = i % 2 === 0 ? 1 : -1;
      const y = s * R * Math.sin(a);
      const zk = zA + (k - (stations - 1) / 2) * pitch;
      const xTop = -Math.sqrt((R + padT) ** 2 - y * y);
      // yerel X→+Y, Y→+Z, Z→+X (120° / (1,1,1)); y<0 sırası için X ekseni etrafında 180°.
      let leg = column(xTop - xBot).rotate(120, [0, 0, 0], [1, 1, 1]);
      if (s < 0) leg = leg.rotate(180, [0, 0, 0], [1, 0, 0]);
      columns.push(leg.translate(xTop, y, zk));
      const zl = zk - padL / 2;
      const zh = zk + padL / 2;
      pads.push(pad(box(-(R + padT) - 1, 0, y - padW / 2, y + padW / 2, zl, zh), zl, zh));
    }
  }
  return { columns, pads };
}

export const legs: PartModule<Support> = {
  build(p, frame, ctx) {
    const { columns, pads } = legAssembly(p, frame, ctx);
    return makeCompound([...columns, ...pads]) as Shape3D;
  },
};
