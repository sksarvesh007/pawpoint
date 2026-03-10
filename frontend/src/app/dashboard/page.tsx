/**
 * Main dashboard page - real-time updates via Server-Sent Events.
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { Download } from "lucide-react";
import {
  DashboardContent,
  type WidgetVisibility,
} from "@/components/dashboard/DashboardContent";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { env } from "@/lib/env";
import { getDashboardLayout } from "@/lib/api/preferences";
import type { DashboardAnalytics } from "@/types/analytics";

const DATE_RANGES = [
  { label: "7 days", value: 7 },
  { label: "30 days", value: 30 },
  { label: "90 days", value: 90 },
];

function exportAnalyticsCSV(analytics: DashboardAnalytics) {
  const lines: string[] = [];
  lines.push("Metric,Value");
  lines.push(`Total Calls,${analytics.calls.total_calls}`);
  lines.push(`Calls Today,${analytics.calls.calls_today}`);
  lines.push(`AI Handled %,${analytics.calls.ai_handled_percentage}`);
  lines.push(`Avg Duration (s),${analytics.calls.average_duration_seconds}`);
  lines.push(`Emergency Transfers,${analytics.calls.emergency_transfers}`);
  lines.push(`Total Appointments,${analytics.appointments.total_appointments}`);
  lines.push(
    `Appointments This Week,${analytics.appointments.appointments_this_week}`
  );
  lines.push(`Bookings via AI,${analytics.appointments.bookings_via_ai}`);
  lines.push(`No Show Rate,${analytics.appointments.no_show_rate}`);
  lines.push(`Total Patients,${analytics.patients.total_active_patients}`);
  lines.push(
    `New Patients This Month,${analytics.patients.new_patients_this_month}`
  );
  if (analytics.chats) {
    lines.push(`Total Chats,${analytics.chats.total_chats}`);
    lines.push(`Chats Today,${analytics.chats.chats_today}`);
  }

  const blob = new Blob([lines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `dashboard-analytics-${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected" | "error"
  >("connecting");
  const [widgetVisibility, setWidgetVisibility] =
    useState<WidgetVisibility | undefined>(undefined);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    getDashboardLayout()
      .then((data) => {
        const vis: WidgetVisibility = {} as WidgetVisibility;
        for (const w of data.widgets) {
          vis[w.id] = w.visible;
        }
        setWidgetVisibility(vis);
      })
      .catch(() => {
        // Use defaults (all visible) on error
      });
  }, []);

  useEffect(() => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const eventSource = new EventSource(
      `${env.apiUrl}/api/v1/analytics/stream?days=${days}`,
      { withCredentials: true }
    );

    eventSourceRef.current = eventSource;

    eventSource.addEventListener("analytics_update", (event) => {
      try {
        const data: DashboardAnalytics = JSON.parse(event.data);
        setAnalytics(data);
        setLoading(false);
        setConnectionStatus("connected");
        setError(null);
      } catch (err) {
        if (process.env.NODE_ENV === "development") {
          console.error("Failed to parse analytics data:", err);
        }
        setError("Failed to parse dashboard data");
      }
    });

    eventSource.addEventListener("open", () => {
      setConnectionStatus("connected");
      setError(null);
    });

    eventSource.addEventListener("error", () => {
      setConnectionStatus("error");
      eventSource.close();
    });

    const timeoutRef = reconnectTimeoutRef;
    return () => {
      eventSource.close();
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [days]);

  const handleDaysChange = (newDays: number) => {
    setDays(newDays);
  };

  return (
    <ErrorBoundary>
      <div className="relative">
        {/* Date Range & Export Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-1 bg-white dark:bg-[#1E2530] rounded-lg border border-zinc-200 dark:border-zinc-700 p-1">
            {DATE_RANGES.map((range) => (
              <button
                key={range.value}
                onClick={() => handleDaysChange(range.value)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  days === range.value
                    ? "bg-teal-600 text-white"
                    : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700"
                }`}
              >
                {range.label}
              </button>
            ))}
          </div>
          {analytics && (
            <button
              onClick={() => exportAnalyticsCSV(analytics)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-600 dark:text-zinc-400 bg-white dark:bg-[#1E2530] border border-zinc-200 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-700"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          )}
        </div>

        {/* Connection status indicator (only show if disconnected) */}
        {connectionStatus !== "connected" && !loading && (
          <div className="fixed top-4 right-4 z-50">
            <div
              className={`px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 ${
                connectionStatus === "connecting"
                  ? "bg-yellow-100 text-yellow-800"
                  : connectionStatus === "error"
                    ? "bg-red-100 text-red-800"
                    : "bg-zinc-100 text-zinc-800"
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  connectionStatus === "connecting"
                    ? "bg-yellow-600 animate-pulse"
                    : connectionStatus === "error"
                      ? "bg-red-600"
                      : "bg-zinc-600"
                }`}
              />
              <span className="text-sm font-medium">
                {connectionStatus === "connecting"
                  ? "Connecting..."
                  : connectionStatus === "error"
                    ? "Reconnecting..."
                    : "Disconnected"}
              </span>
            </div>
          </div>
        )}

        <DashboardContent
          analytics={analytics}
          loading={loading}
          error={error}
          widgetVisibility={widgetVisibility}
        />
      </div>
    </ErrorBoundary>
  );
}
