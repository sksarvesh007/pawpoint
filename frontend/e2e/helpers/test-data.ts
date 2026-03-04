import fs from "fs";
import path from "path";

export const STRONG_PASSWORD = "TestPass123!";

interface TestEnv {
  email: string;
  password: string;
  clinicName: string;
}

let cachedEnv: TestEnv | null = null;

export function getTestEnv(): TestEnv {
  if (cachedEnv) return cachedEnv;

  const envFile = path.join(__dirname, "..", ".auth", "test-env.json");
  if (fs.existsSync(envFile)) {
    cachedEnv = JSON.parse(fs.readFileSync(envFile, "utf-8"));
    return cachedEnv!;
  }

  // Generate fresh credentials for setup
  const id = Date.now().toString(36);
  cachedEnv = {
    email: `e2e-${id}@test.pawpoint.dev`,
    password: STRONG_PASSWORD,
    clinicName: `E2E Clinic ${id}`,
  };
  return cachedEnv;
}

export function uniqueName(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}`;
}
