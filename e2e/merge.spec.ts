import { test, expect } from "@playwright/test";
import { PDFDocument } from "pdf-lib";
import { fileURLToPath } from "node:url";

const docA = fileURLToPath(new URL("./fixtures/doc-a.pdf", import.meta.url));
const docB = fileURLToPath(new URL("./fixtures/doc-b.pdf", import.meta.url));

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("loads pages from added PDFs and shows thumbnails", async ({ page }) => {
  await page.getByLabel("Add files").setInputFiles([docA, docB]);
  await expect(page.getByLabel("doc-a.pdf Page 1")).toBeVisible();
  await expect(page.getByLabel("doc-a.pdf Page 2")).toBeVisible();
  await expect(page.getByLabel("doc-b.pdf Page 1")).toBeVisible();
  await expect(page.locator(".card img").first()).toHaveJSProperty("complete", true);
});

test("merges all pages into a downloadable PDF", async ({ page }) => {
  await page.getByLabel("Add files").setInputFiles([docA, docB]);
  await expect(page.getByLabel("doc-b.pdf Page 1")).toBeVisible();

  const download = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Save PDF" }).click(),
  ]).then(([d]) => d);

  expect(download.suggestedFilename()).toBe("merged.pdf");

  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(chunk as Buffer);
  const merged = await PDFDocument.load(Buffer.concat(chunks));
  expect(merged.getPageCount()).toBe(3);
});

test("deletes a page and restores it from the trash", async ({ page }) => {
  await page.getByLabel("Add files").setInputFiles([docA]);
  const card = page.getByLabel("doc-a.pdf Page 1");
  await card.getByRole("button", { name: "Delete" }).click();
  await expect(page.getByLabel("doc-a.pdf Page 1")).toHaveCount(0);

  await page.getByRole("button", { name: /Trash \(1\)/ }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Restore" }).click();
  await page.getByRole("button", { name: "Close" }).click();
  await expect(page.getByLabel("doc-a.pdf Page 1")).toBeVisible();
});

test("switches language to German", async ({ page }) => {
  await page.getByRole("button", { name: "DE", exact: true }).click();
  await expect(page.getByRole("button", { name: "PDF speichern" })).toBeVisible();
});
