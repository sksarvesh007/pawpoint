/**
 * Demo dashboard page with mock data.
 * No authentication required - public showcase.
 * Mirrors the exact same UI as the real dashboard with clickable tabs.
 */

"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { MOCK_ANALYTICS } from "@/components/dashboard/mockData";
import { env } from "@/lib/env";
import {
  LayoutDashboard,
  Calendar,
  PawPrint,
  Phone,
  Settings,
  Inbox,
  MessageCircle,
  FileText,
  LayoutGrid,
  Shield,
  HelpCircle,
  LogOut,
  X,
  ArrowLeft,
} from "lucide-react";

type DemoTab =
  | "dashboard"
  | "inbox"
  | "appointments"
  | "patients"
  | "calls"
  | "chat"
  | "reports"
  | "settings";

// Mock appointment requests data
const MOCK_APPOINTMENTS = [
  {
    id: 1,
    petName: "Buddy",
    ownerName: "Sarah Johnson",
    phone: "+1 (555) 123-4567",
    type: "Checkup",
    requestedDate: "Jan 30, 2026",
    status: "pending",
    species: "Dog",
  },
  {
    id: 2,
    petName: "Whiskers",
    ownerName: "Mike Chen",
    phone: "+1 (555) 234-5678",
    type: "Vaccination",
    requestedDate: "Jan 31, 2026",
    status: "confirmed",
    species: "Cat",
  },
  {
    id: 3,
    petName: "Max",
    ownerName: "Emily Davis",
    phone: "+1 (555) 345-6789",
    type: "Sick Visit",
    requestedDate: "Jan 29, 2026",
    status: "pending",
    species: "Dog",
  },
  {
    id: 4,
    petName: "Luna",
    ownerName: "James Wilson",
    phone: "+1 (555) 456-7890",
    type: "Dental",
    requestedDate: "Feb 1, 2026",
    status: "confirmed",
    species: "Cat",
  },
  {
    id: 5,
    petName: "Rocky",
    ownerName: "Lisa Brown",
    phone: "+1 (555) 567-8901",
    type: "Follow-up",
    requestedDate: "Jan 30, 2026",
    status: "cancelled",
    species: "Dog",
  },
];

// Mock patients data
const MOCK_PATIENTS = [
  {
    id: 1,
    name: "Buddy",
    species: "Dog",
    breed: "Golden Retriever",
    age: "5 years",
    owner: "Sarah Johnson",
    lastVisit: "Jan 15, 2026",
  },
  {
    id: 2,
    name: "Whiskers",
    species: "Cat",
    breed: "Persian",
    age: "3 years",
    owner: "Mike Chen",
    lastVisit: "Jan 20, 2026",
  },
  {
    id: 3,
    name: "Max",
    species: "Dog",
    breed: "German Shepherd",
    age: "7 years",
    owner: "Emily Davis",
    lastVisit: "Dec 28, 2025",
  },
  {
    id: 4,
    name: "Luna",
    species: "Cat",
    breed: "Siamese",
    age: "2 years",
    owner: "James Wilson",
    lastVisit: "Jan 10, 2026",
  },
  {
    id: 5,
    name: "Rocky",
    species: "Dog",
    breed: "Bulldog",
    age: "4 years",
    owner: "Lisa Brown",
    lastVisit: "Jan 5, 2026",
  },
  {
    id: 6,
    name: "Coco",
    species: "Bird",
    breed: "Cockatiel",
    age: "1 year",
    owner: "Anna Martinez",
    lastVisit: "Jan 22, 2026",
  },
];

// Transcript type
type TranscriptMessage = {
  speaker: "ai" | "caller" | "system";
  text: string;
  timestamp: string;
};
type CallWithTranscript = {
  id: number;
  phone: string;
  caller: string;
  duration: string;
  outcome: string;
  sentiment: string;
  time: string;
  aiReceptionist: string;
  transcript: TranscriptMessage[];
};

