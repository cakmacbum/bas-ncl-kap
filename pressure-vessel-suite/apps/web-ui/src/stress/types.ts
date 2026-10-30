// Gerilme alanı sözleşmesi (P03 üretir, P04 görselleştirir). Birimler: mm, MPa.
// Nokta, CAD model çerçevesindedir: kap ekseni +Z, radyal düzlem XY (vesselModel.componentFrames ile aynı).

export type StressZone = "membrane" | "discontinuity" | "nozzle" | "head" | "support" | "unknown";

export type StressSample = {
  vm: number;      // von Mises eşdeğeri, MPa
  hoop: number;    // çevresel (σθ), MPa
  axial: number;   // boyuna/meridyen (σz/σφ), MPa
  zone: StressZone;
};

export type StressField = {
  at: (p: [number, number, number]) => StressSample;
  allowable: number | null; // izin verilen gerilme S (MPa) — renk skalası referansı; yoksa null
  maxVm: number;            // tahmini en yüksek vm (skala üst sınırı)
};
