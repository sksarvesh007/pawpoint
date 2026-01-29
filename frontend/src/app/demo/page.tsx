/**
 * Demo dashboard page with mock data.
 * No authentication required - public showcase.
 */

"use client";

import { useState } from "react";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { MOCK_ANALYTICS } from "@/components/dashboard/mockData";
import { Navbar } from "@/components/Navbar";
import { NAVBAR_HEIGHT } from "@/components/Logo";
import {
  LayoutDashboard,
  Calendar,
  PawPrint,
  Phone,
  Settings,
} from "lucide-react";

type DemoTab = "dashboard" | "appointments" | "patients" | "calls" | "settings";

const navItems = [
  { id: "dashboard" as DemoTab, label: "Dashboard", icon: LayoutDashboard },
  {
    id: "appointments" as DemoTab,
    label: "Appointment Requests",
    icon: Calendar,
  },
  { id: "patients" as DemoTab, label: "Patients", icon: PawPrint },
  { id: "calls" as DemoTab, label: "Call Log", icon: Phone },
  { id: "settings" as DemoTab, label: "Settings", icon: Settings },
];

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

// Mock call logs data
const MOCK_CALLS = [
  {
    id: 1,
    phone: "+1 (555) 123-4567",
    caller: "Sarah Johnson",
    duration: "2:22",
    outcome: "Appointment Booked",
    sentiment: "positive",
    time: "12 min ago",
  },
  {
    id: 2,
    phone: "+1 (555) 234-5678",
    caller: "Mike Chen",
    duration: "1:38",
    outcome: "Information Provided",
    sentiment: "neutral",
    time: "28 min ago",
  },
  {
    id: 3,
    phone: "+1 (555) 345-6789",
    caller: "Emily Davis",
    duration: "5:12",
    outcome: "Emergency Transfer",
    sentiment: "negative",
    time: "45 min ago",
  },
  {
    id: 4,
    phone: "+1 (555) 456-7890",
    caller: "James Wilson",
    duration: "2:36",
    outcome: "Appointment Booked",
    sentiment: "positive",
    time: "1 hr ago",
  },
  {
    id: 5,
    phone: "+1 (555) 567-8901",
    caller: "Lisa Brown",
    duration: "3:23",
    outcome: "Message Taken",
    sentiment: "neutral",
    time: "1.5 hr ago",
  },
];

function AppointmentsContent() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Appointment Requests
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
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
        {/* AI Configuration */}
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

        {/* Notification Settings */}
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

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState<DemoTab>("dashboard");

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardContent analytics={MOCK_ANALYTICS} loading={false} />;
      case "appointments":
        return <AppointmentsContent />;
      case "patients":
        return <PatientsContent />;
      case "calls":
        return <CallsContent />;
      case "settings":
        return <SettingsContent />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFA]">
      {/* Top Navbar */}
      <Navbar />

      <div className="flex">
        {/* Sidebar */}
        <aside
          className="fixed left-0 w-64 bg-gradient-to-b from-[#A8DCD9] via-[#B4E2DF] to-[#C5E8E6] z-20 flex flex-col overflow-hidden"
          style={{
            top: `${NAVBAR_HEIGHT}px`,
            height: `calc(100vh - ${NAVBAR_HEIGHT}px)`,
          }}
        >
          {/* Wave patterns - subtle background */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
            <svg
              className="absolute top-0 left-0 w-full"
              height="200"
              viewBox="0 0 300 200"
              preserveAspectRatio="none"
            >
              <path
                d="M 0,100 C 75,80 150,120 225,100 L 300,100 L 300,0 L 0,0 Z"
                fill="url(#sidebarWave1)"
              />
              <defs>
                <linearGradient
                  id="sidebarWave1"
                  x1="0%"
                  y1="0%"
                  x2="0%"
                  y2="100%"
                >
                  <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.1" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* Content */}
          <div className="relative z-10 flex flex-col h-full">
            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
              {navItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-left ${
                      isActive
                        ? "bg-white/90 text-[#1D3533] font-semibold shadow-sm"
                        : "text-[#1D3533]/80 hover:bg-white/40 hover:text-[#1D3533]"
                    }`}
                  >
                    <div
                      className={`p-2 rounded-lg shrink-0 ${
                        isActive
                          ? "bg-[#3EB5B0] text-white"
                          : "bg-white/60 text-[#3EB5B0]"
                      }`}
                    >
                      <item.icon className="w-5 h-5" />
                    </div>
                    <span className="text-sm">{item.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Bottom section - clinic info */}
            <div className="p-4 border-t border-white/20">
              <div className="px-4 py-3 bg-white/60 backdrop-blur-sm rounded-xl">
                <p className="text-xs text-[#1D3533]/60 uppercase tracking-wide mb-1 font-medium">
                  Clinic
                </p>
                <p className="text-sm font-bold text-[#1D3533] truncate">
                  Demo Clinic
                </p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 ml-64 p-8 relative z-10">
          {/* Demo mode badge */}
          <div className="mb-6 flex items-center gap-3">
            <div className="px-4 py-2 bg-orange-100 text-orange-700 text-sm font-bold rounded-full">
              Demo Mode
            </div>
            <span className="text-sm text-zinc-500">
              This is a demo with sample data
            </span>
          </div>

          {renderContent()}
        </main>
      </div>
    </div>
  );
}