// Mock call logs data with transcripts
const MOCK_CALLS: CallWithTranscript[] = [
  {
    id: 1,
    phone: "+1 (555) 123-4567",
    caller: "Sarah Johnson",
    duration: "2:22",
    outcome: "Appointment Booked",
    sentiment: "positive",
    time: "12 min ago",
    aiReceptionist: "Megan",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Megan, the virtual receptionist. How can I help you today?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, I'd like to schedule a check-up appointment for my dog.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'd be happy to help with that. May I have your name, please?",
        timestamp: "0:12",
      },
      {
        speaker: "caller",
        text: "Sure, it's Sarah Johnson.",
        timestamp: "0:18",
      },
      {
        speaker: "ai",
        text: "Thank you, Sarah. And what is your dog's name?",
        timestamp: "0:21",
      },
      { speaker: "caller", text: "His name is Buddy.", timestamp: "0:25" },
      {
        speaker: "ai",
        text: "Buddy — what a great name. I've scheduled Buddy's check-up for March 3rd at 10:00 a.m. You'll receive a confirmation shortly.",
        timestamp: "0:28",
      },
      {
        speaker: "caller",
        text: "That's perfect. Thank you!",
        timestamp: "0:45",
      },
      {
        speaker: "ai",
        text: "You're welcome, Sarah. We look forward to seeing you and Buddy soon. Have a great day!",
        timestamp: "0:48",
      },
    ],
  },
  {
    id: 2,
    phone: "+1 (555) 234-5678",
    caller: "Mike Chen",
    duration: "1:38",
    outcome: "Information Provided",
    sentiment: "neutral",
    time: "28 min ago",
    aiReceptionist: "Ashley",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Ashley. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, I'm new to the area and wanted to confirm your hours and location.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "Welcome! We're located at 123 8th Ave in Sarasota. Our hours are Monday through Friday 8am to 5pm.",
        timestamp: "0:15",
      },
      {
        speaker: "caller",
        text: "That's really helpful, thank you.",
        timestamp: "0:30",
      },
      {
        speaker: "ai",
        text: "You're welcome! Would you like me to send you our details by text?",
        timestamp: "0:33",
      },
      {
        speaker: "caller",
        text: "Yes please, that would be great.",
        timestamp: "0:38",
      },
      {
        speaker: "ai",
        text: "Done! Have a great day, Mike.",
        timestamp: "0:42",
      },
    ],
  },
  {
    id: 3,
    phone: "+1 (555) 345-6789",
    caller: "Emily Davis",
    duration: "1:00",
    outcome: "Emergency Transfer",
    sentiment: "negative",
    time: "45 min ago",
    aiReceptionist: "Becky",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Becky. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Oh my god—my dog is vomiting blood. Please help.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'm so sorry. This is a medical emergency. I'm transferring you to our veterinary team right now. Please stay on the line.",
        timestamp: "0:15",
      },
      {
        speaker: "system",
        text: "— Call transferred to live hospital staff —",
        timestamp: "0:58",
      },
    ],
  },
  {
    id: 4,
    phone: "+1 (555) 456-7890",
    caller: "James Wilson",
    duration: "2:36",
    outcome: "Appointment Booked",
    sentiment: "positive",
    time: "1 hr ago",
    aiReceptionist: "Mary",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Mary. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, my dog has been limping and I'd like to schedule an appointment.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'm sorry to hear that. I can help schedule that. What's your dog's name?",
        timestamp: "0:13",
      },
      { speaker: "caller", text: "Luna.", timestamp: "0:20" },
      {
        speaker: "ai",
        text: "I've scheduled Luna's appointment with Dr. Mike for February 26th at 1:30 p.m.",
        timestamp: "0:25",
      },
      { speaker: "caller", text: "Thank you so much!", timestamp: "0:35" },
    ],
  },
  {
    id: 5,
    phone: "+1 (555) 567-8901",
    caller: "Lisa Brown",
    duration: "3:23",
    outcome: "Message Taken",
    sentiment: "neutral",
    time: "1.5 hr ago",
    aiReceptionist: "Emma",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Emma. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, I'm calling to order flea and tick medication for my dog Rocky.",
        timestamp: "0:10",
      },
      {
        speaker: "ai",
        text: "I can help with that. I've noted your request and our staff will prepare it for pickup.",
        timestamp: "0:18",
      },
      { speaker: "caller", text: "Perfect, thank you.", timestamp: "0:30" },
    ],
  },
  {
    id: 6,
    phone: "+1 (555) 678-9012",
    caller: "Anna Martinez",
    duration: "1:10",
    outcome: "Emergency Transfer",
    sentiment: "negative",
    time: "2 hr ago",
    aiReceptionist: "Bethany",
    transcript: [
      {
        speaker: "ai",
        text: "Thank you for calling PawPoint Animal Hospital. This is Bethany. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Please help—my dog was bitten by a rattlesnake!",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "This is a life-threatening emergency. I'm transferring you to Southpaw Emergency Veterinary Hospital now.",
        timestamp: "0:15",
      },
      {
        speaker: "system",
        text: "— Call transferred to Southpaw Emergency Veterinary Hospital —",
        timestamp: "1:05",
      },
    ],
  },
];

