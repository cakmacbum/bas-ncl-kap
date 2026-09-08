// Türkçe sözlük — durum, hesap tipi ve bileşen etiketleri.

export const STATUS_TR: Record<string, string> = {
  PASS: "GEÇTİ",
  FAIL: "KALDI",
  "REVIEW REQUIRED": "İNCELEME GEREKLİ",
  "NOT CALCULATED": "HESAPLANMADI",
  "OUT OF SCOPE": "KAPSAM DIŞI",
  "BLOCKED CODE DATA": "Veri Engelli (lisans)",
  "BLOCKED MISSING INPUT": "Girdi Eksik",
};

export const STATUS_CLASS: Record<string, string> = {
  PASS: "badge--pass",
  FAIL: "badge--fail",
  "REVIEW REQUIRED": "badge--review",
  "NOT CALCULATED": "badge--nc",
  "OUT OF SCOPE": "badge--scope",
  "BLOCKED CODE DATA": "badge--blocked",
  "BLOCKED MISSING INPUT": "badge--blocked",
};

export const CALC_TYPE_TR: Record<string, string> = {
  thickness: "Et kalınlığı",
  mawp: "MAWP",
  hydrotest: "Hidrostatik test",
  nozzle_reinforcement: "Nozul takviyesi",
  weld_validation: "Kaynak doğrulama",
  clash_check: "Çakışma kontrolü",
  external_pressure_check: "Dış basınç kontrolü",
  external_pressure: "Dış basınç",
  vacuum_stability: "Vakum stabilitesi",
  pressure_consistency: "Basınç tutarlılığı",
  material_check: "Malzeme kontrolü",
  saddle_stress: "Eyer gerilmesi (Zick)",
  skirt_stress: "Etek gerilmesi",
  leg_stress: "Ayak gerilmesi",
};

export const SUPPORT_TYPE_TR: Record<string, string> = {
  saddle: "Eyer (saddle)",
  skirt: "Etek (skirt)",
  leg: "Ayak (leg)",
};

export const COMPONENT_TR: Record<string, string> = {
  shell: "Gövde",
  head: "Bombe",
  nozzle: "Nozul",
  weld: "Kaynak",
  system: "Sistem",
};

export const HEAD_TYPE_TR: Record<string, string> = {
  elliptical: "Elipsoidal (2:1)",
  torispherical: "Torisferik",
  hemispherical: "Yarım küresel",
  flat: "Düz kapak",
};

export const NOZZLE_TYPE_TR: Record<string, string> = {
  flanged: "Flanşlı",
  slip_on: "Slip-on flanş",
  socket_welded: "Soket kaynaklı",
  coupling: "Manşon (coupling)",
  manway: "Adam deliği (manway)",
  pad_reinforced: "Pedli takviyeli",
};

export const ORIENTATION_TR: Record<string, string> = {
  horizontal: "Yatay",
  vertical: "Dikey",
};

export function tr(map: Record<string, string>, key: string): string {
  return map[key] ?? key;
}
