/**
 * Analytics types for dashboard metrics.
 * These match the backend schemas in backend/app/schemas/analytics.py
 */

export interface CallAnalytics {
  total_calls: number;
  calls_today: number;
  inbound_calls: number;
  outbound_calls: number;
  ai_handled_percentage: number;
  average_duration_seconds: number;
  emergency_transfers: number;
  appointments_booked: number;
  average_confidence_score: number;
  calls_by_outcome: Record<string, number>;
  calls_by_hour: Array<{ hour: number; count: number }>;
  transfer_hours: number[]; // UTC hours when transfers occurred
}

export interface AppointmentAnalytics {
  total_appointments: number;
  appointments_this_week: number;
  bookings_via_ai: number;
  bookings_via_dashboard: number;
  no_show_rate: number;
  cancellation_rate: number;
  appointments_by_type: Record<string, number>;
  appointments_by_status: Record<string, number>;
}

export interface PatientAnalytics {
  total_active_patients: number;
  new_patients_this_month: number;
  patients_by_species: Record<string, number>;
  total_owners: number;
}

export interface PIMSSyncAnalytics {
  connection_status: string;
  last_sync_at: string | null;
  sync_success_rate: number;
  total_syncs_today: number;
  failed_syncs_today: number;
}

export interface SentimentData {
  positive_calls: number;
  neutral_calls: number;
  negative_calls: number;
  average_sentiment_score: number;
}

export interface CallLogSummary {
  id: string;
  started_at: string;
  caller_phone_number: string | null;
  duration_seconds: number | null;
  outcome: string;
  sentiment: string | null;
  ai_confidence_score: number | null;
  direction: string;
}

export interface ChatLogSummary {
  id: string;
  started_at: string;
  user_identifier: string;
  total_messages: number;
  intent: string | null;
  session_active: boolean;
  summary: string | null;
}

export interface ChatAnalytics {
  total_chats: number;
  chats_today: number;
  average_messages_per_chat: number;
  active_sessions: number;
  chats_by_intent: Record<string, number>;
  chats_by_hour: Array<{ hour: number; count: number }>;
}

export interface DashboardAnalytics {
  calls: CallAnalytics;
  appointments: AppointmentAnalytics;
  patients: PatientAnalytics;
  pims: PIMSSyncAnalytics;
  sentiment: SentimentData;
  recent_calls: CallLogSummary[];
  chats?: ChatAnalytics | null;
  recent_chats?: ChatLogSummary[] | null;
}

export interface CallLogsResponse {
  items: CallLogSummary[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ChatLogsResponse {
  items: ChatLogSummary[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface MessageDetail {
  id: string;
  role: string;
  content: string | null;
  created_at: string;
  agent_name: string | null;
}

export interface ChatLogDetail {
  id: string;
  started_at: string;
  ended_at: string | null;
  user_identifier: string;
  total_messages: number;
  intent: string | null;
  session_active: boolean;
  summary: string | null;
  messages: MessageDetail[];
}
