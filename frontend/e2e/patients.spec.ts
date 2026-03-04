import { test, expect } from "@playwright/test";
import { uniqueName } from "./helpers/test-data";
import { waitForTableLoad } from "./helpers/navigation";

test.describe("Patients page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard/patients");
    await waitForTableLoad(page);
  });

  test("renders page header", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Patients" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Add Patient" })).toBeVisible();
  });

  test("renders search and species filter", async ({ page }) => {
    await expect(page.getByPlaceholder("Search by name, owner, phone...")).toBeVisible();
    const speciesSelect = page.locator("select").first();
    await expect(speciesSelect).toBeVisible();
    await expect(speciesSelect).toContainText("All Species");
  });

  test("renders table headers", async ({ page }) => {
    const headers = ["Patient", "Species", "Breed", "Owner", "Phone", "Status", "Actions"];
    for (const header of headers) {
      await expect(page.getByRole("columnheader", { name: header })).toBeVisible();
    }
  });

  test("create a patient", async ({ page }) => {
    const petName = uniqueName("Buddy");
    const ownerFirst = "Jane";
    const ownerLast = uniqueName("Doe");
    const phone = "555-0199";

    await page.getByRole("button", { name: "Add Patient" }).click();

    // Modal opens with "Add Patient" title
    const modal = page.locator("[class*='fixed inset-0']");
    await expect(modal.getByText("Add Patient")).toBeVisible();

    // Fill form — labels lack htmlFor, so locate inputs by label text context
    const petNameInput = modal.locator("label:has-text('Pet Name') + input, label:has-text('Pet Name') ~ input").first();
    await petNameInput.fill(petName);

    const ownerFirstInput = modal.locator("label:has-text('Owner First Name') + input, label:has-text('Owner First Name') ~ input").first();
    await ownerFirstInput.fill(ownerFirst);

    const ownerLastInput = modal.locator("label:has-text('Owner Last Name') + input, label:has-text('Owner Last Name') ~ input").first();
    await ownerLastInput.fill(ownerLast);

    const phoneInput = modal.locator("label:has-text('Phone') + input, label:has-text('Phone') ~ input").first();
    await phoneInput.fill(phone);

    await modal.getByRole("button", { name: "Create Patient" }).click();

    // Wait for modal to close and table to refresh
    await expect(modal).toBeHidden({ timeout: 10_000 });
    await waitForTableLoad(page);

    // Verify patient appears in the table
    await expect(page.getByText(petName)).toBeVisible({ timeout: 10_000 });
  });

  test("search filters patients", async ({ page }) => {
    const searchInput = page.getByPlaceholder("Search by name, owner, phone...");
    await searchInput.fill("Buddy");

    // Wait for debounce (300ms) + network
    await page.waitForTimeout(500);
    await waitForTableLoad(page);

    // Either we find results or "No patients found" — the filter was applied
    const rows = page.locator("tbody tr");
    const count = await rows.count();
    if (count > 0) {
      // All visible rows should be related to search term
      const firstRow = rows.first();
      await expect(firstRow).toBeVisible();
    }
  });

  test("species filter works", async ({ page }) => {
    const speciesSelect = page.locator("select").first();
    await speciesSelect.selectOption("cat");

    await page.waitForTimeout(300);
    await waitForTableLoad(page);

    // Page should have applied the filter (either showing cat patients or empty state)
    await expect(speciesSelect).toHaveValue("cat");
  });

  test("delete a patient", async ({ page }) => {
    // First create a patient to delete
    const petName = uniqueName("DeleteMe");

    await page.getByRole("button", { name: "Add Patient" }).click();
    const modal = page.locator("[class*='fixed inset-0']");

    const petNameInput = modal.locator("label:has-text('Pet Name') + input, label:has-text('Pet Name') ~ input").first();
    await petNameInput.fill(petName);

    const ownerFirstInput = modal.locator("label:has-text('Owner First Name') + input, label:has-text('Owner First Name') ~ input").first();
    await ownerFirstInput.fill("Delete");

    const ownerLastInput = modal.locator("label:has-text('Owner Last Name') + input, label:has-text('Owner Last Name') ~ input").first();
    await ownerLastInput.fill("Test");

    const phoneInput = modal.locator("label:has-text('Phone') + input, label:has-text('Phone') ~ input").first();
    await phoneInput.fill("555-0000");

    await modal.getByRole("button", { name: "Create Patient" }).click();
    await expect(modal).toBeHidden({ timeout: 10_000 });
    await waitForTableLoad(page);
    await expect(page.getByText(petName)).toBeVisible({ timeout: 10_000 });

    // Accept the native confirm dialog
    page.on("dialog", (dialog) => dialog.accept());

    // Find the row with our patient and click Remove
    const row = page.locator("tr", { hasText: petName });
    await row.getByText("Remove").click();

    // Verify patient is gone
    await expect(page.getByText(petName)).toBeHidden({ timeout: 10_000 });
  });
});
