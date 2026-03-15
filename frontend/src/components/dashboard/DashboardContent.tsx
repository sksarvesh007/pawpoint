/**
 * Reusable dashboard content component.
 * Accepts analytics data as props - can be used for both real and demo dashboards.
 */

import {
  Phone,
  Calendar,
  PawPrint,
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  Database,
  MessageCircle,
  PhoneMissed,
} from "lucide-react";
import { StatsCard } from "./StatsCard";
import { CallsChart } from "./CallsChart";
import { AppointmentStatusChart } from "./AppointmentStatusChart";
import { PIMSSyncTrendChart } from "./PIMSSyncTrendChart";
import { CallLogTable } from "./CallLogTable";
import type { DashboardAnalytics } from "@/types/analytics";

export interface WidgetVisibility {
  stats_cards: boolean;
  calls_chart: boolean;
  quick_stats: boolean;
  call_sentiment: boolean;
  chat_sentiment: boolean;
  pims_status: boolean;
  recent_calls: boolean;
  [key: string]: boolean;
}

interface DashboardContentProps {
  analytics: DashboardAnalytics | null;
  loading?: boolean;
  error?: string | null;
  widgetVisibility?: WidgetVisibility;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-10 bg-zinc-200 dark:bg-zinc-700 rounded w-48" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-zinc-200 dark:bg-zinc-700 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="h-64 bg-zinc-200 dark:bg-zinc-700 rounded-xl" />
        ))}
      </div>
    </div>
  );
}

function SentimentCard({
  sentiment,
}: {
  sentiment: DashboardAnalytics["sentiment"] | undefined;
}) {
  if (!sentiment) return null;

  const total =
    sentiment.positive_calls +
    sentiment.neutral_calls +
    sentiment.negative_calls;
  const positivePercent =
    total > 0 ? (sentiment.positive_calls / total) * 100 : 0;
  const neutralPercent =
    total > 0 ? (sentiment.neutral_calls / total) * 100 : 0;
  const negativePercent =
    total > 0 ? (sentiment.negative_calls / total) * 100 : 0;

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-6 flex items-center gap-2">
        <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
          <Activity className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </div>
        Call Sentiment
      </h3>

      {/* Sentiment stats grid */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-xl">
          <p className="text-3xl font-black text-green-600 dark:text-green-400 font-nunito">
            {sentiment.positive_calls}
          </p>
          <p className="text-xs text-green-700 dark:text-green-300 font-semibold mt-1">Positive</p>
        </div>
        <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl">
          <p className="text-3xl font-black text-yellow-600 dark:text-yellow-400 font-nunito">
            {sentiment.neutral_calls}
          </p>
          <p className="text-xs text-yellow-700 dark:text-yellow-300 font-semibold mt-1">Neutral</p>
        </div>
        <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-xl">
          <p className="text-3xl font-black text-red-600 dark:text-red-400 font-nunito">
            {sentiment.negative_calls}
          </p>
          <p className="text-xs text-red-700 dark:text-red-300 font-semibold mt-1">Negative</p>
        </div>
      </div>

      {/* Sentiment bar */}
      <div className="h-3 flex rounded-full overflow-hidden">
        <div
          className="bg-green-500"
          style={{ width: `${positivePercent}%` }}
          title={`${positivePercent.toFixed(1)}% positive`}
        />
        <div
          className="bg-yellow-500"
          style={{ width: `${neutralPercent}%` }}
          title={`${neutralPercent.toFixed(1)}% neutral`}
        />
        <div
          className="bg-red-500"
          style={{ width: `${negativePercent}%` }}
          title={`${negativePercent.toFixed(1)}% negative`}
        />
      </div>
    </div>
  );
}

