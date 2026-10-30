// FEA istemcisi (P12): tek worker; proje değişince debounce sonrası yeniden çözer.
// Çözüm sürerken yeni istek gelirse worker sonlandırılıp yeniden açılır (kuyruk yok, WASM yok → ucuz).
import { useEffect, useRef, useState } from "react";
import type { VesselProject } from "../types";
import type { FeaMainToWorker, FeaOptions, FeaResult, FeaWorkerToMain } from "./types";

export type FeaStatus = "idle" | "running" | "done" | "error";
export interface FeaState {
  status: FeaStatus;
  /** 0..1 — aşama ağırlıklı ilerleme. */
  progress: number;
  phase: string | null;
  result: FeaResult | null;
  error: string | null;
}

const PHASE_SPAN: Record<string, [number, number]> = {
  mesh: [0, 0.05], assemble: [0.05, 0.35], factor: [0.35, 0.9], stress: [0.9, 1],
};

let worker: Worker | null = null;
let busy = false;
let nextReqId = 1;
let handler: ((m: FeaWorkerToMain) => void) | null = null;

function getWorker(): Worker {
  if (worker) return worker;
  worker = new Worker(new URL("./fea.worker.ts", import.meta.url), { type: "module" });
  worker.onmessage = (ev: MessageEvent<FeaWorkerToMain>) => handler?.(ev.data);
  worker.onerror = (ev) => {
    busy = false;
    handler?.({ type: "error", reqId: -1, message: ev.message || "FEA worker hatası" });
  };
  return worker;
}

/** Projeyi worker'da çözer (tek seferlik, Promise). */
export function solveInWorker(project: VesselProject, options: FeaOptions = {}, onProgress?: (p: number, phase: string) => void): Promise<FeaResult> {
  if (busy) {
    worker?.terminate();
    worker = null;
    handler?.({ type: "error", reqId: -1, message: "İptal edildi (yeni istek)" });
  }
  const reqId = nextReqId++;
  busy = true;
  return new Promise((resolve, reject) => {
    handler = (m) => {
      if (m.reqId !== reqId && m.reqId !== -1) return;
      if (m.type === "progress") {
        const [a, b] = PHASE_SPAN[m.phase] ?? [0, 1];
        onProgress?.(a + (b - a) * m.fraction, m.phase);
      } else if (m.type === "result") {
        busy = false;
        resolve(m.result);
      } else {
        busy = false;
        reject(new Error(m.message));
      }
    };
    const msg: FeaMainToWorker = { type: "solve", reqId, project, options };
    getWorker().postMessage(msg);
  });
}

export function useFea(project: VesselProject | null, options: FeaOptions & { debounceMs?: number } = {}): FeaState {
  const [state, setState] = useState<FeaState>({ status: "idle", progress: 0, phase: null, result: null, error: null });
  const gen = useRef(0);
  const refine = options.refine ?? 1;
  const debounce = options.debounceMs ?? 500;

  useEffect(() => {
    if (!project) {
      setState((s) => ({ ...s, status: "idle", progress: 0, phase: null }));
      return;
    }
    const my = ++gen.current;
    const timer = setTimeout(() => {
      setState((s) => ({ ...s, status: "running", progress: 0, phase: "mesh", error: null }));
      solveInWorker(project, { refine }, (progress, phase) => {
        if (gen.current === my) setState((s) => ({ ...s, progress, phase }));
      }).then(
        (result) => { if (gen.current === my) setState({ status: "done", progress: 1, phase: null, result, error: null }); },
        (err: Error) => { if (gen.current === my) setState((s) => ({ ...s, status: "error", phase: null, error: err.message })); },
      );
    }, debounce);
    return () => clearTimeout(timer);
  }, [project, refine, debounce]);

  return state;
}
