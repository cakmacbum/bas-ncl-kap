// node --test pressure-vessel-suite/tools/test-ortami/hesap.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import * as H from './hesap.js';

const IN = 25.4;
const PSI = 0.006894757293168361;
const here = dirname(fileURLToPath(import.meta.url));

function yakin(gercek, beklenen, tol = 0.001, msg = '') {
  const fark = Math.abs(gercek - beklenen) / Math.abs(beklenen);
  assert.ok(fark <= tol, `${msg} beklenen ${beklenen}, bulunan ${gercek} (fark %${(fark * 100).toFixed(3)})`);
}

// ── Yayınlanmış vakalar (docs/validation/asme-worked-examples.md) — SI'ya çevrilerek ──

test('V-01 UG-27(c)(1) PVE-FT s.6 → 0.1004 in', () => {
  const a = H.ug27Cevresel(125 * PSI, 16 * IN, 20000 * PSI, 1.0);
  yakin(a.deger / IN, 0.1004);
  assert.equal(a.madde, 'UG-27(c)(1)');
  assert.equal(a.birim, 'mm');
});

test('V-02 UG-27(c)(2) PVE-S13 s.4 → 0.3560 in', () => {
  yakin(H.ug27Boyuna(284 * PSI, 42.125 * IN, 19700 * PSI, 0.85).deger / IN, 0.3560);
});

test('V-03 UG-27(c)(2) PVE-S13 s.6 → 0.4778 in', () => {
  yakin(H.ug27Boyuna(267 * PSI, 60.125 * IN, 19700 * PSI, 0.85).deger / IN, 0.4778);
});

test('V-08 gövde MAWP PVE-FT s.24 → 816.88 psig', () => {
  const t = 0.3281 * IN, R = (14 / 2 - 0.3281) * IN, S = 17100 * PSI;
  const p = Math.min(H.ug27CevreselMawp(t, R, S, 1).deger, H.ug27BoyunaMawp(t, R, S, 1).deger);
  yakin(p / PSI, 816.88);
});

test('V-09 2:1 eliptik MAWP PVE-FT s.3 → 218.80 psig', () => {
  yakin(H.elipsoidalMawp(0.39 * IN, 71.22 * IN, 20000 * PSI, 1).deger / PSI, 218.80);
});

test('V-07 UG-99(b)/UG-100 PVE-FT s.4 → 284.44 / 240.68 psig (taban MAWP)', () => {
  yakin(H.hidrotest(218.80 * PSI, 1).deger / PSI, 284.44);
  yakin(H.pnomatik(218.80 * PSI, 1).deger / PSI, 240.68);
  yakin(H.hidrotest(816.88 * PSI, 1).deger / PSI, 1061.94);
});

test('V-10 UG-32(f) yarım küre PVE-CMP → 0.2474 in', () => {
  yakin(H.yarimKureKalinlik(420 * PSI, 23.5 * IN, 20000 * PSI, 1).deger / IN, 0.2474);
});

test('V-13 UG-32(d) 2:1 eliptik PVE-CMP → 0.4947 in', () => {
  yakin(H.elipsoidalKalinlik(420 * PSI, 47 * IN, 20000 * PSI, 1).deger / IN, 0.4947);
});

test('V-16 boru hattı: Do girdili gövde, R = Do/2 − t + CA (PVE-S13 s.4) → t_boyuna 0.3560 in', () => {
  const proje = {
    design_conditions: { design_pressure: 284 * PSI, design_temperature: 100, corrosion_allowance_internal: 0.125 * IN },
    shell_sections: [{ section_id: 'S1', outside_diameter: 86 * IN, nominal_thickness: 1 * IN, tangent_length: 1000,
      material_id: 'M', weld_joint_id: 'W', internal_corrosion_allowance: 0.125 * IN, external_corrosion_allowance: 0, mill_tolerance: 0 }],
    heads: [], materials: [{ material_id: 'M', allowable_stress: 19700 * PSI, temperature: 100 }],
    welds: [{ joint_id: 'W', joint_type: 'circumferential', joint_efficiency: 0.85 }],
  };
  const s = H.hesaplaProje(proje).bilesenler[0];
  const R = s.adimlar.find((a) => a.ad === 'Korozyonlu iç yarıçap');
  yakin(R.deger / IN, 42.125, 1e-9, 'R');
  const tb = s.adimlar.find((a) => a.madde === 'UG-27(c)(2)' && a.birim === 'mm');
  yakin(tb.deger / IN, 0.3560);
});

// ── Formül özdeşlikleri ──

test('torisferik r = 0.06L → M = 1.770621 ve 0.885·P·L/(S·E − 0.1·P) ile özdeş', () => {
  const M = H.torisferikM(1000, 60).deger;
  yakin(M, 1.770621, 1e-6);
  const P = 1.5, L = 1000, S = 138, E = 1;
  yakin(H.torisferikKalinlik(P, L, M, S, E).deger, (0.885 * P * L) / (S * E - 0.1 * P), 1e-3);
});

