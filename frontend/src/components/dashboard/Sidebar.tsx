/**
 * Dashboard sidebar navigation with teal background and wave patterns.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Calendar,
  PawPrint,
  Phone,
  Settings,
} from "lucide-react";
import { Logo } from "@/components/Logo";
import { getClinicInfo } from "@/lib/api/clinic";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  {
    href: "/dashboard/appointments",
    label: "Appointment Requests",
    icon: Calendar,
  },
  { href: "/dashboard/patients", label: "Patients", icon: PawPrint },
  { href: "/dashboard/calls", label: "Call Log", icon: Phone },
  { href: "/dashboard/settings/ai", label: "Settings", icon: Settings },
];

interface SidebarProps {
  clinicName?: string;
  topOffset?: number;
  hideLogo?: boolean;
  disableLinks?: boolean;
}

export function Sidebar({
  clinicName: propClinicName,
  topOffset = 0,
  hideLogo = false,
  disableLinks = false,
}: SidebarProps = {}) {
  const pathname = usePathname();
  const [clinicName, setClinicName] = useState<string>(
    propClinicName || "Loading...",
  );

  useEffect(() => {
    if (propClinicName) {
      setClinicName(propClinicName);
      return;
    }

    getClinicInfo()
      .then((info) => setClinicName(info.name))
      .catch(() => setClinicName("My Clinic"));
  }, [propClinicName]);

  return (
    <aside
      className="fixed left-0 w-64 bg-gradient-to-b from-[#A8DCD9] via-[#B4E2DF] to-[#C5E8E6] z-20 flex flex-col overflow-hidden"
      style={{ top: `${topOffset}px`, height: `calc(100vh - ${topOffset}px)` }}
    >
      {/* Wave patterns - subtle background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        {/* Top wave */}
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
            <linearGradient id="sidebarWave1" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Middle wave */}
        <svg
          className="absolute top-1/3 left-0 w-full"
          height="150"
          viewBox="0 0 300 150"
          preserveAspectRatio="none"
        >
          <path
            d="M 0,75 C 60,60 120,90 180,75 C 240,60 270,75 300,75 L 300,150 L 0,150 Z"
            fill="url(#sidebarWave2)"
          />
          <defs>
            <linearGradient id="sidebarWave2" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.05" />
            </linearGradient>
          </defs>
        </svg>

        {/* Bottom wave */}
        <svg
          className="absolute bottom-0 left-0 w-full"
          height="180"
          viewBox="0 0 300 180"
          preserveAspectRatio="none"
        >
          <path
            d="M 0,90 C 75,110 150,70 225,90 L 300,90 L 300,180 L 0,180 Z"
            fill="url(#sidebarWave3)"
          />
          <defs>
            <linearGradient id="sidebarWave3" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#7ECDC8" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#7ECDC8" stopOpacity="0.4" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Logo header - hidden when navbar is present */}
        {!hideLogo && (
          <div className="p-6 border-b border-white/20">
            <Logo />
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navItems.map((item, index) => {
            const isActive = disableLinks
              ? index === 0
              : pathname === item.href;
            const content = (
              <>
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
              </>
            );

            if (disableLinks) {
              return (
                <div
                  key={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all cursor-default ${
                    isActive
                      ? "bg-white/90 text-[#1D3533] font-semibold shadow-sm"
                      : "text-[#1D3533]/80"
                  }`}
                >
                  {content}
                </div>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? "bg-white/90 text-[#1D3533] font-semibold shadow-sm"
                    : "text-[#1D3533]/80 hover:bg-white/40 hover:text-[#1D3533]"
                }`}
              >
                {content}
              </Link>
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
              {clinicName}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
