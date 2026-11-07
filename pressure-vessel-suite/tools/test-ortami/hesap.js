// Bağımsız ASME VIII-1 hesap motoru (test ortamı).
//
// Bu dosya sitenin hesap paketlerinden (code-asme-viii-1, calc-core, ...) BAĞIMSIZDIR:
// formüller ASME VIII-1 metninden kuruldu, hiçbir site kaynağı okunmadı/kopyalanmadı.
// Amaç: sitenin sonuçlarını dışarıdan doğrulamak. ES module, DOM yok, bağımlılık yok.
// Birimler: uzunluk mm, basınç/gerilme MPa. (Formüller birim-homojen olduğundan
// psi/in girdisiyle de doğrudan çalışır; testler bunu kullanır.)
//
// "Çevre" kuralları (geçmiş hataların yaşandığı yer):
//   * Korozyonlu iç yarıçap/çap BÜYÜR: R = Ri + CA_iç, D = Di + 2·CA_iç.
//   * Dış korozyon iç ölçüyü değiştirmez, yalnız etkin kalınlıktan düşülür.
//   * Etkin kalınlık t_e = t_nom·(1 − mill%/100) − şekillendirme incelmesi − CA_iç − CA_dış.
//   * Test basınçlarının tabanı hesaplanan global MAWP'dir (tasarım basıncı değil).

const G = 9.80665; // m/s²

// ── yardımcılar ─────────────────────────────────────────────────────────────

function f(x) {
  if (x === null || x === undefined || !Number.isFinite(x)) return String(x);
  const a = Math.abs(x);
  const d = a >= 1000 ? 2 : a >= 10 ? 4 : 5;
  return String(Number(x.toFixed(d)));
}

function adim(ad, madde, formul, yerine, deger, birim) {
  return { ad, madde, formul, yerine, deger, birim };
}

function tanimli(v) {
  return v !== undefined && v !== null;
}

// ── UG-27 silindirik gövde ──────────────────────────────────────────────────

/** UG-27(c)(1) çevresel gerilme — gerekli kalınlık. */
export function ug27Cevresel(P, R, S, E) {
  const t = (P * R) / (S * E - 0.6 * P);
  return adim('Gerekli kalınlık (çevresel gerilme)', 'UG-27(c)(1)', 't = P·R/(S·E − 0.6·P)',
    `${f(P)}·${f(R)}/(${f(S)}·${f(E)} − 0.6·${f(P)})`, t, 'mm');
}

/** UG-27(c)(2) boyuna gerilme — gerekli kalınlık. */
export function ug27Boyuna(P, R, S, E) {
  const t = (P * R) / (2 * S * E + 0.4 * P);
  return adim('Gerekli kalınlık (boyuna gerilme)', 'UG-27(c)(2)', 't = P·R/(2·S·E + 0.4·P)',
    `${f(P)}·${f(R)}/(2·${f(S)}·${f(E)} + 0.4·${f(P)})`, t, 'mm');
}

/** UG-27(c)(1) ters çözüm — çevresel gerilmeye göre izin verilen basınç. */
export function ug27CevreselMawp(t, R, S, E) {
  const P = (S * E * t) / (R + 0.6 * t);
  return adim('MAWP (çevresel gerilme)', 'UG-27(c)(1)', 'P = S·E·t/(R + 0.6·t)',
    `${f(S)}·${f(E)}·${f(t)}/(${f(R)} + 0.6·${f(t)})`, P, 'MPa');
}

/** UG-27(c)(2) ters çözüm — boyuna gerilmeye göre izin verilen basınç. */
export function ug27BoyunaMawp(t, R, S, E) {
  const P = (2 * S * E * t) / (R - 0.4 * t);
  return adim('MAWP (boyuna gerilme)', 'UG-27(c)(2)', 'P = 2·S·E·t/(R − 0.4·t)',
    `2·${f(S)}·${f(E)}·${f(t)}/(${f(R)} − 0.4·${f(t)})`, P, 'MPa');
}

// ── UG-32 şekillendirilmiş bombeler ────────────────────────────────────────

/** Appendix 1-4(c) K faktörü; D/2h = 2 için K = 1 (UG-32(d)). */
export function elipsoidalK(D, h) {
  const oran = D / (2 * h);
  const K = (2 + oran * oran) / 6;
  return adim('Eliptik şekil faktörü K', 'App. 1-4(c)', 'K = (2 + (D/2h)²)/6',
    `(2 + (${f(D)}/(2·${f(h)}))²)/6`, K, '-');
}

/** UG-32(d) (K=1) / App. 1-4(c) eliptik bombe — gerekli kalınlık. */
export function elipsoidalKalinlik(P, D, S, E, K = 1) {
  const t = (P * D * K) / (2 * S * E - 0.2 * P);
  if (K === 1) {
    return adim('Gerekli kalınlık (2:1 eliptik)', 'UG-32(d)', 't = P·D/(2·S·E − 0.2·P)',
      `${f(P)}·${f(D)}/(2·${f(S)}·${f(E)} − 0.2·${f(P)})`, t, 'mm');
  }
  return adim('Gerekli kalınlık (eliptik, K ile)', 'App. 1-4(c)', 't = P·D·K/(2·S·E − 0.2·P)',
    `${f(P)}·${f(D)}·${f(K)}/(2·${f(S)}·${f(E)} − 0.2·${f(P)})`, t, 'mm');
}

