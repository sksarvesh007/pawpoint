import { test, expect } from "@playwright/test";
import { waitForTableLoad } from "./helpers/navigation";

test.describe("Appointments page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard/appointments");
    await waitForTableLoad(page);
  });

  test("renders page header", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Appointments" })).toBeVisible();
    await expect(page.getByRole("button", { name: "New Appointment" })).toBeVisible();
  });

  test("renders status tabs", async ({ page }) => {
    const tabs = ["All", "Scheduled", "Confirmed", "Completed", "Cancelled"];
    for (const tab of tabs) {
      await expect(page.getByRole("button", { name: tab, exact: true })).toBeVisible();
    }
  });

  test("renders provider filter", async ({ page }) => {
    const providerSelect = page.locator("select").first();
    await expect(providerSelect).toBeVisible();
    await expect(providerSelect).toContainText("All Providers");
  });

  test("renders table headers", async ({ page }) => {
    const headers = ["Date & Time", "Patient", "Provider", "Type", "Status", "Reason", "Actions"];
    for (const header of headers) {
      await expect(page.getByRole("columnheader", { name: header })).toBeVisible();
    }
  });

  test("filter by status tab", async ({ page }) => {
    await page.getByRole("button", { name: "Scheduled", exact: true }).click();
    await page.waitForTimeout(300);
    await waitForTableLoad(page);

    // Either shows scheduled appointments or empty state
    const rows = page.locator("tbody tr");
    const count = await rows.count();
    if (count > 0) {
      // If there are results, check they have the correct status badge
      const firstStatusBadge = page.locator("tbody tr").first().locator("span.capitalize").first();
      if (await firstStatusBadge.isVisible()) {
        await expect(firstStatusBadge).toContainText(/scheduled/i);
      }
    }
  });

  test("open and close create appointment modal", async ({ page }) => {
    await page.getByRole("button", { name: "New Appointment" }).click();

    const modal = page.locator("[class*='fixed inset-0']");
    await expect(modal.getByText("New Appointment")).toBeVisible();

    // Close the modal
    await modal.getByRole("button", { name: "Cancel" }).click();
    await expect(modal).toBeHidden({ timeout: 5_000 });
  });
});
