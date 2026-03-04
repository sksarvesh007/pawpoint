/**
 * Call History page - view call logs with transcript viewer and audio player.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Phone,
  PhoneIncoming,
  PhoneOutgoing,
  X,
  Loader2,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
} from "lucide-react";
import { getRecentCalls, getCallAnalytics, getCallLogDetail } from "@/lib/api/analytics";
import { SentimentBadge, OutcomeBadge, ConfidenceBar } from "@/components/dashboard/CallLogTable";
import type {
  CallLogsResponse,
  CallLogDetail,
  CallAnalytics,
  CallLogSummary,
} from "@/types/analytics";

const DIRECTION_TABS = [
  { value: "", label: "All" },
  { value: "inbound", label: "Inbound" },
  { value: "outbound", label: "Outbound" },
];

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return "\u2014";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function maskPhone(phone: string | null): string {
  if (!phone) return "Unknown";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length >= 4) {
    return `(***) ***-${cleaned.slice(-4)}`;
  }
  return "***";
}

function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const colorClasses: Record<string, { bg: string; icon: string }> = {
    teal: { bg: "bg-teal-50 dark:bg-teal-900/30", icon: "text-teal-600 dark:text-teal-400" },
    blue: { bg: "bg-blue-50 dark:bg-blue-900/30", icon: "text-blue-600 dark:text-blue-400" },
    orange: { bg: "bg-orange-50 dark:bg-orange-900/30", icon: "text-orange-600 dark:text-orange-400" },
    red: { bg: "bg-red-50 dark:bg-red-900/30", icon: "text-red-600 dark:text-red-400" },
  };
  const c = colorClasses[color] || colorClasses.teal;

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 ${c.bg} rounded-lg`}>
          <Icon className={`w-5 h-5 ${c.icon}`} />
        </div>
        <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
          {title}
        </p>
      </div>
      <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">{value}</p>
      {subtitle && (
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">{subtitle}</p>
      )}
    </div>
  );
}

function DirectionIcon({ direction }: { direction: string }) {
  if (direction === "inbound") {
    return <PhoneIncoming className="w-4 h-4 text-green-600 dark:text-green-400" />;
  }
  return <PhoneOutgoing className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
}

function CallDetailModal({
  call,
  onClose,
}: {
  call: CallLogDetail;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#1E2530] rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-zinc-200 dark:border-zinc-700">
          <div>
            <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Call Details</h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              {formatTime(call.started_at)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-zinc-500 dark:text-zinc-400" />
          </button>
        </div>

        {/* Call metadata */}
        <div className="p-4 bg-zinc-50 dark:bg-[#232A35] border-b border-zinc-200 dark:border-zinc-700 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-1.5">
            <DirectionIcon direction={call.direction} />
            <span className="font-medium text-zinc-900 dark:text-zinc-200 capitalize">{call.direction}</span>
          </div>
          <div>
            <span className="text-zinc-500 dark:text-zinc-400">Duration:</span>{" "}
            <span className="font-semibold text-zinc-900 dark:text-white">{formatDuration(call.duration_seconds)}</span>
          </div>
          <div>
            <span className="text-zinc-500 dark:text-zinc-400">Phone:</span>{" "}
            <span className="font-semibold text-zinc-900 dark:text-white">{maskPhone(call.caller_phone_number)}</span>
          </div>
          <div>
            <span className="text-zinc-500 dark:text-zinc-400">Outcome:</span>{" "}
            <OutcomeBadge outcome={call.outcome} />
          </div>
          {call.sentiment && (
            <div>
              <span className="text-zinc-500 dark:text-zinc-400">Sentiment:</span>{" "}
              <SentimentBadge sentiment={call.sentiment} />
            </div>
          )}
          {call.ai_confidence_score !== null && (
            <div className="flex items-center gap-2">
              <span className="text-zinc-500 dark:text-zinc-400">Confidence:</span>
              <span className="font-semibold text-zinc-900 dark:text-white">
                {Math.round(call.ai_confidence_score * 100)}%
              </span>
            </div>
          )}
        </div>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto">
          {/* Summary */}
          {call.summary && (
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-2">Summary</p>
              <p className="text-sm text-zinc-700 dark:text-zinc-300">{call.summary}</p>
            </div>
          )}

          {/* Key Points */}
          {call.key_points && call.key_points.length > 0 && (
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-2">Key Points</p>
              <ul className="list-disc list-inside text-sm text-zinc-700 dark:text-zinc-300 space-y-1">
                {call.key_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Audio Player */}
          {call.recording_url && (
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-2">Recording</p>
              <audio
                controls
                className="w-full"
                src={call.recording_url}
              >
                Your browser does not support the audio element.
              </audio>
            </div>
          )}

          {/* Transcript */}
          {call.transcript && (
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-3">Transcript</p>
              <TranscriptViewer transcript={call.transcript} />
            </div>
          )}

          {/* Actions Taken */}
          {call.actions_taken && call.actions_taken.length > 0 && (
            <div className="p-4">
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase mb-2">Actions Taken</p>
              <ul className="space-y-2">
                {call.actions_taken.map((action, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-zinc-700 dark:text-zinc-300">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-0.5 shrink-0" />
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* No content fallback */}
          {!call.summary && !call.transcript && (!call.key_points || call.key_points.length === 0) && (
            <div className="p-8 text-center text-zinc-500 dark:text-zinc-400">
              <Phone className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mx-auto mb-3" />
              <p className="text-sm">No transcript or analysis available for this call.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function TranscriptViewer({ transcript }: { transcript: string }) {
  // Try to parse as structured transcript (speaker-labeled lines)
  // Format: "Speaker: message" or "AI: message" / "Caller: message"
  const lines = transcript.split("\n").filter((l) => l.trim());
  const isStructured = lines.some((l) => /^(AI|Agent|Caller|User|Customer|Bot):\s/i.test(l));

  if (isStructured) {
    return (
      <div className="space-y-3">
        {lines.map((line, i) => {
          const match = line.match(/^(AI|Agent|Caller|User|Customer|Bot):\s*(.*)/i);
          if (!match) {
            return (
              <p key={i} className="text-sm text-zinc-600 dark:text-zinc-400 italic">{line}</p>
            );
          }
          const [, speaker, message] = match;
          const isAI = /^(AI|Agent|Bot)$/i.test(speaker);

          return (
            <div key={i} className={`flex gap-3 ${isAI ? "justify-start" : "justify-end"}`}>
              {isAI && (
                <div className="w-7 h-7 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center shrink-0 mt-0.5">
                  <Phone className="w-3.5 h-3.5 text-teal-600 dark:text-teal-400" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-2xl px-3.5 py-2 ${
                isAI
                  ? "bg-zinc-100 dark:bg-[#2A3140] text-zinc-900 dark:text-zinc-200"
                  : "bg-teal-600 text-white"
              }`}>
                <p className="text-xs font-medium mb-0.5 opacity-70">{speaker}</p>
                <p className="text-sm">{message}</p>
              </div>
              {!isAI && (
                <div className="w-7 h-7 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-zinc-600 dark:text-zinc-400">C</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // Plain text fallback
  return (
    <div className="bg-zinc-50 dark:bg-[#232A35] rounded-lg p-4 text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap leading-relaxed">
      {transcript}
    </div>
  );
}

export default function CallHistoryPage() {
  const [calls, setCalls] = useState<CallLogsResponse | null>(null);
  const [analytics, setAnalytics] = useState<CallAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [directionFilter, setDirectionFilter] = useState("");
  const [selectedCall, setSelectedCall] = useState<CallLogDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [callData, analyticsData] = await Promise.all([
        getRecentCalls(page, 20),
        getCallAnalytics(),
      ]);
      setCalls(callData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error("Failed to fetch call data:", err);
      setError("Failed to load call data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleViewCall = async (callId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await getCallLogDetail(callId);
      setSelectedCall(detail);
    } catch (err) {
      console.error("Failed to fetch call detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  };

  // Filter calls by direction (client-side since API may not support it)
  const filteredCalls = calls?.items.filter(
    (c) => !directionFilter || c.direction === directionFilter
  );

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 dark:text-white flex items-center gap-3">
          <Phone className="w-8 h-8 text-teal-600" />
          Call History
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 mt-1">
          View detailed call logs, transcripts, and recordings
        </p>
      </div>

      {loading && !calls ? (
        <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-teal-600 animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stats Cards */}
          {analytics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatsCard
                title="Total Calls"
                value={analytics.total_calls}
                subtitle={`+${analytics.calls_today} today`}
                icon={Phone}
                color="teal"
              />
              <StatsCard
                title="Avg Duration"
                value={`${Math.floor(analytics.average_duration_seconds / 60)}:${Math.round(analytics.average_duration_seconds % 60).toString().padStart(2, "0")}`}
                icon={Clock}
                color="blue"
              />
              <StatsCard
                title="AI Coverage"
                value={`${analytics.ai_handled_percentage}%`}
                subtitle={`${analytics.total_calls - analytics.emergency_transfers} handled`}
                icon={Activity}
                color="orange"
              />
              <StatsCard
                title="Emergencies"
                value={analytics.emergency_transfers}
                icon={AlertTriangle}
                color="red"
              />
            </div>
          )}

          {/* Direction filter */}
          <div className="flex bg-zinc-100 dark:bg-zinc-800 rounded-lg p-0.5 w-fit">
            {DIRECTION_TABS.map((tab) => (
              <button
                key={tab.value}
                onClick={() => setDirectionFilter(tab.value)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  directionFilter === tab.value
                    ? "bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                    : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Calls Table */}
          {filteredCalls && filteredCalls.length === 0 ? (
            <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-12 shadow-sm text-center">
              <Phone className="w-16 h-16 text-zinc-300 dark:text-zinc-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">
                No Calls Yet
              </h2>
              <p className="text-zinc-600 dark:text-zinc-400">
                Call logs will appear here once calls are handled.
              </p>
            </div>
          ) : filteredCalls ? (
            <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-zinc-50 dark:bg-[#232A35] border-b border-zinc-200 dark:border-zinc-700">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Time</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Direction</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Phone</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Duration</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Outcome</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Sentiment</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Confidence</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-700">
                  {filteredCalls.map((call: CallLogSummary) => (
                    <tr key={call.id} className="hover:bg-zinc-50 dark:hover:bg-[#252D3A] transition-colors">
                      <td className="px-4 py-3 text-sm text-zinc-900 dark:text-zinc-200 whitespace-nowrap" suppressHydrationWarning>
                        {formatTime(call.started_at)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <DirectionIcon direction={call.direction} />
                          <span className="text-xs text-zinc-600 dark:text-zinc-400 capitalize">{call.direction}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-zinc-700 dark:text-zinc-300 whitespace-nowrap">
                        {maskPhone(call.caller_phone_number)}
                      </td>
                      <td className="px-4 py-3 text-sm text-zinc-700 dark:text-zinc-300 whitespace-nowrap">
                        {formatDuration(call.duration_seconds)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <OutcomeBadge outcome={call.outcome} />
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <SentimentBadge sentiment={call.sentiment} />
                      </td>
                      <td className="px-4 py-3 w-32">
                        <ConfidenceBar score={call.ai_confidence_score} />
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleViewCall(call.id)}
                          className="text-teal-600 hover:text-teal-700 text-sm font-medium hover:underline"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              {calls && calls.total_pages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-200 dark:border-zinc-700">
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">
                    Page {page} of {calls.total_pages}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page <= 1}
                      className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setPage((p) => Math.min(calls.total_pages, p + 1))}
                      disabled={page >= calls.total_pages}
                      className="px-3 py-1.5 text-sm font-medium rounded-lg border border-zinc-200 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}

      {/* Loading overlay */}
      {loadingDetail && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-[#1E2530] rounded-xl p-6 shadow-xl flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
            <span className="text-zinc-700 dark:text-zinc-300">Loading call details...</span>
          </div>
        </div>
      )}

      {/* Call detail modal */}
      {selectedCall && (
        <CallDetailModal
          call={selectedCall}
          onClose={() => setSelectedCall(null)}
        />
      )}
    </div>
  );
}
