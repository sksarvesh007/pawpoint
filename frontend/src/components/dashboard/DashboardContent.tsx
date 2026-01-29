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
} from "lucide-react";
import { StatsCard } from "./StatsCard";
import { CallsChart } from "./CallsChart";
import { CallLogTable } from "./CallLogTable";
import type { DashboardAnalytics } from "@/types/analytics";

interface DashboardContentProps {
  analytics: DashboardAnalytics | null;
  loading?: boolean;
  error?: string | null;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-10 bg-zinc-200 rounded w-48" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-zinc-200 rounded-xl" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="h-64 bg-zinc-200 rounded-xl" />
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
    <div className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] mb-6 flex items-center gap-2">
        <div className="p-2 bg-purple-50 rounded-lg">
          <Activity className="w-5 h-5 text-purple-600" />
        </div>
        Call Sentiment
      </h3>

      {/* Sentiment stats grid */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="text-center p-4 bg-green-50 rounded-xl">
          <p className="text-3xl font-black text-green-600 font-nunito">
            {sentiment.positive_calls}
          </p>
          <p className="text-xs text-green-700 font-semibold mt-1">Positive</p>
        </div>
        <div className="text-center p-4 bg-yellow-50 rounded-xl">
          <p className="text-3xl font-black text-yellow-600 font-nunito">
            {sentiment.neutral_calls}
          </p>
          <p className="text-xs text-yellow-700 font-semibold mt-1">Neutral</p>
        </div>
        <div className="text-center p-4 bg-red-50 rounded-xl">
          <p className="text-3xl font-black text-red-600 font-nunito">
            {sentiment.negative_calls}
          </p>
          <p className="text-xs text-red-700 font-semibold mt-1">Negative</p>
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
    <div className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-sm">
      <h3 className="text-base font-bold text-[#1D3533] mb-6 flex items-center gap-2">
        <div className="p-2 bg-blue-50 rounded-lg">
          <Database className="w-5 h-5 text-blue-600" />
        </div>
        PIMS Sync Status
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-zinc-600 font-medium">Status</span>
          <span
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold ${
              isConnected
                ? "bg-green-100 text-green-700"
                : "bg-zinc-100 text-zinc-700"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-600 animate-pulse" : "bg-zinc-400"}`}
            />
            {pims.connection_status.replace(/_/g, " ").toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4">
          <div className="text-center p-4 bg-zinc-50 rounded-xl">
            <p className="text-2xl font-black text-[#1D3533] font-nunito">
              {pims.sync_success_rate.toFixed(0)}%
            </p>
            <p className="text-xs text-zinc-600 font-semibold mt-1">
              Success Rate
            </p>
          </div>
          <div className="text-center p-4 bg-zinc-50 rounded-xl">
            <p className="text-2xl font-black text-[#1D3533] font-nunito">
              {pims.total_syncs_today}
            </p>
            <p className="text-xs text-zinc-600 font-semibold mt-1">
              Syncs Today
            </p>
          </div>
        </div>

        {pims.last_sync_at && (
          <div className="pt-4 border-t border-zinc-200">
            <p className="text-xs text-zinc-500 font-medium">Last Sync</p>
            <p className="text-sm font-bold text-zinc-900 mt-1">
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
          <div className="pt-4 border-t border-zinc-200">
            <p className="text-sm text-red-600 flex items-center gap-2 font-semibold">
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

export function DashboardContent({
  analytics,
  loading = false,
  error = null,
}: DashboardContentProps) {
  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 text-lg font-semibold mb-2">Error</p>
          <p className="text-zinc-500">{error}</p>
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
          <p className="text-zinc-500 text-lg">Connecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-nunito font-bold text-zinc-900">
          Dashboard
        </h1>
        <p className="text-zinc-600 mt-1">
          Overview of your clinic&apos;s performance
        </p>
      </div>

      {/* Stats Grid - 3 columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Calls Answered"
          value={`${analytics.calls.total_calls}`}
          subtitle={`+${analytics.calls.calls_today} last 7 days`}
          icon={Phone}
          color="orange"
        />
        <StatsCard
          title="Appointments"
          value={analytics.appointments.total_appointments}
          subtitle={`+${analytics.appointments.appointments_this_week} last 7 days`}
          icon={Calendar}
          color="blue"
        />
        <StatsCard
          title="Call Coverage"
          value={`${analytics.calls.ai_handled_percentage}%`}
          subtitle={`${analytics.calls.total_calls - analytics.calls.emergency_transfers} calls answered / ${analytics.calls.total_calls} total`}
          icon={CheckCircle}
          color="teal"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <CallsChart
            data={analytics.calls.calls_by_hour}
            emergencyTransfers={analytics.calls.emergency_transfers}
            transferHours={[3, 15]}
          />
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-orange-50 rounded-lg">
                  <Clock className="w-5 h-5 text-orange-600" />
                </div>
                <p className="text-xs text-zinc-600 font-semibold uppercase tracking-wide">
                  Avg Duration
                </p>
              </div>
              <p className="text-2xl font-black text-zinc-900 font-nunito">
                {Math.floor(analytics.calls.average_duration_seconds / 60)}:
                {(analytics.calls.average_duration_seconds % 60)
                  .toFixed(0)
                  .padStart(2, "0")}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-red-50 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                </div>
                <p className="text-xs text-zinc-600 font-semibold uppercase tracking-wide">
                  Emergencies
                </p>
              </div>
              <p className="text-2xl font-black text-zinc-900 font-nunito">
                {analytics.calls.emergency_transfers}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-teal-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-teal-600" />
                </div>
                <p className="text-xs text-zinc-600 font-semibold uppercase tracking-wide">
                  Appointments Booked
                </p>
              </div>
              <p className="text-2xl font-black text-zinc-900 font-nunito">
                {analytics.appointments.bookings_via_ai}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <PawPrint className="w-5 h-5 text-purple-600" />
                </div>
                <p className="text-xs text-zinc-600 font-semibold uppercase tracking-wide">
                  New Patients
                </p>
              </div>
              <p className="text-2xl font-black text-zinc-900 font-nunito">
                {analytics.patients.new_patients_this_month}
              </p>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <SentimentCard sentiment={analytics.sentiment} />
          <PIMSStatusCard pims={analytics.pims} />
        </div>
      </div>

      {/* Recent Call Logs Table */}
      <CallLogTable calls={analytics.recent_calls} />
    </div>
  );
}