export function elipsoidalMawp(t, D, S, E, K = 1) {
  const P = (2 * S * E * t) / (K * D + 0.2 * t);
  if (K === 1) {
    return adim('MAWP (2:1 eliptik)', 'UG-32(d)', 'P = 2·S·E·t/(D + 0.2·t)',
      `2·${f(S)}·${f(E)}·${f(t)}/(${f(D)} + 0.2·${f(t)})`, P, 'MPa');
  }
  return adim('MAWP (eliptik, K ile)', 'App. 1-4(c)', 'P = 2·S·E·t/(K·D + 0.2·t)',
    `2·${f(S)}·${f(E)}·${f(t)}/(${f(K)}·${f(D)} + 0.2·${f(t)})`, P, 'MPa');
}

/** App. 1-4(d) torisferik M faktörü. L = taç iç yarıçapı, r = büküm iç yarıçapı. */
export function torisferikM(L, r) {
  const M = (3 + Math.sqrt(L / r)) / 4;
  return adim('Torisferik faktör M', 'App. 1-4(d)', 'M = (3 + √(L/r))/4',
    `(3 + √(${f(L)}/${f(r)}))/4`, M, '-');
}

/** UG-32(e) / App. 1-4(d) torisferik — t = P·L·M/(2·S·E − 0.2·P). r = 0.06L için 0.885·P·L/(S·E − 0.1·P) ile aynıdır. */
export function torisferikKalinlik(P, L, M, S, E) {
  const t = (P * L * M) / (2 * S * E - 0.2 * P);
  return adim('Gerekli kalınlık (torisferik)', 'UG-32(e) / App. 1-4(d)', 't = P·L·M/(2·S·E − 0.2·P)',
    `${f(P)}·${f(L)}·${f(M)}/(2·${f(S)}·${f(E)} − 0.2·${f(P)})`, t, 'mm');
}

export function torisferikMawp(t, L, M, S, E) {
  const P = (2 * S * E * t) / (L * M + 0.2 * t);
  return adim('MAWP (torisferik)', 'UG-32(e) / App. 1-4(d)', 'P = 2·S·E·t/(L·M + 0.2·t)',
    `2·${f(S)}·${f(E)}·${f(t)}/(${f(L)}·${f(M)} + 0.2·${f(t)})`, P, 'MPa');
}

/** UG-32(f) yarım küre. L = korozyonlu iç yarıçap. */
export function yarimKureKalinlik(P, L, S, E) {
  const t = (P * L) / (2 * S * E - 0.2 * P);
  return adim('Gerekli kalınlık (yarım küre)', 'UG-32(f)', 't = P·L/(2·S·E − 0.2·P)',
    `${f(P)}·${f(L)}/(2·${f(S)}·${f(E)} − 0.2·${f(P)})`, t, 'mm');
}

export function yarimKureMawp(t, L, S, E) {
  const P = (2 * S * E * t) / (L + 0.2 * t);
  return adim('MAWP (yarım küre)', 'UG-32(f)', 'P = 2·S·E·t/(L + 0.2·t)',
    `2·${f(S)}·${f(E)}·${f(t)}/(${f(L)} + 0.2·${f(t)})`, P, 'MPa');
}

// ── UG-34 düz kapak (dairesel, Z'siz) ──────────────────────────────────────

export function duzKapakKalinlik(P, d, C, S, E) {
  const t = d * Math.sqrt((C * P) / (S * E));
  return adim('Gerekli kalınlık (düz kapak)', 'UG-34(c)(2)', 't = d·√(C·P/(S·E))',
    `${f(d)}·√(${f(C)}·${f(P)}/(${f(S)}·${f(E)}))`, t, 'mm');
}

export function duzKapakMawp(t, d, C, S, E) {
  const P = (S * E * t * t) / (C * d * d);
  return adim('MAWP (düz kapak)', 'UG-34(c)(2)', 'P = S·E·t²/(C·d²)',
    `${f(S)}·${f(E)}·${f(t)}²/(${f(C)}·${f(d)}²)`, P, 'MPa');
}

// ── kalınlık zinciri ────────────────────────────────────────────────────────

/** Gerekli nominal: t_nom = (t_gerekli + CA_iç + CA_dış + incelme)/(1 − mill%/100). */
export function nominalGerekli(tReq, caIc, caDis, incelme, millYuzde) {
  const k = 1 - millYuzde / 100;
  const t = (tReq + caIc + caDis + incelme) / k;
  return adim('Gerekli nominal kalınlık', 'UG-16 / UG-25', 't_nom = (t + CA_iç + CA_dış + incelme)/(1 − mill/100)',
    `(${f(tReq)} + ${f(caIc)} + ${f(caDis)} + ${f(incelme)})/(1 − ${f(millYuzde)}/100)`, t, 'mm');
}

