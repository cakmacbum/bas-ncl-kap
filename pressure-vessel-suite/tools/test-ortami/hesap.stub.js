// GEÇİCİ MOTOR STUB — gerçek motor ./hesap.js (başka paket) yoksa index.html bunu yükler.
// Hesap yapmaz: sözleşme şeklini döndürür, sayısal sonuçlar null'dır (kıyas '—' gösterir).
export const STUB = true;

export function hesaplaProje(project) {
  const adim = (ad, deger, birim) => ({ ad, madde: '—', formul: '(stub: hesap yok)', yerine: '', deger, birim });
  const bilesenler = [];
  for (const s of project.shell_sections || []) {
    bilesenler.push({ id: s.section_id, tip: 'shell', alt_tip: 'cylindrical', adimlar: [adim('D (iç çap)', s.inside_diameter, 'mm')],
      t_gerekli_mm: null, t_nominal_gerekli_mm: null, mawp_mpa: null, durum: 'HESAPLANMADI', notlar: ['MOTOR STUB'] });
  }
  for (const h of project.heads || []) {
    bilesenler.push({ id: h.head_id, tip: 'head', alt_tip: h.type, adimlar: [adim('D (iç çap)', h.inside_diameter, 'mm')],
      t_gerekli_mm: null, t_nominal_gerekli_mm: null, mawp_mpa: null, durum: 'HESAPLANMADI', notlar: ['MOTOR STUB'] });
  }
  return {
    bilesenler,
    global_mawp: { deger_mpa: null, yoneten_id: null, adimlar: [] },
    hidrotest: { deger_mpa: null, adimlar: [] },
    pnomatik: { deger_mpa: null, adimlar: [] },
    varsayimlar: ['MOTOR STUB: bağımsız motor (hesap.js) bulunamadı; sonuçlar boş.'],
  };
}
