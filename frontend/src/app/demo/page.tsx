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
  FileText,
  X,
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

// Structured transcript format
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
  aiReceptionist?: string;
  transcript?: TranscriptMessage[];
};

// Mock call logs data
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
      {
        speaker: "caller",
        text: "His name is Buddy.",
        timestamp: "0:25",
      },
      {
        speaker: "ai",
        text: "Buddy — what a great name. And this visit is for a routine check-up, correct?",
        timestamp: "0:28",
      },
      {
        speaker: "caller",
        text: "Yes, just a regular check-up.",
        timestamp: "0:35",
      },
      {
        speaker: "ai",
        text: "Perfect. Do you have a preferred date and time for Buddy's appointment?",
        timestamp: "0:38",
      },
      {
        speaker: "caller",
        text: "Yes, I was hoping for March 3rd at 10:00 a.m.",
        timestamp: "0:45",
      },
      {
        speaker: "ai",
        text: "Let me check on that for you… Great news — March 3rd at 10:00 a.m. is available.",
        timestamp: "0:51",
      },
      {
        speaker: "caller",
        text: "That's perfect.",
        timestamp: "1:00",
      },
      {
        speaker: "ai",
        text: "Wonderful. I've scheduled Buddy's check-up for March 3rd at 10:00 a.m. at PawPoint Animal Hospital. Before we finish, I can send you a confirmation by text message and email. Would you like me to do that?",
        timestamp: "1:03",
      },
      {
        speaker: "caller",
        text: "Yes, that would be great.",
        timestamp: "1:18",
      },
      {
        speaker: "ai",
        text: "Perfect. I've just sent a confirmation text message and email with Buddy's appointment details. You'll also receive reminders as the appointment gets closer.",
        timestamp: "1:21",
      },
      {
        speaker: "caller",
        text: "Awesome, thank you.",
        timestamp: "1:34",
      },
      {
        speaker: "ai",
        text: "You're very welcome, Sarah. If you need to make any changes or have questions before your visit, just give us a call. We look forward to seeing you and Buddy soon. Have a great day!",
        timestamp: "1:37",
      },
      {
        speaker: "caller",
        text: "You too. Goodbye.",
        timestamp: "1:52",
      },
      {
        speaker: "ai",
        text: "Goodbye!",
        timestamp: "1:55",
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
        text: "Thank you for calling PawPoint Animal Hospital. This is Ashley, the virtual receptionist. How can I help you today?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, I'm new to the area and just wanted to confirm your business hours and location.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "Welcome to the area — I'd be happy to help with that. Before we continue, may I have your name?",
        timestamp: "0:15",
      },
      {
        speaker: "caller",
        text: "Sure, it's Mike Chen.",
        timestamp: "0:22",
      },
      {
        speaker: "ai",
        text: "Thank you, Mike. And do you have a pet you'll be bringing in?",
        timestamp: "0:25",
      },
      {
        speaker: "caller",
        text: "Yes, I have a cat named Whiskers.",
        timestamp: "0:30",
      },
      {
        speaker: "ai",
        text: "Whiskers — that's a great name. Here are our details: PawPoint Animal Hospital is located at 123 8th Ave in Sarasota, Florida. Our regular business hours are Monday through Friday from 8am to 5pm, with lunch from 12pm to 1pm daily. We are closed on Saturday and Sunday. If you ever need help outside of those hours, our phone system can still assist with general information and appointment requests.",
        timestamp: "0:35",
      },
      {
        speaker: "caller",
        text: "That's really helpful, thank you.",
        timestamp: "0:55",
      },
      {
        speaker: "ai",
        text: "You're very welcome. Would you like me to send you our hours and location by text message or email for easy reference?",
        timestamp: "0:58",
      },
      {
        speaker: "caller",
        text: "Yes, that would be great.",
        timestamp: "1:05",
      },
      {
        speaker: "ai",
        text: "Great! May I have your email address?",
        timestamp: "1:08",
      },
      {
        speaker: "caller",
        text: "Sure, it's mikechen@email.com",
        timestamp: "1:12",
      },
      {
        speaker: "ai",
        text: "Perfect — I've just sent you a text message and email with our address, hours, and contact information. If you'd like, I can also help you schedule an appointment for Whiskers or answer any other questions you may have.",
        timestamp: "1:15",
      },
      {
        speaker: "caller",
        text: "I'll do that another time, but thanks again.",
        timestamp: "1:28",
      },
      {
        speaker: "ai",
        text: "Of course, Mike. We're happy to have you in the area and look forward to meeting you and Whiskers whenever you're ready. Have a great day!",
        timestamp: "1:32",
      },
      {
        speaker: "caller",
        text: "You too. Goodbye.",
        timestamp: "1:36",
      },
      {
        speaker: "ai",
        text: "Goodbye!",
        timestamp: "1:38",
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
        text: "Thank you for calling PawPoint Animal Hospital. This is Becky, the virtual receptionist. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Oh my god—my dog is vomiting blood. I don't know what to do. Please help.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'm so sorry this is happening, Emily. Just to confirm, your dog is actively vomiting blood, correct?",
        timestamp: "0:15",
      },
      {
        speaker: "caller",
        text: "Yes—he's thrown up blood twice already.",
        timestamp: "0:22",
      },
      {
        speaker: "ai",
        text: "Thank you for telling me. Based on what you've described, this is a medical emergency and your dog needs immediate attention. I'm going to transfer you right now to a live member of our veterinary team so they can assist you. Please stay on the line.",
        timestamp: "0:26",
      },
      {
        speaker: "caller",
        text: "Okay—please hurry.",
        timestamp: "0:42",
      },
      {
        speaker: "ai",
        text: "I'm transferring your call now. If for any reason the call disconnects, please come directly to PawPoint Animal Hospital or proceed to the nearest emergency veterinary clinic right away. One moment while I connect you.",
        timestamp: "0:45",
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
        text: "Thank you for calling PawPoint Animal Hospital. This is Mary, the virtual receptionist. How can I help you today?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, my dog has been limping, and I'd like to schedule an appointment.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'm sorry to hear that your pet isn't feeling well, James. I'll help get that scheduled for you. May I have your full name, please?",
        timestamp: "0:13",
      },
      {
        speaker: "caller",
        text: "Sure, it's James Wilson.",
        timestamp: "0:20",
      },
      {
        speaker: "ai",
        text: "Thank you, James. And your dog's name is Luna, correct?",
        timestamp: "0:23",
      },
      {
        speaker: "caller",
        text: "Yes, that's right.",
        timestamp: "0:28",
      },
      {
        speaker: "ai",
        text: "Thank you. You mentioned Luna is limping — is she eating and drinking normally otherwise?",
        timestamp: "0:30",
      },
      {
        speaker: "caller",
        text: "Yes, everything else seems normal.",
        timestamp: "0:37",
      },
      {
        speaker: "ai",
        text: "Okay, thank you for letting me know. Do you have a preferred doctor, date, or time?",
        timestamp: "0:40",
      },
      {
        speaker: "caller",
        text: "Yes, I'd like to see Dr. Mike on February 27th at 1:30 p.m. If that's not available, my second choice would be February 26th at 1:30 p.m.",
        timestamp: "0:46",
      },
      {
        speaker: "ai",
        text: "Thank you for providing a backup option — let me check availability for you. Unfortunately, Dr. Mike is not available on February 27th at 1:30 p.m. However, I do have availability with Dr. Mike on February 26th at 1:30 p.m. Would that work for you?",
        timestamp: "0:58",
      },
      {
        speaker: "caller",
        text: "Yes, that works.",
        timestamp: "1:15",
      },
      {
        speaker: "ai",
        text: "Great. I've scheduled Luna's appointment with Dr. Mike for February 26th at 1:30 p.m. at PawPoint Animal Hospital. Before I send your appointment reminders, I just want to confirm your contact information. Is your phone number 850-555-4321?",
        timestamp: "1:18",
      },
      {
        speaker: "caller",
        text: "Yes, that's correct.",
        timestamp: "1:35",
      },
      {
        speaker: "ai",
        text: "And your email address is james@ppihospital.com?",
        timestamp: "1:38",
      },
      {
        speaker: "caller",
        text: "Yes, that's right.",
        timestamp: "1:43",
      },
      {
        speaker: "ai",
        text: "Perfect. I've sent your appointment confirmation and reminders by text message and email. If Luna's limping worsens or she has trouble putting weight on her leg before the appointment, please give us a call right away.",
        timestamp: "1:46",
      },
      {
        speaker: "caller",
        text: "I will. Thank you for your help.",
        timestamp: "2:05",
      },
      {
        speaker: "ai",
        text: "You're very welcome, James. We look forward to seeing you and Luna on February 26th at 1:30 p.m. Have a great day!",
        timestamp: "2:08",
      },
      {
        speaker: "caller",
        text: "You too. Goodbye.",
        timestamp: "2:25",
      },
      {
        speaker: "ai",
        text: "Goodbye!",
        timestamp: "2:28",
      },
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
        text: "Thank you for calling PawPoint Animal Hospital. This is Emma, the virtual receptionist. How can I help you today?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Hi, I'm calling to order flea and tick medication for my dog.",
        timestamp: "0:10",
      },
      {
        speaker: "ai",
        text: "I can help with that. May I have your name, please?",
        timestamp: "0:18",
      },
      {
        speaker: "caller",
        text: "It's Lisa Brown.",
        timestamp: "0:25",
      },
      {
        speaker: "ai",
        text: "Thank you, Lisa. And your dog's name?",
        timestamp: "0:28",
      },
      {
        speaker: "caller",
        text: "Rocky.",
        timestamp: "0:35",
      },
      {
        speaker: "ai",
        text: "Got it — Rocky. I've noted your request for flea and tick medication. I'll forward this request to our medical staff so they can prepare the medication for you.",
        timestamp: "0:38",
      },
      {
        speaker: "caller",
        text: "Okay, great.",
        timestamp: "0:55",
      },
      {
        speaker: "ai",
        text: "Once it's ready, you can stop by the office during our regular business hours to pick it up and take care of payment at that time. If the staff has any questions or needs approval from the doctor before dispensing the medication, they'll reach out to you directly.",
        timestamp: "1:00",
      },
      {
        speaker: "caller",
        text: "Perfect, thank you.",
        timestamp: "1:30",
      },
      {
        speaker: "ai",
        text: "You're very welcome, Lisa. We'll see you soon, and please don't hesitate to call if you have any other questions. Have a great day!",
        timestamp: "1:35",
      },
      {
        speaker: "caller",
        text: "You too. Goodbye.",
        timestamp: "3:10",
      },
      {
        speaker: "ai",
        text: "Goodbye!",
        timestamp: "3:15",
      },
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
        text: "Thank you for calling PawPoint Animal Hospital. This is Bethany, the virtual receptionist. How can I help you?",
        timestamp: "0:00",
      },
      {
        speaker: "caller",
        text: "Please help—my dog was bitten by a rattlesnake. I don't know what to do.",
        timestamp: "0:08",
      },
      {
        speaker: "ai",
        text: "I'm so sorry this is happening, Anna. Just to confirm, your dog was bitten by a rattlesnake, correct?",
        timestamp: "0:15",
      },
      {
        speaker: "caller",
        text: "Yes—her name is Coco. She was bitten on the leg and it's already swelling.",
        timestamp: "0:22",
      },
      {
        speaker: "ai",
        text: "Thank you for telling me, Anna. Based on what you've described, this is a life-threatening medical emergency and Coco needs immediate treatment. Because you're calling after hours, PawPoint Animal Hospital is currently closed. I'm going to transfer your call right now to the emergency hospital designated by our medical team: Southpaw Emergency Veterinary Hospital. Please stay on the line while I connect you. If the call disconnects for any reason, go immediately to Southpaw Emergency Veterinary Hospital or the nearest emergency veterinary clinic.",
        timestamp: "0:30",
      },
      {
        speaker: "caller",
        text: "Okay—please hurry.",
        timestamp: "0:55",
      },
      {
        speaker: "ai",
        text: "I understand, Anna. I'm transferring you now.",
        timestamp: "0:58",
      },
      {
        speaker: "system",
        text: "— Call transferred to Southpaw Emergency Veterinary Hospital —",
        timestamp: "1:05",
      },
    ],
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
                  {call.transcript ? (
                    <button
                      onClick={() => setSelectedCall(call)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg text-xs font-medium transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      View Transcript
                    </button>
                  ) : (
                    <span className="text-xs text-zinc-400">No transcript</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Transcript Modal - Chat Interface */}
      {selectedCall && selectedCall.transcript && (
        <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-[100] pt-32 pb-4 px-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[75vh] flex flex-col">
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
                // System message (e.g., call transfer)
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

                // Regular AI or caller messages
                return (
                  <div
                    key={index}
                    className={`flex ${message.speaker === "ai" ? "justify-start" : "justify-end"}`}
                  >
                    <div
                      className={`flex flex-col max-w-[75%] ${message.speaker === "ai" ? "items-start" : "items-end"}`}
                    >
                      {/* Speaker label - only for first message or speaker change */}
                      {(index === 0 ||
                        selectedCall.transcript?.[index - 1]?.speaker !==
                          message.speaker) && (
                        <span className="text-xs font-semibold text-zinc-500 mb-1 px-1">
                          {message.speaker === "ai"
                            ? selectedCall.aiReceptionist
                            : selectedCall.caller.split(" ")[0]}
                        </span>
                      )}

                      {/* Message bubble */}
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

                      {/* Timestamp */}
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
