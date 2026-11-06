// Kılavuz PDF için ekran görüntüleri: her iş akışı adımı + geometri alt adımları.
// Çalıştır: npx playwright test e2e/kilavuz-shots.spec.ts  → docs/kilavuz/img/*.png
import { expect, test, type Page } from "@playwright/test";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(here, "../../../docs/kilavuz/img");
const clientId = "00000000-0000-4000-8000-00000000c1a0";
const tanks = ["vertical-leg", "horizontal-saddle"];

test.use({ viewport: { width: 1600, height: 1000 } });

async function shot(page: Page, name: string, full = false) {
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(out, `${name}.png`), fullPage: full });
}

for (const tank of tanks) {
  test(`kılavuz görüntüleri — ${tank}`, async ({ page, request }) => {
    test.setTimeout(240_000);
    await mkdir(out, { recursive: true });
    const source = JSON.parse(await readFile(path.join(here, "fixtures", `${tank}.json`), "utf8"));
    source.project_number = tank === "vertical-leg" ? "KLV-001" : "KLV-002";
    source.project_name = tank === "vertical-leg" ? "Dikey ayaklı tank (örnek)" : "Yatay eyerli tank (örnek)";
    const create = await request.post("http://127.0.0.1:5173/api/projects", { data: source, headers: { "X-Client-Id": clientId } });
    expect(create.ok()).toBeTruthy();
    const { id } = await create.json();
    page.on("dialog", (d) => void d.accept());
    await page.addInitScript((cid) => localStorage.setItem("pvs.clientId", cid), clientId);

    await page.goto("/");
    const p = tank === "vertical-leg" ? "v" : "h";
    if (tank === "vertical-leg") await shot(page, "00-acilis");
    await page.getByRole("button", { name: "Projeleri Yenile" }).click();
    await page.getByLabel("Proje aç").selectOption(id);
    await shot(page, `${p}-01-yeni-proje`, true);

    await page.getByRole("button", { name: /Tasarım Koşulları/ }).click();
    await shot(page, `${p}-02-tasarim-kosullari`, true);

    await page.getByRole("button", { name: /Kap Geometrisi/ }).click();
    await expect(page.locator("canvas").first()).toBeVisible({ timeout: 60_000 });
    const tabs = page.getByRole("tablist", { name: "Geometri alt adımları" }).getByRole("tab");
    const n = await tabs.count();
    for (let i = 0; i < n; i++) {
      await tabs.nth(i).click();
      await page.waitForTimeout(1500);
      await shot(page, `${p}-03-geometri-3${i + 1}`);
    }
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await shot(page, `${p}-03-hesap-girdileri`, true);
    await page.getByRole("tab", { name: "Geometri" }).click();
    for (const [label, file] of [["Ölçülü Kesit", "olculu-kesit"], ["Gerilme", "gerilme"]] as const) {
      const t = page.getByRole("tab", { name: label }).or(page.getByRole("button", { name: label }));
      if (await t.count()) { await t.first().click(); await page.waitForTimeout(2500); await shot(page, `${p}-03-${file}`); }
    }

    await page.getByRole("button", { name: /Hesap Sonuçları/ }).click();
    await page.getByRole("button", { name: /^(↻ Yeniden )?Hesapla$/ }).first().click();
    await expect(page.getByText("Global MAWP")).toBeVisible({ timeout: 90_000 });
    await shot(page, `${p}-04-hesap-sonuclari`);
    await shot(page, `${p}-04-hesap-sonuclari-tam`, true);

    await page.getByRole("button", { name: /3D Model/ }).click();
    await page.waitForTimeout(3000);
    await shot(page, `${p}-05-3d-model`);

    await page.getByRole("button", { name: /Rapor & Çıktı/ }).click();
    await page.waitForTimeout(2000);
    await shot(page, `${p}-06-rapor`, true);
  });
}
