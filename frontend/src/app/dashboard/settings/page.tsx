"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { updateChatbotSettings, getChatbotSettings } from "@/lib/api/clinic";
import type { UpdateChatbotSettingsRequest } from "@/types/clinic";

type ChatbotPersona = "professional" | "friendly" | "empathetic" | "warm";

type TabType = "clinic" | "chatbot" | "advanced";

type DaySchedule = {
  open: string;
  close: string;
  closed: boolean;
};

type WeekSchedule = {
  monday: DaySchedule;
  tuesday: DaySchedule;
  wednesday: DaySchedule;
  thursday: DaySchedule;
  friday: DaySchedule;
  saturday: DaySchedule;
  sunday: DaySchedule;
};

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>("clinic");

  // Clinic Information
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [zipCode, setZipCode] = useState("");
  const [officeHours, setOfficeHours] = useState<WeekSchedule>({
    monday: { open: "08:00", close: "18:00", closed: false },
    tuesday: { open: "08:00", close: "18:00", closed: false },
    wednesday: { open: "08:00", close: "18:00", closed: false },
    thursday: { open: "08:00", close: "18:00", closed: false },
    friday: { open: "08:00", close: "18:00", closed: false },
    saturday: { open: "09:00", close: "16:00", closed: false },
    sunday: { open: "", close: "", closed: true },
  });

  // Chatbot Settings
  const [chatbotName, setChatbotName] = useState("");
  const [chatbotPersona, setChatbotPersona] =
    useState<ChatbotPersona>("professional");
  const [greetingMessage, setGreetingMessage] = useState(
    "Thank you for calling our clinic. How can I help you and your pet today?"
  );
  const [additionalContext, setAdditionalContext] = useState("");

  // Advanced Settings
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

  const personas: Array<{
    value: ChatbotPersona;
    label: string;
    description: string;
    icon: string;
  }> = [
    {
      value: "professional",
      label: "Professional",
      description: "Formal, efficient, and clinical",
      icon: "💼",
    },
    {
      value: "friendly",
      label: "Friendly",
      description: "Warm, conversational, and approachable",
      icon: "😊",
    },
    {
      value: "empathetic",
      label: "Empathetic",
      description: "Caring, understanding, and supportive",
      icon: "💚",
    },
    {
      value: "warm",
      label: "Warm",
      description: "Gentle, comforting, and compassionate",
      icon: "🤗",
    },
  ];

  // Load existing settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const settings = await getChatbotSettings();

        // Load contact information
        setPhone(settings.phone || "");
        setEmail(settings.email || "");
        setAddress(settings.address || "");
        setCity(settings.city || "");
        setState(settings.state || "");
        setZipCode(settings.zip_code || "");

        // Load office hours if available
        if (settings.business_hours) {
          setOfficeHours(settings.business_hours as WeekSchedule);
        }

        // Load chatbot settings
        setChatbotName(settings.chatbot_name || "");
        setChatbotPersona(settings.chatbot_persona as ChatbotPersona);
        setGreetingMessage(settings.greeting_message);
        setAdditionalContext(settings.additional_context || "");

        // Load emergency settings
        if (settings.emergency_handling) {
          setTransferImmediately(settings.emergency_handling.transfer_immediately);
          setEmergencyKeywords(settings.emergency_handling.keywords);
          setEmergencyMessage(
            settings.emergency_handling.emergency_message || ""
          );
        }

        // Load appointment settings
        if (settings.appointment_preferences) {
          setAllowBooking(settings.appointment_preferences.allow_booking);
          setAllowCancellation(
            settings.appointment_preferences.allow_cancellation
          );
          setAllowRescheduling(
            settings.appointment_preferences.allow_rescheduling
          );
          setBookingBufferHours(
            settings.appointment_preferences.booking_buffer_hours
          );
        }
      } catch (err) {
        console.error("Failed to load settings:", err);
        setError("Failed to load settings");
      } finally {
        setInitialLoading(false);
      }
    };

    loadSettings();
  }, []);

  const handleAddKeyword = () => {
    const trimmed = newKeyword.trim();

    if (trimmed.length < 2) {
      setError("Keywords must be at least 2 characters");
      return;
    }

    if (trimmed.length > 50) {
      setError("Keywords must be less than 50 characters");
      return;
    }

    if (!/^[A-Za-z0-9\s\-]+$/.test(trimmed)) {
      setError(
        "Keywords can only contain letters, numbers, spaces, and hyphens"
      );
      return;
    }

    if (
      emergencyKeywords.some((k) => k.toLowerCase() === trimmed.toLowerCase())
    ) {
      setError("This keyword already exists");
      return;
    }

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

  const handleSave = async () => {
    setError("");
    setSuccess("");

    // Validation
    if (activeTab === "clinic") {
      if (!phone.trim()) {
        setError("Phone number is required");
        return;
      }
      if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setError("Valid email is required");
        return;
      }
      if (!address.trim()) {
        setError("Address is required");
        return;
      }
      if (!city.trim()) {
        setError("City is required");
        return;
      }
      if (!state.trim()) {
        setError("State is required");
        return;
      }
      if (!zipCode.trim()) {
        setError("ZIP code is required");
        return;
      }
    }

    if (activeTab === "chatbot") {
      if (greetingMessage.trim().length < 10) {
        setError("Greeting message must be at least 10 characters");
        return;
      }
      if (greetingMessage.length > 500) {
        setError("Greeting message must be less than 500 characters");
        return;
      }
    }

    if (activeTab === "advanced") {
      if (emergencyKeywords.length === 0) {
        setError("At least one emergency keyword is required");
        return;
      }
      if (bookingBufferHours < 0 || bookingBufferHours > 72) {
        setError("Booking buffer hours must be between 0 and 72");
        return;
      }
    }

    setLoading(true);

    try {
      const settings: UpdateChatbotSettingsRequest = {
        // Contact Information
        phone: phone.trim(),
        email: email.trim(),
        address: address.trim(),
        city: city.trim(),
        state: state.trim(),
        zip_code: zipCode.trim(),
        business_hours: officeHours,
        // Chatbot Settings
        chatbot_name: chatbotName.trim() || undefined,
        chatbot_persona: chatbotPersona,
        greeting_message: greetingMessage.trim(),
        additional_context: additionalContext.trim() || undefined,
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

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      let errorMessage = "Failed to save settings";

      if (err instanceof Error) {
        errorMessage = err.message;

        if (
          errorMessage.toLowerCase().includes("authenticated") ||
          errorMessage.toLowerCase().includes("log in")
        ) {
          errorMessage = "Your session has expired. Please log in again.";
          setTimeout(() => {
            router.push("/login");
          }, 2000);
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#3DA99F] border-r-transparent"></div>
          <p className="mt-4 text-sm text-zinc-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-[#1D3533]">
          Settings
        </h1>
        <p className="mt-2 text-zinc-600">
          Manage your clinic information and AI assistant configuration
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-zinc-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("clinic")}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "clinic"
                ? "border-[#3DA99F] text-[#3DA99F]"
                : "border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300"
            }`}
          >
            Clinic Information
          </button>
          <button
            onClick={() => setActiveTab("chatbot")}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "chatbot"
                ? "border-[#3DA99F] text-[#3DA99F]"
                : "border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300"
            }`}
          >
            Chatbot Settings
          </button>
          <button
            onClick={() => setActiveTab("advanced")}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === "advanced"
                ? "border-[#3DA99F] text-[#3DA99F]"
                : "border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300"
            }`}
          >
            Advanced Settings
          </button>
        </nav>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-6 rounded-lg bg-green-50 p-4 text-sm text-green-600">
          {success}
        </div>
      )}

      {/* Tab Content */}
      <div className="bg-white rounded-xl border border-zinc-200 p-6 shadow-sm">
        {/* Clinic Information Tab */}
        {activeTab === "clinic" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-[#1D3533] mb-4">
                Contact Information
              </h2>
              <p className="text-sm text-zinc-600 mb-6">
                This information will be displayed to clients in your public chatbot
              </p>

              <div className="space-y-4">
                {/* Phone */}
                <div>
                  <label
                    htmlFor="phone"
                    className="block text-sm font-medium text-zinc-700 mb-2"
                  >
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="(555) 123-4567"
                    className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-zinc-700 mb-2"
                  >
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="contact@clinic.com"
                    className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  />
                </div>

                {/* Address */}
                <div>
                  <label
                    htmlFor="address"
                    className="block text-sm font-medium text-zinc-700 mb-2"
                  >
                    Street Address *
                  </label>
                  <input
                    type="text"
                    id="address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="123 Main Street"
                    className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  />
                </div>

                {/* City, State, ZIP */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="md:col-span-1">
                    <label
                      htmlFor="city"
                      className="block text-sm font-medium text-zinc-700 mb-2"
                    >
                      City *
                    </label>
                    <input
                      type="text"
                      id="city"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      placeholder="San Francisco"
                      className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="state"
                      className="block text-sm font-medium text-zinc-700 mb-2"
                    >
                      State *
                    </label>
                    <input
                      type="text"
                      id="state"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      placeholder="CA"
                      maxLength={2}
                      className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F] uppercase"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="zipCode"
                      className="block text-sm font-medium text-zinc-700 mb-2"
                    >
                      ZIP Code *
                    </label>
                    <input
                      type="text"
                      id="zipCode"
                      value={zipCode}
                      onChange={(e) => setZipCode(e.target.value)}
                      placeholder="94102"
                      maxLength={10}
                      className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                    />
                  </div>
                </div>
              </div>

              {/* Office Hours */}
              <div className="mt-8 pt-8 border-t border-zinc-200">
                <h3 className="text-lg font-semibold text-[#1D3533] mb-4">
                  Office Hours
                </h3>
                <div className="space-y-3">
                  {Object.entries(officeHours).map(([day, schedule]) => (
                    <div
                      key={day}
                      className="flex items-center gap-4 p-3 rounded-lg border border-zinc-200"
                    >
                      <div className="w-28">
                        <p className="text-sm font-medium text-zinc-700 capitalize">
                          {day}
                        </p>
                      </div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={!schedule.closed}
                          onChange={(e) => {
                            setOfficeHours({
                              ...officeHours,
                              [day]: {
                                ...schedule,
                                closed: !e.target.checked,
                              },
                            });
                          }}
                          className="h-4 w-4 rounded text-[#3DA99F] focus:ring-[#3DA99F]"
                        />
                        <span className="text-sm text-zinc-600">Open</span>
                      </label>
                      {!schedule.closed && (
                        <div className="flex items-center gap-2 flex-1">
                          <input
                            type="time"
                            value={schedule.open}
                            onChange={(e) => {
                              setOfficeHours({
                                ...officeHours,
                                [day]: {
                                  ...schedule,
                                  open: e.target.value,
                                },
                              });
                            }}
                            className="px-3 py-2 text-sm border border-zinc-300 rounded-lg focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                          />
                          <span className="text-zinc-500 text-sm">to</span>
                          <input
                            type="time"
                            value={schedule.close}
                            onChange={(e) => {
                              setOfficeHours({
                                ...officeHours,
                                [day]: {
                                  ...schedule,
                                  close: e.target.value,
                                },
                              });
                            }}
                            className="px-3 py-2 text-sm border border-zinc-300 rounded-lg focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                          />
                        </div>
                      )}
                      {schedule.closed && (
                        <span className="text-sm text-zinc-400 italic flex-1">
                          Closed
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chatbot Settings Tab */}
        {activeTab === "chatbot" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-[#1D3533] mb-4">
                Chatbot Personality
              </h2>
              <p className="text-sm text-zinc-600 mb-6">
                Choose the tone and style for your AI assistant
              </p>

              {/* Persona Selection */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                {personas.map((persona) => (
                  <button
                    key={persona.value}
                    type="button"
                    onClick={() => setChatbotPersona(persona.value)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      chatbotPersona === persona.value
                        ? "border-[#3DA99F] bg-[#3DA99F]/10 shadow-md"
                        : "border-zinc-200 hover:border-zinc-300"
                    }`}
                  >
                    <div className="text-2xl mb-2">{persona.icon}</div>
                    <div className="font-semibold text-zinc-900 mb-1">
                      {persona.label}
                    </div>
                    <div className="text-xs text-zinc-600">
                      {persona.description}
                    </div>
                  </button>
                ))}
              </div>

              {/* Chatbot Name */}
              <div className="mb-4">
                <label
                  htmlFor="chatbotName"
                  className="block text-sm font-medium text-zinc-700 mb-2"
                >
                  AI Assistant Name (Optional)
                </label>
                <input
                  id="chatbotName"
                  type="text"
                  value={chatbotName}
                  onChange={(e) => setChatbotName(e.target.value)}
                  maxLength={50}
                  className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="e.g., Bella, Max, Dr. Paws (leave empty to use clinic name)"
                />
                <p className="mt-1 text-xs text-zinc-500">
                  Give your AI assistant a friendly name that will be shown to clients
                </p>
              </div>

              {/* Greeting Message */}
              <div className="mb-4">
                <label
                  htmlFor="greetingMessage"
                  className="block text-sm font-medium text-zinc-700 mb-2"
                >
                  Greeting Message
                </label>
                <textarea
                  id="greetingMessage"
                  value={greetingMessage}
                  onChange={(e) => setGreetingMessage(e.target.value)}
                  rows={3}
                  maxLength={500}
                  className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="Thank you for calling our clinic. How can I help you and your pet today?"
                />
                <div className="mt-1 flex justify-between text-xs text-zinc-500">
                  <span>First thing clients will hear</span>
                  <span>{greetingMessage.length}/500</span>
                </div>
              </div>

              {/* Additional Context */}
              <div>
                <label
                  htmlFor="additionalContext"
                  className="block text-sm font-medium text-zinc-700 mb-2"
                >
                  Additional Information (Optional)
                </label>
                <textarea
                  id="additionalContext"
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  rows={6}
                  maxLength={2000}
                  className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="Add information about specialties, policies, or services..."
                />
                <div className="mt-1 text-xs text-zinc-500 text-right">
                  {additionalContext.length}/2000
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Advanced Settings Tab */}
        {activeTab === "advanced" && (
          <div className="space-y-6">
            {/* Emergency Handling */}
            <div>
              <h2 className="text-xl font-semibold text-[#1D3533] mb-4 flex items-center gap-2">
                <svg
                  className="w-6 h-6 text-red-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                Emergency Handling
              </h2>

              <label className="flex items-center justify-between mb-4 p-3 rounded-lg border border-zinc-200">
                <span className="text-sm text-zinc-700">
                  Transfer emergencies immediately
                </span>
                <input
                  type="checkbox"
                  checked={transferImmediately}
                  onChange={(e) => setTransferImmediately(e.target.checked)}
                  className="h-4 w-4 rounded text-[#3DA99F] focus:ring-[#3DA99F]"
                />
              </label>

              <div className="mb-4">
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
                      className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                    />
                    <button
                      type="button"
                      onClick={handleAddKeyword}
                      className="px-4 py-2 rounded-lg bg-[#3DA99F] text-sm font-medium text-white hover:bg-[#2A9D8F]"
                    >
                      Add
                    </button>
                  </div>
                )}
                <p className="mt-1 text-xs text-zinc-500">
                  {emergencyKeywords.length}/20 keywords
                </p>
              </div>

              <div className="mb-6">
                <label
                  htmlFor="emergencyMessage"
                  className="block text-sm font-medium text-zinc-700 mb-2"
                >
                  Emergency Transfer Message (Optional)
                </label>
                <textarea
                  id="emergencyMessage"
                  value={emergencyMessage}
                  onChange={(e) => setEmergencyMessage(e.target.value)}
                  rows={2}
                  maxLength={200}
                  className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  placeholder="Message played when transferring emergency calls"
                />
                <div className="mt-1 text-xs text-zinc-500 text-right">
                  {emergencyMessage.length}/200
                </div>
              </div>
            </div>

            {/* Appointment Preferences */}
            <div>
              <h2 className="text-xl font-semibold text-[#1D3533] mb-4 flex items-center gap-2">
                <svg
                  className="w-6 h-6 text-[#3DA99F]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                Appointment Options
              </h2>

              <div className="space-y-3">
                <label className="flex items-center justify-between p-3 rounded-lg border border-zinc-200">
                  <span className="text-sm text-zinc-700">
                    Allow booking appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowBooking}
                    onChange={(e) => setAllowBooking(e.target.checked)}
                    className="h-4 w-4 rounded text-[#3DA99F] focus:ring-[#3DA99F]"
                  />
                </label>

                <label className="flex items-center justify-between p-3 rounded-lg border border-zinc-200">
                  <span className="text-sm text-zinc-700">
                    Allow canceling appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowCancellation}
                    onChange={(e) => setAllowCancellation(e.target.checked)}
                    className="h-4 w-4 rounded text-[#3DA99F] focus:ring-[#3DA99F]"
                  />
                </label>

                <label className="flex items-center justify-between p-3 rounded-lg border border-zinc-200">
                  <span className="text-sm text-zinc-700">
                    Allow rescheduling appointments
                  </span>
                  <input
                    type="checkbox"
                    checked={allowRescheduling}
                    onChange={(e) => setAllowRescheduling(e.target.checked)}
                    className="h-4 w-4 rounded text-[#3DA99F] focus:ring-[#3DA99F]"
                  />
                </label>

                <div className="pt-2">
                  <label
                    htmlFor="bookingBufferHours"
                    className="block text-sm font-medium text-zinc-700 mb-2"
                  >
                    Minimum hours in advance for booking
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
                    className="block w-full rounded-lg border border-zinc-300 px-4 py-3 text-zinc-900 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                  />
                  <p className="mt-1 text-xs text-zinc-500">
                    Between 0 and 72 hours
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="mt-8 pt-6 border-t border-zinc-200 flex items-center justify-between">
          <p className="text-sm text-zinc-600">
            Changes will be applied immediately
          </p>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-6 py-3 rounded-lg bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] text-sm font-bold text-white hover:shadow-lg hover:shadow-[#3DA99F]/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#3DA99F]/25"
          >
            {loading ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
