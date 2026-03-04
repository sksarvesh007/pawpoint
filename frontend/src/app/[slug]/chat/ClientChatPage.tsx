"use client";

import { useState } from "react";
import Chatbot from "@/components/Chatbot";
import type { ClinicPublicInfo } from "@/types/chat";

interface ClientChatPageProps {
  slug: string;
  clinicInfo: ClinicPublicInfo;
}

/**
 * Get or create a unique user identifier for anonymous users
 */
function getOrCreateUserIdentifier(slug: string): string {
  if (typeof window === "undefined") {
    return "";
  }

  const storageKey = `pawpoint_user_${slug}`;
  let identifier = localStorage.getItem(storageKey);

  if (!identifier) {
    identifier = `anon_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem(storageKey, identifier);
  }

  return identifier;
}

/**
 * Client component for the public chatbot page
 * Generates a unique user identifier for anonymous users
 */
export default function ClientChatPage({
  slug,
  clinicInfo,
}: ClientChatPageProps) {
  // Initialize state lazily to avoid useEffect + setState pattern
  const [userIdentifier] = useState(() => getOrCreateUserIdentifier(slug));

  // Don't render until we have a user identifier
  if (!userIdentifier) {
    return (
      <div className="flex h-screen items-center justify-center bg-white relative overflow-hidden">
        {/* Background Waves */}
        <div className="absolute inset-0 pointer-events-none">
          <svg
            className="absolute top-0 left-0 w-full h-full"
            viewBox="0 0 1440 900"
            preserveAspectRatio="xMidYMid slice"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="loadingWave1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#2A9D8F" stopOpacity="0.15" />
                <stop offset="50%" stopColor="#3DA99F" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.15" />
              </linearGradient>
              <linearGradient id="loadingWave2" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.1" />
                <stop offset="50%" stopColor="#2A9D8F" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#3DA99F" stopOpacity="0.1" />
              </linearGradient>
            </defs>
            <path
              d="M-100,550 C200,700 400,350 720,450 C1040,550 1200,300 1540,400 L1540,900 L-100,900 Z"
              fill="url(#loadingWave1)"
            />
            <path
              d="M-100,650 C200,500 500,700 800,550 C1100,400 1300,650 1540,500 L1540,900 L-100,900 Z"
              fill="url(#loadingWave2)"
            />
          </svg>
        </div>

        <div className="text-center relative z-10">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#3DA99F] border-t-transparent mx-auto" />
          <p className="mt-4 text-sm text-zinc-600">
            Loading chat...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-white relative overflow-hidden">
      {/* Background Waves */}
      <div className="absolute inset-0 pointer-events-none">
        <svg
          className="absolute top-0 left-0 w-full h-full"
          viewBox="0 0 1440 900"
          preserveAspectRatio="xMidYMid slice"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="chatWave1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="50%" stopColor="#3DA99F" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.15" />
            </linearGradient>
            <linearGradient id="chatWave2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.1" />
              <stop offset="50%" stopColor="#2A9D8F" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#3DA99F" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="chatWave3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3DA99F" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#2A9D8F" stopOpacity="0.12" />
            </linearGradient>
          </defs>
          <path
            d="M-100,550 C200,700 400,350 720,450 C1040,550 1200,300 1540,400 L1540,900 L-100,900 Z"
            fill="url(#chatWave1)"
          />
          <path
            d="M-100,600 C150,450 350,650 650,500 C950,350 1150,600 1540,450 L1540,900 L-100,900 Z"
            fill="url(#chatWave2)"
          />
          <path
            d="M-100,650 C200,500 500,700 800,550 C1100,400 1300,650 1540,500 L1540,900 L-100,900 Z"
            fill="url(#chatWave3)"
          />
        </svg>
      </div>

      <div className="relative z-10 h-full">
        <Chatbot
          clinicSlug={slug}
          clinicName={clinicInfo.clinic_name}
          greetingMessage={clinicInfo.greeting_message.replace(/\{clinic_name\}/g, clinicInfo.clinic_name)}
          userIdentifier={userIdentifier}
          clinicInfo={{
            phone: clinicInfo.phone,
            email: clinicInfo.email,
            address: clinicInfo.address,
            city: clinicInfo.city,
            state: clinicInfo.state,
            zip_code: clinicInfo.zip_code,
            business_hours: clinicInfo.business_hours,
          }}
        />
      </div>
    </div>
  );
}
