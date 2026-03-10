/**
 * API client for user preferences endpoints.
 */

import { env } from "@/lib/env";

export interface WidgetConfig {
  id: string;
  visible: boolean;
}

export interface DashboardLayoutResponse {
  widgets: WidgetConfig[];
}

const API_BASE_URL = env.apiUrl;

export async function getDashboardLayout(): Promise<DashboardLayoutResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/preferences/dashboard-layout`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to load widget layout: ${response.statusText}`);
  }

  return response.json();
}

export async function saveDashboardLayout(
  widgets: WidgetConfig[]
): Promise<DashboardLayoutResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/preferences/dashboard-layout`,
    {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ widgets }),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to save widget layout: ${response.statusText}`);
  }

  return response.json();
}