/** Etkin (korozyonlu, toleranslı) kalınlık: t_e = t_nom·(1 − mill%/100) − incelme − CA_iç − CA_dış. */
export function etkinKalinlik(tNom, caIc, caDis, incelme, millYuzde) {
  const t = tNom * (1 - millYuzde / 100) - incelme - caIc - caDis;
  return adim('Etkin kalınlık (korozyonlu)', 'UG-16 / UG-25', 't_e = t_nom·(1 − mill/100) − incelme − CA_iç − CA_dış',
    `${f(tNom)}·(1 − ${f(millYuzde)}/100) − ${f(incelme)} − ${f(caIc)} − ${f(caDis)}`, t, 'mm');
}

// ── statik kafa ve testler ──────────────────────────────────────────────────

/** Statik sıvı kafası: p = ρ·g·h (ρ kg/m³, h mm → MPa). */
export function statikKafa(rho, hMm) {
  const p = (rho * G * Math.max(0, hMm) / 1000) / 1e6;
  return adim('Statik sıvı kafası', 'UG-22(b)', 'p = ρ·g·h',
    `${f(rho)}·${G}·${f(Math.max(0, hMm) / 1000)} / 1e6`, p, 'MPa');
}

/** UG-99(b): P_T = 1.3·MAWP·LSR. */
export function hidrotest(mawp, lsr) {
  const p = 1.3 * mawp * lsr;
  return adim('Hidrostatik test basıncı (kap üstü)', 'UG-99(b)', 'P_T = 1.3·MAWP·(S_test/S)',
    `1.3·${f(mawp)}·${f(lsr)}`, p, 'MPa');
}

/** UG-100(b): P_T = 1.1·MAWP·LSR. */
export function pnomatik(mawp, lsr) {
  const p = 1.1 * mawp * lsr;
  return adim('Pnömatik test basıncı (kap üstü)', 'UG-100(b)', 'P_T = 1.1·MAWP·(S_test/S)',
    `1.1·${f(mawp)}·${f(lsr)}`, p, 'MPa');
}

// ── proje bağlamı ───────────────────────────────────────────────────────────

function malzemeBul(project, id) {
  return (project.materials || []).find((m) => m.material_id === id) || null;
}

function kaynakBul(project, id) {
  return (project.welds || []).find((w) => w.joint_id === id) || null;
}

function boyunaMi(w) {
  return w.joint_type === 'longitudinal' || w.weld_category === 'A';
}
function cevreselMi(w) {
  return w.joint_type === 'circumferential' || w.weld_category === 'B';
}

/** Bileşenin ilgili kaynak dikişleri: weld_joint_id + connected_components ile bağlananlar. */
function bilesenKaynaklari(project, compId, weldId) {
  const out = [];
  const ref = weldId ? kaynakBul(project, weldId) : null;
  if (ref) out.push(ref);
  for (const w of project.welds || []) {
    if (w !== ref && Array.isArray(w.connected_components) && w.connected_components.includes(compId)) out.push(w);
  }
  return { ref, hepsi: out };
}

function korozyon(comp, dc, notlar, compId, varsayimlar) {
  let caIc;
  if (tanimli(comp.internal_corrosion_allowance)) caIc = comp.internal_corrosion_allowance;
  else {
    caIc = dc.corrosion_allowance_internal ?? 0;
    varsayimlar.push(`${compId}: bileşen iç korozyon payı yok → genel tasarım değeri CA_iç = ${f(caIc)} mm kullanıldı.`);
  }
  let caDis;
  if (tanimli(comp.external_corrosion_allowance)) caDis = comp.external_corrosion_allowance;
  else {
    caDis = dc.corrosion_allowance_external ?? 0;
    varsayimlar.push(`${compId}: bileşen dış korozyon payı yok → genel tasarım değeri CA_dış = ${f(caDis)} mm kullanıldı.`);
  }
  const mill = tanimli(comp.mill_tolerance) ? comp.mill_tolerance : 0;
  if (!tanimli(comp.mill_tolerance)) varsayimlar.push(`${compId}: mill toleransı girilmemiş → %0 alındı.`);
  if (mill > 0) notlar.push(`Mill toleransı %${f(mill)} tam uygulandı (UG-16(c) levha muafiyeti — min(0.3 mm, %6) — kullanılmadı, muhafazakâr).`);
  const incelme = tanimli(comp.forming_thinning) ? comp.forming_thinning : 0;
  return { caIc, caDis, mill, incelme };
}

