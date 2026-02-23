import { test, expect } from "playwright/test";

test("dashboard loads and shows project title", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#project-name")).toBeVisible();
});

test("status API responds", async ({ request, baseURL }) => {
  const res = await request.get(`${baseURL}/api/status`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data).toHaveProperty("areas");
});

test("docs explorer opens, filters, and previews README", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Docs Explorer" }).click();
  await expect(page.locator("#modal-docs-explorer.show")).toBeVisible();

  await page.locator("#docs-search").fill("README.md");
  await page.getByRole("button", { name: "Search" }).click();

  const readmeItem = page.locator("#docs-list .docs-item", { hasText: "README.md" }).first();
  await expect(readmeItem).toBeVisible();
  await readmeItem.click();

  await expect(page.locator("#docs-selected-meta")).toContainText("README.md");
  await expect(page.locator("#docs-preview")).toContainText("#");
});
