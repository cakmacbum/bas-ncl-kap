import { afterEach, describe, expect, it, vi } from "vitest";
import { api, CAD_MISSING_MSG, TOO_BIG_MSG, statusMessage, unreachableMessage } from "../api";
import { defaultProject } from "../store";

vi.mock("../auth/useSession", () => ({ getAccessToken: async () => null, signOut: vi.fn() }));

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("mesaj seçimi", () => {
  it("DEV uvicorn ipucu, PROD kullanıcı dostu", () => {
    expect(unreachableMessage(true)).toContain("uvicorn");
    const p = unreachableMessage(false);
    expect(p).not.toContain("uvicorn");
    expect(p).toContain("Hesap sunucusuna şu an ulaşılamıyor");
  });
  it("413 / 503 eşlemesi", () => {
    expect(statusMessage(413)).toBe(TOO_BIG_MSG);
    expect(statusMessage(503)).toBe(CAD_MISSING_MSG);
    expect(statusMessage(500)).toBeNull();
  });
});

describe("api.calculate", () => {
  it("POST /api/calculate, gövde = proje", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ results: [], errors: [] }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const project = defaultProject();
    await api.calculate(project);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toMatch(/\/api\/calculate$/);
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toEqual(JSON.parse(JSON.stringify(project)));
  });

  it("413 -> proje çok büyük mesajı", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("{}", { status: 413 })));
    await expect(api.calculate(defaultProject())).rejects.toThrow("Proje çok büyük");
  });

  it("zaman aşımı -> kullanıcı mesajı, yavaşta onSlow", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_u: string, init: RequestInit) =>
          new Promise((_res, rej) => {
            init.signal!.addEventListener("abort", () => rej(new DOMException("aborted", "AbortError")));
          })
      )
    );
    const onSlow = vi.fn();
    const assertion = expect(api.calculate(defaultProject(), { onSlow })).rejects.toThrow(/sunucusuna/);
    await vi.advanceTimersByTimeAsync(3_100);
    expect(onSlow).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(27_000);
    await assertion;
  });
});