test('eliptik K: D/2h = 2 → K = 1', () => {
  yakin(H.elipsoidalK(1000, 250).deger, 1, 1e-12);
});

// ── İç tutarlılık: t_gerekli → MAWP = P ──

test('iç tutarlılık: her formülde MAWP(t_gerekli) = P', () => {
  const P = 2.5, S = 138, E = 0.85, R = 512, D = 1024, C = 0.3;
  yakin(H.ug27CevreselMawp(H.ug27Cevresel(P, R, S, E).deger, R, S, E).deger, P, 1e-9);
  yakin(H.ug27BoyunaMawp(H.ug27Boyuna(P, R, S, E).deger, R, S, E).deger, P, 1e-9);
  yakin(H.elipsoidalMawp(H.elipsoidalKalinlik(P, D, S, E).deger, D, S, E).deger, P, 1e-9);
  yakin(H.elipsoidalMawp(H.elipsoidalKalinlik(P, D, S, E, 1.3).deger, D, S, E, 1.3).deger, P, 1e-9);
  const M = H.torisferikM(1050, 70).deger;
  yakin(H.torisferikMawp(H.torisferikKalinlik(P, 1050, M, S, E).deger, 1050, M, S, E).deger, P, 1e-9);
  yakin(H.yarimKureMawp(H.yarimKureKalinlik(P, R, S, E).deger, R, S, E).deger, P, 1e-9);
  yakin(H.duzKapakMawp(H.duzKapakKalinlik(P, D, C, S, E).deger, D, C, S, E).deger, P, 1e-9);
});

function tekBilesen(ek) {
  return {
    orientation: 'vertical',
    design_conditions: { design_pressure: 10, design_temperature: 200, corrosion_allowance_internal: 6 },
    shell_sections: [], heads: [],
    materials: [{ material_id: 'M', allowable_stress: 138, allowable_stress_test_temp: 150, temperature: 200 }],
    welds: [{ joint_id: 'W', joint_type: 'longitudinal', joint_efficiency: 0.85 }],
    ...ek,
  };
}

test('iç tutarlılık (V-16 deseni): t_nominal_gerekli nominal olarak verilince MAWP = P', () => {
  const ortak = { material_id: 'M', weld_joint_id: 'W', internal_corrosion_allowance: 6, external_corrosion_allowance: 1, mill_tolerance: 12.5 };
  const tipler = [
    { tip: 'shell', b: { section_id: 'S', inside_diameter: 50, tangent_length: 500, ...ortak } },
    { tip: 'head', b: { head_id: 'E', type: 'elliptical', inside_diameter: 50, ...ortak } },
    { tip: 'head', b: { head_id: 'T', type: 'torispherical', inside_diameter: 500, outside_diameter: 540, ...ortak } },
    { tip: 'head', b: { head_id: 'H', type: 'hemispherical', inside_diameter: 500, forming_thinning: 1.5, ...ortak } },
    { tip: 'head', b: { head_id: 'F', type: 'flat', inside_diameter: 300, flat_attachment_factor: 0.33, ...ortak } },
  ];
  for (const { tip, b } of tipler) {
    const mk = (tn) => tekBilesen(tip === 'shell' ? { shell_sections: [{ ...b, nominal_thickness: tn }] } : { heads: [{ ...b, nominal_thickness: tn }] });
    const r1 = H.hesaplaProje(mk(9)).bilesenler[0];
    const r2 = H.hesaplaProje(mk(r1.t_nominal_gerekli_mm)).bilesenler[0];
    yakin(r2.mawp_mpa, 10, 1e-9, `${r1.id}`);
    assert.equal(r2.durum, 'PASS', r1.id);
    assert.equal(r1.durum, 'FAIL', r1.id);
  }
});

test('korozyon yönü: CA artınca gerekli kalınlık artar, MAWP düşer (R büyür)', () => {
  const mk = (ca) => tekBilesen({ shell_sections: [{ section_id: 'S', inside_diameter: 1000, tangent_length: 1000, nominal_thickness: 20,
    material_id: 'M', weld_joint_id: 'W', internal_corrosion_allowance: ca, external_corrosion_allowance: 0, mill_tolerance: 0 }] });
  const a = H.hesaplaProje(mk(0)).bilesenler[0];
  const b = H.hesaplaProje(mk(3)).bilesenler[0];
  assert.ok(b.t_gerekli_mm > a.t_gerekli_mm);
  assert.ok(b.mawp_mpa < a.mawp_mpa);
  const R = b.adimlar.find((x) => x.ad === 'Korozyonlu iç yarıçap');
  assert.equal(R.deger, 503);
});