/** Statik kafa yükseklikleri: her bileşenin en alt iç noktasının kabın en alt noktasına göre kotu (mm). */
function kotlar(project, varsayimlar) {
  const heads = project.heads || [];
  const shells = project.shell_sections || [];
  const cones = project.cones || [];
  const ic = (c) => c.inside_diameter ?? (c.outside_diameter - 2 * c.nominal_thickness);
  let seq = project.component_sequence;
  if (!Array.isArray(seq) || seq.length === 0) {
    seq = [];
    if (heads[0]) seq.push({ component_type: 'head', component_id: heads[0].head_id });
    for (const s of shells) seq.push({ component_type: 'shell', component_id: s.section_id });
    for (const h of heads.slice(1)) seq.push({ component_type: 'head', component_id: h.head_id });
    varsayimlar.push('component_sequence yok → sıra: ilk bombe, gövdeler (liste sırası), kalan bombeler.');
  }
  const bul = (r) => r.component_type === 'head' ? heads.find((h) => h.head_id === r.component_id)
    : r.component_type === 'shell' ? shells.find((s) => s.section_id === r.component_id)
      : cones.find((c) => c.cone_id === r.component_id);
  const kot = {};
  const yatay = project.orientation === 'horizontal';
  if (yatay) {
    let Dmax = 0;
    for (const r of seq) {
      const c = bul(r); if (!c) continue;
      Dmax = Math.max(Dmax, r.component_type === 'cone' ? c.large_diameter : ic(c));
    }
    for (const r of seq) {
      const c = bul(r); if (!c) continue;
      const D = r.component_type === 'cone' ? c.large_diameter : ic(c);
      kot[r.component_id] = (Dmax - D) / 2;
    }
    varsayimlar.push('Yatay kap: bileşenler eş eksenli kabul edildi; her bileşenin alt kotu = (D_maks − D)/2.');
    return kot;
  }
  varsayimlar.push(`Dikey kap: component_sequence[0] (${seq[0]?.component_id}) EN ALTTA kabul edildi; kotlar iç ölçü ve korozyonsuz geometriyle yığıldı.`);
  let z = 0;
  seq.forEach((r, i) => {
    const c = bul(r); if (!c) return;
    let boy;
    if (r.component_type === 'head') {
      const D = ic(c);
      let derinlik;
      if (c.type === 'elliptical') derinlik = c.crown_depth ?? D / 4;
      else if (c.type === 'hemispherical') derinlik = D / 2;
      else if (c.type === 'torispherical') {
        const L = c.crown_radius ?? (c.outside_diameter ?? D + 2 * c.nominal_thickness);
        const rk = c.knuckle_radius ?? 0.06 * L;
        derinlik = L - Math.sqrt((L - rk) ** 2 - (D / 2 - rk) ** 2);
      } else derinlik = 0;
      boy = derinlik + (c.straight_flange_length ?? 0);
      kot[r.component_id] = i === 0 ? 0 : z; // alt bombenin en alt noktası 0; üst bombenin en alt noktası başlangıcı
    } else {
      boy = r.component_type === 'cone' ? c.length : c.tangent_length;
      kot[r.component_id] = z;
    }
    z += boy;
  });
  return kot;
}

function baglam(project) {
  const varsayimlar = [];
  const dc = project.design_conditions || {};
  const P = dc.design_pressure;
  let rho = dc.fluid_density_kg_m3 ?? 0;
  const seviye = dc.liquid_level_mm;
  let kot = null;
  if (rho > 0 && tanimli(seviye)) {
    kot = kotlar(project, varsayimlar);
    varsayimlar.push(`Statik kafa: ρ = ${f(rho)} kg/m³, sıvı seviyesi kabın en alt noktasından ${f(seviye)} mm; her bileşen kendi en alt noktasındaki basınçla hesaplandı.`);
  } else {
    rho = 0;
    varsayimlar.push('Statik kafa yok: fluid_density_kg_m3 ve/veya liquid_level_mm girilmemiş (ya da 0) → p_statik = 0.');
  }
  varsayimlar.push(`Tasarım basıncı P = ${f(P)} MPa kap üstünde (iç basınç) kabul edildi; dış basınç bu motorun kapsamında değil.`);
  return { project, dc, P, rho, seviye, kot, varsayimlar };
}

function yerelBasinc(ctx, id, adimlar) {
  if (!ctx.rho || !ctx.kot || !tanimli(ctx.kot[id])) return { Pl: ctx.P, ps: 0 };
  const h = ctx.seviye - ctx.kot[id];
  const a = statikKafa(ctx.rho, h);
  adimlar.push(a);
  const Pl = ctx.P + a.deger;
  adimlar.push(adim('Yerel tasarım basıncı', 'UG-22(b)', 'P_yerel = P + p_statik', `${f(ctx.P)} + ${f(a.deger)}`, Pl, 'MPa'));
  return { Pl, ps: a.deger };
}

