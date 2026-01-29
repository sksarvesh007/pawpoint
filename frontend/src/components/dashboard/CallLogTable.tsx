/**
 * Recent calls table with sentiment and outcome badges.
 */

import type { CallLogSummary } from "@/types/analytics";

interface CallLogTableProps {
  calls: CallLogSummary[];
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatPhone(phone: string | null): string {
  if (!phone) return "Unknown";
  // Format +1234567890 -> (123) 456-7890
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 11 && cleaned.startsWith("1")) {
    return `(${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  return phone;
}

function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  if (!sentiment) {
    return <span className="text-zinc-400 text-sm">—</span>;
  }

  const colors = {
    positive: "bg-green-100 text-green-700",
    neutral: "bg-yellow-100 text-yellow-700",
    negative: "bg-red-100 text-red-700",
  };

  const color = colors[sentiment as keyof typeof colors] || "bg-zinc-100 text-zinc-700";

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      {sentiment}
    </span>
  );
}

function OutcomeBadge({ outcome }: { outcome: string }) {
  const colors: Record<string, string> = {
    appointment_booked: "bg-teal-100 text-teal-700",
    appointment_cancelled: "bg-orange-100 text-orange-700",
    appointment_rescheduled: "bg-blue-100 text-blue-700",
    information_provided: "bg-purple-100 text-purple-700",
    message_taken: "bg-indigo-100 text-indigo-700",
    transferred_to_staff: "bg-amber-100 text-amber-700",
    emergency_transfer: "bg-red-100 text-red-700",
    no_action_needed: "bg-zinc-100 text-zinc-700",
    follow_up_required: "bg-pink-100 text-pink-700",
    voicemail_left: "bg-slate-100 text-slate-700",
    call_dropped: "bg-zinc-100 text-zinc-700",
    other: "bg-zinc-100 text-zinc-700",
    unknown: "bg-zinc-100 text-zinc-700",
  };

  const color = colors[outcome] || "bg-zinc-100 text-zinc-700";
  const label = outcome.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}

function ConfidenceBar({ score }: { score: number | null }) {
  if (score === null || score === undefined) {
    return <span className="text-zinc-400 text-sm">—</span>;
  }

  const percentage = Math.round(score * 100);
  const color =
    percentage >= 80
      ? "bg-green-500"
      : percentage >= 60
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-zinc-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-zinc-600 w-10 text-right">{percentage}%</span>
    </div>
  );
}

export function CallLogTable({ calls }: CallLogTableProps) {
  if (!calls || calls.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-zinc-200 shadow-sm p-8 text-center">
        <h2 className="text-xl font-semibold text-zinc-900 mb-2">Recent Calls</h2>
        <p className="text-zinc-500">No calls yet</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
      <div className="p-6 border-b border-zinc-200">
        <h2 className="text-xl font-semibold text-zinc-900">Recent Calls</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-zinc-50 border-b border-zinc-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                Phone
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                Outcome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                Sentiment
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-600 uppercase tracking-wider">
                AI Confidence
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200">
            {calls.map((call) => (
              <tr key={call.id} className="hover:bg-zinc-50 transition-colors">
                <td className="px-6 py-4 text-sm text-zinc-900 whitespace-nowrap">
                  {formatTime(call.started_at)}
                </td>
                <td className="px-6 py-4 text-sm text-zinc-700 whitespace-nowrap">
                  {formatPhone(call.caller_phone_number)}
                </td>
                <td className="px-6 py-4 text-sm text-zinc-700 whitespace-nowrap">
                  {formatDuration(call.duration_seconds)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <OutcomeBadge outcome={call.outcome} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <SentimentBadge sentiment={call.sentiment} />
                </td>
                <td className="px-6 py-4">
                  <ConfidenceBar score={call.ai_confidence_score} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
