import { test } from "@playwright/test";
import { readFile } from "node:fs/promises";
test("probe", async ({ page, request }) => {
  const cid = "00000000-0000-4000-8000-0000000e2e01";
  const src = JSON.parse(await readFile("e2e/fixtures/vertical-leg.json", "utf8"));
  const { id } = await (await request.post("http://127.0.0.1:5173/api/projects", { data: src, headers: { "X-Client-Id": cid } })).json();
  await page.addInitScript((i) => localStorage.setItem("pvs.clientId", i), cid);
  await page.goto("/");
  await page.getByRole("button", { name: "Projeleri Yenile" }).click();
  await page.getByLabel("Proje aç").selectOption(id);
  await page.getByRole("button", { name: /Kap Geometrisi/ }).click();
  await page.getByRole("button", { name: /Hesap Sonuçları/ }).click();
  await page.waitForTimeout(8000);
  console.log((await page.locator("main").innerText()).slice(0, 600));
});
