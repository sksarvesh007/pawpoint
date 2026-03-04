/**
 * API client for analytics endpoints.
 */

import { env } from "@/lib/env";
import type {
  CallLogsResponse,
  CallLogDetail,
  DashboardAnalytics,
  CallAnalytics,
} from "@/types/analytics";

const API_BASE_URL = env.apiUrl;

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analytics/dashboard`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard analytics: ${response.statusText}`);
  }

  return response.json();
}

export async function getCallAnalytics(days: number = 30): Promise<CallAnalytics> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analytics/calls?days=${days}`,
    {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch call analytics: ${response.statusText}`);
  }

  return response.json();
}

export async function getRecentCalls(
  page: number = 1,
  limit: number = 20
): Promise<CallLogsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/calls?page=${page}&limit=${limit}`,
    {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch call logs: ${response.statusText}`);
  }

  return response.json();
}

export async function getCallLogDetail(callId: string): Promise<CallLogDetail> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/calls/${callId}`,
    {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch call detail: ${response.statusText}`);
  }

  return response.json();
}
