"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Logo, NAVBAR_HEIGHT } from "@/components/Logo";
import { updateChatbotSettings } from "@/lib/api/clinic";
import type { UpdateChatbotSettingsRequest } from "@/types/clinic";

type ChatbotPersona = "professional" | "friendly" | "empathetic" | "warm";

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

export default function ChatbotOnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;

  // Step 1: Clinic Information
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

  // Step 2: Chatbot Personality
  const [chatbotName, setChatbotName] = useState("");
  const [chatbotPersona, setChatbotPersona] =
    useState<ChatbotPersona>("professional");
  const [greetingMessage, setGreetingMessage] = useState(
    "Thank you for calling our clinic. How can I help you and your pet today?"
  );
  const [additionalContext, setAdditionalContext] = useState("");

  // Step 3: Advanced Settings
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

    if (emergencyKeywords.some((k) => k.toLowerCase() === trimmed.toLowerCase())) {
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

  const validateStep = (step: number): boolean => {
    setError("");

    if (step === 1) {
      if (!phone.trim()) {
        setError("Phone number is required");
        return false;
      }
      if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setError("Valid email is required");
        return false;
      }
      if (!address.trim()) {
        setError("Address is required");
        return false;
      }
      if (!city.trim()) {
        setError("City is required");
        return false;
      }
      if (!state.trim()) {
        setError("State is required");
        return false;
      }
      if (!zipCode.trim()) {
        setError("ZIP code is required");
        return false;
      }
    }

    if (step === 2) {
      if (greetingMessage.trim().length < 10) {
        setError("Greeting message must be at least 10 characters");
        return false;
      }
      if (greetingMessage.length > 500) {
        setError("Greeting message must be less than 500 characters");
        return false;
      }
    }

    if (step === 3) {
      if (emergencyKeywords.length === 0) {
        setError("At least one emergency keyword is required");
        return false;
      }
      if (bookingBufferHours < 0 || bookingBufferHours > 72) {
        setError("Booking buffer hours must be between 0 and 72");
        return false;
      }
    }

    return true;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setError("");
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

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
      router.push("/dashboard");
    } catch (err) {
      let errorMessage = "Failed to save settings";

      if (err instanceof Error) {
        errorMessage = err.message;

        if (
          errorMessage.toLowerCase().includes("authenticated") ||
          errorMessage.toLowerCase().includes("log in")
        ) {
          errorMessage = "Your session has expired. Redirecting to login...";
          setTimeout(() => {
            router.push("/login?redirect=/onboarding/chatbot");
          }, 2000);
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    router.push("/dashboard");
  };

  return (
    <div className="flex min-h-screen flex-col bg-white relative overflow-hidden">
      {/* Background Waves */}
      <div className="absolute inset-0 pointer-events-none">
        <svg
          className="absolute top-0 left-0 w-full h-full"
          viewBox="0 0 1440 900"
          preserveAspectRatio="xMidYMid slice"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="onboardingWave1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="50%" stopColor="#3DA99F" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.15" />
            </linearGradient>
            <linearGradient id="onboardingWave2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.1" />
              <stop offset="50%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#3DA99F" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="onboardingWave3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3DA99F" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#2A9D8F" stopOpacity="0.12" />
            </linearGradient>
          </defs>

          <path
            d="M-100,550 C200,700 400,350 720,450 C1040,550 1200,300 1540,400 L1540,900 L-100,900 Z"
            fill="url(#onboardingWave1)"
          />
          <path
            d="M-100,600 C150,450 350,650 650,500 C950,350 1150,600 1540,450 L1540,900 L-100,900 Z"
            fill="url(#onboardingWave2)"
          />
          <path
            d="M-100,650 C200,500 500,700 800,550 C1100,400 1300,650 1540,500 L1540,900 L-100,900 Z"
            fill="url(#onboardingWave3)"
          />
        </svg>
      </div>

      {/* Header */}
      <header
        className="flex items-center justify-between px-6 md:px-12 bg-white/80 backdrop-blur-sm border-b border-zinc-100 shadow-sm relative z-20"
        style={{ height: `${NAVBAR_HEIGHT}px` }}
      >
        <Link href="/" className="flex items-center gap-2">
          <Logo />
        </Link>
      </header>

      {/* Onboarding Form */}
      <main className="flex flex-1 items-center justify-center px-6 py-12 relative z-10">
        <div className="w-full max-w-2xl">
          <div className="rounded-2xl border border-zinc-200/60 bg-white/70 backdrop-blur-md p-8 shadow-xl">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-2xl font-nunito font-bold text-[#1D3533]">
                Set Up Your AI Assistant
              </h1>
              <p className="mt-2 text-sm text-zinc-600">
                Let's configure your chatbot to provide the best experience for your clients
              </p>
            </div>

            {/* Progress Indicator */}
            <div className="mb-8">
              <div className="flex items-start justify-between gap-2">
                {[
                  { step: 1, label: "Clinic Info" },
                  { step: 2, label: "Personality" },
                  { step: 3, label: "Settings" },
                ].map((item, index) => (
                  <div key={item.step} className="flex items-center flex-1">
                    <div className="flex flex-col items-center flex-1">
                      <div
                        className={`flex items-center justify-center w-10 h-10 rounded-full border-2 font-semibold text-sm transition-all mb-2 ${
                          item.step === currentStep
                            ? "border-[#3DA99F] bg-[#3DA99F] text-white"
                            : item.step < currentStep
                            ? "border-[#3DA99F] bg-[#3DA99F] text-white"
                            : "border-zinc-300 bg-white text-zinc-400"
                        }`}
                      >
                        {item.step < currentStep ? (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        ) : (
                          item.step
                        )}
                      </div>
                      <span
                        className={`text-xs text-center ${
                          item.step === currentStep
                            ? "font-medium text-[#2A9D8F]"
                            : "text-zinc-600"
                        }`}
                      >
                        {item.label}
                      </span>
                    </div>
                    {index < 2 && (
                      <div
                        className={`h-1 w-full rounded transition-all mt-[-24px] mx-2 ${
                          item.step < currentStep ? "bg-[#3DA99F]" : "bg-zinc-200"
                        }`}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div
                role="alert"
                aria-live="polite"
                className="mb-6 rounded-lg bg-red-50 p-3 text-sm text-red-600"
              >
                {error}
              </div>
            )}

            {/* Step Content */}
            <div className="min-h-[400px]">
              {/* Step 1: Clinic Information */}
              {currentStep === 1 && (
                <div className="space-y-6 animate-fadeIn">
                  <div>
                    <h2 className="text-lg font-semibold text-[#1D3533] mb-4">
                      Contact Information
                    </h2>
                    <p className="text-sm text-zinc-600 mb-6">
                      This information will be displayed to clients in your chatbot
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
                          className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
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
                          className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
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
                          className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
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
                            className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
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
                            className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F] uppercase"
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
                            className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Office Hours */}
                  <div>
                    <h3 className="text-base font-semibold text-[#1D3533] mb-4 mt-6">
                      Office Hours
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(officeHours).map(([day, schedule]) => (
                        <div
                          key={day}
                          className="flex items-center gap-4 p-3 rounded-lg border border-zinc-200 bg-white/80"
                        >
                          <div className="w-24">
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
                            <>
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
                              <span className="text-zinc-500">to</span>
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
                            </>
                          )}
                          {schedule.closed && (
                            <span className="text-sm text-zinc-400 italic">
                              Closed
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Chatbot Personality */}
              {currentStep === 2 && (
                <div className="space-y-6 animate-fadeIn">
                  <div>
                    <h2 className="text-lg font-semibold text-[#1D3533] mb-2">
                      Choose Your Chatbot's Personality
                    </h2>
                    <p className="text-sm text-zinc-600 mb-6">
                      Select the tone and style for your AI assistant
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
                              : "border-zinc-200 hover:border-zinc-300 bg-white"
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
                        className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                        placeholder="e.g., Bella, Max, Dr. Paws (leave empty to use clinic name)"
                      />
                      <p className="mt-1 text-xs text-zinc-500">
                        Give your AI assistant a friendly name
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
                        className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
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
                        rows={4}
                        maxLength={2000}
                        className="block w-full rounded-lg border border-zinc-300 bg-white/80 px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-1 focus:ring-[#3DA99F]"
                        placeholder="Add information about specialties, policies, or services to help the AI provide accurate responses..."
                      />
                      <div className="mt-1 text-xs text-zinc-500 text-right">
                        {additionalContext.length}/2000
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Advanced Settings */}
              {currentStep === 3 && (
                <div className="space-y-6 animate-fadeIn">
                  <div>
                    <h2 className="text-lg font-semibold text-[#1D3533] mb-2">
                      Emergency & Appointment Settings
                    </h2>
                    <p className="text-sm text-zinc-600 mb-6">
                      Configure how your chatbot handles emergencies and appointments
                    </p>

                    {/* Emergency Handling */}
                    <div className="mb-6 p-4 rounded-lg border border-zinc-200 bg-white/80">
                      <h3 className="font-semibold text-zinc-900 mb-4 flex items-center gap-2">
                        <svg
                          className="w-5 h-5 text-red-500"
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
                      </h3>

                      <label className="flex items-center justify-between mb-4">
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
                              className="flex-1 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm"
                            />
                            <button
                              type="button"
                              onClick={handleAddKeyword}
                              className="px-4 py-2 rounded-lg bg-zinc-100 text-sm font-medium hover:bg-zinc-200"
                            >
                              Add
                            </button>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Appointment Preferences */}
                    <div className="p-4 rounded-lg border border-zinc-200 bg-white/80">
                      <h3 className="font-semibold text-zinc-900 mb-4 flex items-center gap-2">
                        <svg
                          className="w-5 h-5 text-[#3DA99F]"
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
                      </h3>

                      <div className="space-y-3">
                        <label className="flex items-center justify-between">
                          <span className="text-sm text-zinc-700">
                            Allow booking appointments
                          </span>
                          <input
                            type="checkbox"
                            checked={allowBooking}
                            onChange={(e) => setAllowBooking(e.target.checked)}
                            className="h-4 w-4 rounded text-[#3DA99F]"
                          />
                        </label>

                        <label className="flex items-center justify-between">
                          <span className="text-sm text-zinc-700">
                            Allow canceling appointments
                          </span>
                          <input
                            type="checkbox"
                            checked={allowCancellation}
                            onChange={(e) => setAllowCancellation(e.target.checked)}
                            className="h-4 w-4 rounded text-[#3DA99F]"
                          />
                        </label>

                        <label className="flex items-center justify-between">
                          <span className="text-sm text-zinc-700">
                            Allow rescheduling appointments
                          </span>
                          <input
                            type="checkbox"
                            checked={allowRescheduling}
                            onChange={(e) => setAllowRescheduling(e.target.checked)}
                            className="h-4 w-4 rounded text-[#3DA99F]"
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
                            className="block w-full rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="mt-8 flex items-center justify-between gap-4">
              <div className="flex-1">
                {currentStep > 1 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    disabled={loading}
                    className="px-6 py-3 rounded-lg border border-zinc-300 text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                )}
              </div>

              <button
                type="button"
                onClick={handleSkip}
                disabled={loading}
                className="text-sm text-zinc-600 hover:text-zinc-900 transition-colors px-4 py-2"
              >
                Skip for now
              </button>

              <div className="flex-1 flex justify-end">
                {currentStep < totalSteps ? (
                  <button
                    type="button"
                    onClick={handleNext}
                    disabled={loading}
                    className="px-6 py-3 rounded-lg bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] text-sm font-bold text-white hover:shadow-lg hover:shadow-[#3DA99F]/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={loading}
                    className="px-6 py-3 rounded-lg bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] text-sm font-bold text-white hover:shadow-lg hover:shadow-[#3DA99F]/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#3DA99F]/25"
                  >
                    {loading ? "Saving..." : "Complete Setup"}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
