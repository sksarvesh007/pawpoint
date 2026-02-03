"use client";

import { useState, useEffect, useRef } from "react";
import Markdown from "markdown-to-jsx";
import type { ChatMessage } from "@/types/chat";
import { env } from "@/lib/env";
import {
  FALLBACK_CLINIC_INFO,
  DEFAULT_BUSINESS_HOURS,
} from "@/lib/constants";

/** Schedule entry for a single day's business hours */
interface DaySchedule {
  open?: string;
  close?: string;
  closed?: boolean;
}

interface ChatbotProps {
  clinicSlug: string;
  clinicName: string;
  greetingMessage: string;
  userIdentifier: string;
  clinicInfo?: {
    phone?: string;
    email?: string;
    address?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    business_hours?: Record<string, unknown>;
  };
}

export default function Chatbot({
  clinicSlug,
  clinicName,
  greetingMessage,
  userIdentifier,
  clinicInfo,
}: ChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const assistantMessageIndexRef = useRef<number>(-1);

  // Initialize with greeting message
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: greetingMessage,
        timestamp: new Date().toISOString(),
      },
    ]);
  }, [greetingMessage]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setError(null);

    // Add user message to UI
    const newUserMessage: ChatMessage = {
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);

    setLoading(true);

    try {
      // Call streaming endpoint
      const response = await fetch(
        `${env.apiUrl}/api/v1/${clinicSlug}/chat/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userMessage,
            conversation_id: conversationId,
            user_identifier: userIdentifier,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to send message");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";
      let buffer = ""; // Buffer for incomplete lines across chunks
      assistantMessageIndexRef.current = -1;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Append decoded chunk to buffer
          buffer += decoder.decode(value, { stream: true });

          // Process complete lines (ending with \n)
          const lines = buffer.split("\n");
          // Keep the last incomplete line in the buffer
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === "conversation_id") {
                  setConversationId(data.conversation_id);
                } else if (data.type === "token") {
                  assistantMessage += data.content;

                  // Update or create assistant message
                  setMessages((prev) => {
                    if (assistantMessageIndexRef.current === -1) {
                      assistantMessageIndexRef.current = prev.length;
                      return [
                        ...prev,
                        {
                          role: "assistant",
                          content: assistantMessage,
                          timestamp: new Date().toISOString(),
                        },
                      ];
                    } else {
                      const newMessages = [...prev];
                      newMessages[assistantMessageIndexRef.current] = {
                        ...newMessages[assistantMessageIndexRef.current],
                        content: assistantMessage,
                      };
                      return newMessages;
                    }
                  });
                } else if (data.type === "error") {
                  throw new Error(data.message);
                }
              } catch (parseErr) {
                // Skip invalid JSON lines
                if (parseErr instanceof SyntaxError) {
                  continue;
                }
                throw parseErr;
              }
            }
          }
        }

        // Process any remaining data in buffer after stream ends
        if (buffer.startsWith("data: ")) {
          try {
            const data = JSON.parse(buffer.slice(6));
            if (data.type === "error") {
              throw new Error(data.message);
            }
          } catch {
            // Ignore parse errors on final buffer
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove the user message if request failed
      setMessages((prev) => prev.slice(0, -1));
      // Restore input value
      setInputValue(userMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Left Sidebar - Clinic Information */}
      <aside className="hidden md:flex md:w-80 lg:w-96 flex-col border-r border-zinc-200/60 bg-white/70 backdrop-blur-md">
        {/* Clinic Header */}
        <div className="p-6 border-b border-zinc-200/60">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] flex items-center justify-center text-white font-bold text-xl">
              {clinicName.charAt(0)}
            </div>
            <div>
              <h1 className="text-lg font-nunito font-bold text-[#1D3533]">
                {clinicName}
              </h1>
              <p className="text-xs text-zinc-600">AI Assistant</p>
            </div>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#3DA99F]/10 border border-[#3DA99F]/20">
            <div className="w-2 h-2 rounded-full bg-[#3DA99F] animate-pulse" />
            <span className="text-xs font-medium text-[#2A9D8F]">Online</span>
          </div>
        </div>

        {/* Contact Information */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Quick Info */}
          <div>
            <h2 className="text-sm font-semibold text-[#1D3533] mb-3 flex items-center gap-2">
              <svg
                className="w-4 h-4 text-[#3DA99F]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              About This Chat
            </h2>
            <p className="text-sm text-zinc-600 leading-relaxed">
              Chat with our AI assistant to schedule appointments, get information about our services, or ask questions about your pet&apos;s care.
            </p>
          </div>

          {/* Contact Details */}
          <div>
            <h2 className="text-sm font-semibold text-[#1D3533] mb-3 flex items-center gap-2">
              <svg
                className="w-4 h-4 text-[#3DA99F]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                />
              </svg>
              Contact Us
            </h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-lg bg-white/80 border border-zinc-200/60">
                <svg
                  className="w-4 h-4 text-[#3DA99F] mt-0.5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
                <div>
                  <p className="text-xs text-zinc-500 mb-0.5">Phone</p>
                  <p className="text-sm font-medium text-zinc-900">
                    {clinicInfo?.phone || FALLBACK_CLINIC_INFO.phone}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-lg bg-white/80 border border-zinc-200/60">
                <svg
                  className="w-4 h-4 text-[#3DA99F] mt-0.5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                <div>
                  <p className="text-xs text-zinc-500 mb-0.5">Email</p>
                  <p className="text-sm font-medium text-zinc-900">
                    {clinicInfo?.email || FALLBACK_CLINIC_INFO.email}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-lg bg-white/80 border border-zinc-200/60">
                <svg
                  className="w-4 h-4 text-[#3DA99F] mt-0.5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <div>
                  <p className="text-xs text-zinc-500 mb-0.5">Address</p>
                  <p className="text-sm font-medium text-zinc-900">
                    {clinicInfo?.address && clinicInfo?.city ? (
                      <>
                        {clinicInfo.address}<br />
                        {clinicInfo.city}, {clinicInfo.state} {clinicInfo.zip_code}
                      </>
                    ) : (
                      <>{FALLBACK_CLINIC_INFO.address}<br />{FALLBACK_CLINIC_INFO.city}, {FALLBACK_CLINIC_INFO.state} {FALLBACK_CLINIC_INFO.zipCode}</>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Office Hours */}
          <div>
            <h2 className="text-sm font-semibold text-[#1D3533] mb-3 flex items-center gap-2">
              <svg
                className="w-4 h-4 text-[#3DA99F]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Office Hours
            </h2>
            <div className="space-y-2 p-3 rounded-lg bg-white/80 border border-zinc-200/60">
              {clinicInfo?.business_hours ? (
                Object.entries(clinicInfo.business_hours).map(([day, scheduleRaw]) => {
                  const schedule = scheduleRaw as DaySchedule;
                  return (
                    <div key={day} className="flex justify-between text-sm">
                      <span className="text-zinc-600 capitalize">{day}</span>
                      <span className="font-medium text-zinc-900">
                        {schedule.closed ? (
                          "Closed"
                        ) : (
                          <>
                            {schedule.open} - {schedule.close}
                          </>
                        )}
                      </span>
                    </div>
                  );
                })
              ) : (
                <>
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-600">Mon - Fri</span>
                    <span className="font-medium text-zinc-900">{DEFAULT_BUSINESS_HOURS.weekdays}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-600">Saturday</span>
                    <span className="font-medium text-zinc-900">{DEFAULT_BUSINESS_HOURS.saturday}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-600">Sunday</span>
                    <span className="font-medium text-zinc-900">{DEFAULT_BUSINESS_HOURS.sunday}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Important Note */}
          <div className="p-4 rounded-lg bg-gradient-to-br from-[#3DA99F]/10 to-[#7ECDC8]/10 border border-[#3DA99F]/20">
            <div className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-[#2A9D8F] flex-shrink-0 mt-0.5"
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
              <div>
                <p className="text-sm font-semibold text-[#1D3533] mb-1">Emergency?</p>
                <p className="text-xs text-zinc-600 leading-relaxed">
                  If your pet is experiencing a medical emergency, please call us immediately or visit the nearest emergency veterinary clinic.
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Right Side - Chat Interface */}
      <div className="flex-1 flex flex-col bg-white/50 backdrop-blur-sm">
        {/* Mobile Header */}
        <div className="md:hidden border-b border-zinc-200/60 bg-white/80 backdrop-blur-sm px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] flex items-center justify-center text-white font-bold">
              {clinicName.charAt(0)}
            </div>
            <div>
              <h1 className="text-base font-nunito font-bold text-[#1D3533]">
                {clinicName}
              </h1>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[#3DA99F]" />
                <span className="text-xs text-zinc-600">Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] text-white shadow-lg shadow-[#3DA99F]/25"
                      : "bg-white/80 backdrop-blur-sm text-zinc-900 border border-zinc-200/60 shadow-sm"
                  }`}
                >
                  {message.role === "user" ? (
                    <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                      {message.content}
                    </p>
                  ) : (
                    <div className="markdown-content text-sm leading-relaxed">
                      <Markdown
                        options={{
                          overrides: {
                            h1: { props: { className: "text-xl font-bold text-zinc-900 mt-4 mb-2 first:mt-0" } },
                            h2: { props: { className: "text-lg font-bold text-zinc-900 mt-3 mb-2 first:mt-0" } },
                            h3: { props: { className: "text-base font-bold text-zinc-900 mt-3 mb-1 first:mt-0" } },
                            h4: { props: { className: "text-sm font-bold text-zinc-900 mt-2 mb-1 first:mt-0" } },
                            p: { props: { className: "text-zinc-900 mb-2 last:mb-0" } },
                            a: { props: { className: "text-[#3DA99F] hover:underline font-medium" } },
                            ul: { props: { className: "list-disc list-inside text-zinc-900 mb-2 space-y-1" } },
                            ol: { props: { className: "list-decimal list-inside text-zinc-900 mb-2 space-y-1" } },
                            li: { props: { className: "text-zinc-900" } },
                            strong: { props: { className: "font-semibold text-zinc-900" } },
                            em: { props: { className: "italic text-zinc-900" } },
                            code: { props: { className: "bg-zinc-100 text-[#2A9D8F] px-1.5 py-0.5 rounded text-xs font-mono" } },
                            pre: { props: { className: "bg-zinc-900 text-zinc-100 p-3 rounded-lg overflow-x-auto mb-2 text-xs" } },
                            blockquote: { props: { className: "border-l-4 border-[#3DA99F] pl-3 py-1 text-zinc-700 italic mb-2" } },
                            table: { props: { className: "min-w-full divide-y divide-zinc-200 mb-2" } },
                            thead: { props: { className: "bg-zinc-50" } },
                            tbody: { props: { className: "bg-white divide-y divide-zinc-200" } },
                            th: { props: { className: "px-3 py-2 text-left text-xs font-medium text-zinc-700 uppercase tracking-wider" } },
                            td: { props: { className: "px-3 py-2 text-sm text-zinc-900" } },
                            hr: { props: { className: "border-zinc-200 my-3" } },
                          },
                        }}
                      >
                        {message.content}
                      </Markdown>
                    </div>
                  )}
                  {message.timestamp && (
                    <p
                      className={`mt-1.5 text-xs ${
                        message.role === "user"
                          ? "text-white/70"
                          : "text-zinc-500"
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[75%] rounded-2xl bg-white/80 backdrop-blur-sm px-4 py-3 border border-zinc-200/60 shadow-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-[#3DA99F]" />
                    <div
                      className="h-2 w-2 animate-bounce rounded-full bg-[#3DA99F]"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <div
                      className="h-2 w-2 animate-bounce rounded-full bg-[#3DA99F]"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="border-t border-zinc-200/60 bg-red-50/80 backdrop-blur-sm px-4 md:px-6 py-3">
            <div className="max-w-3xl mx-auto">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        )}

        {/* Input Form */}
        <form
          onSubmit={handleSendMessage}
          className="border-t border-zinc-200/60 bg-white/80 backdrop-blur-sm px-4 md:px-6 py-4"
        >
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                disabled={loading}
                maxLength={1000}
                className="flex-1 rounded-xl border border-zinc-300 bg-white px-4 py-3 text-zinc-900 placeholder-zinc-400 focus:border-[#3DA99F] focus:outline-none focus:ring-2 focus:ring-[#3DA99F]/20 disabled:cursor-not-allowed disabled:opacity-50 transition-all"
              />
              <button
                type="submit"
                disabled={loading || !inputValue.trim()}
                className="rounded-xl bg-gradient-to-br from-[#3DA99F] to-[#2A9D8F] px-6 py-3 font-semibold text-white hover:shadow-lg hover:shadow-[#3DA99F]/30 focus:outline-none focus:ring-2 focus:ring-[#3DA99F] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </button>
            </div>
            <p className="mt-2 text-xs text-zinc-500 text-center">
              {inputValue.length}/1000 characters
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
