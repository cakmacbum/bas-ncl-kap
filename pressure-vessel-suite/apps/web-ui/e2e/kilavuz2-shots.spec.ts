// Kılavuz-2 ekran görüntüleri: açılış, şablonlar, tasarım koşulları, geometri alt adımları (ekran + tam form),
// hesap girdileri, hesap sonuçları, 3D model, rapor.  Çıktı: docs/kilavuz2/img/NN-ad.png
// Çalıştır: npx playwright test e2e/kilavuz2-shots.spec.ts
// Not: Her adım `attempt` içinde çalışır; biri başarısız olursa sonraki adımlar devam eder, hatalar sonda listelenir.
import { expect, test, type Page, type APIRequestContext } from "@playwright/test";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(here, "../../../docs/kilavuz2/img");
const clientId = "00000000-0000-4000-8000-00000000c1a2";
const API = "http://127.0.0.1:5173/api";
const W = 1600;
const H = 1000;

test.use({ viewport: { width: W, height: H } });

const failures: string[] = [];
const taken: string[] = [];

async function attempt(name: string, fn: () => Promise<void>) {
  try { await fn(); } catch (e) {
    const msg = `${name}: ${(e as Error).message.split("\n")[0]}`;
    failures.push(msg);
    console.log("BAŞARISIZ →", msg);
  }
}

/** Standart 1600x1000 ekran görüntüsü. */
async function shot(page: Page, name: string, wait = 800) {
  await page.waitForTimeout(wait);
  await page.screenshot({ path: path.join(out, `${name}.png`) });
  taken.push(name);
}

/** İç kaydırmalı alanlar dahil içerik sığacak kadar yüksek pencerede çeker; sonra 1000'e döner. */
async function neededExtra(page: Page): Promise<number> {
  return page.evaluate(() => {
    let max = 0;
    for (const el of Array.from(document.querySelectorAll<HTMLElement>("*"))) {
      const oy = getComputedStyle(el).overflowY;
      if ((oy === "auto" || oy === "scroll") && el.scrollHeight > el.clientHeight + 4) {
        max = Math.max(max, el.scrollHeight - el.clientHeight);
      }
    }
    return max;
  });
}
async function tall(page: Page, name: string, opts: { selector?: string; maxH?: number; wait?: number } = {}) {
  const maxH = opts.maxH ?? 6500;
  await page.waitForTimeout(opts.wait ?? 600);
  for (let pass = 0; pass < 2; pass++) {
    const extra = await neededExtra(page);
    const vp = page.viewportSize()!;
    if (extra <= 8) break;
    await page.setViewportSize({ width: W, height: Math.min(vp.height + extra + 24, maxH) });
    await page.waitForTimeout(700);
  }
  const file = path.join(out, `${name}.png`);
  if (opts.selector) await page.locator(opts.selector).first().screenshot({ path: file });
  else await page.screenshot({ path: file });
  taken.push(name);
  await page.setViewportSize({ width: W, height: H });
  await page.waitForTimeout(300);
}

const openDetails = (page: Page) =>
  page.evaluate(() => document.querySelectorAll("details").forEach((d) => { (d as HTMLDetailsElement).open = true; }));

const acc = (page: Page, title: string) => page.locator("button.accordion__head", { hasText: title }).first();
async function openAcc(page: Page, title: string) {
  const b = acc(page, title);
  if ((await b.getAttribute("aria-expanded")) !== "true") await b.click();
}
async function closeAcc(page: Page, title: string) {
  const b = acc(page, title);
  if ((await b.getAttribute("aria-expanded")) === "true") await b.click();
}
const field = (page: Page, label: string) => page.locator("label.field", { hasText: label }).first();

async function createProject(request: APIRequestContext, tank: string, number: string, name: string) {
  const source = JSON.parse(await readFile(path.join(here, "fixtures", `${tank}.json`), "utf8"));
  source.project_number = number;
  source.project_name = name;
  const res = await request.post(`${API}/projects`, { data: source, headers: { "X-Client-Id": clientId } });
  expect(res.ok(), `proje oluşturulamadı (${res.status()})`).toBeTruthy();
  return (await res.json()).id as string;
}

