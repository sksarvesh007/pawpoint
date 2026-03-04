import { test, expect } from "@playwright/test";

test.describe("Sidebar navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/dashboard/);
  });

  test("displays clinic name", async ({ page }) => {
    const sidebar = page.locator("aside");
    await expect(sidebar.getByText("Veterinary Clinic")).toBeVisible();
  });

  test("all nav sections are visible", async ({ page }) => {
    const sidebar = page.locator("aside");
    await expect(sidebar.getByText("APPLICATIONS")).toBeVisible();
    await expect(sidebar.getByText("OTHERS")).toBeVisible();
    await expect(sidebar.getByText("SUPPORT")).toBeVisible();
  });

  test("all nav links are present", async ({ page }) => {
    const sidebar = page.locator("aside");
    const links = [
      "Home",
      "Inbox",
      "Appointments",
      "Patients",
      "Call Log",
      "Chat Log",
      "Voice Bot",
      "Chat Widget",
      "Reports",
      "Widgets",
      "Settings",
      "Security",
      "Help",
    ];
    for (const label of links) {
      await expect(sidebar.getByText(label, { exact: true })).toBeVisible();
    }
  });

  test("navigate to Patients", async ({ page }) => {
    await page.locator("aside").getByText("Patients", { exact: true }).click();
    await page.waitForURL(/\/dashboard\/patients/);
    await expect(page.getByRole("heading", { name: "Patients" })).toBeVisible();
  });

  test("navigate to Appointments", async ({ page }) => {
    await page.locator("aside").getByText("Appointments", { exact: true }).click();
    await page.waitForURL(/\/dashboard\/appointments/);
    await expect(page.getByRole("heading", { name: "Appointments" })).toBeVisible();
  });

  test("navigate to Home", async ({ page }) => {
    // First go to patients to change away from home
    await page.goto("/dashboard/patients");
    await page.waitForURL(/\/dashboard\/patients/);

    await page.locator("aside").getByText("Home", { exact: true }).click();
    await page.waitForURL(/\/dashboard$/);
  });

  test("active link has highlighted styling", async ({ page }) => {
    // On /dashboard, the "Home" link should be active with bg-white/70
    const homeLink = page.locator("aside").getByText("Home", { exact: true }).locator("..");
    await expect(homeLink).toHaveClass(/bg-white\/70/);
  });
});