// Mock inbox messages (messages left by callers)
const MOCK_INBOX = [
  {
    id: 1,
    caller: "Lisa Brown",
    phone: "+1 (555) 567-8901",
    pet: "Rocky",
    message:
      "Requesting flea and tick medication refill. Will stop by tomorrow to pick up.",
    category: "Medication Request",
    time: "1.5 hr ago",
    status: "unread",
  },
  {
    id: 2,
    caller: "Tom Harris",
    phone: "+1 (555) 789-0123",
    pet: "Bella",
    message:
      "Would like to purchase heartworm prevention medication. Please have it ready for pickup this afternoon.",
    category: "Medication Request",
    time: "3 hr ago",
    status: "unread",
  },
  {
    id: 3,
    caller: "Jennifer Lee",
    phone: "+1 (555) 890-1234",
    pet: "Charlie",
    message:
      "Calling to check if the special diet food for Charlie is in stock. Please call back.",
    category: "Product Inquiry",
    time: "4 hr ago",
    status: "read",
  },
  {
    id: 4,
    caller: "David Kim",
    phone: "+1 (555) 901-2345",
    pet: "Mochi",
    message: "Need to pick up Mochi's prescription. Will be there around 3pm.",
    category: "Medication Pickup",
    time: "5 hr ago",
    status: "read",
  },
  {
    id: 5,
    caller: "Rachel Green",
    phone: "+1 (555) 012-3456",
    pet: "Max",
    message:
      "Interested in purchasing pet insurance information. Please send details via email.",
    category: "General Inquiry",
    time: "Yesterday",
    status: "read",
  },
];

