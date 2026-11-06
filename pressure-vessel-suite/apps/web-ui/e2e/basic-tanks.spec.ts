import { expect, test } from "@playwright/test";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const clientId = "00000000-0000-4000-8000-0000000e2e01";
const tanks = ["vertical-leg", "horizontal-saddle", "skirt-column"];
const fixturePath = (tank: string) => path.join(here, "fixtures", `${tank}.json`);

for (const tank of tanks) {
  test(`${tank} tank renders and calculates in the UI`, async ({ page, request }) => {
    const health = await request.get("http://127.0.0.1:5173/api/health").catch(() => null);
    test.skip(!health?.ok(), "FastAPI API unavailable: start it from pressure-vessel-suite with python -m uvicorn apps.api.main:app --port 8000");
    const source = JSON.parse(await readFile(fixturePath(tank), "utf8"));
    source.project_number = `E2E-${tank}`;
    source.project_name = `E2E ${tank}`;
    const create = await request.post("http://127.0.0.1:5173/api/projects", { data: source, headers: { "X-Client-Id": clientId } });
    expect(create.ok(), `${tank}: project create failed (${create.status()})`).toBeTruthy();

    const { id } = await create.json();
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("dialog", (dialog) => void dialog.accept());
    await page.addInitScript((id) => localStorage.setItem("pvs.clientId", id), clientId);
    await page.goto("/");
    await page.getByRole("button", { name: "Projeleri Yenile" }).click();
    await page.getByLabel("Proje aç").selectOption(id);
    const geometryNav = page.getByRole("button", { name: /Kap Geometrisi/ });
    await geometryNav.click();
    await expect(page.locator("canvas").first()).toBeVisible({ timeout: 60_000 });
    await expect.poll(() => page.locator("canvas").first().evaluate((c: HTMLCanvasElement) => c.width * c.height)).toBeGreaterThan(0);

    await page.getByRole("button", { name: /Hesap Sonuçları/ }).click();
    // Hesap, önceki adımlardan gelen sonuçla hazır olabilir ("Yeniden Hesapla") ya da elle tetiklenir ("Hesapla").
    const run = page.getByRole("button", { name: /^(↻ Yeniden )?Hesapla$/ });
    await run.first().click();
    await expect(page.getByText("Global MAWP")).toBeVisible({ timeout: 90_000 });
    await expect(page.locator("table.table tbody tr").first()).toBeVisible();
    await expect(page.getByText(/Error|Internal Server Error/i)).toHaveCount(0);
    await expect(page.locator("body")).not.toBeEmpty();
    expect(errors, `${tank}: browser errors`).toEqual([]);
    const shots = path.join(here, "__screenshots__");
    await mkdir(shots, { recursive: true });
    await page.screenshot({ path: path.join(shots, `${tank}.png`), fullPage: true });
  });
}