async function loadProject(page: Page, id: string) {
  await page.getByRole("button", { name: "Projeleri Yenile" }).click();
  await page.getByLabel("Proje aç").selectOption(id);
  await page.waitForTimeout(800);
}

async function gotoGeometry(page: Page) {
  await page.getByRole("button", { name: /Kap Geometrisi/ }).click();
  await expect(page.locator("canvas").first()).toBeVisible({ timeout: 60_000 });
  await page.waitForTimeout(2500);
}
const subTab = (page: Page, i: number) =>
  page.getByRole("tablist", { name: "Geometri alt adımları" }).getByRole("tab").nth(i);

async function calculate(page: Page) {
  await page.getByRole("button", { name: /Hesap Sonuçları/ }).click();
  await page.getByRole("button", { name: /^(↻ Yeniden )?Hesapla$/ }).first().click();
  await expect(page.getByText("Global MAWP")).toBeVisible({ timeout: 120_000 });
  await page.waitForTimeout(800);
}

test.beforeAll(async () => { await mkdir(out, { recursive: true }); });

test("kilavuz2 — dikey ayaklı tank (tam akış)", async ({ page, request }) => {
  test.setTimeout(900_000);
  const id = await createProject(request, "vertical-leg", "KLV-201", "Dikey ayaklı tank (örnek)");
  page.on("dialog", (d) => void d.accept());
  await page.addInitScript((cid) => localStorage.setItem("pvs.clientId", cid), clientId);
  await page.goto("/");

  // ---- Adım 1: açılış, şablonlar, kayıtlı proje
  await attempt("01-acilis", () => shot(page, "01-acilis"));
  await attempt("02-yeni-proje", () => tall(page, "02-yeni-proje"));
  await attempt("03-sablon-hava", async () => {
    await page.getByRole("button", { name: "Yatay Hava Tankı şablonunu uygula" }).click();
    await page.waitForTimeout(800);
    await tall(page, "03-yeni-proje-sablon-hava-tanki");
  });
  await attempt("04-sablon-vakum", async () => {
    await page.getByRole("button", { name: "Vakumlu Proses Tankı şablonunu uygula" }).click();
    await page.waitForTimeout(800);
    await tall(page, "04-yeni-proje-sablon-vakum-tanki");
  });
  await attempt("05-kayitli", async () => {
    await loadProject(page, id);
    await tall(page, "05-yeni-proje-kayitli-proje");
  });

  // ---- Adım 2: tasarım koşulları
  await attempt("06-tasarim", async () => {
    await page.getByRole("button", { name: /Tasarım Koşulları/ }).click();
    await tall(page, "06-tasarim-kosullari");
  });
  await attempt("07-yardim-balonu", async () => {
    const dot = field(page, "Dış Basınç").locator(".help-dot").first();
    await dot.scrollIntoViewIfNeeded();
    await dot.hover();
    await shot(page, "07-tasarim-yardim-balonu", 500);
  });
  await attempt("08-tahliye", async () => {
    const sel = field(page, "Tahliye sistemi").locator("select");
    await sel.selectOption("enabled");
    await page.mouse.move(5, 5);
    await tall(page, "08-tasarim-tahliye-etkin");
    await sel.selectOption("disabled");
  });

  // ---- Adım 3: geometri
  await gotoGeometry(page);
  await attempt("09-31", async () => {
    await subTab(page, 0).click();
    await page.locator(".gw-ring").first().click();
    await shot(page, "09-geometri-31-govde", 1500);
    await openDetails(page);
    await tall(page, "10-geometri-31-govde-form", { selector: ".geo-forms", maxH: 3800 });
  });
  await attempt("11-31-ekle", async () => {
    await page.getByRole("button", { name: "+ Sol" }).click();
    await page.getByRole("radio", { name: "Koni" }).click();
    await tall(page, "11-geometri-31-uc-ekle-koni-form", { selector: ".geo-forms", maxH: 3800 });
    await page.getByRole("button", { name: "Vazgeç" }).click();
  });
  await attempt("12-32", async () => {
    await subTab(page, 1).click();
    await shot(page, "12-geometri-32-bombe", 1500);
    await openDetails(page);
    await tall(page, "13-geometri-32-bombe-form", { selector: ".geo-forms", maxH: 3800 });
  });
  await attempt("14-33", async () => {
    await subTab(page, 2).click();
    await page.locator(".gw-table tbody tr").first().click();
    await shot(page, "14-geometri-33-nozul", 1500);
    await openDetails(page);
    await tall(page, "15-geometri-33-nozul-form", { selector: ".geo-forms", maxH: 3800 });
  });
  await attempt("16-34", async () => {
    await subTab(page, 3).click();
    await page.getByRole("button", { name: /Manşon ekle/ }).click();
    await page.waitForTimeout(1200);
    await shot(page, "16-geometri-34-mansonlar", 1500);
    await openDetails(page);
    await tall(page, "17-geometri-34-manson-form", { selector: ".geo-forms", maxH: 3800 });
    await page.locator(".gw-del").first().click();
  });
  await attempt("18-35", async () => {
    await subTab(page, 4).click();
    await page.locator(".gw-table tbody tr").first().click();
    await shot(page, "18-geometri-35-mesnet-ayak", 1500);
    await openDetails(page);
    await tall(page, "19-geometri-35-mesnet-ayak-form", { selector: ".geo-forms", maxH: 4200 });
  });

  // ---- Önizleme sekmeleri
  await attempt("20-3d", async () => {
    await page.getByRole("tab", { name: "3D Önizleme" }).click();
    await shot(page, "20-onizleme-3d", 2500);
  });
  await attempt("21-kesit", async () => {
    await page.getByRole("tab", { name: "Ölçülü Kesit" }).click();
    await shot(page, "21-onizleme-olculu-kesit", 2000);
  });
  await attempt("22-kesin", async () => {
    await page.getByRole("tab", { name: "Kesin Model" }).click();
    await shot(page, "22-onizleme-kesin-model", 7000);
  });
  await attempt("23-gerilme", async () => {
    await page.getByRole("tab", { name: "Gerilme" }).click();
    await shot(page, "23-onizleme-gerilme", 4000);
  });
  await attempt("24-disa-aktar", async () => {
    await page.getByRole("tab", { name: "3D Önizleme" }).click();
    await page.getByRole("button", { name: /Dışa aktar/ }).click();
    await shot(page, "24-onizleme-disa-aktar-menu", 600);
    await page.keyboard.press("Escape");
  });

  // ---- Hesap girdileri sekmesi
  await attempt("25-girdiler", async () => {
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await shot(page, "25-girdiler-sekme", 1500);
  });
  await attempt("26-nozul-yukleri", async () => {
    await openAcc(page, "Nozul dış yükleri");
    await field(page, "Fr (radyal)").locator("input").fill("1000");
    await tall(page, "26-girdiler-nozul-dis-yukleri", { selector: ".geo-forms", maxH: 3800 });
    await page.getByRole("button", { name: "Bu nozulun yük takımını sil" }).click();
    await closeAcc(page, "Nozul dış yükleri");
  });
  await attempt("27-nozul-ayrinti", async () => {
    await page.getByRole("tab", { name: "Geometri" }).click();
    await subTab(page, 2).click();
    await page.locator(".gw-table tbody tr").first().click();
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await openAcc(page, "Nozul ayrıntıları");
    await tall(page, "27-girdiler-nozul-ayrintilari", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Nozul ayrıntıları");
  });
  await attempt("28-flans", async () => {
    await openAcc(page, "Flanşlar");
    await page.getByRole("button", { name: /Flanş Ekle/ }).click();
    await tall(page, "28-girdiler-flanslar-appendix2", { selector: ".geo-forms", maxH: 4800 });
    await page.locator(".nozzle-card__del").first().click();
    await closeAcc(page, "Flanşlar");
  });
  await attempt("29-destek-ayak", async () => {
    await page.getByRole("tab", { name: "Geometri" }).click();
    await subTab(page, 4).click();
    await page.locator(".gw-table tbody tr").first().click();
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await openAcc(page, "Destek ayrıntıları");
    await tall(page, "29-girdiler-destek-ayak", { selector: ".geo-forms", maxH: 4800 });
  });
  const legSecs: [string, string][] = [
    ["Bağlantı ve Kesit", "30-girdiler-ayak-baglanti-kesit"],
    ["Takviye Pedi", "31-girdiler-ayak-takviye-pedi"],
    ["Taban Plakası", "32-girdiler-ayak-taban-plakasi"],
    ["Kaynaklar", "33-girdiler-ayak-kaynaklar"],
    ["WRC Katsayıları", "34-girdiler-ayak-wrc"],
  ];
  for (const [title, name] of legSecs) {
    await attempt(name, async () => {
      const b = page.locator("button.accordion__head", { hasText: title }).first();
      if ((await b.getAttribute("aria-expanded")) !== "true") await b.click();
      await tall(page, name, { selector: ".geo-forms", maxH: 6500 });
      await b.click();
    });
  }
  await attempt("35-malzeme", async () => {
    await closeAcc(page, "Destek ayrıntıları");
    await openAcc(page, "Malzeme");
    await tall(page, "35-girdiler-malzeme", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Malzeme");
  });
  await attempt("36-kaynak", async () => {
    await openAcc(page, "Kaynak & NDT");
    await tall(page, "36-girdiler-kaynak-ndt", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Kaynak & NDT");
  });
  await attempt("37-bom", async () => {
    await tall(page, "37-girdiler-bom-maliyet", { selector: ".geo-forms", maxH: 4800 });
  });
  await attempt("38-kulak", async () => {
    await openAcc(page, "Kaldırma kulağı");
    await page.getByRole("button", { name: "Kaldırma kulağı ekle" }).click();
    await tall(page, "38-girdiler-kaldirma-kulagi", { selector: ".geo-forms", maxH: 4800 });
    await page.getByRole("button", { name: "Kulakları kaldır" }).click();
    await closeAcc(page, "Kaldırma kulağı");
  });
  await attempt("39-koni", async () => {
    await openAcc(page, "Koni birleşimi");
    await tall(page, "39-girdiler-koni-birlesimi-ayak-kabi", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Koni birleşimi");
  });

  // ---- Adım 4: hesap sonuçları
  await attempt("40-sonuc", async () => {
    await calculate(page);
    await shot(page, "40-sonuc-ozet", 1200);
    await page.getByText("Global MAWP").first().scrollIntoViewIfNeeded();
    await page.evaluate(() => document.querySelector(".kpi-row")?.scrollIntoView({ block: "start" }));
    await shot(page, "40b-sonuc-kpi-ve-tablolar", 800);
    await page.evaluate(() => document.querySelector(".main")?.scrollTo(0, 0));
    await tall(page, "41-sonuc-tam", { maxH: 9000 });
  });
  await attempt("42-satir", async () => {
    const row = page.locator("tr.table__expand").first();
    await row.scrollIntoViewIfNeeded();
    await row.click();
    await shot(page, "42-sonuc-satir-acik", 800);
  });

  // ---- Adım 5: 3D model
  await attempt("43-3d-model", async () => {
    await page.locator("nav button.step", { hasText: "3D Model" }).click();
    await page.getByRole("button", { name: /3D Modeli Oluştur/ }).click();
    await page.waitForTimeout(4000);
    await shot(page, "43-3d-model", 2000);
    await page.getByRole("button", { name: /Kesit Görünümü/ }).click();
    await shot(page, "44-3d-model-kesit", 2000);
  });

  // ---- Adım 6: rapor
  await attempt("45-rapor", async () => {
    await page.getByRole("button", { name: /Rapor & Çıktı/ }).click();
    await page.getByRole("button", { name: /Raporu Üret/ }).click();
    await expect(page.locator("iframe.report-frame")).toBeVisible({ timeout: 90_000 });
    await shot(page, "45-rapor-sayfa", 4000);
    await tall(page, "49-rapor-sayfa-tam-acinim", { maxH: 9000, wait: 1500 });
  });
  await attempt("46-rapor-html", async () => {
    const res = await request.get(`${API}/projects/${id}/report.html`, { headers: { "X-Client-Id": clientId } });
    expect(res.ok(), `rapor ${res.status()}`).toBeTruthy();
    const html = await res.text();
    await writeFile(path.join(out, "_rapor-ornek.html"), html, "utf8");
    const rp = await page.context().newPage();
    await rp.setViewportSize({ width: 1200, height: 1500 });
    await rp.setContent(html, { waitUntil: "load" });
    await rp.waitForTimeout(800);
    const total = await rp.evaluate(() => document.documentElement.scrollHeight);
    for (let i = 0; i < 3 && i * 1500 < total; i++) {
      const name = `${46 + i}-rapor-html-${i + 1}`;
      await rp.screenshot({ path: path.join(out, `${name}.png`), fullPage: true, clip: { x: 0, y: i * 1500, width: 1200, height: Math.min(1500, total - i * 1500) } });
      taken.push(name);
    }
    await rp.close();
  });
});

test("kilavuz2 — yatay eyerli tank (Zick eyer girdileri)", async ({ page, request }) => {
  test.setTimeout(600_000);
  const id = await createProject(request, "horizontal-saddle", "KLV-202", "Yatay eyerli tank (örnek)");
  page.on("dialog", (d) => void d.accept());
  await page.addInitScript((cid) => localStorage.setItem("pvs.clientId", cid), clientId);
  await page.goto("/");
  await attempt("H-yukle", () => loadProject(page, id));
  await attempt("H-geometri", () => gotoGeometry(page));
  await attempt("50-eyer", async () => {
    await subTab(page, 4).click();
    await page.locator(".gw-table tbody tr").first().click();
    await shot(page, "50-yatay-geometri-35-mesnet-eyer", 1500);
    await openDetails(page);
    await tall(page, "51-yatay-geometri-35-eyer-form", { selector: ".geo-forms", maxH: 4200 });
  });
  await attempt("52-eyer-girdi", async () => {
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await openAcc(page, "Destek ayrıntıları");
    await tall(page, "52-yatay-girdiler-eyer-zick", { selector: ".geo-forms", maxH: 4800 });
  });
  await attempt("53-3d", async () => {
    await page.getByRole("tab", { name: "Geometri" }).click();
    await page.getByRole("tab", { name: "3D Önizleme" }).click();
    await shot(page, "53-yatay-onizleme-3d", 2500);
  });
  await attempt("54-sonuc", async () => {
    await calculate(page);
    await shot(page, "54-yatay-sonuc-ozet", 1200);
    await tall(page, "55-yatay-sonuc-tam", { maxH: 9000 });
  });
});

test("kilavuz2 — etek kolon (etek + taban halkası girdileri)", async ({ page, request }) => {
  test.setTimeout(600_000);
  const id = await createProject(request, "skirt-column", "KLV-203", "Etekli kolon (örnek)");
  page.on("dialog", (d) => void d.accept());
  await page.addInitScript((cid) => localStorage.setItem("pvs.clientId", cid), clientId);
  await page.goto("/");
  await attempt("S-yukle", () => loadProject(page, id));
  await attempt("S-geometri", () => gotoGeometry(page));
  await attempt("60-etek", async () => {
    await subTab(page, 4).click();
    await page.locator(".gw-table tbody tr").first().click();
    await shot(page, "60-etek-geometri-35-mesnet", 1500);
    await openDetails(page);
    await tall(page, "61-etek-geometri-35-form", { selector: ".geo-forms", maxH: 4200 });
  });
  await attempt("62-etek-girdi", async () => {
    await page.getByRole("tab", { name: "Hesap girdileri" }).click();
    await openAcc(page, "Destek ayrıntıları");
    await tall(page, "62-etek-girdiler-destek", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Destek ayrıntıları");
  });
  await attempt("63-halka", async () => {
    await openAcc(page, "Koni birleşimi");
    await tall(page, "63-etek-girdiler-taban-halkasi", { selector: ".geo-forms", maxH: 4800 });
    await closeAcc(page, "Koni birleşimi");
  });
  await attempt("64-sonuc", async () => {
    await calculate(page);
    await tall(page, "64-etek-sonuc-tam", { maxH: 9000 });
  });
});

test.afterAll(async () => {
  await writeFile(path.join(out, "_calisma-ozeti.json"), JSON.stringify({ taken, failures }, null, 2), "utf8");
  console.log(`ÇEKİLEN: ${taken.length}  BAŞARISIZ: ${failures.length}`);
  failures.forEach((f) => console.log(" - " + f));
});