function malzemeGerilme(ctx, mat, compId, notlar) {
  if (tanimli(mat.temperature) && tanimli(ctx.dc.design_temperature) && mat.temperature !== ctx.dc.design_temperature) {
    notlar.push(`Malzeme S değeri ${f(mat.temperature)} °C için; tasarım sıcaklığı ${f(ctx.dc.design_temperature)} °C — S olduğu gibi kullanıldı.`);
    ctx.varsayimlar.push(`${compId}: S = ${f(mat.allowable_stress)} MPa (${mat.material_id}, ${f(mat.temperature)} °C) tasarım sıcaklığından farklı sıcaklıkta tanımlı, interpolasyon yapılmadı.`);
  }
  return mat.allowable_stress;
}

function bosSonuc(id, tip, alt_tip, adimlar, notlar) {
  return { id, tip, alt_tip, adimlar, t_gerekli_mm: null, t_nominal_gerekli_mm: null, mawp_mpa: null, durum: 'HESAPLANMADI', notlar };
}

function sonuclandir(r, ctx, tReq, ch, tNom, mawpYerel, ps, Pl) {
  const { adimlar } = r;
  const nom = nominalGerekli(tReq, ch.caIc, ch.caDis, ch.incelme, ch.mill);
  adimlar.push(nom);
  let mawp = mawpYerel;
  if (ps > 0) {
    mawp = mawpYerel - ps;
    adimlar.push(adim('MAWP (kap üstüne indirgenmiş)', 'UG-98', 'MAWP = P_izin,yerel − p_statik',
      `${f(mawpYerel)} − ${f(ps)}`, mawp, 'MPa'));
  }
  r.t_gerekli_mm = tReq;
  r.t_nominal_gerekli_mm = nom.deger;
  r.mawp_mpa = mawp;
  if (r.durum !== 'HESAPLANMADI') {
    r.durum = tNom + 1e-9 >= nom.deger && mawpYerel + 1e-12 >= Pl ? 'PASS' : 'FAIL';
    if (r.durum === 'FAIL') r.notlar.push(`Nominal ${f(tNom)} mm < gerekli ${f(nom.deger)} mm (veya MAWP < yerel tasarım basıncı).`);
  }
  return r;
}

// ── bileşen hesapları ───────────────────────────────────────────────────────

/** Silindirik gövde (UG-27): çevresel + boyuna, yöneten büyük kalınlık / küçük MAWP. */
export function hesaplaGovde(shell, ctx) {
  const id = shell.section_id;
  const adimlar = [];
  const notlar = [];
  const r = { id, tip: 'shell', alt_tip: 'cylinder', adimlar, notlar, durum: 'PASS' };
  const mat = malzemeBul(ctx.project, shell.material_id);
  if (!mat) { notlar.push(`Malzeme bulunamadı: ${shell.material_id}`); return bosSonuc(id, 'shell', 'cylinder', adimlar, notlar); }
  const S = malzemeGerilme(ctx, mat, id, notlar);
  const ch = korozyon(shell, ctx.dc, notlar, id, ctx.varsayimlar);
  const tNom = shell.nominal_thickness;

  // E: çevresel gerilme → boyuna dikiş (Kat. A); boyuna gerilme → çevresel dikiş (Kat. B).
  const { ref, hepsi } = bilesenKaynaklari(ctx.project, id, shell.weld_joint_id);
  let E1, E2;
  if (hepsi.length === 0) {
    E1 = E2 = 1.0;
    ctx.varsayimlar.push(`${id}: kaynak dikişi tanımlı değil → dikişsiz kabul, E = 1.0 (her iki gerilme). Kaynaklıysa EMNİYETSİZ olabilir.`);
  } else {
    const wL = hepsi.find(boyunaMi);
    const wC = hepsi.find(cevreselMi);
    E1 = (wL || ref || hepsi[0]).joint_efficiency;
    E2 = (wC || ref || hepsi[0]).joint_efficiency;
    if (!wL) ctx.varsayimlar.push(`${id}: boyuna (Kat. A) dikiş ayrı tanımlı değil → çevresel gerilme için ${(ref || hepsi[0]).joint_id} E = ${f(E1)} kullanıldı.`);
    if (!wC) ctx.varsayimlar.push(`${id}: çevresel (Kat. B) dikiş ayrı tanımlı değil → boyuna gerilme için ${(ref || hepsi[0]).joint_id} E = ${f(E2)} kullanıldı.`);
  }

  let Ri;
  if (tanimli(shell.inside_diameter)) {
    Ri = shell.inside_diameter / 2;
    adimlar.push(adim('İç yarıçap (yeni)', 'geometri', 'Ri = Di/2', `${f(shell.inside_diameter)}/2`, Ri, 'mm'));
  } else {
    Ri = shell.outside_diameter / 2 - tNom;
    adimlar.push(adim('İç yarıçap (yeni)', 'geometri', 'Ri = Do/2 − t_nom', `${f(shell.outside_diameter)}/2 − ${f(tNom)}`, Ri, 'mm'));
    ctx.varsayimlar.push(`${id}: iç çap verilmemiş → Ri = Do/2 − t_nom (nominal kalınlıkla).`);
  }
  const R = Ri + ch.caIc;
  adimlar.push(adim('Korozyonlu iç yarıçap', 'UG-27 (korozyonlu R)', 'R = Ri + CA_iç', `${f(Ri)} + ${f(ch.caIc)}`, R, 'mm'));
  const { Pl, ps } = yerelBasinc(ctx, id, adimlar);

  const a1 = ug27Cevresel(Pl, R, S, E1);
  const a2 = ug27Boyuna(Pl, R, S, E2);
  adimlar.push(a1, a2);
  const tReq = Math.max(a1.deger, a2.deger);
  adimlar.push(adim('Yöneten gerekli kalınlık', 'UG-27(c)', 't = max(t_çevresel, t_boyuna)',
    `max(${f(a1.deger)}, ${f(a2.deger)})`, tReq, 'mm'));
  if (Pl > 0.385 * S * E1 || a1.deger > R / 2) {
    notlar.push('UG-27(c)(1) sınırı aşıldı (t > R/2 veya P > 0.385·S·E) → Appendix 1-2 kalın cidar gerekli; sonuç geçersiz.');
    r.durum = 'HESAPLANMADI';
  }
  if (Pl > 1.25 * S * E2 || a2.deger > R / 2) {
    notlar.push('UG-27(c)(2) sınırı aşıldı (t > R/2 veya P > 1.25·S·E) → Appendix 1-2 gerekli; sonuç geçersiz.');
    r.durum = 'HESAPLANMADI';
  }

  const te = etkinKalinlik(tNom, ch.caIc, ch.caDis, ch.incelme, ch.mill);
  adimlar.push(te);
  const m1 = ug27CevreselMawp(te.deger, R, S, E1);
  const m2 = ug27BoyunaMawp(te.deger, R, S, E2);
  adimlar.push(m1, m2);
  let mY = Math.min(m1.deger, m2.deger);
  adimlar.push(adim('Yöneten izin verilen basınç (yerel)', 'UG-27(c)', 'P = min(P_çevresel, P_boyuna)',
    `min(${f(m1.deger)}, ${f(m2.deger)})`, mY, 'MPa'));
  if (te.deger <= 0) { notlar.push('Etkin kalınlık ≤ 0 → MAWP = 0.'); mY = 0; }
  return sonuclandir(r, ctx, tReq, ch, tNom, mY, ps, Pl);
}

