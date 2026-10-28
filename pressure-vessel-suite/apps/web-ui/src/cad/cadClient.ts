// D06 — CAD worker istemcisi. Tek paylaşılan worker (ilk kullanımda açılır, WASM lazy).
// useCadBuild: preview 150 ms / exact 800 ms debounce; yalnız en son reqId'nin sonucu uygulanır.
import { useEffect, useRef, useState } from "react";
import type {
  BuildWarning,
  Level,
  MainToWorker,
  MeshPart,
  WorkerToMain,
} from "../geometryContract";
import type { VesselProject } from "../types";

export type CadStatus = "loading" | "ready" | "building" | "error";

type Listener = (msg: WorkerToMain) => void;

let worker: Worker | null = null;
let ready = false;
let initError: string | null = null;
let nextReqId = 1;
const listeners = new Set<Listener>();
const waiters = new Map<number, Listener>();

function getWorker(): Worker {
  if (worker) return worker;
  worker = new Worker(new URL("./cad.worker.ts", import.meta.url), { type: "module" });
  worker.onmessage = (ev: MessageEvent<WorkerToMain>) => {
    const msg = ev.data;
    if (msg.type === "ready") {
      ready = true;
      initError = null;
    } else if (msg.type === "error" && msg.reqId === -1) {
      initError = msg.message;
    }
    if ("reqId" in msg) {
      const w = waiters.get(msg.reqId);
      if (w) {
        waiters.delete(msg.reqId);
        w(msg);
      }
    }
    listeners.forEach((l) => l(msg));
  };
  worker.onerror = (ev) => {
    initError = ev.message || "CAD worker hatası";
    listeners.forEach((l) => l({ type: "error", reqId: -1, message: initError! }));
  };
  send({ type: "init" });
  return worker;
}

function send(msg: MainToWorker) {
  getWorker().postMessage(msg);
}

/** Yalnız kullanıcı iptalinde: worker'ı sonlandırır (bir sonraki istekte yeniden açılır, WASM yeniden yüklenir). */
export function terminateCad() {
  worker?.terminate();
  worker = null;
  ready = false;
  for (const [id, w] of waiters) w({ type: "error", reqId: id, message: "İptal edildi" });
  waiters.clear();
}

interface CadBuildState {
  status: CadStatus;
  meshes: MeshPart[];
  warnings: BuildWarning[];
  ms: number | null;
  error: string | null;
}

const DEBOUNCE: Record<Level, number> = { preview: 150, exact: 800 };

export function useCadBuild(project: VesselProject | null, level: Level): CadBuildState {
  const [state, setState] = useState<CadBuildState>(() => ({
    status: ready ? "ready" : "loading",
    meshes: [],
    warnings: [],
    ms: null,
    error: null,
  }));
  const latestReqId = useRef(0);

  // Worker durum dinleyicisi (yükleme/hazır/init hatası + bu hook'un sonuçları)
  useEffect(() => {
    getWorker();
    const onMsg: Listener = (msg) => {
      if (msg.type === "result") {
        if (msg.reqId !== latestReqId.current) return; // eski sonuç
        setState({ status: "ready", meshes: msg.meshes, warnings: msg.warnings, ms: msg.ms, error: null });
      } else if (msg.type === "error") {
        if (msg.reqId !== latestReqId.current && msg.reqId !== -1) return;
        setState((s) => ({ ...s, status: "error", error: msg.message }));
      } else if (msg.type === "ready") {
        setState((s) => (s.status === "loading" ? { ...s, status: latestReqId.current ? "building" : "ready" } : s));
      }
    };
    listeners.add(onMsg);
    if (initError) setState((s) => ({ ...s, status: "error", error: initError }));
    return () => {
      listeners.delete(onMsg);
    };
  }, []);

  useEffect(() => {
    if (!project) return;
    const timer = setTimeout(() => {
      const reqId = nextReqId++;
      latestReqId.current = reqId;
      setState((s) => ({ ...s, status: ready ? "building" : "loading" }));
      send({ type: "build", reqId, project, level });
    }, DEBOUNCE[level]);
    return () => clearTimeout(timer);
  }, [project, level]);

  return state;
}

/** Projeyi exact seviyede STEP/STL olarak dışa aktarır ve indirmeyi tetikler. */
export function exportModel(project: VesselProject, fmt: "step" | "stl"): Promise<void> {
  return new Promise((resolve, reject) => {
    const reqId = nextReqId++;
    waiters.set(reqId, (msg) => {
      if (msg.type === "export-result") {
        const url = URL.createObjectURL(msg.blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = msg.filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        resolve();
      } else if (msg.type === "error") {
        reject(new Error(msg.message));
      }
    });
    send({ type: "export", reqId, project, format: fmt });
  });
}
