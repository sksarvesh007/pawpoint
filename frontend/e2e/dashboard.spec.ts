import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/dashboard/);
  });

  test("renders dashboard heading", async ({ page }) => {
    // The DashboardContent has a "Dashboard" heading or the clinic name
    // Wait generously for SSE data to load
    await expect(page.getByText("Dashboard")).toBeVisible({ timeout: 15_000 });
  });

  test("renders stats cards", async ({ page }) => {
    const statsLabels = [
      "Calls Answered",
      "Appointments",
      "Call Coverage",
      "Chat Sessions",
    ];
    for (const label of statsLabels) {
      await expect(page.getByText(label).first()).toBeVisible({ timeout: 15_000 });
    }
  });
});
