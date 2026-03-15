// Tests demo page loads (does not require backend)
import { test, expect } from '@playwright/test'

test('demo page loads and has chatbot UI', async ({ page }) => {
  await page.goto('/demo')
  // Check that key UI elements exist
  await expect(page.locator('h1, h2').first()).toBeVisible()
})
