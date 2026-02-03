/**
 * API client functions for authentication operations
 */

import { getApiUrl } from "@/lib/env";

/**
 * Logout the current user
 */
export async function logout(): Promise<void> {
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include", // Include httpOnly cookies
  });

  if (!response.ok) {
    throw new Error("Failed to logout");
  }
}
