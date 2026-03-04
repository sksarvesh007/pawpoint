/**
 * Types for public chatbot API
 */

export interface ToolCallInfo {
  tool_name: string;
  status: "calling" | "done";
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
  toolCalls?: ToolCallInfo[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  user_identifier: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  agent_name: string;
  clinic_name: string;
  model_used?: string;
  tokens_used?: number;
}

export interface ClinicPublicInfo {
  clinic_name: string;
  chatbot_name?: string;
  greeting_message: string;
  chatbot_persona: "professional" | "friendly" | "empathetic" | "warm";
  voice_enabled: boolean;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  business_hours?: Record<string, unknown>;
}
