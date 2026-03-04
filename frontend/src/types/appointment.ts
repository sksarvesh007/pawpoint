/**
 * Appointment types matching backend schemas.
 */

export interface Appointment {
  id: string;
  clinic_id: string;
  patient_id: string | null;
  provider_id: string | null;
  call_log_id: string | null;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  appointment_type: string;
  status: string;
  source: string;
  reason: string | null;
  notes: string | null;
  client_notes: string | null;
  cancellation_reason: string | null;
  cancelled_at: string | null;
  patient_name: string | null;
  provider_name: string | null;
  pims_id: string | null;
  sync_status: string;
  created_at: string;
  updated_at: string;
}

export interface AppointmentListItem {
  id: string;
  start_time: string;
  end_time: string;
  appointment_type: string;
  status: string;
  source: string;
  reason: string | null;
  patient_name: string | null;
  provider_name: string | null;
}

export interface AppointmentCreate {
  start_time: string;
  end_time: string;
  appointment_type?: string;
  patient_id?: string;
  provider_id?: string;
  reason?: string;
  notes?: string;
}

export interface AppointmentsResponse {
  items: AppointmentListItem[];
  total: number;
  page: number;
  limit: number;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
}
