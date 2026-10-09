// FastAPI istemcisi (Vite /api proxy üzerinden localhost:8000).

import type {
  VesselProject,
  CalcPayload,
  ProjectSummary,
  GeometryAgentInterpretRequest,
  GeometryAgentSuggestion,
  StepRecognition,
} from "./types";

import { getAccessToken, signOut } from "./auth/useSession";
import { getClientId } from "./clientId";

const BASE = ((import.meta.env.VITE_API_URL as string | undefined) || "").replace(/\/$/, "") + "/api";

// Her istekte Bearer token ekler; 401'de oturumu kapatır (AuthGate giriş ekranına döner).
export async function authFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const token = await getAccessToken();
  const headers = new Headers(init.headers);
  headers.set("X-Client-Id", getClientId());
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(input, { ...init, headers });
  if (res.status === 401 && token) void signOut();
  return res;
}

async function blobUrl(url: string): Promise<string> {
  const res = await authFetch(url);
  if (!res.ok) throw new Error(`İndirilemedi (${res.status})`);
  return URL.createObjectURL(await res.blob());
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* JSON değil (ör. proxy hatası) — statusText'te kal */
    }
    // Backend çalışmıyorsa Vite proxy'si jenerik 5xx döndürür; net yönlendir.
    if (res.status >= 500 && (!detail || /internal server error/i.test(detail))) {
      detail =
        "API sunucusuna ulaşılamadı veya sunucu hatası. Backend çalışıyor mu? " +
        "(pressure-vessel-suite kökünden: uvicorn apps.api.main:app --reload)";
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

// Ağ hatası (backend tümüyle kapalı → fetch reddedilir) için de net mesaj.
async function fetchJson<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await authFetch(input, init);
  } catch {
    throw new Error(
      "API sunucusuna bağlanılamadı. Backend çalışıyor mu? " +
        "(pressure-vessel-suite kökünden: uvicorn apps.api.main:app --reload)"
    );
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
      throw new Error("API sunucusuna bağlanılamadı. Backend çalışıyor mu?");
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

  async calculate(id: string): Promise<CalcPayload> {
    return fetchJson(`${BASE}/projects/${id}/calculate`, { method: "POST" });
  },

  async interpretGeometry(
    payload: GeometryAgentInterpretRequest
  ): Promise<GeometryAgentSuggestion> {
    return fetchJson(`${BASE}/agent/geometry/interpret`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },

  // Başlık gerektiren dosyalar için blob URL (iframe / yeni sekme / indirme).
  reportBlobUrl(id: string): Promise<string> {
    return blobUrl(`${BASE}/projects/${id}/report.html`);
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
