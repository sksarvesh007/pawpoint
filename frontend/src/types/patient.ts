/**
 * Patient types matching backend schemas.
 */

export interface Patient {
  id: string;
  clinic_id: string;
  name: string;
  species: string;
  breed: string | null;
  color: string | null;
  sex: string;
  date_of_birth: string | null;
  weight_kg: number | null;
  is_deceased: boolean;
  allergies: string | null;
  medical_notes: string | null;
  owner_first_name: string;
  owner_last_name: string;
  owner_phone: string;
  owner_phone_alt: string | null;
  owner_email: string | null;
  owner_address: string | null;
  microchip_id: string | null;
  photo_url: string | null;
  owner_full_name: string;
  pims_id: string | null;
  sync_status: string;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatientListItem {
  id: string;
  name: string;
  species: string;
  breed: string | null;
  owner_first_name: string;
  owner_last_name: string;
  owner_phone: string;
  owner_email: string | null;
  is_deceased: boolean;
  photo_url: string | null;
  created_at: string;
}

export interface PatientCreate {
  name: string;
  species?: string;
  owner_first_name: string;
  owner_last_name: string;
  owner_phone: string;
  breed?: string;
  color?: string;
  sex?: string;
  date_of_birth?: string;
  weight_kg?: number;
  owner_email?: string;
  allergies?: string;
  medical_notes?: string;
  microchip_id?: string;
  photo_url?: string;
}

export interface PatientUpdate {
  name?: string;
  species?: string;
  breed?: string;
  color?: string;
  sex?: string;
  date_of_birth?: string;
  weight_kg?: number;
  owner_first_name?: string;
  owner_last_name?: string;
  owner_phone?: string;
  owner_email?: string;
  allergies?: string;
  medical_notes?: string;
  microchip_id?: string;
  is_deceased?: boolean;
}

export interface PatientsResponse {
  items: PatientListItem[];
  total: number;
  page: number;
  limit: number;
}
