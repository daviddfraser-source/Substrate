import { test, expect } from "@playwright/test";

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