function PIMSStatusCard({
  pims,
}: {
  pims: DashboardAnalytics["pims"] | undefined;
}) {
  if (!pims) return null;

  const isConnected = pims.connection_status === "connected";

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-6 flex items-center gap-2">
        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
          <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        PIMS Sync Status
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-zinc-600 dark:text-zinc-400 font-medium">Status</span>
          <span
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold ${
              isConnected
                ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                : "bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-400"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-600 animate-pulse" : "bg-zinc-400"}`}
            />
            {pims.connection_status.replace(/_/g, " ").toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4">
          <div className="text-center p-4 bg-zinc-50 dark:bg-[#232A35] rounded-xl">
            <p className="text-2xl font-black text-[#1D3533] dark:text-white font-nunito">
              {pims.sync_success_rate.toFixed(0)}%
            </p>
            <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold mt-1">
              Success Rate
            </p>
          </div>
          <div className="text-center p-4 bg-zinc-50 dark:bg-[#232A35] rounded-xl">
            <p className="text-2xl font-black text-[#1D3533] dark:text-white font-nunito">
              {pims.total_syncs_today}
            </p>
            <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold mt-1">
              Syncs Today
            </p>
          </div>
        </div>

        {pims.last_sync_at && (
          <div className="pt-4 border-t border-zinc-200 dark:border-zinc-700">
            <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">Last Sync</p>
            <p className="text-sm font-bold text-zinc-900 dark:text-white mt-1" suppressHydrationWarning>
              {new Date(pims.last_sync_at).toLocaleString("en-US", {
                month: "short",
                day: "numeric",
                hour: "numeric",
                minute: "2-digit",
              })}
            </p>
          </div>
        )}

        {pims.failed_syncs_today > 0 && (
          <div className="pt-4 border-t border-zinc-200 dark:border-zinc-700">
            <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2 font-semibold">
              <AlertTriangle className="w-4 h-4" />
              {pims.failed_syncs_today} failed sync
              {pims.failed_syncs_today > 1 ? "s" : ""}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function ChatSentimentMiniCard({
  chats,
}: {
  chats: DashboardAnalytics["chats"] | undefined;
}) {
  if (!chats?.sentiment) return null;

  const s = chats.sentiment;
  const total = s.positive_chats + s.neutral_chats + s.negative_chats;
  if (total === 0) return null;

  const pPct = total > 0 ? Math.round((s.positive_chats / total) * 100) : 0;
  const nPct = total > 0 ? Math.round((s.neutral_chats / total) * 100) : 0;
  const negPct = total > 0 ? Math.round((s.negative_chats / total) * 100) : 0;

  return (
    <div className="bg-white dark:bg-[#1E2530] rounded-2xl border border-zinc-200 dark:border-zinc-700 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] dark:text-white mb-6 flex items-center gap-2">
        <div className="p-2 bg-teal-50 dark:bg-teal-900/30 rounded-lg">
          <MessageCircle className="w-5 h-5 text-teal-600 dark:text-teal-400" />
        </div>
        Chat Sentiment
      </h3>

      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-xl">
          <p className="text-3xl font-black text-green-600 dark:text-green-400 font-nunito">
            {s.positive_chats}
          </p>
          <p className="text-xs text-green-700 dark:text-green-300 font-semibold mt-1">Positive</p>
        </div>
        <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl">
          <p className="text-3xl font-black text-yellow-600 dark:text-yellow-400 font-nunito">
            {s.neutral_chats}
          </p>
          <p className="text-xs text-yellow-700 dark:text-yellow-300 font-semibold mt-1">Neutral</p>
        </div>
        <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-xl">
          <p className="text-3xl font-black text-red-600 dark:text-red-400 font-nunito">
            {s.negative_chats}
          </p>
          <p className="text-xs text-red-700 dark:text-red-300 font-semibold mt-1">Negative</p>
        </div>
      </div>

      <div className="h-3 flex rounded-full overflow-hidden">
        <div
          className="bg-green-500"
          style={{ width: `${pPct}%` }}
          title={`${pPct}% positive`}
        />
        <div
          className="bg-yellow-500"
          style={{ width: `${nPct}%` }}
          title={`${nPct}% neutral`}
        />
        <div
          className="bg-red-500"
          style={{ width: `${negPct}%` }}
          title={`${negPct}% negative`}
        />
      </div>

      {chats.resolution_rate !== null && (
        <div className="mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-700 flex justify-between text-sm">
          <span className="text-zinc-500 dark:text-zinc-400">Resolution Rate</span>
          <span className="font-bold text-zinc-900 dark:text-white">{chats.resolution_rate}%</span>
        </div>
      )}
    </div>
  );
}

export function DashboardContent({
  analytics,
  loading = false,
  error = null,
  widgetVisibility,
}: DashboardContentProps) {
  const isVisible = (id: string) => !widgetVisibility || widgetVisibility[id] !== false;
  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 text-lg font-semibold mb-2">Error</p>
          <p className="text-zinc-500 dark:text-zinc-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-zinc-500 dark:text-zinc-400 text-lg">Connecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 mt-1">
          Overview of your clinic&apos;s performance
        </p>
      </div>

      {/* Stats Grid - 4 columns */}
      {isVisible("stats_cards") && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Calls Answered"
            value={`${analytics.calls.total_calls}`}
            subtitle={`+${analytics.calls.calls_today} today`}
            icon={Phone}
            color="orange"
          />
          <StatsCard
            title="Appointments"
            value={analytics.appointments.total_appointments}
            subtitle={`+${analytics.appointments.appointments_this_week} this week`}
            icon={Calendar}
            color="blue"
          />
          <StatsCard
            title="Call Coverage"
            value={`${analytics.calls.ai_handled_percentage}%`}
            subtitle={`${analytics.calls.total_calls - analytics.calls.emergency_transfers} answered / ${analytics.calls.total_calls} total`}
            icon={CheckCircle}
            color="teal"
          />
          <StatsCard
            title="Chat Sessions"
            value={analytics.chats?.total_chats ?? 0}
            subtitle={`+${analytics.chats?.chats_today ?? 0} today`}
            icon={MessageCircle}
            color="purple"
          />
          {(() => {
            const missedCount =
              (analytics.calls.calls_by_outcome["call_dropped"] ?? 0) +
              (analytics.calls.calls_by_outcome["voicemail_left"] ?? 0);
            const missedRate =
              analytics.calls.total_calls > 0
                ? ((missedCount / analytics.calls.total_calls) * 100).toFixed(1)
                : "0.0";
            return (
              <StatsCard
                title="Missed Calls"
                value={missedCount}
                subtitle={`${missedRate}% miss rate`}
                icon={PhoneMissed}
                color="orange"
              />
            );
          })()}
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {isVisible("calls_chart") && (
            <CallsChart
              data={analytics.calls.calls_by_hour}
              chatData={analytics.chats?.chats_by_hour}
              emergencyTransfers={analytics.calls.emergency_transfers}
              transferHours={analytics.calls.transfer_hours}
            />
          )}
          {isVisible("quick_stats") && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-orange-50 dark:bg-orange-900/30 rounded-lg">
                    <Clock className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
                    Avg Duration
                  </p>
                </div>
                <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">
                  {Math.floor(analytics.calls.average_duration_seconds / 60)}:
                  {(analytics.calls.average_duration_seconds % 60)
                    .toFixed(0)
                    .padStart(2, "0")}
                </p>
              </div>
              <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-red-50 dark:bg-red-900/30 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
                    Emergencies
                  </p>
                </div>
                <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">
                  {analytics.calls.emergency_transfers}
                </p>
              </div>
              <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-teal-50 dark:bg-teal-900/30 rounded-lg">
                    <Calendar className="w-5 h-5 text-teal-600 dark:text-teal-400" />
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
                    Appointments Booked
                  </p>
                </div>
                <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">
                  {analytics.appointments.bookings_via_ai}
                </p>
              </div>
              <div className="bg-white dark:bg-[#1E2530] rounded-xl border border-zinc-200 dark:border-zinc-700 p-5 shadow-sm">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
                    <PawPrint className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 font-semibold uppercase tracking-wide">
                    New Patients
                  </p>
                </div>
                <p className="text-2xl font-black text-zinc-900 dark:text-white font-nunito">
                  {analytics.patients.new_patients_this_month}
                </p>
              </div>
            </div>
          )}
          {isVisible("appointment_status") && (
            <AppointmentStatusChart
              data={analytics.appointments.appointments_by_status}
            />
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {isVisible("call_sentiment") && (
            <SentimentCard sentiment={analytics.sentiment} />
          )}
          {isVisible("chat_sentiment") && (
            <ChatSentimentMiniCard chats={analytics.chats} />
          )}
          {isVisible("pims_status") && (
            <PIMSStatusCard pims={analytics.pims} />
          )}
          {isVisible("pims_sync_trend") &&
            analytics.pims.sync_trend.length > 0 && (
              <PIMSSyncTrendChart data={analytics.pims.sync_trend} />
            )}
        </div>
      </div>

      {/* Recent Call Logs Table */}
      {isVisible("recent_calls") && (
        <CallLogTable calls={analytics.recent_calls} />
      )}
    </div>
  );
}
