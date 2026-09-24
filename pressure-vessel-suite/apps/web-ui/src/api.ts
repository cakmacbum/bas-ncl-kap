// FastAPI istemcisi (Vite /api proxy üzerinden localhost:8000).

import type {
  VesselProject,
  CalcPayload,
  ProjectSummary,
  GeometryAgentInterpretRequest,
  GeometryAgentSuggestion,
} from "./types";

const BASE = "/api";

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
    res = await fetch(input, init);
  } catch {
    throw new Error(
      "API sunucusuna bağlanılamadı. Backend çalışıyor mu? " +
        "(pressure-vessel-suite kökünden: uvicorn apps.api.main:app --reload)"
    );
  }
  return jsonOrThrow<T>(res);
}

export const api = {
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
