/**
 * Clinic-related types for chatbot settings and configuration
 */

export interface ClinicInfo {
  id: string;
  name: string;
  email: string;
  slug: string;
}

export interface EmergencyHandlingSettings {
  transfer_immediately: boolean;
  keywords: string[];
  emergency_message?: string;
}

export interface AppointmentPreferences {
  allow_booking: boolean;
  allow_cancellation: boolean;
  allow_rescheduling: boolean;
  booking_buffer_hours: number;
}

export interface CallFlowRules {
  transfer_failure_action: "retry" | "voicemail" | "take_message" | "callback_request";
  max_hold_seconds: 30 | 60 | 120;
  voicemail_enabled: boolean;
  callback_requests_enabled: boolean;
}

export interface ChatbotSettings {
  chatbot_persona: "professional" | "friendly" | "empathetic" | "warm";
  greeting_message: string;
  voice_enabled: boolean;
  emergency_handling?: EmergencyHandlingSettings;
  appointment_preferences?: AppointmentPreferences;
}

export interface ChatbotSettingsResponse {
  chatbot_name?: string;
  chatbot_persona: string;
  greeting_message: string;
  additional_context?: string;
  voice_enabled: boolean;
  emergency_handling: EmergencyHandlingSettings;
  appointment_preferences: AppointmentPreferences;
  call_flow_rules: CallFlowRules;
  clinic_name: string;
  // Contact information
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  business_hours?: Record<string, unknown>;
}

export interface UpdateChatbotSettingsRequest {
  // Contact Information
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  business_hours?: Record<string, unknown>;
  // Chatbot Settings
  chatbot_name?: string;
  chatbot_persona: "professional" | "friendly" | "empathetic" | "warm";
  greeting_message: string;
  additional_context?: string;
  emergency_handling?: EmergencyHandlingSettings;
  appointment_preferences?: AppointmentPreferences;
  call_flow_rules?: CallFlowRules;
}
