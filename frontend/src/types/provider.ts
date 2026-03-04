/**
 * Provider types matching backend schemas.
 */

export interface Provider {
  id: string;
  clinic_id: string;
  first_name: string;
  last_name: string;
  title: string | null;
  email: string | null;
  phone: string | null;
  provider_type: string;
  license_number: string | null;
  specialties: string[] | null;
  bio: string | null;
  is_active: boolean;
  accepts_appointments: boolean;
  default_appointment_duration_min: number;
  availability: Record<string, unknown> | null;
  color: string | null;
  photo_url: string | null;
  full_name: string;
  display_name: string;
  pims_id: string | null;
  sync_status: string;
  created_at: string;
  updated_at: string;
}

export interface ProviderCreate {
  first_name: string;
  last_name: string;
  title?: string;
  email?: string;
  phone?: string;
  provider_type?: string;
  license_number?: string;
  specialties?: string[];
  bio?: string;
  default_appointment_duration_min?: number;
  availability?: Record<string, unknown>;
}
