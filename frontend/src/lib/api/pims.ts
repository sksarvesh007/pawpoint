/**
 * PIMS integration API client.
 */

import { env } from "@/lib/env";
import type {
  PIMSConnectionStatus,
  PIMSSyncLog,
  PIMSSyncTriggerResponse,
  PIMSTestConnectionResponse,
} from "@/types/pims";

const API_BASE_URL = env.apiUrl;

export async function getPIMSStatus(): Promise<PIMSConnectionStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pims/status`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch PIMS status: ${response.statusText}`);
  }

  return response.json();
}

export async function savePIMSCredentials(data: {
  pims_type: string;
  credentials: Record<string, string>;
}): Promise<PIMSConnectionStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pims/credentials`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to save PIMS credentials: ${response.statusText}`);
  }

  return response.json();
}

export async function testPIMSConnection(): Promise<PIMSTestConnectionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/pims/test-connection`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to test PIMS connection: ${response.statusText}`,
    );
  }

  return response.json();
}

export async function disconnectPIMS(): Promise<PIMSConnectionStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pims/disconnect`, {
    method: "DELETE",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Failed to disconnect PIMS: ${response.statusText}`);
  }

  return response.json();
}

export async function triggerSync(
  entity: "patients" | "appointments" | "providers",
): Promise<PIMSSyncTriggerResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/pims/sync/${entity}`,
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to trigger sync: ${response.statusText}`);
  }

  return response.json();
}

export async function getSyncLogs(
  limit: number = 20,
): Promise<PIMSSyncLog[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/pims/sync-logs?limit=${limit}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch sync logs: ${response.statusText}`);
  }

  return response.json();
}
