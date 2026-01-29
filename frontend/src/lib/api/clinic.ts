/**
 * API client functions for clinic operations
 */

import { env } from "@/lib/env";
import type {
  ChatbotSettingsResponse,
  UpdateChatbotSettingsRequest,
  ClinicInfo,
} from "@/types/clinic";

/**
 * Get basic clinic info for authenticated user
 */
export async function getClinicInfo(): Promise<ClinicInfo> {
  const response = await fetch(`${env.apiUrl}/api/v1/clinics/me`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch clinic info");
  }

  return response.json();
}

/**
 * Get current chatbot settings for authenticated clinic
 */
export async function getChatbotSettings(): Promise<ChatbotSettingsResponse> {
  const response = await fetch(
    `${env.apiUrl}/api/v1/clinics/chatbot-settings`,
    {
      method: "GET",
      credentials: "include", // Include httpOnly cookies
    }
  );

  if (!response.ok) {
    let errorMessage = "Failed to fetch chatbot settings";

    if (response.status === 401) {
      errorMessage = "Please log in to continue";
    } else if (response.status === 404) {
      errorMessage = "Clinic not found";
    }

    try {
      const error = await response.json();
      if (error.detail) {
        errorMessage = error.detail;
      }
    } catch {
      // Response might not be JSON, use default message
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Update chatbot settings for authenticated clinic
 */
export async function updateChatbotSettings(
  settings: UpdateChatbotSettingsRequest
): Promise<ChatbotSettingsResponse> {
  const response = await fetch(
    `${env.apiUrl}/api/v1/clinics/chatbot-settings`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // Include httpOnly cookies
      body: JSON.stringify(settings),
    }
  );

  if (!response.ok) {
    let errorMessage = "Failed to update chatbot settings";

    if (response.status === 401) {
      errorMessage = "Please log in to continue";
    } else if (response.status === 403) {
      errorMessage = "You don't have permission to update these settings";
    } else if (response.status === 422 || response.status === 400) {
      errorMessage = "Please check your input and try again";
    } else if (response.status === 429) {
      errorMessage = "Too many requests. Please try again in a minute";
    }

    try {
      const error = await response.json();
      if (error.detail) {
        errorMessage =
          typeof error.detail === "string"
            ? error.detail
            : "Validation error. Please check your input.";
      }
    } catch {
      // Response might not be JSON, use default message
    }

    throw new Error(errorMessage);
  }

  return response.json();
}
