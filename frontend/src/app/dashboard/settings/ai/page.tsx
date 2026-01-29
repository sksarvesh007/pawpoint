/**
 * AI Assistant Settings page within dashboard.
 * Allows editing chatbot configuration.
 */

"use client";

import { useState, useEffect } from "react";
import { Settings } from "lucide-react";
import { updateChatbotSettings, getChatbotSettings } from "@/lib/api/clinic";
import type { UpdateChatbotSettingsRequest } from "@/types/clinic";

type ChatbotPersona = "professional" | "friendly" | "empathetic" | "warm";

export default function AISettingsPage() {
  // Form state
  const [chatbotPersona, setChatbotPersona] =
    useState<ChatbotPersona>("professional");
  const [greetingMessage, setGreetingMessage] = useState(
    "Thank you for calling our clinic. How can I help you and your pet today?"
  );
  const [transferImmediately, setTransferImmediately] = useState(true);
  const [emergencyKeywords, setEmergencyKeywords] = useState<string[]>([
    "emergency",
    "dying",
    "bleeding",
    "poison",
    "hit by car",
  ]);
  const [newKeyword, setNewKeyword] = useState("");
  const [emergencyMessage, setEmergencyMessage] = useState(
    "I'm transferring you to our emergency line right away."
  );
  const [allowBooking, setAllowBooking] = useState(true);
  const [allowCancellation, setAllowCancellation] = useState(false);
  const [allowRescheduling, setAllowRescheduling] = useState(true);
  const [bookingBufferHours, setBookingBufferHours] = useState(2);

  // UI state
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [emergencyExpanded, setEmergencyExpanded] = useState(true);
  const [appointmentExpanded, setAppointmentExpanded] = useState(true);

  const personas: Array<{
    value: ChatbotPersona;
    label: string;
    description: string;
  }> = [
    {
      value: "professional",
      label: "Professional",
      description: "Formal, efficient, and clinical",
    },
    {
      value: "friendly",
      label: "Friendly",
      description: "Warm, conversational, and approachable",
    },
    {
      value: "empathetic",
      label: "Empathetic",
      description: "Caring, understanding, and supportive",
    },
    {
      value: "warm",
      label: "Warm",
      description: "Gentle, comforting, and compassionate",
    },
  ];

  // Load current settings
  useEffect(() => {
    getChatbotSettings()
      .then((settings) => {
        if (settings.chatbot_persona) {
          setChatbotPersona(settings.chatbot_persona as ChatbotPersona);
        }
        if (settings.greeting_message) {
          setGreetingMessage(settings.greeting_message);
        }
        if (settings.emergency_handling) {
          setTransferImmediately(
            settings.emergency_handling.transfer_immediately ?? true
          );
          setEmergencyKeywords(settings.emergency_handling.keywords ?? []);
          setEmergencyMessage(
            settings.emergency_handling.emergency_message ??
              "I'm transferring you to our emergency line right away."
          );
        }
        if (settings.appointment_preferences) {
          setAllowBooking(settings.appointment_preferences.allow_booking ?? true);
          setAllowCancellation(
            settings.appointment_preferences.allow_cancellation ?? false
          );
          setAllowRescheduling(
            settings.appointment_preferences.allow_rescheduling ?? true
          );
          setBookingBufferHours(
            settings.appointment_preferences.booking_buffer_hours ?? 2
          );
        }
      })
      .catch((err) => {
        console.error("Failed to load settings:", err);
      })
      .finally(() => setInitialLoading(false));
  }, []);

  const handleAddKeyword = () => {
    if (newKeyword.trim() && emergencyKeywords.length < 20) {
      setEmergencyKeywords([...emergencyKeywords, newKeyword.trim()]);
      setNewKeyword("");
    }
  };

  const handleRemoveKeyword = (index: number) => {
    setEmergencyKeywords(emergencyKeywords.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Client-side validation
    if (greetingMessage.trim().length < 10) {
      setError("Greeting message must be at least 10 characters");
      return;
    }

    if (greetingMessage.length > 500) {
      setError("Greeting message must be less than 500 characters");
      return;
    }

    if (emergencyKeywords.length === 0) {
      setError("At least one emergency keyword is required");
      return;
    }

    if (bookingBufferHours < 0 || bookingBufferHours > 72) {
      setError("Booking buffer hours must be between 0 and 72");
      return;
    }

    setLoading(true);

    try {
      const settings: UpdateChatbotSettingsRequest = {
        chatbot_persona: chatbotPersona,
        greeting_message: greetingMessage.trim(),
        emergency_handling: {
          transfer_immediately: transferImmediately,
          keywords: emergencyKeywords,
          emergency_message: emergencyMessage.trim() || undefined,
        },
        appointment_preferences: {
          allow_booking: allowBooking,
          allow_cancellation: allowCancellation,
          allow_rescheduling: allowRescheduling,
          booking_buffer_hours: bookingBufferHours,
        },
      };

      await updateChatbotSettings(settings);

      setSuccess("Settings saved successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="max-w-4xl">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-zinc-200 rounded w-64" />
          <div className="h-96 bg-zinc-200 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <Settings className="w-8 h-8 text-teal-600" />
          AI Assistant Settings
        </h1>
        <p className="text-zinc-600 mt-1">
          Customize how your AI chatbot interacts with clients
        </p>
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <div
              role="alert"
              aria-live="polite"
              className="rounded-lg bg-red-50 p-3 text-sm text-red-600"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              role="alert"
              aria-live="polite"
              className="rounded-lg bg-green-50 p-3 text-sm text-green-600"
            >
              {success}
            </div>
          )}

          {/* Chatbot Persona */}
          <fieldset>
            <legend className="block text-sm font-medium text-zinc-700 mb-3">
              Chatbot Persona
            </legend>
            <div className="space-y-3">
              {personas.map((persona) => (
                <label
                  key={persona.value}
                  className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    chatbotPersona === persona.value
                      ? "border-teal-500 bg-teal-50"
                      : "border-zinc-200 hover:border-zinc-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="chatbotPersona"
                    value={persona.value}
                    checked={chatbotPersona === persona.value}
                    onChange={(e) =>
                      setChatbotPersona(e.target.value as ChatbotPersona)
                    }
                    className="mt-1 h-4 w-4 text-teal-600 focus:ring-teal-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-zinc-900">
                      {persona.label}
                    </div>
                    <div className="text-sm text-zinc-600">
                      {persona.description}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Greeting Message */}
          <div>
            <label
              htmlFor="greetingMessage"
              className="block text-sm font-medium text-zinc-700"
            >
              Greeting Message
            </label>
            <textarea
              id="greetingMessage"
              name="greetingMessage"
              value={greetingMessage}
              onChange={(e) => setGreetingMessage(e.target.value)}
              required
              rows={3}
              maxLength={500}
              className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
              placeholder="Thank you for calling our clinic. How can I help you and your pet today?"
            />
            <div className="mt-1 flex justify-between text-xs text-zinc-500">
              <span>This will be the first thing clients hear</span>
              <span>{greetingMessage.length}/500</span>
            </div>
          </div>

          {/* Emergency Handling */}
          <div className="border border-zinc-200 rounded-lg">
            <button
              type="button"
              onClick={() => setEmergencyExpanded(!emergencyExpanded)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-50 transition-colors"
            >
              <span className="text-sm font-medium text-zinc-700">
                Emergency Handling
              </span>
              <svg
                className={`w-5 h-5 text-zinc-500 transition-transform ${
                  emergencyExpanded ? "rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {emergencyExpanded && (
              <div className="p-4 pt-0 space-y-4">
                {/* Transfer Immediately Toggle */}
                <label className="flex items-center justify-between">
                  <span className="text-sm text-zinc-700">
                    Transfer emergencies immediately
                  </span>
                  <input
                    type="checkbox"
                    checked={transferImmediately}
                    onChange={(e) => setTransferImmediately(e.target.checked)}
                    className="h-4 w-4 rounded text-teal-600 focus:ring-teal-500"
                  />
                </label>

                {/* Emergency Keywords */}
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-2">
                    Emergency Keywords
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {emergencyKeywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-red-100 text-red-800"
                      >
                        {keyword}
                        <button
                          type="button"
                          onClick={() => handleRemoveKeyword(index)}
                          className="hover:text-red-900"
                          aria-label={`Remove ${keyword}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  {emergencyKeywords.length < 20 && (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            handleAddKeyword();
                          }
                        }}
                        placeholder="Add keyword"
                        maxLength={50}
                        className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-900 placeholder-zinc-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
                      />
                      <button
                        type="button"
                        onClick={handleAddKeyword}
                        className="px-4 py-2 rounded-lg bg-zinc-100 text-sm font-medium text-zinc-700 hover:bg-zinc-200 transition-colors"
                      >
                        Add
                      </button>
                    </div>
                  )}
                  <p className="mt-1 text-xs text-zinc-500">
                    {emergencyKeywords.length}/20 keywords
                  </p>
                </div>

                {/* Emergency Message */}
                <div>
                  <label
                    htmlFor="emergencyMessage"
                    className="block text-sm font-medium text-zinc-700"
                  >
                    Emergency Transfer Message (Optional)
                  </label>
                  <textarea
                    id="emergencyMessage"
                    value={emergencyMessage}
                    onChange={(e) => setEmergencyMessage(e.target.value)}
                    rows={2}
                    maxLength={200}
                    className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
                    placeholder="Message played when transferring emergency calls"
                  />
                  <div className="mt-1 text-xs text-zinc-500 text-right">
                    {emergencyMessage.length}/200
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Appointment Preferences */}
          <div className="border border-zinc-200 rounded-lg">
            <button
              type="button"
              onClick={() => setAppointmentExpanded(!appointmentExpanded)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-50 transition-colors"
            >
              <span className="text-sm font-medium text-zinc-700">
                Appointment Preferences
              </span>
              <svg
                className={`w-5 h-5 text-zinc-500 transition-transform ${
                  appointmentExpanded ? "rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {appointmentExpanded && (
              <div className="p-4 pt-0 space-y-4">
                {/* Allow Booking */}
                <label className="flex items-center justify-between">
                  <span className="text-sm text-zinc-700">
                    Allow booking appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowBooking}
                    onChange={(e) => setAllowBooking(e.target.checked)}
                    className="h-4 w-4 rounded text-teal-600 focus:ring-teal-500"
                  />
                </label>

                {/* Allow Cancellation */}
                <label className="flex items-center justify-between">
                  <span className="text-sm text-zinc-700">
                    Allow canceling appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowCancellation}
                    onChange={(e) => setAllowCancellation(e.target.checked)}
                    className="h-4 w-4 rounded text-teal-600 focus:ring-teal-500"
                  />
                </label>

                {/* Allow Rescheduling */}
                <label className="flex items-center justify-between">
                  <span className="text-sm text-zinc-700">
                    Allow rescheduling appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowRescheduling}
                    onChange={(e) => setAllowRescheduling(e.target.checked)}
                    className="h-4 w-4 rounded text-teal-600 focus:ring-teal-500"
                  />
                </label>

                {/* Booking Buffer Hours */}
                <div>
                  <label
                    htmlFor="bookingBufferHours"
                    className="block text-sm font-medium text-zinc-700"
                  >
                    Booking Buffer Hours
                  </label>
                  <input
                    type="number"
                    id="bookingBufferHours"
                    value={bookingBufferHours}
                    onChange={(e) =>
                      setBookingBufferHours(parseInt(e.target.value) || 0)
                    }
                    min={0}
                    max={72}
                    className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
                  />
                  <p className="mt-1 text-xs text-zinc-500">
                    Minimum hours in advance required for booking
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 rounded-lg bg-teal-600 py-3 text-sm font-medium text-white hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
            >
              {loading ? "Saving..." : "Save Changes"}
            </button>
            <button
              type="button"
              onClick={() => window.location.reload()}
              disabled={loading}
              className="px-6 rounded-lg border border-zinc-300 py-3 text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors"
            >
              Reset
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
