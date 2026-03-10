/**
 * Widgets page - Configure which widgets appear on the dashboard.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  LayoutGrid,
  Phone,
  Calendar,
  Activity,
  MessageCircle,
  Database,
  List,
  BarChart3,
  Eye,
  EyeOff,
  ArrowUp,
  ArrowDown,
  Loader2,
  Check,
  RotateCcw,
  X,
} from "lucide-react";
import {
  getDashboardLayout,
  saveDashboardLayout,
  type WidgetConfig,
} from "@/lib/api/preferences";

const WIDGET_CATALOG: Record<
  string,
  { label: string; description: string; icon: typeof Phone }
> = {
  stats_cards: {
    label: "Stats Cards",
    description: "Top-level metrics: calls answered, appointments, coverage, chats",
    icon: BarChart3,
  },
  calls_chart: {
    label: "Calls & Chats Chart",
    description: "Hourly call and chat volume bar chart",
    icon: Phone,
  },
  quick_stats: {
    label: "Quick Stats Grid",
    description: "Average duration, emergencies, appointments booked, new patients",
    icon: Calendar,
  },
  call_sentiment: {
    label: "Call Sentiment",
    description: "Positive, neutral, and negative call breakdown",
    icon: Activity,
  },
  chat_sentiment: {
    label: "Chat Sentiment",
    description: "Chat sentiment distribution and resolution rate",
    icon: MessageCircle,
  },
  appointment_status: {
    label: "Appointment Status",
    description: "Breakdown of appointments by status (booked, cancelled, no-show)",
    icon: Calendar,
  },
  pims_status: {
    label: "PIMS Sync Status",
    description: "Practice management system connection and sync health",
    icon: Database,
  },
  pims_sync_trend: {
    label: "PIMS Sync Trend",
    description: "Daily success/failure trend chart for PIMS syncs",
    icon: Database,
  },
  recent_calls: {
    label: "Recent Calls Table",
    description: "Table of latest call logs with outcome and sentiment",
    icon: List,
  },
};

const DEFAULT_WIDGETS: WidgetConfig[] = [
  { id: "stats_cards", visible: true },
  { id: "calls_chart", visible: true },
  { id: "quick_stats", visible: true },
  { id: "appointment_status", visible: true },
  { id: "call_sentiment", visible: true },
  { id: "chat_sentiment", visible: true },
  { id: "pims_status", visible: true },
  { id: "pims_sync_trend", visible: true },
  { id: "recent_calls", visible: true },
];

export default function WidgetsPage() {
  const [widgets, setWidgets] = useState<WidgetConfig[]>(DEFAULT_WIDGETS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [hasChanges, setHasChanges] = useState(false);
  const [savedWidgets, setSavedWidgets] = useState<WidgetConfig[]>(DEFAULT_WIDGETS);

  const loadLayout = useCallback(async () => {
    try {
      const data = await getDashboardLayout();
      setWidgets(data.widgets);
      setSavedWidgets(data.widgets);
    } catch {
      // Use defaults on error
      setWidgets(DEFAULT_WIDGETS);
      setSavedWidgets(DEFAULT_WIDGETS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLayout();
  }, [loadLayout]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    const changed =
      JSON.stringify(widgets) !== JSON.stringify(savedWidgets);
    setHasChanges(changed);
  }, [widgets, savedWidgets]);

  const toggleWidget = (id: string) => {
    setWidgets((prev) =>
      prev.map((w) => (w.id === id ? { ...w, visible: !w.visible } : w))
    );
  };

  const moveWidget = (index: number, direction: "up" | "down") => {
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= widgets.length) return;
    setWidgets((prev) => {
      const copy = [...prev];
      [copy[index], copy[newIndex]] = [copy[newIndex], copy[index]];
      return copy;
    });
  };

  const handleSave = async () => {
    setError("");
    setSaving(true);
    try {
      await saveDashboardLayout(widgets);
      setSavedWidgets(widgets);
      setSuccess("Dashboard layout saved");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to save layout"
      );
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setWidgets(DEFAULT_WIDGETS);
  };

  if (loading) {
    return (
      <div className="max-w-2xl">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-teal-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 flex items-center gap-3">
          <LayoutGrid className="w-8 h-8 text-teal-600" />
          Widgets
        </h1>
        <p className="text-zinc-600 mt-1">
          Choose which widgets appear on your dashboard and set their order
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      {success && (
        <div className="mb-6 rounded-lg bg-green-50 p-4 text-sm text-green-600 flex items-center justify-between">
          <span>{success}</span>
          <button onClick={() => setSuccess("")}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Widget List */}
      <div className="bg-white rounded-xl border border-zinc-200 shadow-sm divide-y divide-zinc-100">
        {widgets.map((widget, index) => {
          const meta = WIDGET_CATALOG[widget.id];
          if (!meta) return null;
          const Icon = meta.icon;

          return (
            <div
              key={widget.id}
              className={`flex items-center gap-4 p-4 transition-colors ${
                !widget.visible ? "opacity-50" : ""
              }`}
            >
              {/* Reorder buttons */}
              <div className="flex flex-col gap-0.5">
                <button
                  onClick={() => moveWidget(index, "up")}
                  disabled={index === 0}
                  className="p-1 rounded hover:bg-zinc-100 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-400 hover:text-zinc-600"
                  aria-label="Move up"
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => moveWidget(index, "down")}
                  disabled={index === widgets.length - 1}
                  className="p-1 rounded hover:bg-zinc-100 disabled:opacity-30 disabled:cursor-not-allowed text-zinc-400 hover:text-zinc-600"
                  aria-label="Move down"
                >
                  <ArrowDown className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Icon */}
              <div
                className={`p-2.5 rounded-lg ${
                  widget.visible
                    ? "bg-teal-50 text-teal-600"
                    : "bg-zinc-100 text-zinc-400"
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-zinc-900">
                  {meta.label}
                </p>
                <p className="text-xs text-zinc-500 mt-0.5">
                  {meta.description}
                </p>
              </div>

              {/* Toggle */}
              <button
                onClick={() => toggleWidget(widget.id)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  widget.visible ? "bg-teal-600" : "bg-zinc-300"
                }`}
                aria-label={widget.visible ? "Hide widget" : "Show widget"}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm ${
                    widget.visible ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>

              {/* Visibility icon */}
              {widget.visible ? (
                <Eye className="w-4 h-4 text-teal-600 shrink-0" />
              ) : (
                <EyeOff className="w-4 h-4 text-zinc-400 shrink-0" />
              )}
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 mt-6">
        <button
          onClick={handleSave}
          disabled={saving || !hasChanges}
          className="flex items-center gap-2 px-5 py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Check className="w-4 h-4" />
          )}
          Save Layout
        </button>
        <button
          onClick={handleReset}
          className="flex items-center gap-2 px-5 py-2.5 border border-zinc-300 text-zinc-700 rounded-lg text-sm font-medium hover:bg-zinc-50"
        >
          <RotateCcw className="w-4 h-4" />
          Reset to Default
        </button>
      </div>

      {hasChanges && (
        <p className="text-xs text-amber-600 mt-3">
          You have unsaved changes
        </p>
      )}
    </div>
  );
}
