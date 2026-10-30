// Gerilme renk skalası: 0 → maxVm, mavi → camgöbeği → yeşil → sarı → kırmızı.
// Saf fonksiyonlar (three bağımlılığı yok) — test edilebilir.

export type RGB = [number, number, number]; // 0..1

const STOPS: RGB[] = [
  [0.13, 0.25, 0.85], // mavi
  [0.0, 0.75, 0.9],   // camgöbeği
  [0.15, 0.8, 0.3],   // yeşil
  [0.98, 0.9, 0.15],  // sarı
  [0.9, 0.12, 0.1],   // kırmızı
];

/** t∈[0,1] → renk; aralık dışı değerler uçlara kenetlenir (lejant 0…max gösterir). */
export function scaleColor(t: number): RGB {
  const x = Number.isFinite(t) ? Math.min(1, Math.max(0, t)) : 0;
  const f = x * (STOPS.length - 1);
  const i = Math.min(STOPS.length - 2, Math.floor(f));
  const k = f - i;
  const a = STOPS[i], b = STOPS[i + 1];
  return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
}

/** MPa değeri → renk (0…max). max ≤ 0 ise skalanın alt ucu. */
export function stressColor(value: number, max: number): RGB {
  return scaleColor(max > 0 ? value / max : 0);
}

/** Lejant için CSS linear-gradient (üstte max, altta 0). */
export function scaleGradientCss(): string {
  const n = 8;
  const parts: string[] = [];
  for (let i = 0; i <= n; i++) {
    const [r, g, b] = scaleColor(1 - i / n);
    parts.push(`rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)}) ${Math.round((i / n) * 100)}%`);
  }
  return `linear-gradient(to bottom, ${parts.join(", ")})`;
}

/** Lejant etiketleri: 0…max arası eşit aralıklı (n+1 adet), MPa. */
export function scaleTicks(max: number, n = 4): number[] {
  return Array.from({ length: n + 1 }, (_, i) => (max * i) / n);
}

/** allowable çizgisinin lejanttaki konumu (0=alt, 1=üst). Skalanın dışındaysa null. */
export function allowablePosition(allowable: number | null, max: number): number | null {
  if (allowable == null || !(max > 0) || allowable < 0 || allowable > max) return null;
  return allowable / max;
}
