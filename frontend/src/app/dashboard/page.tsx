/**
 * Main dashboard page - real-time updates via Server-Sent Events.
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { DashboardContent } from "@/components/dashboard/DashboardContent";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { env } from "@/lib/env";
import type { DashboardAnalytics } from "@/types/analytics";

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected" | "error"
  >("connecting");
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    let mounted = true;

    const connectToStream = () => {
      if (!mounted) return;

      setConnectionStatus("connecting");

      // Create EventSource for Server-Sent Events
      const eventSource = new EventSource(
        `${env.apiUrl}/api/v1/analytics/stream`,
        { withCredentials: true }
      );

      eventSourceRef.current = eventSource;

      // Handle analytics updates
      eventSource.addEventListener("analytics_update", (event) => {
        if (!mounted) return;

        try {
          const data: DashboardAnalytics = JSON.parse(event.data);
          setAnalytics(data);
          setLoading(false);
          setConnectionStatus("connected");
          setError(null);
        } catch (err) {
          console.error("Failed to parse analytics data:", err);
          setError("Failed to parse dashboard data");
        }
      });

      // Handle connection open
      eventSource.addEventListener("open", () => {
        if (!mounted) return;
        setConnectionStatus("connected");
        setError(null);

        // Log in development only
        if (process.env.NODE_ENV === "development") {
          console.log("✅ Dashboard stream connected");
        }
      });

      // Handle errors
      eventSource.addEventListener("error", (event: Event) => {
        if (!mounted) return;

        setConnectionStatus("error");

        // Only log in development
        if (process.env.NODE_ENV === "development") {
          console.error("Dashboard stream error:", event);
        }

        // Close connection and attempt reconnect
        eventSource.close();

        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          if (mounted) {
            if (process.env.NODE_ENV === "development") {
              console.log("Attempting to reconnect...");
            }
            connectToStream();
          }
        }, 5000);
      });
    };

    // Initial connection
    connectToStream();

    // Cleanup on unmount
    return () => {
      mounted = false;
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return (
    <ErrorBoundary>
      <div className="relative">
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

        <DashboardContent analytics={analytics} loading={loading} error={error} />
      </div>
    </ErrorBoundary>
  );
}