/** Bombe (UG-32 eliptik/torisferik/yarım küre, UG-34 düz). */
export function hesaplaBombe(head, ctx) {
  const id = head.head_id;
  const tip = head.type;
  const adimlar = [];
  const notlar = [];
  const r = { id, tip: 'head', alt_tip: tip, adimlar, notlar, durum: 'PASS' };
  const mat = malzemeBul(ctx.project, head.material_id);
  if (!mat) { notlar.push(`Malzeme bulunamadı: ${head.material_id}`); return bosSonuc(id, 'head', tip, adimlar, notlar); }
  const S = malzemeGerilme(ctx, mat, id, notlar);
  const ch = korozyon(head, ctx.dc, notlar, id, ctx.varsayimlar);
  const tNom = head.nominal_thickness;
  const w = head.weld_joint_id ? kaynakBul(ctx.project, head.weld_joint_id) : null;
  let E;
  if (w) E = w.joint_efficiency;
  else {
    E = 1.0;
    ctx.varsayimlar.push(`${id}: bombe kaynak dikişi tanımlı değil → dikişsiz bombe kabul, E = 1.0.`);
  }
  if (tanimli(head.flat_z_factor) && tip === 'flat') notlar.push('Z faktörü girilmiş: dairesel olmayan düz kapak (UG-34(c)(3)) bu motorun kapsamında değil; dairesel kabul edildi.');

  const Di = head.inside_diameter;
  const D = Di + 2 * ch.caIc;
  adimlar.push(adim('Korozyonlu iç çap', 'UG-32 (korozyonlu D)', 'D = Di + 2·CA_iç', `${f(Di)} + 2·${f(ch.caIc)}`, D, 'mm'));
  const { Pl, ps } = yerelBasinc(ctx, id, adimlar);
  const te = etkinKalinlik(tNom, ch.caIc, ch.caDis, ch.incelme, ch.mill);

  let tReq, mY;
  if (tip === 'elliptical') {
    let K = 1;
    if (tanimli(head.crown_depth)) {
      const hc = head.crown_depth + ch.caIc;
      adimlar.push(adim('Korozyonlu iç derinlik', 'App. 1-4(c)', 'h = h0 + CA_iç', `${f(head.crown_depth)} + ${f(ch.caIc)}`, hc, 'mm'));
      const ka = elipsoidalK(D, hc);
      adimlar.push(ka);
      K = Math.abs(ka.deger - 1) < 1e-9 ? 1 : ka.deger;
    } else {
      ctx.varsayimlar.push(`${id}: crown_depth yok → 2:1 eliptik (h = D/4, K = 1) kabul edildi.`);
    }
    const a = elipsoidalKalinlik(Pl, D, S, E, K); adimlar.push(a); tReq = a.deger;
    adimlar.push(te);
    const m = elipsoidalMawp(te.deger, D, S, E, K); adimlar.push(m); mY = m.deger;
    if (te.deger / (K * 0.9 * D) < 0.002) notlar.push('t_s/L < 0.002 → Appendix 1-4(f) kontrolü gerekli (bu motorda yok).');
  } else if (tip === 'torispherical') {
    const Do = head.outside_diameter ?? Di + 2 * tNom;
    let L0 = head.crown_radius;
    if (!tanimli(L0)) {
      L0 = Do;
      ctx.varsayimlar.push(`${id}: taç yarıçapı yok → standart ASME F&D, L = Do = ${f(Do)} mm${tanimli(head.outside_diameter) ? '' : ' (Do = Di + 2·t_nom)'}.`);
    }
    let r0 = head.knuckle_radius;
    if (!tanimli(r0)) {
      r0 = 0.06 * L0;
      ctx.varsayimlar.push(`${id}: büküm yarıçapı yok → standart ASME F&D, r = 0.06·L = ${f(r0)} mm.`);
    }
    if (r0 < 0.06 * L0 - 1e-9) notlar.push('UG-32(e) ihlali: r < 0.06·L.');
    if (L0 > Do + 1e-9) notlar.push('UG-32(e) ihlali: L > Do (taç yarıçapı dış çapı aşamaz).');
    const L = L0 + ch.caIc, rk = r0 + ch.caIc;
    adimlar.push(adim('Korozyonlu taç yarıçapı', 'UG-32(e)', 'L = L0 + CA_iç', `${f(L0)} + ${f(ch.caIc)}`, L, 'mm'));
    adimlar.push(adim('Korozyonlu büküm yarıçapı', 'UG-32(e)', 'r = r0 + CA_iç', `${f(r0)} + ${f(ch.caIc)}`, rk, 'mm'));
    const Ma = torisferikM(L, rk); adimlar.push(Ma);
    const a = torisferikKalinlik(Pl, L, Ma.deger, S, E); adimlar.push(a); tReq = a.deger;
    adimlar.push(te);
    const m = torisferikMawp(te.deger, L, Ma.deger, S, E); adimlar.push(m); mY = m.deger;
    if (te.deger / L < 0.002) notlar.push('t_s/L < 0.002 → Appendix 1-4(f) kontrolü gerekli (bu motorda yok).');
  } else if (tip === 'hemispherical') {
    const L = D / 2;
    adimlar.push(adim('Korozyonlu iç yarıçap', 'UG-32(f)', 'L = D/2', `${f(D)}/2`, L, 'mm'));
    const a = yarimKureKalinlik(Pl, L, S, E); adimlar.push(a); tReq = a.deger;
    if (tReq > 0.356 * L || Pl > 0.665 * S * E) {
      notlar.push('UG-32(f) sınırı aşıldı (t > 0.356L veya P > 0.665SE) → Appendix 1-3 gerekli; sonuç geçersiz.');
      r.durum = 'HESAPLANMADI';
    }
    adimlar.push(te);
    const m = yarimKureMawp(te.deger, L, S, E); adimlar.push(m); mY = m.deger;
  } else if (tip === 'flat') {
    const C = head.flat_attachment_factor;
    if (!tanimli(C)) {
      notlar.push('UG-34 C katsayısı (flat_attachment_factor) girilmemiş → hesaplanmadı.');
      return bosSonuc(id, 'head', tip, adimlar, notlar);
    }
    ctx.varsayimlar.push(`${id}: UG-34 d = korozyonlu iç çap (Di + 2·CA_iç); C = ${f(C)} kullanıcı girdisi. Şekil UG-34'teki d tanımı farklıysa sonuç geçersiz.`);
    const a = duzKapakKalinlik(Pl, D, C, S, E); adimlar.push(a); tReq = a.deger;
    adimlar.push(te);
    const m = duzKapakMawp(te.deger, D, C, S, E); adimlar.push(m); mY = m.deger;
  } else {
    notlar.push(`Bilinmeyen bombe tipi: ${tip}`);
    return bosSonuc(id, 'head', tip, adimlar, notlar);
  }
  if (te.deger <= 0) { notlar.push('Etkin kalınlık ≤ 0 → MAWP = 0.'); mY = 0; }
  return sonuclandir(r, ctx, tReq, ch, tNom, mY, ps, Pl);
}

