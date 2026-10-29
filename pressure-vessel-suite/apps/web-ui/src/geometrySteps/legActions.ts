// Ayak editörünün saf eylemleri (React'siz → vitest ile test edilir).

import { getUpn } from "../data/catalogs";
import { useStore } from "../store";
import type { Support, VesselProject } from "../types";

/** "Hazır UPN seç": h, b, tw, tf alanlarını katalogdan doldurur (sonra elle değiştirilebilir). */
export function upnPatch(name: string): Partial<Support> | null {
  const u = getUpn(name);
  if (!u) return null;
  return {
    leg_section_type: "channel",
    leg_profile_height_mm: u.h,
    leg_profile_width_mm: u.b,
    leg_web_thickness_mm: u.tw,
    leg_flange_thickness_mm: u.tf,
  };
}

/** Yeni ayak başlangıcı: channel + UPN 120 + profil boyu 1500 (öneri; elle değiştirilebilir). */
export function newLegPatch(count?: number): Partial<Support> {
  return {
    ...upnPatch("UPN 120"),
    height_mm: 1500,
    leg_channel_facing: "web",
    ...(count != null ? { leg_count: count } : {}),
  };
}

/** Katalogdaki satırlardan biri mevcut 4 alanla birebir eşleşiyorsa adı (seçici göstergesi için). */
export function matchingUpn(s: Support, rows: { name: string; h: number; b: number; tw: number; tf: number }[]): string {
  return rows.find((r) =>
    s.leg_profile_height_mm === r.h && s.leg_profile_width_mm === r.b &&
    s.leg_web_thickness_mm === r.tw && s.leg_flange_thickness_mm === r.tf)?.name ?? "";
}

/** Yeni ayak ekler (channel + UPN 120 + 1500 mm), seçer, id döner. */
export function addLegSupport(count?: number): string {
  const st = useStore.getState();
  const id = st.addSupport("leg");
  const idx = useStore.getState().project.supports.findIndex((s) => s.support_id === id);
  if (idx >= 0) useStore.getState().updateSupport(idx, newLegPatch(count));
  useStore.getState().setSelection({ kind: "support", id });
  return id;
}

/** "Kabı dikey yap". */
export function makeVertical(): void {
  useStore.getState().setProject((p: VesselProject) => ({ ...p, orientation: "vertical" }));
}
