// FEA worker (P12): ağ + çözüm ana iş parçacığı dışında; büyük ağda UI donmaz.
import type { VesselProject } from "../types";
import { runFea } from "./solver";
import type { FeaMainToWorker, FeaWorkerToMain } from "./types";

const ctx = self as unknown as DedicatedWorkerGlobalScope;
const post = (msg: FeaWorkerToMain, transfer: Transferable[] = []) => ctx.postMessage(msg, transfer);

ctx.onmessage = (ev: MessageEvent<FeaMainToWorker>) => {
  const msg = ev.data;
  if (msg.type !== "solve") return;
  const { reqId } = msg;
  try {
    let last = -1;
    const result = runFea(msg.project as VesselProject, msg.options ?? {}, (phase, fraction) => {
      const pct = Math.round(fraction * 100);
      if (pct === last && phase !== "mesh") return;
      last = pct;
      post({ type: "progress", reqId, phase, fraction });
    });
    const m = result.mesh;
    const transfer: Transferable[] = [m.nodes.buffer, m.elems.buffer, result.u.buffer, result.stress.buffer, result.vm.buffer];
    if (m.elemColumn) transfer.push(m.elemColumn.buffer);
    post({ type: "result", reqId, result }, transfer);
  } catch (err) {
    post({ type: "error", reqId, message: err instanceof Error ? err.message : String(err) });
  }
};
