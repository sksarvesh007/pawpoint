import { test, expect } from "@playwright/test";
import { STRONG_PASSWORD, getTestEnv } from "./helpers/test-data";

test.describe("Login page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("renders login form", async ({ page }) => {
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
    await expect(page.getByRole("button", { name: "Log in" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign up" })).toBeVisible();
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.getByLabel("Email").fill("fake@nobody.test");
    await page.getByLabel("Password").fill("WrongPass123!");
    await page.getByRole("button", { name: "Log in" }).click();

    const alert = page.locator('[role="alert"][aria-live="polite"]');
    await expect(alert).toContainText("Invalid email or password");
  });

  test("successful login redirects to dashboard", async ({ page }) => {
    const { email, password } = getTestEnv();
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(password);
    await page.getByRole("button", { name: "Log in" }).click();

    await page.waitForURL(/\/dashboard/, { timeout: 15_000 });
    expect(page.url()).toContain("/dashboard");
  });

  test("navigate to signup via link", async ({ page }) => {
    await page.getByRole("link", { name: "Sign up" }).click();
    await page.waitForURL(/\/signup/);
    expect(page.url()).toContain("/signup");
  });
});

test.describe("Signup page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/signup");
  });

  test("renders signup form", async ({ page }) => {
    await expect(page.getByLabel("Clinic Name")).toBeVisible();
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Confirm Password")).toBeVisible();
    await expect(page.getByRole("button", { name: "Create account" })).toBeVisible();
  });

  test("shows error for short password", async ({ page }) => {
    await page.getByLabel("Clinic Name").fill("Test Clinic");
    await page.getByLabel("Email").fill("short@test.com");
    await page.getByLabel("Password", { exact: true }).fill("Ab1!");
    await page.getByLabel("Confirm Password").fill("Ab1!");
    await page.getByRole("button", { name: "Create account" }).click();

    const alert = page.locator('[role="alert"][aria-live="polite"]');
    await expect(alert).toContainText("at least 8 characters");
  });

  test("shows error for missing uppercase", async ({ page }) => {
    await page.getByLabel("Clinic Name").fill("Test Clinic");
    await page.getByLabel("Email").fill("noup@test.com");
    await page.getByLabel("Password", { exact: true }).fill("lowercase1!");
    await page.getByLabel("Confirm Password").fill("lowercase1!");
    await page.getByRole("button", { name: "Create account" }).click();

    const alert = page.locator('[role="alert"][aria-live="polite"]');
    await expect(alert).toContainText("uppercase");
  });

  test("shows error for password mismatch", async ({ page }) => {
    await page.getByLabel("Clinic Name").fill("Test Clinic");
    await page.getByLabel("Email").fill("mismatch@test.com");
    await page.getByLabel("Password", { exact: true }).fill(STRONG_PASSWORD);
    await page.getByLabel("Confirm Password").fill("DifferentPass1!");
    await page.getByRole("button", { name: "Create account" }).click();

    const alert = page.locator('[role="alert"][aria-live="polite"]');
    await expect(alert).toContainText("do not match");
  });

  test("navigate to login via link", async ({ page }) => {
    await page.getByRole("link", { name: "Log in" }).click();
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain("/login");
  });
});

test.describe("Logout", () => {
  test("logout redirects to home", async ({ page }) => {
    // First log in
    const { email, password } = getTestEnv();
    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(password);
    await page.getByRole("button", { name: "Log in" }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 15_000 });

    // Then log out
    await page.getByText("Log Out").click();
    await page.waitForURL("/", { timeout: 10_000 });
    expect(page.url()).toMatch(/\/$/);
  });
});
