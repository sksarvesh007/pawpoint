/**
 * Providers API client.
 */

import { env } from "@/lib/env";
import type { Provider, ProviderCreate } from "@/types/provider";

const API_BASE_URL = env.apiUrl;

export async function getProviders(
  activeOnly: boolean = true,
): Promise<Provider[]> {
  const params = new URLSearchParams({
    active_only: String(activeOnly),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/providers/?${params}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch providers: ${response.statusText}`);
  }

  return response.json();
}

export async function createProvider(data: ProviderCreate): Promise<Provider> {
  const response = await fetch(`${API_BASE_URL}/api/v1/providers/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create provider: ${response.statusText}`);
  }

  return response.json();
}

export async function updateProvider(
  id: string,
  data: Partial<Provider>,
): Promise<Provider> {
  const response = await fetch(`${API_BASE_URL}/api/v1/providers/${id}`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update provider: ${response.statusText}`);
  }

  return response.json();
}

export async function deleteProvider(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/providers/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to delete provider: ${response.statusText}`);
  }
}
