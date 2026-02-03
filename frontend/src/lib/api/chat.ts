/**
 * API client functions for public chatbot
 */

import { getApiUrl } from "@/lib/env";
import type {
  ChatRequest,
  ChatResponse,
  ClinicPublicInfo,
} from "@/types/chat";

/**
 * Get public clinic info by slug (no authentication required)
 */
export async function getClinicPublicInfo(
  clinicSlug: string
): Promise<ClinicPublicInfo> {
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/v1/${clinicSlug}/info`, {
    method: "GET",
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Clinic not found");
    }
    throw new Error("Failed to fetch clinic info");
  }

  return response.json();
}

/**
 * Send a chat message to the clinic's chatbot
 */
export async function sendChatMessage(
  clinicSlug: string,
  request: ChatRequest
): Promise<ChatResponse> {
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/v1/${clinicSlug}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Clinic not found");
    }
    if (response.status === 400) {
      const error = await response.json();
      throw new Error(error.detail || "Invalid request");
    }
    if (response.status === 429) {
      throw new Error("Too many requests. Please try again in a minute");
    }
    throw new Error("Failed to send message");
  }

  return response.json();
}
