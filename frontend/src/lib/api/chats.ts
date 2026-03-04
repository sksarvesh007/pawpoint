/**
 * Chat logs API client.
 */

import { env } from "@/lib/env";
import type { ChatLogsResponse, ChatLogDetail, EnhancedChatAnalytics } from "@/types/analytics";

const API_BASE_URL = env.apiUrl;

/**
 * Fetch paginated chat logs.
 */
export async function getChatLogs(
  page: number = 1,
  limit: number = 20,
): Promise<ChatLogsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/chats?page=${page}&limit=${limit}`,
    {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch chat logs: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch a single chat log with all messages.
 */
export async function getChatLogDetail(chatId: string): Promise<ChatLogDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chats/${chatId}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch chat detail: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch enhanced chat analytics with sentiment, resolution, and topic data.
 */
export async function getChatAnalytics(
  days: number = 30,
): Promise<EnhancedChatAnalytics> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analytics/chats?days=${days}`,
    {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch chat analytics: ${response.statusText}`);
  }

  return response.json();
}
