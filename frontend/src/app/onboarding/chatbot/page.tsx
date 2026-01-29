"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";
import { updateChatbotSettings } from "@/lib/api/clinic";
import type { UpdateChatbotSettingsRequest } from "@/types/clinic";

type ChatbotPersona = "professional" | "friendly" | "empathetic" | "warm";

export default function ChatbotOnboardingPage() {
  const router = useRouter();

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
  const [loading, setLoading] = useState(false);
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

  const handleAddKeyword = () => {
    const trimmed = newKeyword.trim();

    // Validate length
    if (trimmed.length < 2) {
      setError("Keywords must be at least 2 characters");
      return;
    }

    if (trimmed.length > 50) {
      setError("Keywords must be less than 50 characters");
      return;
    }

    // Validate characters (match backend validation)
    if (!/^[A-Za-z0-9\s\-]+$/.test(trimmed)) {
      setError(
        "Keywords can only contain letters, numbers, spaces, and hyphens"
      );
      return;
    }

    // Check for duplicates
    if (emergencyKeywords.some((k) => k.toLowerCase() === trimmed.toLowerCase())) {
      setError("This keyword already exists");
      return;
    }

    // Add keyword
    if (emergencyKeywords.length < 20) {
      setEmergencyKeywords([...emergencyKeywords, trimmed]);
      setNewKeyword("");
      setError("");
    } else {
      setError("Maximum 20 keywords allowed");
    }
  };

  const handleRemoveKeyword = (index: number) => {
    setEmergencyKeywords(emergencyKeywords.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

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

      // Success - redirect to dashboard
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    router.push("/dashboard");
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-blue-50 to-white dark:from-zinc-900 dark:to-black">
      {/* Header */}
      <header
        className="flex items-center justify-between px-6 md:px-12 bg-white border-b border-white shadow-sm"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <Link href="/" className="flex items-center gap-2">
          <Logo />
        </Link>
      </header>

      {/* Onboarding Form */}
      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-2xl">
          <div className="rounded-xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h1 className="text-2xl font-nunito font-bold text-zinc-900 dark:text-white">
              Customize Your AI Chatbot
            </h1>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Configure how your AI assistant will interact with clients. You
              can change these settings anytime.
            </p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-8">
              {error && (
                <div
                  role="alert"
                  aria-live="polite"
                  className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400"
                >
                  {error}
                </div>
              )}

              {/* Chatbot Persona */}
              <fieldset>
                <legend className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-3">
                  Chatbot Persona
                </legend>
                <div className="space-y-3">
                  {personas.map((persona) => (
                    <label
                      key={persona.value}
                      className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                        chatbotPersona === persona.value
                          ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                          : "border-zinc-200 hover:border-zinc-300 dark:border-zinc-700 dark:hover:border-zinc-600"
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
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-zinc-900 dark:text-white">
                          {persona.label}
                        </div>
                        <div className="text-sm text-zinc-600 dark:text-zinc-400">
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
                  className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
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
                  className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                  placeholder="Thank you for calling our clinic. How can I help you and your pet today?"
                />
                <div className="mt-1 flex justify-between text-xs text-zinc-500 dark:text-zinc-400">
                  <span>This will be the first thing clients hear</span>
                  <span>
                    {greetingMessage.length}/500
                  </span>
                </div>
              </div>

              {/* Emergency Handling */}
              <div className="border border-zinc-200 rounded-lg dark:border-zinc-700">
                <button
                  type="button"
                  onClick={() => setEmergencyExpanded(!emergencyExpanded)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                >
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
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
                      <span className="text-sm text-zinc-700 dark:text-zinc-300">
                        Transfer emergencies immediately
                      </span>
                      <input
                        type="checkbox"
                        checked={transferImmediately}
                        onChange={(e) => setTransferImmediately(e.target.checked)}
                        className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
                      />
                    </label>

                    {/* Emergency Keywords */}
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                        Emergency Keywords
                      </label>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {emergencyKeywords.map((keyword, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                          >
                            {keyword}
                            <button
                              type="button"
                              onClick={() => handleRemoveKeyword(index)}
                              className="hover:text-red-900 dark:hover:text-red-200"
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
                            className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                          />
                          <button
                            type="button"
                            onClick={handleAddKeyword}
                            className="px-4 py-2 rounded-lg bg-zinc-100 text-sm font-medium text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700 transition-colors"
                          >
                            Add
                          </button>
                        </div>
                      )}
                      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                        {emergencyKeywords.length}/20 keywords
                      </p>
                    </div>

                    {/* Emergency Message */}
                    <div>
                      <label
                        htmlFor="emergencyMessage"
                        className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                      >
                        Emergency Transfer Message (Optional)
                      </label>
                      <textarea
                        id="emergencyMessage"
                        value={emergencyMessage}
                        onChange={(e) => setEmergencyMessage(e.target.value)}
                        rows={2}
                        maxLength={200}
                        className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                        placeholder="Message played when transferring emergency calls"
                      />
                      <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400 text-right">
                        {emergencyMessage.length}/200
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Appointment Preferences */}
              <div className="border border-zinc-200 rounded-lg dark:border-zinc-700">
                <button
                  type="button"
                  onClick={() => setAppointmentExpanded(!appointmentExpanded)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                >
                  <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
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
                      <span className="text-sm text-zinc-700 dark:text-zinc-300">
                        Allow booking appointments
                      </span>
                      <input
                        type="checkbox"
                        checked={allowBooking}
                        onChange={(e) => setAllowBooking(e.target.checked)}
                        className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
                      />
                    </label>

                    {/* Allow Cancellation */}
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-zinc-700 dark:text-zinc-300">
                        Allow canceling appointments
                      </span>
                      <input
                        type="checkbox"
                        checked={allowCancellation}
                        onChange={(e) => setAllowCancellation(e.target.checked)}
                        className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
                      />
                    </label>

                    {/* Allow Rescheduling */}
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-zinc-700 dark:text-zinc-300">
                        Allow rescheduling appointments
                      </span>
                      <input
                        type="checkbox"
                        checked={allowRescheduling}
                        onChange={(e) => setAllowRescheduling(e.target.checked)}
                        className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
                      />
                    </label>

                    {/* Booking Buffer Hours */}
                    <div>
                      <label
                        htmlFor="bookingBufferHours"
                        className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
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
                        className="mt-2 block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-white dark:placeholder-zinc-500"
                      />
                      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                        Minimum hours in advance required for booking
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Form Actions */}
              <div className="space-y-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-blue-600 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                >
                  {loading ? "Saving settings..." : "Save Settings"}
                </button>

                <button
                  type="button"
                  onClick={handleSkip}
                  disabled={loading}
                  className="w-full text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200 transition-colors"
                >
                  Skip for now
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
