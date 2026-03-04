import type { Page } from "@playwright/test";

/**
 * Wait for table loading skeletons (animate-pulse) to disappear,
 * indicating data has loaded.
 */
export async function waitForTableLoad(page: Page, timeout = 15_000): Promise<void> {
  await page.locator(".animate-pulse").first().waitFor({ state: "hidden", timeout }).catch(() => {
    // If no skeleton was ever shown (fast load), that's fine
  });
}
