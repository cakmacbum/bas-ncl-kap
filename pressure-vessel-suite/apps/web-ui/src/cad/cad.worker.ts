/// <reference lib="webworker" />
// D06 — tarayıcı OCCT worker'ı (replicad + replicad-opencascadejs). Protokol: D00 §3.
// - init: WASM lazy (?url → ayrı asset), indirme ilerlemesi `loading` ile bildirilir.
// - build: seviye başına tek bekleyen yuva; parçalar arasında daha yeni istek gelirse kalan atlanır.
// - export: exact cache'i kullanır; STEP = varlık başına adlı katı compound'u, STL ikili.
import { setOC, type Shape3D } from "replicad";
import type {
  BuildWarning,
  Level,
  MainToWorker,
  MeshPart,
  WorkerToMain,
} from "../geometryContract";
import type { VesselProject } from "../types";
import { ShapeCache } from "./cache";
import { MESH_TOLERANCE } from "./parts";
import { buildShapes as buildShapesImpl, sweepWarnings } from "./buildShapes";
import { exportFilename, stepBlob, stlBlob } from "./export";

const ctx = self as unknown as DedicatedWorkerGlobalScope;
const post = (msg: WorkerToMain, transfer: Transferable[] = []) => ctx.postMessage(msg, transfer);

// ---- OCCT başlatma ----
let ocReady: Promise<void> | null = null;

async function fetchWithProgress(url: string): Promise<ArrayBuffer> {
  const res = await fetch(url);
  if (!res.ok || !res.body) throw new Error(`WASM indirilemedi (${res.status})`);
  const total = Number(res.headers.get("content-length")) || 0;
  const reader = res.body.getReader();
  const chunks: Uint8Array[] = [];
  let got = 0;
  let lastPct = -1;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    got += value.byteLength;
    if (total) {
      const pct = Math.floor((got / total) * 100);
      if (pct !== lastPct) {
        lastPct = pct;
        post({ type: "loading", progress: Math.min(0.95, (got / total) * 0.95) });
      }
    }
  }
  const buf = new Uint8Array(got);
  let off = 0;
  for (const c of chunks) {
    buf.set(c, off);
    off += c.byteLength;
  }
  return buf.buffer;
}

function initOC(): Promise<void> {
  ocReady ??= (async () => {
    post({ type: "loading", progress: 0 });
    const [{ default: opencascade }, { default: wasmUrl }] = await Promise.all([
      import("replicad-opencascadejs"),
      import("replicad-opencascadejs/wasm?url"),
    ]);
    const wasmBinary = await fetchWithProgress(wasmUrl);
    // print: OCCT STEP yazıcısının istatistik dökümünü sustur (printErr açık kalır).
    const oc = await opencascade({ wasmBinary, locateFile: () => wasmUrl, print: () => {} });
    setOC(oc);
    post({ type: "loading", progress: 1 });
    post({ type: "ready" });
  })();
  return ocReady;
}

// ---- Cache (varlık başına) ----
interface MeshData {
  positions: Float32Array;
  normals: Float32Array;
  indices: Uint32Array;
  edges: Float32Array;
}
const shapes = new ShapeCache<Shape3D>();
const meshes = new ShapeCache<MeshData>();
const warningCache = new Map<string, BuildWarning[]>();
const lastKeys: Record<Level, Set<string>> = { preview: new Set(), exact: new Set() };

function sweepCaches() {
  const keep = new Set([...lastKeys.preview, ...lastKeys.exact]);
  shapes.sweep(keep);
  meshes.sweep(keep);
  sweepWarnings(warningCache, keep);
}

function meshOf(key: string, shape: Shape3D, level: Level): MeshData {
  const hit = meshes.get(key);
  if (hit) return hit;
  const tol = MESH_TOLERANCE[level];
  const m = shape.mesh(tol);
  const e = shape.meshEdges(tol);
  const data: MeshData = {
    positions: new Float32Array(m.vertices),
    normals: new Float32Array(m.normals),
    indices: new Uint32Array(m.triangles),
    edges: new Float32Array(e.lines),
  };
  meshes.set(key, data);
  return data;
}

