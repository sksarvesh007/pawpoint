/**
 * Dashboard sidebar navigation with modern glassmorphism design.
 */

"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Calendar,
  PawPrint,
  Phone,
  Settings,
  MessageCircle,
  LogOut,
  Inbox,
  FileText,
  LayoutGrid,
  HelpCircle,
  Shield,
  Mic,
  Database,
} from "lucide-react";
import { getClinicInfo } from "@/lib/api/clinic";
import { logout } from "@/lib/api/auth";
import { ThemeToggle } from "./ThemeToggle";

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
  const router = useRouter();
  const [clinicName, setClinicName] = useState<string>("Loading...");
  const [clinicSlug, setClinicSlug] = useState<string>("");
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    if (propClinicName) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setClinicName(propClinicName);
      return;
    }

    let mounted = true;
    getClinicInfo()
      .then((info) => {
        if (mounted) {
          setClinicName(info.name);
          setClinicSlug(info.slug);
        }
      })
      .catch(() => {
        if (mounted) setClinicName("My Clinic");
      });

    return () => {
      mounted = false;
    };
  }, [propClinicName]);

  useEffect(() => {
    let es: EventSource | null = null;
    let pollInterval: ReturnType<typeof setInterval> | null = null;

    const startPolling = () => {
      if (pollInterval) return;
      pollInterval = setInterval(async () => {
        try {
          const res = await fetch("/api/v1/notifications/unread-count");
          if (res.ok) {
            const data = (await res.json()) as { unread_count: number };
            setUnreadCount(data.unread_count);
          }
        } catch {
          // ignore
        }
      }, 30_000);
    };

    const startSSE = () => {
      es = new EventSource("/api/v1/notifications/stream");
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as { unread_count: number };
          setUnreadCount(data.unread_count);
        } catch {
          // ignore malformed events
        }
      };
      es.onerror = () => {
        es?.close();
        es = null;
        // Fall back to 30s polling on SSE error
        startPolling();
      };
    };

    startSSE();

    return () => {
      es?.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, []);

  const handleLogout = async () => {
    setLoggingOut(true);
    setLogoutError(null);
    try {
      await logout();
      router.push("/");
    } catch (error) {
      console.error("Logout failed:", error);
      setLogoutError("Failed to log out. Please try again.");
      setLoggingOut(false);
    }
  };

  // Navigation items organized by sections
  const navSections = [
    {
      title: null, // No title for main items
      items: [
        { href: "/dashboard", label: "Home", icon: LayoutDashboard, badge: null as number | null },
        { href: "/dashboard/inbox", label: "Inbox", icon: Inbox, badge: unreadCount > 0 ? unreadCount : null },
      ],
    },
    {
      title: "APPLICATIONS",
      items: [
        {
          href: "/dashboard/appointments",
          label: "Appointments",
          icon: Calendar,
        },
        { href: "/dashboard/patients", label: "Patients", icon: PawPrint },
        { href: "/dashboard/calls", label: "Call Log", icon: Phone },
        { href: "/dashboard/chats", label: "Chat Log", icon: MessageCircle },
        { href: "/dashboard/voice", label: "Voice Bot", icon: Mic },
        {
          href: clinicSlug ? `/${clinicSlug}/chat` : "#",
          label: "Chat Widget",
          icon: MessageCircle,
          external: true,
        },
        { href: "/dashboard/settings/pims", label: "PIMS", icon: Database },
      ],
    },
    {
      title: "OTHERS",
      items: [
        { href: "/dashboard/reports", label: "Reports", icon: FileText },
        { href: "/dashboard/widgets", label: "Widgets", icon: LayoutGrid },
      ],
    },
    {
      title: "SUPPORT",
      items: [
        { href: "/dashboard/settings", label: "Settings", icon: Settings },
        { href: "/dashboard/security", label: "Security", icon: Shield },
        { href: "/dashboard/help", label: "Help", icon: HelpCircle },
      ],
    },
  ];

  return (
    <aside
      className="fixed left-0 w-[280px] z-20 flex flex-col overflow-hidden"
      style={{ top: `${topOffset}px`, height: `calc(100vh - ${topOffset}px)` }}
    >
      {/* Glassmorphism background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#E8F5F4]/95 via-[#F0F9F8]/90 to-[#E3F2F1]/95 dark:from-[#151D25]/95 dark:via-[#1A2330]/90 dark:to-[#141C24]/95 backdrop-blur-xl" />

      {/* Subtle decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 -left-10 w-40 h-40 bg-[#A8DCD9]/20 dark:bg-[#3EB5B0]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-40 -right-10 w-32 h-32 bg-[#3EB5B0]/15 dark:bg-[#3EB5B0]/8 rounded-full blur-2xl" />
        <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-[#FF8A65]/10 dark:bg-[#FF8A65]/5 rounded-full blur-2xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Logo header - hidden when navbar is present */}
        {!hideLogo && (
          <div className="px-6 pt-6 pb-5">
            <div className="flex items-center gap-3 px-4 py-3 bg-white/50 dark:bg-white/10 backdrop-blur-md rounded-2xl border border-white/60 dark:border-white/10 shadow-sm">
              <div className="w-9 h-9 bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] rounded-xl flex items-center justify-center shadow-md">
                <PawPrint className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-[#1D3533] dark:text-white truncate">
                  {clinicName}
                </p>
                <p className="text-xs text-[#1D3533]/50 dark:text-zinc-400">Veterinary Clinic</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 px-4 overflow-y-auto">
          {navSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="mb-6">
              {section.title && (
                <div className="px-4 mb-3">
                  <p className="text-[10px] font-semibold text-[#1D3533]/40 dark:text-zinc-500 tracking-wider uppercase">
                    {section.title}
                  </p>
                </div>
              )}
              <div className="space-y-1">
                {section.items.map((item, itemIndex) => {
                  const isActive = disableLinks
                    ? sectionIndex === 0 && itemIndex === 0
                    : pathname === item.href;
                  const badge = "badge" in item ? item.badge : null;
                  const content = (
                    <>
                      <div
                        className={`p-2 rounded-xl shrink-0 transition-all ${
                          isActive
                            ? "bg-gradient-to-br from-[#3EB5B0] to-[#2A8A86] text-white shadow-md shadow-[#3EB5B0]/20"
                            : "bg-white/40 dark:bg-white/10 text-[#3EB5B0]"
                        }`}
                      >
                        <item.icon className="w-4 h-4" strokeWidth={2.5} />
                      </div>
                      <span
                        className={`flex-1 text-[13px] font-medium ${
                          isActive ? "text-[#1D3533] dark:text-white" : "text-[#1D3533]/70 dark:text-zinc-400"
                        }`}
                      >
                        {item.label}
                      </span>
                      {badge !== null && badge > 0 && (
                        <span className="ml-auto min-w-[20px] h-5 px-1.5 flex items-center justify-center rounded-full bg-[#3EB5B0] text-white text-[10px] font-bold leading-none">
                          {badge > 99 ? "99+" : badge}
                        </span>
                      )}
                    </>
                  );

                  if (disableLinks || item.href === "#") {
                    return (
                      <div
                        key={item.href}
                        className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all cursor-default ${
                          isActive
                            ? "bg-white/70 dark:bg-white/10 backdrop-blur-sm shadow-sm border border-white/80 dark:border-white/10"
                            : "opacity-50"
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
                      className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all group ${
                        isActive
                          ? "bg-white/70 dark:bg-white/10 backdrop-blur-sm shadow-sm border border-white/80 dark:border-white/10"
                          : "hover:bg-white/50 dark:hover:bg-white/5 hover:backdrop-blur-sm"
                      }`}
                    >
                      {content}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Bottom section - theme toggle + logout */}
        <div className="p-4 border-t border-white/30 dark:border-white/10 space-y-2">
          <ThemeToggle />
          {logoutError && (
            <div className="px-3 py-2 bg-red-100 border border-red-200 rounded-lg">
              <p className="text-xs text-red-700">{logoutError}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all bg-white/40 dark:bg-white/10 hover:bg-white/60 dark:hover:bg-white/15 backdrop-blur-sm border border-white/50 dark:border-white/10 disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <div className="p-2 rounded-xl shrink-0 bg-gradient-to-br from-[#FF8A65] to-[#FF6E40] text-white shadow-sm">
              <LogOut className="w-4 h-4" strokeWidth={2.5} />
            </div>
            <span className="text-[13px] font-medium text-[#1D3533]/70 dark:text-zinc-400 group-hover:text-[#1D3533] dark:group-hover:text-zinc-200">
              {loggingOut ? "Logging out..." : "Log Out"}
            </span>
          </button>
        </div>
      </div>
    </aside>
  );
}
