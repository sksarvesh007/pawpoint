/**
 * Appointments API client.
 */

import { env } from "@/lib/env";
import type {
  Appointment,
  AppointmentCreate,
  AppointmentListItem,
  AppointmentsResponse,
  TimeSlot,
} from "@/types/appointment";

const API_BASE_URL = env.apiUrl;

export async function getAppointments(params: {
  page?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  status?: string;
  provider_id?: string;
}): Promise<AppointmentsResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.limit) searchParams.set("limit", String(params.limit));
  if (params.start_date) searchParams.set("start_date", params.start_date);
  if (params.end_date) searchParams.set("end_date", params.end_date);
  if (params.status) searchParams.set("status", params.status);
  if (params.provider_id)
    searchParams.set("provider_id", params.provider_id);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/appointments/?${searchParams}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch appointments: ${response.statusText}`);
  }

  return response.json();
}

export async function getAppointment(id: string): Promise<Appointment> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/appointments/${id}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch appointment: ${response.statusText}`);
  }

  return response.json();
}

export async function createAppointment(
  data: AppointmentCreate,
): Promise<Appointment> {
  const response = await fetch(`${API_BASE_URL}/api/v1/appointments/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create appointment: ${response.statusText}`);
  }

  return response.json();
}

export async function updateAppointmentStatus(
  id: string,
  status: string,
  cancellation_reason?: string,
): Promise<Appointment> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/appointments/${id}/status`,
    {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, cancellation_reason }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to update appointment status: ${response.statusText}`,
    );
  }

  return response.json();
}

export async function getAvailableSlots(
  providerId: string,
  date: string,
  duration?: number,
): Promise<TimeSlot[]> {
  const params = new URLSearchParams({
    provider_id: providerId,
    date: date,
  });
  if (duration) params.set("duration", String(duration));

  const response = await fetch(
    `${API_BASE_URL}/api/v1/appointments/available-slots?${params}`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch available slots: ${response.statusText}`,
    );
  }

  return response.json();
}

export async function getTodayAppointments(): Promise<AppointmentListItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/appointments/today`,
    {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch today's appointments: ${response.statusText}`,
    );
  }

  return response.json();
}
