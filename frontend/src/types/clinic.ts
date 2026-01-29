/**
 * Clinic-related types for chatbot settings and configuration
 */

export interface ClinicInfo {
  id: string;
  name: string;
  email: string;
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

export interface ChatbotSettings {
  chatbot_persona: "professional" | "friendly" | "empathetic" | "warm";
  greeting_message: string;
  voice_enabled: boolean;
  emergency_handling?: EmergencyHandlingSettings;
  appointment_preferences?: AppointmentPreferences;
}

export interface ChatbotSettingsResponse {
  chatbot_persona: string;
  greeting_message: string;
  voice_enabled: boolean;
  emergency_handling: EmergencyHandlingSettings;
  appointment_preferences: AppointmentPreferences;
  clinic_name: string;
}

export interface UpdateChatbotSettingsRequest {
  chatbot_persona: "professional" | "friendly" | "empathetic" | "warm";
  greeting_message: string;
  emergency_handling?: EmergencyHandlingSettings;
  appointment_preferences?: AppointmentPreferences;
}
