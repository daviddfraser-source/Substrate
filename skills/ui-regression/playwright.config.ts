import { defineConfig } from "@playwright/test";

const baseURL = process.env.UI_BASE_URL || "http://127.0.0.1:8090";

export default defineConfig({
  testDir: "./tests",
  reporter: [["list"]],
  use: {
    baseURL,
    headless: true,
  },
});
