/**
 * Patients API client.
 */

import { env } from "@/lib/env";
import type {
  Patient,
  PatientCreate,
  PatientListItem,
  PatientUpdate,
  PatientsResponse,
} from "@/types/patient";

const API_BASE_URL = env.apiUrl;

export async function getPatients(
  page: number = 1,
  limit: number = 20,
  search?: string,
  species?: string,
): Promise<PatientsResponse> {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  });
  if (search) params.set("search", search);
  if (species) params.set("species", species);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/patients/?${params}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch patients: ${response.statusText}`);
  }

  return response.json();
}

export async function getPatient(id: string): Promise<Patient> {
  const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch patient: ${response.statusText}`);
  }

  return response.json();
}

export async function createPatient(data: PatientCreate): Promise<Patient> {
  const response = await fetch(`${API_BASE_URL}/api/v1/patients/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create patient: ${response.statusText}`);
  }

  return response.json();
}

export async function updatePatient(
  id: string,
  data: PatientUpdate,
): Promise<Patient> {
  const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update patient: ${response.statusText}`);
  }

  return response.json();
}

export async function deletePatient(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to delete patient: ${response.statusText}`);
  }
}

export async function searchPatients(
  query: string,
  limit: number = 10,
): Promise<PatientListItem[]> {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/patients/search?${params}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to search patients: ${response.statusText}`);
  }

  return response.json();
}
