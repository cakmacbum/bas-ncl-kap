// FastAPI istemcisi (Vite /api proxy üzerinden localhost:8000).

import type {
  VesselProject,
  CalcPayload,
  ProjectSummary,
  StepRecognition,
} from "./types";

import { getAccessToken, signOut } from "./auth/useSession";
import { getClientId } from "./clientId";

const BASE = ((import.meta.env.VITE_API_URL as string | undefined) || "").replace(/\/$/, "") + "/api";

export const TIMEOUT_MS = 30_000;
export const SLOW_MS = 3_000;
export const CAD_MISSING_MSG =
  "Sunucuda CAD motoru yok. Kesin modeli Kap Geometrisi → Dışa aktar menüsünden indirin.";
export const TOO_BIG_MSG = "Proje çok büyük (sunucu sınırı 2 MB). Bileşen/nozul sayısını azaltın.";

// Üretimde kullanıcı dostu, geliştirmede uvicorn ipucu içeren bağlantı hatası.
export function unreachableMessage(dev: boolean): string {
  return dev
    ? "API sunucusuna bağlanılamadı. Backend çalışıyor mu? " +
        "(pressure-vessel-suite kökünden: uvicorn apps.api.main:app --reload)"
    : "Hesap sunucusuna şu an ulaşılamıyor. Geometri ve 3D çalışmaya devam eder; birkaç saniye sonra tekrar deneyin.";
}

// Durum koduna göre kullanıcı mesajı (yoksa null → sunucu detayı kullanılır).
export function statusMessage(status: number): string | null {
  if (status === 413) return TOO_BIG_MSG;
  if (status === 503) return CAD_MISSING_MSG;
  return null;
}

// Her istekte Bearer token ekler; 401'de oturumu kapatır (AuthGate giriş ekranına döner).
// 30 sn zaman aşımı (AbortController); `onSlow` ilk yanıt 3 sn'yi geçerse çağrılır (soğuk başlangıç).
export async function authFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
  opts: { onSlow?: () => void } = {}
): Promise<Response> {
  const token = await getAccessToken();
  const headers = new Headers(init.headers);
  headers.set("X-Client-Id", getClientId());
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const ctrl = new AbortController();
  const killTimer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  const slowTimer = opts.onSlow ? setTimeout(opts.onSlow, SLOW_MS) : undefined;
  try {
    const res = await fetch(input, { ...init, headers, signal: ctrl.signal });
    if (res.status === 401 && token) void signOut();
    return res;
  } finally {
    clearTimeout(killTimer);
    if (slowTimer) clearTimeout(slowTimer);
  }
}

async function blobUrl(url: string, init?: RequestInit): Promise<string> {
  let res: Response;
  try {
    res = await authFetch(url, init);
  } catch {
    throw new Error(unreachableMessage(import.meta.env.DEV));
  }
  if (!res.ok) throw new Error(statusMessage(res.status) ?? `İndirilemedi (${res.status})`);
  return URL.createObjectURL(await res.blob());
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const mapped = statusMessage(res.status);
    if (mapped) throw new Error(mapped);
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* JSON değil (ör. proxy hatası) — statusText'te kal */
    }
    // Backend çalışmıyorsa Vite proxy'si jenerik 5xx döndürür; net yönlendir.
    if (res.status >= 500 && (!detail || /internal server error/i.test(detail))) {
      detail = unreachableMessage(import.meta.env.DEV);
    }
    if (typeof detail !== "string") detail = JSON.stringify(detail);
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

// Ağ hatası (backend tümüyle kapalı → fetch reddedilir) için de net mesaj.
async function fetchJson<T>(input: RequestInfo, init?: RequestInit, opts?: { onSlow?: () => void }): Promise<T> {
  let res: Response;
  try {
    res = await authFetch(input, init, opts);
  } catch {
    throw new Error(unreachableMessage(import.meta.env.DEV));
  }
  return jsonOrThrow<T>(res);
}

export const api = {
  async importStep(file: File): Promise<StepRecognition> {
    let res: Response;
    try {
      res = await authFetch(`${BASE}/import/step`, {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream", "X-Filename": encodeURIComponent(file.name) },
        body: file,
      });
    } catch {
      throw new Error(unreachableMessage(import.meta.env.DEV));
    }
    if (res.status === 413) throw new Error("Dosya 20 MB sınırını aşıyor.");
    if (res.status === 415) throw new Error("Dosya STEP (ISO-10303-21) değil.");
    if (res.status === 503) throw new Error("CAD motoru kurulu değil.");
    return jsonOrThrow<StepRecognition>(res);
  },
  async listProjects(): Promise<ProjectSummary[]> {
    return fetchJson(`${BASE}/projects`);
  },

  async getProject(id: string): Promise<VesselProject> {
    return fetchJson(`${BASE}/projects/${encodeURIComponent(id)}`);
  },

  async listRevisions(id: string): Promise<{ revision: number; created_at?: string }[]> {
    return fetchJson(`${BASE}/projects/${encodeURIComponent(id)}/revisions`);
  },

  async getRevision(id: string, n: number): Promise<VesselProject> {
    return fetchJson(`${BASE}/projects/${encodeURIComponent(id)}/revisions/${n}`);
  },

  async health(): Promise<{ status: string; cad_available: boolean }> {
    return fetchJson(`${BASE}/health`);
  },

  async createProject(
    project: VesselProject
  ): Promise<{ id: string; input_file_hash: string }> {
    return fetchJson(`${BASE}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
  },

  async updateProject(
    id: string,
    project: VesselProject
  ): Promise<{ id: string; input_file_hash: string }> {
    return fetchJson(`${BASE}/projects/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
  },

  // Durumsuz hesap: güncel proje gövdede gider, kayıt gerekmez.
  async calculate(project: VesselProject, opts?: { onSlow?: () => void }): Promise<CalcPayload> {
    return fetchJson(
      `${BASE}/calculate`,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project) },
      opts
    );
  },

  // Başlık gerektiren rapor için blob URL (iframe / yeni sekme).
  reportBlobUrl(project: VesselProject): Promise<string> {
    return blobUrl(`${BASE}/report.html`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(project),
    });
  },

  async downloadStep(id: string): Promise<void> {
    const href = await blobUrl(`${BASE}/projects/${id}/model.step`);
    const a = document.createElement("a");
    a.href = href;
    a.download = `${id}.step`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(href), 10_000);
  },

  reportUrl(id: string): string {
    return `${BASE}/projects/${id}/report.html`;
  },

  stepUrl(id: string): string {
    return `${BASE}/projects/${id}/model.step`;
  },

  stlUrl(id: string): string {
    return `${BASE}/projects/${id}/model.stl`;
  },
};
