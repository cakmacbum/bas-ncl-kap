// Kıyas katmanı: siteye (yerel API) sorar ve bağımsız motor sonucuyla yan yana koyar.
// Hesap formülü YOK; yalnız alan eşleme + yüzde fark.
//
// Gerçek payload (apps/api /api/calculate, 4 örnekte doğrulandı):
//   { global_mawp_mpa, results:[{ component_id, component_type, calculation_type,
//     clause_reference, intermediate_values:[{name,value,unit}], final_result, status }], errors }
// Bileşen satırları: calculation_type 'thickness' (t_required, t_nominal_required)
//                    ve 'mawp' (MAWP). Sistem satırları component_id '' ile gelir:
//                    'hydrotest' (P_test), 'pneumatic_test' (P_test).

// ---- EŞLEME TABLOSU (düzeltme gerekirse yalnız burası) ---------------------
// bag(b): bağımsız bileşen nesnesinden değer. site: {tur, ad} -> sonuç satırı + ara değer adı
// ad === null ise final_result sayısı alınır; ad verilmiş ama yoksa final_result'a düşülür.
export const BILESEN_ESLEME = [
  { buyukluk: 't_gerekli [mm]',         bag: (b) => b.t_gerekli_mm,         site: { tur: 'thickness', ad: 't_required' } },
  { buyukluk: 't_nominal_gerekli [mm]', bag: (b) => b.t_nominal_gerekli_mm, site: { tur: 'thickness', ad: 't_nominal_required' } },
  { buyukluk: 'MAWP [MPa]',             bag: (b) => b.mawp_mpa,             site: { tur: 'mawp',      ad: 'MAWP' } },
];
export const SISTEM_ESLEME = [
  { bilesen: 'GLOBAL', buyukluk: 'Global MAWP [MPa]', bag: (r) => r.global_mawp?.deger_mpa,
    siteDoğrudan: (p) => p.global_mawp_mpa, site: null },
  { bilesen: 'SİSTEM', buyukluk: 'Hidrotest basıncı [MPa]', bag: (r) => r.hidrotest?.deger_mpa,
    site: { tur: 'hydrotest', ad: 'P_test' } },
  { bilesen: 'SİSTEM', buyukluk: 'Pnömatik test basıncı [MPa]', bag: (r) => r.pnomatik?.deger_mpa,
    site: { tur: 'pneumatic_test', ad: 'P_test' } },
];
// Site tarafında bileşen olarak değerlendirilen tipler (weld/system/nozzle... atlanmaz ama
// yalnız bu tiplerde thickness/mawp satırı aranır).
const SITE_BILESEN_TIPLERI = new Set(['shell', 'head']);

// ---- API ---------------------------------------------------------------------
function istemciKimligi() {
  const uret = () => {
    if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
    const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  };
  try {
    let id = localStorage.getItem('test-ortami-client-id');
    if (!id) { id = uret(); localStorage.setItem('test-ortami-client-id', id); }
    return id;
  } catch { return uret(); }
}

export async function siteSonucu(project, apiUrl = 'http://127.0.0.1:8000') {
  const url = `${apiUrl.replace(/\/+$/, '')}/api/calculate`;
  let yanit;
  try {
    yanit = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Client-Id': istemciKimligi() },
      body: JSON.stringify(project),
    });
  } catch (e) {
    throw new Error(`API çalışmıyor: ${apiUrl} açık mı? (Tarayıcı bağlanamadı ya da CORS reddetti; `
      + `API'yi CORS_ORIGINS=http://127.0.0.1:4322 ile başlatın.) Ayrıntı: ${e.message}`);
  }
  if (!yanit.ok) {
    let detay = '';
    try { const j = await yanit.json(); detay = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail ?? j); }
    catch { /* gövde JSON değil */ }
    throw new Error(`API ${yanit.status} döndü${detay ? `: ${detay.slice(0, 400)}` : ''}`);
  }
  return yanit.json();
}

// ---- Karşılaştırma -----------------------------------------------------------
const sayi = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

function siteDegeri(satir, ad) {
  if (!satir) return null;
  if (ad) {
    const iv = (satir.intermediate_values || []).find((x) => x.name === ad);
    if (iv && sayi(iv.value) !== null) return iv.value;
  }
  return sayi(satir.final_result);
}

function maddeMetni(satir) {
  if (!satir) return '';
  const durum = satir.status && satir.status !== 'PASS' ? ` [${satir.status}]` : '';
  return `${satir.clause_reference || ''}${durum}`.trim();
}

function satirUret(bilesen, buyukluk, bag, siteDeger, siteSatir, tol) {
  const b = sayi(bag);
  const s = sayi(siteDeger);
  let fark = null;
  let isaret = '—';
  if (b !== null && s !== null) {
    if (s === 0) fark = b === 0 ? 0 : null;
    else fark = ((b - s) / Math.abs(s)) * 100;
    if (fark === null) isaret = '❌';
    else if (Math.abs(fark) <= tol.ok) isaret = '✅';
    else if (Math.abs(fark) <= tol.uyari) isaret = '⚠️';
    else isaret = '❌';
  }
  return { bilesen, buyukluk, bagimsiz: b, site: s, fark_yuzde: fark, isaret, site_madde: maddeMetni(siteSatir) };
}

export function karsilastir(bagimsiz, payload, tol = { ok: 0.5, uyari: 2 }) {
  const sonuclar = Array.isArray(payload?.results) ? payload.results : [];
  const bul = (id, tur) => sonuclar.find((r) => r.component_id === id && r.calculation_type === tur);
  const satirlar = [];

  // Bileşenler: bağımsız motorun sırası; sonra yalnız sitede olan shell/head'ler.
  const gorulen = new Set();
  for (const b of bagimsiz?.bilesenler || []) {
    gorulen.add(b.id);
    for (const e of BILESEN_ESLEME) {
      const sr = bul(b.id, e.site.tur);
      satirlar.push(satirUret(b.id, e.buyukluk, e.bag(b), siteDegeri(sr, e.site.ad), sr, tol));
    }
  }
  const sadeceSite = new Set(sonuclar
    .filter((r) => SITE_BILESEN_TIPLERI.has(r.component_type) && r.component_id && !gorulen.has(r.component_id))
    .map((r) => r.component_id));
  for (const id of sadeceSite) {
    for (const e of BILESEN_ESLEME) {
      const sr = bul(id, e.site.tur);
      satirlar.push(satirUret(id, e.buyukluk, null, siteDegeri(sr, e.site.ad), sr, tol));
    }
  }

  // Global / hidrotest / pnömatik
  for (const e of SISTEM_ESLEME) {
    let sr = null; let sd = null;
    if (e.siteDoğrudan) sd = e.siteDoğrudan(payload || {});
    else { sr = sonuclar.find((r) => r.calculation_type === e.site.tur && !r.component_id); sd = siteDegeri(sr, e.site.ad); }
    satirlar.push(satirUret(e.bilesen, e.buyukluk, e.bag(bagimsiz || {}), sd, sr, tol));
    if (e.siteDoğrudan) satirlar[satirlar.length - 1].site_madde = 'global_mawp_mpa';
  }
  return satirlar;
}
