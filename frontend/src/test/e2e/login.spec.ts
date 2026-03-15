// Tests login page renders and has expected elements
// Does NOT require a running backend — just checks static UI
import { test, expect } from '@playwright/test'

test('login page has email and password fields', async ({ page }) => {
  await page.goto('/login')
  await expect(page.locator('input[type="email"]')).toBeVisible()
  await expect(page.locator('input[type="password"]')).toBeVisible()
  await expect(page.locator('button[type="submit"]')).toBeVisible()
})