// ── global ──────────────────────────────────────────────────────────────────

/** Global MAWP = min(bileşen MAWP'leri, kap üstüne indirgenmiş). */
export function globalMawp(bilesenler) {
  const hesaplanan = bilesenler.filter((b) => b.durum !== 'HESAPLANMADI' && Number.isFinite(b.mawp_mpa));
  if (hesaplanan.length === 0) return { deger_mpa: null, yoneten_id: null, adimlar: [] };
  let y = hesaplanan[0];
  for (const b of hesaplanan) if (b.mawp_mpa < y.mawp_mpa) y = b;
  const a = adim('Global MAWP (kap üstü)', 'UG-98', 'MAWP = min(MAWP_i)',
    `min(${hesaplanan.map((b) => `${b.id}: ${f(b.mawp_mpa)}`).join(', ')})`, y.mawp_mpa, 'MPa');
  return { deger_mpa: y.mawp_mpa, yoneten_id: y.id, adimlar: [a] };
}

/** En düşük gerilme oranı LSR = min(S_test/S) — hesaplanan bileşenlerin malzemeleri üzerinden. */
export function enDusukGerilmeOrani(project, malzemeIdleri, varsayimlar) {
  const adimlar = [];
  let lsr = Infinity;
  for (const mid of [...new Set(malzemeIdleri)]) {
    const m = malzemeBul(project, mid);
    if (!m) continue;
    let oran;
    if (tanimli(m.allowable_stress_test_temp)) {
      oran = m.allowable_stress_test_temp / m.allowable_stress;
      adimlar.push(adim(`Gerilme oranı ${mid}`, 'UG-99(b)', 'oran = S_test/S',
        `${f(m.allowable_stress_test_temp)}/${f(m.allowable_stress)}`, oran, '-'));
    } else {
      oran = 1;
      varsayimlar.push(`${mid}: test sıcaklığı izin verilen gerilmesi (allowable_stress_test_temp) yok → S_test/S = 1 kabul edildi.`);
      adimlar.push(adim(`Gerilme oranı ${mid}`, 'UG-99(b)', 'oran = S_test/S (varsayım)', '1 (S_test girilmedi)', 1, '-'));
    }
    lsr = Math.min(lsr, oran);
  }
  if (!Number.isFinite(lsr)) {
    lsr = 1;
    varsayimlar.push('LSR hesaplanacak malzeme yok → LSR = 1 kabul edildi.');
  }
  adimlar.push(adim('En düşük gerilme oranı', 'UG-99(b)', 'LSR = min(S_test/S)', '', lsr, '-'));
  return { lsr, adimlar };
}

