/**
 * Application-wide constants for PawPoint Frontend
 */

/**
 * Fallback values for clinic information when real data is not available.
 * Used in chatbot and other components that display clinic contact details.
 */
export const FALLBACK_CLINIC_INFO = {
  phone: "(555) 123-4567",
  email: "contact@clinic.com",
  address: "123 Main Street",
  city: "City",
  state: "State",
  zipCode: "12345",
} as const;

/**
 * Default business hours shown when clinic hours are not available
 */
export const DEFAULT_BUSINESS_HOURS = {
  weekdays: "8:00 AM - 6:00 PM",
  saturday: "9:00 AM - 4:00 PM",
  sunday: "Closed",
} as const;

/**
 * API endpoints - centralized path definitions
 */
export const API_ENDPOINTS = {
  chatStream: (clinicSlug: string) => `/api/v1/${clinicSlug}/chat/stream`,
  clinicInfo: (clinicSlug: string) => `/api/v1/${clinicSlug}/info`,
  analyticsStream: "/api/v1/analytics/stream",
} as const;