// ---- İş kuyruğu: seviye başına tek bekleyen build yuvası + FIFO export ----
type BuildReq = Extract<MainToWorker, { type: "build" }>;
type ExportReq = Extract<MainToWorker, { type: "export" }>;
const pendingBuild: Record<Level, BuildReq | null> = { preview: null, exact: null };
const exportQueue: ExportReq[] = [];
let running = false;

const yieldToEvents = () => new Promise<void>((r) => setTimeout(r, 0));

function buildShapes(project: VesselProject, level: Level, cancelled: () => boolean) {
  return buildShapesImpl(project, level, cancelled, { shapes, warnings: warningCache }, (used) => { lastKeys[level] = used; }, yieldToEvents);
}

async function runBuild(req: BuildReq) {
  const t0 = performance.now();
  const isStale = () => {
    const p = pendingBuild[req.level];
    return p != null && p.reqId > req.reqId;
  };
  const built = await buildShapes(req.project, req.level, isStale);
  if (!built) return; // daha yeni istek var; bu atlandı
  const out: MeshPart[] = [];
  const transfer: Transferable[] = [];
  for (const p of built.parts) {
    if (isStale()) return;
    const m = meshOf(p.key, p.shape, req.level);
    // Cache'teki diziler korunur; kopyalar transfer edilir.
    const part: MeshPart = {
      partId: p.partId,
      kind: p.kind,
      positions: m.positions.slice(),
      normals: m.normals.slice(),
      indices: m.indices.slice(),
      edges: m.edges.slice(),
    };
    transfer.push(part.positions.buffer, part.normals.buffer, part.indices.buffer, part.edges!.buffer);
    out.push(part);
  }
  sweepCaches();
  post({ type: "result", reqId: req.reqId, level: req.level, meshes: out, warnings: built.warnings, ms: performance.now() - t0 }, transfer);
}

async function runExport(req: ExportReq) {
  const built = await buildShapes(req.project, "exact", () => false);
  if (!built || built.parts.length === 0) throw new Error("Dışa aktarılacak katı yok");
  sweepCaches();
  const blob = req.format === "step" ? stepBlob(built.parts) : stlBlob(built.parts);
  post({ type: "export-result", reqId: req.reqId, blob, filename: exportFilename(req.project, req.format) });
}

async function pump() {
  if (running) return;
  running = true;
  try {
    await initOC();
    for (;;) {
      const ex = exportQueue.shift();
      if (ex) {
        try {
          await runExport(ex);
        } catch (err) {
          post({ type: "error", reqId: ex.reqId, message: err instanceof Error ? err.message : String(err) });
        }
        continue;
      }
      // preview önce (etkileşim), sonra exact
      const level: Level | null = pendingBuild.preview ? "preview" : pendingBuild.exact ? "exact" : null;
      if (!level) break;
      const req = pendingBuild[level]!;
      pendingBuild[level] = null;
      try {
        await runBuild(req);
      } catch (err) {
        post({ type: "error", reqId: req.reqId, message: err instanceof Error ? err.message : String(err) });
      }
    }
  } catch (err) {
    // OCCT başlatılamadı: bekleyen tüm isteklere hata
    const message = `OCCT başlatılamadı: ${err instanceof Error ? err.message : String(err)}`;
    ocReady = null;
    for (const l of ["preview", "exact"] as const) {
      const r = pendingBuild[l];
      if (r) post({ type: "error", reqId: r.reqId, message });
      pendingBuild[l] = null;
    }
    for (const ex of exportQueue.splice(0)) post({ type: "error", reqId: ex.reqId, message });
    post({ type: "error", reqId: -1, message });
  } finally {
    running = false;
  }
}

ctx.onmessage = (ev: MessageEvent<MainToWorker>) => {
  const msg = ev.data;
  if (msg.type === "init") {
    void pump();
  } else if (msg.type === "build") {
    const cur = pendingBuild[msg.level];
    if (!cur || msg.reqId > cur.reqId) pendingBuild[msg.level] = msg;
    void pump();
  } else if (msg.type === "export") {
    exportQueue.push(msg);
    void pump();
  }
};
