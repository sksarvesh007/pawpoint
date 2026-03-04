import { test as setup } from "@playwright/test";
import { getTestEnv } from "./helpers/test-data";
import fs from "fs";
import path from "path";

const AUTH_DIR = path.join(__dirname, ".auth");
const STORAGE_STATE = path.join(AUTH_DIR, "user.json");
const TEST_ENV_FILE = path.join(AUTH_DIR, "test-env.json");

setup("authenticate", async ({ page }) => {
  fs.mkdirSync(AUTH_DIR, { recursive: true });

  const { email, password, clinicName } = getTestEnv();

  // Register a fresh clinic via the API
  const res = await page.request.post("http://localhost:8000/api/v1/auth/register", {
    data: {
      clinic_name: clinicName,
      email,
      password,
    },
  });

  if (!res.ok()) {
    // Registration failed — likely the user already exists. Try logging in.
    const loginRes = await page.request.post("http://localhost:8000/api/v1/auth/login", {
      data: { email, password },
    });
    if (!loginRes.ok()) {
      const regBody = await res.text();
      throw new Error(
        `Registration failed (${res.status()}): ${regBody}\n` +
        `Login fallback also failed (${loginRes.status()}): ${await loginRes.text()}`
      );
    }
  }

  // Navigate to the frontend to associate cookies with the frontend domain
  await page.goto("/dashboard");
  await page.waitForURL(/\/dashboard/, { timeout: 15_000 });

  // Save storage state for authenticated tests
  await page.context().storageState({ path: STORAGE_STATE });

  // Save test credentials for use in tests
  fs.writeFileSync(TEST_ENV_FILE, JSON.stringify({ email, password, clinicName }));
});
