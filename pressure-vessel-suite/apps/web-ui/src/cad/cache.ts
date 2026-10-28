// Varlık başına katı cache'i (D00 §3): stableHash(params+frame+level) → değer.
// OCCT nesneleri WASM belleğinde yaşar; atılan girdiler `delete()` ile serbest bırakılır.

/** Anahtar sırasından bağımsız, kararlı JSON. undefined alanlar atlanır. */
export function stableStringify(v: unknown): string {
  if (v === null || typeof v !== "object") {
    return typeof v === "number" && !Number.isFinite(v) ? "null" : JSON.stringify(v) ?? "null";
  }
  if (Array.isArray(v)) return `[${v.map(stableStringify).join(",")}]`;
  const o = v as Record<string, unknown>;
  const keys = Object.keys(o).filter((k) => o[k] !== undefined).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(o[k])}`).join(",")}}`;
}

/** FNV-1a 64 bit (iki 32 bit yarı) → 16 hane hex. */
export function stableHash(v: unknown): string {
  const s = stableStringify(v);
  let h1 = 0x811c9dc5;
  let h2 = 0x01000193 ^ s.length;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 0x01000193);
    h2 = Math.imul(h2 ^ c, 0x5bd1e995);
  }
  return (h1 >>> 0).toString(16).padStart(8, "0") + (h2 >>> 0).toString(16).padStart(8, "0");
}

interface Deletable { delete?: () => void }

/** Basit Map cache; `sweep(keep)` kullanılmayanları siler (ve OCCT belleğini bırakır). */
export class ShapeCache<V> {
  private map = new Map<string, V>();
  constructor(private dispose: (v: V) => void = (v) => (v as Deletable)?.delete?.()) {}

  get(key: string): V | undefined { return this.map.get(key); }
  has(key: string): boolean { return this.map.has(key); }
  set(key: string, v: V): void {
    const old = this.map.get(key);
    if (old !== undefined && old !== v) this.dispose(old);
    this.map.set(key, v);
  }
  get size(): number { return this.map.size; }

  sweep(keep: Set<string>): void {
    for (const [k, v] of this.map) {
      if (!keep.has(k)) {
        this.dispose(v);
        this.map.delete(k);
      }
    }
  }
}