function InboxContent() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">Inbox</h1>
        <p className="text-zinc-600 mt-1">Messages and requests from callers</p>
      </div>

      {/* Stats */}
      <div className="flex gap-4">
        <div className="px-4 py-2 bg-teal-50 rounded-xl">
          <span className="text-sm font-bold text-teal-700">
            {MOCK_INBOX.filter((m) => m.status === "unread").length} Unread
          </span>
        </div>
        <div className="px-4 py-2 bg-zinc-100 rounded-xl">
          <span className="text-sm font-medium text-zinc-600">
            {MOCK_INBOX.length} Total Messages
          </span>
        </div>
      </div>

      {/* Messages list */}
      <div className="space-y-3">
        {MOCK_INBOX.map((msg) => (
          <div
            key={msg.id}
            className={`bg-white rounded-2xl border p-5 shadow-sm transition-all hover:shadow-md ${
              msg.status === "unread"
                ? "border-teal-200 bg-teal-50/30"
                : "border-zinc-200"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-4 flex-1">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.status === "unread" ? "bg-teal-100" : "bg-zinc-100"
                  }`}
                >
                  <Inbox
                    className={`w-6 h-6 ${msg.status === "unread" ? "text-teal-600" : "text-zinc-500"}`}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-zinc-900">{msg.caller}</h3>
                    {msg.status === "unread" && (
                      <span className="w-2 h-2 rounded-full bg-teal-500" />
                    )}
                  </div>
                  <p className="text-sm text-zinc-500 mb-2">
                    {msg.phone} • Pet: {msg.pet}
                  </p>
                  <p className="text-sm text-zinc-700 leading-relaxed">
                    {msg.message}
                  </p>
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-bold mb-2 ${
                    msg.category === "Medication Request"
                      ? "bg-purple-100 text-purple-700"
                      : msg.category === "Medication Pickup"
                        ? "bg-blue-100 text-blue-700"
                        : msg.category === "Product Inquiry"
                          ? "bg-orange-100 text-orange-700"
                          : "bg-zinc-100 text-zinc-700"
                  }`}
                >
                  {msg.category}
                </span>
                <p className="text-xs text-zinc-400">{msg.time}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReportsContent() {
  // Generate call summaries from MOCK_CALLS
  const callSummaries = MOCK_CALLS.map((call) => ({
    id: call.id,
    caller: call.caller,
    duration: call.duration,
    outcome: call.outcome,
    sentiment: call.sentiment,
    time: call.time,
    summary:
      call.outcome === "Appointment Booked"
        ? `${call.caller} called to schedule an appointment. The AI receptionist successfully booked the appointment and sent confirmation.`
        : call.outcome === "Emergency Transfer"
          ? `${call.caller} reported an emergency situation. The call was immediately transferred to veterinary staff for urgent care.`
          : call.outcome === "Information Provided"
            ? `${call.caller} inquired about clinic information. The AI provided details about location, hours, and services.`
            : `${call.caller} left a message for the clinic staff regarding a service request.`,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Reports
        </h1>
        <p className="text-zinc-600 mt-1">
          AI-generated summaries and insights
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl border border-zinc-200 p-5 shadow-sm">
          <p className="text-xs text-zinc-500 font-semibold uppercase tracking-wide mb-1">
            Total Calls
          </p>
          <p className="text-3xl font-black text-zinc-900">
            {MOCK_CALLS.length}
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-zinc-200 p-5 shadow-sm">
          <p className="text-xs text-zinc-500 font-semibold uppercase tracking-wide mb-1">
            Appointments Booked
          </p>
          <p className="text-3xl font-black text-teal-600">
            {
              MOCK_CALLS.filter((c) => c.outcome === "Appointment Booked")
                .length
            }
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-zinc-200 p-5 shadow-sm">
          <p className="text-xs text-zinc-500 font-semibold uppercase tracking-wide mb-1">
            Emergency Transfers
          </p>
          <p className="text-3xl font-black text-red-600">
            {
              MOCK_CALLS.filter((c) => c.outcome === "Emergency Transfer")
                .length
            }
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-zinc-200 p-5 shadow-sm">
          <p className="text-xs text-zinc-500 font-semibold uppercase tracking-wide mb-1">
            Positive Sentiment
          </p>
          <p className="text-3xl font-black text-green-600">
            {MOCK_CALLS.filter((c) => c.sentiment === "positive").length}
          </p>
        </div>
      </div>

      {/* Call Summaries */}
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-zinc-200">
          <h2 className="text-xl font-bold text-zinc-900">Call Summaries</h2>
          <p className="text-sm text-zinc-500 mt-1">
            AI-generated summary for each call
          </p>
        </div>
        <div className="divide-y divide-zinc-100">
          {callSummaries.map((call) => (
            <div
              key={call.id}
              className="p-5 hover:bg-zinc-50 transition-colors"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      call.sentiment === "positive"
                        ? "bg-green-100"
                        : call.sentiment === "negative"
                          ? "bg-red-100"
                          : "bg-yellow-100"
                    }`}
                  >
                    <Phone
                      className={`w-5 h-5 ${
                        call.sentiment === "positive"
                          ? "text-green-600"
                          : call.sentiment === "negative"
                            ? "text-red-600"
                            : "text-yellow-600"
                      }`}
                    />
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-900">{call.caller}</h3>
                    <p className="text-xs text-zinc-500">
                      {call.time} • {call.duration}
                    </p>
                  </div>
                </div>
                <span
                  className={`inline-flex px-3 py-1 rounded-full text-xs font-bold ${
                    call.outcome === "Appointment Booked"
                      ? "bg-teal-100 text-teal-700"
                      : call.outcome === "Emergency Transfer"
                        ? "bg-red-100 text-red-700"
                        : call.outcome === "Information Provided"
                          ? "bg-purple-100 text-purple-700"
                          : "bg-zinc-100 text-zinc-700"
                  }`}
                >
                  {call.outcome}
                </span>
              </div>
              <p className="text-sm text-zinc-600 leading-relaxed pl-13">
                {call.summary}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Demo clinic slug for API calls
const DEMO_CLINIC_SLUG = "demo-clinic";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

function ChatContent() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! Welcome to PawPoint Demo Clinic. I'm your AI assistant. How can I help you and your pet today?",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [userIdentifier] = useState(
    () => `demo_${Date.now()}_${Math.random().toString(36).substring(7)}`,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = inputValue;
    setInputValue("");
    setIsTyping(true);
    setError(null);

    try {
      // Call the streaming chat API
      const response = await fetch(
        `${env.apiUrl}/api/v1/${DEMO_CLINIC_SLUG}/chat/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userInput,
            conversation_id: conversationId,
            user_identifier: userIdentifier,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to connect to AI assistant");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";
      let assistantMessageIndex = -1;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

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
                    const timestamp = new Date().toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    });
                    if (assistantMessageIndex === -1) {
                      assistantMessageIndex = prev.length;
                      return [
                        ...prev,
                        {
                          role: "assistant",
                          content: assistantMessage,
                          timestamp,
                        },
                      ];
                    } else {
                      const newMessages = [...prev];
                      newMessages[assistantMessageIndex] = {
                        ...newMessages[assistantMessageIndex],
                        content: assistantMessage,
                      };
                      return newMessages;
                    }
                  });
                } else if (data.type === "error") {
                  throw new Error(data.message);
                }
              } catch (parseErr) {
                if (parseErr instanceof SyntaxError) continue;
                throw parseErr;
              }
            }
          }
        }
      }
    } catch (err) {
      // Show error when API fails
      console.error("Chat API error:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect to AI assistant",
      );
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-[calc(100vh-180px)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">Chat</h1>
        <p className="text-zinc-600 mt-1">Try the AI chatbot assistant</p>
      </div>

      {/* Chat container */}
      <div className="flex-1 bg-white rounded-2xl border border-zinc-200 shadow-sm overflow-hidden flex flex-col">
        {/* Chat header */}
        <div className="px-6 py-4 border-b border-zinc-200 bg-gradient-to-r from-teal-50 to-teal-100/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] rounded-xl flex items-center justify-center shadow-md">
              <PawPrint className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-zinc-900">PawPoint AI Assistant</h2>
              <p className="text-xs text-zinc-500 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                Online - Demo Mode
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-zinc-50">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex flex-col max-w-[75%] ${msg.role === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`px-4 py-3 rounded-3xl ${
                    msg.role === "user"
                      ? "bg-teal-600 text-white rounded-tr-md"
                      : "bg-white border border-zinc-200 text-zinc-800 rounded-tl-md"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
                <span className="text-xs text-zinc-400 mt-1 px-1">
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-zinc-200 rounded-3xl rounded-tl-md px-4 py-3">
                <div className="flex items-center gap-1.5">
                  <div
                    className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  />
                  <div
                    className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Error message */}
        {error && (
          <div className="px-4 py-3 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-zinc-200 bg-white">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type your message... (try: appointment, hours, services)"
              className="flex-1 px-4 py-3 bg-white border border-zinc-300 rounded-xl text-sm text-zinc-900 placeholder:text-zinc-400 focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none"
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim()}
              className="px-6 py-3 bg-[#3EB5B0] hover:bg-[#2A8A86] disabled:bg-zinc-300 disabled:cursor-not-allowed text-white rounded-xl font-semibold transition-colors shadow-md"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-zinc-400 mt-2 text-center">
            This is a demo chatbot. Try asking about appointments, hours,
            services, or location.
          </p>
        </div>
      </div>
    </div>
  );
}

function AppointmentsContent() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Appointments
        </h1>
        <p className="text-zinc-600 mt-1">
          Manage incoming appointment requests from callers
        </p>
      </div>
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-zinc-50 border-b border-zinc-200">
            <tr>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Pet
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Owner
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Type
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Requested Date
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {MOCK_APPOINTMENTS.map((apt) => (
              <tr key={apt.id} className="hover:bg-zinc-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-teal-100 flex items-center justify-center">
                      <PawPrint className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-zinc-900">
                        {apt.petName}
                      </p>
                      <p className="text-xs text-zinc-500">{apt.species}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <p className="font-medium text-zinc-900">{apt.ownerName}</p>
                  <p className="text-xs text-zinc-500">{apt.phone}</p>
                </td>
                <td className="px-6 py-4 text-zinc-700">{apt.type}</td>
                <td className="px-6 py-4 text-zinc-700">{apt.requestedDate}</td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex px-3 py-1 rounded-full text-xs font-bold ${
                      apt.status === "confirmed"
                        ? "bg-green-100 text-green-700"
                        : apt.status === "pending"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                    }`}
                  >
                    {apt.status.charAt(0).toUpperCase() + apt.status.slice(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PatientsContent() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Patients
        </h1>
        <p className="text-zinc-600 mt-1">View and manage patient records</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {MOCK_PATIENTS.map((patient) => (
          <div
            key={patient.id}
            className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-teal-100 to-teal-200 flex items-center justify-center flex-shrink-0">
                <PawPrint className="w-7 h-7 text-teal-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-lg text-zinc-900">
                  {patient.name}
                </h3>
                <p className="text-sm text-zinc-600">{patient.breed}</p>
                <div className="mt-3 space-y-1">
                  <p className="text-xs text-zinc-500">
                    <span className="font-semibold">Species:</span>{" "}
                    {patient.species}
                  </p>
                  <p className="text-xs text-zinc-500">
                    <span className="font-semibold">Age:</span> {patient.age}
                  </p>
                  <p className="text-xs text-zinc-500">
                    <span className="font-semibold">Owner:</span>{" "}
                    {patient.owner}
                  </p>
                  <p className="text-xs text-zinc-500">
                    <span className="font-semibold">Last Visit:</span>{" "}
                    {patient.lastVisit}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CallsContent() {
  const [selectedCall, setSelectedCall] = useState<CallWithTranscript | null>(
    null,
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Call Log
        </h1>
        <p className="text-zinc-600 mt-1">
          Recent calls handled by PawPoint AI
        </p>
      </div>
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-zinc-50 border-b border-zinc-200">
            <tr>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Caller
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Duration
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Outcome
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Sentiment
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Time
              </th>
              <th className="text-left px-6 py-4 text-xs font-bold text-zinc-600 uppercase tracking-wide">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {MOCK_CALLS.map((call) => (
              <tr key={call.id} className="hover:bg-zinc-50 transition-colors">
                <td className="px-6 py-4">
                  <p className="font-semibold text-zinc-900">{call.caller}</p>
                  <p className="text-xs text-zinc-500">{call.phone}</p>
                </td>
                <td className="px-6 py-4 text-zinc-700 font-mono">
                  {call.duration}
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex px-3 py-1 rounded-full text-xs font-bold ${
                      call.outcome === "Appointment Booked"
                        ? "bg-teal-100 text-teal-700"
                        : call.outcome === "Emergency Transfer"
                          ? "bg-red-100 text-red-700"
                          : "bg-zinc-100 text-zinc-700"
                    }`}
                  >
                    {call.outcome}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex items-center gap-1.5 text-sm font-medium ${
                      call.sentiment === "positive"
                        ? "text-green-600"
                        : call.sentiment === "negative"
                          ? "text-red-600"
                          : "text-yellow-600"
                    }`}
                  >
                    <span
                      className={`w-2 h-2 rounded-full ${
                        call.sentiment === "positive"
                          ? "bg-green-500"
                          : call.sentiment === "negative"
                            ? "bg-red-500"
                            : "bg-yellow-500"
                      }`}
                    />
                    {call.sentiment.charAt(0).toUpperCase() +
                      call.sentiment.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 text-zinc-500 text-sm">{call.time}</td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => setSelectedCall(call)}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg text-xs font-medium transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    View Transcript
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Transcript Modal */}
      {selectedCall && (
        <div
          className="fixed inset-0 bg-black/50 flex items-start justify-center z-[100] pt-32 pb-4 px-4"
          onClick={() => setSelectedCall(null)}
        >
          <div
            className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[75vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-zinc-200 bg-gradient-to-r from-teal-50 to-teal-100/50 rounded-t-3xl">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-teal-600 rounded-xl shadow-sm">
                  <Phone className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-zinc-900">
                    Call Transcript
                  </h2>
                  <p className="text-sm text-zinc-600">
                    AI Receptionist ({selectedCall.aiReceptionist}) ↔{" "}
                    {selectedCall.caller}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCall(null)}
                className="p-2 hover:bg-white/60 rounded-xl transition-colors"
              >
                <X className="w-5 h-5 text-zinc-600" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-zinc-50">
              {selectedCall.transcript.map((message, index) => {
                if (message.speaker === "system") {
                  return (
                    <div key={index} className="flex justify-center my-6">
                      <div className="flex flex-col items-center max-w-md">
                        <div className="px-6 py-3 bg-red-50 border-2 border-red-200 rounded-2xl">
                          <p className="text-sm font-semibold text-red-700 text-center">
                            {message.text}
                          </p>
                        </div>
                        <span className="text-xs text-zinc-400 mt-1 font-mono">
                          {message.timestamp}
                        </span>
                      </div>
                    </div>
                  );
                }
                return (
                  <div
                    key={index}
                    className={`flex ${message.speaker === "ai" ? "justify-start" : "justify-end"}`}
                  >
                    <div
                      className={`flex flex-col max-w-[75%] ${message.speaker === "ai" ? "items-start" : "items-end"}`}
                    >
                      {(index === 0 ||
                        selectedCall.transcript[index - 1]?.speaker !==
                          message.speaker) && (
                        <span className="text-xs font-semibold text-zinc-500 mb-1 px-1">
                          {message.speaker === "ai"
                            ? selectedCall.aiReceptionist
                            : selectedCall.caller.split(" ")[0]}
                        </span>
                      )}
                      <div
                        className={`px-4 py-3 rounded-3xl ${
                          message.speaker === "ai"
                            ? "bg-white border border-zinc-200 text-zinc-800 rounded-tl-md"
                            : "bg-teal-600 text-white rounded-tr-md"
                        }`}
                      >
                        <p className="text-sm leading-relaxed">
                          {message.text}
                        </p>
                      </div>
                      <span className="text-xs text-zinc-400 mt-1 px-1 font-mono">
                        {message.timestamp}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-zinc-200 bg-white rounded-b-3xl">
              <div className="flex items-center justify-between">
                <div className="text-sm text-zinc-500">
                  Duration:{" "}
                  <span className="font-mono font-semibold">
                    {selectedCall.duration}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedCall(null)}
                  className="px-6 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-medium transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SettingsContent() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Settings
        </h1>
        <p className="text-zinc-600 mt-1">
          Configure your PawPoint AI assistant
        </p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-zinc-900 mb-4">
            AI Configuration
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-2">
                Greeting Message
              </label>
              <textarea
                className="w-full px-4 py-3 border border-zinc-300 rounded-xl text-sm resize-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                rows={3}
                defaultValue="Hi! Thanks for calling Demo Clinic. How can I help you and your pet today?"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-2">
                Clinic Hours
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-zinc-300 rounded-xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                defaultValue="Mon-Fri 8AM-6PM, Sat 9AM-2PM"
                readOnly
              />
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-zinc-900">Emergency Detection</p>
                <p className="text-xs text-zinc-500">
                  Auto-transfer urgent calls to staff
                </p>
              </div>
              <div className="w-12 h-7 bg-teal-500 rounded-full relative cursor-pointer">
                <div className="w-5 h-5 bg-white rounded-full absolute right-1 top-1 shadow-sm" />
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-zinc-900 mb-4">
            Notifications
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-zinc-100">
              <div>
                <p className="font-medium text-zinc-900">Email Notifications</p>
                <p className="text-xs text-zinc-500">
                  Get email for new appointments
                </p>
              </div>
              <div className="w-12 h-7 bg-teal-500 rounded-full relative cursor-pointer">
                <div className="w-5 h-5 bg-white rounded-full absolute right-1 top-1 shadow-sm" />
              </div>
            </div>
            <div className="flex items-center justify-between py-3 border-b border-zinc-100">
              <div>
                <p className="font-medium text-zinc-900">SMS Alerts</p>
                <p className="text-xs text-zinc-500">
                  Text alerts for emergencies
                </p>
              </div>
              <div className="w-12 h-7 bg-teal-500 rounded-full relative cursor-pointer">
                <div className="w-5 h-5 bg-white rounded-full absolute right-1 top-1 shadow-sm" />
              </div>
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-zinc-900">Daily Summary</p>
                <p className="text-xs text-zinc-500">
                  Receive daily call reports
                </p>
              </div>
              <div className="w-12 h-7 bg-zinc-300 rounded-full relative cursor-pointer">
                <div className="w-5 h-5 bg-white rounded-full absolute left-1 top-1 shadow-sm" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Demo sidebar with clickable navigation
function DemoSidebar({
  activeTab,
  onTabChange,
}: {
  activeTab: DemoTab;
  onTabChange: (tab: DemoTab) => void;
}) {
  const navSections = [
    {
      title: null,
      items: [
        { id: "dashboard" as DemoTab, label: "Home", icon: LayoutDashboard },
        { id: "inbox" as DemoTab, label: "Inbox", icon: Inbox },
      ],
    },
    {
      title: "APPLICATIONS",
      items: [
        {
          id: "appointments" as DemoTab,
          label: "Appointments",
          icon: Calendar,
        },
        { id: "patients" as DemoTab, label: "Patients", icon: PawPrint },
        { id: "calls" as DemoTab, label: "Call Log", icon: Phone },
        { id: "chat" as DemoTab, label: "Chat", icon: MessageCircle },
      ],
    },
    {
      title: "OTHERS",
      items: [
        { id: "reports" as DemoTab, label: "Reports", icon: FileText },
        { id: null, label: "Widgets", icon: LayoutGrid, disabled: true },
      ],
    },
    {
      title: "SUPPORT",
      items: [
        { id: "settings" as DemoTab, label: "Settings", icon: Settings },
        { id: null, label: "Security", icon: Shield, disabled: true },
        { id: null, label: "Help", icon: HelpCircle, disabled: true },
      ],
    },
  ];

  return (
    <aside className="fixed left-0 top-0 w-[280px] h-screen z-20 flex flex-col overflow-hidden">
      {/* Glassmorphism background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#E8F5F4]/95 via-[#F0F9F8]/90 to-[#E3F2F1]/95 backdrop-blur-xl" />

      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 -left-10 w-40 h-40 bg-[#A8DCD9]/20 rounded-full blur-3xl" />
        <div className="absolute bottom-40 -right-10 w-32 h-32 bg-[#3EB5B0]/15 rounded-full blur-2xl" />
        <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-[#FF8A65]/10 rounded-full blur-2xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Logo header */}
        <div className="px-6 pt-6 pb-5">
          <div className="flex items-center gap-3 px-4 py-3 bg-white/50 backdrop-blur-md rounded-2xl border border-white/60 shadow-sm">
            <div className="w-9 h-9 bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] rounded-xl flex items-center justify-center shadow-md">
              <PawPrint className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-[#1D3533] truncate">
                Demo Clinic
              </p>
              <p className="text-xs text-[#1D3533]/50">Veterinary Clinic</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 overflow-y-auto">
          {navSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="mb-6">
              {section.title && (
                <div className="px-4 mb-3">
                  <p className="text-[10px] font-semibold text-[#1D3533]/40 tracking-wider uppercase">
                    {section.title}
                  </p>
                </div>
              )}
              <div className="space-y-1">
                {section.items.map((item, itemIndex) => {
                  const isActive = item.id === activeTab;
                  const isDisabled = item.disabled || !item.id;

                  return (
                    <button
                      key={itemIndex}
                      onClick={() => item.id && onTabChange(item.id)}
                      disabled={isDisabled}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-left ${
                        isActive
                          ? "bg-white/70 backdrop-blur-sm shadow-sm border border-white/80"
                          : isDisabled
                            ? "opacity-40 cursor-not-allowed"
                            : "hover:bg-white/50 hover:backdrop-blur-sm cursor-pointer"
                      }`}
                    >
                      <div
                        className={`p-2 rounded-xl shrink-0 transition-all ${
                          isActive
                            ? "bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] text-white shadow-md shadow-[#3EB5B0]/20"
                            : "bg-white/40 text-[#3EB5B0]"
                        }`}
                      >
                        <item.icon className="w-4 h-4" strokeWidth={2.5} />
                      </div>
                      <span
                        className={`text-[13px] font-medium ${isActive ? "text-[#1D3533]" : "text-[#1D3533]/70"}`}
                      >
                        {item.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="p-4 border-t border-white/30">
          <div className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all bg-white/40 hover:bg-white/60 backdrop-blur-sm border border-white/50 opacity-50 cursor-not-allowed">
            <div className="p-2 rounded-xl shrink-0 bg-gradient-to-br from-[#FF8A65] to-[#FF6E40] text-white shadow-sm">
              <LogOut className="w-4 h-4" strokeWidth={2.5} />
            </div>
            <span className="text-[13px] font-medium text-[#1D3533]/70">
              Log Out
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState<DemoTab>("dashboard");

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardContent analytics={MOCK_ANALYTICS} loading={false} />;
      case "inbox":
        return <InboxContent />;
      case "appointments":
        return <AppointmentsContent />;
      case "patients":
        return <PatientsContent />;
      case "calls":
        return <CallsContent />;
      case "chat":
        return <ChatContent />;
      case "reports":
        return <ReportsContent />;
      case "settings":
        return <SettingsContent />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-[#F5F8F8] via-[#FAFCFC] to-[#F0F6F6]">
      {/* Sidebar with clickable tabs */}
      <DemoSidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main content */}
      <main className="flex-1 ml-[280px] p-8 relative z-10">
        {/* Top bar with homepage link and demo badge */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-orange-100 text-orange-700 text-sm font-bold rounded-full">
              Demo Mode
            </div>
            <span className="text-sm text-zinc-500">
              This is a demo with sample data
            </span>
          </div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-zinc-200 hover:bg-zinc-50 text-zinc-700 rounded-xl text-sm font-medium transition-colors shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Homepage
          </Link>
        </div>

        {renderContent()}
      </main>
    </div>
  );
}