test('düz kapak C yoksa HESAPLANMADI; torisferik yarıçap yoksa varsayım yazılır', () => {
  const r = H.hesaplaProje(tekBilesen({ heads: [
    { head_id: 'F', type: 'flat', inside_diameter: 300, nominal_thickness: 30, material_id: 'M', internal_corrosion_allowance: 0 },
    { head_id: 'T', type: 'torispherical', inside_diameter: 1000, nominal_thickness: 30, material_id: 'M', weld_joint_id: 'W', internal_corrosion_allowance: 0 },
  ] }));
  assert.equal(r.bilesenler[0].durum, 'HESAPLANMADI');
  assert.equal(r.global_mawp.yoneten_id, 'T');
  assert.ok(r.varsayimlar.some((v) => v.includes('T:') && v.includes('L = Do')));
  assert.ok(r.varsayimlar.some((v) => v.includes('r = 0.06·L')));
});

test('test basınçları global MAWP tabanlı ve LSR = min(S_test/S)', () => {
  const r = H.hesaplaProje(tekBilesen({ design_conditions: { design_pressure: 1, design_temperature: 200, corrosion_allowance_internal: 0 },
    shell_sections: [{ section_id: 'S', inside_diameter: 1000, tangent_length: 1000, nominal_thickness: 20, material_id: 'M', weld_joint_id: 'W',
      internal_corrosion_allowance: 0, external_corrosion_allowance: 0, mill_tolerance: 0 }] }));
  const m = r.global_mawp.deger_mpa;
  assert.ok(m > 1);
  yakin(r.hidrotest.deger_mpa, 1.3 * m * (150 / 138), 1e-12);
  yakin(r.pnomatik.deger_mpa, 1.1 * m * (150 / 138), 1e-12);
});

test('statik kafa: dikey kap, alt bileşen yerel basınçla hesaplanır, MAWP üste indirgenir', () => {
  const ortak = { material_id: 'M', weld_joint_id: 'W', internal_corrosion_allowance: 0, external_corrosion_allowance: 0, mill_tolerance: 0, nominal_thickness: 10 };
  const p = tekBilesen({
    design_conditions: { design_pressure: 1, design_temperature: 200, fluid_density_kg_m3: 1000, liquid_level_mm: 5000 },
    heads: [{ head_id: 'HB', type: 'elliptical', inside_diameter: 1000, straight_flange_length: 0, ...ortak },
      { head_id: 'HT', type: 'elliptical', inside_diameter: 1000, straight_flange_length: 0, ...ortak }],
    shell_sections: [{ section_id: 'S', inside_diameter: 1000, tangent_length: 2000, ...ortak }],
    component_sequence: [{ component_type: 'head', component_id: 'HB' }, { component_type: 'shell', component_id: 'S' }, { component_type: 'head', component_id: 'HT' }],
  });
  const r = H.hesaplaProje(p);
  const hb = r.bilesenler.find((b) => b.id === 'HB');
  const ps = hb.adimlar.find((a) => a.ad === 'Statik sıvı kafası').deger;
  yakin(ps, 1000 * 9.80665 * 5 / 1e6, 1e-12);
  const s = r.bilesenler.find((b) => b.id === 'S');
  const psS = s.adimlar.find((a) => a.ad === 'Statik sıvı kafası').deger;
  yakin(psS, 1000 * 9.80665 * 4.75 / 1e6, 1e-12); // gövde alt kotu = 1000/4 = 250 mm
});

// ── Fixture ──

test('fixture vessel_project_five_component.json çökmeden işlenir', () => {
  const p = JSON.parse(readFileSync(join(here, '../../tests/fixtures/vessel_project_five_component.json'), 'utf8'));
  const r = H.hesaplaProje(p);
  assert.equal(r.bilesenler.length, 4);
  for (const b of r.bilesenler) {
    assert.ok(['shell', 'head'].includes(b.tip));
    assert.ok(['PASS', 'FAIL', 'HESAPLANMADI'].includes(b.durum));
    assert.ok(Number.isFinite(b.t_gerekli_mm) && Number.isFinite(b.mawp_mpa), b.id);
    for (const a of b.adimlar) for (const k of ['ad', 'madde', 'formul', 'yerine', 'deger', 'birim']) assert.ok(k in a, `${b.id} ${k}`);
  }
  // El hesabı: SHELL-01 R = 500 + 2 = 502, E = 1.0 (WJ-01 boyuna) → t = 1.2·502/(138 − 0.72)
  const s1 = r.bilesenler.find((b) => b.id === 'SHELL-01');
  yakin(s1.t_gerekli_mm, (1.2 * 502) / (138 - 0.72), 1e-12);
  assert.ok(r.global_mawp.yoneten_id);
  assert.ok(Number.isFinite(r.hidrotest.deger_mpa) && Number.isFinite(r.pnomatik.deger_mpa));
  assert.ok(r.varsayimlar.some((v) => v.includes('Koniler')));
  assert.ok(r.varsayimlar.some((v) => v.startsWith('Statik kafa yok')));
  assert.ok(r.varsayimlar.some((v) => v.includes('S_test/S = 1')));
});