/** Ana giriş noktası. */
export function hesaplaProje(project) {
  const ctx = baglam(project);
  const bilesenler = [];
  for (const s of project.shell_sections || []) bilesenler.push(hesaplaGovde(s, ctx));
  for (const h of project.heads || []) bilesenler.push(hesaplaBombe(h, ctx));
  if ((project.cones || []).length > 0) {
    ctx.varsayimlar.push(`Koniler (${project.cones.map((c) => c.cone_id).join(', ')}) bu motorun kapsamı DIŞINDA (UG-32(g) yok) → global MAWP ve test basınçlarına DAHİL DEĞİL; koni yönetiyorsa global MAWP olduğundan yüksek görünür.`);
  }
  if ((project.nozzles || []).length > 0 || (project.flanges || []).length > 0) {
    ctx.varsayimlar.push('Nozul/flanş MAWP sınırları (UG-37, App. 2, B16.5 sınıfı) kapsam dışı → global MAWP yalnız gövde ve bombelerden.');
  }
  for (const b of bilesenler) {
    if (b.durum === 'HESAPLANMADI') ctx.varsayimlar.push(`${b.id}: hesaplanmadı → global MAWP'ye dahil değil.`);
  }

  const gm = globalMawp(bilesenler);
  const matIds = [];
  for (const s of project.shell_sections || []) matIds.push(s.material_id);
  for (const h of project.heads || []) matIds.push(h.material_id);
  const { lsr, adimlar: lsrAdim } = enDusukGerilmeOrani(project, matIds, ctx.varsayimlar);

  let taban = gm.deger_mpa;
  const tabanAdim = [];
  if (!Number.isFinite(taban)) {
    taban = ctx.P;
    ctx.varsayimlar.push('Global MAWP hesaplanamadı → test tabanı olarak tasarım basıncı kullanıldı (UG-99(b) dipnot muafiyeti).');
    tabanAdim.push(adim('Test tabanı', 'UG-99(b) dipnot', 'taban = P_tasarım', f(ctx.P), ctx.P, 'MPa'));
  } else {
    tabanAdim.push(adim('Test tabanı', 'UG-99(b)', 'taban = global MAWP', f(taban), taban, 'MPa'));
  }
  const hA = hidrotest(taban, lsr);
  const pA = pnomatik(taban, lsr);
  ctx.varsayimlar.push('Test basınçları kap ÜSTÜNDE; test sırasındaki sıvı kafası ve UG-99(d)/UG-100 gerilme kontrolleri hesaplanmadı.');

  return {
    bilesenler,
    global_mawp: gm,
    hidrotest: { deger_mpa: hA.deger, adimlar: [...tabanAdim, ...lsrAdim, hA] },
    pnomatik: { deger_mpa: pA.deger, adimlar: [...tabanAdim, ...lsrAdim, pA] },
    varsayimlar: ctx.varsayimlar,
  };
}
